"""Query resolution module for /when command."""

from pathlib import Path

from claudeutils.when import fuzzy
from claudeutils.when.index_parser import parse_index


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
        return "file"
    if query.startswith("."):
        # Section mode: strip prefix and resolve
        section_query = query[1:].strip()
        return _resolve_section(section_query, decisions_dir)

    # Trigger mode: fuzzy match against index entries
    return _resolve_trigger(query, index_path, decisions_dir)


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


def _resolve_trigger(query: str, index_path: str, decisions_dir: str) -> str:
    """Resolve trigger mode query via fuzzy matching.

    Builds candidate list from index entries, fuzzy matches query,
    returns matching heading and content from decision file.

    Args:
        query: Trigger text (no prefix)
        index_path: Path to index file
        decisions_dir: Directory containing decision files

    Returns:
        Heading and section content

    Raises:
        ResolveError: If no match found
    """
    index_file = Path(index_path)
    dec_dir = Path(decisions_dir)

    # Parse index entries
    entries = parse_index(index_file)

    # Build candidates: "{operator} {trigger}" for fuzzy matching
    candidates = [f"{e.operator} {e.trigger}" for e in entries]

    # Fuzzy match: include operator prefix in query
    # Query comes without prefix, so match against "when trigger" or "how trigger"
    matches = fuzzy.rank_matches(query, candidates, limit=1)

    if not matches:
        msg = f"No match for '{query}'"
        raise ResolveError(msg)

    matched_candidate, _score = matches[0]

    # Extract the operator and trigger from the matched candidate
    parts = matched_candidate.split(" ", 1)
    operator = parts[0]
    trigger_text = parts[1] if len(parts) > 1 else ""

    # Find the matching entry
    matching_entry = None
    for entry in entries:
        if entry.operator == operator and entry.trigger == trigger_text:
            matching_entry = entry
            break

    if not matching_entry:
        msg = "Could not map matched candidate to entry"
        raise ResolveError(msg)

    # Construct expected heading from operator and trigger
    heading = _build_heading(operator, trigger_text)

    # Extract section name from index (it points to the file)
    # For now, assume the section name is the file name
    file_path = dec_dir / f"{matching_entry.section}.md"

    if not file_path.exists():
        msg = f"Decision file not found: {file_path}"
        raise ResolveError(msg)

    # Read the file and extract the section
    content = _extract_section(file_path, heading)

    if not content:
        msg = f"Section not found in {file_path}: {heading}"
        raise ResolveError(msg)

    return content


def _build_heading(operator: str, trigger: str) -> str:
    """Build heading from operator and trigger text.

    Args:
        operator: "when" or "how"
        trigger: Trigger text (e.g., "writing mock tests")

    Returns:
        Heading string (e.g., "## When Writing Mock Tests")
    """
    if operator == "how":
        # Capitalize first letter of each word
        words = trigger.split()
        capitalized = " ".join(w.capitalize() for w in words)
        return f"## How To {capitalized}"

    # "when" operator
    words = trigger.split()
    capitalized = " ".join(w.capitalize() for w in words)
    return f"## When {capitalized}"


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

    lines = content.split("\n")
    heading_level = len(heading) - len(heading.lstrip("#"))
    heading_marker = "#" * heading_level

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

        # Check if we've hit another heading of the same or higher level
        if line.startswith(heading_marker) and line[0] == "#":
            # Count the # symbols
            heading_chars = len(line) - len(line.lstrip("#"))
            if heading_chars <= heading_level and heading_chars > 0:
                break

        result_lines.append(line)

    return "\n".join(result_lines).rstrip()
