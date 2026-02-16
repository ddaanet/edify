# Design Review: Workwoods

**Design Document**: plans/workwoods/design.md
**Review Date**: 2026-02-16
**Reviewer**: design-vet-agent (opus)

## Summary

Comprehensive design for replacing manual jobs.md tracking with filesystem-inferred plan state, adding cross-tree awareness, upgrading wt-ls, implementing per-section merge strategies, and enabling bidirectional worktree merge. The design is well-structured with clear data models, binding classification tables, grounded codebase references, and complete phase decomposition.

**Overall Assessment**: Needs Minor Changes

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Vet naming convention variance not addressed**
   - Problem: The vet chain convention table maps `runbook-phase-N.md -> reports/phase-N-review.md`, but the when-recall plan uses `checkpoint-N-vet.md` for phase-level reports. The design also did not address escalation suffix variants like `runbook-outline-review-opus.md` found in worktree-merge-data-loss.
   - Impact: Phase 2 implementation would produce false staleness for plans using non-standard naming, or miss valid vet reports entirely.
   - Fix Applied: Added "Naming variance" paragraph after the vet chain table specifying fallback glob pattern for non-standard names, and added escalation variant handling to the iterative reviews section.

2. **Merge resolution chain context missing for Phase 6 removal**
   - Problem: Phase 6 lists "Remove `_resolve_jobs_md_conflict()` from `merge.py`" but doesn't clarify that the merge resolution chain in `_phase3_merge_parent` calls session, learnings, and jobs resolvers sequentially. A planner could accidentally remove the wrong function or break the call chain.
   - Impact: Planner might not understand which call to remove from the chain or could accidentally affect adjacent resolvers.
   - Fix Applied: Added parenthetical clarifying that session and learnings resolvers remain, and that only the jobs call is removed from `_phase3_merge_parent`.

### Minor Issues

1. **FR-5 title inconsistency between requirements and design**
   - Problem: requirements.md titles FR-5 "Additive task merge" but the design broadened it to "Per-section session.md merge strategies" after discussion round D-5. A planner checking requirements could be confused by the narrower title.
   - Fix Applied: Added note to FR-5 entry in design's Requirements section explaining the title broadening from discussion.

2. **Documentation Perimeter ambiguous about missing architecture.md**
   - Problem: The parenthetical "(if it exists; not found in worktree)" is ambiguous — unclear whether planner should search harder or skip.
   - Fix Applied: Changed to "(skip if not found in worktree)" for unambiguous planner instruction.

3. **Phase 5 execute-rule.md transition ordering unclear**
   - Problem: Phase 5 (general portion) switches execute-rule.md STATUS from jobs.md to planstate, but the Unscheduled Plans section in execute-rule.md also references jobs.md for status values. The relationship between Phase 5 (adoption) and Phase 6 (removal) wasn't explicit for this specific touchpoint.
   - Fix Applied: Added note clarifying that Unscheduled Plans fully transitions to planstate in Phase 5, with the CLAUDE.md @-reference removal deferred to Phase 6.

## Requirements Alignment

**Requirements Source:** plans/workwoods/requirements.md

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Phase 3 (aggregation) + Phase 4 (CLI) |
| FR-2 | Yes | Phase 2 (vet.py mtime detection) |
| FR-3 | Yes | Phase 1 (inference.py + state rules table) |
| FR-4 | Yes | Phase 5 (skill update, D-4) |
| FR-5 | Yes | Phase 5 (per-section merge table, D-5) |
| FR-6 | Yes | Phase 6 (elimination + archive, D-3) |
| NFR-1 | Yes | All phases use read-only aggregation |
| NFR-2 | Yes | Each tree owns session.md; aggregation is read-only |
| NFR-3 | Yes | All state git-versioned or computed |
| C-1 | Yes | Phase 2 (filesystem mtime) |
| C-2 | Yes | Phase 3 (git commit hash anchor) |
| C-3 | Yes | Noted as already satisfied |

**Gaps:** None. All requirements traced to design elements. FR-5 title broadened from requirements during discussion (noted in design).

## Positive Observations

- **Binding classification tables**: The state inference rules table and per-section merge strategy table are marked as binding specifications, eliminating ambiguity for planners.
- **Data models are concrete**: Python dataclasses with explicit types, field comments, and clear relationships between models. `PlanState.gate` as `str | None` with advisory semantics is a clean design choice.
- **Codebase grounding**: Design references verified functions (`_resolve_session_md_conflict`, `find_section_bounds`, `extract_task_blocks`, `_parse_worktree_list`, `focus_session`) that all exist in the codebase. File paths verified via Glob.
- **External dependency handling**: D-6 correctly isolates worktree-merge-data-loss as an execution dependency with a clear gate (Phases 1-4 independent, Phase 5 blocked until Track 1+2 deployed).
- **Phase type classification**: Each phase is explicitly tagged TDD or mixed with rationale, enabling correct runbook expansion.
- **Affected files table**: Complete and verified against codebase — all "Modify" targets exist, all "New" targets are in appropriate locations, all "Delete" targets exist.
- **Test strategy grounded in existing patterns**: Real git repos via `tmp_path` follows established worktree test suite pattern, avoiding mocked subprocess anti-pattern.
- **State inference refinement**: The explicit note that `outline.md` without `design.md` stays at `requirements` status (not `designed`) resolves the outline's Q-1 and prevents premature status promotion.

## Recommendations

- Phase 2 test suite should include a test case with `checkpoint-N-vet.md` naming to verify the fallback glob pattern works for legacy plans.
- Phase 5 Blockers extraction test cases should cover: empty Blockers section, no Blockers section in theirs, multiple blocker items with continuation lines, and slug tagging format.
- Consider whether `VetChain.report` should be `list[str]` instead of `str | None` to naturally handle multiple matching reports (iterative + escalation variants). Current design handles this at the function level rather than the data model level — either works, but the planner should be aware of the choice.

## Next Steps

- Route to `/runbook` for phase expansion
- No blocking issues remain
