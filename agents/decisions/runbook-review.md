# Runbook Review

Pre-execution review of runbook outlines and expanded runbooks. Catches structural defects that cause execution failures, wasted items, and regression cascades.

Complements `deliverable-review.md` (post-execution artifact review).

## .Review Axes

### When Detecting Vacuous Items

Items where RED tests don't constrain implementation (TDD) or steps produce no functional outcome (general). Haiku satisfies them with degenerate output — structurally correct, behaviorally meaningless.

**TDD:**
- RED can be satisfied by `import X; assert callable(X)` or structural assertion
- GREEN adds ≤3 lines of non-branching code (no conditional, no state transformation)
- Cycle tests integration wiring (A calls B) rather than behavior (given X, observe Y)
- Cycle tests presentation format (output shape) rather than semantic correctness

**General:**
- Step creates scaffolding (empty class, stub file, directory structure) without functional outcome
- Step N+1 produces outcome achievable by extending step N alone → merge
- Consecutive steps modify same artifact with composable changes

**Behavioral vacuity detection:**
- **TDD:** For each cycle pair (N, N+1) on the same function, verify N+1's RED assertion would fail given N's GREEN implementation. If not, cycles are behaviorally vacuous — N+1 adds no constraint beyond N.
- **General:** For consecutive steps modifying the same artifact, verify step N+1 produces an outcome not achievable by extending step N's implementation alone. If achievable, steps should be merged.
- **Heuristic (both types):** items > LOC/20 signals consolidation needed — item count exceeds the behavioral surface area of the code.

**Action:** Eliminate, or merge into the nearest behavioral item.

**Grounding:** LLMs produce "syntactically correct but irrelevant" code at 13.6–31.7% rate ("wrong logical direction"), scaling inversely with model size. Vacuous RED tests cannot detect this failure mode. ([Jiang et al., 2024](https://arxiv.org/html/2406.08731v1))

### When Ordering Runbook Dependencies

Items that reference structures not yet created. The executing model must either create them ad-hoc (scope creep) or mock them (implementation coupling). Both produce fragile implementations that break in later items.

**TDD:**
- Cycle N tests behavior depending on structure created in cycle N+k (k>0)
- Cycle N's GREEN must assume a data shape that a later cycle establishes
- Refactoring in a later cycle invalidates GREEN from an earlier cycle

**General:**
- Step references output not yet produced by a prior step
- Step assumes file state from a future step

**Action:** Reorder to foundation-first: existence → structure → behavior → refinement. Each item should build on the last without forward references.

**Grounding:** WebApp1K error taxonomy identifies "API Call Mismatch" (Type C) and "Scope Violation" (Type F) as direct consequences of executing against structures that don't match expected state. Non-reasoning models default to pretraining patterns when spec contradicts expectations. ([Fan et al., 2025](https://arxiv.org/html/2505.09027v1))

### When Evaluating Item Density

Unnecessary items that dilute expansion quality and increase execution context pressure. Every item adds prompt length during both expansion (planner attention budget) and execution (context window).

**TDD:**
- Two adjacent cycles test the same function and differ by only a single branch point
- A cycle tests a single edge case expressible as a parametrized test row in the prior cycle
- A cycle exists solely for formatting/presentation separable from behavior
- An entire phase has ≤3 cycles, all Low complexity, on a function that already exists

**General:**
- Adjacent steps modifying same file with composable changes
- Single-line config changes expressible as part of an adjacent step
- An entire phase has ≤3 steps, all trivial edits

**Action:** Collapse into nearest behavioral item. For edge-case clusters, use single item with parametrized test description (TDD) or combined edit list (general).

**Grounding:** "Instruction loss in long prompts" — fidelity degrades as prompt grows. Remediation loops improve results only when tests encode meaningful requirements; trivial tests don't contribute signal. ([Mathews & Nagappan, 2024](https://arxiv.org/abs/2402.13521); [Fan et al., 2025](https://arxiv.org/html/2505.09027v1))

### When Spacing Runbook Checkpoints

Distance between quality gates. Without intermediate checkpoints, haiku drift accumulates across phases — pretraining bias overrides spec, and errors compound.

**TDD:**
- Count cycles between explicit checkpoints
- Flag gaps >10 cycles or >2 phases without a checkpoint
- Flag phases with ≥8 cycles and no checkpoint

**General:**
- Count steps between explicit checkpoints
- Flag gaps >10 steps or >2 phases without a checkpoint
- Flag phases with ≥8 steps and no checkpoint

**Action:** Add checkpoints after phases that involve:
- Complex data manipulation (JSON, parsing, conflict resolution)
- Integration points (phase that composes functions from prior phases)
- High item count (≥8 items in single phase)

**Grounding:** "Non-reasoning models understand semantics and write functioning code, but fail expectations" — functional code that violates spec. Checkpoints are the remediation loop. ([Fan et al., 2025](https://arxiv.org/html/2505.09027v1))

### When Planning For File Growth

Growth projection prevents refactor escalations from line-limit violations discovered mid-execution.

**TDD:**
- Estimate lines added per cycle from RED/GREEN descriptions
- Project cumulative file size at phase boundaries
- Flag when projected size exceeds 350 lines (400-line enforcement threshold minus buffer)

**General:**
- Estimate lines added per step from step descriptions
- Flag steps adding substantial content to files already near limit
- Flag outlines with >10 items modifying same file but no growth projection

**Action:** Insert proactive file split at phase boundary before projected threshold breach, with split point documented in outline.

**Evidence:** 7+ refactor escalations, >1hr wall-clock on line-limit fixes alone across worktree-update runbook.

## .Process

1. Read runbook outline (phase structure, item descriptions, dependency declarations). Identify phase types (TDD or general) — apply type-appropriate criteria in subsequent steps.
2. For each item (cycle or step), evaluate against vacuity and dependency ordering axes. Apply behavioral vacuity detection for consecutive items on the same target.
3. For each phase, evaluate item (cycle or step) density and identify collapse candidates.
4. Check checkpoint spacing across full runbook — count items (cycles or steps) between quality gates.
5. Project file growth per phase, flag threshold breaches.
6. Classify findings: High (dependency ordering — causes regression), Medium (vacuity/density/growth — wastes budget), Low (checkpoint gaps — drift risk).

## .Sources

- [Jiang et al., 2024 — Where Do LLMs Fail When Generating Code?](https://arxiv.org/html/2406.08731v1) — Error taxonomy, meaningless code failure type, model-size scaling
- [Fan et al., 2025 — Tests as Prompt: WebApp1K](https://arxiv.org/html/2505.09027v1) — Instruction loss, pretraining bias, dependency ordering errors
- [Mathews & Nagappan, ASE 2024 — TDD for Code Generation](https://arxiv.org/abs/2402.13521) — TDD effectiveness, remediation loop value, edge-case persistence
- [Microsoft, 2025 — Taxonomy of Failure Modes in Agentic AI](https://www.microsoft.com/en-us/security/blog/2025/04/24/new-whitepaper-outlines-the-taxonomy-of-failure-modes-in-ai-agents/) — Task decomposition and sequencing failures
