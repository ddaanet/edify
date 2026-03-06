# Decomposition: Internal Conceptual Analysis

Project-specific dimensions, constraints, and desiderata for decomposing complex design jobs into sub-problems with dependency graphs, without premature sequencing.

---

## 1. Properties of a Good Decomposition

### 1.1 Context-Window Scoping

Each sub-problem must be completable within a single agent session's context budget. The active recall outline's Phase 3 (hierarchical index) spans parser changes, migration strategy, hook updates, backward compatibility, and recall loop updates — any one of these could consume a full session. A decomposition that produces sub-problems exceeding context capacity forces the sub-problem itself through the Tier 2/3 pipeline, creating recursive decomposition with no clear base case.

**Desideratum:** Sub-problems should be leaf-schedulable — each enters the Tier 1-3 pipeline exactly once without requiring further decomposition at execution time.

### 1.2 Independently Testable Boundaries

The project's execution model requires clean tree after every step and precommit validation as exit gate. Sub-problems that share mutable state (same module, same test file, same index file) create merge conflicts when executed in parallel worktrees and validation failures when executed sequentially with interleaved commits.

**Desideratum:** Sub-problem boundaries should align with testable integration points — each sub-problem leaves the system in a passing-precommit state.

### 1.3 Design Inputs vs Implementation Units

The active recall outline conflated these. Design inputs (grounding, research, format specification) produce knowledge consumed by implementation units. They are not "phases" — they are prerequisites with different execution characteristics: no code output, no test coverage, different model tier (opus for synthesis vs sonnet for implementation), different validation criteria (quality of analysis vs passing tests).

**Desideratum:** Decomposition must distinguish sub-problem *type* — design input, implementation unit, migration task, validation task — because type determines pipeline routing, model selection, and acceptance criteria.

### 1.4 Minimal Cross-Sub-Problem Interface

Sub-problems connected by broad, poorly-defined interfaces create rework when one side changes. The outline's Phase 4 → Phase 5 interface was "metadata fields are additive" — an assertion about interface stability that was actually a hope. A good decomposition makes the interface between sub-problems explicit and narrow.

**Desideratum:** Each dependency edge should name the specific artifact and contract it carries. "Phase 5 feeds Phase 6" is insufficient; "format-specification.md defining trigger syntax consumed by extraction-agent prompt" is actionable.

---

## 2. Failure Modes the Project Has Already Encountered

### 2.1 Premature Commitment (Outline Phase 4/5)

Phase 4 committed to `when`/`how` taxonomy before Phase 5 could validate it. The mitigation ("fields are additive") assumed the interface between metadata model and format grounding was narrow. If grounding invalidates the taxonomy entirely (proposing different trigger classes), Phase 4's model changes, tests, and skill updates are rework.

**Decomposition should prevent:** Sub-problems proceeding before their design inputs are resolved. The dependency graph must make design-readiness a gate, not a hope.

### 2.2 Scope Conflation in Outlines

The outline used "phase" for both logical grouping (all index-related work) and execution ordering (Phase 3 before Phase 4). This made it impossible to express "parser changes and migration tooling are the same *domain* but different *work units* that could proceed independently once the format is defined."

**Decomposition should prevent:** Confusing domain grouping with execution dependency. Sub-problems should be connected by data dependencies, not by proximity to a shared topic.

### 2.3 Worktree Merge Conflicts from Shared Files

The project's worktree parallelism model gives each task its own branch. When two sub-problems edit the same file (e.g., both touch `IndexEntry` model or both update the recall skill), merging creates conflicts. The orchestration decision "partition scope completely before launch — no mid-flight messaging available" means conflicts discovered at merge time require manual resolution.

**Decomposition should prevent:** Two parallel sub-problems touching the same file unless their edits are structurally non-overlapping (different sections, different functions).

### 2.4 Design Session Producing Implementation Artifacts

The current pipeline has design producing an outline, which becomes a runbook. When a "phase" in the outline is actually a research question (format grounding), it gets treated as an implementation step with RED/GREEN/REFACTOR cycles. Research doesn't have test coverage targets or code output.

**Decomposition should prevent:** Research sub-problems entering the implementation pipeline. Type annotation (design input vs implementation unit) gates pipeline routing.

### 2.5 Orchestrator Context Exhaustion

The orchestration-execution decisions document that orchestrator context grows with step count. The outline's 6 phases each containing multiple sub-tasks create a long orchestration session. If the orchestrator must hold context for all phases to manage cross-phase dependencies, context exhaustion causes late-phase degradation.

**Decomposition should prevent:** Orchestration sessions that span the full dependency graph. Sub-problems with resolved dependencies should be independently launchable without requiring the orchestrator to remember earlier sub-problems.

---

## 3. LLM-Agent Execution Model Constraints

### 3.1 One-Shot Partitioning

From the orchestration decisions: "Partition scope completely before launch — no mid-flight messaging available." This means decomposition outputs must be complete specifications — a sub-problem's scope, inputs, outputs, and acceptance criteria must be fully defined before any agent starts executing it.

**Constraint:** Decomposition cannot rely on runtime negotiation between sub-problems. All interfaces must be statically defined.

### 3.2 Context Window as Hard Capacity Bound

The 200K token limit is absolute. A sub-problem that requires reading the full outline (6 phases), all 21 decision files (~64k tokens), and the requirements document before starting implementation has consumed a third of its context budget on orientation. The remaining budget must cover file reads, reasoning, edits, and validation.

**Constraint:** Sub-problem specifications must include a context budget estimate: required reading (design doc, relevant decisions, step file) vs available budget for execution. Sub-problems requiring more orientation context than execution context are mis-scoped.

### 3.3 Model Tier Mismatch Penalty

Running opus on mechanical work wastes cost; running sonnet on architectural synthesis produces lower-quality decisions. The current pipeline assigns model at the runbook level, but decomposition happens earlier. If sub-problems mix design reasoning with mechanical implementation, the model tier is a forced compromise.

**Constraint:** Sub-problems should be model-homogeneous — each sub-problem's cognitive requirements should map cleanly to a single model tier.

### 3.4 Agent Scope Enforcement by Context Absence

From the orchestration decisions: "Give executing agent step + design + outline only. Scope enforced structurally by context absence." Agents scope-creep when they can see adjacent work. A decomposition that produces overlapping sub-problems (shared files, shared concepts) makes scope enforcement harder — the agent sees enough to "helpfully" do work belonging to a sibling sub-problem.

**Constraint:** Sub-problems should have minimal context overlap. Two sub-problems that require reading the same files to execute are candidates for merging or for explicit boundary fencing (clear "OUT OF SCOPE" declarations in their specifications).

### 3.5 Sequential Commit Dependency

Git commits are sequential — two worktrees cannot commit to the same branch simultaneously. Parallel sub-problems must operate on separate branches with a defined merge order. The merge order imposes a sequencing constraint that decomposition must account for even when the sub-problems are logically independent.

**Constraint:** Parallel sub-problems must have a defined merge strategy. Sub-problems that modify the same files need explicit merge ordering (first-to-merge wins; second-to-merge rebases).

---

## 4. Design Readiness Assessment

### 4.1 Readiness Categories

Not all sub-problems are equally ready for implementation. The active recall outline had sub-problems at three different readiness levels masquerading as a single sequence:

- **Executable:** All inputs resolved, acceptance criteria testable, no open design questions. Can proceed to runbook. (Example: token count cache — storage decision made, schema defined, integration point identified.)
- **Designable:** Problem well-understood, approach unclear. Needs a design session before runbook. (Example: hierarchical index parser — format defined, but traversal semantics, migration strategy, and backward compat require design decisions.)
- **Groundable:** Problem not yet well-enough understood for design. Needs research/grounding before design. (Example: format grounding — don't know what alternatives to when/how exist.)

### 4.2 Readiness Signals

| Signal | Executable | Designable | Groundable |
|--------|-----------|------------|------------|
| Open design questions | None | Named, bounded | Unbounded or existential |
| Acceptance criteria | Testable assertions | Outcome-describable | Not yet articulable |
| Interface with dependencies | Artifact + contract named | Artifact named, contract fuzzy | Neither named |
| Model in domain | Exists, fields known | Exists, fields TBD | Model may not survive |
| Prior art in codebase | Pattern exists to extend | Related patterns exist | No applicable patterns |

### 4.3 Readiness Transitions

Sub-problems move through readiness levels as work completes:

- Groundable → Designable: research artifact produced, open questions bounded
- Designable → Executable: design decisions made, acceptance criteria testable
- Executable → Complete: implementation passes acceptance criteria

Each transition produces a specific artifact that the dependency graph can reference.

### 4.4 Readiness and the Premature Commitment Problem

The active recall outline's Phase 4/5 inversion occurred because readiness was not assessed per-sub-problem. The metadata model (Phase 4) was assumed executable because it was "lightweight" — but its correctness depended on format grounding (Phase 5) which was groundable. A decomposition that tags readiness would have caught this: Phase 4 has a dependency on a groundable sub-problem, therefore Phase 4 is at most designable until that dependency resolves.

**Rule:** A sub-problem's readiness level cannot exceed the minimum readiness of its unresolved dependencies.

---

## 5. Dependency Types

### 5.1 Data Dependency (Artifact Flow)

Sub-problem B consumes an artifact produced by sub-problem A. The most common type. The dependency is on the artifact, not the sub-problem — if the artifact already exists (from prior work, from a different sub-problem), the dependency is already satisfied.

**Examples:**
- Format specification (from grounding) → extraction agent prompt (in pipeline)
- Consolidated recall module (from Phase 2) → hierarchical parser (in Phase 3)
- Token cache (from Phase 1) → split threshold measurement (in Phase 3)

**Interface contract:** Named file path + content schema (e.g., "format-specification.md containing trigger syntax BNF and validation rules").

### 5.2 Structural Dependency (Code Prerequisite)

Sub-problem B modifies code that sub-problem A introduces. This is stronger than data dependency — B needs A's code to exist in the codebase, not just A's artifact in a report file.

**Examples:**
- Unified `IndexEntry` model (from consolidation) → trigger class field addition (in metadata)
- Hierarchical parser (from Phase 3) → recall mode simplification (uses new traversal)

**Interface contract:** Module path + API surface (e.g., "`IndexEntry` in `src/claudeutils/recall/models.py` with fields `trigger`, `extras`, `source_file`").

### 5.3 Knowledge Dependency (Design Input)

Sub-problem B's design depends on conclusions from sub-problem A. A is a research/grounding task whose output informs B's architectural decisions. This is the dependency type the outline mishandled — format grounding (A) informs metadata model design (B), but B was sequenced before A.

**Examples:**
- Decomposition methodology grounding → outline redraft (the current situation)
- Format grounding → metadata model design
- Format grounding → extraction pipeline design

**Interface contract:** Named decision or specification (e.g., "trigger taxonomy: set of trigger classes with definitions and examples"). Unlike data dependencies, knowledge dependencies may invalidate already-made decisions if the knowledge contradicts assumptions.

### 5.4 Merge Dependency (Branch Ordering)

Sub-problem B's branch must merge after sub-problem A's because both touch shared files. Not a logical dependency — the sub-problems are conceptually independent — but a mechanical constraint from the worktree model.

**Examples:**
- Both recall consolidation and hierarchical index modify `parse_memory_index()`
- Both metadata addition and mode simplification modify the `/recall` skill

**Interface contract:** File path list + merge order assertion. Merge dependencies are the primary constraint on parallelism — two sub-problems with no merge dependency can run in parallel worktrees.

### 5.5 Validation Dependency (Integration Gate)

Sub-problem B's acceptance criteria include verifying behavior across multiple completed sub-problems. B is an integration test, not an implementation task. Current pipeline has no explicit concept of this — validation is per-step (precommit), not cross-sub-problem.

**Examples:**
- After consolidation + hierarchical index: `_recall resolve` works end-to-end through hierarchy
- After all phases: recall-explore-recall pattern still functions (FR-6 regression check)

**Interface contract:** Test specification referencing multiple sub-problem outputs.

---

## 6. Worktree Parallelism Interaction

### 6.1 Parallelism Budget

The project runs worktrees for parallel independent tasks. But parallelism is not free — each worktree is a separate agent session consuming API tokens. The decomposition should identify the *maximum useful parallelism* at each stage of the dependency graph, not the maximum theoretical parallelism.

**Dimension:** At any point in execution, how many sub-problems have all dependencies satisfied and no merge conflicts with each other? This is the parallelism frontier.

### 6.2 Merge Topology

Worktree branches merge back to main. The merge order matters when sub-problems touch shared files. A decomposition should produce an explicit merge topology:

- **Independent merge:** Sub-problems touch disjoint file sets. Merge in any order. Maximum parallelism.
- **Sequential merge:** Sub-problems touch shared files. Must merge in dependency order. First-to-merge defines the base for second-to-merge's rebase.
- **Fan-in merge:** Multiple sub-problems feed into an integration sub-problem. All must merge before integration begins.

The active recall system has significant shared-file overlap (recall module, index parser, skill files, test files), which limits practical parallelism more than the dependency graph alone suggests.

### 6.3 Worktree-Readiness Alignment

Not all executable sub-problems should launch as worktrees simultaneously. The classification heuristic for in-tree vs worktree tasks (from session.md conventions) considers:

- Does the sub-problem benefit from isolation? (touches many files, long-running)
- Does the sub-problem conflict with other in-progress work?
- Is the sub-problem small enough for in-tree execution?

**Dimension:** Decomposition should annotate sub-problems with isolation preference, enabling the scheduler (session.md task classification) to make informed worktree decisions.

### 6.4 Worktree Session Continuity

Each worktree gets its own session.md and its own session context. Cross-worktree communication happens only through committed artifacts (brief.md, merged code). A decomposition that creates sub-problems requiring real-time coordination between worktrees is inherently broken in this model.

**Constraint:** Sub-problems in parallel worktrees must be fire-and-forget with a defined merge point. No handshake protocol, no shared mutable state, no "check if the other worktree finished X before proceeding."

---

## 7. Evaluation Axes for Decomposition Quality

### 7.1 Dependency Density

Ratio of dependency edges to sub-problem count. High density means tight coupling — most sub-problems block on others. Low density means high parallelism potential. The active recall outline had approximately linear dependency (Phase 1 → 2 → 3 → 4 → 5 → 6) with density near 1.0 — minimal parallelism despite logical independence between some phases.

### 7.2 Readiness Distribution

How many sub-problems are immediately executable vs requiring further design vs requiring grounding? A decomposition that produces mostly groundable sub-problems has not progressed the design — it has merely renamed open questions. A good decomposition should have a mix weighted toward executable, with groundable items explicitly identified as blockers.

### 7.3 Context Budget Fit

For each sub-problem: estimated orientation context (files to read) vs estimated execution context (files to write, tests to run, validation to perform). Sub-problems where orientation exceeds 40% of the 200K budget are at risk of context exhaustion during execution.

### 7.4 File-Set Overlap

For each pair of sub-problems: how many files appear in both file sets? High overlap means sequential merge requirement and reduced parallelism. The decomposition should minimize overlap or explicitly sequence overlapping pairs.

### 7.5 Type Homogeneity

Each sub-problem should map to a single type (design input, implementation, migration, validation). Mixed-type sub-problems force model tier compromises and complicate acceptance criteria. A sub-problem that is "implement parser changes AND ground format specification" conflates two types.

---

## 8. Desiderata Summary

| ID | Desideratum | Source |
|----|-------------|--------|
| D-1 | Sub-problems are leaf-schedulable (enter Tier 1-3 once) | Context-window scoping (1.1) |
| D-2 | Each sub-problem leaves system in passing-precommit state | Testable boundaries (1.2) |
| D-3 | Sub-problem type explicitly annotated (design input / implementation / migration / validation) | Type distinction (1.3), pipeline routing (2.4) |
| D-4 | Dependency edges name specific artifact and contract | Minimal interface (1.4), premature commitment (2.1) |
| D-5 | Decomposition is not domain grouping — dependencies are data flow, not topic proximity | Scope conflation (2.2) |
| D-6 | Parallel sub-problems touch disjoint file sets | Merge conflict prevention (2.3) |
| D-7 | Sub-problems are model-homogeneous | Model tier mismatch (3.3) |
| D-8 | Readiness level tagged per sub-problem (executable / designable / groundable) | Readiness assessment (4.1-4.4) |
| D-9 | Readiness cannot exceed minimum readiness of unresolved dependencies | Premature commitment rule (4.4) |
| D-10 | Merge topology explicit (independent / sequential / fan-in) | Worktree merge (6.2) |
| D-11 | No cross-worktree real-time coordination | Session continuity (6.4) |
| D-12 | Dependency density minimized; parallelism frontier identified | Evaluation (7.1) |
