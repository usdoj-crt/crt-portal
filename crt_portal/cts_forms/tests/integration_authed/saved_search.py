import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, admin_models, element


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
