# Session.md Merge Fix — Outline

## Problem

`_worktree merge` drops session.md context on non-conflict paths. Two manifestations:
1. Worktree Tasks entries dropped (Merge 1: `f525d705`, Merge 2: `c91c7628`)
2. Branch-only content appended to wrong sections (Merge 3: `8a97fb71` — 5 `[from: planstate-delivered]` entries in Blockers)

**Root cause:** `resolve_session_md()` only runs on the conflict path (phase 3, via `_auto_resolve_known_conflicts`). When git's 3-way merge resolves session.md "cleanly," the structural merge never runs. For focused sessions (which rewrite most of session.md), git's line-level result is structurally incorrect:
- Focused session deletes sections → git may favor deletion over main's additions
- Content from one section bleeds into adjacent sections due to line-level merge of structurally different documents

Same bug class as the learnings.md orphan problem fixed by `remerge_learnings_md()`.

## Approach

Add `remerge_session_md(slug)` analogous to `remerge_learnings_md()` — runs in phase 4 for ALL merge paths, overwrites git's line-level result with the structural per-section merge.

**Key difference from learnings.md fix:** Session.md uses per-section strategies (not uniform diff3). No merge-base needed — ours (main) is authoritative source, theirs (branch) contributes additions only. Reuse existing `_merge_session_contents()` logic.

## Key decisions

- **D-1: Reuse `_merge_session_contents()` for both paths.** Conflict path (`:2:`/`:3:`) and remerge path (`HEAD`/`MERGE_HEAD`) use the same merge logic. No new merge algorithm needed.
- **D-2: No merge-base involvement.** Session.md's ours-as-base strategy is correct: main is authoritative, branch contributes new tasks and new blockers. Unlike learnings.md (where both sides can modify entries), session.md sections have clear ownership.
- **D-3: Phase 4 integration.** Call `remerge_session_md()` in `_phase4_merge_commit_and_precommit`, after `remerge_learnings_md()`. Single insertion point, all state machine paths converge here.
- **D-4: Skip if no session.md.** Guard: `MERGE_HEAD` exists AND `agents/session.md` exists on disk. Matches `remerge_learnings_md()` guards.
- **D-5: Slug parameter.** `remerge_session_md(slug)` needs the branch slug for `[from: slug]` blocker tagging. Thread it through from `merge()` → `_phase4_merge_commit_and_precommit()` → `remerge_session_md()`.

## Function signature

```python
def remerge_session_md(slug: str | None = None) -> None:
    """Structural session.md merge for all paths; skips when no MERGE_HEAD."""
```

Reads `HEAD:agents/session.md` (ours) and `MERGE_HEAD:agents/session.md` (theirs). Calls `_merge_session_contents(ours, theirs, slug)`. Writes result, stages file.

## Scope

**IN:**
- `remerge_session_md()` implementation in `resolve.py`
- Phase 4 integration (thread slug parameter through)
- Integration tests: focused session merge preserves WT section, task list, blockers

**OUT:**
- Blocker format parsing rewrite (`extract_blockers` uses `- ` marker but session.md uses `**bold:**` headers — separate fix, different scope)
- Inline worktree marker migration (decided in operational-tooling.md, separate task)
- Session.md precommit structural validation (separate, analogous to learnings.md orphan check)
- Merge-base 3-way diff for session.md (unnecessary given per-section ownership model)

## Affected files

- `src/claudeutils/worktree/resolve.py` — add `remerge_session_md()`
- `src/claudeutils/worktree/merge.py` — add slug param to `_phase4_merge_commit_and_precommit()`, call `remerge_session_md(slug)`
- `tests/test_worktree_merge_session_resolution.py` — integration tests (extend existing)

## Testing approach

Integration-first with real git repos (`tmp_path`). Scenarios:
1. Focused session merge on clean path → WT section preserved, full task list preserved
2. Branch adds new pending task → task appears in merged result
3. Branch adds new blocker → blocker tagged and appended
4. Branch modifies existing blocker → main's version kept (ours-wins for existing)

## Phase typing

- Phase 1 (TDD): `remerge_session_md()` + phase 4 integration + focused-session-preserves-main tests
- Phase 2 (TDD): Edge cases — branch-added tasks, blocker tagging, already-conflicted path still works
