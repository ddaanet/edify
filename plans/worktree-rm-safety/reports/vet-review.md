# Vet Review: Worktree RM Safety Gate

**Scope**: Safety gate implementation — dirty checks, --confirm/--force flags, exit code semantics, SKILL.md Mode C, tests
**Date**: 2026-02-17T00:00:00
**Mode**: review + fix

## Summary

The implementation satisfies all 5 FRs. `--confirm` gates direct invocation (exit 2 without it), `--force` bypasses all checks, dirty checks on parent and submodule exit 2 before other operations, guard refusal exits 2, and branch deletion failure exits 1. All 25 tests pass. Two minor docstring issues found and fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Trivial docstrings in `_is_branch_merged` and `_is_submodule_dirty` restate signatures**
   - Location: `src/claudeutils/worktree/utils.py:41-58`, `src/claudeutils/worktree/utils.py:82-90`
   - Note: `_is_branch_merged` had a multi-paragraph docstring with Args/Returns blocks restating what the signature expresses. `_is_submodule_dirty` had a two-sentence docstring that restates "returns False if absent or clean, True if dirty." Neither adds information beyond the signature.
   - **Status**: FIXED — collapsed both to single-line summaries covering non-obvious behavior

2. **Blank line after `derive_slug` function creates visual gap**
   - Location: `src/claudeutils/worktree/cli.py:46-47`
   - Note: Extra blank line between `derive_slug` and `add_sandbox_dir` (two blank lines total where PEP 8 requires two between top-level defs). Cosmetic; linter may flag.
   - **Status**: FIXED — removed the extra blank line

## Fixes Applied

- `src/claudeutils/worktree/utils.py:41` — collapsed `_is_branch_merged` docstring to single-line summary with non-obvious implementation detail (merge-base --is-ancestor)
- `src/claudeutils/worktree/utils.py:82` — collapsed `_is_submodule_dirty` docstring to single-line summary
- `src/claudeutils/worktree/cli.py:46` — removed extra blank line between `derive_slug` and `add_sandbox_dir`

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: exit 2 if parent/submodule dirty (before other ops) | Satisfied | `cli.py:359-372` — dirty checks precede `_guard_branch_removal`, `_probe_registrations`, `_warn_if_dirty`, `_update_session_and_amend` |
| FR-2: guard refusal exits 2 | Satisfied | `cli.py:289` — `raise SystemExit(2)` in `_guard_branch_removal` |
| FR-3: `--force` bypasses confirm, dirty, guard | Satisfied | `cli.py:354-377` — `if not force:` wraps all three check blocks |
| FR-4: `--confirm` required; without it exits 2 with skill message | Satisfied | `cli.py:305-312` — `_check_confirm` exits 2 with message referencing skill |
| Exit semantics: 0=success, 2=safety gate, 1=operational error | Satisfied | Guard: `SystemExit(2)`; branch deletion failure: `SystemExit(1)`; success: 0 |

---

## Positive Observations

- `--force` uses a single `if not force:` block to wrap all three check groups — clean, no logic duplication
- Dirty checks run before `_warn_if_dirty` and `_update_session_and_amend`, so FR-1 ordering is correct
- `test_rm_guard_prevents_destruction` explicitly verifies that session.md task, worktree dir, branch, AND registration all survive guard refusal — thorough regression guard
- `test_rm_amends_merge_commit_when_session_modified` creates `test-feature` as the *merged parent* of the merge commit, matching the real workflow; this was a non-trivial test scenario to get right
- `_check_confirm` message mentions both the skill (`wt merge`) and `--confirm`, giving the user both the safe path and the direct invocation path
- SKILL.md Mode C exit code handling is precise: exit 2 for safety gate, exit 1 for operational error, with explicit "do NOT retry with force" guidance
