# Vet Review: Phase 4 Checkpoint — CLI Integration

**Scope**: Phase 4 changed files: cli.py (ls upgrade), display.py (new), models.py (tree_path field), aggregation.py (tree_path assignment), test_worktree_ls_upgrade.py (4 tests), test_worktree_commands.py (ls tests)
**Date**: 2026-02-17T08:10:20
**Mode**: review + fix

## Summary

Phase 4 delivers the `--porcelain` flag and rich `ls` output. The core structure is correct: porcelain mode is backward-compatible, `display.py` delegates to `aggregate_trees()` for plan data, and tests use real git repos. Two critical bugs exist: `display.py` uses wrong paths for `session.md` (omits `agents/` prefix), and the test fixture was written to match the buggy path rather than the design spec. Several minor deslop issues in `aggregation.py` (narration comments, verbose private-function docstrings).

**Overall Assessment**: Needs Minor Changes (post-fix: Ready)

---

## Issues Found

### Critical Issues

1. **Wrong session.md path in `format_tree_header()`**
   - Location: `src/claudeutils/worktree/display.py:26,37`
   - Problem: `Path(path) / "session.md"` should be `Path(path) / "agents" / "session.md"`. Design spec (design.md:164) and `aggregation.py:223` both use `agents/session.md`. The wrong path means `session_path.exists()` always returns False, so `commits_count` is always 0 and all trees show "clean" regardless of actual state. The git log command also passes `"session.md"` as the path filter (line 37) instead of `"agents/session.md"`.
   - Fix: Change both occurrences to use the correct path.
   - **Status**: FIXED

2. **Test fixture creates session.md at wrong path, matching the bug**
   - Location: `tests/test_worktree_ls_upgrade.py:137-138`
   - Problem: `session_file = worktree_path / "session.md"` creates the file at the worktree root. The correct location is `worktree_path / "agents" / "session.md"`. The test passes because the fixture and implementation share the same wrong path. After fixing `display.py`, the test will fail unless the fixture is also fixed.
   - Fix: Move the session file creation to `worktree_path / "agents" / "session.md"` (creating parent dir), and update the git log reference path.
   - **Status**: FIXED

### Major Issues

1. **Task line absent from rich output**
   - Location: `src/claudeutils/worktree/display.py:90-124`
   - Problem: Design spec (design.md:196-199) requires a `Task:` line showing the first pending task name per tree. `format_rich_ls()` emits Plan and Gate lines but no Task line. `aggregate_trees()` returns `AggregatedStatus` with a `trees` list containing `TreeInfo` objects (which include `task_summary`), but `format_rich_ls()` ignores the `trees` list entirely.
   - The scope OUT notes: "Task line display in rich mode (implemented in format_tree_header but not yet wired to aggregate_trees task_summary)". This is explicitly listed as out-of-scope for Phase 4.
   - **Status**: DEFERRED — scope OUT explicitly lists "Task line display in rich mode (implemented in format_tree_header but not yet wired to aggregate_trees task_summary)"

### Minor Issues

1. **Narration comments in `aggregation.py`**
   - Location: `src/claudeutils/planstate/aggregation.py:59,71,75,86,110,133,159,256,269,272,276,288,299`
   - Note: Multiple inline comments restate what the adjacent code does (e.g., `# Strip "refs/heads/" prefix` before the strip, `# Fetch latest commit timestamp for this tree` before the subprocess call, `# Sort trees by latest_commit_timestamp in descending order` before the sort). These are narration comments — they describe *what*, not *why*.
   - **Status**: FIXED

2. **Verbose private-function docstrings in `aggregation.py`**
   - Location: `src/claudeutils/planstate/aggregation.py:_parse_worktree_list`, `_latest_commit`, `_is_dirty`, `_task_summary`
   - Note: Private functions have full `Args:` / `Returns:` sections with descriptions that restate the function name, parameter names, and return type annotations. Only `_is_dirty` has non-obvious behavior worth documenting ("Untracked files are ignored"). The rest add no information beyond what the signature already states.
   - **Status**: FIXED

3. **Narration comments in `display.py`**
   - Location: `src/claudeutils/worktree/display.py:15,25,100,104,115`
   - Note: `# Dirty detection`, `# Commits since handoff`, `# Aggregate plans across all trees`, `# Add plans and gates for main tree`, `# Add plans and gates for this worktree` — all narrate what follows.
   - **Status**: FIXED

4. **`_parse_worktree_entries` duplicates `_parse_worktree_list` in cli.py**
   - Location: `src/claudeutils/worktree/display.py:68-87` vs `src/claudeutils/worktree/cli.py:126-143`
   - Note: Both functions parse git worktree porcelain output with identical logic. The duplication is a consequence of the known design deviation (display.py doesn't use planstate functions). Since `aggregate_trees()` already discovers trees, `format_rich_ls()` could use `aggregated.trees` instead of re-parsing the porcelain output. However, `TreeInfo` doesn't include the raw path in a `(slug, branch, path)` tuple form.
   - This is part of the acknowledged design deviation (scope OUT: "display.py reimplements git helpers instead of using planstate functions"). Flagging as minor rather than critical.
   - **Status**: DEFERRED — scope OUT acknowledges the git helper reimplementation as an acceptable Phase 4 deviation

---

## Fixes Applied

### Critical Fix 1: Wrong session.md paths in display.py

`src/claudeutils/worktree/display.py:26` — Changed `Path(path) / "session.md"` to `Path(path) / "agents" / "session.md"`
`src/claudeutils/worktree/display.py:37` — Changed git log path arg from `"session.md"` to `"agents/session.md"`

### Critical Fix 2: Test fixture path

`tests/test_worktree_ls_upgrade.py:137-138` — Changed `session_file = worktree_path / "session.md"` to create `agents/` dir and place file at `worktree_path / "agents" / "session.md"`. Updated the commit loop to use correct path.

### Minor Fix 1: Narration comments in aggregation.py

Removed narration-only inline comments from `_parse_worktree_list()` and `aggregate_trees()`.

### Minor Fix 2: Verbose docstrings in aggregation.py

Simplified private function docstrings to imperative one-liners. `_is_dirty` retains the "untracked files ignored" note (non-obvious). `_commits_since_handoff` retains the "0 if no anchor" edge-case note. Full `Args:`/`Returns:` sections removed from all private functions.

### Minor Fix 3: Narration comments in display.py

Removed `# Dirty detection`, `# Commits since handoff`, `# Aggregate plans across all trees`, `# Add plans and gates for main tree`, `# Add plans and gates for this worktree` from `display.py`.

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Cross-tree status display | Partial | Trees displayed with dirty indicator + commit status; plan/gate lines per tree. Task line deferred (scope OUT). |
| `--porcelain` flag: machine-readable tab-separated `slug\tbranch\tpath` | Satisfied | `cli.py:147-155`, test coverage in `test_porcelain_mode_backward_compatible` |
| Rich mode: header with dirty indicator (●/○), commit status, plan/gate lines indented | Partial (path bug fixed) | `display.py:65`, plan lines at `display.py:108-122`. Commit counting now works correctly after path fix. |

---

## Positive Observations

- Real git repo fixtures in all 4 new tests — no mocked subprocess, consistent with project pattern
- Porcelain backward compatibility cleanly preserved: flag defaults to False, existing consumers unaffected
- `PlanState.tree_path` addition is minimal — single optional field, no breaking change to existing callers
- `aggregate_trees()` correctly assigns `tree_path` from the git worktree path string, enabling the `plan.tree_path == path` filter in `format_rich_ls()`
- `test_rich_mode_plan_and_gate` creates a real worktree with plan directories and asserts on the exact output format strings — meaningful coverage of the plan discovery path

## Recommendations

- Phase 5: When wiring the Task line, use `aggregated.trees` (already has `task_summary`) rather than additional git calls in `format_tree_header()`
- Phase 5: Consider refactoring `format_rich_ls()` to use `aggregated.trees` for the header loop instead of re-parsing porcelain via `_parse_worktree_entries()` — eliminates the duplication noted in Minor Issue 4
