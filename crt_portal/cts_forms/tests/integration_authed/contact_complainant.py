import pytest

from cts_forms.tests.integration_util import console, features, admin_models, element, reporting


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
@features.login_as_superuser_with_feature('separate-referrals-workflow')
@reporting.capture_report('contact_complainant_modal.pdf')
def test_contact_complainant_modal(page, *, report):
    page.goto("/form/view/?contact_first_name=Testing&contact_last_name=Tester")

    assert page.is_visible("#filters-form")

    with page.expect_navigation():
        page.evaluate("document.querySelector('.td-link').click()")

    page.locator('button').filter(has_text="Contact complainant").click()

    modal = page.locator('#intake_template')

    report.screenshot(page, full_page=True, caption='Upon clicking "Contact Complaint" from the Report Details page, users will be presented with this modal.')
    assert element.normalize_text(modal.locator('#id_templates_default option[checked]')) == '[Select response letter]'
    assert element.normalize_text(modal.locator('#intake_description')) == '[Select response letter]'
    assert modal.locator('#intake_letter').input_value() == ''

    modal.locator('select').filter(has_text='English').select_option('Spanish')
    modal.locator('select').filter(has_text='[Select response letter]').select_option('CRT - No capacity')

    modal.locator('#intake_description').filter(has_text='Your Civil Rights Division Report').wait_for()
    modal.locator('#intake_letter_html').filter(has_text='Dear Testing Tester').wait_for()
    assert modal.locator('.optionals').is_hidden()

    modal.locator('button').filter(has_text="Cancel").click()
    assert modal.locator('#intake_letter_html').text_content() == ''

    page.locator('button').filter(has_text="Contact complainant").click()
    
    modal.locator('select').filter(has_text='English').select_option('Spanish')
    modal.locator('select').filter(has_text='[Select response letter]').select_option('CRT - No capacity')

    modal.locator('#intake_description').filter(has_text='Your Civil Rights Division Report').wait_for()
    modal.locator('#intake_letter_html').filter(has_text='Dear Testing Tester').wait_for()

    for label in ['Send', 'Print letter', 'Copy letter']:
        assert modal.locator('button').filter(has_text=label).is_enabled()
    report.screenshot(page, full_page=True, caption='Users can select a language and a response letter from the dropdowns. The letter will be populated with the complainant\'s name, the date the report was submitted, etc. The content of these templates can be changed by application administrators.')

    with page.expect_navigation():
        modal.locator('button').filter(has_text='Send').click()

    report.screenshot(page, full_page=True, caption='Upon clicking "Send", the complainant will be sent an email with the letter at the content. A success message will be displayed at the top of the page if the send was successful. Note that, with the way email works, a send might be successful but the message may not be delivered (it may be caught by a spam filter, etc)')
    success = element.normalize_text(page.locator('.usa-alert--success'))
    try:
        assert success == "Email sent: 'CRT - No capacity' to testing@test.com via govDelivery TMS"
    except AssertionError:
        assert success == 'testing@test.com not in allowed domains, not attempting to deliver CRT - No capacity.'


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
@features.login_as_superuser_with_feature('separate-referrals-workflow')
@reporting.capture_report('contact_complainant_modal_optionals.pdf')
def test_contact_complainant_modal_optionals(page, *, report):
    admin_models.update(
        page,
        admin_path='/admin/cts_forms/responsetemplate',
        filters={'title': 'EXAMPLE - Optional Sections'},
        show_in_dropdown=True,
    )

    page.goto("/form/view/?contact_first_name=Testing&contact_last_name=Tester")

    assert page.is_visible("#filters-form")

    with page.expect_navigation():
        page.evaluate("document.querySelector('.td-link').click()")

    report_id = page.locator('.details-id h2').text_content().split(':')[1].split('-')[0].strip()

    page.locator('button').filter(has_text="Contact complainant").click()

    modal = page.locator('#intake_template')

    report.screenshot(page, full_page=True, caption='Upon clicking "Contact Complaint" from the Report Details page, users will be presented with this modal.')

    modal.locator('select').filter(has_text='[Select response letter]').select_option('EXAMPLE - Optional Sections')

    modal.locator('#intake_description').filter(has_text='Your Civil Rights Division Report').wait_for()
    modal.locator('#intake_letter_html').filter(has_text='Dear Testing Tester').wait_for()
    modal.locator('.optionals').filter(has_text='Big Headers').wait_for()

    report.screenshot(page, full_page=True, scroll_to_selector='.optionals', caption='Upon selecting a template with optional sections, users will be presented with the optional sections. These sections can be toggled on and off by clicking the checkbox next to the section name.')

    html = modal.locator('#intake_letter_html').filter(has_text='Dear Testing Tester')
    html.wait_for()
    assert 'How you have helped:' not in html.text_content()
    assert 'American Bar Association' not in html.text_content()
    modal.locator('label').filter(has_text='How you have helped').click()
    modal.locator('label').filter(has_text='American Bar').click()
    modal.locator('#intake_letter_html').filter(has_text='How you have helped:').wait_for()
    modal.locator('#intake_letter_html').filter(has_text='American Bar Association').wait_for()

    report.screenshot(page, full_page=True, scroll_to_selector='#intake_letter_html', caption='For example, selecting "How you have helped" and "American Bar" will add those sections to the letter. The content of these templates can be changed by application administrators.')

    with page.expect_navigation():
        modal.locator('button').filter(has_text="Send").click()

    page.locator('.usa-alert--success').wait_for()

    page.goto(f"/admin/tms/tmsemail/?report={report_id}")

    with page.expect_navigation():
        page.locator('.field-tms_id a').nth(0).click()

    tms_html_body = page.locator('.field-html_body')
    assert 'How you have helped:' in tms_html_body.text_content()
    assert 'American Bar Association' in tms_html_body.text_content()
    assert 'What you can do' not in tms_html_body.text_content()

    tms_body = page.locator('.field-body')
    assert 'How you have helped:' in tms_body.text_content()
    assert 'American Bar Association' in tms_body.text_content()
    assert 'What you can do' not in tms_body.text_content()

    page.locator('.field-html_body').filter(has_text='American Bar Association').wait_for()

    page.locator('.field-body').filter(has_text='American Bar Association').wait_for()

    admin_models.update(
        page,
        admin_path='/admin/cts_forms/responsetemplate',
        filters={'title': 'EXAMPLE - Optional Sections'},
        show_in_dropdown=False,
    )
