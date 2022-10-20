import pytest


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):  # pragma: no cover
    return {
        **browser_context_args,
        "user_agent": "SamsungBrowser"
    }


@pytest.mark.only_browser("chromium")
def test_unsupported_browser_modal_visible(page):  # pragma: no cover

    page.goto("/report")

    page.wait_for_selector("text=NOTICE: Your mobile browser is not compatible with this form",
                           state='visible',
                           timeout=3000)
