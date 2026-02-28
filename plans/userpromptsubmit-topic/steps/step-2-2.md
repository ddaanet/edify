# Cycle 2.2

**Plan**: `plans/userpromptsubmit-topic/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Adds caching layer to `topic_matcher.py` so repeated prompts don't re-parse memory-index.md. Cache stored in project-local `tmp/` per D-4.

---

---

## Cycle 2.2: Cache hit and invalidation

**RED Phase:**

**Test:** `test_cache_behavior` (parametrized)

**Case 1 — cache hit avoids reparsing:**
**Assertions:**
- Call `get_or_build_index(index_path, project_dir)` twice with same inputs
- Monkeypatch `parse_memory_index` in topic_matcher module to track call count
- Assert `parse_memory_index` called exactly once (second call uses cache)

**Case 2 — cache invalidation on mtime change:**
**Assertions:**
- Call `get_or_build_index(index_path, project_dir)` once (builds cache)
- Modify source file: append a newline to index_path (changes mtime)
- Call `get_or_build_index(index_path, project_dir)` again
- Monkeypatch `parse_memory_index` call count across both builds
- Assert `parse_memory_index` called twice total (cache invalidated, rebuilt)

**Expected failure:** Cache hit test may pass trivially if GREEN implementation doesn't load from cache yet, or fail on monkeypatch setup

**Why it fails:** Cache read + mtime validation not yet implemented

**Verify RED:** `pytest tests/test_recall_topic_matcher.py::test_cache_behavior -v`

**GREEN Phase:**

**Implementation:** Add cache-read and mtime-validation logic to `get_or_build_index()`.

**Behavior:**
- On cache file exists: load JSON, check if source file mtime > cache timestamp
- If source newer: invalidate (delete cache), rebuild
- If source same or older: reconstruct entries + inverted_index from cached JSON
- Reconstruct IndexEntry objects from JSON (convert sorted lists back to sets for keywords)

**Approach:** `os.path.getmtime()` for mtime comparison. JSON round-trip with set↔list conversion.

**Changes:**
- File: `src/claudeutils/recall/topic_matcher.py`
  Action: Add cache-read path to `get_or_build_index()` — load JSON, validate mtime, reconstruct or invalidate
  Location hint: Beginning of `get_or_build_index()`, before cache-miss path

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_recall_topic_matcher.py::test_cache_behavior -v`
**Verify no regression:** `just test`

---

**Light checkpoint** after Phase 2: `just dev` + verify cache file creation in `tmp/`.

---
