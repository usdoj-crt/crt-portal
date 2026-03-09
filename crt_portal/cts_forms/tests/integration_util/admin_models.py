"""Contains utilties for creating models using the admin panel for testing."""
import urllib.parse

from cts_forms.tests.integration_util import element


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
            page,
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
        create(
            page,
            admin_path='/admin/cts_forms/foo',
            title='A Title',
            kind='bar',
        )

    If you encounter an unsupported input type, you may need to handle it below.

    Returns: The id of the created model.
    """
    with page.expect_navigation():
        page.goto(f'{admin_path}/add/')

    fill_fields(page, selector_format='#id_{}', fields=fields)

    with page.expect_navigation():
        page.locator('input[type="submit"]').filter(has_text='Save and continue editing').click()
    
    # Wait for the page to fully load after navigation
    page.wait_for_load_state('networkidle')

    # Check if there were any form errors
    if page.locator('.errorlist').count() > 0:
        errors = page.locator('.errorlist').all_text_contents()
        raise ValueError(f"Form validation errors: {errors}")
    
    # Django 5.2 changed the admin HTML structure, so we get the ID from the current URL
    # URL format: /admin/app/model/123/change/
    current_url = page.url
    
    # If still on add page, check for success message and try alternative methods
    if '/add/' in current_url:
        # Check if save was successful (look for success message)
        if page.locator('.success').count() > 0 or page.locator('.messagelist .success').count() > 0:
            # Try to get ID from breadcrumb or other location
            # For some models, we might need to navigate to the list and find it
            raise ValueError(f"Object was created but still on add page. URL: {current_url}")
        else:
            raise ValueError(f"Failed to save object. Still on add page: {current_url}")
    
    url_parts = current_url.rstrip('/').split('/')
    
    # Find the numeric ID in the URL (should be second-to-last part before 'change')
    if 'change' in url_parts:
        id_index = url_parts.index('change') - 1
        return int(url_parts[id_index])
    else:
        # Fallback: look for the first numeric part after the model name
        for i, part in enumerate(url_parts):
            if part.isdigit():
                return int(part)
        raise ValueError(f"Could not extract ID from URL: {current_url}")


def _go_to_model(page, admin_path, filters):
    filterstring = urllib.parse.urlencode(filters, quote_via=urllib.parse.quote)
    query_page_path = f'{admin_path}/?{filterstring}'
    with page.expect_navigation():
        page.goto(query_page_path)
    if page.locator('.paginator').text_content().strip().startswith('0 '):
        raise ValueError(f'No models found matching the given filters: {filters}')
    with page.expect_navigation():
        page.locator("#result_list tbody tr th a").first.click()


def read(page, admin_path, filters, fields):
    """Helper to retrieve the values of an admin model.

    The supplied filters should only match _one_ object. If they don't the first one will be chosen.

    For example:
        read(
            page,
            admin_path='/admin/cts_forms/foo',
            filters={'title': 'A Title'},
            fields=['title', 'kind'],
        )

    If you encounter an unsupported input type, you may need to handle it below.
    """
    _go_to_model(page, admin_path, filters)
    return {
        field: _read_field(page, field)
        for field in fields
    }


def _read_field(page, field):
    container = page.locator(f'.field-{field}')
    if container.evaluate("el => el.querySelector('.readonly')"):
        return element.normalize_text(container.locator('.readonly'))

    if container.evaluate("el => el.querySelector('input')"):
        return container.locator('input').value

    return element.normalize_text(container)


def update(page, admin_path, filters, **fields):
    """Helper to modify an admin model.

    The supplied filters should only match _one_ object.

    For example:
        update(
            page,
            admin_path='/admin/cts_forms/foo',
            filters={'title': 'A Title'},
            title='A Title',
            kind='bar',
        )

    If you encounter an unsupported input type, you may need to handle it below.
    """
    _go_to_model(page, admin_path, filters)

    fill_fields(page, selector_format='#id_{}', fields=fields)

    with page.expect_navigation():
        page.locator('input[type="submit"]').filter(has_text='Save and continue editing').click()
