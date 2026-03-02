"""Tests for topic matcher index caching: build, store, hit, and invalidation."""

import json
import os
import time
from pathlib import Path

import pytest

from claudeutils.recall.index_parser import IndexEntry, parse_memory_index
from claudeutils.recall.topic_matcher import get_or_build_index

MEMORY_INDEX_CONTENT = (
    "# Memory Index\n\n"
    "## agents/decisions/operational-practices.md\n\n"
    "evaluating recall system effectiveness — 4.1% voluntary activation\n"
)


def test_missing_index_returns_empty(tmp_path: Path) -> None:
    """get_or_build_index returns empty results for nonexistent index_path."""
    nonexistent = tmp_path / "missing-memory-index.md"

    entries, inverted_index = get_or_build_index(nonexistent, tmp_path)

    assert entries == []
    assert inverted_index == {}

    # No cache file should be created
    cache_files = list(tmp_path.glob("tmp/topic-index-*.json"))
    assert len(cache_files) == 0


def test_cache_stores_index_to_project_tmp(tmp_path: Path) -> None:
    """get_or_build_index should build and cache index to project tmp."""
    memory_index = tmp_path / "memory-index.md"
    memory_index.write_text(MEMORY_INDEX_CONTENT)

    entries, inverted_index = get_or_build_index(memory_index, tmp_path)

    assert isinstance(entries, list)
    assert len(entries) > 0
    assert all(isinstance(entry, IndexEntry) for entry in entries)
    assert isinstance(inverted_index, dict)
    assert all(isinstance(k, str) for k in inverted_index)

    cache_files = list(tmp_path.glob("tmp/topic-index-*.json"))
    assert len(cache_files) == 1

    cache_data = json.loads(cache_files[0].read_text())
    assert "entries" in cache_data
    assert "inverted_index" in cache_data
    assert "timestamp" in cache_data
    assert isinstance(cache_data["entries"], list)
    assert isinstance(cache_data["inverted_index"], dict)
    assert isinstance(cache_data["timestamp"], (int, float))


@pytest.fixture
def cache_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, list[int]]:
    """Memory-index file + monkeypatched parse with call counter."""
    memory_index = tmp_path / "memory-index.md"
    memory_index.write_text(MEMORY_INDEX_CONTENT)
    parse_call_count: list[int] = [0]

    def mock_parse(path: Path) -> list[IndexEntry]:
        parse_call_count[0] += 1
        return parse_memory_index(path)

    monkeypatch.setattr(
        "claudeutils.recall.topic_matcher.parse_memory_index", mock_parse
    )
    return memory_index, parse_call_count


def test_cache_hit_avoids_reparsing(
    tmp_path: Path, cache_env: tuple[Path, list[int]]
) -> None:
    """Second call with unchanged source should read from cache, not reparse."""
    memory_index, parse_call_count = cache_env

    get_or_build_index(memory_index, tmp_path)
    assert parse_call_count[0] == 1

    get_or_build_index(memory_index, tmp_path)
    assert parse_call_count[0] == 1


def test_cache_invalidation_triggers_rebuild(
    tmp_path: Path, cache_env: tuple[Path, list[int]]
) -> None:
    """Source file newer than cache should trigger rebuild."""
    memory_index, parse_call_count = cache_env

    get_or_build_index(memory_index, tmp_path)
    assert parse_call_count[0] == 1

    time.sleep(0.01)
    memory_index.write_text(
        MEMORY_INDEX_CONTENT
        + "memory index amplifies thin user input — keyword matching\n"
    )
    os.utime(memory_index, None)

    get_or_build_index(memory_index, tmp_path)
    assert parse_call_count[0] == 2
