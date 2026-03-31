"""Tests for CLI markdown command."""

from pathlib import Path

from click.testing import CliRunner

from edify.cli import cli


def test_help_shows_markdown_command() -> None:
    """Test: markdown command is registered in CLI."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "markdown" in result.output


def test_markdown_processes_file_from_stdin(
    tmp_path: Path,
) -> None:
    """Test: markdown command processes file from stdin."""
    filepath = tmp_path / "test.md"
    filepath.write_text("## About __init__.py\n")

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=str(filepath) + "\n")

    assert str(filepath) in result.output
    assert filepath.read_text() == "## About `__init__.py`\n"


def test_markdown_skips_unchanged_files(
    tmp_path: Path,
) -> None:
    """Test: markdown command skips unchanged files."""
    filepath = tmp_path / "test.md"
    filepath.write_text("## About `__init__.py`\n")

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=str(filepath) + "\n")

    assert result.output == ""


def test_markdown_errors_on_non_md_file(
    tmp_path: Path,
) -> None:
    """Test: markdown command errors on non-.md file."""
    filepath = tmp_path / "test.txt"
    filepath.write_text("content")

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=str(filepath) + "\n")

    assert result.exit_code == 1
    # Error message could be in output or exception
    assert "not a markdown file" in result.output or (
        result.exception and "not a markdown file" in str(result.exception)
    )


def test_markdown_errors_on_missing_file(
    tmp_path: Path,
) -> None:
    """Test: markdown command errors on missing file."""
    filepath = tmp_path / "missing.md"

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=str(filepath) + "\n")

    assert result.exit_code == 1
    # Error message could be in output or exception
    assert "does not exist" in result.output or (
        result.exception and "does not exist" in str(result.exception)
    )


def test_markdown_processes_multiple_files(
    tmp_path: Path,
) -> None:
    """Test: markdown command processes multiple files."""
    file1 = tmp_path / "test1.md"
    file2 = tmp_path / "test2.md"
    file3 = tmp_path / "test3.md"

    file1.write_text("## About __init__.py\n")
    file2.write_text("## About __name__.py\n")
    file3.write_text("## About `__init__.py`\n")

    input_text = f"{file1}\n{file2}\n{file3}\n"

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=input_text)

    assert str(file1) in result.output
    assert str(file2) in result.output
    assert str(file3) not in result.output


def test_markdown_batch_processes_all_valid_files_despite_errors(
    tmp_path: Path,
) -> None:
    """Test: markdown command processes all valid files even when some are invalid."""
    valid1 = tmp_path / "valid1.md"
    invalid = tmp_path / "invalid.txt"
    valid2 = tmp_path / "valid2.md"
    missing = tmp_path / "missing.md"
    valid3 = tmp_path / "valid3.md"

    valid1.write_text("## About __init__.py\n")
    invalid.write_text("content")
    valid2.write_text("## About __name__.py\n")
    # missing.md doesn't exist
    valid3.write_text("## About __main__.py\n")

    input_text = f"{valid1}\n{invalid}\n{valid2}\n{missing}\n{valid3}\n"

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=input_text)

    # Should exit with error code due to invalid files
    assert result.exit_code == 1

    # But should still process all valid files (their paths appear in success messages)
    assert str(valid1) in result.output
    assert str(valid2) in result.output
    assert str(valid3) in result.output

    # Error messages include invalid paths, valid ones were processed
    # Check that errors were reported for invalid files
    output_text = result.output
    error_messages = (
        output_text[output_text.find("Error:") :]
        if "Error:" in output_text
        else output_text
    )
    assert (
        "not a markdown file" in error_messages or "not a markdown file" in output_text
    )
    assert "does not exist" in error_messages or "does not exist" in output_text

    # Verify valid files were actually modified
    assert valid1.read_text() == "## About `__init__.py`\n"
    assert valid2.read_text() == "## About `__name__.py`\n"
    assert valid3.read_text() == "## About `__main__.py`\n"


def test_markdown_reports_multiple_processing_errors(
    tmp_path: Path,
) -> None:
    """Test: markdown command fixes inner fences by upgrading to 4 backticks."""
    file1 = tmp_path / "file1.md"
    file2 = tmp_path / "file2.md"
    file3 = tmp_path / "file3.md"

    # Create files with inner fences (typical Claude output discussing code blocks)
    file1.write_text(
        "```python\n"
        "def foo():\n"
        '    """\n'
        "    Example:\n"
        "    ```\n"
        "    code\n"
        "    ```\n"
        '    """\n'
        "```\n"
    )

    file2.write_text("```bash\n# Example\n```\ninner content\n```\n```\n")

    file3.write_text("## About __init__.py\n")

    input_text = f"{file1}\n{file2}\n{file3}\n"

    runner = CliRunner()
    result = runner.invoke(cli, ["markdown"], input=input_text)

    # Should exit successfully (no errors)
    assert result.exit_code == 0

    # All modified files should be in output
    assert str(file1) in result.output
    assert str(file2) in result.output
    assert str(file3) in result.output

    # Verify inner fences were fixed by upgrading to 4 backticks
    assert file1.read_text() == (
        "````python\n"
        "def foo():\n"
        '    """\n'
        "    Example:\n"
        "    ```\n"
        "    code\n"
        "    ```\n"
        '    """\n'
        "````\n"
    )

    assert file2.read_text() == "````bash\n# Example\n```\ninner content\n```\n````\n"

    assert file3.read_text() == "## About `__init__.py`\n"
