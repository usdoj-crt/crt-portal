import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, admin_models, reporting

TEST_DATA = {
    "contact_first_name": "fakefirst",
    "contact_last_name": "fakelast",
    "contact_phone": "+15555555555",
    "contact_email": "fake@example.com",
    "contact_address_line_1": "123 Fake St",
    "contact_address_line_2": "",
    "contact_city": "Fakington",
    "contact_state": "OH",
    "contact_zip": "12345",
    "primary_complaint": "voting",
    "location_name": "Fake Org",
    "location_address_line_1": "1234 Fake Ave",
    "location_address_line_2": "",
    "location_city_town": "Fakeville",
    "location_state": "AZ",
    "violation_summary": "something happened",
    "crt_reciept_month": '8',
    "crt_reciept_day": '15',
    "crt_reciept_year": '2024',
    "intake_format": "phone",
}


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore=['404', 'The user aborted a request.'])
@reporting.capture_report('phone_pro_form_from_blank.pdf')
def test_form(page, *, report):
    login_as_superuser(page)
    page.goto('/form/new/phone/')

    report.screenshot(page, full_page=True, caption="The phone intake form involves a subset of report fields that you can and save changes to on the fly. These include who is calling, what they're calling about, and where and when the event happened.")

    for accordion in page.locator('.usa-accordion button').all():
        accordion.click()

    report.screenshot(page, full_page=True, caption="As not all callers provide all of the information we'd normally take in via the intake form, some of these fields are hidden behind expansion panels to keep the primary interface clean.")

    admin_models.fill_fields(page, selector_format='#id_{}', fields={
        k: v for k, v in TEST_DATA.items() if k in ["contact_first_name", "contact_last_name"]
    })

    page.locator('button[data-saves]').click()
    page.locator('.usa-alert').filter(has_text="Successfully created report").wait_for()
    report.screenshot(page, full_page=True, caption="One key feature of the phone intake form is that information can be partially filled in, saved, and then edited without leaving the page. We've only filled in the contact first and last name here before clicking save, and we're already presented with a Record Locator we can give to the caller.")

    admin_models.fill_fields(page, selector_format='#id_{}', fields={
        k: v for k, v in TEST_DATA.items() if k not in ["contact_first_name", "contact_last_name", "primary_complaint", "intake_format"]
    })
    report.screenshot(page, full_page=True, caption="After filling the remaining fields, we can click save again to finish up the form.")
    page.locator('[data-saves]').click()
    page.locator('.usa-alert').filter(has_text="Successfully updated report").wait_for()
    page.locator('.usa-alert').filter(has_text="1234 Fake Ave").wait_for()


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore=['404', 'The user aborted a request.'])
@reporting.capture_report('phone_pro_form_from_existing.pdf')
def test_loads_page_from_id(page, *, report):
    login_as_superuser(page)

    report_id = admin_models.create_report(
        page,
        **TEST_DATA
    )

    page.goto(f'/form/new/phone/{report_id}')

    for accordion in page.locator('.usa-accordion button').all():
        accordion.click()

    report.screenshot(page, full_page=True, caption='An existing report may be opened via the URL. In this example, we see that previously saved fields are populated on page load.')

    automatic = set(TEST_DATA.keys()) - {'primary_complaint'}
    for field in automatic:
        assert str(page.locator(f'[name="{field}"]').input_value()) == TEST_DATA[field]

    assert page.locator('[name="primary_complaint"][checked]').input_value() == 'voting'
