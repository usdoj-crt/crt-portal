import functools
import pytest

IGNORE = [
    'Retrying preview',  # Happens when a preview API request is canceled.
]


def _record_error(container, message, ignore=None):
    if message.type != 'error':
        return

    if ignore is None:
        ignore = []

    if isinstance(ignore, str):
        ignore = [ignore]

    ignore = [*IGNORE, *ignore]

    if any(i in message.text for i in ignore):
        return

    if 'failed to fetch' in message.text.lower():
        return  # When racing between pages in tests, requests get canceled.

    line = message.location.get('lineNumber', -1)
    column = message.location.get('columnNumber', -1)
    url = message.location.get('url', '')

    if url and any(i in url for i in ignore):
        return

    container.append(
        f'{message.text}\n'
        f'    - url: {url}\n'
        f'    - line: {line}\n'
        f'    - column: {column}\n'
    )


def raise_errors(ignore=None):
    """Fails pytest when console errors are present.

    Args:
        ignore: Error messages (matched on text) to not raise on.
    """
    def wrapper(func):
        @functools.wraps(func)
        def decorator(page, *args, **kwargs):
            errors = []
            page.on("console", lambda message: _record_error(errors, message, ignore=ignore))
            result = func(page, *args, **kwargs)
            if not errors:
                return result
            error_text = '\n'.join([f'  - {error}' for error in errors])
            pytest.fail(f'Console errors were present on {page.url}:\n{error_text}')
        return decorator
    return wrapper
