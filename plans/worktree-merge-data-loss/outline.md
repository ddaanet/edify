# Worktree Merge Data Loss — Outline

## Problem

Two independent bugs compound into permanent data loss:

1. **Merge bug (primary):** Parent repo changes from the worktree branch are not merged. The merge completes (exit 0, "Precommit passed") but the branch's parent repo file changes (pipeline-contracts.md, learnings.md, memory-index.md) are absent from main. Submodule changes merge correctly. The branch has unmerged commits that git correctly detects.

2. **Removal bug (makes it permanent):** `rm` outputs `"use: git branch -D <slug>"` when `git branch -d` fails. Agents follow the instruction and force-delete the branch, destroying the only copy of the unmerged changes. Additionally, `rm` proceeds with `shutil.rmtree` and `git worktree remove --force` unconditionally.

## Root Causes

### Root Cause 1: Merge Doesn't Include Parent Repo Changes

The merge CLI reports success but the worktree branch's parent repo file changes are not in the merge result. Evidence:
- Branch tip (063add3) contains changes to 5 files (agent-core + 4 parent repo files)
- After merge, only agent-core and session.md changes are present in main
- pipeline-contracts.md, learnings.md, memory-index.md changes are absent
- `git branch -d` correctly reports "unmerged changes" — the branch was never fully merged

The focused session commit guarantees branch divergence (MERGE_HEAD is always present). The mechanism by which parent repo changes are dropped during an otherwise successful merge needs investigation during design.

### Root Cause 2: Destructive CLI Output

`cli.py` `rm` command, lines 369-376:
```python
r = subprocess.run(["git", "branch", "-d", slug], ...)
if r.returncode != 0 and "not found" not in r.stderr.lower():
    click.echo(f"Branch {slug} has unmerged changes — use: git branch -D {slug}")

if worktree_path.exists():
    shutil.rmtree(worktree_path)
```

Three bugs in sequence:
- Worktree directory removed unconditionally even when branch has unmerged changes
- Warning message contains a destructive instruction that LLM agents follow
- `git branch -d` failure is treated as advisory, not blocking

## Approach

Primary fix: make `rm` refuse to destroy unmerged work. Secondary: update skill to handle refusal.

### Track 1: Removal Safety (`cli.py rm`)

**Before any removal, classify the branch:**
- `git rev-list --count <merge-base>..<branch>` to count commits beyond fork point
- Check first commit message for marker text `"Focused session for {slug}"` (created by `new --task`, `cli.py:175`)
- **Focused-session-only:** 1 commit AND marker text matches → safe to delete
- **Real history:** 2+ commits, OR 1 commit without marker text → refuse if unmerged

**Behavior by classification:**

| Branch merged? | Classification | Action |
|---------------|---------------|--------|
| Yes | any | Remove worktree + delete branch. Exit 0. |
| No | focused-session-only (1 commit + marker) | Remove worktree + delete branch. Exit 0. Message: "Removed <slug> (focused session only)" |
| No | real history | **Refuse.** Do not remove worktree. Do not delete branch. Exit 1. Message: "Branch <slug> has N unmerged commits. Run merge first." |

**Merged detection:** `git merge-base --is-ancestor <branch> HEAD` — if branch tip is ancestor of HEAD, it's merged.

**No destructive instructions in output.** Never suggest `git branch -D` in CLI output — agents treat CLI output as instructions.

### Track 2: Skill Update (`SKILL.md`)

Mode C step 3: Currently calls `rm` unconditionally after merge exit 0. With the new guard, `rm` may exit 1 if the merge didn't fully incorporate the branch.

Update Mode C to handle `rm` exit 1: "Merge reported success but branch has unmerged commits. Escalate to user — do not force-delete."

### Track 3: Merge Correctness (merge.py)

**Investigate:** Determine why `git merge --no-commit --no-ff` with a diverged branch (MERGE_HEAD present) produces a merge that doesn't include the branch's parent repo file changes. The submodule resolution (Phase 2) and session conflict auto-resolution (Phase 3) may interact with git's merge state in a way that drops non-conflicting parent repo changes.

**Post-merge validation:** After Phase 4 commit, verify:
- Commit has two parents (merge commit, not regular commit)
- Branch tip is ancestor of the new commit (`git merge-base --is-ancestor <branch> HEAD`)
If either check fails, error before precommit — the merge didn't fully incorporate the branch.

## Key Decisions

- **D-1:** Focused session detection — marker text `"Focused session for {slug}"` in first commit message, not just commit count. A branch with 1 user-authored commit is real history. Only branches whose sole commit matches the marker are safe to delete without merge.
- **D-2:** `rm` exit codes — 0 (removed), 1 (refused: unmerged real changes), 2 (error)
- **D-3:** No destructive instructions in CLI output — agents follow them. Report the problem, not the workaround.

## Scope

**In:**
- `cli.py` `rm` command: branch classification, removal guard, safe messaging
- `cli.py` or `merge.py`: branch depth helper (`_branch_commit_count` or similar)
- `merge.py` Phase 4: post-commit two-parent validation (defensive)
- `agent-core/skills/worktree/SKILL.md` Mode C: `rm` refusal handling
- Tests: branch depth detection, removal guard (merged/unmerged/focused-session), post-merge parent count

**Out:**
- Phase 2/3 merge logic (submodule resolution and conflict auto-resolution unchanged)
- Merge strategy changes
- Worktree creation changes
- Precommit additions

## Phase Types

- Phase 1 (removal guard + post-merge validation): TDD — behavioral changes to cli.py and merge.py
- Phase 2 (skill update): general — prose edits to SKILL.md
