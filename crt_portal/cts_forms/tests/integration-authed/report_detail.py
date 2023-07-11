import pytest

from auth import login_as_superuser


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
