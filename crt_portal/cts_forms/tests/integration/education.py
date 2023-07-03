import pytest


@pytest.mark.only_browser("chromium")
def test_education_accordion(page):
    page.goto('/')

    assert not page.locator('#crt-landing-hate_crime--example').is_visible()

    page.locator('.crt-landing--example_option').filter(has_text="Victim of a hate crime").click()

    assert page.locator('p').filter(has_text="Attacks, threats of violence, or destruction of property at place of worship").is_visible()
    assert page.locator('a').filter(has_text="Get help for hate crimes").is_visible()
