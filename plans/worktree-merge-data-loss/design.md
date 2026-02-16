# Worktree Merge Data Loss — Design

## Problem

Two bugs compound into permanent data loss:

1. **Merge creates single-parent commit.** Phase 4 creates a regular commit (one parent) instead of a merge commit (two parents). Parent repo file changes from the worktree branch are silently dropped. Exit 0 reported, precommit passes.
2. **`rm` destroys unmerged branches.** After incomplete merge, `rm` removes the worktree directory unconditionally, outputs `"use: git branch -D {slug}"`, and agents follow the instruction — permanently destroying unmerged changes.

Evidence: commit 3d72597 has one parent (63a10da). Files from 063add3 (pipeline-contracts.md, learnings.md, memory-index.md) absent from merge. Cherry-pick (1438fbc) recovered.

**Proximate cause:** Phase 4 took the `elif` path (MERGE_HEAD absent, staged changes present) instead of the `if merge_in_progress` path. A regular `git commit` was created with one parent instead of `git commit --allow-empty` during an active merge (which would produce two parents via MERGE_HEAD).

**Root cause not fully determined from code inspection.** The mechanism by which MERGE_HEAD disappears between Phase 3 completion and Phase 4 entry is unknown. Phase 2's submodule commit creating an intermediate commit on main before Phase 3's merge is the most likely trigger. Defensive checks prevent the symptom regardless of root cause.

## Requirements

**Functional:**
- FR-1: `rm` classifies branch before removal (merged / focused-session-only / real-history-unmerged) — addressed by Track 1 branch classification
- FR-2: `rm` refuses removal when branch has unmerged real history, exit 1 — addressed by Track 1 guard
- FR-3: `rm` allows removal of focused-session-only branches (1 commit with marker text) — addressed by Track 1 classification
- FR-4: `rm` exit codes: 0 (removed), 1 (refused), 2 (error) — addressed by Track 1 guard
- FR-5: CLI never suggests destructive commands in output — addressed by Track 1 messaging
- FR-6: Phase 4 refuses single-parent commit when merge expected (MERGE_HEAD absent + branch not merged = exit 2) — addressed by Track 2 checkpoint
- FR-7: Post-merge validation: branch tip is ancestor of merge result — addressed by Track 2 validation
- FR-8: `rm` reports removal type in success message — addressed by Track 1 messaging
- FR-9: Skill Mode C handles `rm` exit 1 by escalating to user — addressed by Track 3

**Out of scope:**
- Phase 2/3 merge logic (submodule resolution, conflict auto-resolution unchanged)
- Merge strategy changes (still `--no-commit --no-ff`)
- Worktree creation, precommit additions, git config, batch merge

## Architecture

### Track 1: Removal Safety Guard (`cli.py` `rm`)

#### Helpers

**`_is_branch_merged(slug: str) -> bool`** in `utils.py` (shared with Track 2):
```
git merge-base --is-ancestor <slug> HEAD → returncode 0 = merged
```

**`_classify_branch(slug: str) -> tuple[int, bool]`** in `cli.py` (rm-specific):
```
merge_base = git merge-base HEAD <slug>
count = git rev-list --count <merge_base>..<slug>
if count == 1:
    msg = git log -1 --format=%s <slug>
    is_focused = (msg == f"Focused session for {slug}")
return (count, is_focused)
```

Handles `merge-base` failure (orphan branch): returns `(0, False)` — treated as real history, refused. Guard message for orphan: "Branch {slug} is orphaned (no common ancestor). Merge first."

#### Guard Logic

Insert before ALL destructive operations in `rm`:

```
1. branch_exists = git rev-parse --verify <slug>
2. If not exists: skip guard, proceed to directory cleanup only
3. merged = _is_branch_merged(slug)
4. If not merged:
   a. count, focused = _classify_branch(slug)
   b. If not focused:
      if count == 0:  # orphan branch (merge-base failed)
        stderr: "Branch {slug} is orphaned (no common ancestor). Merge first."
      else:
        stderr: "Branch {slug} has {count} unmerged commit(s). Merge first."
      exit 1
5. Proceed with removal
```

**Branch deletion:**
- Merged: `git branch -d` (should succeed; exit 2 if unexpectedly fails)
- Focused-session-only unmerged: `git branch -D` (safe — only auto-generated commit)

**Success messages:**
- `"Removed {slug}"` (merged)
- `"Removed {slug} (focused session only)"` (focused-session-only)

**Current → new flow:**
```
BEFORE: probe → warn → remove_session_task → remove_worktrees → branch -d → suggest -D → rmtree → clean
AFTER:  check_exists → guard → probe → warn → remove_session_task → remove_worktrees → branch -d/-D → rmtree → clean
```

Guard runs FIRST. If guard refuses, nothing is removed or modified.

### Track 2: Merge Correctness (`merge.py`)

#### MERGE_HEAD Checkpoint (Phase 4 Entry)

Current Phase 4 has two commit paths:
- `if merge_in_progress:` → `git commit --allow-empty` (two-parent merge commit)
- `elif staged_check.returncode != 0:` → `git commit` (single-parent regular commit) ← **THE BUG**

Fix: before the `elif` path creates a commit, verify the branch is already merged. If not merged, abort — a single-parent commit would lose branch ancestry.

```python
if merge_in_progress:
    _git("commit", "--allow-empty", "-m", f"🔀 Merge {slug}")
elif staged_check.returncode != 0:
    if not _is_branch_merged(slug):
        click.echo("Error: merge state lost — MERGE_HEAD absent, branch not merged", err=True)
        raise SystemExit(2)
    _git("commit", "-m", f"🔀 Merge {slug}")
else:
    # No MERGE_HEAD, no staged changes
    if not _is_branch_merged(slug):
        click.echo("Error: nothing to commit and branch not merged", err=True)
        raise SystemExit(2)
    # Already merged, nothing to do — skip commit
```

The `elif` path now only executes for already-merged branches (idempotent case). The `else` path handles the no-MERGE_HEAD, no-staged-changes case: if the branch is already merged, skip silently; if not merged, exit 2. For unmerged branches with lost MERGE_HEAD, exit 2 fires before any commit.

#### Post-Merge Ancestry Validation

New function `_validate_merge_result(slug)` called after commit, before precommit:

```python
def _validate_merge_result(slug: str) -> None:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", slug, "HEAD"],
        check=False,
    )
    if result.returncode != 0:
        click.echo(f"Error: branch {slug} not fully merged", err=True)
        raise SystemExit(2)
```

Defense-in-depth: catches merge integrity failures even if MERGE_HEAD checkpoint passes. Ancestry check is the semantic property (all branch changes reachable from HEAD).

**Diagnostic logging:** Also emit parent count when < 2 (warning, not error):
```python
commit_info = _git("cat-file", "-p", "HEAD")
parent_count = sum(1 for line in commit_info.split("\n") if line.startswith("parent "))
if parent_count < 2:
    click.echo(f"Warning: merge commit has {parent_count} parent(s)", err=True)
```

#### Phase 4 Modified Flow

```
check MERGE_HEAD → check staged →
  if MERGE_HEAD: commit --allow-empty (merge commit)
  elif staged + branch merged: commit (idempotent)
  elif staged + branch NOT merged: exit 2 (bug detected)
  else (no MERGE_HEAD, no staged):
    if branch merged: skip commit
    else: exit 2 (nothing to commit, branch not merged)
→ validate ancestry (after any successful commit or skip) → precommit
```

### Track 3: Skill Update (`SKILL.md` Mode C)

Mode C step 3 — after successful merge (exit 0), `rm` may now exit 1:

> `rm` will refuse (exit 1) if the branch has unmerged commits. If this happens after a successful merge (exit 0), the merge itself may be incomplete. Escalate to user: "Merge may be incomplete — branch {slug} has unmerged commits after merge reported success."

Do not retry `rm` or force-delete. The mismatch between merge-success and rm-refusal indicates a merge correctness issue.

## Key Design Decisions

- **D-1: Focused session detection via marker text.** `"Focused session for {slug}"` in first commit message (set by `_create_session_commit`, cli.py:175). Commit count alone insufficient — 1 user-authored commit is real history. Marker text is deterministic; false positives require manual creation with exact format.
- **D-2: `rm` exit codes.** 0 (removed), 1 (refused: unmerged real history), 2 (error). Fail-fast over force-create.
- **D-3: No destructive instructions in output.** Agents follow CLI output. Report the problem, not the workaround.
- **D-4: MERGE_HEAD checkpoint.** Phase 4 refuses to create single-parent commits for unmerged branches. Prevents the exact failure from the incident.
- **D-5: Post-merge ancestry validation.** `merge-base --is-ancestor` after commit. Semantic check (content inclusion) over structural (parent count). Defense-in-depth.
- **D-6: Guard before destruction.** Removal guard runs before ANY destructive operation. The incident's `shutil.rmtree` ran before `git branch -d` could detect the problem.
- **D-7: `_is_branch_merged` in utils.py.** Both cli.py (rm guard) and merge.py (MERGE_HEAD checkpoint) need this check. utils.py is the existing shared module.

## Implementation Notes

**Affected files:**
- `src/claudeutils/worktree/cli.py` — `rm` rewrite: guard logic, `_classify_branch`, exit codes, messaging (~35 LOC delta)
- `src/claudeutils/worktree/merge.py` — Phase 4: MERGE_HEAD checkpoint, `_validate_merge_result`, diagnostic logging (~25 LOC delta)
- `src/claudeutils/worktree/utils.py` — `_is_branch_merged` helper (~8 LOC)
- `agent-core/skills/worktree/SKILL.md` — Mode C step 3: `rm` exit 1 handling (prose)
- `tests/` — new test files for removal guard and merge validation

**Testing strategy:** All tests use real git repos (tmp_path, `repo_with_submodule` fixture). No mocked subprocess for git operations.

Track 1 tests (removal guard):
- Merged branch removal succeeds (exit 0)
- Focused-session-only unmerged removal succeeds (exit 0, reports type)
- Real-history unmerged removal refused (exit 1, stderr message)
- Worktree directory NOT removed when guard refuses (regression test)
- No `git branch -D` in output for any case
- Orphan branch: refused with specific message (exit 1)
- Branch-not-found: directory cleanup proceeds

Track 2 tests (merge correctness):
- Parent repo file preservation: branch with parent repo changes + submodule changes → merge → all files present in result
- Two-parent merge commit structure after merge
- Branch ancestry: slug is ancestor of HEAD after merge
- MERGE_HEAD checkpoint: simulate absent MERGE_HEAD with unmerged branch → exit 2
- Already-merged idempotency: re-merge already-merged branch → no error
- No MERGE_HEAD + no staged + branch not merged → exit 2

**Reproduction test note:** The parent repo file preservation test (Track 2, first test) may or may not reproduce the original bug. If it passes without code changes, the bug was environment-specific and the defensive checks serve as belt-and-suspenders. If it fails, the fix addresses the root cause.

## Phase Types

- Phase 1 (removal guard + merge correctness): **TDD** — behavioral changes to cli.py, merge.py, utils.py
- Phase 2 (skill update): **general** — prose edits to SKILL.md

## References

- `plans/worktree-merge-data-loss/reports/explore-merge-logic.md` — four-phase merge architecture analysis
- `plans/worktree-merge-data-loss/reports/explore-git-history.md` — incident timeline, single-parent commit evidence
- `plans/worktree-merge-data-loss/reports/outline-review.md` — outline review findings

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `src/claudeutils/worktree/cli.py` — current `rm` implementation (lines 347-382)
- `src/claudeutils/worktree/merge.py` — current Phase 4 (lines 261-299)
- `src/claudeutils/worktree/utils.py` — shared helpers (`_git`, `wt_path`)
- `tests/fixtures_worktree.py` — `repo_with_submodule`, `commit_file`, `mock_precommit` fixtures
- `tests/test_worktree_merge_parent.py` — existing merge tests (pattern reference)
- `agents/decisions/testing.md` — test conventions

**Additional research allowed:** Planner may explore test patterns in other `test_worktree_*` files.

## Next Steps

Route to `/runbook` for planning. Phase 1 (TDD): removal guard + merge correctness. Phase 2 (general): skill update.
