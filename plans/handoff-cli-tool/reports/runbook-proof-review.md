# Runbook Review: handoff-cli-tool

**Artifact**: `plans/handoff-cli-tool/runbook.md`
**Date**: 2026-03-14T00:00:00Z
**Mode**: review + fix-all
**Phase types**: Mixed (3 general steps in Phase 1, 6 TDD phases)

## Summary

Post-proof-verdict review of the handoff-cli-tool runbook after 6 revise verdicts were applied. The runbook is structurally sound with 25 items across 7 phases. Three minor issues were found and fixed: a misleading cycle note in Cycle 3.3, a duplicate test case in Step 1.3, and an open question embedded in the Outstanding Design Revisions section.

**Overall Assessment**: Ready (with escalation note on ST-1 outline alignment)

---

## Critical Issues

None.

---

## Major Issues

None.

---

## Minor Issues

### 1. Cycle 3.3 Note Inaccurate — "top priority unblocked items" mischaracterizes the algorithm

**Location**: Cycle 3.3, opening note
**Problem**: Note said ST-1 changed to "top priority unblocked items" — but the implemented algorithm is "first eligible consecutive group in document order, cap 5." The Outstanding Design Revisions section clarified "consecutive constraint retained," making the note's description contradictory. An executor reading the note would expect a priority-based algorithm, then find consecutive logic in the assertions.
**Fix**: Replaced with "first eligible consecutive group (document order, cap 5)" and explained that the cap and consecutive constraint retention are both implemented.
**Status**: FIXED

### 2. Step 1.3 — Duplicate test case (`test_git_changes_mixed` duplicates `test_git_changes_clean_submodule_omitted`)

**Location**: Step 1.3, Tests section, lines 241-242
**Problem**: Both tests described the same scenario: parent dirty + submodule clean → only parent section shown. `test_git_changes_clean_submodule_omitted` asserted "no submodule section present"; `test_git_changes_mixed` asserted "only parent section has content." These test the same behavior and the second adds no new branch point. Density violation — adjacent test descriptions for the same condition.
**Fix**: Removed `test_git_changes_mixed`, consolidated its intent into `test_git_changes_clean_submodule_omitted` assertion text ("no submodule section present in output").
**Status**: FIXED

### 3. Outstanding Design Revisions — Third bullet is an open investigation question, not a directive

**Location**: `## Outstanding Design Revisions`, third bullet
**Problem**: "What in the runbook generation process caused Cycles 7.1-7.3 to be deferred..." — this is an investigation note framed as a question. Runbook content must be executable directives or clear context; open questions embedded in the runbook stall executors who may spend time investigating instead of orchestrating.
**Fix**: Removed the third bullet. The ST-1 semantics bullet also updated for consistency with the Cycle 3.3 fix.
**Status**: FIXED

---

## Fixes Applied

- Cycle 3.3, opening note — Replaced misleading "top priority unblocked items" with accurate description of consecutive-first algorithm with cap 5
- Step 1.3, test list — Removed `test_git_changes_mixed` (duplicate of `test_git_changes_clean_submodule_omitted`); consolidated assertion text
- Outstanding Design Revisions — Removed open investigation question (third bullet); updated ST-1 bullet wording for consistency

---

## Structural Observations (Non-Findings)

These are documented for audit trail but do not block orchestration:

- **Cycle 4.5 numbering gap**: Phase 4 runs 4.1→4.4→4.6→4.7 after the 4.5 kill. The Execution Model metadata correctly documents "4.1-4.4, 4.6-4.7." Executors should read the metadata — the gap is intentional and documented.
- **H-4 step_reached values**: Runbook Cycle 4.4 documents `"write_session"` and `"diagnostics"` as valid values (precommit step removed). Outline H-4 lists `"precommit"` as a third value. The runbook's simplified set is the post-proof-verdict canonical version.
- **plan_dir extension mechanism**: Cycle 2.1 GREEN says "Extend ParsedTask with plan_dir" without specifying subclass vs wrapper. The executor has discretion on mechanism — behavioral outcome (`.plan_dir` accessible) is specified. Acceptable ambiguity for an executor with design context.

---

## Unfixable Issues (Escalation Required)

1. **ST-1 outline alignment**: Cycle 3.3 note says "Outline update required before orchestration." The `plans/handoff-cli-tool/outline.md` ST-1 section wording needs updating to match the "first eligible consecutive group" algorithm before the runbook is orchestrated. The runbook implementation is correct; the outline still uses "largest independent group" wording. This is a cross-artifact consistency issue — the runbook cannot fix the outline.

---

**Ready for next step**: Yes — all runbook issues fixed. Outline ST-1 wording update required before orchestration (see escalation above).
