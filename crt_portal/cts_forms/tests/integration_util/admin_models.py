"""Contains utilties for creating models using the admin panel for testing."""
import urllib.parse


def delete(page, admin_path, **filters):
    query_page_path = f'{admin_path}?{urllib.parse.urlencode(filters)}'
    with page.expect_navigation():
        page.goto(query_page_path)
    page.click("#action-toggle")
    page.select_option('select[name="action"]', 'delete_selected')
    with page.expect_navigation():
        page.locator('button').filter(has_text='Go').click()


def create(page, admin_path, **fields) -> int:
    """Helper to create an admin model.

    For example:
        _create_model(
            admin_path='/admin/cts_forms/foo',
            title='A Title',
            kind='bar',
        )

    If you encounter an supported input type, you may need to handle it below.

    Returns: The id of the created model.
    """
    with page.expect_navigation():
        page.goto(f'{admin_path}/add/')

    for field, value in fields.items():
        el = page.locator(f'#{field}')
        tag_name = el.evaluate('el => el.tagName')
        input_type = el.evaluate('el => el.type')

        if tag_name == 'select':
            el.select_option(value)
            continue

        if tag_name == 'input' and input_type == 'checkbox':
            if value == el.is_checked():
                continue
            el.check()
            continue

        el.fill(value)

    with page.expect_navigation():
        page.locator('button').filter(has_text='Save and continue editing').click()

    return int(page.url.split('/')[-2])
