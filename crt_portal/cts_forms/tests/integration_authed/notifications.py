import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser, get_test_credentials
from cts_forms.tests.integration_util import console, reporting, admin_models, element


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


def _set_assignee(page, username):
    page.locator('#id_status').select_option('open')
    page.locator('#id_assigned_to').click()
    if username:
        page.locator('#id_assigned_to--list li').filter(has_text=username).click()
    else:
        page.keyboard.press('Tab')
        page.keyboard.press('Enter')
    with page.expect_navigation():
        page.locator('button[value="actions"]').click()


def _set_user(page, username, email, preference):
    admin_models.update(page,
                        admin_path='/admin/auth/user',
                        filters={'username': username},
                        **{
                            'email': email,
                            'notification_preference-0-assigned_to': preference,
                        })


def _get_email_content(page):
    return admin_models.read(
        page,
        admin_path='/admin/tms/tmsemail',
        filters={'recipient__contains': 'notifications_test@example.com'},
        fields=['subject', 'body'],
    )


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
def test_notifications_send(page):
    login_as_superuser(page)
    report_id = admin_models.create_report(
        page,
        crt_reciept_month='12',
        crt_reciept_day='25',
        crt_reciept_year='2000',
        intake_format_2='phone',
        primary_complaint='something_else',
    )
    username, _ = get_test_credentials()

    _set_user(page, username, '', 'individual')
    page.goto(f'/form/view/{report_id}')
    _set_assignee(page, '')
    _set_assignee(page, username)
    assert page.locator('.usa-alert--success').filter(has_text=f'will not be notified because they do not have an email address listed').is_visible()

    _set_user(page, username, 'notifications_test@example.com', 'individual')
    page.goto(f'/form/view/{report_id}')
    _set_assignee(page, '')
    _set_assignee(page, username)
    assert page.locator('.usa-alert--success').filter(has_text=f'{username} will be notified').is_visible()
    sent = _get_email_content(page)
    assert f'You have been assigned [Report {report_id}](/form/view/{report_id})' in sent['body']
    assert sent['subject'] == f'[CRT Portal] Assigned: Report {report_id}'

    _set_user(page, username, 'notifications_test@example.com', 'weekly')
    page.goto(f'/form/view/{report_id}')
    _set_assignee(page, '')
    _set_assignee(page, username)
    assert page.locator('.usa-alert--success').filter(has_text=f'{username} will be notified').is_visible()

    admin_models.delete(page,
                        '/admin/cts_forms/savedsearch',
                        name__contains='Test search for notifications')
    page.goto('/form/saved-searches/actions/new')
    page.locator('#id_name').fill('Test search for notifications')
    page.locator('#id_query').fill('violation_summary=test_for_search_notifications')
    page.locator('label').filter(has_text='Weekly Digest').click()
    with page.expect_navigation():
        page.locator('button').filter(has_text='Add').click()

    admin_models.create_report(
        page,
        crt_reciept_month='02',
        crt_reciept_day='01',
        crt_reciept_year='2020',
        intake_format_2='phone',
        primary_complaint='something_else',
        violation_summary='test_for_search_notifications',
    )

    admin_models.update(
        page,
        admin_path='/admin/cts_forms/schedulednotification',
        filters={'recipient__username': username},
        scheduled_for_0='2020-01-01',
    )
    page.goto('/admin/cts_forms/schedulednotification/check_saved_searches/')
    page.goto('/admin/cts_forms/schedulednotification/send_scheduled_notifications/')
    assert 'Sent notification' in element.normalize_text(page.locator('body'))
    sent = _get_email_content(page)
    assert 'You have been assigned to the following reports:' in sent['body']
    assert sent['subject'] == '[CRT Portal] weekly notification digest'

    assert 'new reports matching your search' in sent['body']


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore='404')
def test_group_saved_search_notification(page):
    login_as_superuser(page)
    username, _ = get_test_credentials()
    admin_models.create(
        page,
        '/admin/auth/group',
        name='Group Integration Test',
    )
    saved_search = admin_models.create(
        page,
        '/admin/cts_forms/savedsearch',
        name='Saved Search Integration Test - group notifications',
        query='status=new&status=open&violation_summary=%22group!%22&no_status=false&grouping=default',
        shared=True,
    )
    page.goto('/admin/auth/group/')
    with page.expect_navigation():
        page.locator('a').filter(has_text='Group Integration Test').click()
    option = page.locator('#id_group_preferences-0-admins > option').filter(has_text=username)
    option.click()
    with page.expect_navigation():
        page.click("input[type='submit']")
    page.goto(f'/form/saved-searches/actions/{saved_search}')

    assert page.locator('label').filter(has_text='Group Notifications').is_visible()
    assert page.locator('label').filter(has_text='Group Integration Test').is_visible()
    page.locator('.group-notifications-container label').filter(has_text='Weekly Digest').click()
    with page.expect_navigation():
        page.locator('button').filter(has_text='Apply changes').click()

    assert page.locator('.usa-alert--success').is_visible()
