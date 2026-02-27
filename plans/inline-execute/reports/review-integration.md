# Review: Pipeline Integration (inline-execute plan)

**Scope**: Uncommitted changes across 5 files: `agent-core/skills/runbook/SKILL.md`, `agents/decisions/pipeline-contracts.md`, `agents/memory-index.md`, `agent-core/skills/memory-index/SKILL.md`, `agent-core/fragments/continuation-passing.md`
**Date**: 2026-02-27
**Mode**: review + fix

## Summary

Pipeline integration replaces runbook Tier 1/2 execution sequences with `/inline` invocations, adds T6.5 transformation row and 3 decision sections to pipeline-contracts.md, syncs memory-index entries, and adds /inline to the continuation-passing cooperative skills table. Three issues found: missing memory-index SKILL.md sync entries, broken heading convention preventing `when-resolve.py` resolution, and stale cooperative skills count.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

1. **memory-index SKILL.md missing 3 new pipeline-contracts entries**
   - Location: `agent-core/skills/memory-index/SKILL.md:173`
   - Problem: The sync comment (`<!-- Synced from agents/memory-index.md -->`) requires both files to stay in sync. Three new entries added to `agents/memory-index.md` (lines 257-259) were not replicated to the SKILL.md copy. Sub-agents using the SKILL.md index cannot discover `/when using inline execution lifecycle`, `/how dispatch corrector from inline skill`, or `/when triage feedback shows divergence`.
   - Fix: Add the 3 entries to the pipeline-contracts.md section in SKILL.md.
   - **Status**: FIXED

### Major Issues

1. **`/how dispatch corrector` heading missing "To" — when-resolve.py fails**
   - Location: `agents/decisions/pipeline-contracts.md:352`
   - Problem: Heading `### How Dispatch Corrector From Inline Skill` missing "To". The resolver transforms `/how X` to heading `How To X`. Existing `/how` heading in same file is `## How To Review Delegation Scope Template`. Resolution fails: "Section not found: How to Dispatch Corrector From Inline Skill".
   - Fix: Change heading to `### How To Dispatch Corrector From Inline Skill`.
   - **Status**: FIXED

### Minor Issues

1. **Cooperative skills count stale after /inline addition**
   - Location: `agent-core/fragments/continuation-passing.md:80`
   - Problem: Text says "Five cooperative skills" but the table now lists six (/design, /runbook, /inline, /orchestrate, /handoff, /commit).
   - Fix: Change "Five" to "Six".
   - **Status**: FIXED

## Fixes Applied

- `agent-core/skills/memory-index/SKILL.md:173` — Added 3 missing entries (`/when using inline execution lifecycle`, `/how dispatch corrector from inline skill`, `/when triage feedback shows divergence`) after the existing pipeline-contracts.md section entries, matching `agents/memory-index.md`.
- `agents/decisions/pipeline-contracts.md:352` — Changed heading from `### How Dispatch Corrector From Inline Skill` to `### How To Dispatch Corrector From Inline Skill`. Verified resolution succeeds post-fix.
- `agent-core/fragments/continuation-passing.md:80` — Changed "Five cooperative skills" to "Six cooperative skills".

## Verification Criteria

| Criterion | Result |
|-----------|--------|
| 1. Runbook Tier 1/2 criteria sections unchanged | PASS — Criteria blocks (lines 109-115, 127-131) identical to pre-change |
| 2. Runbook Tier 3 section completely unchanged | PASS — No diff in Tier 3 section or Planning Process |
| 3. Runbook recall context sections preserved | PASS — Both Tier 1 (lines 116-120) and Tier 2 (lines 132-136) recall sections identical |
| 4. Runbook design constraints and escalation handling preserved | PASS — Lines 140-157 (constraints, model override, key distinction, escalations) identical |
| 5. T6.5 row format consistent with T1-T6 | PASS — Same column structure, appropriate content per column |
| 6. Memory-index entries follow naming conventions | PASS — Activity-at-decision-point naming, no article issues, trigger keywords aligned |
| 7. Continuation-passing table row matches /inline frontmatter | PASS — default-exit `["/handoff --commit", "/commit"]` matches SKILL.md frontmatter |
| 8. All enumeration sites for T1-T6 updated to T1-T6.5 | PASS — `agents/memory-index.md:229`, `agent-core/skills/memory-index/SKILL.md:165` both updated. One remaining "T1-T6" in `plans/orchestrate-evolution/recall-artifact.md:68` is a different plan's recall artifact (out of scope). |

## Positive Observations

- Runbook SKILL.md changes are surgical: only the execution sequence paragraphs replaced, all assessment criteria and supporting sections preserved intact.
- T6.5 row correctly identifies `classification.md` as an input (triage feedback reads it) and `review report` as an additional output (corrector produces it).
- Continuation-passing table insertion maintains alphabetical/pipeline order (design, runbook, inline, orchestrate) and adds "(Tier 1/2)" and "(Tier 3)" annotations that clarify the tier relationship.
- Pipeline-contracts decision sections follow the existing pattern: parent `##` with `###` subsections for related sub-decisions.
- Memory-index entries include descriptive trigger keywords consistent with neighboring entries.
