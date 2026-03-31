"""Tests for markdown module."""

from edify.markdown import fix_markdown_code_blocks


def test_fix_markdown_code_blocks_nests_when_inner_fence_detected() -> None:
    """Test: Nest ```markdown block containing inner ``` fence."""
    input_lines = [
        "```markdown\n",
        "# Example\n",
        "```python\n",
        "code\n",
        "```\n",
        "```\n",
    ]
    expected = [
        "````markdown\n",
        "# Example\n",
        "```python\n",
        "code\n",
        "```\n",
        "````\n",
    ]
    assert fix_markdown_code_blocks(input_lines) == expected


def test_fix_markdown_code_blocks_no_change_without_inner_fence() -> None:
    """Test: Leave ```markdown block without inner fence unchanged."""
    input_lines = [
        "```markdown\n",
        "# Simple Example\n",
        "No inner fences here\n",
        "```\n",
    ]
    expected = input_lines.copy()
    assert fix_markdown_code_blocks(input_lines) == expected


def test_fix_markdown_code_blocks_passes_through_inner_fence_in_python() -> None:
    """Test: ```python block with inner fence is upgraded to 4 backticks."""
    input_lines = [
        "```python\n",
        "def foo():\n",
        '    """\n',
        "    Example:\n",
        "    ```\n",
        "    code\n",
        "    ```\n",
        '    """\n',
        "```\n",
    ]
    expected = [
        "````python\n",
        "def foo():\n",
        '    """\n',
        "    Example:\n",
        "    ```\n",
        "    code\n",
        "    ```\n",
        '    """\n',
        "````\n",
    ]
    assert fix_markdown_code_blocks(input_lines) == expected


def test_fix_markdown_code_blocks_ignores_inline_backticks() -> None:
    """Test: Don't detect ``` as fence when it appears inline in text."""
    input_lines = [
        "Text about `` ```markdown `` blocks\n",
        "\n",
        "```bash\n",
        "echo hello\n",
        "```\n",
        "\n",
        "More text with `` ```python `` and `` ```javascript `` references\n",
    ]
    # Should not raise an error or modify the content
    assert fix_markdown_code_blocks(input_lines) == input_lines


def test_fix_markdown_code_blocks_handles_multiple_blocks() -> None:
    """Test: Handle multiple ```markdown blocks correctly."""
    input_lines = [
        "# Doc\n",
        "\n",
        "```markdown\n",
        "```python\n",
        "code\n",
        "```\n",
        "```\n",
        "\n",
        "Some text\n",
        "\n",
        "```markdown\n",
        "No inner fence\n",
        "```\n",
    ]
    expected = [
        "# Doc\n",
        "\n",
        "````markdown\n",
        "```python\n",
        "code\n",
        "```\n",
        "````\n",
        "\n",
        "Some text\n",
        "\n",
        "```markdown\n",
        "No inner fence\n",
        "```\n",
    ]
    assert fix_markdown_code_blocks(input_lines) == expected
