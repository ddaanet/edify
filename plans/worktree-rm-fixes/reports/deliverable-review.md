# Deliverable Review: worktree-rm-fixes

**Date:** 2026-02-20
**Methodology:** agents/decisions/deliverable-review.md (adapted — no design.md, session.md as specification)

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | src/claudeutils/worktree/cli.py | 427 |
| Test | tests/test_worktree_commands.py | 397 |
| Test | tests/test_worktree_new_creation.py | 155 |
| Test | tests/test_worktree_rm.py | 329 |
| Test | tests/test_worktree_rm_dirty.py | 159 |
| Test | tests/test_worktree_submodule.py | 212 |

All 36 tests pass (0 failures). Lint clean.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**M1 — Stale sandbox entry on partial new() failure**
`new()` cleanup (lines 230-238) removes directory and empty container on failure but does not clean up sandbox entries written by `add_sandbox_dir()` inside `_setup_worktree`. Harmless — stale entries in `settings.local.json` reference non-existent directories and have no operational effect.

**M2 — cli.py at 427 lines (soft limit 400)**
Was 398 on main, now 427 (+29 lines). The three fixes added `_delete_submodule_branch` (17 lines), cleanup try-except in `new()` (8 lines), and expanded dirty check in `rm()` — net growth crosses the soft limit. Candidate for extraction (`_delete_submodule_branch` + `_delete_branch` could move to utils).

## Gap Analysis

| Requirement | Status | Reference |
|-------------|--------|-----------|
| Bug 1: Dirty check targets worktree not parent | Covered | rm() lines 381-393, _update_session_and_amend() lines 344-352 |
| Bug 2: new() cleanup on git failure | Covered | new() lines 230-238 |
| Bug 3: rm --confirm submodule branch cleanup | Covered | _delete_submodule_branch() lines 310-324, called line 423 |
| Bug 1 tests: block on dirty worktree | Covered | test_rm_blocks_on_dirty_worktree, test_rm_allows_removal_with_dirty_parent, test_rm_command_blocks_dirty_worktree, test_rm_force_bypasses_dirty_check |
| Bug 2 tests: cleanup on failure | Covered | test_new_cleans_up_on_git_failure |
| Bug 3 tests: submodule branch deletion | Covered | test_rm_deletes_submodule_branch |
| Obsolete test removal | Covered | test_rm_dirty_warning removed |

## Summary

- Critical: 0
- Major: 0
- Minor: 2

All three bugs are correctly fixed with matching test coverage. Code follows existing codebase patterns (error signaling, exit codes, subprocess usage). No behavioral gaps or correctness issues found. Ready to merge.
