"""Context calculation for statusline display."""

import json
import os
import subprocess
from pathlib import Path

from edify.statusline.models import (
    GitStatus,
    PythonEnv,
    StatuslineInput,
    ThinkingState,
)

# Transcript parsing constants
_TRANSCRIPT_READ_SIZE = 1024 * 1024  # 1MB read window for transcript


def get_git_status() -> GitStatus:
    """Detect if in git repository and return branch name.

    Returns:
        GitStatus with branch name and dirty status.
        Returns branch=None if not in a git repository.
    """
    try:
        # Check if we're in a git repository
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True,
        )

        # Get the current branch name
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        )

        branch = result.stdout.strip()

        # Check for dirty working tree
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )

        dirty = bool(status_result.stdout.strip())

        return GitStatus(branch=branch, dirty=dirty)

    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not in a git repository or git not found
        return GitStatus(branch=None, dirty=False)


def get_python_env() -> PythonEnv:
    """Detect active Python environment from environment variables.

    Checks for Conda and virtual environment indicators in order of precedence:
    1. CONDA_DEFAULT_ENV (Conda environment takes priority)
    2. VIRTUAL_ENV (virtualenv or venv activation)

    Returns:
        PythonEnv model with environment name, or name=None if no environment detected.
        For VIRTUAL_ENV, extracts basename from path (e.g., /path/to/venv → venv).
    """
    # Check CONDA_DEFAULT_ENV first (takes precedence)
    conda_env = os.environ.get("CONDA_DEFAULT_ENV", "").strip()
    if conda_env:
        return PythonEnv(name=conda_env)

    # Check VIRTUAL_ENV (extract basename from path)
    venv_path = os.environ.get("VIRTUAL_ENV", "").strip()
    if venv_path:
        venv_name = Path(venv_path).name
        return PythonEnv(name=venv_name)

    # No environment detected
    return PythonEnv(name=None)


def parse_transcript_context(transcript_path: str) -> int:
    """Parse transcript JSONL to extract context tokens from assistant messages.

    Reads the last 1MB of the transcript file, parses JSONL lines in reverse,
    and finds the first assistant message with non-zero tokens.

    Args:
        transcript_path: Path to transcript JSONL file.

    Returns:
        Sum of 4 token fields (inputTokens, outputTokens,
        cacheCreationInputTokens, cacheReadInputTokens) from first
        assistant message found, or 0 if none found.
    """
    try:
        path = Path(transcript_path)
        file_size = path.stat().st_size
        # Read last _TRANSCRIPT_READ_SIZE bytes (or entire file if smaller)
        read_size = min(_TRANSCRIPT_READ_SIZE, file_size)
        start_pos = max(0, file_size - read_size)

        with path.open() as f:
            f.seek(start_pos)
            content = f.read()

        # Parse lines in reverse to find first assistant message with tokens
        lines = content.strip().split("\n")
        for line in reversed(lines):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                # Check for assistant message (not sidechain)
                if data.get("type") == "assistant" and not data.get(
                    "isSidechain", False
                ):
                    tokens = data.get("tokens", {})
                    if tokens:
                        input_tokens = int(tokens.get("inputTokens", 0) or 0)
                        output_tokens = int(tokens.get("outputTokens", 0) or 0)
                        cache_creation = int(
                            tokens.get("cacheCreationInputTokens", 0) or 0
                        )
                        cache_read = int(tokens.get("cacheReadInputTokens", 0) or 0)
                        total = (
                            input_tokens + output_tokens + cache_creation + cache_read
                        )
                        if total > 0:
                            return total
            except (json.JSONDecodeError, ValueError, TypeError):
                # Skip malformed lines
                continue
    except (FileNotFoundError, OSError, AttributeError):
        # File doesn't exist, can't be read, or other error
        pass

    return 0


def get_thinking_state() -> ThinkingState:
    """Read thinking state from ~/.claude/settings.json.

    Returns:
        ThinkingState with enabled flag from alwaysThinkingEnabled field.
        Returns enabled=True if settings file doesn't exist, can't be parsed,
        or field is null/missing (thinking enabled by default).
    """
    try:
        settings_path = Path.home() / ".claude" / "settings.json"
        with settings_path.open() as f:
            settings = json.load(f)
        # Default to True if null or missing (matches shell behavior)
        enabled = settings.get("alwaysThinkingEnabled")
        if enabled is None:
            return ThinkingState(enabled=True)
        return ThinkingState(enabled=bool(enabled))
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # Settings file not found or can't be parsed - default to enabled
        return ThinkingState(enabled=True)


def calculate_context_tokens(input_data: StatuslineInput) -> int:
    """Calculate total context tokens from current_usage or transcript fallback.

    Sums the 4 token fields (input_tokens, output_tokens,
    cache_creation_input_tokens, cache_read_input_tokens) from
    current_usage when present. Falls back to parsing transcript
    file when current_usage is None (R2 requirement).

    Args:
        input_data: StatuslineInput containing context_window information
                   and transcript_path for fallback parsing.

    Returns:
        Sum of the 4 token fields from current_usage, or from transcript
        fallback if current_usage is None, or 0 if neither available.
    """
    if input_data.context_window.current_usage is not None:
        usage = input_data.context_window.current_usage
        return (
            usage.input_tokens
            + usage.output_tokens
            + usage.cache_creation_input_tokens
            + usage.cache_read_input_tokens
        )

    # Fallback: parse transcript file
    return parse_transcript_context(input_data.transcript_path)
