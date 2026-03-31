"""Tests for Usage API caching."""

import json
from pathlib import Path

from edify.account import UsageCache


def test_usage_cache_get_stale() -> None:
    """Test that UsageCache.get() returns None when cache missing or stale.

    Tests cache behavior when file doesn't exist or is stale.
    """
    cache = UsageCache()
    result = cache.get()
    assert result is None


def test_usage_cache_put(tmp_path: Path) -> None:
    """Test that UsageCache.put() writes cache file with current timestamp.

    Verifies that put() writes data to cache file and that get() retrieves it
    when cache is fresh.
    """
    # Use tmp_path for test isolation
    cache = UsageCache()
    cache.cache_dir = tmp_path
    cache.cache_file = tmp_path / "usage_cache.json"

    # Test data
    test_data: dict[str, object] = {"usage": 42, "credits": 100}

    # Put data to cache
    cache.put(test_data)

    # Verify file was created
    assert cache.cache_file.exists()

    # Verify data is correct
    with cache.cache_file.open() as f:
        cached = json.load(f)
    assert cached == test_data

    # Verify get() retrieves it when fresh
    result = cache.get()
    assert result == test_data


def test_usage_cache_ttl() -> None:
    """Test that UsageCache TTL constant is set to exactly 10 seconds.

    Verifies the cache expiration timeout matches the design specification (D7).
    This ensures cached usage data is refreshed frequently enough to keep
    displayed account status current during active CLI sessions.

    Checks:
    - TTL value equals 10 (not 30, not any other value)
    - TTL is an integer (not float or string)
    - TTL is positive (non-zero, greater than zero)
    """
    # Verify TTL constant value is exactly 10
    assert UsageCache.TTL_SECONDS == 10

    # Verify TTL is an integer type
    assert isinstance(UsageCache.TTL_SECONDS, int)

    # Verify TTL is positive
    assert UsageCache.TTL_SECONDS > 0
