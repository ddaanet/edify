# Review: Segment-level diff3 merge for learnings.md

**Scope**: 6 changed files — diff3 merge core, pipeline integration, precommit validation, tests
**Date**: 2026-02-23
**Mode**: review + fix

## Summary

Five TDD cycles produced a working segment-level diff3 implementation for `agents/learnings.md`. All 44 tests pass. The resolution matrix is correctly implemented for all 14 enumerable rows. Two integration tests cover both observed scenarios (clean-merge orphan prevention, divergent-edit conflict). The main issues are: redundant `parse_segments` calls in the conflict branch of `remerge_learnings_md`, a missing user-action hint when `remerge_learnings_md` exits 3, a local import inside a test function that should be top-level, and a minor comment in `_resolve_heading` that obscures Row 1 handling.

**Overall Assessment**: Ready (after fixes applied)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Redundant `parse_segments` calls in `remerge_learnings_md` conflict branch**
   - Location: `src/edify/worktree/resolve.py:380-386`
   - Problem: `ours_content` and `theirs_content` are already parsed into `merged_segments, conflicts = diff3_merge_segments(parse_segments(ours_content), parse_segments(theirs_content), ...)` using parsed inputs. But `_segments_to_content_with_conflicts` is called with `parse_segments(ours_content)` and `parse_segments(theirs_content)` — re-parsing strings that were already parsed. The parsed segment dicts are not reused.
   - Fix: Store parsed dicts before calling `diff3_merge_segments`, pass them directly to `_segments_to_content_with_conflicts`.
   - **Status**: FIXED

### Minor Issues

1. **Local import inside test function**
   - Location: `tests/test_worktree_merge_learnings.py:84`
   - Note: `from edify.validation.learnings import parse_segments` is imported inside the test body with a `# noqa: PLC0415` suppression. The suppression flag implies the code knows this is wrong. It should be at the top of the file with the other imports.
   - **Status**: FIXED

2. **Missing user-action hint in `remerge_learnings_md` conflict message**
   - Location: `src/edify/worktree/resolve.py:377-388`
   - Note: When segment conflicts are detected in phase 4, the function emits the conflict headings to stderr and writes markers to the file, then exits 3. There is no instruction telling the user what to do next (manually resolve `agents/learnings.md`, `git add` it, then re-run the merge command). Contrast with `_format_conflict_report` which includes "Resolve conflicts, git add, then re-run: ...".
   - **Status**: FIXED

3. **`_resolve_heading` Row 1 comment is misleading**
   - Location: `src/edify/worktree/resolve.py:285`
   - Note: The comment "Row 1: theirs-only new — catch-all handles it" is attached to the `return None, False` path. The function returns `None` here specifically so the post-loop catch-all in `diff3_merge_segments` can append it. This dual-mechanism is non-obvious. The comment should explain the return value's intent.
   - **Status**: FIXED

## Fixes Applied

- `src/edify/worktree/resolve.py:350-391` — Store `ours_segs`/`theirs_segs` before `diff3_merge_segments` call; pass them directly to `_segments_to_content_with_conflicts` in conflict branch; eliminated two redundant `parse_segments()` calls.
- `src/edify/worktree/resolve.py:377-388` — Added "Resolve `agents/learnings.md` and re-run merge." hint after the conflict count message.
- `src/edify/worktree/resolve.py:285` — Updated comment to explain the `None` return and catch-all mechanism.
- `tests/test_worktree_merge_learnings.py:1-12` — Moved `parse_segments` import to top level; removed `noqa` suppression.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Segment-level diff3 merge | Satisfied | `diff3_merge_segments()` in resolve.py, `parse_segments()` in learnings.py |
| FR-2: 15-row resolution matrix | Satisfied | 14 enumerable rows in `_resolve_heading`/`_resolve_both_present`/`_resolve_one_sided_deletion`; Row 15 (all absent) is structurally impossible |
| FR-3: All merge paths covered | Satisfied | Phase 3 conflict path via `resolve_learnings_md`; phase 4 all-paths via `remerge_learnings_md` |
| FR-4: Conflict markers at line granularity | Satisfied | `_format_conflict_segment` wraps body lines in `<<<<<<</=======/>>>>>>>` markers |
| NFR-1: Precommit structural validation | Satisfied | `_detect_orphaned_content` added to `validate()` in learnings.py |
| NFR-2: No false positives on clean learnings.md | Satisfied | `test_clean_learnings_file_no_orphan_errors` uses actual file structure |

---

## Positive Observations

- Resolution matrix decomposition into `_resolve_heading`, `_resolve_both_present`, `_resolve_one_sided_deletion` cleanly separates the three structural cases. Each function handles one decision axis.
- `_segments_to_content_with_conflicts` correctly defers to `_format_conflict_segment` for conflicting headings, overriding the merged body — ensures the conflict marker content is authoritative.
- Preamble special-casing in `_resolve_both_present` (additive merge, no conflict) matches the design decision and handles the real-world case where both sides append to the preamble.
- `remerge_learnings_md` correctly guards on `MERGE_HEAD` existence and file existence before attempting the merge — no spurious re-merges outside merge context.
- Integration tests use real git repos via `tmp_path` fixtures with `mock_precommit`, matching testing conventions. Tests reproduce the two specific observed failure scenarios from the diagnostic.
- All 30 unit tests in `test_learnings_diff3.py` directly correspond to matrix rows and output format cases — test suite serves as a living specification for the resolution matrix.
