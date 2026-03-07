# Runbook Review: Phases 2 and 3

**Artifact**: `plans/handoff-cli-tool/runbook-phase-2.md`, `plans/handoff-cli-tool/runbook-phase-3.md`
**Date**: 2026-03-07T00:00:00Z
**Mode**: review + fix-all
**Phase types**: TDD (Phase 2: 2 cycles, Phase 3: 4 cycles)

## Summary

Both phases are structurally sound TDD phases with good RED/GREEN discipline. GREEN phases are behavioral (no prescriptive code). RED assertions are specific with expected failure reasons. Three issues found and fixed: a fixture inconsistency that would have broken Phase 3 tests, an algorithm terminology error that could have caused a wrong implementation, and an underspecified parsing target for `_worktree ls` output.

**Overall Assessment**: Ready

---

## Critical Issues

### Issue 1: Fixture inconsistency — "Future work" task missing `→ wt` marker

**Location**: Phase 2, Cycle 2.1, `SESSION_MD_FIXTURE`
**Problem**: The fixture shows `- [ ] **Future work** — ...` with no `→` marker. Phase 3 Cycle 3.1 asserts that `render_next` skips tasks with `worktree_marker="wt"`, and Phase 3 Cycle 3.2 asserts the Worktree section renders `- Future work → wt`. Both assertions require "Future work" to have `worktree_marker="wt"`, which requires `→ \`wt\`` in the task line. Without the marker in the fixture, tests importing it from Phase 2 fixtures would produce `worktree_marker=None`, causing Phase 3 tests to fail with wrong data, not the behavior under test.
**Fix**: Added `→ \`wt\`` to the "Future work" task line in the fixture.
**Status**: FIXED

---

## Major Issues

### Issue 2: Algorithm terminology error in Cycle 3.3 GREEN

**Location**: Phase 3, Cycle 3.3, GREEN Phase — Approach line
**Problem**: "find largest clique of independent tasks" — a clique is a fully-connected subgraph (all members depend on each other), the opposite of what's needed. An independent set has no edges between members. An implementor following the "clique" description would build the wrong algorithm.
**Fix**: Replaced "largest clique of independent tasks" with correct description: enumerate subsets of pending tasks in descending size order, return first subset with no dependency edges between any pair.
**Status**: FIXED

---

## Minor Issues

### Issue 3: Underspecified `_worktree ls` output parsing in Cycle 3.4 GREEN

**Location**: Phase 3, Cycle 3.4, GREEN Phase — bullet "Parse `_worktree ls` output for plan status information"
**Problem**: No format specification for what to parse. The actual `_worktree ls` output format is `  Plan: {name} [{status}] → {next_action}` (from `format_rich_ls` in `src/claudeutils/worktree/display.py`). Without this, an implementor must guess the format or read implementation code.
**Fix**: Added the line pattern and extraction target: `lines matching \`  Plan: {name} [{status}] → ...\` — extract name and status into a dict \`{name: status}\` passed to \`render_pending()\``.
**Status**: FIXED

---

## Findings Not Raised

- **Pending section header mismatch** (`Pending:` in Phase 3 vs `In-tree:` in execute-rule.md): Pre-existing design decision in the outline (outline.md line 324 uses `Pending:`). Runbook faithfully reproduces the design's output spec. Suppress.
- **`_extract_plan_from_block()` private import**: Outline Expansion Guidance explicitly directs importing this private function. Suppress.
- **`SessionFileError` not in `exceptions.py`**: Expected to be created during implementation per Phase 2 GREEN. Not a review finding.

---

## Fixes Applied

- Phase 2, Cycle 2.1 fixture: Added `→ \`wt\`` to "Future work" task line
- Phase 3, Cycle 3.3 GREEN Approach: Corrected "clique" → "independent set" with brute-force description
- Phase 3, Cycle 3.4 GREEN: Added `_worktree ls` line format and extraction target

---

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
