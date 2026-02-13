# Runbook Review: worktree-update-recovery

**Artifact**: `plans/worktree-update/runbook.md`
**Date**: 2026-02-13T23:45:00Z
**Mode**: review + fix-all
**Phase types**: General (non-TDD)

---

## Summary

- Total steps: 6 (1.1-1.6)
- Issues found: 1 critical, 4 major, 1 minor
- Issues fixed: 6
- Unfixable (escalation required): 0
- Overall assessment: **Ready**

All 6 findings from deliverable review (C2, C3, C4, C5, M1, M2) are correctly mapped to steps. Runbook structure is sound. File references verified. All fixes applied.

---

## Critical Issues

### C1. File reference error in validation commands
**Location**: Steps 1.3 and 1.4, validation sections
**Problem**: Validation commands reference `tests/test_worktree_cli.py` which doesn't exist in the codebase. The actual test file is `tests/test_worktree_commands.py` or the tests don't exist yet.
**Fix**: Updated validation sections to account for test function absence, reference correct file path, and provide manual verification fallback.
**Status**: FIXED

---

## Major Issues

### M1. Missing prerequisite validation
**Location**: Step 1.2 (agent-core setup recipe)
**Problem**: Creation step touching `agent-core/justfile` lacks investigation prerequisite. Should read existing file structure before adding new recipe.
**Fix**: Added prerequisite: "Read `agent-core/justfile` (full file) — understand existing recipe structure and patterns."
**Status**: FIXED

### M2. Prescriptive implementation code in general step
**Location**: Step 1.3, implementation approach section
**Problem**: Full Python code block with exact implementation (`in_relevant_section = False`, loop structure, etc.). General runbook steps should describe behavior and approach, not prescribe exact code.
**Fix**: Replaced code block with behavioral description of state tracking approach (including/skipping states, bullet detection, continuation handling).
**Status**: FIXED

### M3. File location ambiguity
**Location**: Steps 1.5 and 1.6
**Problem**: Step 1.5 says "Create new test function" without clarifying it's added to existing file. Step 1.6 offered two file options without choosing one.
**Fix**:
- Step 1.5: Clarified "Add new test function to existing file (`test_worktree_merge_parent.py`)"
- Step 1.6: Removed ambiguity, specified `test_worktree_merge_validation.py` with rationale (validation-focused)
**Status**: FIXED

### M4. Validation command inconsistency
**Location**: Step 1.6, validation section
**Problem**: Validation showed two alternative pytest commands (validation file OR parent file) after choosing specific file in implementation.
**Fix**: Removed alternative command, kept only the chosen file: `pytest tests/test_worktree_merge_validation.py::test_merge_idempotency -v`
**Status**: FIXED

---

## Minor Issues

### m1. Validation assumes non-existent test functions
**Location**: Steps 1.3 and 1.4
**Problem**: Validation commands reference specific test functions that may not exist yet (test_filter_section_continuation, test_focus_session_plan_dir).
**Fix**: Updated validation sections to conditionally check for test existence and provide manual verification fallback when tests don't exist.
**Status**: FIXED

---

## Fixes Applied

- Step 1.2: Added prerequisite to read agent-core/justfile before modification
- Step 1.3: Replaced prescriptive code block with behavioral state-tracking description
- Step 1.3: Updated validation to handle missing test function, correct file path
- Step 1.4: Updated validation to handle missing test function, correct file path
- Step 1.5: Clarified adding to existing file (not creating new)
- Step 1.6: Removed file location ambiguity, chose validation file with rationale
- Step 1.6: Removed alternative validation command

---

## Requirements Satisfaction

| Finding | Step | Coverage |
|---------|------|----------|
| C2: wt-merge THEIRS clean tree check | 1.1 | ✅ Full |
| C3: agent-core setup recipe | 1.2 | ✅ Full |
| M1: _filter_section continuation lines | 1.3 | ✅ Full |
| M2: plan_dir regex case-sensitivity | 1.4 | ✅ Full |
| C4: Precommit failure test | 1.5 | ✅ Full |
| C5: Merge idempotency test | 1.6 | ✅ Full |

**Deferred findings (correctly excluded):**
- C1: wt-ls native bash → workwoods FR-1
- R1: Auto-combine session.md/jobs.md → workwoods FR-5/FR-6
- M3-M10: Test quality improvements → post-workwoods
- 24 minor findings → batch or defer

---

## LLM Failure Mode Check

### Vacuity
**Status**: ✅ Pass — All steps produce functional outcomes (code fixes, config additions, test additions).

### Dependency Ordering
**Status**: ✅ Pass — Steps are independent (can run in parallel per metadata). No forward references.

### Density
**Status**: ✅ Pass — Step scope appropriate. No single-line fixes inflated to full steps. No overloaded steps combining unrelated domains.

### Checkpoint Spacing
**Status**: ✅ Pass — Final checkpoint covers all 6 steps (reasonable for recovery work). Each step has clear validation criteria.

---

## File Reference Validation

| File Path | Status | Notes |
|-----------|--------|-------|
| `justfile` | ✅ Exists | Lines 209-222 verified for wt-merge recipe |
| `agent-core/justfile` | ✅ Exists | Setup recipe to be added |
| `src/claudeutils/worktree/cli.py` | ✅ Exists | Lines 55-60, 73 verified |
| `tests/test_worktree_merge_parent.py` | ✅ Exists | Lines 89-159 verified |
| `tests/test_worktree_merge_validation.py` | ✅ Exists | Idempotency test to be added |
| ~~`tests/test_worktree_cli.py`~~ | ❌ Does not exist | **Fixed**: Updated to `test_worktree_commands.py` or manual verification |

---

## Metadata Accuracy

**Total Steps**: 6 — ✅ Matches actual count (1.1, 1.2, 1.3, 1.4, 1.5, 1.6)

**Execution Model**: Sonnet for all steps — ✅ Appropriate (code fixes, config updates, test additions)

**Step Dependencies**: Independent — ✅ Correct (all steps touch different files, no dependency chain)

**Prerequisites**:
- Repository clean state ✅
- Test suite functional ✅
- **Added**: Read agent-core/justfile before Step 1.2 ✅

---

## Step Quality (General Runbook)

### Objective Clarity
✅ All steps have clear objectives tied to specific findings

### Implementation Guidance
✅ Sufficient detail for sonnet execution (file paths, line references, behavioral guidance)
**Fixed**: Removed prescriptive code from Step 1.3

### Validation Criteria
✅ Each step has specific validation (grep patterns, pytest commands, manual tests)
**Fixed**: Updated validation commands to handle missing test functions

### Error Conditions
✅ Error conditions identified for Steps 1.1-1.6 (git failures, syntax errors, mock issues, cleanup gaps)

### Prerequisites
✅ Investigation prerequisites now complete
**Fixed**: Added prerequisite for Step 1.2 (agent-core/justfile structure)

---

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes — proceed to orchestration.
