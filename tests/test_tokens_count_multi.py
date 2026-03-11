"""Unit tests for count_tokens_for_files function."""

from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import pytest
from anthropic import APIError
from pytest_mock import MockerFixture

from claudeutils.exceptions import ApiError
from claudeutils.tokens import (
    ModelId,
    TokenCount,
    calculate_total,
    count_tokens_for_file,
    count_tokens_for_files,
)


class TestCountTokensForFiles:
    """Tests for count_tokens_for_files function."""

    def test_count_tokens_for_files_reuses_single_client(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
        mocker: MockerFixture,
    ) -> None:
        """Verify client is reused across multiple files.

        Given: Three test files ("Hello", "World", "Test"), mock client
        When: count_tokens_for_files is called with paths and resolved ID
        Then: Returns three TokenCount objects, client's
        messages.count_tokens called exactly 3 times
        """
        # Create test files
        file1 = tmp_path / "file1.md"
        file1.write_text("Hello")
        file2 = tmp_path / "file2.md"
        file2.write_text("World")
        file3 = tmp_path / "file3.md"
        file3.write_text("Test")

        # Setup mock with side_effect for multiple responses
        mock_responses = [
            Mock(input_tokens=2),
            Mock(input_tokens=1),
            Mock(input_tokens=3),
        ]
        mock_client = mock_anthropic_client(side_effect=mock_responses)

        # Bypass token cache so API mock is exercised
        mocker.patch(
            "claudeutils.token_cache.get_default_cache",
            side_effect=Exception("no cache"),
        )

        # Call function
        results = count_tokens_for_files(
            [file1, file2, file3],
            ModelId("claude-sonnet-4-5-20250929"),
        )

        # Verify
        assert len(results) == 3
        assert mock_client.messages.count_tokens.call_count == 3

    def test_count_tokens_for_multiple_files(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Count tokens for multiple files.

        Given: Two files: "Hello" (file1), "World" (file2), model="sonnet"
        When: count_tokens_for_files(paths, model) called
        Then: Returns list of TokenCount objects with per-file counts
        """
        # Create test files
        file1 = tmp_path / "file1.md"
        file1.write_text("Hello")
        file2 = tmp_path / "file2.md"
        file2.write_text("World")

        # Setup mock with side_effect for multiple responses
        mock_responses = [
            Mock(input_tokens=2),
            Mock(input_tokens=1),
        ]
        mock_anthropic_client(side_effect=mock_responses)

        # Call function
        results = count_tokens_for_files([file1, file2], ModelId("sonnet"))

        # Verify
        assert len(results) == 2
        assert results[0].path == str(file1)
        assert results[0].count == 2
        assert results[1].path == str(file2)
        assert results[1].count == 1

    def test_calculate_total_across_files(self) -> None:
        """Calculate total tokens across files.

        Given: TokenCount results for 3 files: [5, 10, 8]
        When: calculate_total(results) called
        Then: Returns 23
        """
        results = [
            TokenCount(path="file1.md", count=5),
            TokenCount(path="file2.md", count=10),
            TokenCount(path="file3.md", count=8),
        ]

        total = calculate_total(results)

        assert total == 23

    def test_preserve_file_order_in_results(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Preserve file order in results.

        Given: Files [b.md, a.md, c.md] in that order, model="haiku"
        When: count_tokens_for_files(paths, model) called
        Then: Results maintain input order [b.md, a.md, c.md]
        """
        # Create test files in specific order
        file_b = tmp_path / "b.md"
        file_b.write_text("B")
        file_a = tmp_path / "a.md"
        file_a.write_text("A")
        file_c = tmp_path / "c.md"
        file_c.write_text("C")

        # Setup mock with side_effect for multiple responses
        mock_responses = [
            Mock(input_tokens=10),
            Mock(input_tokens=20),
            Mock(input_tokens=30),
        ]
        mock_anthropic_client(side_effect=mock_responses)

        # Call function with files in order [b, a, c]
        results = count_tokens_for_files([file_b, file_a, file_c], ModelId("haiku"))

        # Verify order is preserved
        assert len(results) == 3
        assert results[0].path == str(file_b)
        assert results[1].path == str(file_a)
        assert results[2].path == str(file_c)

    def test_count_tokens_handles_network_error(
        self,
        tmp_path: Path,
        mock_anthropic_client: Callable[..., Mock],
    ) -> None:
        """Handle generic API errors.

        Given: Test file with content, mock to raise APIError
        When: count_tokens_for_file is called
        Then: Raises ApiError with message containing "API error"
        """
        # Create test file
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        # Setup mock to raise APIError
        api_error = APIError("Connection timeout", request=Mock(), body={})
        mock_client = mock_anthropic_client(side_effect=api_error)

        # Call function, should raise ApiError
        with pytest.raises(ApiError) as exc_info:
            count_tokens_for_file(test_file, ModelId("sonnet"), mock_client)

        # Verify error message contains "API error"
        error_msg = str(exc_info.value).lower()
        assert "api error" in error_msg
