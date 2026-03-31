"""Markdown composition utilities for assembling documents from fragments."""

import re
import sys
from pathlib import Path
from re import Match

import yaml


def get_header_level(line: str) -> int | None:
    """Detect markdown header level.

    Args:
        line: A string that may be a markdown header.

    Returns:
        int: Header level (1-6) if the line is a valid header, None otherwise.
    """
    match = re.match(r"^(#{1,6})\s", line)
    if match:
        return len(match.group(1))
    return None


def increase_header_levels(content: str, levels: int = 1) -> str:
    """Increase all markdown header levels in content.

    Args:
        content: Markdown content as a string.
        levels: Number of header levels to increase (default 1).

    Returns:
        str: Content with all headers increased by specified levels.
    """

    def replace_header(match: Match[str]) -> str:
        hashes = match.group(1)
        new_hashes = "#" * (len(hashes) + levels)
        rest = match.group(2)
        return new_hashes + rest

    return re.sub(r"^(#{1,6})(\s.*)$", replace_header, content, flags=re.MULTILINE)


def normalize_newlines(content: str) -> str:
    """Ensure content ends with exactly one newline.

    Args:
        content: A string that may need newline normalization.

    Returns:
        str: Content with exactly one trailing newline if it doesn't already have one.
    """
    if not content or content.endswith("\n"):
        return content
    return content + "\n"


def format_separator(style: str) -> str:
    """Return formatted separator string based on style parameter.

    Args:
        style: Separator style - "---" (default), "blank", or "none".

    Returns:
        str: Formatted separator string.

    Raises:
        ValueError: If style is not recognized.
    """
    if style == "---":
        return "\n---\n\n"
    if style == "blank":
        return "\n\n"
    if style == "none":
        return ""
    msg = f"Unknown separator style: {style}"
    raise ValueError(msg)


def load_config(config_path: Path | str) -> dict[str, object]:
    """Load and parse YAML configuration file.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        dict: Parsed YAML configuration.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        yaml.YAMLError: If YAML is malformed.
        ValueError: If required fields are missing.
    """
    config_path_obj = Path(config_path) if isinstance(config_path, str) else config_path

    # Check file existence
    if not config_path_obj.exists():
        msg = "Configuration file not found"
        raise FileNotFoundError(msg)

    with config_path_obj.open(encoding="utf-8") as f:
        config = yaml.safe_load(f)
        if not isinstance(config, dict):
            msg = "Configuration must be a YAML mapping"
            raise TypeError(msg)

    # Validate required fields
    if "fragments" not in config:
        msg = "Missing required field: fragments"
        raise ValueError(msg)
    if "output" not in config:
        msg = "Missing required field: output"
        raise ValueError(msg)

    return config


def compose(
    fragments: list[Path | str],
    output: Path | str,
    *,
    title: str | None = None,
    adjust_headers: bool = False,
    separator: str = "---",
    **kwargs: str,
) -> None:
    """Compose multiple markdown fragments into a single output file.

    Args:
        fragments: List of fragment file paths (Path or str).
        output: Path to output file (Path or str).
        title: Optional markdown header to prepend.
        adjust_headers: If True, increase all fragment headers by 1 level.
        separator: Fragment separator style ("---", "blank", "none").
        **kwargs: Additional options including validate_mode ("strict" or "warn").

    Raises:
        FileNotFoundError: If fragment not found and validate_mode is "strict".
    """
    validate_mode = kwargs.get("validate_mode", "strict")
    # Convert string paths to Path objects
    output_path = Path(output) if isinstance(output, str) else output
    fragment_paths = [Path(f) if isinstance(f, str) else f for f in fragments]

    # Auto-create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Compose content from fragments
    composed_content = []

    # Add title if provided
    if title:
        composed_content.append(f"# {title}\n\n")

    for i, frag_path in enumerate(fragment_paths):
        # Check fragment existence
        if not frag_path.exists():
            if validate_mode == "strict":
                msg = f"Fragment not found: {frag_path}"
                raise FileNotFoundError(msg)
            if validate_mode == "warn":
                print(f"WARNING: Fragment not found: {frag_path}", file=sys.stderr)
                continue

        # Read and normalize fragment content
        content = frag_path.read_text(encoding="utf-8")

        # Apply header adjustment if enabled
        if adjust_headers:
            content = increase_header_levels(content, 1)

        content = normalize_newlines(content)
        composed_content.append(content)

        # Add separator between fragments (not after last non-skipped)
        # Only add separator if there are more fragments to process
        remaining = sum(1 for p in fragment_paths[i + 1 :] if p.exists())
        if remaining > 0:
            sep = format_separator(separator)
            composed_content.append(sep)

    # Write composed output
    with output_path.open("w", encoding="utf-8") as out:
        out.write("".join(composed_content))
