# Deliverable Review: Worktree Merge Data Loss — Source Code

**Artifact:** cli.py, merge.py, utils.py (worktree-merge-data-loss implementation)
**Date:** 2026-02-16
**Mode:** research/review (read-only)

## Summary

The implementation correctly addresses the core data loss bug across both tracks. Track 1 (removal guard) prevents `rm` from destroying unmerged branches. Track 2 (MERGE_HEAD checkpoint + ancestry validation) prevents single-parent commits when a merge is expected. All 9 functional requirements (FR-1 through FR-9) are covered. Test coverage is thorough with real git repos.

Three issues identified: one major (design deviation in error handling), two minor (style inconsistency, code placement).

## Findings

### Major

**1. `_delete_branch` swallows unexpected failure instead of exit 2**
- File: `cli.py:351-352`
- Axis: Conformance, Error signaling
- Design spec (D-2, FR-4): "Merged: `git branch -d` (should succeed; exit 2 if unexpectedly fails)". Exit codes defined as 0 (removed), 1 (refused), 2 (error).
- Implementation: On `-d` failure, emits error to stderr but does not exit with code 2. The `rm` command continues to print a success message and exits 0.
- Impact: If `-d` fails unexpectedly (e.g., branch ref corruption), the CLI reports success. Downstream consumers (skill Mode C) assume clean removal.
- Fix: Add `raise SystemExit(2)` after the error message in `_delete_branch`, or return a failure indicator so `rm` can exit 2.

### Minor

**2. `sys.stderr.write` vs `click.echo(..., err=True)` inconsistency in merge.py**
- File: `merge.py:273, 288, 316-317, 323`
- Axis: Modularity
- All new code in `_validate_merge_result` and the MERGE_HEAD checkpoint uses `sys.stderr.write()`. All existing merge.py code uses `click.echo(..., err=True)` (9 call sites). cli.py also uses `click.echo(..., err=True)` exclusively.
- Impact: Functional equivalence, but breaks established convention. `click.echo` handles encoding edge cases and integrates with Click's testing infrastructure.

**3. `_classify_branch` placed in utils.py instead of cli.py**
- File: `utils.py:61-83`
- Axis: Conformance, Modularity
- Design spec: "`_classify_branch(slug)` in `cli.py` (rm-specific)". Only cli.py imports it (confirmed via grep). `_is_branch_merged` correctly in utils.py per D-7 (shared).
- Impact: Negligible. utils.py is the right place if the function were shared, but it's rm-specific. Placing it in cli.py would better communicate scope.

### Observations (not issues)

**4. Unreachable comment after raise**
- File: `merge.py:325`
- Axis: Vacuity
- Comment `# Branch is merged, nothing to commit -- skip commit, continue to validation` sits after `raise SystemExit(2)` on line 324. The comment documents the implicit else-branch behavior (when `_is_branch_merged` returns True, the elif block isn't entered and execution falls through to `_validate_merge_result`). Misleading placement but the logic is correct.

**5. `_is_branch_merged` docstring restates code**
- File: `utils.py:42-52`
- Axis: Vacuity (deslop)
- 10-line docstring with Args/Returns sections for a 5-line function whose name, signature, and return type annotation fully communicate intent. Per project deslop rules: "Write docstrings only when they explain non-obvious behavior."

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: rm classifies branch | Satisfied | `_guard_branch_removal` calls `_is_branch_merged` then `_classify_branch` (cli.py:322-325) |
| FR-2: rm refuses unmerged real history | Satisfied | Guard raises `click.Abort` (cli.py:339), test `test_rm_refuses_unmerged_real_history` |
| FR-3: rm allows focused-session-only | Satisfied | Guard returns `"focused"` for count==1 + marker match (cli.py:326-327), test `test_rm_allows_focused_session_only` |
| FR-4: rm exit codes 0/1/2 | Partial | 0 and 1 correct. Exit 2 on error not implemented in `_delete_branch` (Finding #1) |
| FR-5: No destructive commands in output | Satisfied | No `git branch -D` suggestions anywhere. Test `test_rm_no_destructive_suggestions` covers all scenarios |
| FR-6: Phase 4 refuses single-parent when unmerged | Satisfied | MERGE_HEAD checkpoint (merge.py:314-319), test `test_phase4_refuses_single_parent_when_unmerged` |
| FR-7: Post-merge ancestry validation | Satisfied | `_validate_merge_result` (merge.py:262-288), tests `test_validate_merge_valid/invalid` |
| FR-8: rm reports removal type | Satisfied | Success messages differentiate merged vs focused (cli.py:389-394) |
| FR-9: Skill Mode C handles exit 1 | N/A | Skill update is Track 3 (prose), not in source review scope |

## Design Decision Conformance

| Decision | Status | Notes |
|----------|--------|-------|
| D-1: Focused session marker text | Conforms | Exact match `f"Focused session for {slug}"` (utils.py:81) |
| D-2: Exit codes 0/1/2 | Partial | Missing exit 2 on `-d` failure (Finding #1) |
| D-3: No destructive instructions | Conforms | No `git branch -D` in any output path |
| D-4: MERGE_HEAD checkpoint | Conforms | Three-way branch in Phase 4 (merge.py:312-325) |
| D-5: Post-merge ancestry validation | Conforms | `_validate_merge_result` with diagnostic parent count (merge.py:262-288) |
| D-6: Guard before destruction | Conforms | `_guard_branch_removal` is first call in `rm` (cli.py:359) |
| D-7: `_is_branch_merged` in utils.py | Conforms | Shared by cli.py and merge.py |

## Test Coverage Assessment

Tests use real git repos (tmp_path + `init_repo`/`make_repo_with_branch` fixtures). No mocked subprocess for git operations. Coverage is thorough:

**Track 1 (rm guard):**
- `test_is_branch_merged` — merged vs unmerged detection
- `test_classify_branch` — 4 branch types (focused, real-history single, multi-commit, wrong format)
- `test_classify_orphan_branch` — orphan branch returns (0, False)
- `test_rm_refuses_unmerged_real_history` — exit 1, message, directory/branch preserved (2 scenarios: real history + orphan)
- `test_rm_allows_merged_branch` — exit 0, branch deleted, success message
- `test_rm_allows_focused_session_only` — exit 0, branch deleted, "(focused session only)" message
- `test_rm_guard_prevents_destruction` — regression: all destructive ops prevented (directory, branch, session.md, worktree registration)
- `test_rm_no_destructive_suggestions` — 3 scenarios, no `git branch -D` in output

**Track 2 (merge correctness):**
- `test_phase4_refuses_single_parent_when_unmerged` — MERGE_HEAD deleted, staged changes present, unmerged branch -> exit 2
- `test_phase4_allows_already_merged` — idempotent: staged changes + already-merged -> exit 0, commit created
- `test_phase4_no_merge_head_unmerged_exits` — no MERGE_HEAD, no staged, not merged -> exit 2
- `test_phase4_no_merge_head_merged_skips` — no MERGE_HEAD, no staged, already merged -> exit 0, no commit
- `test_validate_merge_valid/invalid` — ancestry validation pass/fail
- `test_validate_merge_single_parent_warning` — diagnostic warning for single-parent
- `test_merge_preserves_parent_repo_files` — full integration: worktree changes merged, 2-parent commit, ancestry verified

**Gap:** No test for `_delete_branch` failure path (connected to Finding #1).

## Positive Observations

- Guard-before-destruction pattern (D-6) is cleanly implemented — `_guard_branch_removal` is the first call in `rm`, raising before any side effects
- `_classify_branch` orphan handling via `CalledProcessError` catch is robust — no merge-base means no common ancestor
- Phase 4 three-way branch covers all MERGE_HEAD/staged/merged combinations with correct exit codes
- `_validate_merge_result` includes diagnostic parent count warning — aids future debugging without blocking
- Test for guard preventing ALL destructive operations (`test_rm_guard_prevents_destruction`) is a strong regression test — checks directory, branch, session.md, and worktree registration
- `test_rm_no_destructive_suggestions` across 3 scenarios directly validates the learning that motivated this work (agents following destructive CLI output)
