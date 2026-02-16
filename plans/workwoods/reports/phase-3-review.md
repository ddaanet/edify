# Runbook Review: Phase 3 - Cross-Tree Aggregation

**Artifact**: plans/workwoods/runbook-phase-3.md
**Date**: 2026-02-16T21:30:00Z
**Mode**: review + fix-all
**Phase types**: TDD (8 cycles)

## Summary

Phase 3 implements cross-tree status collection via git worktree discovery and per-tree data gathering. Total items: 8 cycles. Issues found: 0 critical, 8 major (weak RED assertions), 0 minor. All issues fixed.

**Overall Assessment**: Ready

## Major Issues

### Issue 1: Cycle 3.1 RED assertions too vague
**Location**: Cycle 3.1, lines 23-29
**Problem**: RED assertions described porcelain format generically without specifying exact input structure, block separation, or prefix stripping behavior. Executor could write tests that check "contains path and branch" without verifying blank-line separation or refs/heads/ stripping.
**Fix**: Added specific format details — blocks separated by blank lines, "worktree <path>" on first line, "branch <ref>" on second line, refs/heads/ prefix stripped. Added exact input examples with newlines.
**Status**: FIXED

### Issue 2: Cycle 3.2 RED assertions lack behavioral specificity
**Location**: Cycle 3.2, lines 66-72
**Problem**: Assertions described is_main and slug fields generically without specifying types (boolean vs truthy), None vs empty string distinction, or exact basename extraction. Tests could pass with is_main=1 or slug="".
**Fix**: Added type specifications (boolean True, not truthy), None vs empty string distinction, exact basename verification, specific path-to-slug examples.
**Status**: FIXED

### Issue 3: Cycle 3.3 RED assertions missing edge cases and format verification
**Location**: Cycle 3.3, lines 112-118
**Problem**: Assertions described commit counting generally without specifying return type, edge case values (no session.md → 0, session.md in HEAD → 0), or git command format verification.
**Fix**: Added concrete setup (4 commits, 3 after session.md), exact return value (integer 3), edge cases with expected values, subprocess verification (no mocking), command format check.
**Status**: FIXED

### Issue 4: Cycle 3.4 RED assertions missing type and format checks
**Location**: Cycle 3.4, lines 155-161
**Problem**: Assertions described extraction generically without verifying tuple return type, exact string matching (not substring), integer type check, or Unix epoch validity.
**Fix**: Added tuple type check, exact string match specification, integer type verification, Unix epoch value range check, git command format verification.
**Status**: FIXED

### Issue 5: Cycle 3.5 RED assertions lack edge case coverage
**Location**: Cycle 3.5, lines 198-203
**Problem**: Assertions described dirty detection generally without specifying boolean type (not truthy), untracked file handling, or exact git command format.
**Fix**: Added boolean type specification, untracked file edge case (must return False), exact git command verification (--porcelain --untracked-files=no).
**Status**: FIXED

### Issue 6: Cycle 3.6 RED assertions missing function verification and edge cases
**Location**: Cycle 3.6, lines 239-245
**Problem**: Assertions described task extraction generically without verifying extract_task_blocks usage, task name format (no markdown), or all None-return edge cases.
**Fix**: Added extract_task_blocks call verification, exact session.md format with markdown example, task name-only return (no formatting), all edge cases (no section, empty section, missing file).
**Status**: FIXED

### Issue 7: Cycle 3.7 RED assertions lack deduplication specifics
**Location**: Cycle 3.7, lines 285-291
**Problem**: Assertions described plan discovery generally without specifying deduplication behavior, precedence rules (main wins), or aggregate count verification.
**Fix**: Added concrete setup (plan-a in main, plan-b in worktree, plan-c in both), exact count verification (2 or 1 depending on deduplication), precedence rule (main wins), real list_plans() usage.
**Status**: FIXED

### Issue 8: Cycle 3.8 RED assertions missing order and type verification
**Location**: Cycle 3.8, lines 329-335
**Problem**: Assertions described sorting generally without specifying exact timestamp relationship, index-to-tree mapping, or type checks for timestamp values.
**Fix**: Added concrete timestamp setup (T3 > T2 > T1), exact index checks (trees[0] is most recent), descending verification formula, slug/is_main mapping to indices, integer type check.
**Status**: FIXED

## Fixes Applied

- Cycle 3.1: Added porcelain format specifics (blank line separation, line structure, refs/heads/ stripping)
- Cycle 3.2: Added type specifications (boolean True, None vs empty string, exact basename)
- Cycle 3.3: Added concrete setup, exact return values, edge cases, subprocess verification
- Cycle 3.4: Added tuple type check, exact string match, integer type, Unix epoch range
- Cycle 3.5: Added boolean type, untracked edge case, exact git command format
- Cycle 3.6: Added extract_task_blocks verification, task name format, all edge cases
- Cycle 3.7: Added deduplication setup, count verification, precedence rule, real function usage
- Cycle 3.8: Added timestamp setup, index mapping, descending formula, type checks

## Unfixable Issues (Escalation Required)

None — all issues fixed

---

**Ready for next step**: Yes
