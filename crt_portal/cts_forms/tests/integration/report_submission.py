import pytest

from .form_utils import (
    next_step,
    click_button,
    fill_public_form
)


@pytest.mark.only_browser("chromium")
def test_error_if_form_refreshed(page, base_url):

    page.goto("/report")
    # We'll complete the first step
    page.check("input[name='0-servicemember']")
    click_button(page, 'Next')
    with page.expect_navigation():
        click_button(page, "No, I don't want to provide it")

    # Refresh the page in another tab
    new_tab = page.context.new_page()
    new_tab.goto(f"{base_url}/report")

    # Now try and progress on original tab where we're still on step #2
    assert page.title() == "Step 2: Primary concern - Contact the Civil Rights Division | Department of Justice"
    page.check("#id_1-primary_complaint_0")
    response = next_step(page)

    # Now we've got an error page on the original tab
    assert response.status == 422
    assert "We're sorry, something went wrong" in response.text()


@pytest.mark.only_browser("chromium")
def test_report_complete_and_valid_submission(page):
    fill_public_form(page)
