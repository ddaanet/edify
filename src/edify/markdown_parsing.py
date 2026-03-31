"""Segment parsing for markdown processing.

Splits markdown documents into processable and protected segments (code blocks,
YAML prologs, etc.) to allow targeted fixes without corrupting protected
content.
"""

import re
from collections.abc import Callable

from pydantic import BaseModel


def _try_parse_yaml_prolog(
    lines: list[str], start_idx: int
) -> tuple[Segment | None, int]:
    """Try to parse YAML prolog starting at index.

    Returns:
        (segment or None, new_index)
    """
    prolog_lines = [lines[start_idx]]
    j = start_idx + 1
    has_key_value = False
    found_closing = False

    # Check if next line exists and is not blank (immediate content required)
    if not (j < len(lines) and lines[j].strip()):
        return None, start_idx

    while j < len(lines):
        current_line = lines[j]
        current_stripped = current_line.strip()

        if not current_stripped:
            # Blank line inside - not a valid prolog
            return None, start_idx

        if current_stripped == "---":
            prolog_lines.append(current_line)
            found_closing = True
            j += 1
            break

        if re.match(r"^[a-zA-Z_][\w-]*:", current_stripped):
            has_key_value = True

        prolog_lines.append(current_line)
        j += 1

    if found_closing and has_key_value:
        return (
            Segment(
                processable=False,
                language="yaml-prolog",
                lines=prolog_lines,
                start_line=start_idx,
            ),
            j,
        )
    return None, start_idx


def _extract_fence_info(line: str) -> tuple[int, str | None]:
    """Extract backtick count and language from fence line."""
    backtick_count = 0
    for char in line:
        if char == "`":
            backtick_count += 1
        else:
            break
    language = line[backtick_count:].strip() or None
    return backtick_count, language


def _find_fenced_block_end(
    lines: list[str], start_idx: int, backtick_count: int
) -> tuple[list[str], int, list[tuple[int, str | None]]]:
    """Find end of fenced block, tracking nesting.

    Returns:
        (block_lines, end_index, fence_stack_at_exit)
    """
    fence_lines = [lines[start_idx]]
    i = start_idx + 1
    _, language = _extract_fence_info(lines[start_idx])
    fence_stack: list[tuple[int, str | None]] = [(backtick_count, language)]

    while i < len(lines) and fence_stack:
        current_stripped = lines[i].strip()
        fence_lines.append(lines[i])

        if current_stripped.startswith("```"):
            backtick_in_line, _ = _extract_fence_info(current_stripped)
            language_in_line = current_stripped[backtick_in_line:].strip() or None

            if backtick_in_line == backtick_count:
                if language_in_line:
                    fence_stack.append((backtick_in_line, language_in_line))
                else:
                    fence_stack.pop()
                    if not fence_stack:
                        i += 1
                        break
        i += 1

    return fence_lines, i, fence_stack


def _parse_fenced_block(lines: list[str], start_idx: int) -> tuple[list[Segment], int]:
    """Parse fenced code block starting at index.

    Returns:
        (segments, new_index)
    """
    stripped = lines[start_idx].strip()
    backtick_count, language = _extract_fence_info(stripped)

    fence_lines, end_idx, _fence_stack = _find_fenced_block_end(
        lines, start_idx, backtick_count
    )

    # Markdown blocks are processable, others are protected
    processable = language == "markdown"

    if not processable or len(fence_lines) <= 2:
        return (
            [
                Segment(
                    processable=processable,
                    language=language,
                    lines=fence_lines,
                    start_line=end_idx - len(fence_lines),
                )
            ],
            end_idx,
        )

    # Recursive parsing for markdown blocks
    inner_content = fence_lines[1:-1]
    inner_start_line = (end_idx - len(fence_lines)) + 1

    inner_segments = parse_segments(inner_content)
    for seg in inner_segments:
        seg.start_line += inner_start_line

    return (
        [
            Segment(
                processable=True,
                language=language,
                lines=[fence_lines[0]],
                start_line=end_idx - len(fence_lines),
            ),
            *inner_segments,
            Segment(
                processable=True,
                language=language,
                lines=[fence_lines[-1]],
                start_line=end_idx - 1,
            ),
        ],
        end_idx,
    )


def _collect_plain_text(lines: list[str], start_idx: int) -> tuple[list[str], int]:
    """Collect plain text until next fence or YAML prolog.

    Returns:
        (text_lines, new_index)
    """
    text_lines: list[str] = []
    i = start_idx
    while i < len(lines):
        stripped = lines[i].strip()
        if text_lines and stripped.startswith("```"):
            break
        if (
            text_lines
            and stripped == "---"
            and i + 1 < len(lines)
            and lines[i + 1].strip()
        ):
            break
        text_lines.append(lines[i])
        i += 1
    return text_lines, i


class Segment(BaseModel):
    """A segment of markdown document (processable or protected)."""

    processable: bool
    language: str | None
    lines: list[str]
    start_line: int


def flatten_segments(segments: list[Segment]) -> list[str]:
    """Flatten segments back into a list of lines."""
    result: list[str] = []
    for segment in segments:
        result.extend(segment.lines)
    return result


def apply_fix_to_segments(
    segments: list[Segment],
    fix_fn: Callable[[list[str]], list[str]],
) -> list[Segment]:
    """Apply a fix function to processable segments only.

    Args:
        segments: List of segments to process
        fix_fn: Function that takes list[str] and returns list[str]

    Returns:
        New list of segments with fix applied to processable ones only

    Note: Protected segments (processable=False) are returned unchanged,
    regardless of their language or content. This includes bare fences,
    code blocks, YAML prologs, and markdown blocks.
    """
    result = []
    for segment in segments:
        if segment.processable:
            fixed_lines = fix_fn(segment.lines)
            result.append(
                Segment(
                    processable=segment.processable,
                    language=segment.language,
                    lines=fixed_lines,
                    start_line=segment.start_line,
                )
            )
        else:
            result.append(segment)
    return result


def parse_segments(lines: list[str]) -> list[Segment]:
    """Parse document into segments (processable vs protected)."""
    if not lines:
        return []

    segments: list[Segment] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Try to parse YAML prolog
        if stripped == "---":
            prolog_segment, next_idx = _try_parse_yaml_prolog(lines, i)
            if prolog_segment:
                segments.append(prolog_segment)
                i = next_idx
                continue

        # Try to parse fenced block
        if stripped.startswith("```"):
            new_segments, next_idx = _parse_fenced_block(lines, i)
            segments.extend(new_segments)
            i = next_idx
            continue

        # Collect plain text
        text_lines, next_idx = _collect_plain_text(lines, i)
        if text_lines:
            segments.append(
                Segment(
                    processable=True,
                    language=None,
                    lines=text_lines,
                    start_line=i,
                )
            )
        i = next_idx

    return segments


def fix_dunder_references(line: str) -> str:
    """Wrap __name__.py in backticks within headings."""
    if line.startswith("#"):
        # Negative lookbehind/lookahead to avoid double-wrapping
        line = re.sub(r"(?<!`)(__[A-Za-z0-9_]+__(\.py)?)(?!`)", r"`\1`", line)
    return line
