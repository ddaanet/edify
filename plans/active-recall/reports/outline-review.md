# Outline Review: active-recall (Rev 2)

**Artifact**: plans/active-recall/outline.md
**Date**: 2026-03-06
**Mode**: review + fix-all (PDR criteria)

## Summary

Rev 2 is a substantial improvement over Rev 1 — the phase-based structure has been replaced with sub-problem decomposition (DSM banding), explicit dependency typing, readiness classification, and tear point analysis. Traceability is strong: the Completeness Check table maps all 11 FRs, 4 NFRs, and 6 constraints. Gaps were limited to NFR-2 CLI enumeration, C-4 systematic accounting, recall-informed failure modes for submodule work, and missing automation profile context from recall entries. All fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | S-A + S-D | Complete | Token cache prereq, hierarchy, generated index, embedded keywords |
| FR-2 | S-E | Complete | Trigger class metadata, per-entry decision |
| FR-3 | S-E | Complete | Learning categories, dependency partitioning |
| FR-4 | S-G | Complete | Pipeline, corrector pass, first targets, idempotency |
| FR-5 | S-C | Complete | Grounding research, format spec output |
| FR-6 | S-H | Complete | Pattern documentation and regression verification |
| FR-7 | S-F | Complete | Mode reduction (5 to 2), pipeline point updates |
| FR-8 | S-B | Complete | Three-module merge, model unification, deprecation alias |
| FR-9 | S-I + S-J | Complete | Multi-submodule refactor, submodule creation, propagation |
| FR-10 | S-L | Complete | Capture-time writes, learnings.md removal, /codify removal |
| FR-11 | S-K | Complete | Corrector agent, quality criteria, suppression taxonomy |
| NFR-1 | S-D (Completeness Check) | Complete | O(log_k(N)) lookup noted |
| NFR-2 | S-B (fixed) | Complete | All CLI commands enumerated with disposition |
| NFR-3 | S-D | Complete | Incremental migration strategy |
| NFR-4 | S-A + S-D | Complete | Token budget as design target, threshold deferred to S-D design |
| C-1 | S-C -> S-G edge | Complete | Format grounding before bulk conversion |
| C-2 | S-D -> S-G edge | Complete | Hierarchy before bulk conversion |
| C-3 | S-A -> S-D edge | Complete | Token counting before split |
| C-4 | S-B + accounting table (fixed) | Complete | Full infrastructure item mapping added |
| C-5 | S-J + S-H | Complete | Cross-worktree visibility via shared branch |
| C-6 | S-I | Complete | Multi-submodule with per-submodule strategy |

**Traceability Assessment**: All requirements covered. Open questions Q-1 through Q-7 appropriately deferred to sub-problem design phases.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **NFR-2 CLI disposition incomplete**
   - Location: S-B
   - Problem: Only `_when` deprecation alias mentioned. Requirements list `_recall check`, `_recall diff` as needing backward compat. No enumeration of CLI commands and their migration disposition.
   - Fix: Added NFR-2 CLI disposition table listing all four CLI commands with their status (preserve, alias, removal timeline).
   - **Status**: FIXED

2. **Known submodule failure modes absent from risks**
   - Location: Risks section
   - Problem: Four documented submodule failure patterns from recall (core.worktree stale after rm, diverging commits during orchestration, task agents skipping pointer updates, no-op merge orphaning branches) not referenced. S-I refactors submodule handling and S-J creates a new submodule — both directly exposed to these failure modes.
   - Fix: Added "Known submodule failure modes (S-I, S-J)" risk entry enumerating all four patterns with requirement that S-I strategy dispatch and S-J propagation account for them.
   - **Status**: FIXED

3. **C-4 infrastructure accounting not systematic**
   - Location: Completeness Check table
   - Problem: C-4 lists 9+ specific infrastructure items (3 module dirs, index file, learnings, 4 skills, hook, test files). Outline mentions C-4 in S-B controls but no systematic mapping of each item to its handling sub-problem.
   - Fix: Added C-4 infrastructure accounting table mapping all 10 infrastructure items to their handling sub-problems.
   - **Status**: FIXED

### Minor Issues

1. **FR-2/FR-4 automation profile distinction not referenced**
   - Location: S-E, S-G
   - Problem: Recall entry "when converting external documentation to recall entries" provides critical insight — `how` entries are automation-safe, `when` entries require hand-curation. This distinction directly informs S-G pipeline design (corrector intensity per class) and S-E metadata model (class needed for routing). Not mentioned in outline.
   - Fix: Added recall note to S-E about automation profiles and corrector intensity implications.
   - **Status**: FIXED

2. **Recognition vs retrieval gap not noted for mode simplification**
   - Location: S-F
   - Problem: Recall entry "when evaluating recall system effectiveness" warns that lookup improvements only help retrieval, not recognition (agent knowing when to look). S-F's mode simplification must preserve forced-injection paths (PreToolUse hook, pipeline recall points) that bypass recognition.
   - Fix: Added design consideration to S-F about recognition gap and forced-injection path preservation.
   - **Status**: FIXED

3. **Hardcoded reference count discrepancy with requirements**
   - Location: S-I
   - Problem: S-I says "42 occurrences across 4 files", requirements say "38 hardcoded plugin references across 4 files". Verified via grep: 42 is the correct count (requirements stale).
   - Fix: No change to outline (42 is correct). Requirements.md has the stale number.
   - **Status**: NOTED (requirements.md needs update, not outline)

## Fixes Applied

- S-B: Expanded FR description to reference all CLI commands, not just `_when`
- S-B: Added `_recall check`/`_recall diff` preservation to How section
- S-B: Added NFR-2 CLI disposition table with all 4 commands
- Completeness Check: Updated C-4 reference to include accounting table
- Completeness Check: Added C-4 infrastructure accounting table (10 items mapped)
- Risks: Added known submodule failure modes entry (4 patterns from recall)
- S-E: Added recall note on automation profiles (how=automation-safe, when=hand-curation)
- S-F: Added design consideration on recognition vs retrieval gap

## Positive Observations

- Sub-problem decomposition (DSM banding) is a significant structural improvement over phase-based ordering — separates logical decomposition from scheduling
- Dependency graph is thorough: 17 edges with typed dependencies (structural, data, knowledge, merge), 18 explicitly absent edges with rationale
- Tear point analysis (T-1, T-2, T-3) makes coupling decisions explicit with cost/benefit reasoning
- Readiness classification (executable/designable/groundable) with propagation semantics enables correct pipeline routing
- Band structure naturally exposes parallelism (4 concurrent in Band 0, up to 4 in Band 2)
- S-J/S-D design question about ordering is well-articulated with a clear recommendation
- Completeness Check with mutual exclusivity verification is rigorous
- Scope boundaries explicitly enumerate IN and OUT items

## Recommendations

- **Requirements.md stale count:** Update C-6 from "38 hardcoded" to "42 hardcoded" (verified via grep)
- **S-D internal decomposition:** Outline notes S-D is the largest sub-problem and "may need internal decomposition during /design phase." This is appropriate — flag it during S-D design if step count exceeds runbook limits
- **Token budget threshold (Q-1):** Early resolution during S-D design enables informed split decisions. Consider measuring current memory-index.md token count as a baseline during S-A implementation

## Recall Context Applied

Resolved entries from `plans/active-recall/recall-artifact.md`:
- "when converting external documentation to recall entries" — applied to S-E automation profile distinction
- "when evaluating recall system effectiveness" — applied to S-F recognition gap consideration
- "when removing worktrees with submodules" — informed submodule failure modes risk
- "when submodule commits diverge during orchestration" — informed submodule failure modes risk
- "when task agents skip submodule pointer" — informed submodule failure modes risk
- "when no-op merge orphans branch" — informed submodule failure modes risk
- "when corrector agents lack recall mechanism" — verified S-K design includes clean context loading (satisfied)
- "when requiring per-artifact vet coverage" — verified all write paths route through S-K corrector (satisfied)

---

**Ready for user presentation**: Yes — all issues fixed. One noted item for requirements.md (stale reference count).
