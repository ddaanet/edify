"""Tests for markdown composition utilities."""

from pathlib import Path

import pytest
import yaml
from _pytest.capture import CaptureFixture

from edify.compose import (
    compose,
    format_separator,
    get_header_level,
    increase_header_levels,
    load_config,
    normalize_newlines,
)


def test_get_header_level_detects_h1() -> None:
    """Detect h1 header."""
    assert get_header_level("# Title") == 1


def test_get_header_level_detects_h3() -> None:
    """Detect h3 header."""
    assert get_header_level("### Subsection") == 3


def test_get_header_level_detects_h6() -> None:
    """Detect h6 header."""
    assert get_header_level("###### Deep") == 6


def test_get_header_level_returns_none_for_non_header() -> None:
    """Return None for non-header lines."""
    assert get_header_level("Not a header") is None
    assert get_header_level(" # Space before hash") is None


def test_increase_header_levels_by_one() -> None:
    """Increase all headers by 1 level."""
    content = "# Title\n## Section\n### Subsection"
    result = increase_header_levels(content, 1)
    assert result == "## Title\n### Section\n#### Subsection"


def test_increase_header_levels_by_two() -> None:
    """Increase all headers by 2 levels."""
    content = "# Title\n## Section"
    result = increase_header_levels(content, 2)
    assert result == "### Title\n#### Section"


def test_increase_header_levels_preserves_non_headers() -> None:
    """Don't modify non-header lines."""
    content = "# Header\nNormal text\n## Section"
    result = increase_header_levels(content, 1)
    assert result == "## Header\nNormal text\n### Section"


def test_increase_header_levels_default_is_one() -> None:
    """Default levels parameter is 1."""
    content = "# Title"
    result = increase_header_levels(content)
    assert result == "## Title"


def test_normalize_newlines_adds_newline() -> None:
    """Add newline if missing."""
    assert normalize_newlines("text") == "text\n"


def test_normalize_newlines_preserves_single_newline() -> None:
    """Don't add extra newline if already present."""
    assert normalize_newlines("text\n") == "text\n"


def test_format_separator_default_horizontal_rule() -> None:
    """Default separator is horizontal rule."""
    assert format_separator("---") == "\n---\n\n"


def test_format_separator_blank() -> None:
    """Blank separator is double newline."""
    assert format_separator("blank") == "\n\n"


def test_format_separator_none() -> None:
    """None separator is empty string."""
    assert format_separator("none") == ""


def test_load_config_basic(tmp_path: Path) -> None:
    """Load valid YAML configuration."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
fragments:
  - file1.md
  - file2.md
output: result.md
""")

    config = load_config(config_file)
    assert config["fragments"] == ["file1.md", "file2.md"]
    assert config["output"] == "result.md"


def test_load_config_with_optional_fields(tmp_path: Path) -> None:
    """Load config with optional fields."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
fragments:
  - file1.md
output: result.md
title: "My Document"
adjust_headers: true
separator: "blank"
validate_mode: "warn"
""")

    config = load_config(config_file)
    assert config["title"] == "My Document"
    assert config["adjust_headers"] is True
    assert config["separator"] == "blank"
    assert config["validate_mode"] == "warn"


def test_load_config_applies_defaults(tmp_path: Path) -> None:
    """Apply defaults for missing optional fields."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
fragments:
  - file1.md
output: result.md
""")

    config = load_config(config_file)
    assert config.get("title") is None
    assert config.get("adjust_headers", False) is False
    assert config.get("separator", "---") == "---"
    assert config.get("validate_mode", "strict") == "strict"


def test_load_config_with_sources_anchors(tmp_path: Path) -> None:
    """Support YAML anchors for path deduplication."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
defaults: &defaults
  separator: "---"

fragments:
  - file1.md
  - file2.md
output: result.md
<<: *defaults
""")

    config = load_config(config_file)
    # YAML anchors are supported via yaml.safe_load
    assert config["fragments"] == ["file1.md", "file2.md"]
    assert config["separator"] == "---"


def test_load_config_missing_file() -> None:
    """Raise FileNotFoundError for missing config file."""
    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        load_config(Path("nonexistent.yaml"))


def test_load_config_invalid_yaml(tmp_path: Path) -> None:
    """Raise YAMLError for malformed YAML."""
    config_file = tmp_path / "bad.yaml"
    config_file.write_text("invalid: yaml: : syntax")

    with pytest.raises(yaml.YAMLError):
        load_config(config_file)


def test_load_config_missing_fragments_field(tmp_path: Path) -> None:
    """Raise ValueError for missing fragments field."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("output: result.md")

    with pytest.raises(ValueError, match="Missing required field: fragments"):
        load_config(config_file)


def test_load_config_missing_output_field(tmp_path: Path) -> None:
    """Raise ValueError for missing output field."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("fragments:\n  - file1.md")

    with pytest.raises(ValueError, match="Missing required field: output"):
        load_config(config_file)


def test_compose_single_fragment(tmp_path: Path) -> None:
    """Compose single fragment to output."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Header\n\nContent\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output)

    assert output.exists()
    assert output.read_text() == "# Header\n\nContent\n"


def test_compose_multiple_fragments_with_separator(tmp_path: Path) -> None:
    """Compose multiple fragments with default separator."""
    frag1 = tmp_path / "frag1.md"
    frag1.write_text("# Part 1\n")
    frag2 = tmp_path / "frag2.md"
    frag2.write_text("# Part 2\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2], output=output)

    result = output.read_text()
    assert "# Part 1\n" in result
    assert "\n---\n\n" in result
    assert "# Part 2\n" in result


def test_compose_creates_output_directory(tmp_path: Path) -> None:
    """Auto-create output parent directory."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    output = tmp_path / "nested" / "dir" / "output.md"
    compose(fragments=[frag], output=output)

    assert output.exists()
    assert output.parent.exists()


def test_compose_accepts_string_paths(tmp_path: Path) -> None:
    """Accept string paths, not just Path objects."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    output = tmp_path / "output.md"
    compose(fragments=[str(frag)], output=str(output))

    assert output.exists()


def test_compose_with_title(tmp_path: Path) -> None:
    """Prepend title as h1 header."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output, title="My Document")

    result = output.read_text()
    assert result.startswith("# My Document\n\n")
    assert "Content\n" in result


def test_compose_separator_blank(tmp_path: Path) -> None:
    """Use blank line separator."""
    frag1 = tmp_path / "frag1.md"
    frag1.write_text("Part 1\n")
    frag2 = tmp_path / "frag2.md"
    frag2.write_text("Part 2\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2], output=output, separator="blank")

    result = output.read_text()
    assert result == "Part 1\n\n\nPart 2\n"


def test_compose_separator_none(tmp_path: Path) -> None:
    """Use no separator."""
    frag1 = tmp_path / "frag1.md"
    frag1.write_text("Part 1\n")
    frag2 = tmp_path / "frag2.md"
    frag2.write_text("Part 2\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2], output=output, separator="none")

    result = output.read_text()
    assert result == "Part 1\nPart 2\n"


def test_compose_no_title_by_default(tmp_path: Path) -> None:
    """Don't add title if not provided."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Existing Header\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output)

    result = output.read_text()
    assert result.startswith("# Existing Header\n")


def test_compose_adjust_headers_increases_levels(tmp_path: Path) -> None:
    """Increase all header levels when adjust_headers=True."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Title\n## Section\n### Subsection\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output, adjust_headers=True)

    result = output.read_text()
    assert "## Title\n" in result
    assert "### Section\n" in result
    assert "#### Subsection\n" in result


def test_compose_adjust_headers_disabled_by_default(tmp_path: Path) -> None:
    """Don't adjust headers by default."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Title\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output)

    result = output.read_text()
    assert "# Title\n" in result


def test_compose_adjust_headers_with_title(tmp_path: Path) -> None:
    """Adjust headers with title creates proper hierarchy."""
    frag = tmp_path / "frag.md"
    frag.write_text("# Purpose\n## Details\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag], output=output, title="Document", adjust_headers=True)

    result = output.read_text()
    assert result.startswith("# Document\n\n")
    assert "## Purpose\n" in result
    assert "### Details\n" in result


def test_compose_strict_mode_raises_on_missing_fragment(tmp_path: Path) -> None:
    """Raise FileNotFoundError in strict mode for missing fragment."""
    frag1 = tmp_path / "exists.md"
    frag1.write_text("Content\n")
    frag2 = tmp_path / "missing.md"  # Does not exist

    output = tmp_path / "output.md"

    with pytest.raises(FileNotFoundError, match="Fragment not found"):
        compose(fragments=[frag1, frag2], output=output, validate_mode="strict")


def test_compose_strict_mode_is_default(tmp_path: Path) -> None:
    """Strict mode is default validation mode."""
    missing = tmp_path / "missing.md"
    output = tmp_path / "output.md"

    with pytest.raises(FileNotFoundError):
        compose(fragments=[missing], output=output)


def test_compose_warn_mode_skips_missing_fragment(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Skip missing fragments in warn mode with warning."""
    frag1 = tmp_path / "exists.md"
    frag1.write_text("Content 1\n")
    frag2 = tmp_path / "missing.md"  # Does not exist
    frag3 = tmp_path / "exists2.md"
    frag3.write_text("Content 2\n")

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2, frag3], output=output, validate_mode="warn")

    # Output should contain only existing fragments
    result = output.read_text()
    assert "Content 1\n" in result
    assert "Content 2\n" in result

    # Warning should be printed to stderr
    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert "missing.md" in captured.err


def test_compose_warn_mode_creates_partial_output(tmp_path: Path) -> None:
    """Create output with available fragments in warn mode."""
    frag1 = tmp_path / "exists.md"
    frag1.write_text("Available content\n")
    frag2 = tmp_path / "missing.md"  # Does not exist

    output = tmp_path / "output.md"
    compose(fragments=[frag1, frag2], output=output, validate_mode="warn")

    assert output.exists()
    assert "Available content\n" in output.read_text()
