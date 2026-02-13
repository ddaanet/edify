# Workflow Pipeline Redesign: Outline

Supersedes previous outline (gap patches) and previous iteration (G1-G7 within bifurcated architecture). Scope: unify /plan-tdd and /plan-adhoc into single /plan skill with per-phase type tagging.

## Problem

The design-to-deliverable pipeline has two parallel planning skills (/plan-tdd, /plan-adhoc) that share 75% of their structure. The bifurcation causes:

1. **Forced binary choice** — real work is mixed (behavioral code + infrastructure), but the planner must pick one mode upfront. TDD cycles get forced on non-behavioral work (skill definitions), adhoc steps get forced on behavioral work that should have tests.

2. **Duplicate maintenance** — tier assessment, outline generation, consolidation gates, complexity checks, assembly, checkpoints all duplicated verbatim. Bug fixes must be applied twice.

3. **Inconsistent review gates** — each path evolved independently. Adhoc routes to vet-fix-agent (rejects planning artifacts). TDD checks prescriptive code but not LLM failure modes. Neither path has unified criteria.

4. **Architectural gaps (G1-G7 from prior analysis)** — wrong agent routing, autofix contradictions, missing re-validation, dead-end recommendations, agent ambiguity, missing scope context, incomplete completion. Most trace to the bifurcation itself.

**Pipeline stages:** `/design` → `/plan` → `/orchestrate` → deliverable

## Approach: Unified /plan with Per-Phase Typing

**Core insight:** The step type (TDD cycle vs general task) is a property of each phase, not the runbook. A single runbook can have TDD phases for behavioral code and general phases for infrastructure.

**Per-phase type tagging:**
- Planner tags each phase: `type: tdd` or `type: general`
- Expansion guidance differs by phase type (cycle planning vs script evaluation)
- Review criteria adapt per-phase-type (TDD discipline on TDD phases, step quality on general phases)
- LLM failure mode checks (vacuity, ordering, density, checkpoints) apply universally regardless of type
- prepare-runbook.py already detects per-file (cycle headers vs step headers) — no changes needed
- Orchestrate handles both within one run (phase boundary detection already type-agnostic)

**What dissolves:**
- G1 (wrong agent routing) — single review path, no adhoc-specific routing
- G2 (autofix contradiction) — single fix-all pattern, no manual re-fix step
- G3 (missing LLM failure mode re-validation) — unified review criteria include failure modes for all phase types
- G4 (dead-end recommendations) — fix-all pattern: fix or escalate, no recommendations
- G5 (agent ambiguity) — single plan-reviewer agent, explicit everywhere
- G7 (orchestrate completion gap) — unified completion delegates to vet-fix-agent for both types

**What remains:**
- G6 (missing scope context) — still needs explicit scope IN/OUT in review delegations

## Key Decisions

### D1: Per-phase type granularity
**Decision:** Phase-level, not step-level or runbook-level.
- Per-runbook forces the binary choice (current problem)
- Per-step is over-granular — you wouldn't mix a TDD cycle and a general step in the same phase
- Per-phase matches how work naturally groups: "this phase tests behavior, that phase updates config"

### D2: Review agent architecture
**Decision:** Rename tdd-plan-reviewer → plan-reviewer, review-tdd-plan → review-plan. Clean names, no legacy aliases. v0.0 — no backward compatibility debt.

The plan-reviewer agent loads the review-plan skill. The skill has unified criteria: LLM failure modes for all phases, TDD discipline for TDD phases, step quality for general phases.

### D3: Recommendation propagation
**Decision:** Drop. Fix-all pattern: reviewer fixes directly, escalates UNFIXABLE. No recommendation dead-ends.

### D4: I/O contracts
**Decision:** Centralized in `agents/decisions/pipeline-contracts.md`. Each skill has brief Inputs/Outputs referencing the central doc. Transformation table from pipeline analysis becomes the authoritative contract spec.

### D5: LLM failure mode criteria location
**Decision:** In review-plan skill (unified with TDD/general criteria). The four axes (vacuity, ordering, density, checkpoints) apply to all phase types. TDD-specific checks (prescriptive code, RED/GREEN) are conditional sections.

## Unified /plan Skill Structure

Target: ~1200 lines (down from 2205 combined). Deduplication of 75% shared content.

**Shared sections (no branching):**
- Tier assessment and routing
- Outline generation and review (via runbook-outline-review-agent)
- Consolidation gate (outline level)
- Complexity check and fast-paths
- Outline sufficiency check (currently adhoc-only, applies to TDD too)
- File size planning
- Assembly and metadata (prepare-runbook.py invocation)
- Consolidation gate (runbook level)
- Checkpoints and validation
- Artifact preparation and handoff

**Per-phase-type sections (conditional on phase tag):**
- TDD: Cycle planning guidance (numbering, RED specs, GREEN hints, investigation prereqs, stop conditions, dependencies)
- General: Script evaluation (size classification, step types, conformance validation)

**Review delegation (unified, type-aware):**
- Per-phase: delegate to plan-reviewer with phase type + scope IN/OUT
- Holistic: delegate to plan-reviewer for cross-phase consistency
- LLM failure modes checked for ALL phase types
- TDD discipline (prescriptive code, RED/GREEN) checked for TDD phases only
- Step quality (prereqs, script eval, clarity) checked for general phases only

## Changes by Artifact

### New artifacts
- `agent-core/skills/plan/SKILL.md` — unified planning skill
- `agent-core/agents/plan-reviewer.md` — agent definition loading review-plan skill
- `agents/decisions/pipeline-contracts.md` — centralized I/O contracts

### Modified artifacts
- `agent-core/skills/review-tdd-plan/SKILL.md` → `review-plan/SKILL.md` — add general-phase criteria, LLM failure modes, rename
- `agent-core/skills/orchestrate/SKILL.md` — unified completion (vet-fix-agent for both types), remove type-specific branching at completion
- `agent-core/skills/design/SKILL.md` — route to `/plan` (not `/plan-tdd` or `/plan-adhoc`), add pipeline-contracts.md to Documentation Perimeter
- `CLAUDE.md` / `agent-core/fragments/workflows-terminology.md` — update workflow references to unified /plan
- `agent-core/agents/tdd-plan-reviewer.md` → `plan-reviewer.md` — rename, load review-plan skill
- `agent-core/agents/runbook-outline-review-agent.md` — no structural changes (outline review is already unified)
- `agent-core/skills/vet/SKILL.md` — add execution context section, UNFIXABLE guidance

### Deprecated artifacts (delete after unified skill validated)
- `agent-core/skills/plan-tdd/SKILL.md` (1052 lines)
- `agent-core/skills/plan-adhoc/SKILL.md` (1153 lines)

### Unchanged artifacts
- `agent-core/bin/prepare-runbook.py` — already handles both types via header detection
- `agent-core/agents/vet-fix-agent.md` — no changes needed (UNFIXABLE format already documented)
- `agent-core/agents/vet-agent.md` — unchanged

## Scope

**IN:**
- Unified /plan skill (merge plan-tdd + plan-adhoc with per-phase typing)
- Review skill rename and expansion (review-tdd-plan → review-plan, add general + LLM failure mode criteria)
- plan-reviewer agent definition
- Pipeline contracts decision doc
- Orchestrate unified completion
- Design skill routing update
- Workflow terminology updates (CLAUDE.md, fragments)
- Vet skill context guidance
- Deprecation of plan-tdd and plan-adhoc skills
- Symlink synchronization (just sync-to-parent)

**OUT:**
- prepare-runbook.py changes (already works)
- Skills prolog restructuring
- Plugin-dev upstream contributions
- worktree-update runbook fixes
- New agent types beyond plan-reviewer
- vet-fix-agent vs vet-agent duplication extraction (future optimization, not blocking unification)
- In-flight plan migration strategy (existing runbooks remain compatible via prepare-runbook.py detection)

## Resolved Questions

1. **Mixed-phase runbook format:** YAGNI. prepare-runbook.py already detects per-phase-file (cycle headers vs step headers). Mixed-phase runbooks work naturally — each phase file is typed independently. Document as edge case, no upfront implementation needed.

2. **Outline sufficiency shortcut for TDD:** Yes, apply to TDD outlines when <3 phases AND <10 cycles. Threshold documented in unified /plan skill.

## Mode

General workflow (not TDD). Modifies skill/agent definitions and planning artifacts. Downstream: `/plan-adhoc` (ironic, but this is the last adhoc runbook before unification) → execute with opus for architectural artifacts.
