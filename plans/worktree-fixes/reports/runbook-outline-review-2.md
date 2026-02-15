# Runbook Outline Review — worktree-fixes (Round 2)

**Reviewed:** `plans/worktree-fixes/runbook-outline.md`
**Against:** `plans/worktree-fixes/design.md`, `plans/worktree-fixes/requirements.md`, codebase
**Date:** 2026-02-14

---

## Overall Assessment: READY (with minor fixes applied below)

Requirements coverage is complete (all 5 FRs mapped). Phase structure matches design. Cycle granularity is appropriate. Expansion guidance is detailed and actionable.

---

## Issues Found

### Minor Issues

**M-1: Outline references non-existent test — FIXED**

Line 200 references `test_worktree_merge_conflicts.py::test_conflicting_pending_tasks` but no such test exists. The actual test is `test_merge_conflict_session_md`.

**M-2: Duplicate expansion guidance sections — FIXED**

Lines 122-163 and 183-202 both contain "Expansion Guidance" content. The second section (from outline review) repeats/overlaps with the first. These should be consolidated into a single section.

**M-3: TASK_PATTERN regex discrepancy between validation and design — INFO**

`validation/tasks.py` uses `^- \[[ x>]\] \*\*(.+?)\*\* —` (requires em dash after name). Design's `extract_task_blocks()` uses `^- \[[ x>]\] \*\*(.+?)\*\*` (no em dash required). This is correct — Worktree Tasks entries have `→ \`slug\`` after the name, not an em dash. The outline should note this difference in Phase 1 expansion so the implementer uses the right pattern. Added a note.

**M-4: Phase 1 cycles 1.4-1.6 overlap — FIXED**

Cycles 1.4 (`_resolve_session_md_conflict uses extract_task_blocks`), 1.5 (`preserves continuation lines`), and 1.6 (`inserts with find_section_bounds`) describe what is effectively one behavioral change to `_resolve_session_md_conflict()`. The current merge logic is ~40 lines. Splitting the fix into 3 cycles risks vacuous GREEN phases where the intermediate states aren't meaningful. Consolidated 1.4-1.6 into two cycles: one for block-based comparison + preservation, one for insertion point using `find_section_bounds()`.

**M-5: Phase 1 cycles 1.10-1.11 can consolidate — FIXED**

`focus_session()` is 19 lines. Two separate cycles for "uses extract_task_blocks" and "preserves continuation lines" are artificially split — the only reason to use `extract_task_blocks()` IS to preserve continuation lines. Consolidated into one cycle.

---

## Recommendations (for expansion phase)

**R-1: Phase 1 Cycle 1.1 — test file placement**

New `session.py` tests should go in a new `tests/test_worktree_session.py` file (per design). The outline mentions this in the design testing strategy but should be explicit in cycle 1.1 expansion.

**R-2: Phase 1 merge test — use existing test structure**

`test_merge_conflict_session_md` in `test_worktree_merge_conflicts.py` provides the E2E pattern: creates repo, branches, diverges session.md, merges. New merge tests should follow this exact fixture pattern (`repo_with_submodule`, `commit_file`, `mock_precommit`).

**R-3: Phase 2 `rm` reorder — verify current operation sequence**

The `rm` command's current operation order should be verified during expansion. Design says reorder to: check → edit session.md → delete branch → cleanup. The implementer should read `cli.py`'s `rm` command to confirm current order before writing tests.

**R-4: `_resolve_session_md_conflict` insertion — blank line before next section**

Design specifies "blank line separation before next section header." The current code inserts `["", *sorted(new_tasks)]` at the next section boundary. The fix must ensure multi-line blocks maintain proper blank-line separation. Expansion should include a test case with tasks that have continuation lines immediately before a `## ` header.

---

## Fixes Applied

All minor issues fixed in outline below. No critical or major issues found.
