def try_to_import():
    """Reads from the test table. Assumes modify ran successfully."""
    try:
        import numpy  # noqa: F401
    except Exception as e:
        return f"Wasn't able to import numpy: {e}"
    return "Imported successfully!"
