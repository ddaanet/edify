# Runbook Outline Review: worktree-merge-from-main

**Artifact**: plans/worktree-merge-from-main/runbook-outline.md
**Requirements**: plans/worktree-merge-from-main/requirements.md
**Date**: 2026-03-02
**Mode**: review + fix-all

## Summary

Well-structured outline with correct phase progression (foundation, resolution policies, CLI/E2E, documentation). The original outline missed two critical pipeline functions (`_phase3_merge_parent`, `_detect_merge_state`) and had an incorrect FR-5 mapping. Code review of `merge_state.py` revealed that `_detect_merge_state` and `_recover_untracked_file_collision` are already direction-agnostic, eliminating one planned cycle. All issues fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Items | Coverage | Notes |
|-------------|-------|-------|----------|-------|
| FR-1 session.md keep-ours | Phase 2 | 2.1, 2.2 | Complete | resolve + remerge both adapted |
| FR-2 learnings theirs-base + ours delta | Phase 3 | 3.1, 3.2 | Complete | ours/theirs inversion in diff3 |
| FR-3 accept main's structural changes | Phase 2 | 2.3, 2.4 | Complete | Delete/modify auto-resolution, E2E verified |
| FR-4 sandbox bypass | Phase 4 | Mode D docs | Complete | Documented in Mode D skill text (runtime concern, not code) |
| FR-5 idempotent resume | Phase 1 | (shared) | Complete | `merge_state.py` already direction-agnostic per code review |
| NFR-1 minimal output | All | Per function | Complete | Consistent with existing merge output style |
| NFR-2 no data loss | Phase 2, 3 | E2E tests 2.4, 3.4 | Complete | session.md, learnings.md verified in both E2E tests |
| C-1 unify with existing merge infra | Phase 1 | 1.1-1.5 | Complete | Direction param through shared pipeline |
| C-2 requires clean tree | Phase 1 | 1.2 | Complete | Reuses `_check_clean_for_merge` |
| C-3 worktree skill integration | Phase 3, 4 | 3.3, 3.4, Phase 4 | Complete | CLI flag + Mode D skill |

**Coverage Assessment**: All requirements covered.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles/Steps | Complexity | Percentage | Assessment |
|-------|-------------|------------|------------|------------|
| 1 | 5 | Medium | 31% | Balanced |
| 2 | 4 | Medium | 25% | Balanced |
| 3 | 4 | Medium | 25% | Balanced |
| 4 | 2 | Low | 12% | Balanced (inline, appropriate size) |

**Balance Assessment**: Well-balanced. No phase exceeds 31%.

### Complexity Distribution

- Low complexity phases: 1 (Phase 4 — documentation only)
- Medium complexity phases: 3 (Phases 1-3 — code + test changes)
- High complexity phases: 0

**Distribution Assessment**: Appropriate. Medium reflects the parameterization pattern (branching on `from_main` flag) applied across existing functions. No phase introduces novel algorithms.

## Review Findings

### Critical Issues

1. **Missing `_phase3_merge_parent` adaptation**
   - Location: Phase 1
   - Problem: No cycle covered the actual `git merge` invocation in `_phase3_merge_parent`. For from-main, the merge target changes: `git merge --no-commit --no-ff slug` must use "main" as target, and the merge message must reflect direction. Without this, the merge command would try to merge the worktree branch into itself.
   - Fix: Added Cycle 1.5 covering `_phase3_merge_parent` adaptation with direction-aware merge target and message.
   - **Status**: FIXED

2. **Incorrect FR-5 mapping**
   - Location: Requirements mapping table
   - Problem: FR-5 was mapped to "1.3; verified Phase 3 Cycle 3.3" but Cycle 1.3 covers `_phase4_merge_commit_and_precommit` (lifecycle skip), not idempotent resume. The original claimed `_detect_merge_state` needed adaptation, but code review revealed it already works for both directions.
   - Fix: Updated FR-5 mapping to note shared infrastructure is already direction-agnostic, with explanation. Removed phantom Cycle 1.5 for `merge_state.py`.
   - **Status**: FIXED

### Major Issues

1. **Remerge function signature propagation unspecified**
   - Location: Cycles 2.2, 3.2
   - Problem: `remerge_session_md()` and `remerge_learnings_md()` don't currently accept `from_main` parameter. Cycle 1.3 passes `from_main` to them, but the receiving functions need signature changes. Outline didn't mention this.
   - Fix: Added `from_main: bool = False` parameter requirement to Cycles 2.2 and 3.2 descriptions, plus regression tests for worktree-to-main behavior.
   - **Status**: FIXED

2. **Delete/modify conflict detection mechanism underspecified**
   - Location: Cycle 2.3
   - Problem: Original said "in `_auto_resolve_known_conflicts`" but that function does path-based matching (agent-core, session.md, learnings.md). Delete/modify is a conflict type, not a path pattern. Also, expansion guidance incorrectly suggested `git diff --diff-filter` which doesn't work during active merge conflicts.
   - Fix: Updated Cycle 2.3 to specify `git status` conflict markers (UD/DU). Updated expansion guidance to use `git status --porcelain` and corrected the anti-pattern about `git diff --diff-filter`.
   - **Status**: FIXED

3. **Phase 4 missing checkpoint**
   - Location: Phase 4
   - Problem: No checkpoint after skill file updates. Enumeration site errors (recall: "when adding new variant") affect runtime behavior and need validation.
   - Fix: Added checkpoint after Phase 4 steps.
   - **Status**: FIXED

4. **Phase 4 missing enumeration site coverage**
   - Location: Phase 4
   - Problem: Only Mode D addition was listed. SKILL.md has multiple references to merge behavior (Principles, Continuation, Mode C mentions) that need updating for bidirectional awareness per recall "when adding new variant to an enumerated system."
   - Fix: Added Step 4.2 for enumeration site updates with specific sections to grep.
   - **Status**: FIXED

### Minor Issues

1. **Missing Notes column in requirements mapping**
   - Location: Requirements mapping table
   - Problem: Table lacked Notes column per expected format, reducing traceability clarity.
   - Fix: Added Notes column with explanatory text for each mapping.
   - **Status**: FIXED

2. **Phase 4 steps unnumbered**
   - Location: Phase 4
   - Problem: Step was listed as a bullet without step number, inconsistent with other phases.
   - Fix: Numbered as Steps 4.1 and 4.2.
   - **Status**: FIXED

3. **Expansion guidance missing test pattern recall**
   - Location: Expansion Guidance section
   - Problem: Recall entry "when tests simulate merge workflows" (branch as merged parent, amend preserves) not referenced. This is directly relevant to all merge test fixtures.
   - Fix: Added to test infrastructure section of expansion guidance.
   - **Status**: FIXED

4. **No growth projection**
   - Location: Expansion Guidance section
   - Problem: 5 files modified with no growth projection. `merge.py` (387 lines) projects to ~437, above 400-line threshold.
   - Fix: Added growth projection for all 5 target files with measured current sizes and estimated additions. Flagged `merge.py` as exceeding threshold with extraction recommendation.
   - **Status**: FIXED

5. **Expansion guidance had incorrect delete/modify detection advice**
   - Location: Expansion Guidance, Cycle 2.3 note
   - Problem: Original said "use `git diff --diff-filter=`" which doesn't work during active merge conflict state.
   - Fix: Changed to `git status --porcelain` conflict markers with explicit note not to use `git diff --diff-filter`.
   - **Status**: FIXED

6. **Regression preservation not mentioned**
   - Location: Expansion Guidance
   - Problem: No explicit note about preserving existing worktree-to-main behavior, especially the completed task filtering from recall "when merging completed tasks from branch."
   - Fix: Added regression preservation section to expansion guidance noting all `from_main` code paths must gate on the flag.
   - **Status**: FIXED

## Fixes Applied

- Requirements mapping table: added Notes column, corrected FR-5 mapping from "1.3" to "(shared)" with direction-agnostic explanation, updated C-1 range to 1.1-1.5, added E2E test references to NFR-2
- Phase 1: added Cycle 1.5 (`_phase3_merge_parent` adaptation), removed incorrect Cycle 1.5 (`merge_state.py` — unnecessary per code review)
- Cycle 2.2: added `from_main` parameter requirement and regression test note
- Cycle 2.3: updated detection mechanism from path-based to conflict-type-based (`git status` markers), added `from_main` parameter to `_auto_resolve_known_conflicts`
- Cycle 3.2: added `from_main` parameter requirement and regression test note
- Phase 4: numbered steps (4.1, 4.2), added Step 4.2 for enumeration sites, added checkpoint
- Expansion Guidance: restructured with headers, added test pattern recall, corrected delete/modify detection, added regression preservation section, added growth projection with measured file sizes, added enumeration sites section, added consolidation candidates section

## Design Alignment

No separate design.md exists. Requirements.md serves as the combined requirements+design document with C-1 specifying exact shared/direction-specific function mapping.

- **Architecture**: Aligned. Direction parameter threads through existing 4-phase pipeline per C-1.
- **Module structure**: Aligned. Changes span merge.py, resolve.py, remerge.py, cli.py, SKILL.md — all referenced in C-1 and requirements References section.
- **Key decisions**: All 4 key decisions in outline are consistent with requirements (direction threading per C-1, slug semantics per Q-1, resolution inversion per C-1 direction-specific policies, CLI contract per Q-1).

## Positive Observations

- Clean separation: Phase 1 (pipeline plumbing) before Phase 2-3 (resolution policies) is the right order — resolution functions need the `from_main` parameter threaded through before they can branch on it
- Both resolve and remerge functions covered for each file type — the outline correctly identifies that both code paths need adaptation
- E2E tests (2.4, 3.4) exercise realistic merge scenarios with real git repos, consistent with testing conventions
- Constraint C-1 (unify with existing infra) is well-reflected — no new modules, only parameter additions to existing functions
- Phase 4 as inline type is appropriate — no behavioral code, only documentation

## Recommendations

- `merge.py` growth (projected ~437 lines): during expansion, consider whether direction-specific conditionals can be extracted into a helper or whether the function decomposition is already sufficient
- The `_auto_resolve_known_conflicts` function is accumulating responsibility — after this change it handles agent-core, session.md, learnings.md, AND delete/modify conflicts. Monitor for extraction opportunity
- Consider whether the E2E tests (2.4, 3.4) should share a fixture or remain independent — shared fixture reduces setup duplication but couples test files

---

**Ready for full expansion**: Yes
