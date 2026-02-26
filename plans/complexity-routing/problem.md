# Complexity Classification and Task Routing — Grounding Needed

## Problem

The `/design` and `/runbook` skills conflate *what kind of code* (behavioral vs prose) with *what kind of work* (production vs exploration vs investigation). This causes prototype scripts, spikes, one-off analysis tools, and migration helpers to be routed through production TDD ceremony.

## Evidence

Session-scraping prototype (C-3: "standalone prototype first") was classified Complex (correct — data model decisions needed), design resolved all complexity, then behavioral-code gate routed to `/runbook` which assessed Tier 3 (~20 TDD cycles, multi-session). User interrupted: "that was supposed to be a quick prototype."

## Current Model

**Classification (design skill Phase 0):** Stacey Matrix — implementation certainty × requirement stability → Simple/Moderate/Complex/Defect.

**Execution-readiness (design skill Phase B):** Binary — prose edits → execute directly, behavioral code → `/runbook`.

**Tier assessment (runbook skill):** File count, cycle count, session span → Tier 1/2/3. Assumes production conventions (test files, lint gates, module splitting).

## Gaps Identified

1. **No exploration/prototype work type.** The vocabulary is Simple/Moderate/Complex/Defect. No: Prototype, Spike, Exploration, One-off. C-3-style constraints don't map to any pipeline concept.

2. **Behavioral code always routes to /runbook.** The design skill's sufficiency gate has no path for "behavioral code that doesn't need planning ceremony." A resolved design for a single prototype script gets the same routing as a multi-module production feature.

3. **Tier assessment ignores artifact destination.** `/runbook` counts files against production conventions regardless of whether target is `src/` (production, needs tests) or `plans/prototypes/` (exploration, no tests).

4. **Complexity resolved but routing not reassessed.** Design resolves architectural uncertainty, but routing decisions at the sufficiency gate use static criteria rather than post-resolution state.

## Grounding Questions

- What dimensions should complexity classification use beyond implementation certainty × requirement stability?
- How do established frameworks (Cynefin, Boehm spiral, XP spikes, Lean build-measure-learn) handle exploratory work?
- What routing decisions should change based on artifact destination (production module vs prototype vs one-off)?
- Where should fix points land — triage (Phase 0), sufficiency gate (Phase B), tier assessment (/runbook), or a new pre-routing gate?

## Scope

Ground the classification + routing model. Don't redesign `/design` or `/runbook` skills wholesale — they are consumers of the model. Grounded model produces revised taxonomy and routing rules; skill edits are execution of those rules (moderate complexity).

## Related Learnings

- "When redesigning a process skill" — ground against external frameworks first
- "When companion tasks bundled into /design invocation" — same root cause class (procedural momentum overriding contextual judgment), opposite direction (skipped process vs over-applied process)
