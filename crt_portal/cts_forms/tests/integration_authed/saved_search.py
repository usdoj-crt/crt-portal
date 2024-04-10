import uuid
import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, admin_models, element, reporting, features


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
@reporting.capture_report('saved_search.pdf')
@features.login_as_superuser_with_feature('saved_searches')
def test_intake_add_search(page, *, report):
    admin_models.delete(
        page,
        '/admin/cts_forms/savedsearch',
        name__contains='Saved Search Integration Test',
    )

    page.goto('/form/view')
    page.fill('#id_summary', 'test')

    report.screenshot(page, full_page=True, caption='The easiest way to create a saved search is from the list page. Start by choosing the filters you want to save and choose "Apply Filters".')

    page.goto('/form/view?status=new&status=open&summary=test')

    report.screenshot(page, full_page=True, caption='Once the filters update, you can choose "Save search" to save the search.')

    with page.expect_navigation():
        page.locator('button').filter(has_text='Save search').click()

    search_id = str(uuid.uuid4())
    page.fill('#id_name', f'Saved Search Integration Test {search_id}')
    page.locator('a').filter(has_text='/link/search/saved-search-integration-test').wait_for()
    page.locator('#id_description').fill('This is a test search')
    assert page.locator('#id_query').input_value() == '&status=new&status=open&summary=test'
    page.select_option('#id_section', 'ELS')
    page.check('#id_shared')

    report.screenshot(page, full_page=True, caption="""This will bring you to a page where you can name the search, add a description, and choose whether to share the search with others. The "Query" field is a representation of the filters you've selected; don't change it unless you know what you're doing. Once you're done, choose "Add" to save the search.""")

    with page.expect_navigation():
        page.locator('button').filter(has_text='Add').click()

    page.locator('.usa-alert--success').filter(has_text=f'Successfully added new saved search: Saved Search Integration Test {search_id}.').wait_for()

    report.screenshot(page, full_page=True, caption="""You can now see your saved search in the list of saved searches. Note that you may need to move to the "My Saved Searches" tab if you didn't choose to share it.""")

    row = page.locator('tr').filter(has_text=search_id)

    assert row.locator('a').filter(has_text='Saved Search Integration Test').get_attribute('href') == f'/link/search/saved-search-integration-test-{search_id}'

    with page.expect_navigation():
        row.locator('button').filter(has_text='Edit').click()

    assert page.locator('#id_name').input_value() == f'Saved Search Integration Test {search_id}'
    assert f'/link/search/saved-search-integration-test-{search_id}' in page.locator('div').filter(has_text='Short Link').locator('a').get_attribute('href')
    assert page.locator('#id_description').input_value() == 'This is a test search'
    assert page.locator('#id_query').input_value() == '&status=new&status=open&summary=test'
    assert element.normalize_text(page.locator('#id_section [selected]')) == 'ELS'
    assert page.locator('#id_shared').is_checked()

    page.fill('#id_name', f'Saved Search Integration Test {search_id} - Updated')
    page.fill('#id_description', 'This is an updated test search')
    page.fill('#id_query', 'status=new&status=open&summary=test2')
    page.select_option('#id_section', 'ADM')
    page.uncheck('#id_shared')
    page.locator('div').filter(has_text='Short Link').locator('a').filter(has_text=f'/link/search/saved-search-integration-test-{search_id}-updated').wait_for()

    report.screenshot(page, full_page=True, caption="""You can edit your saved search by choosing the "Edit" button. You can change the name, description, and sharing settings. Changing the name will update the short link. Again, the "Query" field is a representation of the filters you've selected; don't change it unless you know what you're doing. Choose "Apply changes" to save your changes.""")

    with page.expect_navigation():
        page.locator('button').filter(has_text='Apply changes').click()

    page.locator('.usa-alert--success').filter(has_text=f'Successfully updated Name, Query, Section, Description, and Share in Saved Search Integration Test {search_id} - Updated').wait_for()

    report.screenshot(page, full_page=True, caption="""Because your search is no longer shared, you won't see it in the "Shared saved searches" tab anymore.""")

    assert search_id not in page.locator('.saved-search-table').text_content()
    with page.expect_navigation():
        page.locator('a').filter(has_text='My saved searches').click()
    assert search_id in page.locator('.saved-search-table').text_content()

    row = page.locator('tr').filter(has_text=search_id)

    report.screenshot(page, full_page=True, caption="""Clicking "My saved searches" will show it.""")

    assert f'/link/search/saved-search-integration-test-{search_id}-updated' in row.locator('a').filter(has_text='Saved Search Integration Test').get_attribute('href')

    with page.expect_navigation():
        row.locator('button').filter(has_text='Edit').click()

    assert page.locator('#id_name').input_value() == f'Saved Search Integration Test {search_id} - Updated'
    assert f'/link/search/saved-search-integration-test-{search_id}-updated' in page.locator('div').filter(has_text='Short Link').locator('a').get_attribute('href')
    assert page.locator('#id_description').input_value() == 'This is an updated test search'
    assert page.locator('#id_query').input_value() == 'status=new&status=open&summary=test2'
    assert element.normalize_text(page.locator('#id_section [selected]')) == 'ADM'
    assert not page.locator('#id_shared').is_checked()


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
def test_auto_close(page):
    login_as_superuser(page)

    admin_models.delete(
        page,
        '/admin/cts_forms/savedsearch',
        name__contains='Saved Search Integration Test',
    )

    unclosed = admin_models.create_report(
        page,
        crt_reciept_month='12',
        crt_reciept_day='25',
        crt_reciept_year='2000',
        intake_format='phone',
        primary_complaint='something_else',
        contact_first_name='SavedSearchTest',
    )

    page.goto(f'/form/view/{unclosed}')
    assert element.normalize_text(page.locator('#id_status [selected]')) == 'New'

    admin_models.create(
        page,
        '/admin/cts_forms/savedsearch',
        name='Saved Search Integration Test - Auto-close',
        auto_close=True,
        auto_close_reason='it was auto-routed to other agency for processing',
        query='status=new&status=open&violation_summary=%22refer%20to%20agency!%22&no_status=false&grouping=default',
    )

    closed = admin_models.create_report(
        page,
        crt_reciept_month='12',
        crt_reciept_day='25',
        crt_reciept_year='2000',
        intake_format='phone',
        primary_complaint='something_else',
        contact_first_name='SavedSearchTest',
        violation_summary='refer to agency!',
    )

    page.goto(f'/form/view/{closed}')
    assert element.normalize_text(page.locator('#id_status [selected]')) == 'Closed'
    assert page.locator('#id_summary').input_value() == 'Report automatically closed on submission because it was auto-routed to other agency for processing'


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
def test_auto_reroute(page):
    login_as_superuser(page)

    admin_models.delete(
        page,
        '/admin/cts_forms/savedsearch',
        name__contains='Saved Search Integration Test',
    )

    unrouted = admin_models.create_report(
        page,
        crt_reciept_month='12',
        crt_reciept_day='25',
        crt_reciept_year='2000',
        intake_format='phone',
        primary_complaint='something_else',
        contact_first_name='SavedSearchTest',
    )

    page.goto(f'/form/view/{unrouted}')
    assert element.normalize_text(page.locator('#id_assigned_section [selected]')) == 'ADM'

    admin_models.create(
        page,
        '/admin/cts_forms/savedsearch',
        name='Saved Search Integration Test - auto-reroute',
        override_section_assignment=True,
        override_section_assignment_with='DRS',
        query='status=new&status=open&violation_summary=%22reroute!%22&no_status=false&grouping=default',
    )

    routed = admin_models.create_report(
        page,
        crt_reciept_month='12',
        crt_reciept_day='25',
        crt_reciept_year='2000',
        intake_format='phone',
        primary_complaint='something_else',
        contact_first_name='SavedSearchTest',
        violation_summary='reroute!',
    )

    page.goto(f'/form/view/{routed}')
    assert element.normalize_text(page.locator('#id_assigned_section [selected]')) == 'DRS'
