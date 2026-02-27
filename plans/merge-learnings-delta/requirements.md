# Merge Learnings Delta

## Problem

When merging a worktree branch that diverged before a learnings consolidation on main, `claudeutils _worktree merge` brings in the branch's full pre-consolidation `agents/learnings.md` over main's consolidated version. Git's merge strategy sees the branch version as a superset and favors it, silently reverting the consolidation.

**Observed:** 30-line (consolidated) → 222-line (pre-consolidation + branch additions) after merge. 175 lines were duplicates of content already consolidated into permanent documentation (`agents/decisions/*.md`, `agent-core/fragments/*.md`).

**Root cause:** Git textual merge has no semantic understanding of consolidation. The branch's learnings.md is a strict superset of the common ancestor, so git takes the branch version. Main's version is shorter (post-consolidation) and git treats the deletions as conflicting with the branch's additions.

**Scope:** `agents/learnings.md` is the primary target. `agents/session.md` has similar merge semantics but is handled by existing ours-strategy resolution. This requirements doc focuses on learnings.md only.

**Both merge directions affected:**
- **Branch → main** (`_worktree merge`): Main consolidated, branch has pre-consolidation content. Observed case.
- **Main → branch** (merge-from-main / catch-up): Branch has pre-consolidation content, main consolidated since branch point. Same divergence, reversed roles — the "local" side has stale content, "incoming" side has consolidated version. The reconciliation strategy is symmetric: consolidated version is the base, delta from the other side is appended.

## Current State

**The segment-level diff3 merge infrastructure already handles this problem.** The following code exists and runs on all merge paths:

- `remerge_learnings_md()` (remerge.py) — Phase 4 remerge, runs on ALL merge paths before commit
- `resolve_learnings_md()` (resolve.py) — Phase 3 conflict resolution
- `diff3_merge_segments()` (resolve.py) — three-way merge using `parse_segments()` heading boundaries
- `parse_segments()` (validation/learnings.py) — splits learnings.md by `## ` headings

**How diff3 handles consolidation divergence:** Given base (pre-consolidation), ours/HEAD (main, consolidated), theirs/MERGE_HEAD (branch, pre-consolidation + new entries):
- Entries deleted from ours (consolidation removed them) but unchanged in theirs → deleted (consolidation respected) — `_resolve_one_sided_deletion` Rows 10/11
- New entries in theirs not in base → appended — Row 1 + post-loop catch-all
- Branch modified entries that ours consolidated away → conflict — Rows 12/13

This IS the "consolidated base + delta" strategy. No consolidation marker is needed — the generic diff3 resolution handles it correctly.

## Requirements

### Functional Requirements

**FR-1: Test coverage for consolidation scenarios**

The diff3 merge handles consolidation divergence correctly, but has no targeted test coverage for this specific scenario class. Add test fixtures and assertions verifying correct behavior.

Acceptance criteria:
- Test: branch diverged before consolidation, main consolidated, branch added new entries → result is consolidated version + new entries only
- Test: same scenario, branch did NOT add new entries → result matches consolidated version exactly
- Test: branch modified an entry that was subsequently consolidated away on main → conflict reported
- Test: branch modified an entry still present in consolidated version → modification preserved
- Test: no consolidation (both sides only added) → standard diff3 behavior, all entries present
- Test: both merge directions (branch→main via `_worktree merge`, main→branch via merge-from-main)
- Tests use real git repos (tmp_path fixtures) per testing conventions, not mocked subprocess

**FR-2: Merge reporting**

`remerge_learnings_md()` currently operates silently. Add summary output when segments change.

Acceptance criteria:
- Report: count of entries kept from ours, count appended from theirs, count dropped (in base+theirs but not ours)
- Format: `learnings.md: kept N + appended M new (dropped K consolidated)`
- Output via `click.echo` consistent with existing merge reporting
- No output when learnings.md unchanged (no-op merge)

### Non-Functional Requirements

**NFR-1: No merge failure**
Learnings reconciliation must not cause the merge to fail. If reconstruction fails for any reason, warn and leave the merged file as-is. Already implemented — conflicts exit 3 with diagnostic.

**NFR-2: No new dependencies**
Implementation uses existing `parse_segments()`, `diff3_merge_segments()`, and `remerge_learnings_md()`. No new modules or consolidation marker infrastructure needed.

### Out of Scope

- Consolidation marker mechanism (Q-1 from original requirements) — resolved: generic diff3 handles consolidation without explicit markers
- FR-1 (original: detect consolidation divergence) — unnecessary; diff3 resolution matrix handles it as a special case of one-sided deletion
- FR-2 (original: reconstruct correct file) — already implemented in `remerge_learnings_md()`
- FR-3 edge cases — already covered by diff3 resolution matrix; test coverage in FR-1 verifies these

### References

- `src/claudeutils/worktree/resolve.py` — diff3_merge_segments, resolve_learnings_md
- `src/claudeutils/worktree/remerge.py` — remerge_learnings_md (Phase 4 entry point)
- `src/claudeutils/validation/learnings.py` — parse_segments
- `src/claudeutils/worktree/merge.py` — merge pipeline phases
