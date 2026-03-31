"""Tests for statusline context module."""

import json
import subprocess
from unittest.mock import MagicMock, patch

from edify.statusline.context import (
    calculate_context_tokens,
    get_git_status,
    get_python_env,
    get_thinking_state,
)
from edify.statusline.models import (
    ContextUsage,
    ContextWindowInfo,
    CostInfo,
    GitStatus,
    ModelInfo,
    PythonEnv,
    StatuslineInput,
    ThinkingState,
    WorkspaceInfo,
)


def test_get_git_status_in_repo() -> None:
    """Test get_git_status returns GitStatus with branch when in git repo."""
    with patch("subprocess.run") as mock_run:
        # Mock git rev-parse --git-dir (succeeds, repo exists)
        git_dir_process = MagicMock()
        git_dir_process.returncode = 0
        git_dir_process.stdout = ".git\n"

        # Mock git branch --show-current (succeeds, returns branch)
        branch_process = MagicMock()
        branch_process.returncode = 0
        branch_process.stdout = "main\n"

        # Mock git status --porcelain (succeeds, empty output = clean)
        status_process = MagicMock()
        status_process.returncode = 0
        status_process.stdout = ""

        # Return different mocks for each call
        mock_run.side_effect = [git_dir_process, branch_process, status_process]

        result = get_git_status()

        # Verify result
        assert isinstance(result, GitStatus)
        assert result.branch == "main"
        assert result.dirty is False

        # Verify subprocess calls
        assert mock_run.call_count == 3
        calls = mock_run.call_args_list
        assert calls[0][0][0] == ["git", "rev-parse", "--git-dir"]
        assert calls[1][0][0] == ["git", "branch", "--show-current"]
        assert calls[2][0][0] == ["git", "status", "--porcelain"]


def test_get_git_status_dirty() -> None:
    """Test get_git_status detects dirty working tree with porcelain output."""
    with patch("subprocess.run") as mock_run:
        # Mock git rev-parse --git-dir (succeeds, repo exists)
        git_dir_process = MagicMock()
        git_dir_process.returncode = 0
        git_dir_process.stdout = ".git\n"

        # Mock git branch --show-current (succeeds, returns branch)
        branch_process = MagicMock()
        branch_process.returncode = 0
        branch_process.stdout = "main\n"

        # Mock git status --porcelain (succeeds, non-empty output = dirty)
        status_process = MagicMock()
        status_process.returncode = 0
        status_process.stdout = " M file.txt\n"

        # Return different mocks for each call
        mock_run.side_effect = [git_dir_process, branch_process, status_process]

        result = get_git_status()

        # Verify result
        assert isinstance(result, GitStatus)
        assert result.branch == "main"
        assert result.dirty is True

        # Verify subprocess calls
        assert mock_run.call_count == 3
        calls = mock_run.call_args_list
        assert calls[0][0][0] == ["git", "rev-parse", "--git-dir"]
        assert calls[1][0][0] == ["git", "branch", "--show-current"]
        assert calls[2][0][0] == ["git", "status", "--porcelain"]


def test_get_git_status_not_in_repo() -> None:
    """Test get_git_status returns defaults when not in git repo."""
    with patch("subprocess.run") as mock_run:
        # Mock subprocess to raise CalledProcessError (not in git repo)
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")

        result = get_git_status()

        # Verify result has branch=None and dirty=False
        assert isinstance(result, GitStatus)
        assert result.branch is None
        assert result.dirty is False


def test_get_thinking_state_enabled() -> None:
    """Test get_thinking_state returns ThinkingState with enabled=True.

    When alwaysThinkingEnabled is true in settings.json.
    """
    settings_data = {"alwaysThinkingEnabled": True}

    with patch("pathlib.Path.open", create=True) as mock_open:
        # Mock file content as JSON string
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(settings_data)
        mock_open.return_value = mock_file

        result = get_thinking_state()

        # Verify result
        assert isinstance(result, ThinkingState)
        assert result.enabled is True


def test_get_thinking_state_missing_file() -> None:
    """Test get_thinking_state returns enabled when settings.json missing.

    Matches shell behavior: thinking enabled by default (no 😶 indicator).
    """
    with patch("pathlib.Path.home") as mock_home:
        # Mock Path.home() and then the missing file
        mock_path = MagicMock()
        mock_path.__truediv__.return_value = mock_path
        mock_path.open.side_effect = FileNotFoundError(
            "[Errno 2] No such file or directory: '~/.claude/settings.json'"
        )
        mock_home.return_value = mock_path

        result = get_thinking_state()

        # Verify result - enabled by default (matches shell)
        assert isinstance(result, ThinkingState)
        assert result.enabled is True


def test_get_thinking_state_null_handling() -> None:
    """Test get_thinking_state handles null and missing key gracefully.

    When alwaysThinkingEnabled is null or absent, defaults to enabled=True.
    """
    # Test case 1: alwaysThinkingEnabled: null
    settings_data_null = {"alwaysThinkingEnabled": None}
    with patch("pathlib.Path.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(
            settings_data_null
        )
        mock_open.return_value = mock_file

        result = get_thinking_state()
        assert isinstance(result, ThinkingState)
        assert result.enabled is True

    # Test case 2: alwaysThinkingEnabled key absent
    settings_data_absent = {"otherKey": "value"}
    with patch("pathlib.Path.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(
            settings_data_absent
        )
        mock_open.return_value = mock_file

        result = get_thinking_state()
        assert isinstance(result, ThinkingState)
        assert result.enabled is True

    # Test case 3: alwaysThinkingEnabled: false (explicit disable)
    settings_data_false = {"alwaysThinkingEnabled": False}
    with patch("pathlib.Path.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(
            settings_data_false
        )
        mock_open.return_value = mock_file

        result = get_thinking_state()
        assert isinstance(result, ThinkingState)
        assert result.enabled is False


def test_calculate_context_tokens_from_current_usage() -> None:
    """Test calculate_context_tokens sums 4 token fields from current_usage."""
    # Create StatuslineInput with current_usage containing 4 token values
    current_usage = ContextUsage(
        input_tokens=100,
        output_tokens=50,
        cache_creation_input_tokens=25,
        cache_read_input_tokens=25,
    )
    context_window = ContextWindowInfo(
        current_usage=current_usage, context_window_size=200000
    )
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude 3"),
        workspace=WorkspaceInfo(current_dir="/home/user"),
        transcript_path="/home/user/.claude/transcript.md",
        context_window=context_window,
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="sess-123",
    )

    # Call calculate_context_tokens
    result = calculate_context_tokens(input_data)

    # Should sum to 100 + 50 + 25 + 25 = 200
    assert result == 200


def test_calculate_context_tokens_from_transcript() -> None:
    """Parses transcript JSONL when current_usage is None.

    When current_usage is None, should fall back to reading transcript file and
    parsing JSONL for assistant messages with tokens.
    """
    # Create transcript JSONL with assistant message containing tokens
    transcript_content = (
        '{"type": "assistant", "isSidechain": false, "tokens": '
        '{"inputTokens": 50, "outputTokens": 100, '
        '"cacheCreationInputTokens": 25, "cacheReadInputTokens": 25}}\n'
    )

    # Create StatuslineInput with current_usage=None (forces transcript fallback)
    context_window = ContextWindowInfo(current_usage=None, context_window_size=200000)
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude 3"),
        workspace=WorkspaceInfo(current_dir="/home/user"),
        transcript_path="/home/user/.claude/transcript.md",
        context_window=context_window,
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="sess-123",
    )

    # Mock Path.stat() and Path.open() to return transcript JSONL
    with patch("edify.statusline.context.Path") as mock_path_class:
        # Mock the Path instance
        mock_path_instance = MagicMock()

        # Mock stat() to return file size
        mock_stat = MagicMock()
        mock_stat.st_size = len(transcript_content)
        mock_path_instance.stat.return_value = mock_stat

        # Mock open() to return file content
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = transcript_content
        mock_file.__enter__.return_value.seek = MagicMock()
        mock_path_instance.open.return_value = mock_file

        # Make Path() return our mock instance
        mock_path_class.return_value = mock_path_instance

        # Call calculate_context_tokens
        result = calculate_context_tokens(input_data)

        # Should sum to 50 + 100 + 25 + 25 = 200
        assert result == 200


def test_calculate_context_tokens_missing_transcript() -> None:
    """Test missing transcript returns 0 without exception.

    When current_usage is None and transcript file doesn't exist, should return
    0 without raising exception (fail-safe per D8).
    """
    # Create StatuslineInput with current_usage=None and non-existent path
    context_window = ContextWindowInfo(current_usage=None, context_window_size=200000)
    input_data = StatuslineInput(
        model=ModelInfo(display_name="Claude 3"),
        workspace=WorkspaceInfo(current_dir="/home/user"),
        transcript_path="nonexistent.json",
        context_window=context_window,
        cost=CostInfo(total_cost_usd=0.05),
        version="1.0.0",
        session_id="sess-123",
    )

    # Mock Path to raise FileNotFoundError when opening missing file
    with patch("edify.statusline.context.Path") as mock_path_class:
        # Mock the Path instance
        mock_path_instance = MagicMock()

        # Mock stat() to raise FileNotFoundError (file doesn't exist)
        mock_path_instance.stat.side_effect = FileNotFoundError(
            "[Errno 2] No such file or directory: 'nonexistent.json'"
        )

        # Make Path() return our mock instance
        mock_path_class.return_value = mock_path_instance

        # Call calculate_context_tokens - should return 0 without raising
        result = calculate_context_tokens(input_data)

        # Should return 0 (fail-safe default)
        assert result == 0


def test_get_python_env() -> None:
    """Test get_python_env detects Python environments from variables.

    Tests multiple scenarios:
    - VIRTUAL_ENV set: extracts basename as environment name
    - CONDA_DEFAULT_ENV set: uses environment name as-is
    - Both set: Conda takes precedence
    - Neither set: returns PythonEnv with name=None
    - Empty values: treated as absent
    """
    # Test case 1: VIRTUAL_ENV with full path
    with patch.dict("os.environ", {"VIRTUAL_ENV": "/path/to/myenv"}, clear=True):
        result = get_python_env()
        assert isinstance(result, PythonEnv)
        assert result.name == "myenv"

    # Test case 2: CONDA_DEFAULT_ENV
    with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": "conda-env"}, clear=True):
        result = get_python_env()
        assert isinstance(result, PythonEnv)
        assert result.name == "conda-env"

    # Test case 3: Both set (Conda takes precedence)
    with patch.dict(
        "os.environ",
        {"VIRTUAL_ENV": "/path/to/venv", "CONDA_DEFAULT_ENV": "conda-env"},
        clear=True,
    ):
        result = get_python_env()
        assert isinstance(result, PythonEnv)
        assert result.name == "conda-env"

    # Test case 4: Neither set
    with patch.dict("os.environ", {}, clear=True):
        result = get_python_env()
        assert isinstance(result, PythonEnv)
        assert result.name is None

    # Test case 5: VIRTUAL_ENV empty string
    with patch.dict("os.environ", {"VIRTUAL_ENV": ""}, clear=True):
        result = get_python_env()
        assert isinstance(result, PythonEnv)
        assert result.name is None

    # Test case 6: CONDA_DEFAULT_ENV empty string
    with patch.dict("os.environ", {"CONDA_DEFAULT_ENV": ""}, clear=True):
        result = get_python_env()
        assert isinstance(result, PythonEnv)
        assert result.name is None

    # Test case 7: VIRTUAL_ENV basename extraction
    with patch.dict("os.environ", {"VIRTUAL_ENV": "/Users/david/venv"}, clear=True):
        result = get_python_env()
        assert isinstance(result, PythonEnv)
        assert result.name == "venv"
