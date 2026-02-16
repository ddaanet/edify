# Outline Review: Worktree Merge Data Loss

**Artifact**: plans/worktree-merge-data-loss/outline.md
**Date**: 2026-02-16T13:15:00-08:00
**Mode**: review + fix-all

## Summary

The outline addresses the core merge data loss bug and provides a two-track fix (merge correctness + removal safety). The approach is sound and feasible. All requirements are covered with explicit traceability. Several critical issues were identified and fixed: missing requirement coverage, vague decision points, incomplete scope definition, and unclear validation semantics.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | D-1, Track 1 | Complete | Two-parent merge commits for real history |
| FR-2 | Track 1: Ensure merge parent | Complete | MERGE_HEAD verification prevents data loss |
| FR-3 | Track 2: Guard rm | Complete | Ancestor check blocks unmerged removal |
| FR-4 | Track 2: Focused session detection | Complete | Exception for single-commit worktrees |
| FR-5 | Track 1: Ensure merge parent | Complete | MERGE_HEAD check before Phase 4 commit |
| FR-6 | Track 1: Post-merge validation | Complete | Two-parent verification after commit |
| FR-7 | Track 1: Detect branch depth | Complete | Commit count classification |
| FR-8 | Track 1: Detect branch depth | Complete | Skip merge for focused-session-only |
| FR-9 | Track 1: Ensure merge parent | Complete | Two-parent preservation |
| FR-10 | Track 2: Guard rm | Partial | Error message specified, success feedback missing — FIXED |

**Traceability Assessment**: All requirements covered after fixes

## Review Findings

### Critical Issues

1. **D-2 decision point missing error vs force-create distinction**
   - Location: Key Decisions section
   - Problem: D-2 frames "error vs force merge commit creation" but the outline's "Ensure merge parent" section only describes failing with clear error. The force-create path is not elaborated, leaving implementation ambiguous.
   - Fix: Clarified D-2 to specify fail-fast as chosen approach, noted force-create as rejected alternative
   - **Status**: FIXED

### Major Issues

1. **Missing CLI feedback specification for success paths**
   - Location: Track 2, FR-10
   - Problem: Outline specifies error messages ("refuse removal, exit 1 with clear message") but doesn't specify success feedback for rm operation
   - Fix: Added success feedback specification to Track 2
   - **Status**: FIXED

2. **Post-merge validation semantics unclear**
   - Location: Track 1: Post-merge validation
   - Problem: "verify the commit has two parents" — unclear if this check applies to ALL merges or only non-focused-session merges. Focused-session merges are skipped, so there's no commit to verify.
   - Fix: Added constraint that validation only applies when merge commit was created
   - **Status**: FIXED

3. **Scope OUT missing explicit items**
   - Location: Scope section
   - Problem: "Out" section lists what's not changing, but doesn't explicitly exclude potential scope creep areas like merge strategy selection, git config changes, or precommit check additions
   - Fix: Added explicit out-of-scope items
   - **Status**: FIXED

### Minor Issues

1. **Branch depth threshold lacks rationale**
   - Location: D-1
   - Problem: "1 commit = focused session, 2+ = real history" — stated as decision but rationale not provided
   - Fix: Added rationale (focused session = initial commit only, 2+ = collaborative work with history)
   - **Status**: FIXED

2. **Skill update scope vague**
   - Location: Skill Update section
   - Problem: "Skill must handle this new exit code" — doesn't specify WHAT the skill should do (retry? escalate? report?)
   - Fix: Specified skill behavior (report merge bug, escalate to user)
   - **Status**: FIXED

3. **Phase 3 mention in Track 1 imprecise**
   - Location: Track 1: Ensure merge parent
   - Problem: "After Phase 3, before Phase 4 commits" — mixing implementation phases with track structure creates navigational confusion
   - Fix: Rephrased to "After merge initiation, before commit" (implementation-neutral)
   - **Status**: FIXED

4. **Missing test scope detail**
   - Location: Scope IN section
   - Problem: "Tests for merge parent preservation and removal guard" — doesn't specify test types (unit? integration? both?)
   - Fix: Specified test coverage (unit + integration for both tracks)
   - **Status**: FIXED

## Fixes Applied

- D-2 — Clarified fail-fast chosen, force-create rejected
- Track 2 — Added success feedback specification (FR-10 completion)
- Track 1 Post-merge validation — Added "only when merge commit created" constraint
- Scope OUT — Added explicit exclusions (merge strategy, git config, precommit checks, batch merge)
- D-1 — Added rationale for 1-commit threshold
- Skill Update — Specified error handling behavior (report merge bug, escalate)
- Track 1 Ensure merge parent — Rephrased "Phase 3/4" to implementation-neutral language
- Scope IN Tests — Specified unit + integration coverage

## Positive Observations

- Clear separation of merge correctness vs removal safety concerns
- Explicit detection of focused-session-only edge case
- Post-merge validation as defense-in-depth (not just pre-commit checks)
- Skill update scoped appropriately (Mode C error handling only)
- Phase type assignments match work type (TDD for behavioral changes, general for prose)
- Scope boundaries explicit and reasonable

## Recommendations

- During implementation, verify git merge-base behavior with submodule-only changes (Phase 2 creates intermediate commit — does this affect branch depth count?)
- Consider adding diagnostic logging to merge.py for future debugging (MERGE_HEAD state, branch depth, ancestor check results)
- Skill update should reference new exit code semantics explicitly in Mode C step 3 (currently says "may now refuse" — should be "will refuse when X")

---

**Ready for user presentation**: Yes
