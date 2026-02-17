# Current Worktree RM Implementation

## Summary

The `_worktree rm` command is implemented in the CLI module and removes worktrees with a two-phase guard: safety checks that prevent removal of branches with unmerged commits, followed by cleanup of directory, branch, and session metadata. The worktree skill wraps it in Mode C (merge ceremony), triggering `rm` after successful merge. Current implementation has focused session detection and session.md integration but lacks dirty-check and submodule-safety requirements from the plan.

## Key Findings

### 1. CLI Entry Point: `_worktree rm` Command

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/cli.py` (lines 364-397)

**Command signature:**
```python
@worktree.command()
@click.argument("slug")
def rm(slug: str) -> None:
```

**Removal flow (current):**
1. **Guard check** (`_guard_branch_removal`): Verify branch can be safely removed
   - Check branch exists
   - Allow if merged via `_is_branch_merged(slug)`
   - Allow if focused-session-only (1 commit, message "Focused session for {slug}") via `_classify_branch(slug)`
   - Refuse if orphaned (0 common ancestors) or has multiple unmerged commits
   - Exit code 1 if guard refuses, blocks all downstream operations
2. **Worktree introspection** (`_probe_registrations`): Check if worktree/submodule registered
3. **Dirty warning** (non-blocking): Report uncommitted files but proceed
4. **Session cleanup** (`_update_session_and_amend`): Remove task from Worktree Tasks
   - Amends merge commit if HEAD is merge (2+ parents) and session.md modified
5. **Worktree removal** (multi-step):
   - Remove submodule worktree (if registered) with `--force`
   - Remove parent worktree (if registered) with `--force`
   - Prune worktree refs
   - Delete container directory if empty
6. **Branch deletion** (guarded): Use `-d` for merged, `-D` for focused-session-only
   - Exit code 2 if branch deletion fails (e.g., still exists and unmerged)

### 2. Guard Function: `_guard_branch_removal`

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/cli.py` (lines 305-333)

**Returns:** `(bool, str | None)` — (branch_exists, removal_type)
- `removal_type`: "merged", "focused", or None
- Exit code 1 via `click.Abort` if guard refuses

**Guard logic:**
```python
def _guard_branch_removal(slug: str) -> tuple[bool, str | None]:
    # 1. Branch existence check
    if branch_check.returncode != 0:
        return False, None

    # 2. Merged check
    if _is_branch_merged(slug):
        return True, "merged"

    # 3. Focused session check (1 commit with marker)
    count, is_focused = _classify_branch(slug)
    if count == 1 and is_focused:
        return True, "focused"

    # 4. Refuse with error (orphan or unmerged)
    if count == 0:
        error: "Branch {slug} is orphaned (no common ancestor). Merge first."
    else:
        error: "Branch {slug} has {count} unmerged commit(s). Merge first."
```

### 3. Safety Check Functions

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/utils.py`

#### `_is_branch_merged(slug: str) -> bool` (lines 41-58)
- Uses `git merge-base --is-ancestor <slug> HEAD`
- Returns True if branch is ancestor of current HEAD (merged)
- Returns False if branch has unmerged commits

#### `_classify_branch(slug: str) -> tuple[int, bool]` (lines 61-83)
- Counts commits between merge-base and branch tip: `git rev-list --count`
- Detects focused-session marker: message == "Focused session for {slug}"
- Returns (count, is_focused)
- Orphan branches: returns (0, False) — no merge-base

#### `_is_merge_commit() -> bool` (lines 149-152)
- Returns True if HEAD has 2+ parents
- Used to detect merge commits for session.md amending

#### `_probe_registrations(worktree_path: Path) -> tuple[bool, bool]` (lines 119-127)
- Check parent worktree in `git worktree list`
- Check submodule worktree in `git -C agent-core worktree list`
- Returns (parent_registered, submodule_registered)

### 4. Session Cleanup Function: `_update_session_and_amend`

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/cli.py` (lines 349-361)

```python
def _update_session_and_amend(slug: str) -> bool:
    session_md_path = Path("agents/session.md")

    # 1. Remove task from Worktree Tasks
    remove_worktree_task(session_md_path, slug, slug)

    # 2. Only amend if HEAD is merge commit
    if not _is_merge_commit():
        return False

    # 3. Check if session.md was modified
    status_output = _git("status", "--porcelain", "agents/session.md", check=False)
    if not status_output.strip():
        return False

    # 4. Stage and amend
    _git("add", "agents/session.md")
    _git("commit", "--amend", "--no-edit")
    return True
```

**Behavior:**
- Always calls `remove_worktree_task` (removes task from Worktree Tasks)
- Only amends if (a) HEAD is merge commit AND (b) session.md changed
- Returns True if amend occurred (for output messaging)

### 5. Worktree Skill Integration

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/agent-core/skills/worktree/SKILL.md` (lines 84-135)

**Mode C: Merge Ceremony** orchestrates the removal:

1. **Pre-merge setup:** Run `/handoff --commit` to ensure clean tree
2. **Merge phase:** `claudeutils _worktree merge <slug>` (exit 0 = success, 1 = conflicts, 2 = fatal)
3. **Cleanup phase (on merge success):**
   ```
   claudeutils _worktree rm <slug>
   ```
4. **Handle rm exit codes:**
   - Exit 0: Cleanup succeeded, report "Merged and cleaned up"
   - Exit 1: Guard refused (unmerged commits after merge reported success) — escalate with "Merge may be incomplete"
   - Exit 2: Unexpected error (branch deletion failed) — escalate with stderr, note worktree may already be removed

**Skill constraint:** `Bash(claudeutils _worktree:*)` + `dangerouslyDisableSandbox: true` required

### 6. Test Coverage for RM

**Files:**
- `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/tests/test_worktree_rm.py` (8 tests)
- `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/tests/test_worktree_rm_guard.py` (10 tests)

**Test cases (combined):**

| Test | Coverage |
|------|----------|
| `test_rm_basic` | Happy path: removes dir, branch, reports success |
| `test_rm_dirty_warning` | Uncommitted files don't block removal (warning only) |
| `test_rm_branch_only` | Cleans up branch when directory removed externally |
| `test_rm_detects_merge_commit` | `_is_merge_commit()` correctly identifies merge commits |
| `test_rm_amends_merge_commit_when_session_modified` | Amends merge commit when session.md removed task |
| `test_rm_does_not_amend_on_normal_commit` | Does NOT amend normal (1-parent) commits |
| `test_rm_output_indicates_amend` | Output shows "merge commit amended" when applicable |
| `test_is_branch_merged` | Guard: allows merged branches |
| `test_classify_branch` | Guard: detects focused-session marker and commit counts |
| `test_classify_orphan_branch` | Guard: orphan branches return (0, False) |
| `test_rm_refuses_unmerged_real_history` | Guard: refuses branches with 2+ unmerged commits (exit 1) |
| `test_rm_allows_merged_branch` | Guard: allows merged branch with safe `-d` delete |
| `test_rm_allows_focused_session_only` | Guard: allows focused-session with force `-D` delete |
| `test_rm_guard_prevents_destruction` | Guard refusal (exit 1) prevents all downstream operations |
| `test_rm_no_destructive_suggestions` | CLI never suggests `git branch -D` in output (FR-5) |
| `test_delete_branch_exits_2_on_failure` | `_delete_branch` exits 2 if git command fails |

### 7. Session Integration

**File:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/session.py`

**Function used by rm:** `remove_worktree_task(session_md_path, slug, slug)`
- Removes task entry from "## Worktree Tasks" section
- Called unconditionally at start of `_update_session_and_amend`
- Changes are staged and amended into merge commit (if applicable)

## Current Safety Implementation

**What exists:**
1. Guard against removal of branches with unmerged commits (exit 1, blocks all operations)
2. Focused-session-only detection (1 commit with marker) — allows safe removal with `-D`
3. Merged branch detection — allows safe removal with `-d`
4. Orphan branch detection — refuses removal, reports "no common ancestor"
5. Session.md task removal with merge commit amending (only on merge commits)
6. Worktree directory cleanup (handles missing directories gracefully)
7. Submodule worktree cleanup with `--force`
8. Non-blocking dirty file warning (proceeds anyway)

**What is missing (from plan FRs):**
1. **FR-1: Dirty tree check (parent + submodule)** — Currently only warns on dirty worktree; does NOT check parent repo or require clean state before removal
2. **FR-2: Exit code 2 for guard refusal** — Currently exits 1 (click.Abort), not 2
3. **FR-3: `--force` bypass flag** — Not implemented; guard refusal cannot be bypassed
4. **FR-4: Skill confirmation requirement** — No check for removal via skill vs direct CLI
5. **FR-5: No destructive suggestions** — Already implemented; tests confirm no `git branch -D` in output

## Architecture Notes

**Entry point hierarchy:**
- CLI: `claudeutils _worktree rm <slug>`
- Skill (Mode C): Calls rm after successful merge via `claudeutils _worktree merge <slug>` → `claudeutils _worktree rm <slug>`
- Workflow: `wt merge <slug>` → skill reads exit codes and handles escalation

**Worktree-to-branch mapping:**
- Slug derived deterministically from task name: `re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")`
- Branch can exist before worktree creation (existing branch) or be created during (new branch)
- Worktree path: `<parent>/<parent-name>-wt/<slug>` (sibling container pattern)

**Merge commit integration:**
- `_is_merge_commit()` checks parent count: 2+ parents = merge
- Session.md is amended ONLY into merge commits (detected by parent count after merge completes)
- Allows merge commits to include task-list cleanup without breaking merge history

**Error handling:**
- Guard refusal: exit 1 (click.Abort) — prevents all downstream operations
- Branch deletion failure: exit 2 (SystemExit) — subprocess error during cleanup
- Merge not implemented errors: exit 1 (SystemExit) — from merge.py `_check_clean_for_merge`

## Gap Analysis

### Dirty Tree Checks (FR-1)
**Current:** Only warns if worktree directory is dirty
**Missing:**
- No check that parent repo (main) is clean before removal
- No check that submodule (agent-core) is clean
- No blocking if dirty (currently proceeds)

**Impact:** Removing worktree on dirty parent could lose uncommitted work

### Exit Code 2 for Guard (FR-2)
**Current:** Guard uses `click.Abort` (exit 1)
**Expected:** Exit code 2 for guard refusal
**Impact:** Skill cannot distinguish between "guard refused" (exit 1) vs "guard refused with unmerged commits" (needs to be 2 to separate from merge conflicts)

### Force Bypass (FR-3)
**Current:** No `--force` flag
**Expected:** `--force` flag to bypass guard checks
**Impact:** Users cannot manually override safety in emergency situations

### Skill Confirmation (FR-4)
**Current:** No check for removal origin (direct CLI vs skill)
**Expected:** Refuse direct CLI, require skill invocation
**Impact:** Users can bypass planned removal workflow by calling CLI directly

## File Paths (Absolute)

- **CLI implementation:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/cli.py`
- **Utilities (guards, checks):** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/utils.py`
- **Merge module:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/merge.py`
- **Session module:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/src/claudeutils/worktree/session.py`
- **Skill definition:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/agent-core/skills/worktree/SKILL.md`
- **Unit tests (rm):** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/tests/test_worktree_rm.py`
- **Guard tests:** `/Users/david/code/claudeutils-wt/worktree-rm-safety-gate/tests/test_worktree_rm_guard.py`

## Code Snippet: Guard Refusal Flow

Current guard refusal (exit 1):
```python
# From cli.py lines 305-333
def _guard_branch_removal(slug: str) -> tuple[bool, str | None]:
    # ... checks ...
    if count == 0:
        click.echo(f"Branch {slug} is orphaned (no common ancestor). Merge first.", err=True)
    else:
        click.echo(f"Branch {slug} has {count} unmerged commit(s). Merge first.", err=True)
    raise click.Abort  # Exit 1
```

Expected: Should raise `SystemExit(2)` for consistency with error handling model
