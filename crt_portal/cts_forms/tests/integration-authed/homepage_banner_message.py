import pytest

from auth import login_as_superuser


@pytest.mark.only_browser("chromium")
def test_can_add_banner_message(page):
    """Filters and takes action on an open report."""
    login_as_superuser(page)

    page.goto("/admin/cts_forms/bannermessage/")

    if page.locator('.paginator').text_content().strip() != '0 banner messages':
        page.click("#action-toggle")
        page.select_option('select[name="action"]', 'delete_selected')
        with page.expect_navigation():
            page.click('button[name="index"]')

        with page.expect_navigation():
            page.click('input[type="submit"]')

    page.goto("/admin/cts_forms/bannermessage/add/")

    page.fill("input[name='order']", "0")
    page.check("input[name='show']")
    page.select_option('select#id_kind', "notice")
    page.fill("#translated-textarea-0", "es _translation_")
    page.fill("#translated-textarea-1", "en _translation_")

    with page.expect_navigation():
        page.click("input[name='_addanother']")

    page.fill("input[name='order']", "1")
    page.check("input[name='show']")
    page.select_option('select#id_kind', "alert")
    page.fill("#translated-textarea-0", "es _translation_")
    page.fill("#translated-textarea-1", "en _translation_")

    with page.expect_navigation():
        page.click("input[name='_addanother']")

    page.fill("input[name='order']", "2")
    page.check("input[name='show']")
    page.select_option('select#id_kind', "emergency")
    page.fill("#translated-textarea-0", "es _translation_")
    page.fill("#translated-textarea-1", "en _translation_")

    with page.expect_navigation():
        page.click("input[name='_addanother']")

    page.fill("input[name='order']", "3")
    page.select_option('select#id_kind', "emergency")
    page.fill("#translated-textarea-1", "hidden")

    with page.expect_navigation():
        page.click("input[name='_save']")

    page.goto("/")

    messages = page.locator('.crt-landing--admin-message').all()

    assert len(messages) == 3
    notice, alert, emergency = messages

    assert notice.text_content().strip() == 'en translation'
    assert alert.text_content().strip() == 'en translation'
    assert emergency.text_content().strip() == 'en translation'
    assert 'crt-landing--admin-message-notice' in notice.get_attribute('class')
    assert 'crt-landing--admin-message-alert' in alert.get_attribute('class')
    assert 'crt-landing--admin-message-emergency' in emergency.get_attribute('class')

    page.select_option("#i8n_select", "es")
    with page.expect_navigation():
        page.click("#language-select")

    assert notice.text_content().strip() == 'es translation'
    assert alert.text_content().strip() == 'es translation'
    assert emergency.text_content().strip() == 'es translation'
