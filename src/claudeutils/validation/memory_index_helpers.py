"""Helper functions for memory index validation."""

import re
from pathlib import Path

# Semantic header: ##+ followed by space and non-dot
SEMANTIC_HEADER = re.compile(r"^(##+) ([^.].+)$")
# Structural header: ##+ followed by space and dot
STRUCTURAL_HEADER = re.compile(r"^(##+) \..+$")
# Document title
DOC_TITLE = re.compile(r"^# .+$")

# Files that contain semantic headers requiring index entries
INDEXED_GLOBS = [
    "agents/decisions/*.md",
]

# Sections that are exempt from file-based validation
EXEMPT_SECTIONS = {
    "Behavioral Rules (fragments — already loaded)",
    "Technical Decisions (mixed — check entry for specific file)",
}


def collect_structural_headers(root: Path) -> set[str]:
    """Scan indexed files for dot-prefixed structural headers."""
    structural = set()

    for glob_pattern in INDEXED_GLOBS:
        for filepath in sorted(root.glob(glob_pattern)):
            try:
                lines = filepath.read_text().splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            for line in lines:
                stripped = line.strip()
                match = STRUCTURAL_HEADER.match(stripped)
                if match:
                    full = stripped.split(" ", 1)[1]
                    title = full[1:]
                    structural.add(title.lower())

    return structural


def collect_semantic_headers(root: Path) -> dict[str, list[tuple[str, int, str]]]:
    """Scan indexed files for semantic headers.

    Returns dict: lowercase title -> list of (file_path, line_number, header_level).
    """
    headers: dict[str, list[tuple[str, int, str]]] = {}

    for glob_pattern in INDEXED_GLOBS:
        for filepath in sorted(root.glob(glob_pattern)):
            rel = str(filepath.relative_to(root))
            try:
                lines = filepath.read_text().splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            in_doc_intro = False
            seen_first_h2 = False

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                if not seen_first_h2 and DOC_TITLE.match(stripped):
                    in_doc_intro = True
                    continue

                if in_doc_intro and stripped.startswith("## "):
                    in_doc_intro = False
                    seen_first_h2 = True

                if in_doc_intro:
                    continue

                m = SEMANTIC_HEADER.match(stripped)
                if m:
                    level = m.group(1)
                    title = m.group(2)
                    key = title.lower()
                    headers.setdefault(key, []).append((rel, i, level))

    return headers


def _resolve_index_path(index_path: Path | str, root: Path) -> Path:
    """Resolve index_path relative to root."""
    return root / index_path


def extract_index_structure(
    index_path: Path | str, root: Path
) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Extract full index structure: (preamble lines, [(section_name, entries)])."""
    try:
        lines = _resolve_index_path(index_path, root).read_text().splitlines()
    except FileNotFoundError:
        return [], []

    preamble: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current_section: str | None = None
    current_entries: list[str] = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## ") and not stripped.startswith("### "):
            if current_section is not None:
                sections.append((current_section, current_entries))
            current_section = stripped[3:]
            current_entries = []
            continue

        if current_section is None:
            preamble.append(line)
            continue

        if not stripped or stripped.startswith("**"):
            continue

        current_entries.append(stripped)

    if current_section is not None:
        sections.append((current_section, current_entries))

    return preamble, sections


def _build_file_entries_map(
    sections: list[tuple[str, list[str]]],
    headers: dict[str, list[tuple[str, int, str]]],
    structural: set[str],
) -> dict[str, list[tuple[int, str]]]:
    """Build map from file paths to sorted entries."""
    file_entries: dict[str, list[tuple[int, str]]] = {}

    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            continue
        for entry in entry_lines:
            # Extract key using same logic as _extract_entry_key in memory_index.py
            if entry.startswith(("/when ", "/how ")):
                _, rest = entry.split(" ", 1)
                key = rest.split("|", 1)[0].strip().lower()
            elif " — " in entry:
                key = entry.split(" — ")[0].lower()
            else:
                key = entry.lower()
            if key in structural:
                continue
            if key in headers:
                source_file = headers[key][0][0]
                source_lineno = headers[key][0][1]
                file_entries.setdefault(source_file, []).append((source_lineno, entry))

    for entries_list in file_entries.values():
        entries_list.sort()

    return file_entries


def _rebuild_index_content(
    preamble: list[str],
    sections: list[tuple[str, list[str]]],
    file_entries: dict[str, list[tuple[int, str]]],
) -> list[str]:
    """Rebuild index: preamble, exempt sections, then file sections sorted."""
    output = list(preamble)

    for section_name, entry_lines in sections:
        if section_name in EXEMPT_SECTIONS:
            output.append(f"\n## {section_name}\n")
            output.extend(entry_lines)

    for filepath in sorted(file_entries.keys()):
        output.append(f"\n## {filepath}\n")
        for _, entry in file_entries[filepath]:
            output.append(entry)

    return output


def autofix_index(
    index_path: Path | str,
    root: Path,
    headers: dict[str, list[tuple[str, int, str]]],
    structural: set[str] | None = None,
) -> bool:
    """Rewrite memory-index.md with correct sections and order."""
    if structural is None:
        structural = set()

    preamble, sections = extract_index_structure(index_path, root)
    file_entries = _build_file_entries_map(sections, headers, structural)
    output = _rebuild_index_content(preamble, sections, file_entries)

    try:
        _resolve_index_path(index_path, root).write_text("\n".join(output) + "\n")
    except OSError:
        return False
    else:
        return True


def check_duplicate_entries(index_path: Path | str, root: Path) -> list[str]:
    """Check for duplicate index entries."""
    errors: list[str] = []
    try:
        lines = _resolve_index_path(index_path, root).read_text().splitlines()
    except FileNotFoundError:
        return errors

    seen: dict[str, int] = {}
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "**", "- ")):
            continue
        key = (
            stripped.split(" — ")[0].lower() if " — " in stripped else stripped.lower()
        )
        if key in seen:
            errors.append(
                f"  memory-index.md:{i}: duplicate index entry '{key}' "
                f"(first at line {seen[key]})"
            )
        else:
            seen[key] = i

    return errors


def check_em_dash_and_word_count(entries: dict[str, tuple[int, str, str]]) -> list[str]:
    """Check entries for em-dash separator and 8-15 word count."""
    errors = []
    for lineno, full_entry, _section in entries.values():
        if " — " not in full_entry:
            errors.append(
                f"  memory-index.md:{lineno}: entry lacks em-dash separator "
                f"(D-3): '{full_entry}'"
            )
        else:
            # Check word count (8-15 word hard limit for key + description total)
            word_count = len(full_entry.split())
            if word_count < 8 or word_count > 15:
                errors.append(
                    f"  memory-index.md:{lineno}: entry has {word_count} words, "
                    f"must be 8-15: '{full_entry}'"
                )
    return errors


def check_entry_placement(
    entries: dict[str, tuple[int, str, str]],
    headers: dict[str, list[tuple[str, int, str]]],
) -> list[str]:
    """Check that entries are in correct file sections."""
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


def check_orphan_entries(
    entries: dict[str, tuple[int, str, str]],
    headers: dict[str, list[tuple[str, int, str]]],
    structural: set[str],
) -> list[str]:
    """Check for orphan index entries with no matching semantic headers."""
    errors = []
    for key, (lineno, _full_entry, section) in entries.items():
        if section in EXEMPT_SECTIONS or key in structural:
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
    """Check for entries pointing to structural (dot-prefixed) sections."""
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
