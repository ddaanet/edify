# Outline Review (Redraft): active-recall

**Artifact**: plans/active-recall/outline.md
**Date**: 2026-03-06
**Mode**: review + fix-all (PDR + decomposition methodology criteria)

## Summary

The redrafted outline correctly applies DSM banding, Axiomatic Design zigzag, and TRL readiness scale. The prior conflation of subtasks with execution phases is resolved — sub-problems are decomposed by problem/solution domain pairing (Principle 1), dependencies discovered via ICOM (Principle 2), and banded for partial ordering (Principle 3). Primary issues were: missing dependency edge (S-D to S-H), inconsistent readiness labels on S-G, missing S-A to S-G edge in the graph section, and an inaccurate mutual exclusivity claim. All fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | S-A (cache) + S-D (hierarchy) | Complete | Token-counted splits, arbitrary nesting, parser, migration, recall loop |
| FR-2 | S-E | Complete | Trigger class metadata, per-entry decision |
| FR-3 | S-E | Complete | Learning categories, dependency partitioning, version-change scope |
| FR-4 | S-G | Complete | Pipeline, corrector, first targets, methodology sources |
| FR-5 | S-C | Complete | Format grounding research, format spec output |
| FR-6 | S-H | Complete | Pattern documentation, regression verification |
| FR-7 | S-F | Complete | Mode reduction (5 to 2), pipeline point updates |
| FR-8 | S-B | Complete | Module merge, model unification, deprecation alias |
| NFR-1 | S-D | Complete | O(log_k(N)) hierarchical lookup |
| NFR-2 | S-B (deprecation alias) + S-D (path migration) | Complete | Backward compat during transition |
| NFR-3 | S-D | Complete | Incremental migration strategy |
| NFR-4 | S-A (measurement) + S-D (threshold) | Complete | Token budget as design target |
| C-1 | S-C to S-G edge | Complete | Format before bulk conversion |
| C-2 | S-D to S-G edge | Complete | Hierarchy before bulk conversion |
| C-3 | S-A to S-D edge | Complete | Token counting before split |
| C-4 | S-B | Complete | Infrastructure accounting |

**Traceability Assessment**: All requirements covered. Every FR, NFR, and constraint maps to specific sub-problem(s) with explicit dependency edges enforcing ordering constraints.

## Decomposition Methodology Assessment

### Principle 1: Zigzag decomposition (AD)
Each sub-problem states FR (what) and DP (how). S-C correctly identified as a "what" question (format grounding) separated from "how" answers (S-E metadata, S-G pipeline). The Phase 4/5 inversion from the prior outline is resolved — S-E explicitly waits for S-C (Tear T-2 not torn). **Pass.**

### Principle 2: Dependencies discovered during decomposition (ICOM)
All sub-problems include Inputs/Outputs/Controls/Mechanism. Dependencies emerge from ICOM rather than being post-hoc additions. Example: S-A to S-D (data: token cache) discovered from S-D's Input specification. **Pass.**

### Principle 3: Partial ordering via bands, not total ordering
4 bands with explicit parallelism notes. Band 0 has 3 concurrent roots (disjoint file sets). Prior linear Phase 1 to 6 replaced. **Pass.**

### Principle 4: Coupled sub-problems have explicit tear decisions
T-1 (S-C/S-D): torn — hierarchy structure independent of entry format, tear assumption documented, mitigation stated (parser is format-agnostic). T-2 (S-C/S-E): not torn — S-E waits, cost/benefit documented. **Pass.**

### Principle 5: Readiness propagation
S-E correctly propagated to groundable from S-C dependency. S-G was labeled "Designable (propagated groundable)" which contradicts propagation rule — fixed to "Groundable (propagated)." S-D correctly labeled designable (S-A and S-B are executable, not readiness-limiting). **Pass after fix.**

### Principle 6: 100% rule (completeness + mutual exclusivity)
Completeness table covers all 8 FRs, 4 NFRs, 4 constraints. Mutual exclusivity claim was inaccurate ("No FR appears in two implementation sub-problems" when FR-1 spans S-A + S-D) — fixed to correctly characterize the prerequisite-to-consumer relationship. **Pass after fix.**

### Principle 7: DAG as primary output
Explicit dependency graph with typed edges, absent edges, and derived bands. DAG is navigable and complete. **Pass.**

## Review Findings

### Critical Issues

None.

### Major Issues

1. **S-H missing S-D dependency edge**
   - Location: S-H sub-problem and Dependency Graph
   - Problem: S-H verifies end-to-end `_recall resolve` through hierarchy (FR-6) but only listed S-F as dependency. Hierarchy (S-D) must exist for traversal verification. Graph was missing S-D to S-H edge.
   - Fix: Added S-D to S-H inputs, added edge to Dependency Graph, updated Band 3 and Readiness Summary
   - **Status**: FIXED

2. **S-G readiness label inconsistent with propagation rule**
   - Location: S-G Readiness field and Bands section
   - Problem: S-G header said "Designable" but body acknowledged "at most groundable until S-C completes." Principle 5 says readiness cannot exceed min dependency readiness. S-C is groundable, so S-G is groundable.
   - Fix: Changed readiness to "Groundable (propagated)" in sub-problem, bands, and readiness summary
   - **Status**: FIXED

3. **S-A to S-G edge missing from Dependency Graph**
   - Location: Dependency Graph section
   - Problem: S-G's Inputs list S-A (data: measure generated entries) but the edge was absent from the graph edges list
   - Fix: Added `S-A -> S-G (data: token cache for measuring generated entry sizes)` to graph
   - **Status**: FIXED

4. **100% rule mutual exclusivity claim inaccurate**
   - Location: Completeness Check section
   - Problem: Claimed "No FR appears in two implementation sub-problems" but FR-1 maps to both S-A and S-D. The relationship is prerequisite-to-consumer (disjoint deliverables), not scope overlap, but the blanket claim was false.
   - Fix: Reworded to accurately describe the prerequisite-consumer relationship and clarify that no two sub-problems produce the same deliverable
   - **Status**: FIXED

### Minor Issues

1. **Absent edges section incomplete for S-H**
   - Location: Dependency Graph, absent edges
   - Problem: S-H pairwise independence with S-E and S-G not listed
   - Fix: Added `S-E ⊥ S-H` and `S-G ⊥ S-H` to absent edges
   - **Status**: FIXED

2. **Band 3 dependency description imprecise**
   - Location: Bands section
   - Problem: Said "depends on Band 2" but S-H also depends on S-D (Band 1)
   - Fix: Changed to "depends on Band 1 + Band 2"
   - **Status**: FIXED

3. **Q-4 version-change wording misaligned with requirements**
   - Location: Open Questions
   - Problem: Said "deferred past this project" without acknowledging requirements Q-1 frames mechanism selection as a design-phase question
   - Fix: Clarified that mechanism selection happens during design, implementation is deferred
   - **Status**: FIXED

## PDR Criteria Assessment

| Criterion | Verdict | Notes |
|-----------|---------|-------|
| Approach meets requirements (FR traceability) | Pass | All 8 FRs mapped, all NFRs/constraints covered |
| Options selected with rationale | Pass | Each sub-problem states DP with rationale; no "explore options" language |
| Risks and open questions identified | Pass | 5 risks, 5 open questions, all with mitigation or resolution path |
| Scope boundaries explicit (IN/OUT) | Pass | 10 IN items, 7 OUT items, all enumerated |

## Fixes Applied

- S-G: Changed readiness from "Designable" to "Groundable (propagated)" in sub-problem body
- S-G: Updated Band 2 label from "[designable -> after S-C, S-D]" to "[groundable -> designable after S-C]"
- S-G: Updated Readiness Summary from "Designable (propagated groundable)" to "Groundable (propagated)", added S-A to blockers
- S-H: Expanded Inputs to include S-D (hierarchical index for traversal verification)
- S-H: Updated Readiness Summary to list S-D and S-F as blockers
- Dependency Graph: Added `S-D -> S-H` edge
- Dependency Graph: Added `S-A -> S-G` edge
- Dependency Graph: Added `S-E ⊥ S-H` and `S-G ⊥ S-H` absent edges
- Band 3: Changed "depends on Band 2" to "depends on Band 1 + Band 2", added S-D to needs
- Completeness Check: Reworded mutual exclusivity claim to accurately describe FR-1's prerequisite-consumer split
- Q-4: Clarified mechanism selection in design vs implementation deferral

## Positive Observations

- The Phase 4/5 inversion from the prior outline is fully resolved via Tear T-2 (S-C/S-E not torn — S-E waits for grounding)
- Tear T-1 (S-C/S-D) is well-reasoned — hierarchy structure genuinely is format-agnostic, and the mitigation (recursive traversal unaffected by format changes) is substantive, not hope-based
- ICOM annotations on every sub-problem make dependency discovery verifiable — reviewers can trace each graph edge back to its source in Inputs/Outputs
- Readiness propagation correctly prevents S-E from appearing executable prematurely
- Band 0 parallelism (3 concurrent roots) is a material scheduling improvement over the prior linear Phase 1 to 6
- File-set annotations enable merge conflict prediction without reading code
- Mechanism annotations (model tier, worktree/in-tree) enable direct task classification in session.md
- Scope OUT section matches requirements Out of Scope exactly, plus version-change implementation deferral

## Recall Context Applied

Resolved entries that informed review:
- "when recall loads new entries mid-artifact" — verified sub-problem dependencies don't create mid-decomposition consistency issues
- "when converting external documentation to recall entries" — S-G correctly reflects how/when automation profile distinction in its FR-2 reference
- "when too many rules in context" — relevant to NFR-1 scaling; S-D's hierarchical structure addresses this by keeping per-session index loads bounded
- "when grounding identifies gaps in existing structure" — S-C correctly scoped as research without assuming existing structure is wrong
- "when checking complexity before expansion" — S-D flagged as potentially needing internal decomposition during design (line 333 "may need internal decomposition") — appropriate callback

---

**Ready for user presentation**: Yes
