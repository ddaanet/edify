# Design Outline: Inline Phase Type

## Problem Statement

The pipeline treats all phases uniformly: discrete agents with step files, regardless of work type. Prose edits — which have no implementation loop — get the same ceremony as TDD cycles with test gates.

Evidence: error-handling runbook used 11 opus agents for ~250 lines of additive prose. Each agent re-read target files, wrote a report, and returned — the delegation ceremony cost more tokens than the edits. The plan-reviewer caught a regression *introduced* by the runbook generation process (Step 4.2 dropped 2 of 4 skills that the outline correctly listed).

Two related gaps:
- **Phase-level:** No mechanism for simple phases within a complex runbook to skip agent delegation
- **Job-level:** Execution readiness gate uses ≤3 files heuristic, which is too conservative (7 files with independent additive changes and pre-resolved decisions can be simpler than 2 files with interleaving structural changes)

See `plans/inline-phase-type/reports/explore-phase-typing.md` for pipeline component analysis.
See `plans/inline-phase-type/reports/explore-decisions.md` for decision basis.

## Approach

Add `inline` as a third phase type alongside `tdd` and `general`. Inline phases are executed directly by the orchestrator — no agent delegation, no step files. Complement with execution readiness gate refinement for all-inline jobs.

The concept already exists informally: `workflow-planning.md` records "trivial phases get inline instructions" as a fast path. This design formalizes that pattern.

## Key Decisions

**D-1: Inline is a phase type, not an orthogonal execution mode flag.** One concept, one annotation (`type: inline`). The alternative (type + execution-mode as orthogonal dimensions) adds combinatorial complexity for the same discriminator.

**D-2: Type contract expanded.** The current contract (`pipeline-contracts.md`) explicitly says "Type does NOT affect orchestration." Inline affects how orchestration delegates — the orchestrator executes inline phases directly instead of dispatching to a Task agent. Update the contract: types can affect the delegation model (per-step agents, batch agent, or orchestrator-direct), not only expansion format and review criteria. The original narrowness was descriptive of two types, not prescriptive of all future types.

**D-3: Orchestrator-direct for inline phases; batching deferred.** prepare-runbook.py skips step-file generation for inline phases. The runbook phase content IS the execution instruction. orchestrator-plan.md marks inline phases with `Execution: inline` (vs `Execution: steps/step-N-M.md` for general phases) so the orchestrator reads the phase content from the runbook directly.

For all-inline runbooks: orchestrator-direct (opus orchestrator does the work). No sub-agent batching — there's no coordination context to protect from pollution.

For mixed runbooks (inline + general/TDD phases): batching consecutive inline phases into a single sub-agent may be beneficial (preserves orchestrator context for coordination). **This threshold is currently ungrounded.** Data needed: measured token cost of Task delegation roundtrip (baseline + common context + step + report cycle), observed context degradation from inline edits in mixed orchestration sessions. Decision deferred until empirical data collected. Until then, orchestrator-direct for all inline phases regardless of runbook composition.

**D-4: LLM failure mode checks still apply.** Review is lighter, not zero. plan-reviewer inline criteria:
- **Apply:** Vacuity (instruction must name concrete target and operation), density (outcome must be verifiable — not "update X" but "add Y to section Z of X"), dependency ordering (inline instructions within a phase must sequence correctly)
- **Skip:** Step quality checks (no steps), script evaluation (no scripts), prerequisite validation (orchestrator handles directly), RED/GREEN discipline (no test loop)
- **Detection:** plan-reviewer identifies inline phases by `(type: inline)` tag in phase heading, same convention as `(type: tdd)`. (FR-5)

**D-5: Execution readiness gate refinement.** Replace ≤3 files with coordination complexity discriminator. All of: decisions pre-resolved, changes additive, cross-file deps phase-ordered, content derivable from architecture section → design is execution-ready, skip runbook. File count is a proxy; the underlying property is "no implementation loops across any phase."

**D-6: Inline eligibility discriminator.** A phase qualifies as inline when: outcome fully determined by instruction + target file state. No runtime feedback loop (tests, scripts, external state). Prose edits, config additions, cross-reference insertions, mechanical content application.

**D-7: Phase boundary vet follows existing proportionality.** Inline phases still get phase-boundary checkpoints, but vet-requirement proportionality applies: ≤5 net lines across ≤2 files, additive → self-review (git diff + verification). Larger inline phases get vet delegation as normal. This rule is part of the orchestrate/SKILL.md inline execution path (FR-4).

## Open Questions

- **Q-1: Content auto-detection in prepare-runbook.py** (resolved). For mixed runbooks (inline + general phases), `## Step` headers from general phases would trigger the content-override and classify the whole runbook as `general`, losing `inline` markers. Resolution: extend the auto-detection to treat runbooks with any `inline`-tagged phase frontmatter as `mixed`, and add `'inline'` to the per-phase type passthrough so inline phases are not reclassified. Concretely: (a) add `'inline'` to `valid_types`; (b) in `validate_and_create()`, detect inline phases by frontmatter and skip step-file generation for them; (c) in `assemble_phase_files()`, mark inline phases in orchestrator-plan.md with `Execution: inline` rather than a step file reference. This leaves general-phase Step headers intact for their phases without contaminating inline phases. (FR-4)

## Scope Boundaries

**IN:**
- Type definition and eligibility criteria
- Type contract update (`pipeline-contracts.md`)
- Execution readiness gate refinement (`workflow-optimization.md`)
- 4 pipeline components: prepare-runbook.py, plan-reviewer, runbook skill, orchestrate skill

**OUT:**
- New baseline agent for inline (uses quiet-task.md when delegation is needed; orchestrator uses no baseline for inline phases)
- New tooling scripts
- Hook changes
- Changes to TDD or general type behavior

## Architecture

### Type System (updated)

| Type | Expansion | Review | Execution |
|------|-----------|--------|-----------|
| `tdd` | RED/GREEN cycles | TDD discipline + LLM failure modes | Agent delegation |
| `general` | Discrete steps | Step quality + LLM failure modes | Agent delegation |
| `inline` | Pass-through (no decomposition) | Vacuity + density + dependency ordering (LLM failure modes; no step/script/TDD checks) | Orchestrator direct (batching deferred — D-3) |

### Pipeline Flow Per Type

**TDD/General (unchanged):**
```
outline → /runbook expansion → plan-reviewer → prepare-runbook.py → step files → /orchestrate → Task agents
```

**Inline:**
```
outline → /runbook (pass-through) → plan-reviewer (lighter) → prepare-runbook.py (skip step gen) → /orchestrate → orchestrator reads runbook directly
```

**All-inline job (gate bypass):**
```
outline sufficiency gate → execution readiness gate → direct execution from outline → vet
```

### Component Changes

- **pipeline-contracts.md**: Add inline type. Update type contract to include orchestration. Add inline eligibility criteria.
- **workflow-optimization.md**: Replace ≤3 files gate with coordination complexity discriminator.
- **runbook/SKILL.md**: Add inline expansion path in Phase 1 (pass-through, no step decomposition). Update outline phase tagging examples.
- **plan-reviewer.md** + **review-plan/SKILL.md**: Add inline detection (by `(type: inline)` tag) and review criteria (vacuity, density, dependency ordering; skip step quality, script evaluation, prerequisite validation, RED/GREEN discipline).
- **orchestrate/SKILL.md**: Add inline execution path — orchestrator reads phase content from runbook, executes edits directly, runs validation. Phase boundary vet with proportionality. Batching deferred (D-3).
- **prepare-runbook.py**: Add 'inline' to valid_types. Skip step-file generation for inline phases. Mark inline phases in orchestrator-plan.md. Handle content auto-detection for mixed runbooks (Q-1).

### Affected Files

- `agents/decisions/pipeline-contracts.md`
- `agents/decisions/workflow-optimization.md`
- `agent-core/skills/runbook/SKILL.md`
- `agent-core/agents/plan-reviewer.md`
- `agent-core/skills/review-plan/SKILL.md`
- `agent-core/skills/orchestrate/SKILL.md`
- `agent-core/bin/prepare-runbook.py`

## Implementation Plan

### Phase 0: Data Collection (prerequisite for D-3 batching decision)
- Measure Task delegation token overhead from existing session data (baseline + common context + step + report cycle)
- Measure orchestrator context consumption per inline edit (file reads + edit reasoning)
- Analyze whether context degradation occurs in mixed orchestration sessions
- Output: grounded batching threshold or confirmation that orchestrator-direct suffices for all cases

### Phase 1: Type Definition + Contract (type: inline)
- Update `pipeline-contracts.md`: add inline type row to type table, eligibility criteria (D-6), updated type contract (D-2), inline marker format (`Execution: inline` in orchestrator-plan.md)
- Update `workflow-optimization.md`: replace ≤3 files heuristic with coordination complexity discriminator (D-5)

### Phase 2: Planning Pipeline (type: inline)
- Update `runbook/SKILL.md`: add inline expansion path (pass-through), update Phase 0.95 sufficiency thresholds to include inline, update runbook template to show `(type: inline)` phase heading
- Update `plan-reviewer.md` + `review-plan/SKILL.md`: add inline detection (by `(type: inline)` tag), inline review criteria (vacuity, density, dependency ordering — from D-4)

### Phase 3: Execution Pipeline (type: inline)
- Update `orchestrate/SKILL.md`: add inline execution path (read phase content from runbook, execute directly, apply vet proportionality per D-7). Batching deferred pending Phase 0 data.
- Update `prepare-runbook.py`: add `'inline'` to `valid_types`, skip step-file generation for inline phases, emit `Execution: inline` in orchestrator-plan.md, handle mixed runbook auto-detection per Q-1 resolution

### Phase 4: Validation — execute error-handling design inline
- Execute `plans/error-handling/outline.md` using inline execution model (orchestrator-direct from design outline)
- Serves as end-to-end test of the inline workflow
- Collects empirical data for Phase 0 batching analysis (token consumption, context quality)

All implementation phases are prose edits to existing artifacts. By this design's own discriminator, implementation is inline-eligible. Phase 4 validates the design by using it.
