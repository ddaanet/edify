# Deliverable Review: workflow-rca-fixes

**Date:** 2026-02-15
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | Lines |
|------|------|-------|
| Agentic prose | agent-core/agents/vet-fix-agent.md | 454 |
| Agentic prose | agent-core/agents/design-vet-agent.md | 386 |
| Agentic prose | agent-core/agents/outline-review-agent.md | 347 |
| Agentic prose | agent-core/agents/plan-reviewer.md | 182 |
| Agentic prose | agent-core/agents/refactor.md | 266 |
| Agentic prose | agent-core/agents/runbook-outline-review-agent.md | 523 |
| Agentic prose | agent-core/agents/vet-taxonomy.md | 62 |
| Agentic prose | agent-core/skills/design/SKILL.md | 367 |
| Agentic prose | agent-core/skills/error-handling/SKILL.md | 20 |
| Agentic prose | agent-core/skills/memory-index/SKILL.md | 290 |
| Agentic prose | agent-core/skills/orchestrate/SKILL.md | 462 |
| Agentic prose | agent-core/skills/project-conventions/SKILL.md | 39 |
| Agentic prose | agent-core/skills/review-plan/SKILL.md | 504 |
| Agentic prose | agent-core/skills/runbook/SKILL.md | 824 |
| Human docs | agent-core/fragments/vet-requirement.md | 135 |
| Human docs | agent-core/fragments/workflows-terminology.md | 37 |
| Human docs | agents/decisions/orchestration-execution.md | 224 |
| Human docs | agents/decisions/runbook-review.md | 122 |
| Human docs | agent-core/skills/runbook/references/general-patterns.md | 126 |
| Human docs | agent-core/skills/runbook/references/anti-patterns.md | 34 |
| Human docs | agent-core/skills/runbook/references/examples.md | 344 |

**Total:** 21 deliverables, 5,748 lines
**Design conformance:** All 20 FRs have corresponding deliverables. No missing deliverables.
**Unspecified deliverables:** `vet-taxonomy.md` (not in design table but supports FR-7). Acceptable — artifact supports a design requirement.
**Code changes on branch:** `src/claudeutils/` and `tests/` changes are from the when-recall plan (pre-existing on branch). Not workflow-rca-fixes deliverables. C-1 (no code changes) satisfied.

## Critical Findings

**1. FIXED — Non-existent agent reference `runbook-review-agent`**
- Source: deliverable-review-docs.md
- File: `agent-core/fragments/workflows-terminology.md:19`
- Design requirement: FR-16
- Fix: Changed to `plan-reviewer` (the actual review agent used in the workflow)

**2. FIXED — Memory-index skill drifted from canonical source**
- Source: deliverable-review-skills.md
- File: `agent-core/skills/memory-index/SKILL.md`
- Design requirement: FR-13
- 3 entries missing (`item-level escalation`, `local recovery`, `global replanning`), section ordering mismatched
- Fix: Replaced entire index content with canonical ordering from `agents/memory-index.md`

## Major Findings

**3. FIXED — FR-18 missing from outline-review-agent**
- Source: deliverable-review-agents.md
- File: `agent-core/agents/outline-review-agent.md`
- Root cause: Design Phase 3 narrowed FR-18 scope to vet-fix-agent only; requirements.md names 3 agents
- Fix: Added merge-don't-append rule to fix process

**4. FIXED — FR-18 missing from plan-reviewer**
- Source: deliverable-review-agents.md
- File: `agent-core/agents/plan-reviewer.md`
- Same root cause as #3
- Fix: Added merge-don't-append rule to fix process

**5. FIXED — Runbook References section omits general-patterns.md**
- Source: deliverable-review-skills.md
- File: `agent-core/skills/runbook/SKILL.md:806`
- Design requirement: FR-4
- Fix: Added `general-patterns.md` to References list

**6. FIXED — Ordering guidance cross-references patterns.md not general-patterns.md**
- Source: deliverable-review-skills.md
- File: `agent-core/skills/runbook/SKILL.md:719`
- Design requirement: FR-4
- Fix: Updated to reference both `patterns.md` (TDD) and `general-patterns.md` (general)

**7. FIXED — Design skill agent-name validation hardcoded directories**
- Source: deliverable-review-skills.md
- File: `agent-core/skills/design/SKILL.md:199`
- Design requirement: FR-19
- Fix: Added `.claude/plugins/*/agents/*.md` glob pattern

**8. FIXED — Constraints field not covered by enforcement paragraph**
- Source: deliverable-review-docs.md
- File: `agent-core/fragments/vet-requirement.md:93`
- Design requirement: FR-10
- Fix: Added "missing Constraints section" to enforcement checklist

**9. FIXED — Bare "refactor agent" without path**
- Source: deliverable-review-docs.md
- File: `agents/decisions/orchestration-execution.md:97`
- Design requirement: FR-17
- Fix: Changed to backtick-wrapped `` `refactor` `` with path

**10. NOT FIXED — No automated sync mechanism for memory-index skill**
- Source: deliverable-review-skills.md
- File: `agent-core/skills/memory-index/SKILL.md:35`
- The sync comment creates an implicit contract but no enforcement. Index content was manually synced as part of this review. A future precommit check or script would prevent drift.
- Status: DEFERRED — requires infrastructure (script or precommit hook), not a prose edit

## Minor Findings

**11. FIXED — refactor.md uses raw grep in examples**
- File: `agent-core/agents/refactor.md:136`
- Fix: Replaced bash grep blocks with Grep tool instructions

**12. FIXED — refactor.md uses python prefix on prepare-runbook.py**
- File: `agent-core/agents/refactor.md:152`
- Fix: Changed to direct invocation via shebang

**13. FIXED — runbook-outline-review-agent lacks skills: frontmatter**
- File: `agent-core/agents/runbook-outline-review-agent.md` frontmatter
- Fix: Added `skills: ["project-conventions"]`

**14. FIXED — Phase 0.95 density check uses TDD-specific language**
- File: `agent-core/skills/runbook/SKILL.md:345`
- Fix: Made type-agnostic ("same target with minimal delta" + type-specific thresholds)

**15. FIXED — Redundant vacuity bullet in review-plan Section 11.1**
- File: `agent-core/skills/review-plan/SKILL.md:277`
- Fix: Removed duplicate behavioral vacuity detection bullet

**16. FIXED — "4 gates" misnomer in vet-requirement.md**
- File: `agent-core/fragments/vet-requirement.md:117`
- Fix: Changed to "3 gates checked ... with conclusion"

**17. FIXED — Dot-prefix on h3 subsection**
- File: `agents/decisions/orchestration-execution.md:116`
- Fix: Changed `### .Implementation Deferral` to `### Implementation Deferral`

**18. NOT FIXED — orchestrate template "fail loudly" partially vague**
- File: `agent-core/skills/orchestrate/SKILL.md:161`
- Mechanized with specific STOP instruction. Remaining vagueness is acceptable for sonnet-class orchestrator.

**19-24. ACCEPTED (no fix needed):**
- m2 (project-conventions ~350 tokens): informational, within design target
- m3 (code-removal omitted): requirements-to-design gap, design is correct
- m5 (LOC delta threshold for prose): design limitation, threshold reasonable
- m7 (density heuristic rough for prose): heuristic, reasonable for sanity check
- m9 (anti-patterns section modest coverage): 6 entries cover key patterns
- m10 (examples use specific plan names): real plan names acceptable

## Gap Analysis

| Design Requirement | Status | Reference |
|----|--------|-----------|
| FR-1: Type-agnostic runbook-review.md | Covered | agents/decisions/runbook-review.md |
| FR-2: Review-plan Section 11 general detection | Covered | agent-core/skills/review-plan/SKILL.md |
| FR-3: LLM failure mode gate Phase 0.95 | Covered | agent-core/skills/runbook/SKILL.md |
| FR-4: General-step reference material | Covered | references/general-patterns.md, anti-patterns.md, examples.md |
| FR-5: Outline growth validation | Covered | agent-core/agents/runbook-outline-review-agent.md |
| FR-6: Delete Phase 1.4 | Covered | agent-core/skills/runbook/SKILL.md |
| FR-7: Vet status taxonomy | Covered | vet-fix-agent.md, vet-taxonomy.md, vet-requirement.md |
| FR-8: Investigation-before-escalation | Covered | agent-core/agents/vet-fix-agent.md |
| FR-9: UNFIXABLE validation | Covered | agent-core/fragments/vet-requirement.md |
| FR-10: Orchestrate template enforcement | Covered | agent-core/skills/orchestrate/SKILL.md |
| FR-11: Semantic propagation checklist | Covered | agent-core/agents/runbook-outline-review-agent.md |
| FR-12: Agent convention injection | Covered | 6 agents with skills: frontmatter |
| FR-13: Memory index injection | Covered | agent-core/skills/memory-index/SKILL.md |
| FR-14: Design density checkpoint | Covered | agent-core/skills/design/SKILL.md |
| FR-15: Repetition helper prescription | Covered | agent-core/skills/design/SKILL.md |
| FR-16: Deliverable review workflow step | Covered | agent-core/fragments/workflows-terminology.md |
| FR-17: Execution-to-planning feedback | Covered | agents/decisions/orchestration-execution.md |
| FR-18: Review-fix integration | Covered | vet-fix-agent.md, outline-review-agent.md, plan-reviewer.md |
| FR-19: Agent-name validation + late-addition | Covered | agent-core/skills/design/SKILL.md |
| FR-20: Design-vet cross-reference + mechanism | Covered | agent-core/agents/design-vet-agent.md |

## Summary

- **Critical:** 2 found, 2 fixed
- **Major:** 8 found, 7 fixed, 1 deferred (sync mechanism — infrastructure needed)
- **Minor:** 14 found, 7 fixed, 1 partially fixed, 6 accepted
- **All 20 FRs covered** — no missing deliverables

**Sub-reports:**
- `plans/workflow-rca-fixes/reports/deliverable-review-agents.md`
- `plans/workflow-rca-fixes/reports/deliverable-review-skills.md`
- `plans/workflow-rca-fixes/reports/deliverable-review-docs.md`
