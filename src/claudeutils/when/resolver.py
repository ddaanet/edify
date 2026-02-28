"""Query resolution module for /when command."""

from pathlib import Path

from claudeutils.when import fuzzy
from claudeutils.when.index_parser import WhenEntry, parse_index


class ResolveError(Exception):
    """Error during resolution."""


def resolve(query: str, index_path: str, decisions_dir: str) -> str:
    """Resolve query to decision file content via prefix-based routing.

    Args:
        query: The search query (bare trigger text)
        index_path: Path to memory index file
        decisions_dir: Path to decisions directory

    Returns:
        Resolved content as string
    """
    if query.startswith(".."):
        return _resolve_file(query[2:].strip(), decisions_dir)
    if query.startswith("."):
        return _resolve_section(query[1:].strip(), decisions_dir)
    return _resolve_trigger(query, index_path, decisions_dir)


def _resolve_file(filename: str, decisions_dir: str) -> str:
    """Resolve filename to file content."""
    dec_dir = Path(decisions_dir)
    file_path = dec_dir / filename

    if not file_path.exists():
        available_files = sorted(dec_dir.glob("*.md"))
        msg = f"File '{filename}' not found in decision files."
        if available_files:
            msg += "\nAvailable:"
            for md_file in available_files:
                msg += f"\n  ..{md_file.name}"
        raise ResolveError(msg)

    return _read_file(file_path)


def _read_file(file_path: Path) -> str:
    """Read file with error handling."""
    try:
        return file_path.read_text()
    except OSError as e:
        msg = f"Failed to read {file_path}: {e}"
        raise ResolveError(msg) from e


def _build_section_not_found_error(
    query: str, heading_to_files: dict[str, list[tuple[Path, str]]]
) -> ResolveError:
    """Format error with available headings (up to 10).

    Args:
        query: Section query that was not found
        heading_to_files: Map of lowercase heading to (file, full_heading_line) tuples

    Returns:
        ResolveError with suggestions list (max 10 headings)
    """
    available_headings = []
    for heading_lower in sorted(heading_to_files.keys()):
        if heading_to_files[heading_lower]:
            full_heading = heading_to_files[heading_lower][0][1]
            # Extract text from full heading line (strip # markers)
            heading_text = full_heading.lstrip("#").strip()
            available_headings.append(f".{heading_text}")

    msg = f"Section '{query}' not found."
    if available_headings:
        suggestions = available_headings[:10]
        msg += "\nAvailable:\n  " + "\n  ".join(suggestions)

    return ResolveError(msg)


def _resolve_section(query: str, decisions_dir: str) -> str:
    """Resolve heading to section content via case-insensitive lookup.

    Now supports H2, H3, H4, etc. headings (not just H2).
    """
    dec_dir = Path(decisions_dir)
    heading_to_files: dict[str, list[tuple[Path, str]]] = {}

    for md_file in sorted(dec_dir.glob("*.md")):
        content = _read_file(md_file)
        for line in content.split("\n"):
            if line.startswith("##"):
                # Extract heading text by stripping all leading # and whitespace
                heading_text = line.lstrip("#").strip()
                if heading_text:
                    heading_lower = heading_text.lower()
                    if heading_lower not in heading_to_files:
                        heading_to_files[heading_lower] = []
                    # Store full heading line (with # markers) for extraction
                    heading_to_files[heading_lower].append((md_file, line.strip()))

    query_lower = query.lower()
    if query_lower not in heading_to_files:
        raise _build_section_not_found_error(query, heading_to_files)

    matches = heading_to_files[query_lower]
    if len(matches) > 1:
        files = ", ".join(str(m[0]) for m in matches)
        msg = f"Ambiguous heading '{query}' found in: {files}"
        raise ResolveError(msg)

    file_path, full_heading = matches[0]
    content = extract_section(file_path, full_heading)
    if not content:
        msg = f"Failed to extract section '{full_heading}' from {file_path}"
        raise ResolveError(msg)

    return content


def _get_suggestions(
    query: str, candidates: list[str], limit: int = 3
) -> list[tuple[str, float]]:
    """Get top fuzzy suggestions sorted by score.

    Uses simple sequential character matching for suggestions (looser than main
    fuzzy engine which has minimum threshold filters).
    """
    scored = []
    query_lower = query.lower()
    for candidate in candidates:
        candidate_lower = candidate.lower()
        matched = 0
        q_idx = 0
        for c in candidate_lower:
            if q_idx < len(query_lower) and c == query_lower[q_idx]:
                matched += 1
                q_idx += 1
        if matched > 0:
            scored.append((candidate, float(matched)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def _handle_no_match(
    query: str, candidates: list[str], entries: list[WhenEntry]
) -> None:
    """Raise ResolveError with fuzzy suggestions.

    Candidates are bare trigger text (no operator prefix). Shows each suggestion
    with its entry's actual operator.
    """
    suggestions = _get_suggestions(query, candidates)
    msg = f"No match for '{query}'"
    if suggestions:
        trigger_to_op = {e.trigger: e.operator for e in entries}
        msg += "\nDid you mean:"
        for trigger, _score in suggestions:
            op = trigger_to_op.get(trigger, "when")
            msg += f"\n  /{op} {trigger}"
    raise ResolveError(msg)


def _load_matched_entry(matched_trigger: str, entries: list[WhenEntry]) -> WhenEntry:
    """Find entry by bare trigger text."""
    for entry in entries:
        if entry.trigger == matched_trigger:
            return entry
    msg = "Could not map matched trigger to entry"
    raise ResolveError(msg)


def _resolve_trigger(query: str, index_path: str, decisions_dir: str) -> str:
    """Resolve trigger via fuzzy matching.

    Args:
        query: The search query (bare trigger text)
        index_path: Path to memory index file
        decisions_dir: Path to decisions directory

    Returns:
        Resolved content with source reference
    """
    index_file = Path(index_path)
    dec_dir = Path(decisions_dir)

    entries = parse_index(index_file)
    # Strip leading "to " — cli.py splits "how to X" → query="to X".
    # Safe to match lowercase only: callers always pass lowercase (memory-index
    # entries use /how, cli.py lowercases the operator check, so "to " prefix
    # is always lowercase when present).
    query = query.removeprefix("to ")
    trigger_candidates = [e.trigger for e in entries]
    matches = fuzzy.rank_matches(query, trigger_candidates, limit=1)

    if not matches:
        _handle_no_match(query, trigger_candidates, entries)

    matched_trigger, _score = matches[0]
    matching_entry = _load_matched_entry(matched_trigger, entries)
    # Section: full path (agents/decisions/cli.md) or bare name
    section_path = Path(matching_entry.section)
    if section_path.suffix == ".md":
        section_filename = section_path.name
    else:
        section_filename = f"{matching_entry.section}.md"
    file_path = dec_dir / section_filename

    if not file_path.exists():
        msg = f"Decision file not found: {file_path}"
        raise ResolveError(msg)

    heading_text = _build_heading(matching_entry.operator, matching_entry.trigger)
    file_content = _read_file(file_path)

    actual_heading = _find_heading(heading_text, file_content)
    if not actual_heading:
        msg = f"Section not found in {file_path}: {heading_text}"
        raise ResolveError(msg)

    content = extract_section(file_path, actual_heading)
    heading_text_only = actual_heading.lstrip("#").strip()

    formatted_heading = f"# {heading_text_only}"
    content_lines = content.split("\n")
    section_content = "\n".join(content_lines[1:]).lstrip()

    # Section path relative to decisions_dir parent (agents/decisions/<file>)
    source_path = f"agents/decisions/{section_filename}"
    output_parts = [formatted_heading, section_content, f"\nSource: {source_path}"]

    return "\n".join(output_parts).rstrip()


def _heading_matches(line: str, target_heading: str) -> bool:
    """Check if line matches target heading (case-insensitive).

    Args:
        line: The line to check (may include leading # markers)
        target_heading: The heading text to match against (may include # markers)

    Returns:
        True if line matches the heading (ignoring case and whitespace)
    """
    line_stripped = line.strip().lower()
    target_stripped = target_heading.strip().lower()

    # Extract heading text (remove # markers for comparison)
    line_text = line_stripped.lstrip("#").strip()
    target_text = target_stripped.lstrip("#").strip()

    return line_text == target_text


def _find_heading(heading_text: str, file_content: str) -> str | None:
    """Find heading in file content, with fuzzy fallback.

    Tries exact case-insensitive match first. Falls back to fuzzy scoring
    when exact match fails (e.g., trigger text omits articles present in heading).

    Args:
        heading_text: Expected heading text (without # markers)
        file_content: Full file content to search

    Returns:
        The matching heading line (with # markers) or None
    """
    heading_lines: list[str] = []
    for line in file_content.split("\n"):
        line_stripped = line.strip()
        if line_stripped.startswith("#"):
            if _heading_matches(line_stripped, heading_text):
                return line_stripped
            heading_lines.append(line_stripped)

    if not heading_lines:
        return None

    # Fuzzy fallback: score all headings against expected text
    target_text = heading_text.lstrip("#").strip()
    candidates = [h.lstrip("#").strip() for h in heading_lines]
    matches = fuzzy.rank_matches(target_text, candidates, limit=1)
    if not matches:
        return None

    matched_text, _score = matches[0]
    for h in heading_lines:
        if h.lstrip("#").strip() == matched_text:
            return h
    return None


def _build_heading(operator: str, trigger: str) -> str:
    """Build heading from operator and trigger."""
    words = trigger.split()
    # Preserve all-caps acronyms, capitalize normal words
    capitalized = " ".join(w if w.isupper() else w.capitalize() for w in words)
    if operator == "how":
        return f"How to {capitalized}"
    return f"When {capitalized}"


def _extract_section_content(heading: str, file_content: str) -> str:
    """Extract section by heading boundary detection."""
    lines = file_content.split("\n")
    heading_level = len(heading) - len(heading.lstrip("#"))

    start_idx = None
    for idx, line in enumerate(lines):
        if _heading_matches(line, heading):
            start_idx = idx
            break

    if start_idx is None:
        return ""

    result_lines = [lines[start_idx]]
    for idx in range(start_idx + 1, len(lines)):
        line = lines[idx]
        if line.startswith("#"):
            line_heading_level = len(line) - len(line.lstrip("#"))
            if line_heading_level <= heading_level:
                break
        result_lines.append(line)

    return "\n".join(result_lines).rstrip("\n")


def extract_section(file_path: Path, heading: str) -> str:
    """Extract section from file."""
    try:
        content = file_path.read_text()
    except OSError:
        return ""
    return _extract_section_content(heading, content)
