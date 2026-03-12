# Deliverable Review: recall-gate

**Date:** 2026-03-12
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Agentic prose | `agent-core/skills/runbook/SKILL.md` | 18 | 8 |
| Agentic prose | `agent-core/skills/inline/SKILL.md` | 20 | 11 |
| Learning | `agents/learnings.md` | 5 | 0 |

Design conformance: All three in-scope gates (runbook Tier 1, runbook Tier 2, inline Phase 2.3) rewritten. Learning entry appended. No missing deliverables. No unspecified deliverables.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**M1: Naming inconsistency with Tier 3 reference** — `agent-core/skills/runbook/references/tier3-planning-process.md:22` still uses "mandatory tool call on both paths" phrasing. The rewritten gates use "tool call required." Internal naming inconsistency within the runbook skill. Low risk — Tier 3 planning process is a different gate (augmentation, not consumption), but the stale phrasing could reinforce the old mental model.

**M2: Review dispatch template retains artifact-first branching** — `agent-core/skills/inline/references/review-dispatch-template.md:25-27` uses "Read this file. If absent: Read memory-index.md" — the same structural pattern the brief identifies as problematic. This is a review recall gate (not implementation recall), technically out of brief scope, but the structural vulnerability is identical.

## Gap Analysis

| Brief requirement | Status | Reference |
|---|---|---|
| Reframe gate: memory-index is constant, artifact is additive | Covered | runbook/SKILL.md:121, inline/SKILL.md:70-71 |
| Add implementation-scope signal | Covered | "patterns for building this, not classifying it" in all three gates |
| Preserve D+B anchor | Covered | "tool call required" + null no-op in step 4 |
| Upstream triage disclaimer | Covered | "Upstream triage recall (from /design) uses different triggers and does not satisfy this gate" |

## Summary

- Critical: 0
- Major: 0
- Minor: 2

The three rewritten gates are structurally consistent with each other and address all brief requirements. The scope signal ("patterns for building, not classifying") is clear and present in all gates. Minor findings are naming/structural echoes of the old pattern in adjacent reference files outside the brief's explicit scope.
