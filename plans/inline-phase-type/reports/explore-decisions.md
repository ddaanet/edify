# Exploration: Decision Basis for Inline Phase Type

## Summary

The existing phase type system (`tdd` | `general`) is narrowly scoped: it controls only expansion format, review criteria, and LLM failure mode checks — not tier assessment, orchestration, or checkpoints. A separate but related mechanism already exists for bypassing the runbook pipeline entirely (`execution readiness gate`). An `inline` phase type would need to interact with both mechanisms without duplicating the bypass logic. Key constraints come from model selection rules (prose artifacts always require opus) and the strict phase-type contract defined in pipeline-contracts.md.

---

## Key Findings

### 1. Phase Type Declaration and Contract

**Source:** `/Users/david/code/claudeutils-wt/error-handling-design/agents/decisions/pipeline-contracts.md` lines 57–66

**Rule:**
> Runbook phases declare type: `tdd` or `general` (default: general).
>
> Type determines:
> - **Expansion format:** TDD cycles (RED/GREEN) vs general steps (script evaluation)
> - **Review criteria:** TDD discipline for TDD phases, step quality for general phases
> - **LLM failure modes:** Apply universally regardless of type
>
> Type does NOT affect: tier assessment, outline generation, consolidation gates, assembly, orchestration, checkpoints.

**Implications for `inline`:**
- The type system is intentionally narrow — it controls expansion and review, nothing else.
- An `inline` type would need to fit within this contract: a different expansion format (no step files, execute in-place) and different review criteria (no vet delegation for trivial changes).
- The explicit exclusion of "orchestration" from the type's scope creates a tension: inline execution *is* an orchestration-level concern. This may argue for implementing inline as an execution mode flag rather than a phase type.

---

### 2. Model Selection for Prose Artifact Edits

**Source:** `/Users/david/code/claudeutils-wt/error-handling-design/agents/decisions/pipeline-contracts.md` lines 162–176

**Rule:**
> Prose edits to skills, fragments, agent definitions, and architectural documents require opus. These artifacts are LLM-consumed instructions — wording directly determines downstream agent behavior.
>
> Classification:
> - Skills, fragments, agent definitions, design documents → opus
> - Code implementation, test writing, script edits → model by complexity (haiku/sonnet)
> - Mechanical execution (copy-paste, config changes) → haiku

**Implications for `inline`:**
- If `inline` phases target prose artifact edits (the primary motivation), model selection must still be opus for those steps — the model override cannot be relaxed.
- The `inline` type cannot reduce model tier requirements; it can only reduce orchestration ceremony (skipping step file generation, vet delegation, inter-step checkpoints).
- Haiku may be valid for inline phases when the content is mechanical (config changes, single-constant updates). The classification point during `/runbook` expansion still applies.

---

### 3. Execution Readiness Gate (Design Resolves to Simple Execution)

**Source:** `/Users/david/code/claudeutils-wt/error-handling-design/agents/decisions/workflow-optimization.md` lines 103–111

**Rule:**
> **Correct pattern:** Execution readiness gate inline at sufficiency gate. When design output is ≤3 files, prose/additive, insertion points identified, no cross-file coordination → direct execution with vet, skip `/runbook`.
>
> **Rationale:** Design can resolve complexity. A job correctly classified as Complex for design may produce Simple execution. The gate is subtractive (creates exit ramp), not additive (more ceremony).

**Implications for `inline`:**
- The execution readiness gate already handles the whole-job case: if the entire job is simple, skip runbook creation entirely.
- An `inline` phase type handles a different case: the job is complex enough to warrant a runbook, but individual phases within it are simple enough to skip step-file orchestration.
- These are complementary, not overlapping. The gate is a job-level bypass; `inline` would be a phase-level bypass within an otherwise-orchestrated runbook.
- Risk: if the readiness gate already catches all simple cases, the remaining cases needing `inline` may be smaller than expected.

---

### 4. Orchestration Tier Assessment

**Source:** `/Users/david/code/claudeutils-wt/error-handling-design/agents/decisions/workflow-core.md` lines 215–251

**Rule (three tiers):**
> - **Tier 1:** <6 files, straightforward edits → direct implementation + vet
> - **Tier 2:** 6-15 files, moderate scope → Task tool delegation, no full orchestration
> - **Tier 3:** Multiple independent steps, different models, long-running → full runbook + prepare-runbook.py + orchestrate

**Implications for `inline`:**
- Tier 1 and Tier 2 already provide escape routes for simple work. An `inline` phase type targets a specific gap: a Tier 3 runbook that contains a few phases that would individually qualify as Tier 1/2.
- Without `inline`, Tier 3 treatment forces even simple phases through step-file generation, quiet-task delegation, and orchestrator checkpoint ceremony.
- The tier assessment is done once at job level — there is no per-phase tier assessment. An `inline` phase type would introduce implicit per-phase tier reasoning into the expansion step.

---

### 5. Runbook Expansion and Review

**Source:** `/Users/david/code/claudeutils-wt/error-handling-design/agents/decisions/workflow-planning.md` lines 7–46

**Rule:**
> Generate holistic outline first, then expand phase-by-phase with review after each. (Iterative loop, not parallel generation.)

**Also:** `/Users/david/code/claudeutils-wt/error-handling-design/agents/decisions/pipeline-contracts.md` lines 116–128

**Rule:**
> LLM failure mode checks must run at BOTH outline AND expanded phase levels. Outline review catches issues, but phase expansion re-introduces them.

**Implications for `inline`:**
- Per-phase expansion with review is the enforced pattern. An `inline` phase would need a lighter review — but cannot skip LLM failure mode checks entirely (they apply universally, regardless of type).
- The review criteria for `inline` would differ from `general` (no plan-reviewer delegation, self-review sufficient if ≤5 lines) but would still need vacuity and density checks.
- Danger: making `inline` a type that skips review entirely would create a category that silently bypasses the defect-detection chain established after the Phase expansion regression (expanded phases re-introduced 3 vacuous cycles the outline review had fixed).

---

### 6. Complexity Checking Before Expansion

**Source:** `/Users/david/code/claudeutils-wt/error-handling-design/agents/decisions/workflow-planning.md` lines 128–142

**Rule:**
> Check complexity BEFORE expansion; callback to previous level if too large.
>
> Fast paths: Pattern cycles get template+variations; trivial phases get inline instructions.

**Implications for `inline`:**
- "Trivial phases get inline instructions" is already named as a fast path — this suggests the concept exists in the decision record but has not been formalized as a type.
- The callback chain (`step → outline → design → requirements`) does not mention `inline` as a resolution mode; it treats inline instructions as a planning-time optimization, not a runtime execution mode.
- Formalizing `inline` as a phase type would codify an already-recognized pattern.

---

## Patterns

- **Type narrowness is intentional.** The phase type system was deliberately scoped to expansion format and review criteria. Extending it to affect orchestration behavior requires explicitly relaxing the "Type does NOT affect orchestration" rule.
- **Bypasses exist at two levels, not three.** Job-level: execution readiness gate. Phase-level: no formal mechanism today (only informal "trivial phases get inline instructions"). An `inline` type would formalize the missing middle level.
- **Model selection is artifact-driven, not type-driven.** Even if a phase is `inline`, opus is still required for prose artifact edits. The type cannot override this.
- **Review cannot be skipped, only lightened.** The LLM failure mode check requirement is universal. An `inline` type gets lighter ceremony but not zero review.
- **Trivial phase merging is an alternative.** The existing pattern (merge trivial cycles with adjacent work at Gate 1/Gate 2) partially addresses the same problem `inline` would solve, at lower design cost.

---

## Gaps

- **No existing definition of what qualifies a phase as `inline`.** The thresholds implied by vet-requirement.md (≤5 lines, ≤2 files, additive, no behavioral change) could serve as phase eligibility criteria, but this has not been stated.
- **Unclear how prepare-runbook.py handles `inline` phases.** Step-file generation is the current mechanism; `inline` phases would need either a no-op step file or explicit skip logic in the script.
- **Review agent behavior for `inline` is unspecified.** plan-reviewer is type-aware (`tdd` vs `general`) but has no `inline` branch. Self-review (per vet-requirement.md proportionality) would apply, but this needs to be explicit.
- **Interaction with parallel phase execution is unspecified.** Phases 2+3 in some runbooks run concurrently. If one is `inline` and another is `tdd`, the orchestrator's parallelism logic is unaffected (type does not affect orchestration), but the inline phase's execution path inside the Task agent is different.
