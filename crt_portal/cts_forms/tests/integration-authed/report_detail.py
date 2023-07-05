import pytest

from auth import login_as_superuser


@pytest.mark.only_browser("chromium")
def test_click_back_to_all(page):
    """Opens report detail page and goes back to reports page"""

    login_as_superuser(page)

    page.goto("/form/view")
    total_results = page.evaluate("document.querySelector('.intake-pagination').innerText.split(' ')[5]")
    first_result = page.evaluate("document.querySelector('.stripe > td > .td-checkbox > input').value")

    with page.expect_navigation():
        page.evaluate("document.querySelector('.td-link').click()")

    report_id = page.locator('.details-id > h2').text_content()
    assert first_result in report_id
    pagination = page.locator('.usa-pagination > span').text_content().strip()
    assert pagination == '1 of ' + total_results + ' records'

    assert page.is_visible("#contact-info")

    with page.expect_navigation():
        page.evaluate("document.querySelector('.next > a').click()")

    pagination = page.locator('.usa-pagination > span').text_content().strip()
    assert pagination == '2 of ' + total_results + ' records'

    with page.expect_navigation():
        page.evaluate("document.querySelector('.next > a').click()")

    pagination = page.locator('.usa-pagination > span').text_content().strip()
    assert pagination == '3 of ' + total_results + ' records'

    with page.expect_navigation():
        page.evaluate("document.querySelector('.prev > a').click()")

    pagination = page.locator('.usa-pagination > span').text_content().strip()
    assert pagination == '2 of ' + total_results + ' records'

    with page.expect_navigation():
        page.locator('.outline-button--dark').click()

    assert page.is_visible("#contact-email-filter")
