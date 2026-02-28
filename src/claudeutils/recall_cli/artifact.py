"""Artifact parser for recall Entry Keys section."""


def parse_entry_keys_section(content: str) -> list[str] | None:
    """Parse Entry Keys section from artifact content.

    Returns list of entry lines from the Entry Keys section, or None if not
    found. Blank lines and comment lines (starting with #) are excluded.
    """
    lines = content.split("\n")

    heading_found = False
    for i, line in enumerate(lines):
        if line.strip() == "## Entry Keys":
            heading_found = True
            # Start collecting from the next line
            entries = []
            for entry_line in lines[i + 1 :]:
                stripped = entry_line.strip()
                if stripped and not stripped.startswith("#"):
                    entries.append(stripped)
            return entries if entries else []

    return None if not heading_found else []
