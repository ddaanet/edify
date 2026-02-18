# Deliverable Review: Code Partition

**Scope**: Production code artifacts from worktree-merge-resilience implementation
**Date**: 2026-02-18
**Design reference**: plans/worktree-merge-resilience/outline.md
**Requirements**: plans/worktree-merge-resilience/requirements.md

## Summary

The state-machine merge implementation is well-structured, with clean separation between state detection (merge_state.py) and phase execution (merge.py). All 5 states are correctly detected and routed. D-7 (no data loss) is satisfied: no `git merge --abort` or `git clean -fd` remains in any code path. The `merged` route deviation (Phase 1+2+4 instead of Phase 4 only) is well-justified by the haiku regression fix.

**Overall Assessment**: Needs Minor Changes

---

## merge.py

### Major: `parent_conflicts` route skips auto-resolution of session/learnings/agent-core
**Location:** merge.py:327-333
**Axis:** Functional completeness, Idempotency
**Design ref:** FR-2, FR-5
**Finding:** When the user resolves some conflicts but not all, then re-runs `_worktree merge`, the state machine detects `parent_conflicts` and immediately reports + exits 3. It does NOT attempt auto-resolution of `agents/session.md`, `agents/learnings.md`, or `agent-core` submodule pointer. If those files are among the remaining unresolved conflicts (e.g., user resolved `src/feature.py` but `agents/session.md` is still conflicted), the tool reports them as requiring manual resolution when they could be auto-resolved. The `_phase3_merge_parent` path (lines 225-238) correctly runs `resolve_session_md` and `resolve_learnings_md`, but the `parent_conflicts` resume path bypasses this entirely. A user who resolves source conflicts and re-runs would get stuck on auto-resolvable files.

### Minor: Duplicated conflict-listing pattern
**Location:** merge.py:225-226, merge.py:328-331
**Axis:** Vacuity
**Design ref:** N/A
**Finding:** The pattern `_git("diff", "--name-only", "--diff-filter=U").split("\n")` + filter empty strings appears identically in `_phase3_merge_parent` (line 225-226) and the `parent_conflicts` route (line 328-331). A small helper like `_list_unresolved_conflicts()` would reduce duplication and make the auto-resolution fix above cleaner.

### Minor: `_format_conflict_report` divergence label could be clearer
**Location:** merge.py:53-55
**Axis:** Functional correctness (FR-4)
**Design ref:** FR-4
**Finding:** The divergence line reads `Branch: N commits ahead, Main: M commits ahead since merge-base`. FR-4 requires "commit count since merge-base on each side." The current wording is slightly ambiguous: "Branch: N commits ahead" reads as "branch is N commits ahead of main" (which is `HEAD..slug`), but the label then says "Main: M commits ahead" which would be `slug..HEAD`. The calculations are correct, but the phrasing "Branch: X commits ahead, Main: Y commits ahead" is confusing because both say "ahead" — the reader might expect one to be "behind." Consider: `Divergence: branch has N commits, main has M commits since merge-base`.

---

## merge_state.py

### Minor: No guard for absent agent-core directory in `_detect_merge_state`
**Location:** merge_state.py:26-30
**Axis:** Robustness
**Design ref:** D-5
**Finding:** `git -C agent-core rev-parse --verify MERGE_HEAD` will fail with a non-zero exit code when agent-core doesn't exist, which correctly falls through to the parent MERGE_HEAD check. However, git emits an error to stderr ("cannot change to 'agent-core': No such file or directory") that is captured but ignored. This is functionally correct but the error emission is incidental rather than intentional. Since `check=False` and `capture_output=True` handle it, this is cosmetic only. Could add an early return if `Path("agent-core").exists()` is false, matching the pattern used in `_check_clean_for_merge` (merge.py:89-91).

### Minor: `_parse_untracked_files` handles `is_local_changes_error` but naming suggests untracked only
**Location:** merge_state.py:53-71
**Axis:** Code clarity
**Design ref:** D-4
**Finding:** The function name `_parse_untracked_files` and its docstring say "untracked-file collision" but it also parses the "local changes would be overwritten" error (line 63-64). The caller in merge.py (line 203-208) correctly detects both error types and calls this function for either case. The function handles both correctly but the naming is misleading. Consider `_parse_collision_files` or a docstring update.

---

## cli.py

### Minor: D-8 compliance is partial — cli.py functions outside merge scope retain `err=True`
**Location:** cli.py:76, 136, 229, 235, 289, 299, 308, 361, 368
**Axis:** Conformance
**Design ref:** D-8
**Finding:** D-8 specifies "All output to stdout" and "Single output stream." The merge-specific code paths (`merge.py`, `merge_state.py`) are fully compliant — no `err=True` calls. However, `cli.py` retains 9 `err=True` calls in non-merge functions (`_initialize_environment`, `_create_parent_worktree`, `new`, `_guard_branch_removal`, `_delete_branch`, `_check_confirm`, `rm`). The outline's Phase 5 says "migrate all `click.echo(..., err=True)` to `click.echo()` (stdout)." Session.md says "stderr->stdout migration (D-8)" was done with "2 lines changed" in cli.py. The remaining `err=True` calls are outside the merge pipeline but within the same module referenced by Phase 5. These are in `new`, `rm`, and helper functions — the D-8 intent was to unify the merge pipeline output stream, and these functions are separate commands. Noting for completeness but the merge pipeline itself is clean.

---

## resolve.py (called from merge pipeline)

### Major: Two `err=True` calls in `resolve_session_md` violate D-8 during merge
**Location:** resolve.py:98-101, resolve.py:103-106
**Axis:** Conformance
**Design ref:** D-8
**Finding:** `resolve_session_md` is called from `_phase3_merge_parent` (merge.py:233) during the merge pipeline. It contains two `click.echo(..., err=True)` calls in its error-recovery paths (hash-object fallback at line 98-101, and ours-fallback at line 103-106). These execute during a merge operation and send output to stderr, violating D-8's "single output stream" contract. The outline excludes "Changes to `resolve.py` session/learnings strategies" from scope, but D-8 is a cross-cutting output concern that applies to all code executing during merge. These error paths are rare (triggered only when `git add agents/session.md` fails) but when they fire, the output goes to stderr while all other merge output goes to stdout, which is exactly the inconsistency D-8 aims to eliminate.

---

## Cross-Cutting: NFR-2 (No Data Loss) Audit

All `raise SystemExit` paths audited:

| Location | Exit Code | Preserves WIP? | Notes |
|----------|-----------|----------------|-------|
| merge.py:87 | 1 | Yes | Dirty tree — nothing modified yet |
| merge.py:102 | 1 | Yes | Dirty submodule — nothing modified yet |
| merge.py:115 | 2 | Yes | Branch not found — nothing modified yet |
| merge.py:210 | 1 | Yes | Untracked recovery failed — merge not started |
| merge.py:220 | 1 | Yes | Merge still failed after recovery — merge not started |
| merge.py:223 | 1 | Yes | Non-collision merge failure — MERGE_HEAD absent |
| merge.py:238 | 3 | Yes | Conflicts remain — MERGE_HEAD preserved |
| merge.py:253 | 2 | Yes | Post-commit validation — commit already done |
| merge.py:294 | 2 | Yes | MERGE_HEAD lost — commit already done or no changes |
| merge.py:298 | 2 | Yes | Nothing to commit, branch not merged — diagnostic |
| merge.py:314 | 1 | Yes | Precommit failed — merge commit exists |
| merge.py:333 | 3 | Yes | parent_conflicts resume — MERGE_HEAD preserved |
| merge_state.py:86 | 1 | Yes | git add failed during recovery — original error shown |
| merge_state.py:97 | 1 | Yes | Commit failed during recovery — files added but not committed |
| merge_state.py:136 | 1 | Yes | Retry merge failed, no MERGE_HEAD — recovery commit exists |

**Assessment:** No code path discards staged content or untracked files. NFR-2 satisfied.

Note: merge_state.py:97 exits after `git add` succeeded but `git commit` failed. The added files remain staged — no data loss, but the user may need to manually commit or reset. This is acceptable: the error is surfaced with the stderr from `git commit`.

---

## Cross-Cutting: D-1 Exit Code Audit

| Exit Code | Expected Semantics | Actual Usage | Correct? |
|-----------|-------------------|--------------|----------|
| 0 | Success | Implicit (no SystemExit) | Yes |
| 1 | Error (recoverable) | Dirty tree, merge failure, precommit failure, recovery failure | Yes |
| 2 | Fatal/safety | Branch not found, merge state lost, branch not merged post-commit | Yes |
| 3 | Conflicts need resolution | Remaining conflicts after auto-resolve, parent_conflicts resume | Yes |

All exit codes correctly classified per D-1.

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Proceed through submodule conflicts | Satisfied | merge.py:165-171 — `check=False` on submodule merge, returns on conflict (MERGE_HEAD preserved) |
| FR-2: Leave parent merge in progress | Satisfied | merge.py:236-238 — conflicts reported + exit 3, no abort/clean |
| FR-3: Handle untracked file collisions | Satisfied | merge.py:202-220 + merge_state.py:100-138 — parse, add, retry |
| FR-4: Conflict context in output | Satisfied | merge.py:31-62 — status codes, diff stats, divergence, hint |
| FR-5: Idempotent resume | Partial | State detection correct (merge_state.py:10-50), routing correct for clean/merged/parent_resolved/submodule_conflicts. **Gap:** parent_conflicts route skips auto-resolution (see Major issue above) |
| NFR-1: Backward-compatible exit codes | Satisfied | Exit code 3 added, 0/1/2 semantics unchanged |
| NFR-2: No data loss | Satisfied | Full audit above — no abort/clean, all paths preserve WIP |
| C-1: Skill contract | Satisfied | SKILL.md Mode C updated with exit code 3 handling |
| C-2: Non-interactive resolution | Satisfied | No interactive prompts, conflict markers + hint for Edit+git add workflow |

**Gaps:** FR-5 partially satisfied — `parent_conflicts` resume path does not attempt auto-resolution.

---

## Positive Observations

- State machine detection order (D-5) is correctly implemented and well-documented in the docstring
- Clean module split: merge_state.py handles detection/recovery, merge.py handles phase orchestration
- The `merged` route deviation (Phase 1+2+4) is well-justified by the haiku regression and documented in session.md and checkpoint vet reports
- D-7 compliance is thorough: zero instances of `git merge --abort` or `git clean -fd` in the codebase
- `_recover_untracked_file_collision` correctly handles both untracked-file and local-changes-overwritten errors with a single code path (D-4 design)
- Phase 2 submodule conflict handling correctly leaves MERGE_HEAD in place and returns silently, allowing Phase 3 to proceed (D-2)
- Exit code classification is precise: every SystemExit maps correctly to the D-1 taxonomy

---

## Next Steps

1. Fix `parent_conflicts` auto-resolution gap: before reporting conflicts and exiting 3, run `resolve_session_md` and `resolve_learnings_md` on the conflict list (and `checkout --ours` for agent-core). If all conflicts resolve, route to Phase 4 instead of exiting.
2. Migrate `resolve.py` `err=True` calls to stdout (2 instances, lines 100 and 105).
3. Consider extracting `_list_unresolved_conflicts()` helper to deduplicate the pattern.
