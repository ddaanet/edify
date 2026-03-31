"""Code block markdown fixes.

Handles nesting of markdown blocks containing inner fence markers.
"""


def _has_inner_fence_in_block(
    lines: list[str], block_start: int, block_end: int
) -> bool:
    """Check if a block contains inner ``` markers."""
    return any("```" in lines[k] for k in range(block_start, block_end))


def _find_matching_close_fence(lines: list[str], start_idx: int) -> bool:
    """Look ahead to find matching closing ``` fence.

    Returns True if a matching closing fence is found before any opening.
    """
    for k in range(start_idx + 1, len(lines)):
        check_line = lines[k].strip()
        if check_line == "```":
            return True
        if check_line.startswith("```") and len(check_line) > 3:
            # Opening fence before close - stop looking
            return False
    return False


def _build_upgraded_block(language: str, block_lines: list[str]) -> list[str]:
    """Build block with upgraded 4-backtick fences."""
    return [f"````{language}\n", *block_lines[1:-1], "````\n"]


def _track_fence_depth(
    block_stripped: str, fence_depth: int, lines: list[str], idx: int
) -> int:
    """Track fence depth based on current line.

    Returns:
        New fence depth or -1 if outer closing fence found
    """
    if len(block_stripped) > 3:
        return fence_depth + 1
    if block_stripped == "```":
        if fence_depth > 0:
            return fence_depth - 1
        # At fence_depth==0: is this inner opening or outer closing?
        if _find_matching_close_fence(lines, idx):
            return fence_depth + 1
        return -1  # Outer closing fence
    return fence_depth


def fix_markdown_code_blocks(lines: list[str]) -> list[str]:
    """Nest ```markdown blocks that contain inner ``` fences.

    Claude sometimes generates ```markdown blocks containing code examples
    with their own ``` fences. This uses ```` (4 backticks) for the outer
    fence to properly nest the content.

    Note: Only processes ```markdown blocks. Other language blocks with
          inner fences are left as-is, since inline backtick escaping
          handles them correctly.
    """
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```") and len(stripped) > 3:
            language = stripped[3:]

            block_lines = [line]
            j = i + 1
            fence_depth = 0

            while j < len(lines):
                block_line = lines[j]
                block_lines.append(block_line)
                block_stripped = block_line.strip()

                if block_stripped.startswith("```"):
                    new_depth = _track_fence_depth(
                        block_stripped, fence_depth, lines, j
                    )
                    if new_depth == -1:
                        break
                    fence_depth = new_depth

                j += 1
            else:
                result.extend(block_lines)
                i = j
                continue

            # Check if block has inner fences and upgrade if needed
            has_inner_fence = (
                _has_inner_fence_in_block(lines, i + 1, j) or fence_depth > 0
            )
            if has_inner_fence:
                result.extend(_build_upgraded_block(language, block_lines))
            else:
                result.extend(block_lines)

            i = j + 1
            continue

        result.append(line)
        i += 1

    return result
