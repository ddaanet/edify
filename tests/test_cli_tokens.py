"""Integration tests for tokens CLI subcommand."""

import io
import json
import sys
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import pytest
from anthropic import AuthenticationError
from click.testing import CliRunner
from pytest_mock import MockerFixture

from claudeutils.cli import cli
from claudeutils.exceptions import ApiRateLimitError
from claudeutils.token_cache import TokenCache, create_cache_engine
from claudeutils.tokens_cli import handle_tokens


def test_cli_requires_model_argument(tmp_path: Path) -> None:
    """Test that CLI requires model argument."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    runner = CliRunner()
    result = runner.invoke(cli, ["tokens", str(test_file)])

    # Click returns exit code 2 for missing required arguments
    assert result.exit_code == 2
    # Click says "missing argument" instead of "required argument"
    assert "missing" in result.output.lower() or "required" in result.output.lower()


def test_cli_accepts_single_file(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test that CLI accepts single file with model."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Setup mocks
    mock_token_counting(model_id="claude-sonnet-4-5-20250929", counts=42)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("sonnet", [str(test_file)])
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert "test.md" in output
    assert "42" in output


def test_cli_reports_missing_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    cli_base_mocks: dict[str, Mock],
) -> None:
    """Test that CLI reports missing file."""
    missing_file = tmp_path / "missing.md"

    cli_base_mocks["anthropic"].return_value = Mock()
    cli_base_mocks["resolve"].return_value = "claude-haiku-4-5-20251001"

    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("haiku", [str(missing_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "missing.md" in captured.err or "Failed to read" in captured.err


def test_cli_handles_multiple_files(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test that CLI handles multiple files."""
    file1 = tmp_path / "a.md"
    file2 = tmp_path / "b.md"
    file1.write_text("Hello")
    file2.write_text("World")

    # Setup mocks
    mock_token_counting(model_id="claude-opus-4-5-20251101", counts=[10, 20])
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("opus", [str(file1), str(file2)])
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    assert "a.md" in output
    assert "b.md" in output
    assert "10" in output
    assert "20" in output


def test_cli_text_format_with_model_id(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test default text format shows model ID and file counts."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Setup mocks
    mock_token_counting(model_id="claude-sonnet-4-5-20250929", counts=42)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("sonnet", [str(test_file)])
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    lines = output.strip().split("\n")
    assert "Using model: claude-sonnet-4-5-20250929" in lines[0]
    assert "test.md: 42 tokens" in output


def test_cli_json_format_with_model_id(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test JSON format outputs structured data with model ID."""
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Setup mocks
    mock_token_counting(model_id="claude-haiku-4-5-20251001", counts=42)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("haiku", [str(test_file)], json_output=True)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    result = json.loads(output)
    assert result["model"] == "claude-haiku-4-5-20251001"
    assert len(result["files"]) == 1
    assert result["files"][0]["path"] == str(test_file)
    assert result["files"][0]["count"] == 42
    assert result["total"] == 42


def test_cli_json_format_with_multiple_files(
    tmp_path: Path,
    mock_token_counting: Callable[..., None],
) -> None:
    """Test JSON format with multiple files."""
    file1 = tmp_path / "file1.md"
    file2 = tmp_path / "file2.md"
    file1.write_text("Hello")
    file2.write_text("World")

    # Setup mocks
    mock_token_counting(model_id="claude-opus-4-5-20251101", counts=[10, 20])
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        handle_tokens("opus", [str(file1), str(file2)], json_output=True)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout

    result = json.loads(output)
    assert result["model"] == "claude-opus-4-5-20251101"
    assert len(result["files"]) == 2
    assert result["files"][0]["path"] == str(file1)
    assert result["files"][0]["count"] == 10
    assert result["files"][1]["path"] == str(file2)
    assert result["files"][1]["count"] == 20
    assert result["total"] == 30


def test_cli_auth_error_shows_helpful_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], mocker: MockerFixture
) -> None:
    """Handle CLI authentication error with helpful message.

    Given: Test file exists, mock Anthropic() to raise AuthenticationError
    When: handle_tokens called with model="sonnet", files=[test_file]
    Then: Exits with code 1, stderr has "Authentication failed" and
    "ANTHROPIC_API_KEY"
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Mock Anthropic() to raise AuthenticationError
    mock_anthropic_class = mocker.patch(
        "claudeutils.tokens_cli.Anthropic", autospec=True
    )
    mock_anthropic_class.side_effect = AuthenticationError(
        "Invalid API key", response=Mock(), body={}
    )
    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("sonnet", [str(test_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Authentication failed" in captured.err
    assert "ANTHROPIC_API_KEY" in captured.err


def test_cli_rate_limit_error_shows_message(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Handle CLI rate limit error.

    Given: Mock count_tokens_for_file to raise ApiRateLimitError
    When: handle_tokens is called
    Then: Exits with code 1, stderr contains "Error: Rate limit exceeded"
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    # Set fake API key to pass authentication check
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

    # Mock Anthropic client to avoid instantiation with SOCKS proxy
    mocker.patch("claudeutils.tokens_cli.Anthropic", autospec=True)

    # Setup mocks with resolve returning model and count_tokens raising error
    mock_resolve = mocker.patch(
        "claudeutils.tokens_cli.resolve_model_alias", autospec=True
    )
    mock_resolve.return_value = "claude-sonnet-4-5-20250929"
    mocker.patch(
        "claudeutils.token_cache.get_default_cache",
        return_value=TokenCache(create_cache_engine(":memory:")),
    )
    mock_count = mocker.patch(
        "claudeutils.token_cache._count_tokens_for_content", autospec=True
    )
    mock_count.side_effect = ApiRateLimitError()
    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("sonnet", [str(test_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Rate limit exceeded" in captured.err


def test_cli_permission_error_propagates(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    cli_base_mocks: dict[str, Mock],
) -> None:
    """Handle CLI permission error from unreadable file.

    Given: File with permissions 000 (unreadable), model="haiku"
    When: handle_tokens("haiku", [unreadable_file]) called
    Then: Raises SystemExit with code 1, stderr contains "Permission denied" or
    "Failed to read"
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")
    test_file.chmod(0o000)

    try:
        cli_base_mocks["anthropic"].return_value = Mock()
        cli_base_mocks["resolve"].return_value = "claude-haiku-4-5-20251001"
        with pytest.raises(SystemExit) as exc_info:
            handle_tokens("haiku", [str(test_file)])

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err
        # Check for either permission error or generic file read error
        assert "Permission denied" in captured.err or "Failed to read" in captured.err
    finally:
        # Restore permissions for cleanup
        test_file.chmod(0o644)


def test_cli_decode_error_propagates(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    cli_base_mocks: dict[str, Mock],
) -> None:
    """Handle CLI decode error from binary file.

    Given: Binary file (PNG header), model="opus"
    When: handle_tokens("opus", [binary_file]) called
    Then: Raises SystemExit with code 1, stderr contains "Failed to read"
    """
    # Setup - create binary file with PNG header
    binary_file = tmp_path / "test.png"
    binary_file.write_bytes(b"\x89PNG\r\n\x1a\n")

    cli_base_mocks["anthropic"].return_value = Mock()
    cli_base_mocks["resolve"].return_value = "claude-opus-4-5-20251101"
    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("opus", [str(binary_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "Failed to read" in captured.err


def test_cli_detects_empty_api_key_before_sdk(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    api_key_empty: None,
    mocker: MockerFixture,
) -> None:
    """CLI validates empty API key before SDK instantiation.

    Given: Test file "test.md" with content "Hello", ANTHROPIC_API_KEY=""
    When: handle_tokens("sonnet", [test_file]) called
    Then: Raises SystemExit with code 1, stderr contains "Authentication failed"
    and "ANTHROPIC_API_KEY"
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello")

    # Mock config file fallback - should also return no key
    mocker.patch("claudeutils.tokens_cli.get_api_key", return_value=None)
    # Mock SDK components - should NOT be called
    mock_anthropic = mocker.patch("claudeutils.tokens_cli.Anthropic", autospec=True)
    mock_resolve = mocker.patch(
        "claudeutils.tokens_cli.resolve_model_alias", autospec=True
    )

    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("sonnet", [str(test_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Authentication failed" in captured.err
    assert "ANTHROPIC_API_KEY" in captured.err

    # Verify SDK was never called
    assert not mock_anthropic.called
    assert not mock_resolve.called


def test_cli_detects_missing_api_key_before_sdk(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    api_key_unset: None,
    mocker: MockerFixture,
) -> None:
    """CLI validates missing API key before SDK instantiation.

    Given: Test file "test.md" with content "Hello", ANTHROPIC_API_KEY not set
    When: handle_tokens("haiku", [test_file]) called
    Then: Raises SystemExit with code 1, stderr contains "Authentication failed"
    and "ANTHROPIC_API_KEY"
    """
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello")

    # Mock config file fallback - should also return no key
    mocker.patch("claudeutils.tokens_cli.get_api_key", return_value=None)
    # Mock SDK components - should NOT be called
    mock_anthropic = mocker.patch("claudeutils.tokens_cli.Anthropic", autospec=True)
    mock_resolve = mocker.patch(
        "claudeutils.tokens_cli.resolve_model_alias", autospec=True
    )

    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("haiku", [str(test_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Authentication failed" in captured.err
    assert "ANTHROPIC_API_KEY" in captured.err

    # Verify SDK was never called (missing key test)
    assert not mock_anthropic.called
    assert not mock_resolve.called
