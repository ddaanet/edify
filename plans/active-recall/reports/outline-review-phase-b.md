# Outline Review: Active Recall (Phase B PDR)

**Artifact**: plans/active-recall/outline.md (Rev 2)
**Date**: 2026-03-07
**Mode**: review + fix-all
**Focus**: S-L (Capture-Time Memory Writes), S-K (Memory-Corrector Agent), PDR criteria

## Summary

Outline is technically sound with clear decomposition, well-defined dependency graph, and explicit scope boundaries. All 11 FRs, 4 NFRs, and 6 constraints trace to sub-problems with documented coverage rationale. Key design decisions (branch/leaf separation, two recall modes, submodule shared-branch) have stated rationale. Recent S-L and S-K edits correctly reflect the agreed architectural patterns (tool-gating, delegated agent, continuation-prepend). Six fixes applied: two recall-informed gaps in S-K and S-L, one ungrounded complexity claim, one missing FR-6 verification step, one cross-reference improvement, and one FR-3/Q-4 scope clarification.

**Overall Assessment**: Ready (for Phase B user discussion)

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | S-A + S-D | Complete | Token cache prereq, hierarchy, generated index, embedded keywords |
| FR-2 | S-E | Complete | Trigger class metadata, per-entry decision |
| FR-3 | S-E | Complete | Learning categories, dependency partitioning. Version-change detection: design-only (Q-4 clarified) |
| FR-4 | S-G | Complete | Pipeline, corrector pass, first targets, idempotency |
| FR-5 | S-C | Complete | Grounding research, format spec output |
| FR-6 | S-H | Complete | Pattern docs, regression verification, nested invocation (added) |
| FR-7 | S-F | Complete | Mode reduction, pipeline point updates, recognition gap noted |
| FR-8 | S-B | Complete | Module merge, model unification, deprecation alias, CLI disposition |
| FR-9 | S-I + S-J | Complete | Multi-submodule refactor, submodule creation, propagation |
| FR-10 | S-L | Complete | Capture-time writes, learnings removal, /codify removal, /handoff update |
| FR-11 | S-K | Complete | Agent definition, quality criteria, suppression taxonomy, recall loading (added) |
| NFR-1 | S-D | Complete | Hierarchical lookup scales with depth (fixed: removed ungrounded O(log_k(N)) claim) |
| NFR-2 | S-B + S-D | Complete | Deprecation alias, path migration |
| NFR-3 | S-D | Complete | Incremental migration strategy |
| NFR-4 | S-A + S-D | Complete | Token budget as design target |
| C-1 | S-C -> S-G edge | Complete | Encoded as dependency |
| C-2 | S-D -> S-G edge | Complete | Encoded as dependency |
| C-3 | S-A -> S-D edge | Complete | Encoded as dependency |
| C-4 | S-B + accounting table | Complete | Full infrastructure accounting table |
| C-5 | S-J + S-H verification | Complete | Shared branch + verification step |
| C-6 | S-I | Complete | 42 refs, per-submodule strategy dispatch |

**Traceability Assessment**: All requirements covered. Six gaps identified and fixed.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **S-K missing recall loading requirement**
   - Location: S-K "How (DP)" section
   - Problem: Memory-corrector agent definition lacked any mention of recall mechanism. Per "when corrector agents lack recall mechanism" decision, corrector agents without recall cannot flag project-specific failure modes. This was identified as a gap across 3 agents previously and explicitly fixed.
   - Fix: Added recall loading bullet specifying self-contained loading in agent body (option a from the decision)
   - **Status**: FIXED

2. **S-L missing permanent documentation routing constraint**
   - Location: S-L "How (DP)" section
   - Problem: Capture-time writes described routing to "target decision file, section" but didn't enforce that entries must point to permanent documentation. Per "when adding entries without documentation" decision, orphan index entries degrade the index from discovery mechanism to aspirational wishlist.
   - Fix: Added routing constraint bullet referencing the decision
   - **Status**: FIXED

### Minor Issues

1. **Ungrounded complexity claim in NFR-1 coverage**
   - Location: Completeness Check table, NFR-1 row
   - Problem: Stated "O(log_k(N)) hierarchical lookup" without analysis backing the bound. No section defines branching factor k or proves the bound. This is confabulated methodology per no-confabulation rule.
   - Fix: Changed to descriptive "Hierarchical lookup scales with tree depth, not entry count"
   - **Status**: FIXED

2. **S-K "corrector precedent exists" without reference**
   - Location: S-K Readiness description
   - Problem: Claimed precedent without naming it
   - Fix: Added specific reference to design-corrector, outline-corrector, runbook-corrector agents in `.claude/agents/`
   - **Status**: FIXED

3. **S-H missing nested /recall invocation verification**
   - Location: S-H "How (DP)" section
   - Problem: FR-6 acceptance criteria include "Nested `/recall` invocation from other skills works without special infrastructure" but S-H's verification steps didn't explicitly test this
   - Fix: Added verification step for nested `/recall` invocation
   - **Status**: FIXED

4. **S-L continuation-prepend lacked infrastructure reference**
   - Location: S-L "How (DP)" section
   - Problem: Mentioned continuation-prepend support without referencing the continuation-passing infrastructure it depends on (D-2, D-5 decisions)
   - Fix: Added reference to continuation-passing infrastructure decisions
   - **Status**: FIXED

5. **S-L/S-K corrector timing cross-reference incomplete**
   - Location: S-L Readiness description
   - Problem: Q-5 mentioned as open but phrasing "synchronous vs deferred" didn't reference where Q-5 is resolved
   - Fix: Added "resolved during S-K design" and Q-6 cross-reference for routing heuristic
   - **Status**: FIXED

6. **FR-3/Q-4 scope boundary ambiguous**
   - Location: Open Questions, Q-4
   - Problem: Q-4 says "implementation deferred past this project" but FR-3 acceptance criteria require "Version-change detection mechanism defined (design phase)". The outline needed to clarify that FR-3 is satisfied by design-only output.
   - Fix: Added clarification that FR-3 acceptance criterion is satisfied by design-only output from S-E
   - **Status**: FIXED

## Fixes Applied

- S-K "How (DP)" — added quality criterion for permanent doc requirement, added recall loading bullet with self-contained mechanism
- S-K Readiness — specified corrector precedent references (3 existing agents)
- S-L "How (DP)" — added continuation-passing infrastructure references (D-2, D-5), added permanent documentation routing constraint
- S-L Readiness — added Q-5/Q-6 cross-references for design resolution points
- S-H "How (DP)" — added nested `/recall` invocation verification step (FR-6)
- Completeness Check NFR-1 — replaced ungrounded O(log_k(N)) with descriptive scaling statement
- Open Questions Q-4 — clarified FR-3 design-only scope satisfaction

## Recall Integration Assessment

Recall artifact entries were resolved and checked against outline content:

- **Submodule failure modes (4 entries):** All four patterns correctly integrated in S-I/S-J risk section (line 530). Strategy dispatch and propagation mechanism explicitly account for them.
- **Documentation conversion automation profiles:** S-G correctly defaults pattern catalogs to `when` class with stated rationale matching recall entry.
- **Corrector recall loading:** Gap found and fixed (S-K major issue #1).
- **Permanent documentation requirement:** Gap found and fixed (S-L major issue #2).
- **Recognition gap:** S-F design consideration correctly addresses this via forced-injection path preservation.
- **Continuation-passing:** S-L referenced continuation-prepend but lacked infrastructure connection. Fixed.

## Positive Observations

- Decomposition is clean — sub-problems have disjoint file sets with explicit independence assertions
- Tear points are well-analyzed with risk/mitigation for each
- Readiness propagation through dependency graph is tracked (groundable/designable/executable)
- Band structure directly maps to parallelism opportunities (4 concurrent in Band 0)
- C-4 infrastructure accounting is exhaustive — every existing artifact has a disposition
- Mutual exclusivity check prevents overlapping deliverables
- S-G correctly handles `when` vs `how` automation profile distinction per recall decision
- Known submodule failure modes are pre-integrated into risk section from recall entries
- S-L correctly specifies opus for mechanism (behavioral changes to agent directives) per artifact type override rule

## Recommendations

For Phase B user discussion:

- **Q-5 (corrector timing)** is the highest-impact open design decision. Synchronous per-write gives immediate quality but adds latency to every `remember:`. Post-handoff batching amortizes cost but delays feedback. User preference on write latency vs quality assurance feedback loop.
- **Q-7 (migration strategy)** affects S-J/S-D ordering. The outline recommends option (b) — empty submodule, build hierarchy directly. Confirm with user before locking.
- **S-D internal decomposition** is flagged as a risk. During `/design`, consider whether S-D should split into sub-steps (parser, migration tooling, index generation, hook/skill path updates) or remain monolithic for runbook.
- **FR-3 version-change detection scope:** Design-only in this project. User should confirm this deferral is acceptable or if basic implementation (e.g., lockfile diff trigger) should be in scope.

---

**Ready for user presentation**: Yes
