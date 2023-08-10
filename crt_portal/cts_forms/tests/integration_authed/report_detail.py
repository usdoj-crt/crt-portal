import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, features, admin_models, element


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

    modal = page.locator('#intake_template')

    page.screenshot(path="e2e-screenshots/contact_complainant_unselected.png", full_page=True)
    assert element.normalize_text(modal.locator('#id_templates_default option[checked]')) == '[Select response letter]'
    assert element.normalize_text(modal.locator('#intake_description')) == '[Select response letter]'
    assert modal.locator('#intake_letter').input_value() == ''

    modal.locator('select').filter(has_text='English').select_option('Spanish')
    modal.locator('select').filter(has_text='[Select response letter]').select_option('CRT - No capacity')

    modal.locator('#intake_description').filter(has_text='Your Civil Rights Division Report').wait_for()
    modal.locator('#intake_letter_html').filter(has_text='Dear Testing Tester').wait_for()

    for label in ['Send', 'Print letter', 'Copy letter']:
        assert modal.locator('button').filter(has_text=label).is_enabled()
    page.screenshot(path="e2e-screenshots/contact_complainant_selected.png", full_page=True)

    with page.expect_navigation():
        modal.locator('button').filter(has_text='Send').click()

    page.screenshot(path="e2e-screenshots/contact_complainant_sent.png", full_page=True)
    success = element.normalize_text(page.locator('.usa-alert--success'))
    try:
        assert success == "Email sent: 'CRT - No capacity' to testing@test.com via govDelivery TMS"
    except AssertionError:
        assert success == 'testing@test.com not in allowed domains, not attempting to deliver CRT - No capacity.'


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore=['404', 'The user aborted a request.'])
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

    modal = page.locator('#intake_referral_modal')

    page.screenshot(path="e2e-screenshots/refer_1_no_email_unselected.png", full_page=True)
    assert modal.locator('.step.current[data-step="1"]').is_visible()
    assert modal.locator('.step[data-step="2"]').filter(has_text="Agency letter").is_visible()
    assert modal.locator('.step[data-step="3"]').filter(has_text="Review and send").is_visible()
    letter_step = modal.locator('.modal-step.complainant-letter')

    assert letter_step.is_visible()
    assert element.normalize_text(letter_step.locator('.step-text')) == 'Complainant letter'
    assert letter_step.locator('select').filter(has_text="English").input_value() == 'en'
    assert letter_step.locator('select').filter(has_text="[Select an agency]").is_visible()

    assert element.normalize_text(letter_step.locator('.no-email-error .error-message')) == 'There is no email on file for this complainant.'
    assert element.normalize_text(letter_step.locator('.letter-html')) == ''

    modal.locator('button').filter(has_text="Next").click()
    page.screenshot(path="e2e-screenshots/refer_1_no_email_agency_required.png", full_page=True)
    assert modal.get_by_text('Agency is required').is_visible()
    assert modal.locator('.step.current[data-step="1"]').is_visible()

    letter_step.locator('select').filter(has_text="English").select_option('Spanish')

    agency_select = letter_step.locator('select').filter(has_text="[Select an agency]")
    all_agency_options = agency_select.locator('option')
    assert all([
        '(en)' not in element.normalize_text(o)
        for o in all_agency_options.all()
        if o.get_attribute('hidden') != 'true'
    ])
    agency_select.select_option('(es) Referrals integration test - no agency email')

    letter_step.locator('.letter-html').filter(has_text='Dear ReferralTestingNoEmail,').wait_for()

    modal.locator('button').filter(has_text="Next").click()
    assert modal.locator('.step.current[data-step="2"]').is_visible()

    page.screenshot(path="e2e-screenshots/refer_2_with_email_unselected.png", full_page=True)

    letter_step = modal.locator('.modal-step.agency-letter')
    assert letter_step.get_by_text('There is no email on file for this agency.').is_visible()

    letter_step.locator('.letter-html').filter(has_text='we feel is more appropriate for your agency').wait_for()
    letter_step.locator('.letter-html').filter(has_text='First name: ReferralTestingNoEmail').wait_for()

    modal.locator('button').filter(has_text="Next").click()
    assert modal.locator('.step.current[data-step="3"]').is_visible()
    letter_step = modal.locator('.modal-step.review-and-send')

    page.screenshot(path="e2e-screenshots/refer_3_with_email.png", full_page=True)
    letter_step.locator('p.no-email-error').filter(has_text='you must print this letter to send to the complainant').wait_for()
    letter_step.locator('p.no-email-error').filter(has_text='you must print this letter to send to the agency').wait_for()
    assert element.normalize_text(letter_step.locator('h2 .agency-name')) == 'Test Referral Contact No Email'

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
@console.raise_errors(ignore=['404', 'The user aborted a request.'])
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
        addressee_emails='fake.email1@example.com,fake.email2@example.com, fake.email3@example.com'
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

    modal = page.locator('#intake_referral_modal')

    page.screenshot(path="e2e-screenshots/refer_1_with_email_unselected.png", full_page=True)
    assert modal.locator('.step.current[data-step="1"]').is_visible()
    assert modal.locator('.step[data-step="2"]').filter(has_text="Agency letter").is_visible()
    assert modal.locator('.step[data-step="3"]').filter(has_text="Review and send").is_visible()
    letter_step = modal.locator('.modal-step.complainant-letter')

    assert letter_step.is_visible()
    assert element.normalize_text(letter_step.locator('.step-text')) == 'Complainant letter'
    assert letter_step.locator('select').filter(has_text="English").input_value() == 'en'
    assert letter_step.locator('select').filter(has_text="[Select an agency]").is_visible()

    assert element.normalize_text(letter_step.locator('.letter-html')) == ''

    modal.locator('button').filter(has_text="Next").click()
    page.screenshot(path="e2e-screenshots/refer_1_with_email_agency_required.png", full_page=True)
    assert modal.get_by_text('Agency is required').is_visible()
    assert modal.locator('.step.current[data-step="1"]').is_visible()

    letter_step.locator('select').filter(has_text="English").select_option('Spanish')

    agency_select = letter_step.locator('select').filter(has_text="[Select an agency]")
    all_agency_options = agency_select.locator('option')
    assert all([
        '(en)' not in o.text_content()
        for o in all_agency_options.all()
        if o.get_attribute('hidden') != 'true'
    ])
    agency_select.select_option('(es) Referrals integration test - with agency email')

    assert element.normalize_text(letter_step.locator('p').filter(has_text='Email: ')) == 'Email: test@testing.com'
    letter_step.locator('.subject').filter(has_text='Re: [es] your referrals test').wait_for()
    letter_step.locator('.letter-html').filter(has_text='Dear ReferralTestingWithEmail,').wait_for()

    modal.locator('button').filter(has_text="Next").click()
    assert modal.locator('.step.current[data-step="2"]').is_visible()

    page.screenshot(path="e2e-screenshots/refer_2_with_email_unselected.png", full_page=True)

    letter_step = modal.locator('.modal-step.agency-letter')

    assert letter_step.get_by_text('Agency letter').is_visible()
    assert letter_step.get_by_text('Refer complaint to (es) Referrals integration test - with agency email').is_visible()

    # Note: we cannot test email / cc /subject here, because the integration
    # tests aren't allowed to send email; so the recipients are filtered out.

    letter_step.locator('.letter-html').filter(has_text='we feel is more appropriate for your agency').wait_for()
    letter_step.locator('.letter-html').filter(has_text='First name: ReferralTestingWithEmail').wait_for()

    modal.locator('button').filter(has_text="Next").click()
    assert modal.locator('.step.current[data-step="3"]').is_visible()
    letter_step = modal.locator('.modal-step.review-and-send')

    page.screenshot(path="e2e-screenshots/refer_3_with_email.png", full_page=True)
    assert element.normalize_text(letter_step.locator('h2 .agency-name')) == 'Test Referral Contact With Email'

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

    report_id = element.normalize_text(page.locator('.details-id > h2'))
    assert first_result in report_id
    pagination = element.normalize_text(page.locator('.usa-pagination > span'))
    assert pagination == '1 of ' + total_results + ' records'

    assert page.is_visible("#contact-info")
    page.screenshot(path="e2e-screenshots/report_detail_test_3.png", full_page=True)
    with page.expect_navigation():
        page.locator('.pagination .next').click()

    pagination = element.normalize_text(page.locator('.usa-pagination > span'))
    assert pagination == '2 of ' + total_results + ' records'
    page.screenshot(path="e2e-screenshots/report_detail_test_4.png", full_page=True)
    with page.expect_navigation():
        page.locator('.pagination .next').click()

    pagination = element.normalize_text(page.locator('.usa-pagination > span'))
    assert pagination == '3 of ' + total_results + ' records'
    page.screenshot(path="e2e-screenshots/report_detail_test_5.png", full_page=True)
    with page.expect_navigation():
        page.locator('.prev').click()

    pagination = element.normalize_text(page.locator('.usa-pagination > span'))
    assert pagination == '2 of ' + total_results + ' records'
    page.screenshot(path="e2e-screenshots/report_detail_test_6.png", full_page=True)
    with page.expect_navigation():
        page.locator('.outline-button--dark').click()
    page.screenshot(path="e2e-screenshots/report_detail_test_7.png", full_page=True)
    assert page.is_visible("#contact-email-filter")
