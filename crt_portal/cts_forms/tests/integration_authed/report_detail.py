import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, features, admin_models


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
@features.login_as_superuser_with_feature('separate-referrals-workflow')
def test_contact_complainant_modal(page):
    page.goto("/form/view")

    assert page.is_visible("#filters-form")

    page.fill("input[name='contact_first_name']", "Testing")
    page.fill("input[name='contact_last_name']", "Tester")
    page.locator('label').filter(has_text="Closed").click()
    with page.expect_navigation():
        page.evaluate("document.getElementById('apply-filters-button').click()")
    with page.expect_navigation():
        page.evaluate("document.querySelector('.td-link').click()")

    page.locator('button').filter(has_text="Contact complainant").click()

    page.screenshot(path="e2e-screenshots/contact_complainant_unselected.png", full_page=True)
    assert page.locator('#id_templates_default option[checked]').text_content().strip() == '[Select response letter]'
    assert page.locator('#intake_description').text_content().strip() == '[Select response letter]'
    assert page.locator('#intake_letter').input_value().strip() == ''

    page.locator('select').filter(has_text='English').select_option('Spanish')
    page.locator('select').filter(has_text='[Select response letter]').select_option('CRT - No capacity')

    page.wait_for_selector('#intake_description:has-text("Your Civil Rights Division Report")')
    page.wait_for_selector('#intake_letter_html:has-text("Dear Testing Tester")')

    for label in ['Send', 'Print letter', 'Copy letter']:
        assert page.locator('button').filter(has_text=label).is_enabled()
    page.screenshot(path="e2e-screenshots/contact_complainant_selected.png", full_page=True)

    with page.expect_navigation():
        page.locator('button').filter(has_text='Send').click()

    page.screenshot(path="e2e-screenshots/contact_complainant_sent.png", full_page=True)
    success = page.locator('.usa-alert--success').text_content().strip()
    try:
        assert success == "Email sent: 'CRT - No capacity' to testing@test.com via govDelivery TMS"
    except AssertionError:
        assert success == 'testing@test.com not in allowed domains, not attempting to deliver CRT - No capacity.'


@pytest.mark.only_browser("chromium")
@pytest.mark.only
@console.raise_errors(ignore='404')
@features.login_as_superuser_with_feature('separate-referrals-workflow')
def test_refer_complaint_modal_no_email(page):
    admin_models.delete(
        page,
        '/admin/cts_forms/responsetemplate',
        title__contains='Referrals integration test - no agency email',
    )
    admin_models.delete(
        page,
        '/admin/cts_forms/referralcontact',
        machine_name__contains='test-referral-contact-no-email',
    )

    anonymous_report_id = admin_models.create_report(
        page,
        crt_reciept_month='12',
        crt_reciept_day='25',
        crt_reciept_year='2000',
        intake_format='phone',
        primary_complaint='something_else',
        contact_first_name='ReferralTestingNoEmail'
    )
    admin_models.create(
        page,
        '/admin/cts_forms/referralcontact',
        machine_name='test-referral-contact-no-email',
        name='Test Referral Contact No Email',
    )
    for language in ['en', 'es']:
        admin_models.create(
            page,
            '/admin/cts_forms/responsetemplate',
            title=f'({language}) Referrals integration test - no agency email',
            subject=f'Re: [{language}] your referrals test',
            body=r'{{addressee}}, this should be deleted following a successful test.',
            language=language,
            is_html=True,
            show_in_dropdown=True,
            referral_contact='Test Referral Contact No Email',
        )

    page.goto(f'/form/view/{anonymous_report_id}')

    page.locator('button').filter(has_text="Refer complaint").click()

    page.screenshot(path="e2e-screenshots/refer_1_unselected.png", full_page=True)
    assert page.locator('.current-step[aria-label="Current step one of three: Complainant Letter"]').filter(has_text="Complainant letter").is_visible()
    assert page.locator('.future-step[aria-label="Future step two of three: Agency Letter"]').filter(has_text="Agency letter").is_visible()
    assert page.locator('.future-step[aria-label="Future step three of three: Review and Send"]').filter(has_text="Review and send").is_visible()
    assert page.locator('.card-header').innerText == 'Complainant letter'
    assert page.locator('select').filter(has_text="English").input_value().strip() == 'English'
    assert page.locator('select').filter(has_text="[Select an agency]").is_visible()

    assert page.locator('.error-message').text_content().strip() == 'There is no email on file for this complainant.'
    assert page.locator('#intake_letter_html').text_content().strip() == ''

    page.locator('button').filter(has_text="Next").click()
    page.screenshot(path="e2e-screenshots/refer_1_agency_required.png", full_page=True)
    assert page.get_by_text('Agency is required').is_visible()
    assert page.locator('.current-step[aria-label="Current step one of three: Complainant Letter"]').filter(has_text="Complainant letter").is_visible()

    page.locator('select').filter(has_text="English").select_option('Spanish')
    assert page.locator('select').filter(has_text="[Select an agency]").locator('option').count == 1
    page.locator('select').filter(has_text="[Select an agency]").select_option('(es) Referrals integration test - no agency email')
    assert page.get_by_text('Subject:').text_content().strip() == 'Subject: Re: [es] your referrals test'
    page.wait_for_selector('#intake_letter_html:has-text("Dear Testing Tester")')

    admin_models.delete(
        page,
        '/admin/cts_forms/responsetemplate',
        title__contains='Referrals integration test - no agency email',
    )
    admin_models.delete(
        page,
        '/admin/cts_forms/referralcontact',
        machine_name__contains='test-referral-contact-no-email',
    )


@pytest.mark.only_browser("chromium")
# @pytest.mark.only
@console.raise_errors(ignore='404')
@features.login_as_superuser_with_feature('separate-referrals-workflow')
def test_refer_complaint_modal_with_email(page):
    admin_models.delete(
        page,
        '/admin/cts_forms/responsetemplate',
        title__contains='Referrals integration test - with agency email',
    )
    admin_models.delete(
        page,
        '/admin/cts_forms/referralcontact',
        machine_name__contains='test-referral-contact-with-email',
    )

    report_id = admin_models.create_report(
        page,
        crt_reciept_month='12',
        crt_reciept_day='25',
        crt_reciept_year='2000',
        intake_format='phone',
        primary_complaint='something_else',
        contact_first_name='ReferralTestingWithEmail',
        contact_email='test@testing.com',
    )
    admin_models.create(
        page,
        '/admin/cts_forms/referralcontact',
        machine_name='test-referral-contact-with-email',
        name='Test Referral Contact With Email',
        addressee_emails='ayy@example.com, bee@example.com'
    )
    for language in ['en', 'es']:
        admin_models.create(
            page,
            '/admin/cts_forms/responsetemplate',
            title=f'({language}) Referrals integration test - with agency email',
            subject=f'Re: [{language}] your referrals test',
            body=r'{{addressee}}, this should be deleted following a successful test.',
            language=language,
            is_html=True,
            show_in_dropdown=True,
            referral_contact='Test Referral Contact With Email',
        )

    page.goto(f'/form/view/{report_id}')

    page.locator('button').filter(has_text="Refer complaint").click()

    page.screenshot(path="e2e-screenshots/refer_1_unselected.png", full_page=True)
    assert page.locator('.current-step[aria-label="Current step one of three: Complainant Letter"]').filter(has_text="Complainant letter").is_visible()
    assert page.locator('.future-step[aria-label="Future step two of three: Agency Letter"]').filter(has_text="Agency letter").is_visible()
    assert page.locator('.future-step[aria-label="Future step three of three: Review and Send"]').filter(has_text="Review and send").is_visible()
    assert page.locator('.card-header').innerText == 'Complainant letter'
    assert page.locator('select').filter(has_text="English").input_value().strip() == 'English'
    assert page.locator('select').filter(has_text="[Select an agency]").is_visible()

    assert page.locator('p').filter(has_text='Email: ').text_content().strip() == 'Email: test@testing.com'
    assert page.locator('p').filter(has_text='Subject: ').text_content().strip() == 'Subject: Re: [en] your referrals test'
    assert page.locator('#intake_letter_html').text_content().strip() == ''

    page.locator('button').filter(has_text="Next").click()
    page.screenshot(path="e2e-screenshots/refer_1_agency_required.png", full_page=True)
    assert page.get_by_text('Agency is required').is_visible()
    assert page.locator('.current-step[aria-label="Current step one of three: Complainant Letter"]').filter(has_text="Complainant letter").is_visible()

    page.locator('select').filter(has_text="English").select_option('Spanish')
    assert page.locator('select').filter(has_text="[Select an agency]").locator('option').count == 1
    page.locator('select').filter(has_text="[Select an agency]").select_option('(es) Referrals integration test - with agency email')
    assert page.get_by_text('Subject:').text_content().strip() == 'Subject: Re: [es] your referrals test'
    page.wait_for_selector('#intake_letter_html:has-text("Dear Testing Tester")')

    admin_models.delete(
        page,
        '/admin/cts_forms/responsetemplate',
        title__contains='Referrals integration test - with agency email',
    )
    admin_models.delete(
        page,
        '/admin/cts_forms/referralcontact',
        machine_name__contains='test-referral-contact-with-email',
    )


@pytest.mark.only_browser("chromium")
@console.raise_errors()
def test_click_back_to_all(page):
    """Opens report detail page and goes back to reports page"""

    login_as_superuser(page)

    page.goto("/form/view")

    page.locator('#id_status_0').check()

    page.screenshot(path="e2e-screenshots/report_detail_test_1.png", full_page=True)
    with page.expect_navigation():
        page.locator('#apply-filters-button').click()

    total_results = page.evaluate("document.querySelector('.intake-pagination').innerText.split(' ')[5]")
    first_result = page.evaluate("document.querySelector('.stripe > td > .td-checkbox > input').value")
    page.screenshot(path="e2e-screenshots/report_detail_test_2.png", full_page=True)
    with page.expect_navigation():
        page.evaluate("document.querySelector('.td-link').click()")

    report_id = page.locator('.details-id > h2').text_content()
    assert first_result in report_id
    pagination = page.locator('.usa-pagination > span').text_content().strip()
    assert pagination == '1 of ' + total_results + ' records'

    assert page.is_visible("#contact-info")
    page.screenshot(path="e2e-screenshots/report_detail_test_3.png", full_page=True)
    with page.expect_navigation():
        page.locator('.next').click()

    pagination = page.locator('.usa-pagination > span').text_content().strip()
    assert pagination == '2 of ' + total_results + ' records'
    page.screenshot(path="e2e-screenshots/report_detail_test_4.png", full_page=True)
    with page.expect_navigation():
        page.locator('.next').click()

    pagination = page.locator('.usa-pagination > span').text_content().strip()
    assert pagination == '3 of ' + total_results + ' records'
    page.screenshot(path="e2e-screenshots/report_detail_test_5.png", full_page=True)
    with page.expect_navigation():
        page.locator('.prev').click()

    pagination = page.locator('.usa-pagination > span').text_content().strip()
    assert pagination == '2 of ' + total_results + ' records'
    page.screenshot(path="e2e-screenshots/report_detail_test_6.png", full_page=True)
    with page.expect_navigation():
        page.locator('.outline-button--dark').click()
    page.screenshot(path="e2e-screenshots/report_detail_test_7.png", full_page=True)
    assert page.is_visible("#contact-email-filter")
