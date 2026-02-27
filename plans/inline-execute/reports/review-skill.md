# Review: /inline skill implementation

**Scope**: New files `agent-core/skills/inline/SKILL.md` and `agent-core/skills/inline/references/corrector-template.md` reviewed against design outline (`plans/inline-execute/outline.md`), requirements (`plans/inline-execute/requirements.md`), and continuation protocol (`agent-core/fragments/continuation-passing.md`).
**Date**: 2026-02-27
**Mode**: review + fix

## Summary

The /inline skill correctly implements the lifecycle phases (entry gate, pre-work, execute, post-work) with proper D+B anchoring, delegation protocol, and continuation frontmatter. The corrector template is well-structured with field rules, lightweight recall fallback, and a concrete example. Three issues require fixes: missing UNFIXABLE handling for corrector dispatch, Phase 4c not connecting to the continuation mechanism, and missing error propagation guidance per continuation-passing.md step 5.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Missing corrector UNFIXABLE handling in Phase 4a**
   - Location: `agent-core/skills/inline/SKILL.md:119-131`
   - Problem: Phase 4a delegates to corrector and mentions the report path, but does not specify what to do when corrector returns `UNFIXABLE: [description]`. Both /design (C.4) and /orchestrate (3.3 checkpoint) have explicit UNFIXABLE handling (stop + escalate). The corrector template itself says "Return filepath on success, or 'UNFIXABLE: [description]' on failure" — the caller must handle both return values.
   - Suggestion: Add UNFIXABLE handling after the corrector delegation bullet points: read report, if UNFIXABLE issues present, stop and surface to user.
   - **Status**: FIXED

2. **Phase 4c disconnected from continuation mechanism**
   - Location: `agent-core/skills/inline/SKILL.md:142-147`
   - Problem: Phase 4c says "State the pending deliverable-review task before continuing" and "Handoff captures this from conversation context." But it does not connect to the actual mechanism: the Continuation section's default-exit invokes `/handoff --commit` which is the handoff that captures the stated task. The outline (Phase 4c) says "invoke `/handoff [CONTINUATION: /commit]`" — the SKILL.md needs to make clear that Phase 4c is the last phase before continuation (which triggers the handoff).
   - Suggestion: Add a sentence connecting Phase 4c to the Continuation section as the final phase before default-exit.
   - **Status**: FIXED

### Minor Issues

1. **Continuation section omits error propagation**
   - Location: `agent-core/skills/inline/SKILL.md:161-169`
   - Note: The continuation-passing.md "Adding Continuation to a New Skill" step 5 says: "Add error handling: on failure, abort continuation and record in session.md Blockers." The SKILL.md's Continuation section follows the consumption protocol template verbatim but omits error propagation behavior. Other cooperative skills (orchestrate) reference error handling in their continuation sections. Adding a brief note keeps the skill aligned with the protocol spec.
   - **Status**: FIXED

2. **Continuation-passing.md Cooperative Skills table missing /inline entry**
   - Location: `agent-core/fragments/continuation-passing.md:67-74`
   - Note: The Cooperative Skills table lists /design, /runbook, /orchestrate, /handoff, /commit but not /inline. This is a new cooperative skill that should be added.
   - **Status**: OUT-OF-SCOPE — `continuation-passing.md` is not in the changed files for this review. Pipeline integration task covers this.

## Fixes Applied

- `agent-core/skills/inline/SKILL.md:127-131` — Added UNFIXABLE handling after corrector dispatch: read report, stop on UNFIXABLE issues, surface to user before proceeding
- `agent-core/skills/inline/SKILL.md:142-147` — Connected Phase 4c to continuation by noting it is the final phase before the Continuation section triggers default-exit
- `agent-core/skills/inline/SKILL.md:161-169` — Added error propagation note to Continuation section: on failure, abort continuation and record in session.md Blockers per continuation-passing.md

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-2 | Satisfied | Phase 2 (SKILL.md:54-80): task-context.sh, brief.md, recall-artifact resolution, lightweight fallback, reference loading |
| FR-3 | Satisfied | Phase 3 (SKILL.md:82-115): Tier 1 direct, Tier 2 delegated with all 7 delegation protocol aspects from outline |
| FR-4 | Satisfied | Phase 4a (SKILL.md:119-131) + references/corrector-template.md: standardized template, outline.md design context, recall context, lightweight fallback |
| FR-8 | Satisfied | Phase 4c (SKILL.md:142-147) + Continuation section: pending task stated, handoff captures via default-exit |
| D-1 | Satisfied | Entry Points table (SKILL.md:21-28): default and execute entry points, no CLI flags |
| D-4 | Satisfied | corrector-template.md:45: "Always `outline.md` or `design.md` -- never `requirements.md`" |
| D-5 | Satisfied | Phase 4c + Continuation default-exit: `/handoff --commit` → `/commit` with deliverable-review as pending task |
| D-6 | Satisfied | Structure matches spec (SKILL.md + references/corrector-template.md), continuation frontmatter correct, Skill in allowed-tools |
| NFR-1 | Satisfied | Execute entry point skips Phase 2 entirely (SKILL.md:56) |
| NFR-3 | Satisfied | Single corrector template in references/corrector-template.md (SKILL.md:121) |

**Gaps:** None. All in-scope requirements satisfied.

---

## Positive Observations

- D+B anchoring consistent: every phase opens with a tool call (bash commands for git state, when-resolve.py for recall, script invocation for triage feedback)
- Delegation Protocol Summary table (SKILL.md:149-159) is a concise reference that captures all 7 aspects from the outline without duplication
- Corrector template lightweight recall fallback entries are all verified in memory-index.md (5/5 resolve correctly)
- Progressive disclosure well-executed: SKILL.md body at 825 words stays lean, corrector template detail properly externalized to references/
- Frontmatter follows conventions: action verb description, trigger phrases, Skill in allowed-tools, cooperative continuation with correct default-exit

## Recommendations

- When /design and /runbook integration tasks execute (FR-9, FR-10), verify that the existing direct-execution sequences in /design Phase B (lines 330-333) and C.5 (line 426) are replaced with `/inline plans/<job> execute` invocations that match the entry point contract defined here
