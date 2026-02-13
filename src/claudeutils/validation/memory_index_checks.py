"""Check functions for memory index validation.

Contains validation check functions extracted from memory_index_helpers.py.
"""

import re
from pathlib import Path

from .memory_index_helpers import EXEMPT_SECTIONS, extract_index_structure


def check_duplicate_entries(index_path: Path | str, root: Path) -> list[str]:
    """Check for duplicate index entries.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.

    Returns:
        List of error messages for duplicate entries.
    """
    errors: list[str] = []
    try:
        if isinstance(index_path, str):
            full_path = root / index_path
        else:
            full_path = root / index_path
        lines = full_path.read_text().splitlines()
    except FileNotFoundError:
        return errors

    seen_entry_keys: dict[str, int] = {}
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip non-entry lines
        if not stripped or stripped.startswith(("#", "**", "- ")):
            continue
        # Extract key
        key = (
            stripped.split(" — ")[0].lower() if " — " in stripped else stripped.lower()
        )
        # Check for duplicates
        if key in seen_entry_keys:
            errors.append(
                f"  memory-index.md:{i}: duplicate index entry '{key}' "
                f"(first at line {seen_entry_keys[key]})"
            )
        else:
            seen_entry_keys[key] = i

    return errors


def check_trigger_format(entries: dict[str, tuple[int, str, str]]) -> list[str]:
    """Check entries for /when or /how format with valid trigger.

    Args:
        entries: Dictionary of entries from extract_index_entries.

    Returns:
        List of error messages.
    """
    errors = []
    for lineno, full_entry, section in entries.values():
        # Skip entries in exempt sections (preserved as-is)
        if section in EXEMPT_SECTIONS:
            continue

        stripped = full_entry.strip()

        # Check operator prefix
        if not stripped.startswith(("/when ", "/how ")):
            # Allow /when and /how without trailing space
            # (empty trigger case handled below)
            if stripped in ("/when", "/how"):
                operator = stripped
                trigger = ""
            elif stripped.startswith(("/when ", "/how ")):
                # Valid prefix with space
                operator = stripped.split(" ", 1)[0]
                trigger = stripped.split(" ", 1)[1] if " " in stripped else ""
            else:
                # Invalid operator or no operator
                if stripped.startswith("/"):
                    # Invalid operator like /what
                    errors.append(
                        f"  memory-index.md:{lineno}: invalid operator "
                        f"prefix (use /when or /how): '{full_entry}'"
                    )
                else:
                    # No operator (old em-dash format)
                    errors.append(
                        f"  memory-index.md:{lineno}: entry missing "
                        f"operator prefix (no operator prefix): "
                        f"'{full_entry}'"
                    )
                continue
        else:
            # Valid operator prefix
            operator = stripped.split(" ", 1)[0]
            trigger = stripped.split(" ", 1)[1] if " " in stripped else ""

        # Check trigger non-empty after stripping
        trigger = trigger.split("|", 1)[0].strip() if trigger else ""
        if not trigger:
            errors.append(
                f"  memory-index.md:{lineno}: {operator} has "
                f"empty trigger: '{full_entry}'"
            )

    return errors


def check_entry_placement(
    entries: dict[str, tuple[int, str, str]],
    headers: dict[str, list[tuple[str, int, str]]],
) -> list[str]:
    """Check that entries are in correct file sections.

    Args:
        entries: Dictionary of entries from extract_index_entries.
        headers: Dictionary of semantic headers from collect_semantic_headers.

    Returns:
        List of error messages for misplaced entries.
    """
    errors = []
    for key, (lineno, _full_entry, section) in entries.items():
        if section in EXEMPT_SECTIONS:
            continue
        if key in headers:
            # Get the file this header is in
            source_file = headers[key][0][0]  # First location's file
            if section != source_file:
                errors.append(
                    f"  memory-index.md:{lineno}: entry '{key}' in section "
                    f"'{section}' but header is in '{source_file}'"
                )
    return errors


def check_entry_sorting(
    index_path: Path | str,
    root: Path,
    headers: dict[str, list[tuple[str, int, str]]],
) -> list[str]:
    """Check that entries within sections match file order.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.
        headers: Dictionary of semantic headers from collect_semantic_headers.

    Returns:
        List of error messages for out-of-order entries.
    """
    # Section header that specifies a file path
    file_section = re.compile(r"^## (agents/decisions/\S+\.md)$")

    errors = []
    _preamble, sections = extract_index_structure(index_path, root)
    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            continue
        # Check if this section is a file path
        if not file_section.match(f"## {section_name}"):
            continue

        # Get entries with their source line numbers
        entry_positions = []
        for entry in entry_lines:
            # Extract key using same logic as _extract_entry_key
            if entry.startswith(("/when ", "/how ")):
                _, rest = entry.split(" ", 1)
                key = rest.split("|", 1)[0].strip().lower()
            elif " — " in entry:
                key = entry.split(" — ")[0].lower()
            else:
                key = entry.lower()
            if key in headers:
                source_lineno = headers[key][0][1]  # Line number in source file
                entry_positions.append((source_lineno, entry))

        # Check if sorted by source line number
        sorted_positions = sorted(entry_positions)
        if entry_positions != sorted_positions:
            errors.append(f"  Section '{section_name}': entries not in file order")

    return errors


def check_orphan_entries(
    entries: dict[str, tuple[int, str, str]],
    headers: dict[str, list[tuple[str, int, str]]],
    structural: set[str],
) -> list[str]:
    """Check for orphan index entries (no matching headers).

    Args:
        entries: Dictionary of entries from extract_index_entries.
        headers: Dictionary of semantic headers from collect_semantic_headers.
        structural: Set of structural header titles.

    Returns:
        List of error messages for orphan entries.
    """
    errors = []
    for key, (lineno, _full_entry, section) in entries.items():
        # Skip exempt sections
        if section in EXEMPT_SECTIONS:
            continue
        # Skip entries pointing to structural sections (will be removed by autofix)
        if key in structural:
            continue
        if key not in headers:
            errors.append(
                f"  memory-index.md:{lineno}: orphan index entry '{key}' "
                f"has no matching semantic header in agents/decisions/"
            )
    return errors


def check_structural_entries(
    entries: dict[str, tuple[int, str, str]], structural: set[str]
) -> list[str]:
    """Check for entries pointing to structural sections.

    Args:
        entries: Dictionary of entries from extract_index_entries.
        structural: Set of structural header titles.

    Returns:
        List of error messages for structural entries.
    """
    errors = []
    for key, (lineno, _full_entry, section) in entries.items():
        if section in EXEMPT_SECTIONS:
            continue
        if key in structural:
            errors.append(
                f"  memory-index.md:{lineno}: entry '{key}' points to "
                f"structural section"
            )
    return errors
