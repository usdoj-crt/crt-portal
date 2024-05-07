"""Compatibility functions for different ways we might run tests."""
import functools
import os
import dotenv

dotenv.load_dotenv()


def _hide_toolbar(page):
    return page.evaluate('document.getElementById("djDebug")?.remove()')


def hide_django_debug_toolbar(func):
    """Hides the Django Debug Toolbar.

    Args:
        func: The test function to decorate.
    """
    @functools.wraps(func)
    def decorator(page, *args, **kwargs):
        page.on('load', _hide_toolbar)
        return func(page, *args, **kwargs)
    return decorator


def defeat_challenge(func):
    """Disables challenge for requests.

    Args:
        func: The test function to decorate.
    """
    @functools.wraps(func)
    def decorator(page, *args, **kwargs):
        extra_headers = {
            'X-Challenge-Defeat': os.environ['CHALLENGE_DEFEAT_KEY']
        }

        page.context.set_extra_http_headers(extra_headers)

        return func(page, *args, **kwargs)
    return decorator
