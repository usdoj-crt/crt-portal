import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, reporting


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
@reporting.capture_report('notification_management.pdf')
def test_notification_management(page, *, report):
    login_as_superuser(page)
    page.goto('/form/notifications/')

    report.screenshot(page, full_page=True, caption='''
<p>The notification management page allows you to decide what automatic emails you receive from the portal.</p>

<p>Currently, you can choose to receive emails when:</p>
<ul>
    <li>You are assigned to a report</li>
</ul>
''')

    assert page.locator('h2').filter(has_text='Notification management').is_visible()
    assert page.locator('td').filter(has_text='Complaint assignments').is_visible()
    page.locator('label').filter(has_text='None').click()
    with page.expect_navigation():
        page.locator('button').filter(has_text='Save preferences').click()

    page.locator('label').filter(has_text='Individual').click()
    with page.expect_navigation():
        page.locator('button').filter(has_text='Save preferences').click()

    report.screenshot(page, full_page=True, caption='''
<p>To change your preferences, simply select the desired option and click "Save preferences".</p>''')

    assert page.locator('.usa-alert--success').filter(has_text='Your preferences have been saved').is_visible()
