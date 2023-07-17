import pytest

from auth import login_as_superuser, get_test_credentials
from features_per_user import toggle_feature_for_user


@pytest.mark.only_browser("chromium")
@pytest.mark.only
def test_contact_complainant_modal(page):
    """Tests the contact complainant modal."""
    login_as_superuser(page)
    username, _ = get_test_credentials()
    toggle_feature_for_user(page=page, feature_name='separate-referrals-workflow', username=username, enable=True)

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
    page.screenshot(path="report_detail_test_6.png", full_page=True)
    with page.expect_navigation():
        page.locator('.outline-button--dark').click()
    page.screenshot(path="e2e-screenshots/report_detail_test_7.png", full_page=True)
    assert page.is_visible("#contact-email-filter")
