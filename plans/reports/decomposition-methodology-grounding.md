# Decomposition Methodology Grounding

**Grounding:** Strong — 3 established frameworks (DSM, Axiomatic Design, TRL) with direct applicability, 2 supporting frameworks (WBS, IDEF0) providing structural elements. Adapted with 12 project-specific desiderata from internal conceptual analysis.

**Date:** 2026-03-06

**Branch artifacts:**
- Internal: `plans/reports/decomposition-internal-conceptual.md`
- External: `plans/reports/decomposition-external-research.md`

---

## Research Foundation

**Primary frameworks:**
- **Design Structure Matrix (DSM)** — Steward (1981), Eppinger (MIT). Dependency matrix with partitioning, banding, tearing, and clustering operations. [dsmweb.org](https://dsmweb.org/introduction-to-dsm/)
- **Axiomatic Design (AD)** — Suh (MIT, 1990). Zigzag decomposition between functional and physical domains with independence axiom. [axiomaticdesign.com](https://www.axiomaticdesign.com/technology/introduction-to-axiomatic-design-concepts/)
- **Technology Readiness Level (TRL)** — Sadin/Mankins (NASA, 1974/1995). 9-level maturity scale for sub-problem readiness assessment. [NASA TRL](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/)

**Supporting frameworks:**
- **Work Breakdown Structure (WBS)** — DoD MIL-STD-881 (1968), PMI PMBOK. Hierarchical decomposition with 100% rule and DAG dependency network. [Wikipedia](https://en.wikipedia.org/wiki/Work_breakdown_structure)
- **IDEF0** — US Air Force ICAM (1981), based on Ross SADT (1977). Functional decomposition with ICOM arrows forcing dependency identification during decomposition. [Wikipedia](https://en.wikipedia.org/wiki/IDEF0)

---

## Adapted Methodology

### Principle 1: Decomposition alternates between problem and solution domains

**General insight (Axiomatic Design):** Decomposing in a single domain produces elements that are either too abstract (all "what," no "how") or prematurely committed (all "how," no validation against "what"). The zigzag pattern — define what's needed, then how to achieve it, then refine the what at the next level — keeps decomposition grounded at each level.

**Project instance:** The active recall outline decomposed in the execution domain only (Phase 1→6), producing phases that were implementation sequences rather than problem-solution pairs. Grounding (a "what" question — "what trigger taxonomy should we use?") was placed as Phase 5 (an implementation step), after Phase 4 had already committed to metadata model design (a "how" answer to a question not yet asked).

**Procedure:** At each decomposition level:
1. State the functional requirement (what this sub-problem must achieve)
2. Identify the design parameter (how — approach, module, artifact)
3. Check: does the "how" depend on unresolved "what" questions at this or sibling levels?
4. If yes, the unresolved "what" is a separate sub-problem with a knowledge dependency edge

### Principle 2: Dependencies are discovered during decomposition, not added post-hoc

**General insight (IDEF0):** Requiring explicit inputs, outputs, controls, and mechanisms for each sub-problem forces dependency discovery as a byproduct of decomposition. Post-hoc dependency identification misses implicit dependencies — the decomposer knows what connects sub-problems but doesn't record it until a separate "dependency mapping" step that may never happen or happens with lost context.

**Project instance:** The outline listed phases without explicit artifact flow between them. The dependency between format grounding and metadata model was implicit in the decomposer's reasoning but not captured in the outline. The outline review found it, but only because a reviewer traced the logical chain.

**Procedure:** Each sub-problem specification includes:
- **Inputs:** Named artifacts consumed (with source sub-problem or "pre-existing")
- **Outputs:** Named artifacts produced (with consuming sub-problem or "terminal deliverable")
- **Controls:** Decisions or constraints governing this sub-problem (with source)
- **Mechanism:** Model tier, execution mode (worktree/in-tree), pipeline routing

### Principle 3: Dependency analysis produces partial ordering, not total ordering

**General insight (DSM):** A dependency matrix analyzed via partitioning and banding reveals the natural partial order — which elements must precede which, and which can proceed concurrently. Banding groups elements at the same dependency depth: elements within a band have no ordering constraint between them. Total ordering (Phase 1→2→3→4→5→6) discards parallelism information that the partial order preserves.

**Project instance:** The active recall outline's linear Phase 1→6 sequence obscured that token cache (Phase 1) and recall consolidation (Phase 2) had no dependency between them — both could proceed in parallel. The linear sequence imposed an artificial ordering that also made the Phase 4/5 inversion harder to detect (it looked like "just swap two adjacent phases" rather than "these are in different dependency bands").

**Procedure:**
1. After decomposition, populate a dependency matrix (sub-problems as rows/columns, cells indicate dependency type)
2. Partition: reorder to lower-triangular form (reveals natural sequence)
3. Band: identify sub-problems at the same dependency depth (reveals parallelism)
4. The banded partial order is the decomposition output — not a total sequence

### Principle 4: Coupled sub-problems require explicit resolution before sequencing

**General insight (DSM tearing):** Circular dependencies (A needs B's output, B needs A's output) cannot be resolved by sequencing alone. They require a design decision: which dependency to break by accepting an assumption, doing preliminary work, or planning iteration. This is a "tearing" decision — choosing where to cut the cycle.

**Project instance:** Format grounding and metadata model are weakly coupled — grounding informs the model, but the model's requirements constrain what grounding should explore. The outline resolved this implicitly by sequencing (Phase 4 before Phase 5) with a hope-based mitigation ("fields are additive"). DSM tearing would make the resolution explicit: "break the cycle by grounding first, accepting that the metadata model may need revision if grounding produces unexpected taxonomy."

**Procedure:**
1. After partitioning, identify remaining cycles in the dependency matrix
2. For each cycle, select the tear point — the weakest dependency to break
3. Document the assumption being made at the tear point
4. The torn dependency becomes a validation checkpoint: after both sub-problems complete, verify the assumption

### Principle 5: Sub-problem maturity is assessed on a readiness scale, not assumed uniform

**General insight (TRL):** Not all sub-problems are equally ready for implementation. A maturity scale applied independently to each sub-problem prevents premature execution of under-designed elements. The minimum maturity across a sub-problem's dependencies constrains its own maturity — a sub-problem cannot be "ready" if it depends on an unresolved research question.

**Project instance:** The outline treated all phases as implementation-ready. Token cache (well-understood, prior design decisions made) and format grounding (open research question, unknown output) were assigned the same execution pipeline. The internal analysis identified three readiness levels that map to pipeline routing:

| Readiness | Definition | Pipeline routing | Model |
|-----------|-----------|-----------------|-------|
| **Groundable** | Open research question, needs external knowledge | `/ground` | opus |
| **Designable** | Problem understood, approach unresolved | `/design` | opus |
| **Executable** | Inputs resolved, acceptance criteria testable | `/runbook` → `/orchestrate` | sonnet |

**Readiness propagation rule:** A sub-problem's readiness cannot exceed the minimum readiness of its unresolved dependencies. If sub-problem B depends on sub-problem A, and A is groundable, then B is at most groundable regardless of how well-understood B's own scope appears.

### Principle 6: Decomposition completeness is verifiable via the 100% rule

**General insight (WBS):** Child sub-problems must account for 100% of the parent scope. If sub-problems sum to less than the parent, scope is lost. If they overlap, work will be duplicated or conflicting. Mutual exclusivity between siblings prevents the scope conflation the project experienced.

**Project instance:** The outline's phases were not mutually exclusive — Phase 3 (hierarchical index) included parser changes, migration, hook updates, backward compat, and recall loop updates. Some of these (recall loop updates) overlapped with Phase 6 (mode simplification). The 100% rule would catch this: list what each phase covers, verify no element appears in two phases, verify union equals full scope.

**Procedure:** After decomposition, enumerate deliverables per sub-problem. Verify:
- Union of all sub-problem deliverables = full project scope (completeness)
- Intersection of any two sub-problem deliverables = empty (mutual exclusivity)

### Principle 7: The dependency graph is the primary decomposition artifact

**General insight (DAG-based decomposition):** The dependency DAG — not the decomposition tree, not the phase list — is the artifact that enables correct scheduling, parallelism identification, and readiness propagation. The tree shows "what belongs to what" (hierarchy). The DAG shows "what enables what" (ordering).

**Project instance:** The outline was a tree (phases containing sub-tasks) with implicit linear ordering. Converting to an explicit DAG would have revealed: token cache and recall consolidation are independent roots (no predecessors other than "existing codebase"). Format grounding feeds metadata model and extraction pipeline. Hierarchical index depends on consolidation. This DAG structure enables scheduling decisions the linear phase list cannot.

**Decomposition output format:**
```
Sub-problems (nodes):
  - ID, name, type (design-input | implementation | migration | validation)
  - Readiness (groundable | designable | executable)
  - Inputs, outputs, controls, mechanism
  - File set (for merge conflict analysis)

Dependencies (edges):
  - Source → target, type (data | structural | knowledge | merge | validation)
  - Artifact and contract carried on the edge

Bands (derived):
  - Band 0: sub-problems with no dependencies (roots)
  - Band 1: sub-problems depending only on Band 0
  - Band N: sub-problems depending on Band N-1 or lower

  Sub-problems within a band have no ordering constraint.
  Merge dependencies within a band constrain parallelism.
```

---

## Adaptations from External Frameworks

| External element | Adaptation | Rationale |
|-----------------|------------|-----------|
| DSM binary matrix | Typed edges (5 dependency types) | Binary "depends/doesn't" loses the distinction between data flow, knowledge dependency, and merge conflict — each has different resolution |
| AD three-bin coupling (uncoupled/decoupled/coupled) | Continuous readiness scale (3 levels) + dependency propagation | Three bins too coarse; readiness propagation captures the Phase 4/5 problem (coupled through knowledge dependency) |
| TRL 9-level scale | 3-level scale (groundable/designable/executable) | 9 levels designed for hardware maturation; 3 levels map to pipeline routing decisions (ground/design/runbook) |
| WBS 100% rule | Applied as completeness check post-decomposition | WBS applies this during decomposition; applying post-decomposition allows the zigzag procedure to drive decomposition strategy while WBS validates completeness |
| IDEF0 ICOM | Simplified to inputs/outputs/controls/mechanism per sub-problem | Full IDEF0 diagramming is heavy; the ICOM checklist forces dependency discovery without the diagramming overhead |
| DSM banding | Banding as primary scheduling output | DSM uses banding as one analysis operation; here it becomes the primary output replacing linear phase ordering |

**Deliberately excluded:**
- DSM clustering (module identification) — relevant for product architecture, not for work decomposition in this context
- AD Axiom 2 (information minimization) — optimization criterion, not decomposition procedure
- NASA V-model integration side — testing/verification planning is handled by the existing TDD pipeline
- WBS decomposition approach taxonomy (7 types) — the zigzag procedure subsumes approach selection

---

## Grounding Assessment

**Quality label:** Strong

**Evidence basis:**
- DSM banding directly addresses the identified problem (premature sequencing). The framework is established (1981), widely applied, and the banding operation is mathematically grounded in partial order theory
- Axiomatic Design zigzag provides a decomposition procedure missing from DSM (which operates on pre-decomposed elements). The zigzag between functional and physical domains maps to the project's "what vs how" confusion
- TRL provides the readiness classification the project needs, adapted from 9 levels to 3 that map to existing pipeline routing
- Internal analysis produced 12 desiderata grounded in project failure history (outline Phase 4/5, worktree merge conflicts, context exhaustion). All 12 map to external framework elements

**Searches performed:**
- "work breakdown structure methodology decomposition dependency graph"
- "design structure matrix DSM decomposition methodology"
- "problem decomposition framework partial ordering software engineering"
- "design readiness assessment criteria engineering"
- "technology readiness level software development"

**Gaps:**
- No established framework combines all three concerns (decomposition procedure + dependency analysis + readiness classification) — the composition is project-specific
- The readiness propagation rule (Principle 5) is derived from internal analysis, not from TRL literature. TRL assesses elements independently; the propagation rule is an adaptation
- Dependency typing (5 types) is project-specific. DSM uses binary or numerical; the typed edges are grounded in project failure modes, not in DSM literature

---

## Sources

**Primary:**
- Steward, D.V. (1981). *The Design Structure System: A Method for Managing the Design of Complex Systems.* IEEE Transactions on Engineering Management. [DSM Web](https://dsmweb.org/introduction-to-dsm/)
- Suh, N.P. (1990). *The Principles of Design.* Oxford University Press. [Axiomatic Design](https://www.axiomaticdesign.com/technology/introduction-to-axiomatic-design-concepts/)
- Mankins, J.C. (1995). *Technology Readiness Levels.* NASA White Paper. [NASA TRL](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/)

**Secondary:**
- PMI. *A Guide to the Project Management Body of Knowledge (PMBOK).* [WBS](https://en.wikipedia.org/wiki/Work_breakdown_structure)
- Ross, D.T. (1977). *Structured Analysis (SA): A Language for Communicating Ideas.* IEEE TSE. [IDEF0](https://en.wikipedia.org/wiki/IDEF0)
- Eppinger, S.D. & Browning, T.R. (2012). *Design Structure Matrix Methods and Applications.* MIT Press. [IEEE](https://ieeexplore.ieee.org/document/946528/)
- Kahn, A.B. (1962). *Topological Sorting of Large Networks.* Communications of the ACM. [Topological Sort](https://en.wikipedia.org/wiki/Topological_sorting)
