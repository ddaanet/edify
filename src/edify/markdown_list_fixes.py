"""List-related markdown fixes.

Handles metadata blocks, numbered list spacing, warning lines, nested lists, and
metadata list indentation.
"""

import re
from typing import Final

# Characters that indicate tree diagrams
_TREE_CHARS: Final = ["├", "└", "│"]


def _should_skip_prefix_extraction(stripped: str) -> bool:
    """Check if line should be skipped during prefix extraction."""
    if not stripped:
        return True
    if re.match(r"^[-*]|^\d+\.", stripped):
        return True
    if stripped.startswith("|") and stripped.count("|") >= 2:
        return True
    if stripped.startswith(">"):
        return True
    return any(sym in stripped[:3] for sym in _TREE_CHARS)


def _extract_prefix(line: str) -> str | None:
    """Extract non-markup prefix from line.

    Returns None if line is empty, is already a list item, or has no clear
    prefix. Returns prefix string (e.g., "✅", "[TODO]", "NOTE:") if found.

    ONLY matches:
    - Emoji-like symbols (non-alphanumeric at start)
    - Bracketed text [like this]
    - Uppercase words ending with colon (NOTE:, WARNING:, TODO:)
    """
    stripped = line.strip()

    if _should_skip_prefix_extraction(stripped):
        return None

    # Try each pattern in order
    emoji_match = re.match(r"^([^\w\s\[\(\{\-\*\|>`]+)(\s|$)", stripped)
    if emoji_match:
        return emoji_match.group(1)

    bracket_match = re.match(r"^(\[[^\]]+\])(\s|$)", stripped)
    if bracket_match:
        return bracket_match.group(1)

    colon_match = re.match(r"^([A-Z][A-Z0-9_]*:)\s", stripped)
    if colon_match:
        return colon_match.group(1)

    return None


def _is_emoji_prefix(prefix: str) -> bool:
    """Check if prefix is emoji-like."""
    return bool(re.match(r"^[^\w\s\[\(\{\-\*]", prefix))


def _is_bracket_prefix(prefix: str) -> bool:
    """Check if prefix is bracketed text."""
    return prefix.startswith("[")


def _is_colon_prefix(prefix: str) -> bool:
    """Check if prefix ends with colon."""
    return prefix.endswith(":")


def _is_similar_prefix(p1: str | None, p2: str | None) -> bool:
    """Check if two prefixes are similar (emoji, bracket, colon types)."""
    if p1 is None or p2 is None:
        return False
    if p1 == p2:
        return True
    return (
        (_is_emoji_prefix(p1) and _is_emoji_prefix(p2))
        or (_is_bracket_prefix(p1) and _is_bracket_prefix(p2))
        or (_is_colon_prefix(p1) and _is_colon_prefix(p2))
    )


def _collect_metadata_block(
    lines: list[str], start_idx: int, pattern: str
) -> tuple[list[str], int, bool]:
    """Collect consecutive metadata lines and check for trailing blank.

    Returns:
        (metadata_lines, next_idx, has_blank_line_after)
    """
    metadata_lines = [lines[start_idx]]
    j = start_idx + 1
    found_blank = False
    while j < len(lines):
        next_line = lines[j]
        if re.match(pattern, next_line.strip()):
            metadata_lines.append(next_line)
            j += 1
        elif next_line.strip() == "":
            found_blank = True
            j += 1
            break
        else:
            break
    return metadata_lines, j, found_blank


def _indent_following_lists(lines: list[str], start_idx: int, result: list[str]) -> int:
    """Indent list items that follow a metadata block.

    Returns:
        New index after processing
    """
    j = start_idx
    while j < len(lines):
        list_line = lines[j]
        list_stripped = list_line.strip()

        if list_stripped == "":
            result.append(list_line)
            j += 1
            break

        if not re.match(r"^[-*] |^\d+\. ", list_stripped):
            break

        result.append(f"  {list_stripped}\n")
        j += 1
    return j


def fix_metadata_blocks(lines: list[str]) -> list[str]:
    """Convert **Label:** lines to list items, indent following lists.

    Also indents any list items that follow the metadata block.
    """
    result = []
    i = 0
    pattern = r"^\*\*[A-Za-z][^*]+:\*\*|^\*\*[A-Za-z][^*]+\*\*:"

    while i < len(lines):
        line = lines[i]
        if re.match(pattern, line.strip()):
            metadata_lines, j, found_blank = _collect_metadata_block(lines, i, pattern)
            if len(metadata_lines) >= 2:
                for meta_line in metadata_lines:
                    stripped = meta_line.strip()
                    if stripped:
                        result.append(f"- {stripped}\n")
                if found_blank:
                    result.append("\n")
                j = _indent_following_lists(lines, j, result)
                i = j
                continue
        result.append(line)
        i += 1
    return result


def fix_numbered_list_spacing(lines: list[str]) -> list[str]:
    """Ensure numbered lists have proper blank line spacing.

    Rules:
    1. Add blank line before a numbered list when it follows non-list content
    2. Add blank line after **Label:** when followed by a numbered list
    3. Do NOT add blank lines within a numbered list (between items or continuations)
    """
    result: list[str] = []
    numbered_list_pattern = r"^[0-9]+\. \S"
    bullet_list_pattern = r"^[*+-] \S"
    label_pattern = r"^\*\*[^*]+:\*\*\s*$"

    in_numbered_list = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        is_numbered_item = bool(
            re.match(numbered_list_pattern, stripped)
        ) and not line.startswith("   ")
        is_blank = stripped == ""
        is_continuation = in_numbered_list and line.startswith("   ") and not is_blank

        # Update list context BEFORE processing
        if is_blank:
            in_numbered_list = False
        elif is_numbered_item:
            # Check if we should add blank before this list item
            if not in_numbered_list and len(result) > 0:
                prev = result[-1].strip()
                # Add blank only if prev is not blank, not a list item, not **Label:**
                if (
                    prev != ""
                    and not re.match(numbered_list_pattern, prev)
                    and not re.match(bullet_list_pattern, prev)
                    and not re.match(label_pattern, prev)
                ):
                    result.append("\n")
            in_numbered_list = True
        elif not is_continuation:
            # Non-blank, non-numbered, non-continuation exits list context
            in_numbered_list = False

        result.append(line)

        # Add blank line after **Label:** ONLY if next line is a numbered list
        if re.match(label_pattern, stripped) and i + 1 < len(lines):
            next_line = lines[i + 1]
            next_stripped = next_line.strip()
            if re.match(
                numbered_list_pattern, next_stripped
            ) and not next_line.startswith("   "):
                result.append("\n")

    return result


def fix_warning_lines(lines: list[str]) -> list[str]:
    """Convert to list items lines with consistent non-markup prefixes.

    Claude often generates consecutive lines with emoji or symbol prefixes
    that should be formatted as lists. This detects patterns like:
    - ✅ Task completed
    - ❌ Task failed
    - ⚠️ Warning message
    - [TODO] Action item

    Only converts groups of 2+ lines with similar prefix patterns.
    Skips lines already formatted as lists (-, *, numbered).
    """
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        prefix = _extract_prefix(line)

        if prefix:
            prefixed_lines = [line]
            j = i + 1
            while j < len(lines):
                next_prefix = _extract_prefix(lines[j])
                if _is_similar_prefix(prefix, next_prefix):
                    prefixed_lines.append(lines[j])
                    j += 1
                else:
                    break

            if len(prefixed_lines) >= 2:
                for pline in prefixed_lines:
                    stripped = pline.strip()
                    result.append(f"- {stripped}\n")
                i = j
                continue

        result.append(line)
        i += 1

    return result


def fix_nested_lists(lines: list[str]) -> list[str]:
    """Convert lettered sub-items (a., b., c.) to numbered lists."""
    result = []
    for line in lines:
        stripped = line.strip()
        match = re.match(r"^([a-z])\.\s+(.+)$", stripped)
        if match:
            letter = match.group(1)
            content = match.group(2)
            num = ord(letter) - ord("a") + 1  # a=1, b=2, etc.
            indent = line[: len(line) - len(line.lstrip())]
            result.append(f"{indent}{num}. {content}\n")
        else:
            result.append(line)
    return result


def fix_backtick_spaces(lines: list[str]) -> list[str]:
    """Quote content in backticks when it has leading/trailing spaces.

    Makes whitespace explicit in inline code, preventing ambiguity when
    documenting strings with intentional leading/trailing spaces.

    Examples:
        `` `blah ` `` → `` `"blah "` `` (trailing space now visible)
        `` ` blah` `` → `` `" blah"` `` (leading space now visible)
        `` `code` `` → `` `code` `` (unchanged if no spaces)

    Skips escaped backticks (`` `` ``) to avoid processing them twice.
    """
    result = []
    for line in lines:
        # Skip if line contains escaped backticks - don't process twice
        if "`` " in line or " ``" in line:
            result.append(line)
            continue

        # Find all backtick pairs and check for leading/trailing spaces
        def replace_backticks(match: re.Match[str]) -> str:
            content = match.group(1)
            # Check if content has leading or trailing space
            if content and (content[0] == " " or content[-1] == " "):
                return f'`"{content}"`'
            return f"`{content}`"

        # Match backtick pairs with content inside
        modified = re.sub(r"`([^`]*)`", replace_backticks, line)
        result.append(modified)
    return result


def fix_metadata_list_indentation(lines: list[str]) -> list[str]:
    """Convert metadata labels to list items and indent following lists.

    Claude generates metadata labels like **Plan Files:** followed by lists.
    This converts the label to a list item and indents the following list
    by 2 spaces to create proper nested list structure.

    Example:
        **Plan Files:**          →    - **Plan Files:**
        - phase-1.md                    - phase-1.md
        - phase-2.md                    - phase-2.md

    Works with both **Label:** and **Label**: patterns.
    """
    result: list[str] = []
    i = 0
    label_pattern = r"^\*\*[^*]+:\*\*\s*$|^\*\*[^*]+\*\*:\s*$"

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = line[: len(line) - len(line.lstrip())]

        if (
            re.match(label_pattern, stripped)
            and i + 1 < len(lines)
            and re.match(r"^[-*]|^\d+\.", lines[i + 1].strip())
        ):
            result.append(f"{indent}- {stripped}\n")

            j = i + 1
            while j < len(lines):
                list_line = lines[j]
                list_stripped = list_line.strip()

                if list_stripped == "":
                    result.append(list_line)
                    j += 1
                    break

                if not re.match(r"^[-*]|^\d+\.", list_stripped):
                    break

                indent_len = len(list_line) - len(list_line.lstrip())
                list_indent = list_line[:indent_len]
                result.append(f"{list_indent}  {list_stripped}\n")
                j += 1

            i = j
            continue

        result.append(line)
        i += 1

    return result
