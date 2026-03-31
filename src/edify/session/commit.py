"""Commit parser: structured markdown stdin to CommitInput."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_VALID_OPTIONS = {"no-vet", "just-lint", "amend", "no-edit"}


class CommitInputError(Exception):
    """Raised when commit input markdown is invalid."""


@dataclass
class CommitInput:
    """Parsed commit input from structured markdown."""

    files: list[str]
    message: str | None = None
    options: set[str] = field(default_factory=set)
    submodules: dict[str, str] = field(default_factory=dict)


def _strip_blockquote(lines: list[str]) -> str:
    """Strip leading ``> `` or ``>`` from lines, join."""
    stripped = []
    for line in lines:
        if line.startswith("> "):
            stripped.append(line[2:])
        elif line == ">":
            stripped.append("")
        else:
            stripped.append(line)
    return "\n".join(stripped).strip()


def _parse_files(lines: list[str]) -> list[str]:
    """Extract file paths from ``- path`` lines."""
    return [line.removeprefix("- ").strip() for line in lines if line.startswith("- ")]


def _parse_options(lines: list[str]) -> set[str]:
    """Extract and validate options from ``- option`` lines."""
    opts: set[str] = set()
    for line in lines:
        if line.startswith("- "):
            opt = line.removeprefix("- ").strip()
            if opt not in _VALID_OPTIONS:
                msg = f"Unknown option: {opt}"
                raise CommitInputError(msg)
            opts.add(opt)
    return opts


def _split_sections(text: str) -> list[tuple[str, list[str]]]:
    """Split markdown text into (heading, body_lines) pairs."""
    sections: list[tuple[str, list[str]]] = []
    current_name: str | None = None
    current_lines: list[str] = []
    in_message = False

    for line in text.split("\n"):
        heading = re.match(r"^## (.+)$", line)
        if heading and not in_message:
            if current_name is not None:
                sections.append((current_name, current_lines))
            current_name = heading.group(1).strip()
            current_lines = []
            if current_name == "Message":
                in_message = True
        elif current_name is not None:
            current_lines.append(line)

    if current_name is not None:
        sections.append((current_name, current_lines))
    return sections


def _process_sections(
    sections: list[tuple[str, list[str]]],
) -> tuple[list[str] | None, set[str], dict[str, str], str | None, bool]:
    """Classify and parse each section, return raw results."""
    files: list[str] | None = None
    options: set[str] = set()
    submodules: dict[str, str] = {}
    message: str | None = None
    has_message = False

    for name, lines in sections:
        if name == "Files":
            files = _parse_files(lines)
        elif name == "Options":
            options = _parse_options(lines)
        elif name.startswith("Submodule "):
            path = name[len("Submodule ") :]
            submodules[path] = _strip_blockquote(lines)
        elif name == "Message":
            has_message = True
            message = _strip_blockquote(lines)

    return files, options, submodules, message, has_message


def _validate(
    files: list[str] | None,
    options: set[str],
    *,
    has_message: bool,
) -> list[str]:
    """Validate parsed sections, return files or raise."""
    if files is None:
        msg = "Missing required section: ## Files"
        raise CommitInputError(msg)

    if not files:
        msg = "## Files section is empty"
        raise CommitInputError(msg)

    if "no-edit" in options and "amend" not in options:
        msg = "no-edit requires amend option"
        raise CommitInputError(msg)

    if "no-edit" in options and has_message:
        msg = "no-edit contradicts ## Message section"
        raise CommitInputError(msg)

    amend_no_edit = "amend" in options and "no-edit" in options
    if not has_message and not amend_no_edit:
        msg = "Missing required section: ## Message"
        raise CommitInputError(msg)

    return files


def parse_commit_input(text: str) -> CommitInput:
    """Parse structured markdown into CommitInput."""
    sections = _split_sections(text)
    files, options, submodules, message, has_message = _process_sections(sections)
    validated_files = _validate(files, options, has_message=has_message)

    return CommitInput(
        files=validated_files,
        message=message,
        options=options,
        submodules=submodules,
    )
