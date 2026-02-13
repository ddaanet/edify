# Cycle 3.4

**Plan**: `plans/when-recall/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.4: File mode — relative path resolution

**RED Phase:**

**Test:** `test_file_mode_resolves`
**Assertions:**
- `resolve("when", "..testing.md", index_path, decisions_dir)` returns full content of `agents/decisions/testing.md`
- `resolve("when", "..nonexistent.md", index_path, decisions_dir)` raises `ResolveError`
- File path is relative to `decisions_dir` (no absolute paths accepted)

**Expected failure:** AssertionError — file mode not implemented

**Why it fails:** File mode resolution not yet in resolver

**Verify RED:** `pytest tests/test_when_resolver.py::test_file_mode_resolves -v`

**GREEN Phase:**

**Implementation:** Implement file mode.

**Behavior:**
- Strip `..` prefix from query to get filename
- Resolve relative to `decisions_dir`
- Read and return full file content
- If file not found: raise `ResolveError` (handled in 3.9)

**Approach:** `(decisions_dir / filename).read_text()` with existence check.

**Changes:**
- File: `src/claudeutils/when/resolver.py`
  Action: Implement file mode — path resolution, file read, error handling
  Location hint: Within `resolve` function, file mode branch

**Verify GREEN:** `pytest tests/test_when_resolver.py::test_file_mode_resolves -v`
**Verify no regression:** `pytest tests/ -q`

---
