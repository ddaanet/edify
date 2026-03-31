# Deliverable Review: worktree-merge-resilience

**Date:** 2026-02-23
**Methodology:** `agents/decisions/deliverable-review.md`
**Design reference:** `plans/worktree-merge-resilience/outline.md`

---

## Inventory

| Type | File | +lines | -lines |
|------|------|--------|--------|
| Code | `src/edify/validation/learnings.py` | +55 | -2 |
| Code | `src/edify/worktree/merge.py` | +3 | -0 |
| Code | `src/edify/worktree/resolve.py` | +241 | -10 |
| Test | `tests/test_learnings_diff3.py` | +322 | -0 |
| Test | `tests/test_validation_learnings.py` | +158 | -7 |
| Test | `tests/test_worktree_merge_learnings.py` | +153 | -0 |

**Summary:** 3 code files (+299/-12), 3 test files (+633/-7). Total: +932/-19 net. No prose or configuration deliverables.

**Design conformance:** All 6 functional/non-functional requirements satisfied. Resolution matrix correctly implements all 14 enumerable rows. Both observed failure scenarios (diagnostic c330b7d2, brief 6086650e) covered by integration tests. Pipeline integration covers all 5 state machine paths through phase 4.

---

## Critical Findings

None.

---

## Major Findings

None.

---

## Minor Findings

### M1. Integration tests in new file instead of extending existing

- **File:** `tests/test_worktree_merge_learnings.py`
- **Axis:** Conformance
- **Detail:** Outline specifies "Extend `tests/test_worktree_merge_conflicts.py`." Implementation created a separate file. Practically an improvement (learnings-specific tests have clearer ownership), but deviates from the spec.

### M2. `_write_commit` helper in integration test duplicates fixture pattern

- **File:** `tests/test_worktree_merge_learnings.py:21-25`
- **Axis:** Excess
- **Detail:** Local `_write_commit` function adds `mkdir(parents=True)` before writing — needed because `agents/` directory may not exist. The `commit_file` fixture from `fixtures_worktree.py` lacks directory creation, so the local helper is justified. However, the test uses both: `commit_file` for gitignore (line 44) and `_write_commit` for learnings commits. Inconsistent — either extend `commit_file` or use `_write_commit` throughout.

### M3. Preamble key uses `""` vs outline's `None`

- **File:** `src/edify/validation/learnings.py:51`, `src/edify/worktree/resolve.py:169,244,344`
- **Axis:** Conformance
- **Detail:** Outline says "keyed by `None` or sentinel." Implementation uses empty string `""`. Valid choice (outline permits "sentinel"), and empty string is more ergonomic as a dict key than `None`. Consistently applied across all 4 usage sites.

---

## Gap Analysis

| Design Requirement | Status | Evidence |
|---|---|---|
| FR-1: Segment-level diff3 merge | Covered | `diff3_merge_segments()` in resolve.py, `parse_segments()` in learnings.py |
| FR-2: 15-row resolution matrix | Covered | 14 rows in `_resolve_heading`/`_resolve_both_present`/`_resolve_one_sided_deletion`; row 15 structurally impossible. 30 unit tests cover all rows |
| FR-3: All merge paths covered | Covered | Phase 3 conflict path via `resolve_learnings_md`; phase 4 all-paths via `remerge_learnings_md`. All 5 state machine paths pass through phase 4 |
| FR-4: Conflict markers at line granularity | Covered | `_format_conflict_segment` produces `<<<<<<</=======/>>>>>>>` markers; integration test verifies markers in divergent-edit scenario |
| NFR-1: Precommit structural validation | Covered | `_detect_orphaned_content` added to `validate()` |
| NFR-2: No false positives on clean file | Covered | `test_clean_learnings_file_no_orphan_errors` validates real file structure produces zero errors |
| Segment parser reuse | Covered | `parse_segments` in validation/learnings.py used by both resolver and test assertions; orphan detection uses lighter scan (same heading pattern, doesn't need full parse) |
| Every merge, not just conflicts | Covered | `remerge_learnings_md()` at top of `_phase4_merge_commit_and_precommit` — runs on all paths |
| Block, not warn | Covered | `remerge_learnings_md` raises SystemExit(3) on conflict; `_detect_orphaned_content` feeds into `validate()` error list |

No missing deliverables. No unspecified deliverables.

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 3 |

All 6 design requirements fully satisfied. The diff3 resolution matrix is correct for all 14 enumerable rows, tested at both unit and integration levels. Pipeline integration covers all 5 state machine paths. The prior corrector review (tier2-review.md) addressed 1 major and 3 minor issues — all verified fixed in the current codebase.

The 3 minor findings are: one spec deviation (new test file vs extending existing — arguably better), one test helper inconsistency, and one notation choice (empty string vs None for preamble key — outline-permitted).
