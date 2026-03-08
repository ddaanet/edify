"""Tests for token cache database functionality."""

from datetime import timedelta

from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from claudeutils.token_cache import TokenCache, TokenCacheEntry, create_cache_engine


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
