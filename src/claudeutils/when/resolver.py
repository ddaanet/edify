"""Query resolution module for /when command."""

from pathlib import Path

from claudeutils.when import fuzzy, navigation
from claudeutils.when.index_parser import WhenEntry, parse_index


class ResolveError(Exception):
    """Error during resolution."""


def resolve(_mode: str, query: str, index_path: str, decisions_dir: str) -> str:
    """Resolve query to decision file content via prefix-based routing."""
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
        msg = f"File '{filename}' not found in agents/decisions/."
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
    """Format error with available headings (up to 10)."""
    available_headings = []
    for heading_lower in sorted(heading_to_files.keys()):
        if heading_to_files[heading_lower]:
            original_text = heading_to_files[heading_lower][0][1]
            available_headings.append(f".{original_text}")

    msg = f"Section '{query}' not found."
    if available_headings:
        suggestions = available_headings[:10]
        msg += "\nAvailable:\n  " + "\n  ".join(suggestions)

    return ResolveError(msg)


def _resolve_section(query: str, decisions_dir: str) -> str:
    """Resolve heading to section content via case-insensitive lookup."""
    dec_dir = Path(decisions_dir)
    heading_to_files: dict[str, list[tuple[Path, str]]] = {}

    for md_file in sorted(dec_dir.glob("*.md")):
        content = _read_file(md_file)
        for line in content.split("\n"):
            if line.startswith("##") and not line.startswith("###"):
                heading_text = line[2:].strip()
                if heading_text:
                    heading_lower = heading_text.lower()
                    if heading_lower not in heading_to_files:
                        heading_to_files[heading_lower] = []
                    heading_to_files[heading_lower].append((md_file, heading_text))

    query_lower = query.lower()
    if query_lower not in heading_to_files:
        raise _build_section_not_found_error(query, heading_to_files)

    matches = heading_to_files[query_lower]
    if len(matches) > 1:
        files = ", ".join(str(m[0]) for m in matches)
        msg = f"Ambiguous heading '{query}' found in: {files}"
        raise ResolveError(msg)

    file_path, heading_text = matches[0]
    content = _extract_section(file_path, f"## {heading_text}")
    if not content:
        msg = f"Failed to extract section '{heading_text}' from {file_path}"
        raise ResolveError(msg)

    return content


def _get_suggestions(
    query: str, candidates: list[str], limit: int = 3
) -> list[tuple[str, float]]:
    """Get top fuzzy suggestions sorted by score."""
    scored = []
    for candidate in candidates:
        partial_score = _get_partial_match_score(query, candidate)
        if partial_score > 0:
            scored.append((candidate, partial_score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def _get_partial_match_score(query: str, candidate: str) -> float:
    """Count sequential character matches."""
    query_lower = query.lower()
    candidate_lower = candidate.lower()
    matched = 0
    q_idx = 0
    for c in candidate_lower:
        if q_idx < len(query_lower) and c == query_lower[q_idx]:
            matched += 1
            q_idx += 1
    return float(matched)


def _handle_no_match(query: str, candidates: list[str]) -> None:
    """Raise ResolveError with fuzzy suggestions."""
    suggestions = _get_suggestions(query, candidates)
    msg = f"No match for '{query}'"
    if suggestions:
        msg += "\nDid you mean:"
        for candidate, _score in suggestions:
            parts = candidate.split(" ", 1)
            trigger = parts[1] if len(parts) > 1 else candidate
            msg += f"\n  /when {trigger}"
    raise ResolveError(msg)


def _load_matched_entry(matched_candidate: str, entries: list[WhenEntry]) -> WhenEntry:
    """Find matching entry for candidate string."""
    parts = matched_candidate.split(" ", 1)
    operator = parts[0]
    trigger_text = parts[1] if len(parts) > 1 else ""

    for entry in entries:
        if entry.operator == operator and entry.trigger == trigger_text:
            return entry

    msg = "Could not map matched candidate to entry"
    raise ResolveError(msg)


def _resolve_trigger(query: str, index_path: str, decisions_dir: str) -> str:
    """Resolve trigger via fuzzy matching with navigation."""
    index_file = Path(index_path)
    dec_dir = Path(decisions_dir)

    entries = parse_index(index_file)
    candidates = [f"{e.operator} {e.trigger}" for e in entries]
    matches = fuzzy.rank_matches(query, candidates, limit=1)

    if not matches:
        _handle_no_match(query, candidates)

    matched_candidate, _score = matches[0]
    matching_entry = _load_matched_entry(matched_candidate, entries)
    file_path = dec_dir / f"{matching_entry.section}.md"

    if not file_path.exists():
        msg = f"Decision file not found: {file_path}"
        raise ResolveError(msg)

    heading_text = _build_heading(matching_entry.operator, matching_entry.trigger)
    file_content = _read_file(file_path)

    actual_heading = None
    for line in file_content.split("\n"):
        line_stripped = line.strip()
        if line_stripped.endswith(heading_text) and line_stripped.startswith("#"):
            actual_heading = line_stripped
            break

    if not actual_heading:
        msg = f"Section not found in {file_path}: {heading_text}"
        raise ResolveError(msg)

    content = _extract_section(file_path, actual_heading)
    heading_text_only = actual_heading.lstrip("#").strip()

    ancestors = navigation.compute_ancestors(
        heading_text_only, f"{matching_entry.section}.md", file_content
    )
    siblings = navigation.compute_siblings(heading_text_only, file_content, entries)
    nav_text = navigation.format_navigation(ancestors, siblings)

    formatted_heading = f"# {heading_text}"
    content_lines = content.split("\n")
    section_content = "\n".join(content_lines[1:]).lstrip()

    output_parts = [formatted_heading, section_content]
    if nav_text:
        output_parts.append("")
        output_parts.append(nav_text)

    return "\n".join(output_parts).rstrip()


def _build_heading(operator: str, trigger: str) -> str:
    """Build heading from operator and trigger."""
    capitalized = " ".join(w.capitalize() for w in trigger.split())
    if operator == "how":
        return f"How To {capitalized}"
    return f"When {capitalized}"


def _extract_section_content(heading: str, file_content: str) -> str:
    """Extract section by heading boundary detection."""
    lines = file_content.split("\n")
    heading_level = len(heading) - len(heading.lstrip("#"))

    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == heading.strip():
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

    return "\n".join(result_lines).rstrip()


def _extract_section(file_path: Path, heading: str) -> str:
    """Extract section from file."""
    try:
        content = file_path.read_text()
    except OSError:
        return ""
    return _extract_section_content(heading, content)
