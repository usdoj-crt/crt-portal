import pytest

from auth import login_as_superuser


@pytest.mark.only_browser("chromium")
def test_close_report_via_bulk_actions(page):
    """Filters and takes action on an open report."""
    print('Note: this test assumes that report_submission.py was run first')
    login_as_superuser(page)

    page.goto("/form/view")

    assert page.is_visible("#filters-form")

    page.fill("input[name='contact_first_name']", "Testing")
    page.fill("input[name='contact_last_name']", "Tester")
    with page.expect_navigation():
        page.evaluate("document.getElementById('apply-filters-button').click()")

    # This should be the bulk action checkbox:
    page.evaluate("document.querySelector('.tr-status-new input[type=\"checkbox\"]').click()")

    with page.expect_navigation():
        page.evaluate("document.getElementById('actions').click()")

    page.select_option('select#id_status', 'closed')
    page.fill("textarea[name='comment']", "Closed by end-to-end test user.")

    apply_action = page.locator('button[name="selected_ids"]')
    assert apply_action.is_enabled()
    with page.expect_navigation():
        apply_action.click()

    alert = page.locator('#status-update .usa-alert__text').text_content().strip()
    assert alert == '1 record has been updated: status set to closed'
