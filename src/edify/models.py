"""Data models for edify."""

from enum import StrEnum

from pydantic import BaseModel


class FeedbackType(StrEnum):
    """Types of user feedback that can be extracted."""

    TOOL_DENIAL = "tool_denial"
    INTERRUPTION = "interruption"
    MESSAGE = "message"


class SessionInfo(BaseModel):
    """Model for session information."""

    session_id: str
    title: str
    timestamp: str


class FeedbackItem(BaseModel):
    """Model for extracted user feedback."""

    timestamp: str
    session_id: str
    feedback_type: FeedbackType
    content: str
    agent_id: str | None = None
    slug: str | None = None
    tool_use_id: str | None = None
