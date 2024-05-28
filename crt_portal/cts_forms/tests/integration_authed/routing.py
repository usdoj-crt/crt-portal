import pytest

from cts_forms.tests.integration_authed.auth import login_as_superuser
from cts_forms.tests.integration_util import console, reporting


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore=['404', 'The user aborted a request.'])
@reporting.capture_report('refer_complaint_modal_with_email.pdf')
def test_complaint_routing_guide(page, *, report):
    login_as_superuser(page)

    page.goto('/form/view/1/routing-guide/')
    assert page.locator('p').filter(has_text='This guide is intended to help intake specialists').is_visible()
    report.screenshot(page, full_page=True, caption='The routing guide is a tool to help you determine the correct path for a complaint.')


@pytest.mark.only_browser("chromium")
@console.raise_errors(ignore=['404', 'The user aborted a request.'])
@reporting.capture_report('refer_complaint_modal_with_email.pdf')
def test_disposition_routing_guide(page, *, report):
    login_as_superuser(page)

    page.goto('/form/view/1/disposition-guide/')
    assert page.locator('p').filter(has_text='This guide is intended to help intake specialists').is_visible()
    report.screenshot(page, full_page=True, caption='The routing guide is a tool to help you determine the correct path for a complaint.')
