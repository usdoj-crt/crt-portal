import pytest

from cts_forms.tests.integration_util import console, features


@pytest.mark.only_browser("chromium")
@pytest.mark.boop
@console.raise_errors(ignore='404')
@features.login_as_superuser_without_feature('data-dashboard')
def test_flag_off(page):
    page.goto("/form/view")
    assert not page.locator('a').filter(has_text="Data dashboard").is_visible()


@pytest.mark.only_browser("chromium")
@pytest.mark.boop
@console.raise_errors(ignore='404')
@features.login_as_superuser_with_feature('data-dashboard')
def test_dashboard_page(page):
    page.goto("/form/view")

    with page.expect_navigation():
        page.locator('a').filter(has_text="Data dashboard").click()

    assert page.locator('h2').filter(has_text="Data dashboard").is_visible()
