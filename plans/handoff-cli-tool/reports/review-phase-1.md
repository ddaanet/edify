# Runbook Review: Phase 1 — Shared Infrastructure

**Artifact**: `plans/handoff-cli-tool/runbook-phase-1.md`
**Date**: 2026-03-07T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (3 steps)

## Summary

Phase 1 is a general infrastructure phase (git helper extraction, package skeleton, git CLI). Four issues found: two major (wrong line reference + misleading `_git_ok` description), one major (missing import site), one minor (missing prerequisite). All four fixed directly. No unfixable issues.

**Overall Assessment**: Ready

---

## Critical Issues

None.

---

## Major Issues

### Issue 1: Wrong line reference and function name in Step 1.1 prerequisite

- **Location**: Step 1.1, `**Prerequisite:**` line
- **Problem**: Referenced `git_ops.py:85-112` and called function `_is_dirty()`. Actual function is `_is_parent_dirty()` starting at line 78. Line 85 falls inside the function body (the `output = _git(...)` call), not at the definition. An executor reading lines 85-112 would miss the function signature and docstring, and search for `_is_dirty` which doesn't exist.
- **Fix**: Changed to `git_ops.py:78-112` and corrected name to `_is_parent_dirty()`.
- **Status**: FIXED

### Issue 2: Internally contradictory `_git_ok` description

- **Location**: Step 1.1, Implementation item 2
- **Problem**: Said "calls `_git(*args, check=False)` and returns `True` if command succeeds (returncode == 0)" — but `_git()` returns a `str` (stdout), not a returncode. An executor following the first clause would write code that checks truthiness of a string, not returncode. The trailing sentence "Uses `subprocess.run` directly" contradicted the first clause without resolving the ambiguity.
- **Fix**: Removed the `_git()` call reference; replaced with a clear description: uses `subprocess.run` directly, returns `True` if returncode == 0. Added explicit note explaining why `_git()` can't be used.
- **Status**: FIXED

### Issue 3: Missing import site `worktree/remerge.py`

- **Location**: Step 1.1, Import updates list
- **Problem**: `src/claudeutils/worktree/remerge.py` imports `_git` from `claudeutils.worktree.git_ops` (confirmed: `remerge.py:9`). Not listed in the five import update sites. An executor following the step would miss this file, leaving a broken import after extraction.
- **Fix**: Added `worktree/remerge.py` as a sixth import update site.
- **Status**: FIXED

---

## Minor Issues

### Issue 4: Missing prerequisite in Step 1.2

- **Location**: Step 1.2, before `**Implementation:**`
- **Problem**: Step 1.2 modifies the existing `src/claudeutils/cli.py` to register the `_session` group. Creation steps that touch existing files require an investigation prerequisite. The step referenced "line 152" inline without a formal `**Prerequisite:**` field, meaning the executor had no guided read before modifying the file.
- **Fix**: Added `**Prerequisite:** Read src/claudeutils/cli.py:145-152 — understand existing cli.add_command(worktree) registration pattern to replicate for _session group.`
- **Status**: FIXED

---

## Fixes Applied

- Step 1.1, Prerequisite: corrected line range from `85-112` to `78-112`; corrected function name from `_is_dirty()` to `_is_parent_dirty()`
- Step 1.1, Item 2: rewrote `_git_ok` description to eliminate contradictory `_git()` call reference; clarified why `subprocess.run` is required directly
- Step 1.1, Item 6: updated line reference from `82-97` to `78-97`; noted the rename from `_is_parent_dirty` to `_is_dirty` and clarified no import updates needed (no callers outside git_ops.py)
- Step 1.1, Import updates: corrected `_is_dirty` → `_is_parent_dirty` in git_ops.py removal list; added `worktree/remerge.py` as sixth import site
- Step 1.2: added `**Prerequisite:**` field for `cli.py:145-152`

---

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
