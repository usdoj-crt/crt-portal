import pytest

@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "userAgent": "SamsungBrowser/i"
    }


@pytest.mark.only_browser("chromium")
def test_unsupported_browser_modal_visible(page):

    page.goto("/report")

    page.waitForSelector("text=NOTICE: Your mobile browser is not compatible with this form", 
        state='visible', 
        timeout=3000)