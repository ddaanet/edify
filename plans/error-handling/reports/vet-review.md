# Vet Review: Error Handling Framework (Layers 0-5)

**Scope**: 9 changed files (7 modified, 2 new) implementing error handling framework across agent-core fragments and skills
**Date**: 2026-02-19
**Mode**: review + fix

## Summary

The error handling framework implements all 6 design decisions (D-1 through D-6) across 5 layers with clear separation of concerns. The layered architecture in error-handling.md ties the framework together effectively. Three consistency issues found in error-classification.md where pre-existing content wasn't updated to reflect the new 5-category taxonomy and tier-aware classification model. One integration gap where task-failure-lifecycle.md claimed execute-rule.md behavior that wasn't documented there.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

(none)

### Major Issues

1. **Escalation walkthrough contradicts tier-aware classification**
   - Location: `agent-core/fragments/error-classification.md:58-63`
   - Problem: The Phase 2 walkthrough example showed a haiku agent self-classifying ("Classifies: PREREQUISITE_FAILURE"), contradicting the new Tier-Aware Classification section (line 45) which says haiku agents report raw errors and the orchestrator classifies.
   - Suggestion: Update example to show haiku reporting raw error, orchestrator classifying.
   - **Status**: FIXED

2. **"Integration with Weak Orchestrator" section stale on category count and tier-awareness**
   - Location: `agent-core/fragments/error-classification.md:95-100`
   - Problem: "During Execution" section said "Agent classifies error into one of 4 categories" — stale on two counts: (a) taxonomy now has 5 categories, (b) haiku agents don't self-classify. Section heading also said "Haiku Detection" but content now covers all tiers.
   - Suggestion: Update count to 5, add tier-aware classification language, fix section heading.
   - **Status**: FIXED

3. **execute-rule.md MODE 2 didn't document skipping error-state tasks**
   - Location: `agent-core/fragments/execute-rule.md:86-87`
   - Problem: task-failure-lifecycle.md line 56 claimed "`#execute` skips blocked/failed/canceled tasks, picks first pending" but execute-rule.md MODE 2 only said "start first pending task" without mentioning the skip behavior. The behavioral claim existed in one fragment without being documented in the authoritative source.
   - Suggestion: Add skip behavior to MODE 2 description.
   - **Status**: FIXED

### Minor Issues

(none)

## Fixes Applied

- `agent-core/fragments/error-classification.md:58-63` -- Updated escalation walkthrough to show haiku reporting raw error instead of self-classifying; orchestrator now performs classification with retryable annotation
- `agent-core/fragments/error-classification.md:95` -- Changed section heading from "Haiku Detection" to "Agent Detection"
- `agent-core/fragments/error-classification.md:98-100` -- Updated to reflect 5 categories, tier-aware classification (sonnet/opus self-classify, haiku reports raw), and retryable/non-retryable output
- `agent-core/fragments/execute-rule.md:87` -- Added "Skips blocked, failed, and canceled tasks" to MODE 2 behavior description

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| All 5 error categories documented | Satisfied | error-classification.md taxonomy table: 5 rows (Prerequisite, Execution, Unexpected, Ambiguity, Inter-Agent Misalignment) |
| Fault/failure vocabulary (Avizenis FEF) | Satisfied | error-classification.md:9-11: Categories 1,4 = faults; 2,3,5 = failures |
| Retryable/non-retryable per category | Satisfied | error-classification.md:23-33: Table with retryable/non-retryable columns per category |
| Tier-aware classification | Satisfied | error-classification.md:42-47: Sonnet/Opus self-classify, haiku reports raw |
| Escalation acceptance criteria (D-3) | Satisfied | escalation-acceptance.md:6-8: precommit + clean tree + output validates |
| Rollback: revert to step start (D-5) | Satisfied | escalation-acceptance.md:24-31: Rollback protocol with git revert/checkout |
| Timeout: max_turns ~150 (Q1) | Satisfied | escalation-acceptance.md:43-54 and orchestrate/SKILL.md:203: max_turns 150 with calibration data |
| Task states: blocked/failed/canceled (D-2) | Satisfied | task-failure-lifecycle.md: 6-state model, transitions, persistence rules |
| CPS abort-and-record (D-1) | Satisfied | continuation-passing.md:81-91: Abort remaining, record in Blockers, 0 retries |
| Pivot transactions | Satisfied | continuation-passing.md:93-105: Table identifying 3 pivot points |
| Hook error protocol (D-6) | Satisfied | error-handling.md:31-41: Crash/timeout/invalid output table, non-fatal degraded mode |
| Cross-system framework table | Satisfied | error-handling.md:15-23: Layer 0-4 table linking all fragments |
| D-4 fragment allocation | Satisfied | Implicit in file structure: new fragments (escalation-acceptance.md, task-failure-lifecycle.md) for new subsystems; extensions for existing |
| Cross-references correct | Satisfied | All fragment references verified: task-failure-lifecycle.md referenced from execute-rule.md, continuation-passing.md, handoff/SKILL.md, error-handling.md; escalation-acceptance.md referenced from orchestrate/SKILL.md, error-handling.md |
| Terminology consistent | Satisfied | "blocked/failed/canceled" used consistently across execute-rule.md, task-failure-lifecycle.md, handoff/SKILL.md, error-classification.md |

**Gaps:** None. All 6 design decisions addressed. Q1 timeout calibration data referenced.

---

## Positive Observations

- The layered architecture provides clear separation: each layer has a specific fragment, and the framework table in error-handling.md ties them together without duplicating content
- Pivot transaction analysis in continuation-passing.md is precise -- the three pivot points are correctly identified with actionable recovery guidance (forward, not backward)
- The Saga pattern simplification (D-5) is well-grounded: the assumption that all state is git-managed is explicitly called out with the failure mode (non-git state) documented
- Tier-aware classification preserves context locality (sonnet/opus classify at the point of error) while accommodating haiku's limitations
- error-handling.md remains focused: original behavioral rules untouched, framework content added as separate subsection
- The orphaned continuation recovery template in continuation-passing.md gives actionable resume context (chain, failure point, remaining, resume command)

## Deferred Items

The following items were identified but are out of scope:
- **pattern-weak-orchestrator.md says "4 categories"** -- OUT-OF-SCOPE: file not in changed files list, pre-existing content
