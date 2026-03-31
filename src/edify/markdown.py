r"""Preprocessor for Claude markdown-like output.

This module fixes structural issues in Claude-generated markdown before
dprint formatting. It handles patterns that Claude commonly produces but
aren't valid markdown, such as:

- Consecutive lines with emoji/symbol prefixes needing list formatting
- Code blocks with improper fence nesting
- Metadata labels followed by lists needing indentation
- Other structural patterns from Claude output

Processing Pipeline:
    Claude output → markdown.py fixes → dprint formatting

Future Direction:
    This should eventually evolve into a dprint plugin for better integration.

Usage:
    # Process single file
    from pathlib import Path
    from edify.markdown import process_file

    filepath = Path("output.md")
    modified = process_file(filepath)  # Returns True if file was changed

    # Process lines in memory
    from edify.markdown import process_lines

    lines = ["**File:** test.md\n", "**Model:** Sonnet\n"]
    fixed_lines = process_lines(lines)
"""

from pathlib import Path

from edify.exceptions import (
    MarkdownInnerFenceError,
    MarkdownProcessingError,
)
from edify.markdown_block_fixes import fix_markdown_code_blocks
from edify.markdown_inline_fixes import (
    escape_inline_backticks,
    find_inline_code_spans,
    fix_dunder_references,
)
from edify.markdown_list_fixes import (
    fix_backtick_spaces,
    fix_metadata_blocks,
    fix_metadata_list_indentation,
    fix_nested_lists,
    fix_numbered_list_spacing,
    fix_warning_lines,
)
from edify.markdown_parsing import (
    Segment,
    apply_fix_to_segments,
    flatten_segments,
    parse_segments,
)

# ============================================================================
# Processing Pipeline
# ============================================================================
#
# Order: escape_inline_backticks, fix_dunder_references, fix_metadata_blocks,
# fix_warning_lines, fix_nested_lists, fix_numbered_list_spacing,
# fix_backtick_spaces, fix_markdown_code_blocks
#


def process_lines(lines: list[str]) -> list[str]:
    """Apply all markdown structure fixes to lines."""
    segments = parse_segments(lines)

    segments = apply_fix_to_segments(segments, escape_inline_backticks)
    segments = apply_fix_to_segments(
        segments, lambda ls: [fix_dunder_references(line) for line in ls]
    )
    segments = apply_fix_to_segments(segments, fix_metadata_blocks)
    segments = apply_fix_to_segments(segments, fix_warning_lines)
    segments = apply_fix_to_segments(segments, fix_nested_lists)
    segments = apply_fix_to_segments(segments, fix_numbered_list_spacing)
    segments = apply_fix_to_segments(segments, fix_backtick_spaces)

    result = flatten_segments(segments)
    return fix_markdown_code_blocks(result)


def process_file(filepath: Path) -> bool:
    """Process a markdown file, returning True if modified."""
    with filepath.open(encoding="utf-8") as f:
        original_lines = f.readlines()
    try:
        lines = process_lines(original_lines)
    except MarkdownInnerFenceError as e:
        raise MarkdownProcessingError(str(filepath), e) from e
    if lines == original_lines:
        return False
    with filepath.open("w", encoding="utf-8") as f:
        f.writelines(lines)
    return True


# Re-export for backward compatibility
__all__ = [
    "Segment",
    "apply_fix_to_segments",
    "escape_inline_backticks",
    "find_inline_code_spans",
    "fix_backtick_spaces",
    "fix_dunder_references",
    "fix_markdown_code_blocks",
    "fix_metadata_blocks",
    "fix_metadata_list_indentation",
    "fix_nested_lists",
    "fix_numbered_list_spacing",
    "fix_warning_lines",
    "flatten_segments",
    "parse_segments",
    "process_file",
    "process_lines",
]
