"""Compatibility functions for different ways we might run tests."""
import functools


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
