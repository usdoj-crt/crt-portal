import sys
import time
import urllib.parse

import pytest

from .auth import login_as_superuser
from ..integration.form_utils import (
    fill_public_form,
    click_button,
    disable_javascript,
)


@pytest.mark.only_browser("chromium")
def test_report_complete_and_valid_submission(page, base_url):
    nojs_page = disable_javascript(page, base_url)
    nojs_page.goto(f"{base_url}/report")

    now = time.time_ns()
    duplicate_email = f'{now}-duplicate@test.com'
    fill_public_form(nojs_page, contact_email=duplicate_email)

    review = nojs_page.locator('.crt-portal-card', has_text='Review your Report')
    submit = review.locator('input,button,a', has_text='Submit report')
    new_tab_key = "Meta" if sys.platform == "darwin" else "Control"
    for _ in range(3):
        submit.click(modifiers=[new_tab_key])

    submitted_pages = nojs_page.context.pages
    nojs_page.close()
    for submitted in submitted_pages:
        if submitted.is_closed():
            continue
        submitted.wait_for_load_state('networkidle')
        assert submitted.title() == "Submission complete"

    admin_page = page

    login_as_superuser(admin_page)

    escaped_email = urllib.parse.quote(duplicate_email)
    admin_page.goto(f'/form/view/?contact_email={escaped_email}')
    admin_page.fill("input[name='contact_email']", duplicate_email)
    with admin_page.expect_navigation():
        click_button(admin_page, 'Apply filters')

    assert len(admin_page.locator('.crt-table .tr-status-new').all()) == 1
    page.pause()
