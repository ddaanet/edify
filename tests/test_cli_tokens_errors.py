"""Tests for tokens CLI error reporting (auth, rate limit)."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from anthropic import AuthenticationError
from pytest_mock import MockerFixture

from edify.exceptions import ApiAuthenticationError, ApiRateLimitError
from edify.token_cache import TokenCache, create_cache_engine
from edify.tokens_cli import handle_tokens


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

    # Mock client construction to raise AuthenticationError
    mock_make_client = mocker.patch("edify.tokens_cli.make_client", autospec=True)
    mock_make_client.side_effect = AuthenticationError(
        "Invalid API key", response=Mock(), body={}
    )
    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("sonnet", [str(test_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Authentication failed" in captured.err
    assert "ANTHROPIC_API_KEY" in captured.err


def test_cli_auth_error_states_each_part_once(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Report an auth failure without stuttering.

    Given: A revoked credential, so alias resolution raises
           ApiAuthenticationError (whose message already carries the hint)
    When: handle_tokens called with model="sonnet", files=[test_file]
    Then: stderr states "Authentication failed" once and the config hint once,
    and still surfaces the API's reason
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello world")

    mocker.patch("edify.tokens_cli.make_client", autospec=True)
    mocker.patch(
        "edify.tokens_cli.resolve_model_alias",
        side_effect=ApiAuthenticationError("OAuth access token has been revoked."),
    )

    with pytest.raises(SystemExit):
        handle_tokens("sonnet", [str(test_file)])

    captured = capsys.readouterr()
    assert captured.err.count("Authentication failed") == 1
    assert captured.err.count("ANTHROPIC_API_KEY") == 1
    assert "revoked" in captured.err


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

    # Mock client construction to avoid instantiation with SOCKS proxy
    mocker.patch("edify.tokens_cli.make_client", autospec=True)

    # Setup mocks with resolve returning model and count_tokens raising error
    mock_resolve = mocker.patch("edify.tokens_cli.resolve_model_alias", autospec=True)
    mock_resolve.return_value = "claude-sonnet-4-5-20250929"
    mocker.patch(
        "edify.token_cache.get_default_cache",
        return_value=TokenCache(create_cache_engine(":memory:")),
    )
    mock_count = mocker.patch(
        "edify.token_cache._count_tokens_for_content", autospec=True
    )
    mock_count.side_effect = ApiRateLimitError()
    with pytest.raises(SystemExit) as exc_info:
        handle_tokens("sonnet", [str(test_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Rate limit exceeded" in captured.err
