from typing import List


def normalize_text(locator) -> str:
    """Returns the text content of the first element matching the locator.

    - Removes trailing and leading whitespace.
    - Any other whitespace is replaced with a single space.
    """
    return ' '.join(locator.text_content().strip().split())


def all_normalized_text(locator) -> List[str]:
    """Returns the text content all elements matching the locator.

    Only matches visible elements.
    See normalize_text for details on how the text is cleaned.
    """
    return [
        normalize_text(element)
        for element in locator.all()
        if element.is_visible()
    ]
