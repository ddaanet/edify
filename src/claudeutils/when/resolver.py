"""Query resolution module for /when command."""

from pathlib import Path

from claudeutils.when import fuzzy, navigation
from claudeutils.when.index_parser import WhenEntry, parse_index


class ResolveError(Exception):
    """Error during resolution."""


def resolve(_mode: str, query: str, index_path: str, decisions_dir: str) -> str:
    """Resolve query to decision file content.

    Routes by query prefix:
    - ".." prefix → file mode (strip prefix)
    - "." prefix → section mode (strip prefix)
    - No prefix → trigger mode (fuzzy match against index)

    Args:
        _mode: Mode hint (provided for future multi-mode routing)
        query: Query string with optional prefix
        index_path: Path to index file
        decisions_dir: Directory containing decision files

    Returns:
        Section heading and content on successful match

    Raises:
        ResolveError: If no match found or ambiguous match
    """
    if query.startswith(".."):
        # File mode: strip prefix and resolve
        filename = query[2:].strip()
        return _resolve_file(filename, decisions_dir)
    if query.startswith("."):
        # Section mode: strip prefix and resolve
        section_query = query[1:].strip()
        return _resolve_section(section_query, decisions_dir)

    # Trigger mode: fuzzy match against index entries
    return _resolve_trigger(query, index_path, decisions_dir)


def _resolve_file(filename: str, decisions_dir: str) -> str:
    """Resolve file mode query via filename lookup.

    Resolves relative to decisions_dir, reads and returns full file content.

    Args:
        filename: Filename to lookup (e.g., "testing.md")
        decisions_dir: Directory containing decision files

    Returns:
        Full file content

    Raises:
        ResolveError: If file not found
    """
    dec_dir = Path(decisions_dir)
    file_path = dec_dir / filename

    if not file_path.exists():
        msg = f"File not found: {filename}"
        raise ResolveError(msg)

    try:
        content = file_path.read_text()
    except OSError as e:
        msg = f"Failed to read {file_path}: {e}"
        raise ResolveError(msg) from e

    return content


def _resolve_section(query: str, decisions_dir: str) -> str:
    """Resolve section mode query via heading lookup.

    Scans all .md files in decisions_dir, builds heading→file mapping,
    looks up query heading (case-insensitive), checks uniqueness.

    Args:
        query: Heading text to lookup (e.g., "Mock Patching Pattern")
        decisions_dir: Directory containing decision files

    Returns:
        Heading and section content

    Raises:
        ResolveError: If no match, multiple matches, or other error
    """
    dec_dir = Path(decisions_dir)

    # Scan decision files and collect headings
    heading_to_files: dict[str, list[tuple[Path, str]]] = {}

    for md_file in sorted(dec_dir.glob("*.md")):
        try:
            content = md_file.read_text()
        except OSError as e:
            msg = f"Failed to read {md_file}: {e}"
            raise ResolveError(msg) from e

        lines = content.split("\n")
        for line in lines:
            # Match H2+ headings (## or more #'s)
            if line.startswith("##") and not line.startswith("###"):
                # Extract heading text (remove the ##)
                heading_text = line[2:].strip()
                if heading_text:
                    heading_lower = heading_text.lower()
                    if heading_lower not in heading_to_files:
                        heading_to_files[heading_lower] = []
                    heading_to_files[heading_lower].append((md_file, heading_text))

    # Lookup query (case-insensitive)
    query_lower = query.lower()

    if query_lower not in heading_to_files:
        msg = f"Heading not found: {query}"
        raise ResolveError(msg)

    matches = heading_to_files[query_lower]

    # Check uniqueness
    if len(matches) > 1:
        files = ", ".join(str(m[0]) for m in matches)
        msg = f"Ambiguous heading '{query}' found in: {files}"
        raise ResolveError(msg)

    # Extract content from the unique match
    file_path, heading_text = matches[0]
    content = _extract_section(file_path, f"## {heading_text}")

    if not content:
        msg = f"Failed to extract section '{heading_text}' from {file_path}"
        raise ResolveError(msg)

    return content


def _get_suggestions(
    query: str, candidates: list[str], limit: int = 3
) -> list[tuple[str, float]]:
    """Get top fuzzy suggestions when no match found.

    Args:
        query: The search pattern
        candidates: List of candidates to score
        limit: Maximum number of suggestions (default 3)

    Returns:
        List of (candidate, score) tuples sorted by score descending
    """
    scored = []

    for candidate in candidates:
        # Get partial matching score (count of matched chars)
        partial_score = _get_partial_match_score(query, candidate)
        if partial_score > 0:
            scored.append((candidate, partial_score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def _get_partial_match_score(query: str, candidate: str) -> float:
    """Count query characters found in order within candidate."""
    query_lower = query.lower()
    candidate_lower = candidate.lower()

    # Count how many query characters we can match in order
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


def _load_matched_entry(
    matched_candidate: str, entries: list[WhenEntry]
) -> WhenEntry:
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
    """Resolve trigger mode query via fuzzy matching.

    Builds candidate list from index entries, fuzzy matches query,
    returns matching heading and content from decision file, formatted with navigation.

    Args:
        query: Trigger text (no prefix)
        index_path: Path to index file
        decisions_dir: Directory containing decision files

    Returns:
        Heading, section content, and navigation links

    Raises:
        ResolveError: If no match found
    """
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

    # Build heading text and search for it in the file
    heading_text = _build_heading(matching_entry.operator, matching_entry.trigger)
    file_content = file_path.read_text()

    # Find the actual heading line (may be H2, H3, or H4)
    actual_heading = None
    for line in file_content.split("\n"):
        line_stripped = line.strip()
        if line_stripped.endswith(heading_text) and line_stripped.startswith("#"):
            actual_heading = line_stripped
            break

    if not actual_heading:
        msg = f"Section not found in {file_path}: {heading_text}"
        raise ResolveError(msg)

    # Read the file and extract the section
    content = _extract_section(file_path, actual_heading)

    # Extract heading text without the # markers for navigation computation
    heading_text_only = actual_heading.lstrip("#").strip()

    # Compute navigation links
    ancestors = navigation.compute_ancestors(
        heading_text_only, f"{matching_entry.section}.md", file_content
    )
    siblings = navigation.compute_siblings(heading_text_only, file_content, entries)

    # Format navigation output
    nav_text = navigation.format_navigation(ancestors, siblings)

    # Format heading as H1 regardless of source level
    formatted_heading = f"# {heading_text}"

    # Extract content without the original heading line
    content_lines = content.split("\n")
    # Skip first line (the original heading) and join the rest
    section_content = "\n".join(content_lines[1:]).lstrip()

    # Combine content with navigation
    output_parts = [formatted_heading, section_content]
    if nav_text:
        output_parts.append("")
        output_parts.append(nav_text)

    return "\n".join(output_parts).rstrip()


def _build_heading(operator: str, trigger: str) -> str:
    """Build heading from operator and trigger text.

    Args:
        operator: "when" or "how"
        trigger: Trigger text (e.g., "writing mock tests")

    Returns:
        Heading string without leading # markers (e.g., "When Writing Mock Tests")
        Caller will add appropriate level markers.
    """
    if operator == "how":
        # Capitalize first letter of each word
        words = trigger.split()
        capitalized = " ".join(w.capitalize() for w in words)
        return f"How To {capitalized}"

    # "when" operator
    words = trigger.split()
    capitalized = " ".join(w.capitalize() for w in words)
    return f"When {capitalized}"


def _extract_section_content(heading: str, file_content: str) -> str:
    """Extract section content from file by heading boundary detection.

    Finds target heading line and collects content until the next heading of same
    or higher level. Handles both nested (H2/H3) and flat (all H2) structures.

    Args:
        heading: Heading text to extract (e.g., "## Heading A" or "### Child A1")
        file_content: Full file content as string

    Returns:
        Section including heading line and content up to next heading boundary
    """
    lines = file_content.split("\n")
    heading_level = len(heading) - len(heading.lstrip("#"))

    # Find the heading line
    start_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == heading.strip():
            start_idx = idx
            break

    if start_idx is None:
        return ""

    # Extract from heading to next heading of same or higher level
    result_lines = [lines[start_idx]]

    for idx in range(start_idx + 1, len(lines)):
        line = lines[idx]

        # Check if line is a heading
        if line.startswith("#"):
            # Count heading level
            line_heading_level = len(line) - len(line.lstrip("#"))
            # Stop if we hit a heading of same or higher level
            if line_heading_level <= heading_level:
                break

        result_lines.append(line)

    return "\n".join(result_lines).rstrip()


def _extract_section(file_path: Path, heading: str) -> str:
    """Extract section content from decision file.

    Reads file and extracts content from heading to next heading of same level.

    Args:
        file_path: Path to decision file
        heading: Section heading to extract (e.g., "## When Writing Mock Tests")

    Returns:
        Section heading and content, or empty string if not found
    """
    try:
        content = file_path.read_text()
    except OSError:
        return ""

    return _extract_section_content(heading, content)
