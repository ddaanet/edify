"""Artifact parser for recall Entry Keys section."""


def parse_trigger(entry_line: str) -> str:
    """Strip annotation and normalize operator prefix for resolver lookup."""
    # Strip annotation: split on first ' — ' and take left side
    base = entry_line.split(" — ", maxsplit=1)[0].strip()

    # Detect operator: check if first word (lowercased) is when/how
    first_word = base.split()[0].lower() if base.split() else ""
    if first_word in {"when", "how"}:
        return base

    # Bare trigger: prepend "when "
    return f"when {base}"


def parse_entry_keys_section(content: str) -> list[str] | None:
    """Parse Entry Keys section from artifact content.

    Returns list of entry lines from the Entry Keys section, or None if not
    found. Blank lines and comment lines (starting with #) are excluded.
    """
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if line.strip() == "## Entry Keys":
            # Start collecting from the next line
            entries = []
            for entry_line in lines[i + 1 :]:
                stripped = entry_line.strip()
                if stripped and not stripped.startswith("#"):
                    entries.append(stripped)
            return entries or []

    return None
