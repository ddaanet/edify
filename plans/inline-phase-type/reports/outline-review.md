# Outline Review: inline-phase-type

**Artifact**: plans/inline-phase-type/outline.md
**Date**: 2026-02-19T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline is technically sound and architecturally well-grounded — the inline type fits cleanly within the existing type system, key decisions are explicit, and the phase-level vs job-level bypass distinction is clear. Before fixes, two requirements had partial coverage: FR-4 had an open Q-1 gap with no committed resolution, and FR-5 named review criteria by category label only without defining the actual checks. All issues have been fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Distinguish prose vs code (no/with feedback loop) | Problem Statement, D-6 | Complete | D-6 eligibility discriminator defines the split; Problem Statement provides motivation |
| FR-2: Third phase type ("inline") | Approach, D-1, Type System table | Complete | Type defined, annotated, and placed in type hierarchy |
| FR-3: Execution readiness gate routes all-prose to skip runbook | D-5, All-inline pipeline flow, Phase 1 | Complete | Gate replacement criteria specified; all-inline bypass flow shown |
| FR-4: prepare-runbook.py handles inline phases | D-3, Q-1 (resolved), Component Changes, Phase 3 | Complete (post-fix) | Q-1 now resolves mixed-runbook auto-detection; D-3 specifies `Execution: inline` marker format; Phase 3 enumerates all four code changes |
| FR-5: plan-reviewer has inline-specific review criteria | D-4, Type System table, Component Changes, Phase 2 | Complete (post-fix) | D-4 now enumerates apply/skip criteria explicitly; detection mechanism specified (`(type: inline)` tag) |

**Traceability Assessment**: All requirements covered after fixes.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **FR-4 partial — Q-1 unresolved**
   - Location: Open Questions section
   - Problem: Q-1 identified that `## Step` headers from general phases would contaminate inline phase classification in mixed runbooks, but committed to no resolution. Phase 3 just said "handle Q-1" without a concrete approach, leaving the implementer without a design.
   - Fix: Expanded Q-1 to a resolved state with three concrete steps: (a) add `'inline'` to `valid_types`, (b) detect inline phases by frontmatter in `validate_and_create()` and skip step-file generation, (c) emit `Execution: inline` in `assemble_phase_files()`. Phase 3 bullet updated to enumerate all four prepare-runbook.py changes.
   - **Status**: FIXED

2. **FR-5 partial — inline review criteria vague**
   - Location: D-4, Type System table, Component Changes
   - Problem: D-4 said "plan-reviewer checks inline phases for vacuity and density" without specifying what those checks mean for inline phases. Type System table said "Design conformance + LLM failure modes" — undefined term. Component Changes echoed "design conformance" without definition.
   - Fix: D-4 expanded with explicit apply/skip breakdown and detection mechanism. Type System table updated to name the specific checks. Component Changes updated to match. "Design conformance" term eliminated.
   - **Status**: FIXED

### Minor Issues

1. **D-7 orphaned from requirements**
   - Location: D-7 bullet
   - Problem: D-7 (phase boundary vet proportionality for inline phases) is part of the orchestrate/SKILL.md execution path but had no FR reference, making the requirements linkage implicit.
   - Fix: Added "(FR-4)" reference at end of D-7 — vet behavior in inline execution is part of the orchestrate execution path.
   - **Status**: FIXED

2. **Inline marker format missing from Architecture section**
   - Location: D-3, Component Changes (orchestrate/SKILL.md bullet)
   - Problem: D-3 said "orchestrator-plan.md marks inline phases" but not what the marker looks like. Implementer would have to invent the format. The orchestrate Component Change bullet was similarly silent.
   - Fix: D-3 updated to specify `Execution: inline` (vs `Execution: steps/step-N-M.md` for general phases). Component Changes already references D-3 implicitly; the format is now unambiguous.
   - **Status**: FIXED

3. **"Design conformance" undefined in Type System table**
   - Location: Type System table, Architecture section
   - Problem: "Design conformance" appeared in the Review column for inline type without definition. This term does not appear in pipeline-contracts.md or any exploration report.
   - Fix: Replaced with the concrete criteria: "Vacuity + density + dependency ordering (LLM failure modes; no step/script/TDD checks)".
   - **Status**: FIXED

4. **Implementation Plan phase bullets lacked specificity**
   - Location: Implementation Plan, Phases 1–3
   - Problem: Phase 1 bullets said "update pipeline-contracts.md with inline type, eligibility, updated contract" — correct but doesn't name which decisions drive each change. Phases 2 and 3 similarly listed targets without content. An implementer reading the runbook would need to re-derive what to write.
   - Fix: Each phase bullet now enumerates the specific changes and cross-references the design decisions (D-2, D-5, D-6, D-7, Q-1) that motivate them.
   - **Status**: FIXED

## Fixes Applied

- D-3 — Added `Execution: inline` marker format and contrast with `Execution: steps/step-N-M.md`
- D-4 — Expanded from one sentence to apply/skip breakdown with detection mechanism; added FR-5 tag
- D-7 — Added FR-4 reference
- Q-1 — Converted from open question to resolved with three concrete implementation steps; added FR-4 tag
- Type System table — Replaced "Design conformance + LLM failure modes" with specific checks
- Component Changes (plan-reviewer bullet) — Replaced "design conformance, LLM failure modes only" with explicit apply/skip criteria and detection method
- Phase 1 bullet — Added specific changes per decision
- Phase 2 bullet — Added specific changes with cross-references
- Phase 3 bullet — Added all four prepare-runbook.py changes

## Positive Observations

- Problem Statement is grounded in measured evidence (11 opus agents, 250 lines, regression introduced by generation process) — not abstract motivation.
- D-1 through D-7 structure is tight: each decision resolves a choice that could otherwise block implementation. No vague decisions.
- Pipeline flow diagrams per type make the execution path change immediately visible without prose.
- Scope Boundaries section correctly distinguishes what is and is not part of this design (no new tooling scripts, no TDD/general behavior changes) — prevents scope creep.
- Q-1 was correctly identified as the hardest implementation detail before the fix, showing the author traced the content-override mechanism in prepare-runbook.py accurately.
- "By this design's own discriminator, implementation is inline-eligible" at the end of the Implementation Plan is a strong self-consistency check.

## Recommendations

- **For discussion:** D-5 (execution readiness gate) replaces a simple metric (≤3 files) with a multi-factor discriminator. The discriminator is sound in principle but may need examples to guide planner judgment. Consider adding 1–2 examples to pipeline-contracts.md during Phase 1.
- **For Phase 2 review:** runbook/SKILL.md Phase 0.95 sufficiency thresholds currently have a TDD-specific hardcode (`<3 phases AND <10 cycles`). The outline notes this must be updated for inline but doesn't specify the equivalent threshold. The implementer should propose an inline threshold during Phase 2.
- **Parallel execution in mixed runbooks:** explore-decisions.md §Gaps notes that inline + tdd parallel phases have an unspecified interaction. The outline correctly marks this out-of-scope, but it may surface as a question during Phase 3 orchestrate changes.

---

**Ready for user presentation**: Yes
