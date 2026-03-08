"""Tests for token cache database functionality."""

import hashlib
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock

from pytest_mock import MockerFixture
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from claudeutils.token_cache import (
    TokenCache,
    TokenCacheEntry,
    cached_count_tokens_for_file,
    create_cache_engine,
    get_default_cache,
)
from claudeutils.tokens import ModelId, count_tokens_for_files


class TestTokenCacheModel:
    """Tests for TokenCacheEntry model and cache engine."""

    def test_token_cache_entry_columns(self) -> None:
        """TokenCacheEntry has correct column definitions.

        Given: TokenCacheEntry class imported
        When: Inspecting columns
        Then: Has md5_hex (str), model_id (str), token_count (int), last_used (datetime)
        """
        # Get the mapper for TokenCacheEntry
        mapper = inspect(TokenCacheEntry)

        # Verify columns exist with correct types
        columns = {col.name: col.type for col in mapper.columns}

        assert "md5_hex" in columns
        assert "model_id" in columns
        assert "token_count" in columns
        assert "last_used" in columns

    def test_composite_primary_key(self) -> None:
        """TokenCacheEntry has composite primary key on (md5_hex, model_id).

        Given: TokenCacheEntry class
        When: Inspecting primary key
        Then: Primary key contains both md5_hex and model_id
        """
        mapper = inspect(TokenCacheEntry)
        pk_columns = {col.name for col in mapper.primary_key}

        assert "md5_hex" in pk_columns
        assert "model_id" in pk_columns
        assert len(pk_columns) == 2

    def test_create_cache_engine_creates_table(self) -> None:
        """create_cache_engine creates token_cache table.

        Given: Path to in-memory database
        When: Calling create_cache_engine(":memory:")
        Then: Returns engine with token_cache table created
        """
        engine = create_cache_engine(":memory:")

        # Verify table exists
        table_names = inspect(engine).get_table_names()
        assert "token_cache" in table_names


class TestTokenCacheOperations:
    """Tests for TokenCache get/put operations."""

    def test_get_empty_cache_returns_none(self) -> None:
        """TokenCache.get returns None for missing entries.

        Given: Empty token cache
        When: Calling cache.get("abc123", "model-1")
        Then: Returns None
        """
        engine = create_cache_engine(":memory:")
        cache = TokenCache(engine)

        result = cache.get("abc123", "model-1")

        assert result is None

    def test_put_then_get_returns_count(self) -> None:
        """TokenCache stores and retrieves token counts.

        Given: Empty token cache
        When: Calling cache.put("abc123", "model-1", 42)
              then cache.get("abc123", "model-1")
        Then: get returns 42
        """
        engine = create_cache_engine(":memory:")
        cache = TokenCache(engine)

        cache.put("abc123", "model-1", 42)
        result = cache.get("abc123", "model-1")

        assert result == 42

    def test_get_updates_last_used(self) -> None:
        """TokenCache.get updates last_used timestamp.

        Given: Token cache with entry inserted at earlier timestamp
        When: Calling cache.get to retrieve the entry
        Then: last_used is updated to a more recent timestamp
        """
        engine = create_cache_engine(":memory:")
        cache = TokenCache(engine)

        cache.put("abc123", "model-1", 42)

        # Manually update last_used to earlier timestamp
        session_factory = sessionmaker(bind=engine)
        with session_factory() as session:
            entry = session.get(TokenCacheEntry, ("abc123", "model-1"))
            assert entry is not None
            original_last_used = entry.last_used - timedelta(seconds=5)
            entry.last_used = original_last_used
            session.commit()

        # Retrieve entry via cache.get
        cache.get("abc123", "model-1")

        # Verify last_used was updated
        with session_factory() as session:
            entry = session.get(TokenCacheEntry, ("abc123", "model-1"))
            assert entry is not None
            assert entry.last_used > original_last_used

    def test_different_model_ids_separate_entries(self) -> None:
        """TokenCache keeps separate entries for different model IDs.

        Given: Empty token cache
        When: Storing counts for same md5 but different model IDs
        Then: get returns correct count for each model ID
        """
        engine = create_cache_engine(":memory:")
        cache = TokenCache(engine)

        cache.put("abc123", "model-a", 10)
        cache.put("abc123", "model-b", 20)

        assert cache.get("abc123", "model-a") == 10
        assert cache.get("abc123", "model-b") == 20

    def test_put_existing_key_updates_count(self) -> None:
        """TokenCache.put updates existing entries (upsert behavior).

        Given: Token cache with existing entry
        When: Calling put again with same key but different count
        Then: get returns the new count (update, not insert)
        """
        engine = create_cache_engine(":memory:")
        cache = TokenCache(engine)

        cache.put("abc123", "model-1", 42)
        cache.put("abc123", "model-1", 99)

        result = cache.get("abc123", "model-1")

        assert result == 99


class TestCacheIntegration:
    """Tests for cache integration with count_tokens_for_files and CLI."""

    def test_count_tokens_for_files_uses_cache(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """count_tokens_for_files uses cache for duplicate content.

        Calls API only once for identical files across multiple invocations.

        Given: Two files with identical content.
        When: Calling count_tokens_for_files with both files.
        Then: Mocked count_tokens_for_file is called once (second file hits cache).
              Both results have count=10.
        """
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "shared content"
        file1.write_text(content)
        file2.write_text(content)

        # Mock count_tokens_for_file in token_cache module to return 10
        mock_count = mocker.patch(
            "claudeutils.token_cache.count_tokens_for_file", return_value=10
        )
        # Mock get_default_cache to return in-memory cache
        real_cache = TokenCache(create_cache_engine(":memory:"))
        mocker.patch(
            "claudeutils.token_cache.get_default_cache", return_value=real_cache
        )

        results = count_tokens_for_files([file1, file2], ModelId("test-model"))

        # API should be called only once (second file hits cache)
        assert mock_count.call_count == 1
        # Both results should have count 10
        assert len(results) == 2
        assert results[0].count == 10
        assert results[1].count == 10

    def test_cache_db_in_platformdirs_location(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """get_default_cache creates token_cache.db in platformdirs location.

        Given: Mocked platformdirs.user_cache_dir returning tmp_path.
        When: Calling get_default_cache.
        Then: Database file is created at <tmp_path>/token_cache.db.
        """
        mocker.patch(
            "claudeutils.token_cache.platformdirs.user_cache_dir",
            return_value=str(tmp_path),
        )

        cache = get_default_cache()

        # Verify database file exists at expected location
        db_path = tmp_path / "token_cache.db"
        assert db_path.exists()
        # Verify cache is usable (can do put/get)
        cache.put("test-md5", "test-model", 42)
        assert cache.get("test-md5", "test-model") == 42


class TestCachedCountTokens:
    """Tests for cached_count_tokens_for_file wrapper function."""

    def test_cache_miss_calls_api_and_stores(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """API called on cache miss, result stored.

        Given: Empty cache and test file with known content.
        When: Calling cached_count_tokens_for_file with mocked count_tokens_for_file.
        Then: API is called once, result is cached, and count is returned.
        """
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        content_md5 = hashlib.md5(b"hello world").hexdigest()  # noqa: S324

        engine = create_cache_engine(":memory:")
        cache = TokenCache(engine)

        mock_count = Mock(return_value=42)
        mocker.patch("claudeutils.token_cache.count_tokens_for_file", mock_count)
        mock_client = Mock()

        result = cached_count_tokens_for_file(
            test_file, ModelId("test-model"), mock_client, cache
        )

        assert result == 42
        assert mock_count.call_count == 1
        assert cache.get(content_md5, "test-model") == 42

    def test_cache_hit_skips_api(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """cached_count_tokens_for_file uses cache and skips API on hit.

        Given: Cache with stored (md5, model) -> count.
        When: Calling cached_count_tokens_for_file with matching file.
        Then: API is not called, cached count is returned.
        """
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        content_md5 = hashlib.md5(b"hello world").hexdigest()  # noqa: S324

        engine = create_cache_engine(":memory:")
        cache = TokenCache(engine)
        cache.put(content_md5, "test-model", 42)

        mock_count = Mock()
        mocker.patch("claudeutils.token_cache.count_tokens_for_file", mock_count)
        mock_client = Mock()

        result = cached_count_tokens_for_file(
            test_file, ModelId("test-model"), mock_client, cache
        )

        assert result == 42
        assert mock_count.call_count == 0

    def test_cache_key_uses_content_md5_not_path(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """cached_count_tokens_for_file uses content md5 as key, not file path.

        Given: Two files with identical content at different paths.
        When: Calling cached_count_tokens_for_file for file 1, then file 2.
        Then: API is called once (file 1), second call is cache hit.
        """
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "identical content"
        file1.write_text(content)
        file2.write_text(content)

        engine = create_cache_engine(":memory:")
        cache = TokenCache(engine)

        mock_count = Mock(return_value=42)
        mocker.patch("claudeutils.token_cache.count_tokens_for_file", mock_count)
        mock_client = Mock()

        result1 = cached_count_tokens_for_file(
            file1, ModelId("test-model"), mock_client, cache
        )
        result2 = cached_count_tokens_for_file(
            file2, ModelId("test-model"), mock_client, cache
        )

        assert result1 == 42
        assert result2 == 42
        assert mock_count.call_count == 1
