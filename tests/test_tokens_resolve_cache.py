"""Unit tests for resolve_model_alias cache behavior."""

import json
import os
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest

from edify.tokens import resolve_model_alias


class TestResolveModelAliasCache:
    """Tests for model alias resolution cache behavior."""

    def test_resolve_unversioned_alias_from_fresh_cache(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Resolve unversioned alias from fresh cache.

        Given: Cache file exists with valid models list (created < 24h ago),
               includes `claude-haiku-4-5-20251001` and `claude-3-5-haiku-20241022`,
               model="haiku"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Returns `claude-haiku-4-5-20251001` from cache (no API call)
        """
        # Setup cache file
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "models_cache.json"

        # Use a timestamp from 1 hour ago (fresh)
        fresh_time = (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat()

        cache_data = {
            "fetched_at": fresh_time,
            "models": [
                {
                    "id": "claude-haiku-4-5-20251001",
                    "created_at": "2025-10-01T00:00:00Z",
                },
                {
                    "id": "claude-3-5-haiku-20241022",
                    "created_at": "2024-10-22T00:00:00Z",
                },
            ],
        }
        cache_file.write_text(json.dumps(cache_data))

        # Setup mock (won't be called)
        mock_client = mock_models_api()

        # Call function
        result = resolve_model_alias("haiku", mock_client, cache_dir)

        # Verify - should return latest haiku model from cache
        assert result == "claude-haiku-4-5-20251001"
        # Ensure no API calls were made
        mock_client.models.list.assert_not_called()

    def test_resolve_unversioned_alias_with_cache_miss(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Resolve unversioned alias with cache miss.

        Given: No cache file exists, mock API returns models list, model="sonnet"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Queries API, writes cache, returns latest sonnet model ID
        """
        # Setup: no cache file
        cache_dir = tmp_path / "cache"

        # Setup mock with models list response
        models = [
            {
                "id": "claude-sonnet-4-5-20250929",
                "created_at": "2025-09-29T00:00:00Z",
            },
            {
                "id": "claude-sonnet-4-5-20250915",
                "created_at": "2025-09-15T00:00:00Z",
            },
        ]
        mock_client = mock_models_api(models=models)

        # Call function
        result = resolve_model_alias("sonnet", mock_client, cache_dir)

        # Verify - should return latest sonnet model
        assert result == "claude-sonnet-4-5-20250929"
        # Verify API was called
        mock_client.models.list.assert_called_once()
        # Verify cache was written
        cache_file = cache_dir / "models_cache.json"
        assert cache_file.exists()

    def test_resolve_with_expired_cache(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Resolve with expired cache.

        Given: Cache file exists but created > 24h ago, model="opus"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Ignores stale cache, queries API, updates cache
        """
        # Setup: create old cache file
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "models_cache.json"

        # Create cache with models older than 24h
        cache_data = {
            "fetched_at": "2025-12-27T10:30:00Z",
            "models": [
                {
                    "id": "claude-opus-4-20250228",
                    "created_at": "2025-02-28T00:00:00Z",
                },
            ],
        }
        cache_file.write_text(json.dumps(cache_data))

        # Make cache file's mtime > 24h old
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        cache_file.touch()
        os.utime(cache_file, (old_time, old_time))

        # Setup mock with new models
        models = [
            {
                "id": "claude-opus-4-5-20251101",
                "created_at": "2025-11-01T00:00:00Z",
            },
        ]
        mock_client = mock_models_api(models=models)

        # Call function
        result = resolve_model_alias("opus", mock_client, cache_dir)

        # Verify - should return new opus model
        assert result == "claude-opus-4-5-20251101"
        # Verify API was called
        mock_client.models.list.assert_called_once()

    def test_handle_corrupted_cache_file(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Handle corrupted cache file.

        Given: Cache file exists but contains invalid JSON, model="haiku"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Treats as cache miss, queries API, overwrites corrupted cache
        """
        # Setup: create corrupted cache file
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "models_cache.json"

        # Write invalid JSON
        cache_file.write_text("{invalid json}")

        # Setup mock with models
        models = [
            {
                "id": "claude-haiku-4-5-20251001",
                "created_at": "2025-10-01T00:00:00Z",
            },
        ]
        mock_client = mock_models_api(models=models)

        # Call function
        result = resolve_model_alias("haiku", mock_client, cache_dir)

        # Verify warning was logged
        assert "Corrupted cache file" in caplog.text
        assert str(cache_file) in caplog.text

        # Verify - should return haiku model from API
        assert result == "claude-haiku-4-5-20251001"
        # Verify API was called
        mock_client.models.list.assert_called_once()
        # Verify cache was overwritten
        cached = json.loads(cache_file.read_text())
        assert cached["models"][0]["id"] == "claude-haiku-4-5-20251001"

    def test_create_cache_directory_if_missing(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Create cache directory if missing.

        Given: Cache directory does not exist, model="sonnet"
        When: resolve_model_alias(model, client, cache_dir) called
        Then: Cache directory is created, cache file written successfully
        """
        # Setup: cache directory doesn't exist
        cache_dir = tmp_path / "nonexistent" / "nested" / "cache"

        # Setup mock with models
        models = [
            {
                "id": "claude-sonnet-4-5-20250929",
                "created_at": "2025-09-29T00:00:00Z",
            },
        ]
        mock_client = mock_models_api(models=models)

        # Call function
        result = resolve_model_alias("sonnet", mock_client, cache_dir)

        # Verify - should return sonnet model
        assert result == "claude-sonnet-4-5-20250929"
        # Verify cache directory was created
        assert cache_dir.exists()
        # Verify cache file was written
        cache_file = cache_dir / "models_cache.json"
        assert cache_file.exists()

    def test_cache_expired_by_fetched_at_not_mtime(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Cache expired by fetched_at timestamp, not file mtime.

        Given: Cache file with `fetched_at` from 25 hours ago, file mtime
        set to 1 hour ago
        When: resolve_model_alias is called
        Then: Cache treated as expired by fetched_at, API models.list()
        called
        """
        # Setup: create cache file with old fetched_at
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "models_cache.json"

        # Cache data with fetched_at from 25 hours ago (expired)
        old_time = (datetime.now(tz=UTC) - timedelta(hours=25)).isoformat()
        cache_data = {
            "fetched_at": old_time,
            "models": [
                {
                    "id": "claude-sonnet-4-5-20250929",
                    "created_at": "2025-09-29T00:00:00Z",
                },
            ],
        }
        cache_file.write_text(json.dumps(cache_data))

        # Set file mtime to 1 hour ago (recent)
        recent_time = time.time() - (1 * 3600)
        cache_file.touch()
        os.utime(cache_file, (recent_time, recent_time))

        # Setup mock with new models
        models = [
            {
                "id": "claude-sonnet-4-5-20250929",
                "created_at": "2025-09-29T00:00:00Z",
            },
        ]
        mock_client = mock_models_api(models=models)

        # Call function
        result = resolve_model_alias("sonnet", mock_client, cache_dir)

        # Verify - should have called API because fetched_at is expired
        assert result == "claude-sonnet-4-5-20250929"
        mock_client.models.list.assert_called_once()

    def test_cache_valid_by_fetched_at_ignores_old_mtime(
        self,
        tmp_path: Path,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Cache valid by fetched_at, ignores old file mtime.

        Given: Cache file with `fetched_at` from 1 hour ago, file mtime
        set to 25 hours ago
        When: resolve_model_alias is called
        Then: Cached data used (valid by fetched_at), API models.list()
        NOT called
        """
        # Setup: create cache file with recent fetched_at but old mtime
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_file = cache_dir / "models_cache.json"

        # Cache data with fetched_at from 1 hour ago (fresh)
        fresh_time = (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat()
        cache_data = {
            "fetched_at": fresh_time,
            "models": [
                {
                    "id": "claude-sonnet-4-5-20250929",
                    "created_at": "2025-09-29T00:00:00Z",
                },
            ],
        }
        cache_file.write_text(json.dumps(cache_data))

        # Set file mtime to 25 hours ago (old)
        old_mtime = time.time() - (25 * 3600)
        cache_file.touch()
        os.utime(cache_file, (old_mtime, old_mtime))

        # Setup mock (should not be called)
        mock_client = mock_models_api()

        # Call function
        result = resolve_model_alias("sonnet", mock_client, cache_dir)

        # Verify - should use cached data and NOT call API
        assert result == "claude-sonnet-4-5-20250929"
        mock_client.models.list.assert_not_called()

    def test_cache_write_failure_continues_successfully(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
        mock_models_api: Callable[..., Mock],
    ) -> None:
        """Handle cache write failures gracefully.

        Given: Integration test with read-only cache directory, mock Anthropic API
        When: resolve_model_alias is called (attempts cache write after API call)
        Then: Returns correct model ID successfully (write failure is non-fatal)
        """
        # Setup: create read-only cache directory
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        cache_dir.chmod(0o444)  # Read-only

        # Setup mock with models list
        models = [
            {
                "id": "claude-sonnet-4-5-20250929",
                "created_at": "2025-09-29T00:00:00Z",
            },
        ]
        mock_client = mock_models_api(models=models)

        # Call function - should succeed despite cache write failure
        result = resolve_model_alias("sonnet", mock_client, cache_dir)

        # Verify - should return model even though cache write failed
        assert result == "claude-sonnet-4-5-20250929"
        # Verify API was called
        mock_client.models.list.assert_called_once()
        # Verify warning was logged
        assert "Failed to write cache" in caplog.text

        # Cleanup: restore permissions so tmp_path can be cleaned up
        cache_dir.chmod(0o755)
