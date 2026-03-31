"""Unit tests for basic resolve_model_alias functionality."""

from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import anthropic
import pytest

from edify.exceptions import ModelResolutionError
from edify.tokens import resolve_model_alias


class TestResolveModelAliasBasic:
    """Tests for basic model alias resolution logic."""

    def test_pass_full_model_ids_through_unchanged(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Pass full model IDs (with date suffix) through unchanged.

        Given: model="claude-sonnet-4-5-20250929" (full model ID with date suffix)
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Returns same ID unchanged (no API call, no cache check)
        """
        # Setup mock (won't be called)
        cache_dir = tmp_path / "cache"
        mock_client = mock_models_api()

        # Call function
        result = resolve_model_alias(
            "claude-sonnet-4-5-20250929", mock_client, cache_dir
        )

        # Verify
        assert result == "claude-sonnet-4-5-20250929"
        # Ensure no API calls were made
        mock_client.models.list.assert_not_called()

    def test_handle_unknown_model_alias(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Handle unknown model alias.

        Given: API returns models list, model="unknown-alias"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Returns "unknown-alias" unchanged (pass through to API)
        """
        # Setup: no cache file
        cache_dir = tmp_path / "cache"

        # Setup mock with models list (no matching alias)
        models = [
            {
                "id": "claude-sonnet-4-5-20250929",
                "created_at": "2025-09-29T00:00:00Z",
            },
        ]
        mock_client = mock_models_api(models=models)

        # Call function with unknown alias
        result = resolve_model_alias("unknown-alias", mock_client, cache_dir)

        # Verify - should return original input unchanged
        assert result == "unknown-alias"

    def test_resolve_versioned_model_id_to_full_id(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Resolve versioned model ID to full ID with date suffix.

        Given: Mock client with models including "claude-sonnet-4-5-20250929"
               and "claude-sonnet-4-5-20241022", cache directory
        When: resolve_model_alias called with "claude-sonnet-4-5" (versioned
        model ID without date)
        Then: Returns "claude-sonnet-4-5-20250929" (latest 4-5 version with
        full date suffix)
        """
        # Setup: no cache file
        cache_dir = tmp_path / "cache"

        # Setup mock with models list including different versions of sonnet
        models = [
            {
                "id": "claude-sonnet-4-5-20250929",
                "created_at": "2025-09-29T00:00:00Z",
            },
            {
                "id": "claude-sonnet-4-5-20241022",
                "created_at": "2024-10-22T00:00:00Z",
            },
            {
                "id": "claude-opus-4-5-20250228",
                "created_at": "2025-02-28T00:00:00Z",
            },
        ]
        mock_client = mock_models_api(models=models)

        # Call function with versioned model ID (no date suffix)
        result = resolve_model_alias("claude-sonnet-4-5", mock_client, cache_dir)

        # Verify - should return latest sonnet 4-5 model with date suffix
        assert result == "claude-sonnet-4-5-20250929"
        # Verify API was called
        mock_client.models.list.assert_called_once()

    def test_fail_when_models_api_error_prevents_resolution(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Fail when models API error prevents resolution.

        Given: client.models.list() raises API error, model="sonnet"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Raises ModelResolutionError with message explaining API unreachable
        """
        # Setup: no cache file
        cache_dir = tmp_path / "cache"

        # Setup mock that raises API error
        api_error = anthropic.APIError("API Error", request=Mock(), body={})
        mock_client = mock_models_api(raise_error=api_error)

        # Call function with unversioned alias, should raise ModelResolutionError
        with pytest.raises(ModelResolutionError) as exc_info:
            resolve_model_alias("sonnet", mock_client, cache_dir)

        # Verify error message explains the issue
        error_msg = str(exc_info.value).lower()
        assert "models api" in error_msg
        assert "unreachable" in error_msg
