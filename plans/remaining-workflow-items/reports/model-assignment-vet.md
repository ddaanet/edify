# Vet Review: Runbook skill model assignment logic

**Scope**: Model Assignment section and integration points in SKILL.md
**Date**: 2026-02-16
**Mode**: review + fix

## Summary

Changes add opus model assignment override for architectural artifacts across three integration points: new Model Assignment section, Tier 2 delegation guidance, and Weak Orchestrator Metadata template. Implementation correctly addresses the requirement that prose consumed by LLMs requires nuanced understanding.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Weak Orchestrator Metadata template missing general-phase context**
   - Location: Line 570-574 (Weak Orchestrator Metadata section)
   - Note: Template shows Execution Model using "Steps X-Y" notation but doesn't clarify this is for general phases only. TDD phases use "Cycle X.Y" numbering.
   - **Status**: FIXED

2. **Step template Execution Model field lacks guidance on when to use opus**
   - Location: Line 814
   - Note: Template shows `[Haiku / Sonnet / Opus]` options but doesn't reference Model Assignment section for artifact-type override decision
   - **Status**: FIXED

## Fixes Applied

- Line 570: Added clarifying note `(general phases only — TDD cycles use phase-level model)` to Execution Model header in Weak Orchestrator Metadata template
- Line 814: Added reference `— see Model Assignment for artifact-type override` to Execution Model field in Step template

## Positive Observations

- Model Assignment section is well-positioned (after Per-Phase Type Model, before When to Use) — natural discovery during planning
- Artifact-type override list is concrete and actionable (specific path patterns, not abstract categories)
- Rationale explains WHY haiku/sonnet insufficient ("wording directly determines downstream agent behavior")
- Integration complete across all three application points (Tier 2, Tier 3 steps, Weak Orchestrator Metadata)
- Override applies to model parameter in Task calls (Tier 2) and Execution Model field (Tier 3) — consistent terminology

## Recommendations

None. Changes satisfy requirements and integrate cleanly with existing structure.
