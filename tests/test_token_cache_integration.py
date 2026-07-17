"""Tests for cache integration with count_tokens_for_files."""

from pathlib import Path
from unittest.mock import Mock

from pytest_mock import MockerFixture

from edify.token_cache import TokenCache, create_cache_engine, get_default_cache
from edify.tokens import ModelId, count_tokens_for_files


class TestCacheIntegration:
    """Tests for cache integration with count_tokens_for_files and CLI."""

    def test_count_tokens_for_files_uses_cache(
        self, tmp_path: Path, mocker: MockerFixture, mock_client: Mock
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
            "edify.token_cache._count_tokens_for_content", return_value=10
        )
        # Mock get_default_cache to return in-memory cache
        real_cache = TokenCache(create_cache_engine(":memory:"))
        mocker.patch("edify.token_cache.get_default_cache", return_value=real_cache)

        results = count_tokens_for_files(
            [file1, file2], ModelId("test-model"), mock_client
        )

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
            "edify.token_cache.platformdirs.user_cache_dir",
            return_value=str(tmp_path),
        )

        cache = get_default_cache()

        # Verify database file exists at expected location
        db_path = tmp_path / "token_cache.db"
        assert db_path.exists()
        # Verify cache is usable (can do put/get)
        cache.put("test-md5", "test-model", 42)
        assert cache.get("test-md5", "test-model") == 42

    def test_count_tokens_for_files_fallback_on_cache_init_error(
        self, tmp_path: Path, mocker: MockerFixture, mock_client: Mock
    ) -> None:
        """count_tokens_for_files falls back on any cache init error.

        Given: get_default_cache raises a non-OSError exception (e.g. SQLAlchemy).
        When: Calling count_tokens_for_files.
        Then: Falls back to uncached counting, returns correct results.
        """
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        mocker.patch(
            "edify.token_cache.get_default_cache",
            side_effect=RuntimeError("DB schema mismatch"),
        )
        mock_count = mocker.patch("edify.tokens.count_tokens_for_file", return_value=10)

        results = count_tokens_for_files(
            [test_file], ModelId("test-model"), mock_client
        )

        assert len(results) == 1
        assert results[0].count == 10
        assert mock_count.call_count == 1
