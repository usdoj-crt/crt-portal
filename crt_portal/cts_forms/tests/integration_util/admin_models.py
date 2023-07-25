"""Contains utilties for creating models using the admin panel for testing."""
import urllib.parse


def delete(page, admin_path, **filters):
    filterstring = urllib.parse.urlencode(filters, quote_via=urllib.parse.quote)
    query_page_path = f'{admin_path}/?{filterstring}'
    with page.expect_navigation():
        page.goto(query_page_path)
    if page.locator('.paginator').text_content().strip().startswith('0 '):
        return
    page.click("#action-toggle")
    page.select_option('select[name="action"]', 'delete_selected')
    with page.expect_navigation():
        page.locator('button').filter(has_text='Go').click()
    with page.expect_navigation():
        page.locator('input[type="submit"]').click()


def fill_fields(page, *, selector_format, fields):
    """Fills fields that match django's form patterns.

    For example, if the fields look like:
        <input id="id_0-first_name" name="0-first_name" type="text">

    Then you'd call this function using:
        _fill_fields(page, selector_format='id_0-{}', fields={'first_name': 'Jane'})
    """
    for field, value in fields.items():
        try:
            _fill_field(page, selector_format=selector_format, field=field, value=value)
        except Exception as e:
            raise RuntimeError(f'Unable to fill {field} with {value}') from e


def _fill_field(page, *, selector_format, field, value):
    el = page.locator(selector_format.format(field))
    tag_name = el.evaluate('el => el.tagName').lower()
    input_type = (el.evaluate('el => el.type') or '').lower()

    if tag_name == 'select':
        el.select_option(value)
        return

    # Sometimes we are targeting a specific radio / check input
    if tag_name == 'input' and input_type in ['checkbox', 'radio']:
        if value == el.is_checked():
            return
        el.check()
        return

    # Other times, we're targeting a div containing multiple inputs
    if el.evaluate("el => el.querySelector('input[type=\"radio\"]')"):
        el.locator(f'input[type="radio"][value="{value}"]').check()
        return

    if el.evaluate("el => el.querySelector('input[type=\"checkbox\"]')"):
        el.locator(f'input[type="checkbox"][value="{value}"]').check()
        return

    el.fill(value)


def create_report(page, **fields) -> int:
    """Creates a report.

    Note that this uses the proform, not django admin.

    For example, with the minimum required fields:
        create_report(
            crt_reciept_month='12',
            crt_reciept_day='25',
            crt_reciept_year='2000',
            intake_format_2='phone',
            primary_complaint='something_else',
        )

    Returns the id of the created report.
    """
    with page.expect_navigation():
        page.goto('/form/new')

    fill_fields(page, selector_format='#id_0-{}', fields=fields)

    with page.expect_navigation():
        page.locator('input[type="submit"]').filter(has_text='Submit').click()

    id_header = page.locator('.details-id h2')
    return int(id_header.text_content().replace('ID: ', '').split('-')[0])


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

    fill_fields(page, selector_format='#id_{}', fields=fields)

    with page.expect_navigation():
        page.locator('input[type="submit"]').filter(has_text='Save and continue editing').click()

    url_with_id = page.locator('.historylink').get_attribute('href')
    return int(url_with_id.strip('/').split('/')[-2])
