# Deliverable Review: Workwoods Code Artifacts

**Scope**: All production code deliverables from workwoods plan (Phases 1-6)
**Date**: 2026-02-17
**Design Reference**: `plans/workwoods/design.md`

## Summary

The planstate module delivers a coherent, well-structured replacement for manual jobs.md tracking. Core inference, vet staleness, and aggregation work correctly and conform to the design's stated architecture. The merge/session upgrades implement per-section strategies faithfully. Several data model deviations from the design spec are intentional simplifications, but a few represent genuine gaps (gate computation covers only 1 of 4 gate types, `ready` next-action format deviates, `SOURCE_TO_REPORT_MAP` is hardcoded to 6 phases). The validation replacement is clean and the jobs.md elimination is complete.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Gate computation covers only `design.md` stale case**
   - Location: `inference.py:83-91`
   - Problem: Design spec (D-7) defines 4 gate conditions: design vet stale, outline vet stale, phase N vet stale, runbook outline vet stale. Implementation only checks `chain.source == "design.md"` then breaks. The other 3 gate types are never generated.
   - Note: Session.md documents "Gate wiring incomplete in display path" (vet_status_func never passed in production). This is about a *separate* issue: even when vet_status_func IS passed (e.g., in tests or future wiring), only 1 of 4 gate messages can be produced.
   - Suggestion: Implement the full gate priority chain per design: design > runbook outline > phase-level > outline. Each stale chain.source should map to its corresponding gate message.

2. **`ready` status next-action deviates from design**
   - Location: `inference.py:52`
   - Problem: Implementation returns `/orchestrate {plan_name}` but design spec says `/orchestrate plans/<name>/orchestrator-plan.md`. The design's next-action column for `ready` status explicitly references the orchestrator-plan.md path. Consumers parsing this string to construct commands will get different behavior.
   - Suggestion: Change to `f"/orchestrate plans/{plan_name}/orchestrator-plan.md"` to match design spec.

3. **`SOURCE_TO_REPORT_MAP` hardcodes phases 1-6**
   - Location: `vet.py:8-18`
   - Problem: Plans with 7+ phases will have no vet chain entries for phases 7 onward. The design's naming convention table shows the pattern `runbook-phase-N.md` -> `reports/phase-N-review.md` as a general convention, not limited to 6 phases. Implementation should discover phase files dynamically rather than enumerating them.
   - Suggestion: Replace static map entries for phases with dynamic discovery: glob `runbook-phase-*.md` in the plan directory, extract phase numbers, and construct report paths programmatically. Keep the non-phase entries (outline.md, design.md, runbook-outline.md) as static mappings.

4. **`TreeInfo` is missing most `TreeStatus` fields from design**
   - Location: `aggregation.py:16-31`
   - Problem: Design specifies `TreeStatus` with fields: path, slug, branch, is_main, commits_since_handoff, latest_commit_subject, latest_commit_timestamp, is_dirty, task_summary. Implementation has `TreeInfo` (renamed) with only: path, branch, is_main, slug, latest_commit_timestamp. The helper functions `_commits_since_handoff()`, `_is_dirty()`, `_task_summary()`, `_latest_commit()` exist but their results are not stored in TreeInfo. The display module (`display.py`) recomputes these values via separate subprocess calls instead of using aggregated data.
   - Note: Session.md documents `_task_summary` not wired to display. This covers the broader issue: TreeInfo is a thin struct that forces display.py to duplicate all the git queries that aggregation.py already knows how to do. The display module runs ~6 subprocess calls per tree that `aggregate_trees()` could have provided.
   - Suggestion: Either populate TreeInfo with all design-specified fields during aggregation (single pass), or accept this as intentional deviation and document why.

### Minor Issues

1. **`VetStatus` missing `plan_name` field**
   - Location: `models.py:17-27`
   - Problem: Design specifies `VetStatus(plan_name, chains, any_stale)`. Implementation omits `plan_name`. The `any_stale` is correctly implemented as a property. Without `plan_name`, a VetStatus cannot self-identify which plan it belongs to when aggregated in a list.
   - Note: Currently `get_vet_status()` takes `plan_dir` as input so the caller knows the context. Acceptable deviation if VetStatus is never stored in collections without external key.

2. **`AggregatedStatus` missing `vet_statuses` field**
   - Location: `aggregation.py:187-193`
   - Problem: Design specifies `AggregatedStatus(trees, plans, vet_statuses)`. Implementation has only `plans` and `trees`. Vet status per plan is not aggregated. The design envisions `vet_statuses: list[VetStatus]` as a first-class field for consumers to access staleness information without re-computing.
   - Note: Since gate wiring is incomplete (known issue), vet_statuses would currently be empty. Acceptable to defer, but the structural omission means future wiring requires adding this field.

3. **`_determine_status` returns `requirements` for directories with no recognized artifacts**
   - Location: `inference.py:31-39`
   - Problem: If a directory has files but none match the recognized set (no requirements.md, design.md, etc.), `_determine_status` falls through to return `"requirements"`. The caller (`infer_state`) correctly handles this by checking `artifacts` emptiness first (line 76), so this is defense-in-depth rather than a bug. But `_determine_status` alone is misleading if called independently.
   - Note: Low risk since `_determine_status` is private and always called after artifact check.

4. **`exempt_paths` removed `jobs.md` but uses substring matching**
   - Location: `merge.py:84-89`
   - Problem: The exempt_paths set in `_phase1_validate_clean_trees` uses `any(p in line for p in exempt_paths)` which is substring matching. `"agents/session.md"` would match a hypothetical file `agents/session.md.bak`. Not a current bug but fragile pattern.
   - Note: Pre-existing pattern, not introduced by workwoods. Noting for completeness.

5. **display.py `format_tree_header` uses different commit counting method than aggregation.py**
   - Location: `display.py:26-58` vs `aggregation.py:85-121`
   - Problem: `_commits_since_handoff()` in aggregation.py counts commits since the last commit that touched session.md (design spec: `git log -1 --format=%H -- agents/session.md` as anchor). `format_tree_header()` in display.py uses `git log --oneline --follow agents/session.md` to find the oldest session.md commit, then counts from there. These compute fundamentally different numbers. The aggregation version matches the design spec; the display version does not.
   - Note: Since `format_rich_ls` calls `aggregate_trees()` but then ignores TreeInfo for commit counting (see major issue #4), the display shows the wrong counting algorithm.

6. **`_find_iterative_report_for_source` fallback for non-phase sources is greedy**
   - Location: `vet.py:97-105`
   - Problem: For non-phase sources, it globs `{report_base}*.md`. For `outline-review`, this would match `outline-review.md`, `outline-review-2.md`, but also `outline-review-opus.md` and even `outline-review-something-unrelated.md`. The design says "Escalation variants (`*-opus.md`) are treated as additional reviews -- highest mtime among all matching reports wins" which this glob correctly handles. But any file matching `outline-review*.md` (e.g., `outline-review-notes.md`) would be incorrectly included.
   - Note: Low risk given the controlled naming in practice.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Cross-tree status display | Partial | `aggregate_trees()` collects trees and plans correctly. But TreeInfo lacks commits_since_handoff, is_dirty, task_summary. Display recomputes these values via separate git calls. Sort by latest_commit_timestamp implemented. |
| FR-2: Vet artifact staleness | Satisfied | `get_vet_status()` implements mtime-based detection with iterative review support. Missing report = stale. Fallback glob for naming variants. |
| FR-3: Plan state inference | Satisfied | `infer_state()` scans artifacts, determines status by priority (ready > planned > designed > requirements). `list_plans()` aggregates across directory. Exclusions (reports, claude) handled in validator. |
| FR-4: Bidirectional merge | Satisfied | `merge.py` does not delete worktrees. FR-4 was a skill update (Mode C no auto-rm), not code. Code already bidirectional-compatible. |
| FR-5: Per-section merge strategies | Satisfied | `resolve.py:_merge_session_contents()` implements classification table: squash (keep ours) for Status/Completed/Worktree/Reference/Next, additive for Pending Tasks, evaluate+tag for Blockers. Slug propagation through call chain fixed in post-vet. |
| FR-6: Eliminate jobs.md | Satisfied | `validation/jobs.py` deleted. `validation/planstate.py` replaces it. No remaining `jobs.md` or `jobs.py` references in validation or merge code. `_check_clean_for_merge` exempt_paths no longer includes jobs.md. |
| NFR-1: No writes during status | Satisfied | All planstate functions are read-only. `aggregate_trees()` only runs git commands and reads files. No writes. |
| NFR-2: No unversioned shared state | Satisfied | Each tree's session.md is its own. Aggregation is read-only cross-tree scan. |

**Gaps:**
- FR-1 partially satisfied due to TreeInfo data model thinness (major issue #4)
- Gate computation incomplete (major issue #1) affects FR-2/FR-3 integration

## Positive Observations

- Clean module separation: inference, vet, aggregation, models are orthogonal with minimal coupling
- `_collect_artifacts` and `_determine_status` are well-factored — easy to extend for new artifact types
- `extract_blockers()` correctly handles continuation lines and blank line termination
- Per-section merge strategy in `_merge_session_contents()` is faithful to the D-5 classification table
- `_find_best_report()` correctly handles the iteration number vs mtime priority (numbered > unnumbered)
- `_check_plan_consistency()` catches two important invariants: steps without runbook-phase files, and orchestrator-plan without steps
- `aggregate_trees()` main-wins-on-conflict strategy is correctly implemented (process worktrees first, then main overwrites)
- Error handling in git subprocess calls is consistent: `check=False` with explicit return code checks, graceful degradation to empty/zero values
- `VetStatus.any_stale` as a computed property avoids staleness of a cached boolean
- `_phase3_merge_parent` correctly distinguishes merge conflicts (MERGE_HEAD exists) from merge abort failures

## Recommendations

- Prioritize major issue #3 (hardcoded phase map): plans with 7+ phases will silently lack vet coverage. This is the most likely to cause real-world problems since the fix is mechanical (glob-based discovery).
- Major issue #2 (next-action format) is a quick fix but matters for automation consumers that parse the string.
- Major issues #1 and #4 are larger structural gaps. #4 (TreeInfo thinness) is the root cause of #5 (duplicate git calls in display). Resolving #4 automatically fixes #5.
- Consider whether the rename from `TreeStatus` to `TreeInfo` was intentional API simplification or accidental. If intentional, document the deviation from design.

## Next Steps

- Fix major issues #2 and #3 (quick, mechanical)
- Decide on major issues #1 and #4: fix now or document as known deviations with follow-up task
