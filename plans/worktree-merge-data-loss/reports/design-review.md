# Design Review: Worktree Merge Data Loss

**Design Document**: plans/worktree-merge-data-loss/design.md
**Review Date**: 2026-02-16
**Reviewer**: design-vet-agent (opus)

## Summary

The design addresses two compounding bugs (incomplete merge + destructive `rm`) through three well-defined tracks: removal safety guard, merge correctness checks, and skill update. The architecture is grounded in incident evidence, proposes defense-in-depth validation, and correctly identifies the shared helper (`_is_branch_merged`) needed by both tracks.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Missing code path for Phase 4 "else" branch**
   - Problem: The Phase 4 flow diagram specified `else (no MERGE_HEAD, no staged): check if already merged -> skip or exit 2` but no corresponding code block existed in the MERGE_HEAD Checkpoint section. A planner would not know what code to write for this case.
   - Impact: Planner could omit this branch or implement it inconsistently with the rest of the checkpoint logic.
   - Fix Applied: Added explicit `else` branch to the Phase 4 code block with `_is_branch_merged` check (exit 2 if not merged, skip if already merged). Updated the accompanying prose to describe all three branches. Added corresponding test case "No MERGE_HEAD + no staged + branch not merged -> exit 2" to Track 2 tests.

### Minor Issues

1. **Orphan branch guard message would say "0 unmerged commit(s)"**
   - Problem: `_classify_branch` returns `(0, False)` for orphan branches (merge-base failure). The guard logic's stderr message "has {count} unmerged commit(s)" would produce "has 0 unmerged commit(s)" -- confusing and uninformative.
   - Fix Applied: Added orphan-specific message "Branch {slug} is orphaned (no common ancestor). Merge first." in both the `_classify_branch` docstring and the guard logic pseudocode. Added orphan branch test case to Track 1 tests.

2. **Phase 4 flow diagram formatting ambiguity**
   - Problem: Line starting with bare `->` at bottom of flow diagram looked like a fifth conditional branch rather than a post-conditional step applying to all paths.
   - Fix Applied: Restructured flow diagram to expand the `else` branch inline and clarify that ancestry validation follows all successful commit/skip paths.

## Requirements Alignment

**Requirements Source:** inline (design.md Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Track 1 `_classify_branch` + `_is_branch_merged` |
| FR-2 | Yes | Track 1 guard logic, exit 1 |
| FR-3 | Yes | Track 1 focused-session classification |
| FR-4 | Yes | Track 1 guard (exit codes 0/1/2) |
| FR-5 | Yes | Track 1 messaging, D-3 decision |
| FR-6 | Yes | Track 2 MERGE_HEAD checkpoint code |
| FR-7 | Yes | Track 2 `_validate_merge_result` |
| FR-8 | Yes | Track 1 success messages |
| FR-9 | Yes | Track 3 skill update prose |

**Gaps:** None.

## Positive Observations

- **Incident-driven design.** Every requirement traces to observed failure behavior. The evidence section (commit hashes, cherry-pick recovery) grounds the design in reality rather than speculation.
- **Defense-in-depth layers.** Track 2 has three independent checks (MERGE_HEAD presence, ancestry validation, parent count diagnostic) -- any one would have caught the incident.
- **Guard-before-destruction ordering.** D-6 explicitly addresses the sequencing bug where `shutil.rmtree` ran before `git branch -d` could detect the problem. The new guard runs first, before any destructive operation.
- **Shared helper design.** `_is_branch_merged` in utils.py correctly identified as shared between cli.py and merge.py, avoiding duplication.
- **Root cause honesty.** Design explicitly states the root cause is not fully determined and frames Track 2 as defensive rather than claiming to fix an understood mechanism.
- **Reproduction test note.** Acknowledges the parent repo file preservation test may not reproduce the original bug, setting correct expectations for TDD.
- **Documentation Perimeter.** All required reading files verified to exist on disk. Line ranges for cli.py (347-382) and merge.py (261-299) confirmed accurate.

## Recommendations

- The `_validate_merge_result` function uses raw `subprocess.run` instead of the project's `_git` helper. The planner should note this and use `_git` from utils.py for consistency (the design's code block shows `subprocess.run` directly).
- Track 2's diagnostic logging (parent count warning) should specify where it runs relative to `_validate_merge_result` -- before or after. Currently both appear in the Post-Merge Ancestry Validation section but the ordering is implicit.

## Next Steps

- Design is ready for `/runbook` planning
- No fixes require designer re-review
