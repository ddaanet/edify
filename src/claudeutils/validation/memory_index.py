"""Validate memory-index.md entries against semantic headers in indexed files.

Checks:
- All semantic headers (##+ not starting with .) have index entries
- All index entries match at least one semantic header
- No duplicate index entries
- Document intro content (between # and first ##) is exempt
- Entries are in correct file section (autofix by default)
- Entries are in file order within sections (autofix by default)
- Entries pointing to structural sections are removed (autofix)
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from claudeutils.when.fuzzy import score_match

from .memory_index_checks import (
    check_collisions,
    check_entry_sorting,
    check_trigger_format,
)
from .memory_index_helpers import (
    autofix_index,
    check_duplicate_entries,
    check_entry_placement,
    check_orphan_entries,
    check_structural_entries,
    collect_semantic_headers,
    collect_structural_headers,
)

# Section header that specifies a file path
FILE_SECTION = re.compile(r"^## (agents/decisions/\S+\.md)$")


def _extract_entry_key(line: str) -> str | None:
    """Extract key from a line, supporting multiple formats.

    Returns lowercase key for /when, /how, or em-dash formats, or None if
    invalid.
    """
    if line.startswith(("/when ", "/how ")):
        # Parse /when or /how format: extract trigger before pipe
        _, rest = line.split(" ", 1)
        trigger = rest.split("|", 1)[0].strip() if "|" in rest else rest.strip()
        return trigger.lower() if trigger else None
    if " — " in line:
        # Parse em-dash format
        key = line.split(" — ")[0].strip()
        return key.lower() if key else None
    # Bare line without valid format
    return line.lower()


def extract_index_entries(
    index_path: Path | str, root: Path
) -> dict[str, tuple[int, str, str]]:
    """Extract index entries from memory-index.md.

    Supports /when, /how, and em-dash formats.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.

    Returns:
        Dict: lowercase key → (line_number, full_entry, section_name)
        When duplicates exist, only the last occurrence is stored.
    """
    entries: dict[str, tuple[int, str, str]] = {}

    try:
        full_path = root / index_path
        lines = full_path.read_text().splitlines()
    except FileNotFoundError:
        return entries

    current_section: str | None = None

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Handle headers - track section state
        if stripped.startswith("##") and not stripped.startswith("###"):
            current_section = stripped[3:] if stripped.startswith("## ") else None
            continue

        # Skip non-entries
        if not stripped or stripped.startswith(("#", "**", "- ")):
            continue

        # In a section, parse entry
        if current_section:
            key = _extract_entry_key(stripped)
            if key:
                entries[key] = (i, stripped, current_section)

    return entries


def _check_orphan_headers(
    headers: dict[str, list[tuple[str, int, str]]],
    entries: dict[str, tuple[int, str, str]],
) -> list[str]:
    """Check for semantic headers without index entries.

    Uses fuzzy matching to bridge compression between semantic headers and index
    triggers (e.g., "When Writing Mock Tests" fuzzy-matches "write mock test").
    """
    errors = []
    entry_keys = list(entries.keys())
    threshold = 50.0

    for title, locations in sorted(headers.items()):
        # Exact match first
        if title in entries:
            continue

        # Fuzzy match: entry keys are substrings of header titles, so we
        # score each entry key against the header title
        best_score = 0.0
        for entry_key in entry_keys:
            score = score_match(entry_key, title)
            best_score = max(best_score, score)

        # If no match found (exact or fuzzy above threshold), report error
        if best_score < threshold:
            for filepath, lineno, level in locations:
                errors.append(
                    f"  {filepath}:{lineno}: orphan semantic header '{title}' "
                    f"({level} level) has no memory-index.md entry"
                )

    return errors


def _check_duplicate_headers(
    headers: dict[str, list[tuple[str, int, str]]],
) -> list[str]:
    """Check for duplicate headers across files."""
    errors = []
    for title, locations in sorted(headers.items()):
        if len(locations) > 1:
            files = {filepath for filepath, _, _ in locations}
            if len(files) > 1:  # Only error if duplicates are in different files
                errors.append(f"  Duplicate header '{title}' found in multiple files:")
                for filepath, lineno, level in locations:
                    errors.append(f"    {filepath}:{lineno} ({level} level)")
    return errors


@dataclass(slots=True)
class _AutofixContext:
    """Context for autofix operations."""

    index_path: Path | str
    root: Path
    headers: dict[str, list[tuple[str, int, str]]]
    structural: set[str]


def _apply_autofix(
    ctx: _AutofixContext,
    placement_count: int,
    ordering_count: int,
    structural_count: int,
) -> bool:
    """Apply autofix and report summary.

    Returns True if successful.
    """
    fixed = autofix_index(ctx.index_path, ctx.root, ctx.headers, ctx.structural)
    if not fixed:
        return False

    # Report summary
    parts = []
    if placement_count:
        parts.append(f"{placement_count} placement")
    if ordering_count:
        parts.append(f"{ordering_count} ordering")
    if structural_count:
        parts.append(f"{structural_count} structural")
    print(f"Autofixed {' and '.join(parts)} issues", file=sys.stderr)
    return True


def _handle_autofix_errors(
    placement_errors: list[str],
    ordering_errors: list[str],
    structural_entries: list[str],
    *,
    autofix: bool,
    ctx: _AutofixContext,
) -> list[str]:
    """Handle autofixable errors — apply autofix or report as errors."""
    if not (placement_errors or ordering_errors or structural_entries):
        return []

    all_errors = placement_errors + ordering_errors + structural_entries

    if not autofix:
        return all_errors

    # Attempt autofix
    success = _apply_autofix(
        ctx,
        placement_count=len(placement_errors),
        ordering_count=len(ordering_errors),
        structural_count=len(structural_entries),
    )

    return [] if success else all_errors


def validate(index_path: Path | str, root: Path, *, autofix: bool = True) -> list[str]:
    """Validate memory index.

    Returns list of error strings.

    Autofix is enabled by default for section placement, ordering,
    and structural section cleanup.

    Args:
        index_path: Path to memory-index.md (relative to root).
        root: Project root directory.
        autofix: Whether to autofix placement/ordering/structural issues.

    Returns:
        List of error messages. Empty list if no errors found.
    """
    headers = collect_semantic_headers(root)
    structural = collect_structural_headers(root)
    entries = extract_index_entries(index_path, root)

    errors = []

    # Non-autofixable checks
    errors.extend(check_duplicate_entries(index_path, root))
    errors.extend(check_trigger_format(entries))
    errors.extend(_check_orphan_headers(headers, entries))
    errors.extend(check_orphan_entries(entries, headers, structural))
    errors.extend(check_collisions(entries, headers))
    errors.extend(_check_duplicate_headers(headers))

    # Autofixable checks
    placement_errors = check_entry_placement(entries, headers)
    ordering_errors = check_entry_sorting(index_path, root, headers)
    structural_entries = check_structural_entries(entries, structural)

    ctx = _AutofixContext(
        index_path=index_path, root=root, headers=headers, structural=structural
    )
    errors.extend(
        _handle_autofix_errors(
            placement_errors,
            ordering_errors,
            structural_entries,
            autofix=autofix,
            ctx=ctx,
        )
    )

    return errors
