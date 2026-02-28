# Cycle 2.1

**Plan**: `plans/userpromptsubmit-topic/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Adds caching layer to `topic_matcher.py` so repeated prompts don't re-parse memory-index.md. Cache stored in project-local `tmp/` per D-4.

---

---

## Cycle 2.1: Cache build and store

**Prerequisite:** Read `agent-core/hooks/userpromptsubmit-shortcuts.py` lines 393-478 — understand existing continuation registry cache pattern (hash generation, mtime validation, silent failure)

**RED Phase:**

**Test:** `test_cache_stores_index_to_project_tmp`
**Assertions:**
- Given a valid memory-index file in tmp_path, and project_dir = tmp_path (with `tmp/` subdir created)
- `get_or_build_index(index_path, project_dir)` returns `(entries, inverted_index)` tuple
- Assert `entries` is list of IndexEntry with len > 0
- Assert `inverted_index` is dict with string keys
- Assert exactly one file matching `tmp/topic-index-*.json` exists in project_dir
- Assert that file loads as valid JSON
- Assert JSON contains "entries" key (list) and "inverted_index" key (dict) and "timestamp" key (float)

**Expected failure:** `AttributeError` — `get_or_build_index` does not exist

**Why it fails:** Caching layer not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_cache_stores_index_to_project_tmp -v`

**GREEN Phase:**

**Implementation:** Add `get_or_build_index()` with cache-write logic to topic_matcher.py.

**Behavior:**
- Generate cache path: `project_dir / "tmp" / f"topic-index-{hash}.json"` where hash = SHA256 of `str(index_path) + str(project_dir)`
- On cache miss: call `parse_memory_index(index_path)` → `build_inverted_index(entries)` → serialize to JSON → write cache file
- Create `tmp/` subdir if needed (`mkdir(parents=True, exist_ok=True)`)
- Silent failure on cache write error (degrade gracefully)
- Serialization: IndexEntry needs JSON-compatible form (convert sets to sorted lists for JSON, reconstruct on load)

**Approach:** Follow continuation registry pattern. Hash via hashlib.sha256.

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add `get_or_build_index(index_path: Path, project_dir: Path) -> tuple[list[IndexEntry], dict[str, list[IndexEntry]]]` with cache helper functions
  Location hint: After `format_output()`, before entry point

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_cache_stores_index_to_project_tmp -v`
**Verify no regression:** `just test`

---
