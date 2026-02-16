# Runbook Quality Gates

## Requirements

### Functional Requirements

**FR-1: Post-expansion simplification pass**
After Phase 1 expansion completes (all phase files written and per-phase reviewed), run a simplification pass that:
- Detects identical-pattern cycles eligible for parametrized consolidation (e.g., 4 cycles adding one artifact type each → 1 parametrized cycle)
- Detects independent functions in the same module that can batch into a single cycle (e.g., 3 git helper functions → 1-2 cycles)
- Detects sequential additions to the same output loop or data structure that can merge (e.g., 4 formatting lines → 2 cycles)
- Applies consolidation: rewrites affected phase files, renumbers cycles/steps, updates metadata

**Acceptance:** Given workwoods runbook (55 items pre-optimization), simplification pass produces ~43 items with correct renumbering and no stale cross-references.

**FR-2: Model selection review**
Review model tags across all phases against task complexity criteria:
- Safety-critical code edits (complex state, refactoring existing functions) → sonnet minimum
- Prose/skill/fragment edits → opus
- Synthesis tasks (writing summaries from multiple sources) → opus
- Mechanical identical-pattern work → haiku
- Simple file deletion/line removal → haiku

Flag mismatches and apply corrections.

**Acceptance:** Each general step has explicit Model tag. Each model tag matches complexity criteria. No sonnet assigned to synthesis or prose editing. No sonnet assigned to mechanical grep-and-delete.

**FR-3: Pre-execution file lifecycle validation**
Parse all phase files, extract every `File:` + `Action:` reference, build a create→modify dependency chain. Flag:
- Files modified before their creation cycle
- Files created in multiple cycles (conflicting creation)
- Cycles reading files from future phases
- Missing creation cycles for files referenced as "Existing file"

**Acceptance:** Validation runs on assembled phase files. All violations reported with phase:cycle location. Zero false positives on correctly ordered runbooks.

**FR-4: Pre-execution RED plausibility audit**
For each TDD cycle (especially parametrized/batched), verify the expected failure message is plausible given the GREEN implementations from all prior cycles. Flag:
- "Already-passing" RED states where a prior GREEN satisfies the new test
- Expected failure messages referencing modules/functions that already exist from prior cycles
- Parametrized tests where some parameter sets would pass while others fail (split needed)

**Acceptance:** Audit identifies RED plausibility issues. The workwoods Cycle 1.2 consolidation (4→1) should pass audit (prior cycle only creates empty-dir handling, not artifact detection).

**FR-5: Pre-execution test count reconciliation**
Cross-reference checkpoint "All N tests pass" claims against actual test function names defined in cycles within that phase. Account for:
- Parametrized tests (1 function × N parameter sets = 1 in count)
- Tests from prior phases (cumulative)
- Deleted tests (Phase 6 style removals)

**Acceptance:** Every checkpoint test count matches the reconciled count. Mismatches flagged with expected vs claimed count.

**FR-6: Scaling by runbook size**
Adapt review depth to runbook size (similar to deliverable-review's per-artifact delegation):
- Small runbooks (≤3 phases, ≤15 items): Single agent runs all checks (FR-1 through FR-5) in one pass
- Large runbooks (>3 phases or >15 items): Per-phase agents for FR-3/FR-4/FR-5, then holistic agent for FR-1/FR-2 cross-phase analysis
- Agent results written to `plans/<job>/reports/` with standardized format

**Acceptance:** Large runbook (workwoods: 6 phases, 43 items) uses delegated pattern. Small runbook (3 phases, 10 items) uses single-agent pattern. Both produce equivalent quality reports.

### Non-Functional Requirements

**NFR-1: Workflow integration**
New gates integrate into existing `/runbook` skill pipeline without breaking current flow. Simplification pass slots between Phase 1 (expansion) and Phase 3 (holistic review). Pre-execution validation slots between Phase 3 and Phase 4 (prepare-runbook.py).

**NFR-2: Incremental adoption**
Each FR can be implemented independently. A runbook can benefit from FR-1 (simplification) without requiring FR-3-5 (pre-execution checks). Skills degrade gracefully when individual checks are unavailable.

### Constraints

**C-1: No execution during validation**
Pre-execution checks (FR-3-5) analyze runbook text only. They do not create files, run tests, or modify the codebase. Read-only analysis of phase files.

**C-2: Reuse existing plan-reviewer infrastructure**
FR-1/FR-2 (simplification + model review) may extend plan-reviewer agent or run as a separate agent. FR-3-5 (pre-execution checks) should be scriptable (deterministic analysis suitable for Python tooling, not LLM judgment).

### Out of Scope

- Execution-time monitoring (that's orchestrator's job)
- Design-level quality (that's design-vet-agent's job)
- Per-phase TDD discipline review (already handled by plan-reviewer in Phase 1)
- Modifying orchestrate skill or prepare-runbook.py internals

### Dependencies

- Existing `/runbook` skill (pipeline insertion points: after Phase 1, after Phase 3)
- plan-reviewer agent (potential extension target for FR-1/FR-2)
- deliverable-review skill (scaling pattern reference for FR-6)

### Open Questions

- Q-1: Should FR-3-5 be Python scripts (deterministic) or agent-based (judgment required for plausibility)? File lifecycle (FR-3) and test count (FR-5) are clearly scriptable. RED plausibility (FR-4) may require LLM judgment.
- Q-2: Where exactly does simplification pass slot in? Between Phase 1 and Phase 2 (before assembly validation)? Or between Phase 2.5 (consolidation gate) and Phase 3 (holistic review)? The current Phase 2.5 consolidation gate handles trivial-item merging — simplification is broader (batching, model review).
- Q-3: Should FR-1 (simplification) be mandatory for all Tier 3 runbooks, or opt-in? Small runbooks (≤15 items) may not benefit from a simplification pass.

### Skill Dependencies (for /design)

- Load runbook skill SKILL.md before design (workflow integration needed)
- Load plan-reviewer agent definition before design (extension target)
