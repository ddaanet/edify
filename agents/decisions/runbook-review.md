# Runbook Review

Pre-execution review of TDD runbook outlines and expanded runbooks. Catches structural defects that cause execution failures, wasted cycles, and regression cascades.

Complements `deliverable-review.md` (post-execution artifact review).

## .Review Axes

### When Detecting Vacuous Tdd Cycles

Cycles where RED tests don't constrain implementation. Haiku satisfies them with degenerate GREEN (structurally correct, behaviorally meaningless).

**Detection — a cycle is vacuous when any of:**
- RED can be satisfied by `import X; assert callable(X)` or structural assertion
- GREEN adds ≤3 lines of non-branching code (no conditional, no state transformation)
- Cycle tests integration wiring (A calls B) rather than behavior (given X, observe Y)
- Cycle tests presentation format (output shape) rather than semantic correctness

**Action:** Eliminate, or merge into the nearest behavioral cycle as an assertion within that cycle's RED phase.

**Grounding:** LLMs produce "syntactically correct but irrelevant" code at 13.6–31.7% rate ("wrong logical direction"), scaling inversely with model size. Vacuous RED tests cannot detect this failure mode. ([Jiang et al., 2024](https://arxiv.org/html/2406.08731v1))

### When Ordering Runbook Dependencies

Cycles that reference structures not yet created. The executing model must either create them ad-hoc (scope creep) or mock them (implementation coupling). Both produce fragile GREEN implementations that break in later cycles.

**Detection — a dependency ordering problem exists when:**
- Cycle N tests behavior depending on structure created in cycle N+k (k>0)
- Cycle N's GREEN must assume a data shape that a later cycle establishes
- Refactoring in a later cycle invalidates GREEN from an earlier cycle

**Action:** Reorder to foundation-first: existence → structure → behavior → refinement. Each cycle's GREEN should build on the last without forward references.

**Grounding:** WebApp1K error taxonomy identifies "API Call Mismatch" (Type C) and "Scope Violation" (Type F) as direct consequences of executing against structures that don't match expected state. Non-reasoning models default to pretraining patterns when spec contradicts expectations. ([Fan et al., 2025](https://arxiv.org/html/2505.09027v1))

### When Evaluating Cycle Density

Unnecessary cycles that dilute expansion quality and increase execution context pressure. Every cycle adds prompt length during both expansion (planner attention budget) and execution (haiku context window).

**Detection — cycles should collapse when:**
- Two adjacent cycles test the same function with <1 branch point difference
- A cycle tests a single edge case expressible as a parametrized test row in the prior cycle
- A cycle exists solely for formatting/presentation separable from behavior
- An entire phase has ≤3 cycles, all Low complexity, on a function that already exists

**Action:** Collapse into nearest behavioral cycle. For edge-case clusters, use single cycle with parametrized test description.

**Grounding:** "Instruction loss in long prompts" — fidelity degrades as prompt grows. Remediation loops improve results only when tests encode meaningful requirements; trivial tests don't contribute signal. ([Mathews & Nagappan, 2024](https://arxiv.org/abs/2402.13521); [Fan et al., 2025](https://arxiv.org/html/2505.09027v1))

### When Spacing Runbook Checkpoints

Distance between quality gates. Without intermediate checkpoints, haiku drift accumulates across phases — pretraining bias overrides spec, and errors compound.

**Detection:** Count cycles between explicit checkpoints. Flag gaps >10 cycles or >2 phases without a checkpoint.

**Action:** Add checkpoints after phases that involve:
- Complex data manipulation (JSON, parsing, conflict resolution)
- Integration points (phase that composes functions from prior phases)
- High cycle count (≥8 cycles in single phase)

**Grounding:** "Non-reasoning models understand semantics and write functioning code, but fail expectations" — functional code that violates spec. Checkpoints are the remediation loop. ([Fan et al., 2025](https://arxiv.org/html/2505.09027v1))

## .Process

1. Read runbook outline (phase structure, cycle descriptions, dependency declarations)
2. For each cycle, evaluate against vacuity and dependency ordering axes
3. For each phase, evaluate cycle density and identify collapse candidates
4. Check checkpoint spacing across full runbook
5. Classify findings: High (dependency ordering — causes regression), Medium (vacuity/density — wastes budget), Low (checkpoint gaps — drift risk)

## .Sources

- [Jiang et al., 2024 — Where Do LLMs Fail When Generating Code?](https://arxiv.org/html/2406.08731v1) — Error taxonomy, meaningless code failure type, model-size scaling
- [Fan et al., 2025 — Tests as Prompt: WebApp1K](https://arxiv.org/html/2505.09027v1) — Instruction loss, pretraining bias, dependency ordering errors
- [Mathews & Nagappan, ASE 2024 — TDD for Code Generation](https://arxiv.org/abs/2402.13521) — TDD effectiveness, remediation loop value, edge-case persistence
- [Microsoft, 2025 — Taxonomy of Failure Modes in Agentic AI](https://www.microsoft.com/en-us/security/blog/2025/04/24/new-whitepaper-outlines-the-taxonomy-of-failure-modes-in-ai-agents/) — Task decomposition and sequencing failures
