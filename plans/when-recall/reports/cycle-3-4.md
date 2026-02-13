### Cycle 3.4: File mode — relative path resolution

**Timestamp:** 2026-02-13 20:45 UTC

**Status:** GREEN_VERIFIED

**Test command:** `pytest tests/test_when_resolver.py::test_file_mode_resolves -v`

**RED result:** FAIL as expected — AssertionError (file mode returned "file" string instead of content)

**GREEN result:** PASS — test_file_mode_resolves passes with implementation

**Regression check:** 765/781 passed, 16 skipped (no new failures)

**Refactoring:**
- Fixed import placement (moved ResolveError import to top-level)
- No other refactoring needed

**Files modified:**
- `src/claudeutils/when/resolver.py` — Added `_resolve_file()` function, updated `resolve()` to call it
- `tests/test_when_resolver.py` — Added `test_file_mode_resolves()`, fixed `test_mode_detection()` to check file content instead of "file" string

**Stop condition:** none

**Decision made:** none
