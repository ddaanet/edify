"""Pydantic models for Claude Code statusline JSON schema parsing."""

from pydantic import BaseModel, ConfigDict


class GitStatus(BaseModel):
    """Git repository status information."""

    branch: str | None
    dirty: bool


class PythonEnv(BaseModel):
    """Detected Python environment information."""

    name: str | None = None


class ThinkingState(BaseModel):
    """Claude Code thinking state information."""

    enabled: bool


class ContextUsage(BaseModel):
    """Token usage breakdown from Claude Code context window."""

    model_config = ConfigDict(populate_by_name=True)

    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int


class ContextWindowInfo(BaseModel):
    """Context window information from Claude Code."""

    model_config = ConfigDict(populate_by_name=True)

    current_usage: ContextUsage | None = None
    context_window_size: int


class ModelInfo(BaseModel):
    """Model information from Claude Code."""

    model_config = ConfigDict(populate_by_name=True)

    display_name: str


class WorkspaceInfo(BaseModel):
    """Workspace information from Claude Code."""

    model_config = ConfigDict(populate_by_name=True)

    current_dir: str


class CostInfo(BaseModel):
    """Cost information from Claude Code."""

    model_config = ConfigDict(populate_by_name=True)

    total_cost_usd: float


class PlanUsageData(BaseModel):
    """Plan mode usage limits with percentages and reset times."""

    hour5_pct: float
    hour5_reset: str
    day7_pct: float


class ApiUsageData(BaseModel):
    """API usage statistics by model tier from stats-cache.json."""

    today_opus: int
    today_sonnet: int
    today_haiku: int
    week_opus: int = 0
    week_sonnet: int = 0
    week_haiku: int = 0


class StatuslineInput(BaseModel):
    """Parsed Claude Code JSON stdin schema.

    Represents the JSON input from Claude Code statusline hook with all required
    fields for displaying statusline information.
    """

    model_config = ConfigDict(populate_by_name=True)

    model: ModelInfo
    workspace: WorkspaceInfo
    transcript_path: str
    context_window: ContextWindowInfo
    cost: CostInfo
    version: str
    session_id: str
