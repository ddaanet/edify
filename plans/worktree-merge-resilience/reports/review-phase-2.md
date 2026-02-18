# Runbook Review: Phase 2 — Submodule conflict pass-through

**Artifact**: `plans/worktree-merge-resilience/runbook-phase-2.md`
**Date**: 2026-02-18T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (2 cycles)

## Summary

Phase 2 covers FR-1 (submodule conflict pass-through) via two cycles: the core `check=False` behavioral change (Cycle 2.1) and a resume-after-resolution regression guard (Cycle 2.2). Cycle 2.1 is well-formed — RED assertions are concrete, expected failure matches source code behavior, and GREEN avoids prescriptive code. Cycle 2.2 had a self-contradictory "Expected failure" section with hedging mid-paragraph text ("Actually —") that left the cycle's expected failure mode unresolved, and one assertion leaked an implementation mechanism. All issues fixed.

**Overall Assessment**: Ready

## Critical Issues

None.

## Major Issues

### Issue 1: Cycle 2.2 "Expected failure" self-contradictory and unresolved

**Location**: Cycle 2.2, RED Phase, "Expected failure" section (lines 84-88)
**Problem**: Two competing expected failure descriptions in the same section. First paragraph described one failure mode, then "Actually —" mid-paragraph described a different failure mode. Ended with "GREEN may already pass" — planning-time ambiguity left in the runbook. An executor cannot determine what failure to expect or verify.
**Fix**: Replaced both paragraphs with a single clear expected failure: test does not exist yet (collection error). Added explanatory note that GREEN may pass immediately because the skip logic predates this change — this cycle is a regression guard, not a behavioral addition.
**Status**: FIXED

### Issue 2: Cycle 2.2 assertion leaking implementation mechanism

**Location**: Cycle 2.2, RED Phase, Assertions, bullet 4 (line 82)
**Problem**: "Phase 2 is effectively skipped: `wt_commit` is now an ancestor of agent-core HEAD → existing skip logic triggers (line 102: `wt_commit == local_commit` check, or `merge-base --is-ancestor` returns 0)". This describes internal mechanism, not observable behavior. An executor could satisfy this assertion with a mock that makes the check return 0 without the actual skip occurring. The cited line numbers also include alternative paths ("or") which are not specific enough to verify.
**Fix**: Replaced with two behavioral assertions: (1) `git -C agent-core merge-base --is-ancestor <wt_commit> HEAD` returns 0 (observable git state), (2) git log shows exactly 2 commits (manual resolution + parent merge) — no extra Phase 2 commit indicating a re-merge attempt.
**Status**: FIXED

## Minor Issues

### Issue 3: Cycle 2.2 assertion 3 — "already present" vague

**Location**: Cycle 2.2, RED Phase, Assertions, bullet 3 (line 81)
**Problem**: "Git log shows submodule merge commit already present (from manual resolution), plus final parent merge commit" does not specify how many commits total, what commit messages to match, or in what order. An executor could satisfy this with any number of commits containing those subjects.
**Fix**: Replaced with: "`git log --format=%s` shows exactly 2 commits since test start: the manual submodule resolution commit message and the final parent merge commit (🔀 Merge slug)".
**Status**: FIXED

### Issue 4: No phase metadata block

**Location**: Phase header
**Problem**: No `Total Steps`, `Model`, or metadata block present. Weak orchestrator cannot validate cycle count or model assignment from the header.
**Fix**: Omitting — phase files in this runbook do not use a metadata block format; none of the other phase files have one. Cycle count is visible from headers (2 cycles). Adding a non-standard block would be inconsistent. Noting for informational purposes only.
**Status**: OUT-OF-SCOPE (no metadata block format established for this runbook)

## Fixes Applied

- Cycle 2.2, "Expected failure" section — replaced self-contradictory two-paragraph block with single clear expected failure (collection error) and regression-guard framing note
- Cycle 2.2, Assertions bullet 4 — replaced implementation mechanism description with observable behavioral assertion (`merge-base --is-ancestor` return code)
- Cycle 2.2, Assertions bullet 3 — replaced vague "already present" with specific commit count and message pattern

## File Reference Validation

- `tests/test_worktree_merge_submodule.py` — exists, confirmed
- `src/claudeutils/worktree/merge.py` — exists, confirmed
- Line 126 (`_git("-C", "agent-core", "merge", "--no-edit", wt_commit)`) — confirmed: line 126 in source matches description exactly, uses default `check=True`
- Lines 93-135 (`_phase2_resolve_submodule`) — confirmed: function spans lines 93-135
- Lines 100-103 (`wt_commit == local_commit` check) — confirmed: lines 102-103
- Lines 104-116 (`merge-base --is-ancestor` check) — confirmed: lines 105-116

## RED Plausibility Check

**Cycle 2.1:** Source at line 126: `_git("-C", "agent-core", "merge", "--no-edit", wt_commit)` with `check=True` (default in `_git()`). On merge conflict, git exits non-zero → `_git()` raises `CalledProcessError` → CliRunner catches and returns exit code 1. Expected failure (`SystemExit(1)`) is correct. RED will fail.

**Cycle 2.2:** Test does not exist → `pytest` collection error. RED will fail.

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
