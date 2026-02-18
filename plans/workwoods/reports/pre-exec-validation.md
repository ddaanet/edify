# Pre-Execution Validation Report

**Runbook:** workwoods (6 phases, 33 TDD cycles + 10 general steps)
**Date:** 2026-02-16
**Checks:** FR-3 (file lifecycle), FR-4 (RED plausibility), FR-5 (test count reconciliation)

## FR-3: File Lifecycle Validation — PASS

No violations found. All files follow correct create→modify ordering:

**New files created before modification:**
- `src/claudeutils/planstate/__init__.py` — created 1.1, modified 1.5
- `src/claudeutils/planstate/models.py` — created 1.1, modified 1.4, 2.1, 2.4, 3.2
- `src/claudeutils/planstate/inference.py` — created 1.1, modified 1.2-1.5
- `src/claudeutils/planstate/vet.py` — created 2.1, modified 2.2-2.5
- `src/claudeutils/planstate/aggregation.py` — created 3.1, modified 3.2-3.7
- `src/claudeutils/validation/planstate.py` — created 6.1, modified 6.2-6.3
- `agents/plan-archive.md` — created 6.5
- Test files follow same pattern (created in first cycle, modified in subsequent)

**Existing files verified on disk:**
- `src/claudeutils/worktree/cli.py` ✅ (Phase 4)
- `src/claudeutils/worktree/merge.py` ✅ (Phase 5)
- `src/claudeutils/worktree/session.py` ✅ (Phase 5)
- `src/claudeutils/validation/cli.py` ✅ (Phase 6)
- `src/claudeutils/validation/jobs.py` ✅ (Phase 6 deletes it)
- `src/claudeutils/planstate/` — correctly absent (Phase 1 creates)

**Dependency ordering (holistic fix verified):**
- Step 6.9 removes jobs validator code → Step 6.10 deletes jobs.md ✅

## FR-4: RED Plausibility Audit — 3 ISSUES

### Issue 1: Cycle 1.4 — Wrong expected failure message (minor)

**Expected:** `AttributeError: 'PlanState' object has no attribute 'gate'`
**Actual:** PlanState dataclass is defined with `gate` field in Cycle 1.1 GREEN (`models.py`: "Define PlanState dataclass (name, status, next_action, gate, artifacts fields)"). By 1.4, `gate` exists as a field with default value (likely `None`).
**Real failure:** `AssertionError` — gate value is `None` instead of the stale message string.
**Impact:** Test still fails RED. Misleading expected failure description but execution unaffected.
**Action:** Fix expected failure text in runbook phase file.

### Issue 2: Cycle 1.5 — Wrong expected failure message (minor)

**Expected:** `NameError: name 'list_plans' is not defined`
**Actual:** `list_plans` is created in Cycle 1.1 GREEN:
- `__init__.py`: "Create module with public API exports (infer_state, list_plans)"
- Test 1.1 asserts: `list_plans(tmp_path / "plans")` returns `[]`

The function exists (at minimum as a stub returning `[]`). Cycle 1.5's test with multiple plan directories would get an assertion failure, not NameError.
**Real failure:** `AssertionError: assert 0 == 2` (stub returns empty list for populated directory).
**Impact:** Test still fails RED. Misleading expected failure description but execution unaffected.
**Action:** Fix expected failure text in runbook phase file.

### Issue 3: Cycle 3.6 — Missing aggregate_trees() precondition (moderate)

**Expected failure:** `AggregatedStatus.plans contains only main tree plans, or contains duplicate plan-c entries`
**Problem:** No prior cycle (3.1-3.5) creates `aggregate_trees()`. Cycles 3.1-3.5 only create private helpers:
- 3.1: `_parse_worktree_list()`
- 3.2: is_main/slug fields
- 3.3: `_commits_since_handoff()`, `_latest_commit()`
- 3.4: `_is_dirty()`
- 3.5: `_task_summary()`

**Real failure:** `ImportError` or `NameError` — `aggregate_trees` function doesn't exist.
**Impact:** Test still fails RED, but execution agent may be confused about when to create the public function. The 3.6 GREEN says "Add plan discovery loop in aggregate_trees()" (implies modification, not creation).
**Action:** Either:
- (a) Add aggregate_trees() stub creation to an earlier cycle (e.g., 3.5 GREEN creates the shell function), or
- (b) Fix 3.6 GREEN to say "Create aggregate_trees() with plan discovery" and fix expected failure to ImportError

### Acknowledged non-issues

**Cycles 5.1, 5.4:** RED may already pass. Explicitly documented in runbook: "Expected failure: Test passes (find_section_bounds already exists) OR new test reveals edge cases." Handled gracefully with "Test-only cycle if function works."

## FR-5: Test Count Reconciliation — PASS

All checkpoint test counts match:

| Phase | Checkpoint claim | Test functions | Match |
|-------|-----------------|----------------|-------|
| P1 | "All tests pass" (no count) | 5 functions | ✅ |
| P2 | "All 5 tests pass" | 5 functions | ✅ |
| P3 | "All 7 tests pass" | 7 functions | ✅ |
| P4 | "All 4 tests pass" | 4 functions | ✅ |
| P5a | "4 tests pass" | 4 functions | ✅ |
| P5mid | "All 8 tests pass" | 8 functions | ✅ |
| P6 | "All 4 tests pass" | 4 functions | ✅ |

Note: Parametrized tests (1.2, 5.5) count as 1 function regardless of parameter count. This matches pytest `--tb=short` function-level counting.

## Summary

| Check | Result | Issues |
|-------|--------|--------|
| FR-3: File lifecycle | PASS | 0 |
| FR-4: RED plausibility | 3 issues | 2 minor (wrong error text), 1 moderate (missing function) |
| FR-5: Test count | PASS | 0 |

**Recommendation:** Fix the 3 RED plausibility issues in phase files before prepare-runbook.py. All are text corrections — no structural changes needed.
