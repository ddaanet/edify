"""Tests for session commit parser (Phase 5)."""

from __future__ import annotations

import pytest

from claudeutils.session.commit import (
    CommitInput,
    CommitInputError,
    parse_commit_input,
)

COMMIT_INPUT_FIXTURE = """\
## Files
- src/commit/cli.py
- src/commit/gate.py
- agent-core/fragments/vet-requirement.md

## Options
- no-vet
- amend

## Submodule agent-core
> 🤖 Update vet-requirement fragment
>
> - Add scripted gate classification reference

## Message
> ✨ Add commit CLI with scripted vet check
>
> - Structured markdown I/O
> - Submodule-aware commit pipeline
"""


# Cycle 5.1: parse commit markdown stdin


@pytest.mark.parametrize(
    "section",
    ["files", "options", "submodule", "message"],
)
def test_parse_commit_input(section: str) -> None:
    """Parametrized test for each section of commit input."""
    result = parse_commit_input(COMMIT_INPUT_FIXTURE)
    assert isinstance(result, CommitInput)

    if section == "files":
        assert result.files == [
            "src/commit/cli.py",
            "src/commit/gate.py",
            "agent-core/fragments/vet-requirement.md",
        ]
    elif section == "options":
        assert result.options == {"no-vet", "amend"}
    elif section == "submodule":
        assert "agent-core" in result.submodules
        msg = result.submodules["agent-core"]
        assert msg.startswith("🤖 Update vet-requirement fragment")
        assert "- Add scripted gate classification reference" in msg
    elif section == "message":
        assert result.message is not None
        assert result.message.startswith("✨ Add commit CLI")
        assert "- Structured markdown I/O" in result.message
        assert "- Submodule-aware commit pipeline" in result.message


def test_parse_commit_input_edge_cases() -> None:
    """Edge cases: missing sections, unknown options, no-edit rules."""
    # Missing ## Files → error
    with pytest.raises(CommitInputError, match="Files"):
        parse_commit_input("## Message\n> hello\n")

    # Missing ## Message without amend+no-edit → error
    with pytest.raises(CommitInputError, match="Message"):
        parse_commit_input("## Files\n- foo.py\n")

    # Unknown option → error
    with pytest.raises(CommitInputError, match="Unknown option"):
        parse_commit_input(
            "## Files\n- foo.py\n\n## Options\n- foobar\n\n## Message\n> msg\n"
        )

    # no-edit without amend → error
    with pytest.raises(CommitInputError, match="no-edit"):
        parse_commit_input(
            "## Files\n- foo.py\n\n## Options\n- no-edit\n\n## Message\n> msg\n"
        )

    # amend + no-edit without ## Message → valid
    result = parse_commit_input(
        "## Files\n- foo.py\n\n## Options\n- amend\n- no-edit\n"
    )
    assert result.message is None
    assert "amend" in result.options
    assert "no-edit" in result.options

    # no-edit with ## Message present → error (contradictory)
    with pytest.raises(CommitInputError):
        parse_commit_input(
            "## Files\n- f.py\n\n## Options\n- amend\n- no-edit\n\n## Message\n> msg\n"
        )


def test_parse_commit_no_options() -> None:
    """Input without ## Options produces empty set."""
    result = parse_commit_input("## Files\n- foo.py\n\n## Message\n> msg\n")
    assert result.options == set()


def test_parse_commit_multiple_submodules() -> None:
    """Multiple ## Submodule sections parsed independently."""
    text = """\
## Files
- foo.py

## Submodule agent-core
> Core update

## Submodule other-lib
> Lib update

## Message
> commit msg
"""
    result = parse_commit_input(text)
    assert len(result.submodules) == 2
    assert "agent-core" in result.submodules
    assert "other-lib" in result.submodules


def test_parse_commit_blockquote_stripping() -> None:
    """Blockquote > prefix stripped from message and submodule lines."""
    text = """\
## Files
- foo.py

## Message
> First line
>
> - Detail line
> More text
"""
    result = parse_commit_input(text)
    assert result.message is not None
    # No leading "> " in message
    assert not any(line.startswith("> ") for line in result.message.split("\n"))
    assert "First line" in result.message
    assert "- Detail line" in result.message
