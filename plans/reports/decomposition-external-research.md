# Decomposition Methodology: External Research

**Research question:** What established frameworks exist for decomposing complex jobs into sub-problems with dependency graphs, without premature sequencing?

**Date:** 2026-03-06

---

## Frameworks Evaluated

Seven frameworks were evaluated against inclusion criteria (actionable decomposition methodology, dependency-aware, supports partial ordering, applicable to design/engineering work breakdown).

### 1. Design Structure Matrix (DSM)

**Originator:** Donald Steward (1981), extended by Steven Eppinger (MIT)

**Core procedure:**
1. Identify system elements (tasks, components, or organizational units)
2. Populate a square matrix: rows and columns are elements, cells indicate dependencies
3. Reading a column reveals what inputs that element requires; reading a row reveals where its outputs go
4. Apply analytical operations to the matrix:
   - **Partitioning** — reorder rows/columns to achieve lower-triangular form (reveals natural sequencing)
   - **Tearing** — identify and break feedback loops in coupled elements (choose which dependency to resolve iteratively)
   - **Banding** — group elements that can execute in parallel (same dependency depth)
   - **Clustering** — identify modular groups with high internal coupling, low external coupling

**Dependency handling:** Three relationship types — parallel (no interaction), sequential (unidirectional A→B), coupled/interdependent (bidirectional A↔B). Coupled elements form cycles that partitioning cannot eliminate; tearing resolves these by selecting which feedback to break.

**Partial ordering:** Partitioning produces a partial order. Banding explicitly identifies elements at the same dependency depth (concurrent execution). The matrix form naturally represents partial order — elements in the same band have no ordering constraint between them.

**Design readiness distinction:** Not explicit. However, coupled clusters (elements that cannot be sequenced) implicitly signal "needs more design" — the coupling must be resolved (torn) before clean execution is possible. Uncoupled/sequenceable elements are "ready to execute."

**Limitations:**
- Requires upfront identification of all elements and their dependencies
- Tearing decisions are judgment calls — different tears produce different execution orders
- Does not prescribe how to decompose; operates on an already-decomposed set of elements
- Binary DSMs lose dependency strength information; numerical DSMs add complexity

**Relevance:** High. Directly addresses the problem of dependency-aware ordering without premature total sequencing. The banding operation is exactly "partial ordering without premature sequencing."

**Sources:**
- [DSM Web — Introduction](https://dsmweb.org/introduction-to-dsm/)
- [Wikipedia — Design Structure Matrix](https://en.wikipedia.org/wiki/Design_structure_matrix)
- [MIT Sloan — DSM Overview](https://executive.mit.edu/the-design-structure-matrix.html)
- [Eppinger & Browning — DSM applied to decomposition and integration (IEEE)](https://ieeexplore.ieee.org/document/946528/)

---

### 2. Axiomatic Design (AD)

**Originator:** Nam Pyo Suh (MIT, 1990)

**Core procedure (zigzag decomposition):**
1. Define highest-level Functional Requirements (FRs) in a solution-neutral way
2. Select Design Parameters (DPs) that satisfy each FR — this is the creative "how"
3. Construct the design matrix [A] mapping {FRs} = [A]{DPs}
4. Check matrix type against Axiom 1 (Independence):
   - **Uncoupled** (diagonal): each DP affects only its FR — any execution order works
   - **Decoupled** (triangular): DPs must be adjusted in a specific sequence — partial ordering emerges from the matrix
   - **Coupled** (full): violates Independence Axiom — redesign needed
5. Zigzag: return to functional domain, decompose each FR into sub-FRs given the chosen DP
6. Repeat steps 2-5 at each level until implementation-ready

**Four domains:** Customer → Functional → Physical → Process. Decomposition zigzags between adjacent domain pairs.

**Dependency handling:** The design matrix encodes dependencies explicitly. Off-diagonal elements represent coupling. A triangular matrix produces a total order; a diagonal matrix produces no ordering constraint. The matrix type is a design quality signal, not just an analytical output.

**Partial ordering:** Uncoupled designs have no ordering constraints (full parallelism). Decoupled designs have a specific required sequence (total order from triangularity). Coupled designs require iteration. AD does not natively produce partial orders between these extremes — it categorizes into three bins.

**Design readiness distinction:** Coupled designs (full matrix) are explicitly "not ready" — they violate Axiom 1 and require redesign. Uncoupled and decoupled designs are "ready." The axiom violation is a binary readiness gate.

**Limitations:**
- The three-bin classification (uncoupled/decoupled/coupled) is coarse — no gradation
- Zigzag decomposition requires creative DP selection at each level; the methodology doesn't help with that creative step
- Works best for product design; application to process/workflow decomposition requires translation
- Coupled sub-problems are flagged but the methodology says "redesign," not "how to resolve"

**Relevance:** Medium-high. The zigzag procedure is directly applicable to requirements→design decomposition. The design matrix as a dependency representation is powerful. However, the three-bin classification is coarser than DSM's continuous dependency analysis.

**Sources:**
- [Axiomatic Design — Introduction to Concepts](https://www.axiomaticdesign.com/technology/introduction-to-axiomatic-design-concepts/)
- [MIT OCW — Axiomatic Design Chapter](https://ocw.mit.edu/courses/2-800-tribology-fall-2004/7956138e737f6cb1e9fb744fcc6c48ef_ch10_axiomatic.pdf)
- [MIT — Axiomatic Design Q&A](http://web.mit.edu/2.882/www/chapter1/chapter1.htm)

---

### 3. Work Breakdown Structure (WBS)

**Originator:** US Department of Defense (MIL-STD-881, 1968), codified by PMI (PMBOK)

**Core procedure:**
1. Define top-level deliverable (Level 1)
2. Decompose into major deliverables or work areas (Level 2)
3. Continue decomposing each element until work packages are manageable by a single individual/team
4. Apply the 100% Rule: child elements must sum to exactly 100% of parent scope
5. Ensure mutual exclusivity: no overlap between sibling elements
6. Identify dependencies between terminal elements (work packages)
7. Map dependencies into a network diagram for scheduling

**Decomposition approaches (seven documented):**
- Physical decomposition (by product components)
- Functional decomposition (by system functions)
- Process decomposition (by lifecycle phases)
- Objectives decomposition (by critical success factors)
- Geographic, organizational, cost-account decomposition

**Dependency handling:** Dependencies are identified between terminal work packages after decomposition. The WBS itself is a tree (hierarchy), not a graph. Dependencies are added as a separate network diagram layer, producing a DAG suitable for scheduling.

**Partial ordering:** The network diagram is a DAG — inherently a partial order. Topological sort produces valid total orders, but the DAG preserves parallelism information. Elements with no path between them can execute concurrently.

**Design readiness distinction:** Not explicit in the WBS methodology. The stopping criterion is "manageable by a single individual" — a granularity criterion, not a readiness criterion. However, the "rolling wave planning" variant decomposes near-term work in detail while leaving future work at higher levels, which is an implicit readiness heuristic.

**Limitations:**
- Decomposition is hierarchical (tree) — cross-cutting dependencies require a separate representation
- The methodology prescribes structure but not decomposition strategy (which of the seven approaches to use)
- Dependencies are added post-decomposition, not discovered during it
- No formal mechanism to flag sub-problems as "needs more design"

**Relevance:** Medium. Provides the hierarchical decomposition structure and the 100% Rule (completeness check). The dependency network is the right representation. But dependency discovery is treated as a separate, under-specified step rather than being integrated into decomposition.

**Sources:**
- [Wikipedia — Work Breakdown Structure](https://en.wikipedia.org/wiki/Work_breakdown_structure)
- [PMI — Applying WBS to Project Lifecycle](https://www.pmi.org/learning/library/applying-work-breakdown-structure-project-lifecycle-6979)
- [ProjectManager Guide — WBS](https://www.projectmanager.com/guides/work-breakdown-structure)

---

### 4. IDEF0 (Integration DEFinition for Function Modeling)

**Originator:** US Air Force ICAM program (1981), based on SADT by Douglas T. Ross (MIT/SofTech, 1977)

**Core procedure:**
1. Define the top-level function as a single box (A-0 diagram) with ICOM arrows:
   - **I**nputs (left): what the function transforms
   - **C**ontrols (top): constraints/standards governing the function
   - **O**utputs (right): what the function produces
   - **M**echanisms (bottom): resources/tools used
2. Decompose the top-level function into 3-6 sub-functions (A0 diagram)
3. Connect sub-functions via ICOM arrows — outputs of one become inputs/controls of others
4. Recursively decompose each sub-function until sufficient detail is reached
5. At each level, the parent's ICOM arrows must be fully accounted for by child functions (boundary consistency)

**Dependency handling:** Dependencies are explicit in the ICOM arrow connections between sibling functions. An output arrow from function A entering function B as an input creates a dependency A→B. Control arrows represent a different dependency type (governing constraints rather than data flow).

**Partial ordering:** ICOM connections between sibling functions create a DAG at each decomposition level. Functions with no connecting arrows can execute in parallel. The methodology does not require total ordering — it represents the natural partial order from data/control flow.

**Design readiness distinction:** Not explicit. The stopping criterion is "sufficient detail for the decision-making task at hand." In practice, functions that cannot be further decomposed without resolving design questions are left at a higher level.

**Limitations:**
- Purely functional perspective — no structural or behavioral decomposition
- ICOM arrow semantics are rigid (four types only)
- Large models become difficult to navigate despite hierarchical organization
- No formal dependency analysis operations (unlike DSM's partitioning/banding)

**Relevance:** Medium. Strong at revealing dependencies during decomposition (not post-hoc). The ICOM framework forces explicit dependency identification at each level. However, lacks DSM's analytical operations for optimizing the dependency structure.

**Sources:**
- [Wikipedia — IDEF0](https://en.wikipedia.org/wiki/IDEF0)
- [IDEF.com — IDEF0 Function Modeling Method](https://www.idef.com/idefo-function_modeling_method/)

---

### 5. NASA Logical Decomposition (Systems Engineering V-Model)

**Originator:** NASA Systems Engineering Handbook (NASA/SP-2016-6105), built on DoD systems engineering standards

**Core procedure:**
1. Establish system architecture model (the partitioning structure)
2. Translate top-level requirements into required functions (functional analysis)
3. Decompose and allocate functions to lower product breakdown structure levels
4. For each function, identify: inputs, outputs, failure modes, consequence of failure, interface requirements
5. Resolve conflicts between allocated requirements
6. Baseline when: all levels analyzed, requirements understood, verified viable/verifiable/internally consistent
7. Iterate — process is "recursive and iterative"

**Dependency handling:** Functional analysis reveals dependencies through input/output identification. Interface requirements explicitly capture cross-element dependencies.

**Partial ordering:** The V-model left side (decomposition) produces a hierarchy. Dependencies between peer elements at each level create partial ordering. The right side (integration/verification) reverses the hierarchy — lowest elements integrate first.

**Design readiness distinction:** Formal review gates: Preliminary Design Review (PDR) and Critical Design Review (CDR). PDR assesses whether preliminary design is mature enough for detailed design. CDR assesses whether detailed design is ready for implementation. These gates apply to sub-problems at each decomposition level.

**Limitations:**
- Heavy process overhead — designed for aerospace/defense scale
- Review gates are organizational ceremonies, not analytical tools
- V-model implies a left-to-right temporal flow that can become waterfall-like
- Decomposition methodology is underspecified ("translate requirements into functions" without saying how)

**Relevance:** Medium. The formal review gates (PDR/CDR) are the closest thing to a "design readiness assessment" in established practice. The TRL (Technology Readiness Level) scale provides a 1-9 maturity metric applicable to sub-problems.

**Sources:**
- [NASA — Logical Decomposition](https://www.nasa.gov/reference/4-3-logical-decomposition/)
- [NASA — Technology Readiness Levels](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/)
- [Wikipedia — V-model](https://en.wikipedia.org/wiki/V-model)

---

### 6. DAG-Based Task Decomposition (Topological Sort)

**Originator:** Kahn (1962, algorithm), general graph theory. Applied in build systems, CI/CD, compiler optimization.

**Core procedure:**
1. Identify atomic tasks
2. For each task, identify predecessor tasks (what must complete first)
3. Represent as directed acyclic graph (DAG): nodes = tasks, edges = dependencies
4. Verify acyclicity (cycles indicate coupled sub-problems)
5. Apply topological sort to produce valid execution orders
6. Identify independent sets (tasks with no path between them) for parallel execution

**Dependency handling:** Direct edge representation. The DAG is the dependency graph — no separate representation needed.

**Partial ordering:** A DAG defines a partial order by construction. Topological sort produces a linear extension (total order compatible with the partial order), but the DAG preserves the full partial order including parallelism. Multiple valid topological sorts exist — each is one valid sequencing.

**Design readiness distinction:** Cycles in the dependency graph indicate coupled sub-problems that cannot be sequenced. Cycle detection is the readiness test — acyclic sub-graphs are ready for execution ordering; cyclic components need resolution (analogous to DSM tearing).

**Limitations:**
- Not a decomposition methodology — assumes tasks already identified
- No guidance on how to identify tasks or their granularity
- Cycle resolution is not addressed (just detected)
- No notion of decomposition levels or hierarchy

**Relevance:** High as a dependency representation and ordering mechanism. Low as a decomposition methodology. The DAG + topological sort is the mathematical foundation that DSM, WBS network diagrams, and build systems all use. It is the correct target representation, not a complete methodology.

**Sources:**
- [Wikipedia — Topological Sorting](https://en.wikipedia.org/wiki/Topological_sorting)
- [Wikipedia — Dependency Graph](https://en.wikipedia.org/wiki/Dependency_graph)

---

### 7. Technology Readiness Level (TRL)

**Originator:** Stan Sadin (NASA, 1974), refined by John C. Mankins (1995)

**Core scale (9 levels):**
1. Basic principles observed
2. Technology concept formulated
3. Experimental proof of concept
4. Technology validated in lab
5. Technology validated in relevant environment
6. Technology demonstrated in relevant environment
7. System prototype demonstrated in operational environment
8. System complete and qualified
9. System proven in operational environment

**Procedure for sub-problem assessment:**
1. Decompose system into critical technology elements
2. Assess each element independently on the TRL scale
3. The minimum TRL across sub-components represents the system's overall readiness
4. Elements below threshold TRL require further development before system integration

**Dependency handling:** Not a dependency methodology. Assesses maturity independently per element.

**Partial ordering:** Not applicable — TRL is a maturity metric, not an ordering framework.

**Design readiness distinction:** This is TRL's primary contribution. The scale explicitly distinguishes maturity levels. For our purposes, the key boundary is TRL 3-4 (concept validated → lab validated): below TRL 4, a sub-problem "needs more design"; above TRL 4, it can proceed to implementation.

**Limitations:**
- Designed for technology maturation, not design decomposition
- The scale is hardware-oriented; software adaptation is awkward
- No dependency awareness
- Assessment is subjective without detailed criteria

**Relevance:** Low as a decomposition methodology. High as a sub-problem readiness classification scheme. The idea of a maturity scale that gates whether a sub-problem is ready for implementation (vs. needs more research/design) is directly applicable.

**Sources:**
- [NASA — Technology Readiness Levels](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/)
- [Wikipedia — Technology Readiness Level](https://en.wikipedia.org/wiki/Technology_readiness_level)

---

## Comparative Assessment

| Framework | Decomposition Procedure | Dependency Representation | Partial Ordering | Readiness Classification | Actionability |
|-----------|------------------------|--------------------------|-----------------|-------------------------|--------------|
| **DSM** | None (operates on pre-decomposed elements) | Square matrix (binary/numerical) | Yes (banding) | Implicit (coupled = not ready) | High |
| **Axiomatic Design** | Zigzag between domains | Design matrix | Limited (3 bins) | Yes (axiom violation = redesign) | High |
| **WBS** | Hierarchical (7 approaches) | Network diagram (post-hoc) | Yes (DAG) | No (granularity only) | Medium |
| **IDEF0** | Hierarchical with ICOM | Arrow connections | Yes (implicit DAG) | No | Medium |
| **NASA V-Model** | Requirements allocation | Interface requirements | Yes (hierarchy + peers) | Yes (PDR/CDR gates) | Low (heavy) |
| **DAG/Toposort** | None (mathematical foundation) | Direct graph | Yes (by definition) | Cycle detection only | Low (foundation) |
| **TRL** | None (assessment scale) | None | N/A | Yes (9-level scale) | Medium |

---

## Synthesis: Applicable Patterns

No single framework covers all requirements. The applicable methodology is a composition:

**For decomposition procedure:** Axiomatic Design's zigzag — alternate between "what" (functional requirements) and "how" (design parameters) at each level. This prevents decomposing in a single domain, which is what caused the active recall outline problem (sequencing execution phases without grounding design decisions).

**For dependency representation:** DSM — after decomposition, populate a dependency matrix and apply partitioning/banding to discover the natural partial order. Banding identifies parallel groups; partitioning reveals sequential constraints.

**For readiness classification:** A simplified TRL-inspired scale applied to each sub-problem:
- **Ready** — sub-problem is well-understood, can proceed to implementation planning (runbook)
- **Needs design** — sub-problem has open questions or unresolved dependencies that require further design work
- **Needs research/grounding** — sub-problem requires external knowledge or empirical data before design can proceed

**For cycle resolution:** DSM tearing — when sub-problems have circular dependencies, select which dependency to break (accept an assumption, do preliminary work, or iterate).

**Key insight from this research:** The active recall outline's flaw (conflating decomposition with sequencing) is a known problem that DSM banding directly addresses. Banding separates "what depends on what" from "what order to do things in." Multiple elements in the same band can be done in any order — the band assignment is the partial ordering.
