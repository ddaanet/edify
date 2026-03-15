"""Tests for session handoff pipeline (Phase 4)."""

from __future__ import annotations

import pytest

from claudeutils.session.handoff.parse import (
    HandoffInput,
    HandoffInputError,
    parse_handoff_input,
)

HANDOFF_INPUT_FIXTURE = """\
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

**Handoff CLI tool design (Phase A):**
- Produced outline
- Review by outline-review-agent
"""


# --- Cycle 4.1: parse handoff stdin ---


def test_parse_handoff_input() -> None:
    """Valid input returns HandoffInput with status and completed."""
    result = parse_handoff_input(HANDOFF_INPUT_FIXTURE)
    assert isinstance(result, HandoffInput)
    assert result.status_line == "Design Phase A complete — outline reviewed."
    assert len(result.completed_lines) > 0
    assert any("Produced outline" in line for line in result.completed_lines)


def test_parse_handoff_missing_status() -> None:
    """Input without Status line raises HandoffInputError."""
    text = """\
## Completed This Session

- Something done
"""
    with pytest.raises(HandoffInputError, match="Status"):
        parse_handoff_input(text)


def test_parse_handoff_missing_completed() -> None:
    """Input without Completed heading raises HandoffInputError."""
    text = """\
**Status:** Done.
"""
    with pytest.raises(HandoffInputError, match="Completed"):
        parse_handoff_input(text)
