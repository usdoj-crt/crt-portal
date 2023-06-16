def try_to_import_prod():
    """Reads from the test table. Assumes modify ran successfully."""
    try:
        import numpy  # noqa: F401
    except Exception as e:
        return f"Wasn't able to import numpy: {e}"
    return "Imported successfully!"


def try_to_import_dev():
    """Reads from the test table. Assumes modify ran successfully."""
    try:
        import pandas  # noqa: F401
    except Exception:
        return "Import failed as expected"
    return "Uhoh, a dev package was installed on prod"
