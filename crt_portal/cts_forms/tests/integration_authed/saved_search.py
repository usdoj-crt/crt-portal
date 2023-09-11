import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, admin_models, element


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
def test_saved_search(page):
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
        name='Test Auto-Closing Saved Search',
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
