# Runbook Review: error-handling

**Artifact**: `plans/error-handling/runbook.md`
**Date**: 2026-02-19T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (5 phases, 11 steps)

## Summary

General-phase-only runbook covering 5 phases: Foundation (1.1, 1.2), Orchestration Hardening (2.1, 2.2), Task Lifecycle (3.1, 3.2), CPS Chain Error Recovery (4.1, 4.2), and Consolidation (5.1, 5.2, 5.3). Steps are well-structured with clear objectives, prerequisites, and validation commands. One requirements gap found (Step 4.2 omitting orchestrate/handoff from CPS cross-reference coverage) — fixed.

**Overall Assessment**: Ready

## Findings

### Warning

1. **Outline review report missing**
   - Location: `plans/error-handling/reports/runbook-outline-review.md`
   - Problem: No `runbook-outline-review.md` found. The outline was reviewed (see `outline-review-2.md` and `outline-review.md`), but the file is not named per the expected convention.
   - Fix: Informational only — outline review was clearly performed (two review reports exist). No change to runbook required.
   - **Status**: INFORMATIONAL

### Major Issues

1. **Step 4.2 — Missing CPS cross-reference for orchestrate/SKILL.md and handoff/SKILL.md**
   - Location: Step 4.2
   - Problem: The outline's Phase 4 explicitly lists all cooperative skills requiring error handling updates: "Update cooperative skills (`/design`, `/runbook`, `/orchestrate`, `/handoff`) with error handling." Step 4.2 only targeted design/SKILL.md and runbook/SKILL.md. The orchestrate and handoff skills — also cooperative (implement the continuation protocol) — would not receive the abort-and-record cross-reference. This creates an incomplete framework: a `/handoff --commit` or `/orchestrate` in a chain would silently lose continuation state on error.
   - Fix: Expanded Step 4.2 to cover all four cooperative skills. Updated objective, prerequisite, script evaluation note, expected outcome, error conditions, and validation commands to include orchestrate/SKILL.md and handoff/SKILL.md.
   - **Status**: FIXED

### Minor Issues

1. **Step 4.2 — Script evaluation count ("2 files") understated**
   - Location: Step 4.2, Script Evaluation field
   - Problem: Pre-fix said "~5 lines added to each of 2 files." Post-fix is 4 files.
   - Fix: Updated to "~5 lines added to each of 4 files" as part of the major issue fix above.
   - **Status**: FIXED

## Fixes Applied

- Step 4.2 — Expanded scope from 2 to 4 cooperative skills (design, runbook, orchestrate, handoff). Updated: objective, script evaluation, prerequisite, expected outcome, error conditions, and all four validation grep commands.

## LLM Failure Modes — All Clear

- **Vacuity**: No vacuous steps. Step 5.2 (See Also) is lightweight but functionally distinct (navigation enablement). Step 5.3 (consistency review) is a distinct verification pass.
- **Dependency ordering**: Phase dependencies correctly specified. Within each phase, foundation-before-behavior ordering holds. Phase 4 dependency on both Phase 2 (escalation-acceptance.md) and Phase 3 (task-failure-lifecycle.md) explicitly documented.
- **Density**: Adjacent steps serve distinct behavioral concerns throughout. Steps 5.2 and 5.3 are not collapsible without losing the additive-vs-verification distinction.
- **Checkpoint spacing**: 5 phases with clear phase-boundary demarcation. The orchestrate skill's automated phase-boundary checkpoint mechanism handles checkpoint insertion at runtime — no explicit runbook checkpoints needed.
- **File growth**: Step 1.2 targets a 131-line file; estimated addition ~40-60 lines → well under 350-line threshold.

## File Reference Validation — All Clear

All prerequisite paths verified present:
- `agent-core/fragments/error-handling.md` — exists
- `agent-core/fragments/error-classification.md` — exists
- `agent-core/fragments/continuation-passing.md` — exists
- `agent-core/fragments/prerequisite-validation.md` — exists
- `agent-core/skills/orchestrate/SKILL.md` — exists
- `agent-core/skills/handoff/SKILL.md` — exists
- `agent-core/skills/design/SKILL.md` — exists
- `agent-core/skills/runbook/SKILL.md` — exists

New files (escalation-acceptance.md, task-failure-lifecycle.md) correctly identified as not-yet-existing in the Prerequisites section.

## Metadata Accuracy

- Total Steps: 11 — matches actual step count (1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2, 5.1, 5.2, 5.3). Correct.
- Execution Model: Opus for all steps — all targets are fragments or skills (artifact-type override). Correct.
- Step Dependencies: correctly documents Phase 2 ∥ Phase 3 parallelism, Phase 4's dual dependency, and Phase 5's full-chain dependency.

## Step Quality Assessment

All steps have: Objective, Script Evaluation, Execution Model, Prerequisite, Implementation, Expected Outcome, Error Conditions, Validation. Structure complete throughout.

No deferred decisions found. All design choices (D-1 through D-6, Q1) are pre-resolved in Common Context with explicit references.

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
