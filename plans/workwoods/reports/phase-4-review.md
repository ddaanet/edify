# Runbook Review: Phase 4 (wt-ls CLI Upgrade)

**Artifact**: plans/workwoods/runbook-phase-4.md
**Date**: 2026-02-16T20:45:00Z
**Mode**: review + fix-all
**Phase types**: TDD (6 cycles)

## Summary

Reviewed Phase 4 runbook implementing upgraded wt-ls CLI with rich output mode and backward-compatible porcelain flag. Found 8 issues across critical, major, and minor categories. All issues fixed directly in the runbook.

**Overall Assessment**: Ready

**Issue breakdown:**
- Critical: 1 (dependency ordering)
- Major: 4 (metadata, vague RED assertions)
- Minor: 3 (prescriptive GREEN hints)
- Total items: 6 cycles
- Issues fixed: 8
- Unfixable (escalation required): 0

## Critical Issues

### Issue 1: Missing Phase 1-3 dependency check
**Location**: Cycle 4.3, line 107
**Problem**: Cycle attempts to import and call `aggregate_trees()` from `planstate.aggregation` module, which is implemented in Phase 1-3. If executor runs Phase 4 before Phase 1-3 completes, imports will fail with ModuleNotFoundError. No prerequisite validation guards against this.
**Fix**: Added prerequisite check at start of Cycle 4.3: "Verify `src/claudeutils/planstate/aggregation.py` exists with `aggregate_trees()` function (Phase 1-3 dependency). If missing, STOP — Phase 4 requires completed planstate module."
**Status**: FIXED

## Major Issues

### Issue 2: Missing Total Steps metadata
**Location**: Phase header, line 13
**Problem**: Phase header contains "Estimated Complexity" but missing "Total Steps" field required by Weak Orchestrator Metadata pattern. Orchestrator cannot validate cycle count against metadata.
**Fix**: Added "**Total Steps:** 6 cycles" to phase header metadata section
**Status**: FIXED

### Issue 3: Vague RED assertions (Cycle 4.3)
**Location**: Cycle 4.3, RED phase, lines 111-116
**Problem**: Assertions use template placeholders `<slug|"main">`, `<●|○>`, `<N commits>` without specifying concrete expected values. An executor could write different tests that all match this description but verify different behaviors. Violates "Could executor write different tests?" criterion.
**Fix**: Replaced vague placeholders with specific test scenarios: "For worktree with slug='test-wt', branch='feature', is_dirty=True, commits_since_handoff=3: Output contains `test-wt (feature)  ●  3 commits since handoff`" and parallel scenario for main tree with clean state.
**Status**: FIXED

### Issue 4: Vague RED assertions (Cycle 4.4)
**Location**: Cycle 4.4, RED phase, lines 161-166
**Problem**: Assertions say "Task line appears when task_summary is not None" with template `<task_name>`, but don't specify a concrete task name to verify. No specific expected string for test to match against.
**Fix**: Replaced template with specific scenario: "For tree with task_summary='Implement foo feature': Output contains exactly `  Task: Implement foo feature` (2-space indent)"
**Status**: FIXED

### Issue 5: Vague RED assertions (Cycle 4.5)
**Location**: Cycle 4.5, RED phase, lines 203-208
**Problem**: Assertions use templates `<plan-name>`, `<status>`, `<next-action>` without concrete values. Test description allows multiple incompatible implementations.
**Fix**: Replaced templates with specific scenario: "For tree containing plan 'foo' with status='designed', next_action='/runbook plans/foo/design.md': Output contains exactly `  Plan: foo [designed] → /runbook plans/foo/design.md`"
**Status**: FIXED

### Issue 6: Vague RED assertions (Cycle 4.6)
**Location**: Cycle 4.6, RED phase, lines 251-256
**Problem**: Assertions use template `<gate_message>` without concrete expected string. No specific gate message to verify in test.
**Fix**: Replaced template with specific scenario: "For plan with gate='vet stale — re-vet first': Output contains exactly `  Gate: vet stale — re-vet first`"
**Status**: FIXED

## Minor Issues

### Issue 7: Prescriptive GREEN hint (Cycle 4.3)
**Location**: Cycle 4.3, GREEN phase, lines 126-137
**Problem**: GREEN phase lists exact steps to execute ("Call aggregate_trees()", "For each tree in trees list: Format slug...") and prescribes f-string approach. Leans toward step-by-step recipe rather than behavioral description.
**Fix**: Reworded to emphasize behavior: "Call aggregate_trees() to get list of TreeStatus objects. For each tree: format and output header line with slug/branch, dirty indicator, commit status." Moved f-string mention to hint section.
**Status**: FIXED

### Issue 8: Prescriptive GREEN hints (Cycles 4.4, 4.5, 4.6)
**Location**: Cycles 4.4-4.6, GREEN phases
**Problem**: GREEN phases include exact f-string templates (e.g., `click.echo(f"  Task: {tree.task_summary}")`) which prescribe implementation rather than describe behavior.
**Fix**: Removed exact f-string templates, replaced with behavioral descriptions: "output task line with 2-space indent showing task name" and "Task line format: '  Task: ' followed by task_summary content". Moved format details to hint sections.
**Status**: FIXED

## Fixes Applied

- Added "Total Steps: 6 cycles" metadata to phase header
- Added Phase 1-3 dependency prerequisite check to Cycle 4.3
- Replaced vague RED assertion templates with concrete test scenarios (Cycles 4.3-4.6)
- Converted prescriptive GREEN steps to behavioral descriptions (Cycles 4.3-4.6)
- Moved implementation specifics (f-strings, exact formatting) to hint sections

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
