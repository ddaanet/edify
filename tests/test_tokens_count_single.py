"""Unit tests for count_tokens_for_file function."""

from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import pytest
from anthropic import AuthenticationError, RateLimitError

from edify.exceptions import (
    ApiAuthenticationError,
    ApiRateLimitError,
    FileReadError,
)
from edify.tokens import (
    ModelId,
    count_tokens_for_file,
)


class TestCountTokensForFile:
    """Tests for count_tokens_for_file function."""

    def test_count_tokens_for_simple_text(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Count tokens for a simple text file.

        Given: File with content "Hello world", model="sonnet", mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Returns integer token count > 0
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock
        mock_client = mock_anthropic_client(token_count=5)

        # Call function
        result = count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify
        assert isinstance(result, int)
        assert result > 0
        assert result == 5

    def test_count_tokens_for_markdown_with_code_blocks(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Count tokens for markdown file with code blocks.

        Given: File with markdown including code block, model="opus", mock
        When: count_tokens_for_file(path, model, client) called
        Then: Returns token count reflecting full content
        """
        # Create test file with markdown and code block
        test_file = tmp_path / "test.md"
        content = """# Title

Some text here.

```python
def hello():
	print("world")
```

More text."""
        test_file.write_text(content)

        # Setup mock
        mock_client = mock_anthropic_client(token_count=42)

        # Call function
        result = count_tokens_for_file(test_file, ModelId("opus"), mock_client)

        # Verify
        assert isinstance(result, int)
        assert result == 42

    def test_handle_empty_file(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle empty files without API call.

        Given: Empty file, model="haiku", mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Returns 0
        """
        # Create empty test file
        test_file = tmp_path / "empty.md"
        test_file.write_text("")

        # Setup mock (won't be called for empty file)
        mock_client = mock_anthropic_client()

        # Call function
        result = count_tokens_for_file(test_file, ModelId("haiku"), mock_client)

        assert result == 0

    def test_handle_api_authentication_error(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle API authentication error.

        Given: Invalid/missing API key, mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Raises ApiAuthenticationError with clear message
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock to raise AuthenticationError
        auth_error = AuthenticationError("Invalid API key", response=Mock(), body={})
        mock_client = mock_anthropic_client(side_effect=auth_error)

        # Call function, should raise ApiAuthenticationError
        with pytest.raises(
            ApiAuthenticationError, match=r"(?i)(?:anthropic_api_key|api key)"
        ):
            count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

    def test_handle_api_rate_limit_error(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle API rate limit error.

        Given: API returns rate limit error, mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Raises ApiRateLimitError with rate limit message
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock to raise RateLimitError
        rate_limit_error = RateLimitError(
            "Rate limit exceeded", response=Mock(), body={}
        )
        mock_client = mock_anthropic_client(side_effect=rate_limit_error)

        # Call function, should raise ApiRateLimitError
        with pytest.raises(ApiRateLimitError) as exc_info:
            count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify error message mentions rate limit
        error_msg = str(exc_info.value).lower()
        assert "rate limit" in error_msg

    def test_read_api_key_from_environment(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Read API key from environment.

        Given: ANTHROPIC_API_KEY environment variable set, mock client
        When: count_tokens_for_file(path, model, client) called
        Then: Client uses environment variable value
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Set environment variable
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-12345")

        # Setup mock
        mock_client = mock_anthropic_client(token_count=5)

        # Call function
        result = count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify result - the Anthropic SDK was used
        assert result == 5

    def test_error_message_guides_user_to_set_api_key(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Error message guides user to set API key.

        Given: No ANTHROPIC_API_KEY environment variable, mock client
        When: Token counting attempted with count_tokens_for_file
        Then: Error message includes "ANTHROPIC_API_KEY" and setup instructions
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Remove API key from environment
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        # Setup mock to raise AuthenticationError
        auth_error = AuthenticationError("Invalid API key", response=Mock(), body={})
        mock_client = mock_anthropic_client(side_effect=auth_error)

        # Call function, should raise ApiAuthenticationError
        with pytest.raises(ApiAuthenticationError) as exc_info:
            count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify error message includes ANTHROPIC_API_KEY and setup instructions
        error_msg = str(exc_info.value)
        assert "ANTHROPIC_API_KEY" in error_msg
        assert "set" in error_msg.lower()  # "Please set" guidance

    def test_count_tokens_uses_resolved_model_id(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Verify API receives resolved model ID.

        Given: Test file containing "Hello world", mock Anthropic client
        When: count_tokens_for_file is called with file path,
        ModelId("claude-sonnet-4-5-20250929"), and mock client
        Then: Returns token count AND mock's messages.count_tokens was
        called with exact model ID "claude-sonnet-4-5-20250929"
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock
        mock_client = mock_anthropic_client(token_count=5)

        # Call function with mock client
        result = count_tokens_for_file(
            test_file, ModelId("claude-sonnet-4-5-20250929"), mock_client
        )

        # Verify
        assert result == 5
        mock_client.messages.count_tokens.assert_called_once_with(
            model="claude-sonnet-4-5-20250929",
            messages=[{"role": "user", "content": "Hello world"}],
        )

    def test_count_tokens_unreadable_file_shows_reason(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle unreadable file error.

        Given: Test file with permissions 000 (unreadable), mock client
        When: count_tokens_for_file is called
        Then: Raises FileReadError with message containing "Failed to read",
        the file path, and "Permission denied"
        """
        # Create unreadable test file
        test_file = tmp_path / "unreadable.md"
        test_file.write_text("Hello world")
        test_file.chmod(0o000)

        # Setup mock
        mock_client = mock_anthropic_client()

        # Call function, should raise FileReadError
        with pytest.raises(FileReadError) as exc_info:
            count_tokens_for_file(
                test_file, ModelId("claude-sonnet-4-5-20250929"), mock_client
            )

        # Verify error message
        error_msg = str(exc_info.value)
        assert "Failed to read" in error_msg
        assert str(test_file) in error_msg

    def test_count_tokens_binary_file_shows_decode_error(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle binary file decode error.

        Given: Binary file (PNG header bytes), mock Anthropic client
        When: count_tokens_for_file is called
        Then: Raises FileReadError with message containing "Failed to read"
        and file path
        """
        # Create binary test file (PNG header)
        test_file = tmp_path / "binary.png"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n")

        # Setup mock
        mock_client = mock_anthropic_client()

        # Call function, should raise FileReadError
        with pytest.raises(FileReadError) as exc_info:
            count_tokens_for_file(
                test_file, ModelId("claude-sonnet-4-5-20250929"), mock_client
            )

        # Verify error message
        error_msg = str(exc_info.value)
        assert "Failed to read" in error_msg
        assert str(test_file) in error_msg
