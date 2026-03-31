"""Tests for edify data models."""

import pytest
from pydantic import ValidationError

from edify.models import SessionInfo

from . import pytest_helpers as helpers


def test_session_info_creation() -> None:
    """Create SessionInfo with required fields and correct types."""
    info = SessionInfo(
        session_id=helpers.SESSION_ID_MAIN,
        title="Design a python script",
        timestamp="2025-12-16T08:39:26.932Z",
    )
    assert info.session_id == helpers.SESSION_ID_MAIN
    assert info.title == "Design a python script"
    assert info.timestamp == "2025-12-16T08:39:26.932Z"


def test_session_info_validation() -> None:
    """Validate types with Pydantic."""
    with pytest.raises(ValidationError):
        # Intentionally pass wrong types to test Pydantic validation
        SessionInfo(session_id=123, title="foo", timestamp="bar")  # type: ignore[arg-type]
