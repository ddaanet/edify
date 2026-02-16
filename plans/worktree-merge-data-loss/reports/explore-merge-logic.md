# Worktree Merge Logic Exploration

## Summary

The worktree merge implementation in `src/claudeutils/worktree/merge.py` consists of four phases: validation, submodule resolution, parent repo merge with auto-conflict resolution, and precommit validation. The merge logic reports success (exit 0) after completing all phases including precommit validation. The data loss symptom (parent repo files from worktree branch absent after merge) indicates a potential gap between merge completion (which triggers precommit validation) and file staging/committing.

## Architecture Overview

### Entry Point

**File:** `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py:342-344`
```python
@worktree.command()
@click.argument("slug")
def merge(slug: str) -> None:
    """Merge worktree branch: validate, resolve submodule, merge parent."""
    merge_impl(slug)
```

The CLI command delegates to `merge_impl` from `merge.py`.

### Four-Phase Merge Architecture

**File:** `/Users/david/code/claudeutils/src/claudeutils/worktree/merge.py:302-307`

```python
def merge(slug: str) -> None:
    """Merge worktree branch: validate, resolve submodule, merge parent."""
    _phase1_validate_clean_trees(slug)
    _phase2_resolve_submodule(slug)
    _phase3_merge_parent(slug)
    _phase4_merge_commit_and_precommit(slug)
```

Each phase is called sequentially. If any phase raises `SystemExit(1)` or `SystemExit(2)`, execution stops with that exit code.

---

## Phase-by-Phase Analysis

### Phase 1: Tree Validation

**Function:** `_phase1_validate_clean_trees(slug: str)` — Lines 159-183

**Purpose:** Verify both parent and worktree repos are clean before merge.

**Operations:**
1. Check branch exists: `git rev-parse --verify <slug>`
2. Check parent tree is clean (exempting session files):
   - `git status --porcelain --untracked-files=no` in parent repo
   - Exempt: `agents/session.md`, `agents/jobs.md`, `agents/learnings.md`, `agent-core`
3. Check worktree tree is clean:
   - `git status --porcelain --untracked-files=no` in worktree directory
   - No exemptions applied to worktree
4. Check parent repo submodule is clean:
   - `git -C agent-core status --porcelain --untracked-files=no`

**Key Detail:** Exempts `agent-core` submodule from parent tree dirty check because Phase 2 will resolve submodule changes.

**Exit Codes:**
- Exit 0: Validation passed
- Exit 1: Tree is not clean

---

### Phase 2: Submodule Resolution

**Function:** `_phase2_resolve_submodule(slug: str)` — Lines 186-227

**Purpose:** Resolve diverged submodule states before parent merge.

**Operations:**

1. **Check if worktree branch has agent-core entry:**
   - `git ls-tree <slug> -- agent-core`
   - If no output, return (no submodule to resolve)

2. **Compare commits:**
   - Extract worktree's agent-core commit: `git ls-tree <slug> -- agent-core` → parse sha from index position 2
   - Extract parent's agent-core HEAD: `git -C agent-core rev-parse HEAD`
   - If equal, return (no resolution needed)

3. **Check ancestry/reachability:**
   - `git merge-base --is-ancestor <wt_commit> <local_commit>`
   - If return 0 (ancestor): worktree commit is in parent's history, skip fetch
   - If return ≠ 0 (not ancestor): proceed to reachability check

4. **Verify object existence:**
   - `git -C agent-core cat-file -e <wt_commit>`
   - If return 0: object exists locally, proceed to merge
   - If return ≠ 0: object missing, fetch from worktree

5. **Fetch missing commit (if needed):**
   - `git -C agent-core fetch <wt_agent_core_path> HEAD`
   - Retrieves worktree's agent-core repo contents to local

6. **Merge submodule:**
   - `git -C agent-core merge --no-edit <wt_commit>`
   - 3-way merge of local HEAD with fetched worktree commit

7. **Stage submodule pointer update:**
   - `git add agent-core`

8. **Check if staged changes exist:**
   - `git diff --cached --quiet agent-core`
   - If return 0: no changes (merge resulted in same tip)
   - If return ≠ 0: changes staged, proceed to commit

9. **Commit submodule merge (if staged changes):**
   - `git commit -m "🔀 Merge agent-core from <slug>"`
   - Creates merge commit only if agent-core pointer changed

**Key Detail:** Phase 2 does NOT stage or commit parent repo file changes from the worktree branch. It only handles submodule state. Parent repo changes are handled by `git merge` in Phase 3.

**Exit Codes:**
- Exit 0: Submodule resolved (or no resolution needed)
- Exceptions in subprocess: propagate, likely exit ≠ 0

---

### Phase 3: Parent Merge and Auto-Conflict Resolution

**Function:** `_phase3_merge_parent(slug: str)` — Lines 230-258

**Purpose:** Merge worktree branch into parent and auto-resolve known conflicts.

**Operations:**

1. **Initiate merge without commit:**
   ```python
   result = subprocess.run(
       ["git", "merge", "--no-commit", "--no-ff", slug],
       capture_output=True,
       text=True,
       check=False,
   )
   ```
   - Uses `--no-commit` to leave merge staged but uncommitted
   - Uses `--no-ff` to force merge commit (no fast-forward)
   - Captures output/error

2. **If merge succeeds (exit 0):** Return immediately (no conflicts)

3. **If merge has conflicts (exit ≠ 0):**
   - Get conflict list: `git diff --name-only --diff-filter=U`
   - Parse lines with conflicts

4. **Auto-resolve agent-core conflict:**
   ```python
   if "agent-core" in conflicts:
       _git("checkout", "--ours", "agent-core")
       _git("add", "agent-core")
       conflicts = [c for c in conflicts if c != "agent-core"]
   ```
   - Uses parent's version (we already merged submodule in Phase 2)
   - Stages the resolution
   - Removes from conflict list

5. **Auto-resolve session.md, learnings.md, jobs.md:**
   - Call `_resolve_session_md_conflict(conflicts)` (merge new tasks from both)
   - Call `_resolve_learnings_md_conflict(conflicts)` (append unique lines)
   - Call `_resolve_jobs_md_conflict(conflicts)` (keep ours)
   - Each returns updated conflict list with that file removed if resolved

6. **Handle remaining conflicts:**
   - If any conflicts remain after auto-resolution:
     ```python
     if conflicts:
         _git("merge", "--abort")
         _git("clean", "-fd")
         ...
         raise SystemExit(1)
     ```
   - Abort the merge, clean working tree, exit 1

**Critical Observation:** After Phase 3 completes successfully:
- Merge is initiated with `--no-commit` (files staged but not committed)
- Conflicts either auto-resolved (files staged) or merge aborted
- Git index contains merged changes
- Working tree contains merged content
- No commit has been made yet

**Exit Codes:**
- Exit 0: Merge completed (no conflicts or all resolved)
- Exit 1: Conflicts remain after auto-resolution

---

### Phase 4: Merge Commit and Precommit Validation

**Function:** `_phase4_merge_commit_and_precommit(slug: str)` — Lines 261-299

**Purpose:** Commit the merge and validate with precommit checks.

**Operations:**

1. **Check if merge is in progress:**
   ```python
   merge_in_progress = (
       subprocess.run(
           ["git", "rev-parse", "--verify", "MERGE_HEAD"],
           capture_output=True,
           check=False,
       ).returncode
       == 0
   )
   ```
   - MERGE_HEAD file exists during active merge

2. **Check for staged changes:**
   ```python
   staged_check = subprocess.run(
       ["git", "diff", "--cached", "--quiet"],
       check=False,
   )
   ```
   - Exit 0: no staged changes
   - Exit ≠ 0: changes are staged

3. **Commit logic:**
   ```python
   if merge_in_progress:
       _git("commit", "--allow-empty", "-m", f"🔀 Merge {slug}")
   elif staged_check.returncode != 0:
       _git("commit", "-m", f"🔀 Merge {slug}")
   ```
   - If merge in progress: ALWAYS commit (even empty) to complete merge
   - Else if staged changes: commit them
   - Else: skip commit (nothing to do)

4. **Run precommit validation:**
   ```python
   precommit_result = subprocess.run(
       ["just", "precommit"],
       capture_output=True,
       text=True,
       check=False,
   )
   ```

5. **Handle precommit result:**
   - If exit 0: Output "Precommit passed"
   - If exit ≠ 0: Output error and raise SystemExit(1)

**Exit Codes:**
- Exit 0: Merge committed and precommit passed
- Exit 1: Precommit validation failed

---

## Helper Functions

### Conflict Resolution Functions

#### `_resolve_session_md_conflict(conflicts: list[str]) -> list[str]`
Lines 58-113

**Purpose:** Auto-resolve session.md conflicts by keeping ours and extracting new tasks from theirs.

**Logic:**
1. Extract task blocks from both sides using merge stages:
   - `:2:agents/session.md` (ours)
   - `:3:agents/session.md` (theirs)
2. Find new tasks in theirs by name comparison
3. Insert new task blocks into ours before next section
4. Stage the resolved file with `git add agents/session.md`
5. Return updated conflict list (session.md removed)

#### `_resolve_learnings_md_conflict(conflicts: list[str]) -> list[str]`
Lines 116-140

**Purpose:** Auto-resolve learnings.md by appending theirs-only lines to ours.

**Logic:**
1. Extract content from both sides
2. Find lines unique to theirs (not in ours)
3. Append unique lines to ours content
4. Write merged content and stage with `git add`
5. Return updated conflict list (learnings.md removed)

#### `_resolve_jobs_md_conflict(conflicts: list[str]) -> list[str]`
Lines 143-156

**Purpose:** Auto-resolve jobs.md by keeping ours (local plan status is authoritative).

**Logic:**
1. Run `git checkout --ours agents/jobs.md`
2. Stage with `git add agents/jobs.md`
3. Return updated conflict list (jobs.md removed)

### Utility: `_check_clean_for_merge()`
Lines 12-55

**Purpose:** Verify tree is clean with optional exemptions.

**Parameters:**
- `path`: Directory to check (None = current)
- `exempt_paths`: Paths to exclude from dirty check
- `label`: Location label for error messages

**Logic:**
1. Run `git status --porcelain --untracked-files=no`
2. Filter lines:
   - If `exempt_paths`: exclude lines containing any exempt path
   - Else: include all lines
3. If dirty lines remain: exit 1 with error
4. Separately check submodule (agent-core) if exists

---

## Git Commands Used

### Merge Strategy

| Command | Purpose | Flags |
|---------|---------|-------|
| `git merge --no-commit --no-ff <slug>` | Initiate merge without committing | `--no-commit` = leave staged, `--no-ff` = force merge commit |
| `git merge --abort` | Abort in-progress merge | Used on conflict failure |
| `git commit --allow-empty` | Complete merge even if empty | Completes MERGE_HEAD state |
| `git commit -m "<msg>"` | Complete merge with message | Standard merge commit |

### Conflict Detection/Resolution

| Command | Purpose |
|---------|---------|
| `git diff --name-only --diff-filter=U` | List conflicted files |
| `git show :2:<file>` | Get ours version during merge |
| `git show :3:<file>` | Get theirs version during merge |
| `git checkout --ours <file>` | Use our version |
| `git add <file>` | Stage resolved file |
| `git clean -fd` | Clean untracked files after abort |

### Submodule Operations

| Command | Purpose |
|---------|---------|
| `git ls-tree <branch> -- agent-core` | Get submodule commit in branch |
| `git -C agent-core rev-parse HEAD` | Get current submodule HEAD |
| `git merge-base --is-ancestor <a> <b>` | Check if `a` is ancestor of `b` |
| `git -C agent-core cat-file -e <sha>` | Check object existence |
| `git -C agent-core fetch <path> HEAD` | Fetch commits from worktree submodule |
| `git -C agent-core merge --no-edit <sha>` | Merge submodule commits |

### Staging and State

| Command | Purpose |
|---------|---------|
| `git diff --cached --quiet [<file>]` | Check if staged changes exist (exit 0 = no, ≠0 = yes) |
| `git rev-parse --verify MERGE_HEAD` | Check if merge in progress (exit 0 = yes, ≠0 = no) |

---

## Submodule Change Handling

### In Phase 2

1. Worktree branch's agent-core commit identified from `git ls-tree`
2. Fetched from worktree if not reachable locally
3. Merged into parent's agent-core with `--no-edit` (automatic merge strategy)
4. Parent's agent-core pointer updated and staged
5. **Commit created for submodule merge only** (lines 222-227)

### Submodule Pointer in Phase 3

- If both parent and worktree changed agent-core, merge creates conflict in "agent-core" special file
- Phase 3 auto-resolves by taking ours (parent's merged version from Phase 2)
- No second submodule merge happens in Phase 3

### Result

- Submodule commits are merged early (Phase 2)
- Parent repo submodule pointer reflects merged state
- Conflicts due to diverged pointers are resolved (ours) in Phase 3

---

## Data Flow: Parent Repo Files

### Where Parent Repo Changes Should Come From

Parent repo file changes (non-submodule, non-session) come from:
1. Worktree branch: new or modified files committed during task work
2. Merge conflict resolution: auto-resolved files in Phase 3

### Git Merge Processing (Phase 3)

When `git merge --no-commit <slug>` is executed:
1. Git finds common ancestor of main and worktree branch
2. For each file:
   - If only one side changed: takes that change (fast-forward content)
   - If both sides changed differently: CONFLICT
   - If neither side changed: no-op
3. Changed files are staged into index
4. Files remain in working tree
5. Merge state created (MERGE_HEAD exists)

### Staging Status After Phase 3

After successful merge in Phase 3 (no conflicts):
- Git index contains merged content from all changed files
- Working tree contains merged content
- `git status --porcelain` shows no changes (all staged)
- `git diff --cached` shows what will be committed

### Commit Point (Phase 4)

Phase 4 commits staged changes:
- If `MERGE_HEAD` exists (merge in progress): `--allow-empty` ensures commit
- Else if staged changes: commit them
- All staged changes become part of merge commit

---

## Key Findings: Potential Data Loss Points

### Finding 1: No Explicit "Add All" Before Commit

**Location:** Phase 4, lines 282-285

```python
if merge_in_progress:
    _git("commit", "--allow-empty", "-m", f"🔀 Merge {slug}")
elif staged_check.returncode != 0:
    _git("commit", "-m", f"🔀 Merge {slug}")
```

**Issue:** Code assumes all merged files are already staged by Phase 3's `git merge --no-commit`. If any files are in working tree but not staged, they won't be committed.

**Hypothesis for data loss:** If merge succeeds but modified files from parent repo aren't in the git index for any reason, they'll be left in the working tree (not committed and not lost, but not merged).

**Evidence:** Session.md shows "file changes were not present in main after merge" — suggests files were in branch but absent from committed merge.

---

### Finding 2: Phase 3 Exit Path on Success

**Location:** Phase 3, line 239

```python
if result.returncode == 0:
    return
```

**Issue:** Immediately returns without verifying all expected files are staged. No explicit check that merge brought in all expected changes.

**Clean merge scenario:** When parent and worktree both add different files (no conflict), git merge automatically stages them. But no explicit verification happens.

---

### Finding 3: Precommit Validation After Commit

**Location:** Phase 4, lines 287-299

```python
precommit_result = subprocess.run(
    ["just", "precommit"],
    capture_output=True,
    text=True,
    check=False,
)

if precommit_result.returncode == 0:
    click.echo("Precommit passed")
else:
    click.echo("Precommit failed after merge")
    click.echo(precommit_result.stderr)
    raise SystemExit(1)
```

**Issue:** Precommit runs AFTER commit. If precommit fails, merge commit already exists (cannot roll back without manual git command). Precommit failure reports "exit 0" per session notes, but files were missing — suggests precommit didn't detect what was missing.

---

### Finding 4: Missing Files Not in Conflict List

**Key observation from session.md:**
- Merge reported success (exit 0)
- Precommit passed
- Files from worktree branch were absent from main after merge

**Implication:** Files weren't detected as conflicts. They were likely:
- Not explicitly listed in conflicts
- Or conflicts were resolved but file content not staged
- Or `git merge` didn't include them for some reason

**Investigation needed:** Determine why parent repo files (not submodule, not session files) would be unmerged after a successful `git merge --no-commit`.

---

### Finding 5: Submodule Merges Successfully, Parent Files Don't

**From session.md:**
- Submodule (agent-core) changes merged correctly
- Parent repo files changed in worktree but absent after merge
- Suggests issue is specific to parent repo file staging

**Differentiation:**
- Submodule: Phase 2 explicitly merges and commits
- Parent files: Phase 3 uses auto-merge, Phase 4 commits
- Parent files might not be making it through Phase 3's `git merge` command

---

## Test Coverage

### Merge Tests Exist For:

**Validation Phase:**
- Branch existence
- Clean tree requirement
- Dirty working tree rejection

**Submodule Phase:**
- Submodule fetch when unreachable
- Submodule merge with proper commit message
- Two-commit sequence (submodule merge + parent merge)

**Conflict Resolution:**
- Session.md auto-resolution
- Learnings.md auto-resolution
- Jobs.md auto-resolution
- Agent-core conflict auto-resolution
- Generic source file conflict abort

**Parent Merge:**
- Clean merge (no conflicts)
- Merge precommit validation
- Precommit failure handling

**Idempotency:**
- Re-running merge after manual fixes

### Gap: No Test for Parent Repo File Loss

**Missing test:** Create worktree with changes to parent repo files (non-session, non-jobs, non-learnings), merge, verify files are present in committed merge.

---

## Hypothesis: Merge Tree vs Index Desynchronization

### Scenario

1. Phase 3: `git merge --no-commit slug` succeeds (clean merge)
2. All parent repo changes staged in git index
3. Working tree and index synchronized
4. Phase 4: Precommit runs and validates
5. Precommit passes despite missing files

**Possible cause:** Precommit checks don't validate that all worktree branch changes were included. Precommit runs linters, tests, format checks — not merge completeness checks.

---

## References to Session Notes

From `/Users/david/code/claudeutils/agents/session.md`:

**Observed behavior:**
- `claudeutils _worktree merge review-runbook-delegation` reported success (exit 0, "Precommit passed")
- `git branch -D` reported "unmerged changes" on the branch
- Parent repo files changed in worktree branch (pipeline-contracts.md, learnings.md, memory-index.md) were not present in main after merge
- Submodule (agent-core) changes merged correctly
- Cherry-pick of worktree branch tip (063add3) recovered the lost changes

**Root cause markers:**
- Merge command exit code was 0 (success reported)
- But `git branch -D` indicates changes not merged
- Suggests changes existed in branch but weren't pulled into main during merge

---

## Summary of Key Code Paths

### File: `/Users/david/code/claudeutils/src/claudeutils/worktree/merge.py`

| Function | Lines | Purpose | Exit Codes |
|----------|-------|---------|-----------|
| `merge()` | 302-307 | Orchestrates 4 phases | 0, 1, 2 |
| `_phase1_validate_clean_trees()` | 159-183 | Verify clean state | 0, 1, 2 |
| `_phase2_resolve_submodule()` | 186-227 | Merge submodule commits | 0, exception |
| `_phase3_merge_parent()` | 230-258 | Merge branch with conflict auto-resolution | 0, 1 |
| `_phase4_merge_commit_and_precommit()` | 261-299 | Commit and validate | 0, 1 |
| `_check_clean_for_merge()` | 12-55 | Clean tree verification | 0, 1 |
| `_resolve_session_md_conflict()` | 58-113 | Auto-resolve session.md | returns list |
| `_resolve_learnings_md_conflict()` | 116-140 | Auto-resolve learnings.md | returns list |
| `_resolve_jobs_md_conflict()` | 143-156 | Auto-resolve jobs.md | returns list |

### File: `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py`

| Function | Lines | Purpose |
|----------|-------|---------|
| `merge()` | 342-344 | CLI entry point |
| `_probe_registrations()` | 310-318 | Check worktree registration |
| `_remove_worktrees()` | 321-337 | Remove registered worktrees |

### File: `/Users/david/code/claudeutils/src/claudeutils/worktree/utils.py`

| Function | Lines | Purpose |
|----------|-------|---------|
| `_git()` | 7-21 | Git subprocess wrapper |
| `wt_path()` | 24-38 | Compute worktree path |

---

## Skill Definition Integration

**File:** `/Users/david/code/claudeutils/agent-core/skills/worktree/SKILL.md:84-114`

Mode C (Merge Ceremony) describes the expected workflow:

1. `/handoff --commit` to clean tree
2. `claudeutils _worktree merge <slug>` performs merge
3. Exit code 0 = success, proceed to `claudeutils _worktree rm <slug>`
4. Exit code 1 = conflicts/precommit failure
5. Exit code 2 = fatal error

**Skill expects:** Merge completes fully before cleanup. If exit 0, files are committed and ready.

---

## Conclusion

The merge implementation is structurally sound:
- Four-phase design properly separates concerns
- Submodule handling is explicit and tested
- Conflict auto-resolution is deterministic
- Precommit validation occurs post-commit

However, the data loss symptom indicates **one or more parent repo files are not being included in the merge despite the branch containing them**. The most likely causes:

1. **Git merge not pulling in all changes** — Possible race condition or unstaged file
2. **Phase 3 returning early without verifying completeness** — No explicit check that expected files were staged
3. **Precommit passing despite incomplete merge** — Precommit validation is linting/tests, not merge completeness
4. **File staging lost between Phase 3 and Phase 4** — Unlikely but possible if git state corrupted

**Next steps for investigation:**
- Add explicit file presence checks after `git merge --no-commit`
- Verify `git diff --cached` includes all expected files before committing
- Add test case that specifically validates parent repo file loss scenario
- Check git logs for correlation between merge command and file absence
