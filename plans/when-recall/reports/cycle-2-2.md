# Cycle 2.2: Compute ancestor headings (H4→H3→H2→file)

**Timestamp:** 2026-02-12

**Status:** GREEN_VERIFIED

**Test command:** `pytest tests/test_when_navigation.py::test_compute_ancestors -v`

**RED result:** FAIL as expected (ImportError: cannot import name 'compute_ancestors')

**GREEN result:** PASS

**Regression check:** 772/773 passed, 1 xfail (no new failures)

**Refactoring:** Lint with formatter (import order reordering in test file), precommit validation passed

**Files modified:**
- `src/claudeutils/when/navigation.py` — added `compute_ancestors(heading, file_path, file_content)` function
- `tests/test_when_navigation.py` — added `test_compute_ancestors()` test with three cases (H3 under H2, H4 under H3 under H2, H2 top-level)

**Stop condition:** None

**Decision made:** Function collects ancestor chain by walking up from target heading using parent references from hierarchy, then reverses to return top-down order (root to immediate parent), with file link appended as final ancestor.
