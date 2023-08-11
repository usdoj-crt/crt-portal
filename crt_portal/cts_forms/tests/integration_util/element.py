def normalize_text(locator) -> str:
    """Returns the text content of the first element matching the locator.

    - Removes trailing and leading whitespace.
    - Any other whitespace is replaced with a single space.
    """
    return ' '.join(locator.text_content().strip().split())
