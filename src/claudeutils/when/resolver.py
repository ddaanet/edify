"""Query resolution module for /when command."""


def resolve(_mode: str, query: str, _index_path: str, _decisions_dir: str) -> str:
    """Detect and route query to appropriate resolution mode.

    Detects query prefix to determine resolution mode:
    - ".." prefix → file mode (strip prefix)
    - "." prefix → section mode (strip prefix)
    - No prefix → trigger mode

    Args:
        mode: Initial mode hint
        query: Query string with optional prefix
        index_path: Path to index (unused in mode detection)
        decisions_dir: Decisions directory (unused in mode detection)

    Returns:
        Mode identifier after stripping prefix
    """
    if query.startswith(".."):
        return "file"
    if query.startswith("."):
        return "section"
    return "trigger"
