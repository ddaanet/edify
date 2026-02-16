# Worktree CLI Implementation Exploration

## Summary

The worktree system is a comprehensive CLI tool for managing git worktrees in parallel execution workflows. It consists of two parallel implementations: a Python Click-based CLI module (`_worktree`) in claudeutils, and justfile recipes (`wt-*`). The system handles worktree lifecycle (creation, merging, cleanup), session management, and automatic conflict resolution for session files.

## Key Findings

### 1. CLI Module Structure

**Location:** `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/`

**Files:**
- `cli.py` — Main CLI command group with subcommands (ls, new, merge, rm, clean-tree, add-commit)
- `merge.py` — Multi-phase merge implementation with auto-conflict resolution
- `session.py` — Session.md parsing and task movement utilities
- `utils.py` — Shared utilities (_git wrapper, wt_path calculation)

**CLI Entry Point:** Registered as `worktree` group command in main CLI (`cli.py` line 150). Invoked as `claudeutils _worktree <command>` or just `_worktree` via Click group name.

### 2. `wt-ls` Implementation

**Current Location:**
- Python CLI: `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/cli.py` lines 145-151
- Justfile recipe: `/Users/david/code/claudeutils-wt/design-workwoods/justfile` lines 134-136

**Python Implementation:**
```python
@worktree.command()
def ls() -> None:
    """List worktrees excluding main."""
    main_path = _git("rev-parse", "--show-toplevel")
    porcelain = _git("worktree", "list", "--porcelain")
    for slug, branch, path in _parse_worktree_list(porcelain, main_path):
        click.echo(f"{slug}\t{branch}\t{path}")
```

**Display Format:** Tab-separated output: `<slug>\t<branch>\t<path>`
- **slug:** Directory name extracted from worktree path
- **branch:** Git branch reference (e.g., `refs/heads/task-a`)
- **path:** Full worktree directory path

**Parser:** `_parse_worktree_list()` (lines 125-142) handles git porcelain parsing, skipping main repo path.

**Justfile Recipe:** Uses awk pattern-matching and direct git porcelain parsing (line 136):
```bash
@git worktree list --porcelain | awk '/^worktree/ {path=$2; branch=""} /^branch/ {branch=$2; sub(/^refs\/heads\//, "", branch)} /^$/ && branch != "" && path != "{{justfile_directory()}}" {n=split(path, parts, "/"); print parts[n] "\t" branch "\t" path; branch=""}'
```

### 3. `wt-merge` Implementation

**Location:**
- Python: `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/merge.py`
- Justfile: `/Users/david/code/claudeutils-wt/design-workwoods/justfile` lines 196-326

**Four-Phase Merge Process:**

**Phase 1: Validation** (`_phase1_validate_clean_trees()`, lines 159-183)
- Verify branch exists (exit code 2 if not)
- Check main tree clean (exempt: agents/session.md, agents/jobs.md, agents/learnings.md, agent-core)
- Check worktree clean

**Phase 2: Submodule Resolution** (`_phase2_resolve_submodule()`, lines 186-228)
- Extract agent-core commit from worktree branch via `git ls-tree`
- Compare with local agent-core HEAD
- If differs: test ancestry, fetch if needed, merge with `--no-edit`
- Commit merge result if staged changes exist

**Phase 3: Parent Merge** (`_phase3_merge_parent()`, lines 230-258)
- Initiate `git merge --no-commit --no-ff <slug>`
- Auto-resolve known conflicts:
  - **agent-core:** Keep ours (already merged in Phase 2)
  - **agents/session.md:** Keep ours base, extract new tasks from theirs via `extract_task_blocks()`, insert at Pending Tasks section bounds, handle blank line separation
  - **agents/learnings.md:** Keep ours, append theirs-only lines
  - **agents/jobs.md:** Keep ours (local plan status is authoritative)
- Abort merge if unresolved conflicts remain after auto-resolution

**Phase 4: Commit & Precommit** (`_phase4_merge_commit_and_precommit()`, lines 261-299)
- Commit merge: use `--allow-empty` if MERGE_HEAD exists (merge in progress), else normal commit
- Run `just precommit` validation
- Exit code 1 if precommit fails

**Exit Codes:**
- **0:** Success
- **1:** Conflicts or precommit failure
- **2:** Branch not found (fatal)

**Session.md Conflict Resolution** (`_resolve_session_md_conflict()`, lines 58-113):
- Keeps ours (parent) as base
- Extracts task blocks from theirs (worktree) via `extract_task_blocks()`
- Compares by task name to find new tasks
- Inserts new tasks at Pending Tasks section end (before next section)
- Handles blank line separation correctly

### 4. `wt-rm` Implementation

**Location:**
- Python: `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/cli.py` lines 347-382
- Justfile: `/Users/david/code/claudeutils-wt/design-workwoods/justfile` lines 140-194

**Cleanup Steps:**

1. **Probe Registration** (`_probe_registrations()`, lines 310-318)
   - Check parent worktree in `git worktree list`
   - Check submodule worktree in `agent-core` git worktree list

2. **Warn on Uncommitted Changes** (line 355-358)
   - Query `git status --porcelain` in worktree
   - Display count of dirty files

3. **Remove Session.md Entry** (lines 360-362)
   - Call `remove_worktree_task()` to remove task from Worktree Tasks section
   - Determines completion by checking if task still in pending section of worktree branch (`git show <branch>:agents/session.md`)
   - Only removes if task was completed in worktree

4. **Remove Worktrees** (`_remove_worktrees()`, lines 321-337)
   - Remove submodule worktree first with `--force` (git refuses parent removal while submodule exists)
   - Remove parent worktree with `--force`

5. **Cleanup Directory** (lines 375-380)
   - Delete remaining worktree directory if exists (orphaned cleanup)
   - Remove empty container directory

6. **Branch Cleanup** (lines 369-373)
   - Delete branch with `git branch -d <slug>`
   - If unmerged changes: echo warning message suggesting `git branch -D` (not executed)

7. **Output Status** (line 382): Confirmation message

### 5. Worktree Skill Structure

**Location:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/worktree/SKILL.md`

**Allowed Tools:**
- Read, Write, Edit
- Bash(claudeutils _worktree:*)
- Bash(just precommit)
- Bash(git status:*, git worktree:*, git add:*, git commit:*, git submodule:*, git branch:*, git log:*)
- Skill

**Three Modes:**

**Mode A: Single Task** (lines 33-45)
- User specifies `wt <task-name>`
- Read session.md to locate task
- Invoke `claudeutils _worktree new --task "<task name>"`
- Output: `<slug>\t<path>` (tab-separated)
- Automatically moves task from Pending Tasks to Worktree Tasks with `→ \`slug\`` marker

**Mode B: Parallel Group** (lines 47-82)
- User invokes `wt` with no arguments
- Analyzes pending tasks for independent groups based on:
  - Plan directory independence
  - Logical dependencies (blockers, gotchas)
  - Model tier compatibility
  - Restart requirement exclusion
- Selects largest independent group
- Creates multiple worktrees sequentially
- Outputs consolidated launch commands

**Mode C: Merge Ceremony** (lines 84-114)
- User invokes `wt merge <slug>`
- Calls `/handoff --commit` to ensure clean tree
- Invokes `claudeutils _worktree merge <slug>`
- Parses exit code: 0 (success, cleanup), 1 (conflicts, fix and retry), 2 (fatal)
- Handles conflict resolution:
  - Session files: auto-resolve
  - Source files: manual edit, re-run merge
  - Precommit failure: fix, amend, re-run merge
- Cleanup via `claudeutils _worktree rm <slug>`

**Key Properties:**
- Slug derivation is deterministic and repeatable
- Merge is idempotent (can be safely re-run)
- Session.md task movement is automated
- Cleanup is user-initiated (except Mode C includes cleanup)

### 6. Justfile Recipes

**Location:** `/Users/david/code/claudeutils-wt/design-workwoods/justfile` lines 54-194

**Recipes:**

**`wt-new name base="HEAD" session=""`** (lines 56-113)
- Creates worktree in sibling `-wt` container
- Supports optional focused session.md via `--session` parameter
- Creates session commit if provided (using temp git index)
- Creates parent worktree (existing branch or new branch with `-b`)
- Creates agent-core submodule worktree (shared object store)
- Registers container in sandbox permissions (both parent and local settings)
- Runs `just setup` or fallback `direnv allow && uv sync && npm install`
- Output: Success message with launch command

**`wt-task name task_name base="HEAD"`** (lines 117-132)
- Legacy recipe: generates focused session inline
- Creates temporary session.md file
- Extracts task from session.md via grep
- Delegates to `wt-new` with session file
- Cleans up temp session.md

**`wt-ls`** (lines 135-136)
- Direct git porcelain parsing via awk
- Excludes main repo path (checks against `justfile_directory()`)

**`wt-rm name`** (lines 140-194)
- Probes worktree and submodule registration
- Warns about uncommitted changes
- Removes submodule worktree first, then parent
- Cleans up orphaned directory
- Deletes branch or suggests `-D` for unmerged branches
- Output: Success message with path

**`wt-merge name`** (lines 198-326)
- Validates clean tree (exempts session files)
- Phase 2: Submodule resolution (explicit fetch fallback, merge, commit)
- Phase 3: Parent merge with auto-resolution:
  - agent-core: keep ours
  - session.md: keep ours, warn for new tasks (simplified)
  - learnings.md: warn for merge (simplified)
  - jobs.md: warn for merge (simplified)
- Phase 4: Commit merge, run precommit gate
- Output: Success message with cleanup command

### 7. Session.md Parsing & Task Movement

**Location:** `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/session.py`

**TaskBlock Dataclass** (lines 9-15):
- `name`: Task name (extracted from markdown)
- `lines`: All lines (task line + continuation lines)
- `section`: Section name ("Pending Tasks", "Worktree Tasks")

**Key Functions:**

**`extract_task_blocks(content, section=None)`** (lines 18-82)
- Parses task blocks matching pattern: `- [[ x>]] **<task-name>**`
- Collects continuation lines (indented, non-blank)
- Stops at next task, section header, or blank line
- Filters by section if provided
- Returns list of TaskBlock instances

**`find_section_bounds(content, header)`** (lines 85-115)
- Locates section by header name (without "## " prefix)
- Returns (start_line, end_line) tuple
- end_line is next "## " header or EOF

**`move_task_to_worktree(session_path, task_name, slug)`** (lines 118-184)
- Finds task in Pending Tasks (or checks Worktree Tasks for idempotency)
- Adds `→ \`slug\`` marker to task first line
- Removes task from Pending Tasks
- Creates or locates Worktree Tasks section
- Inserts task block with blank line separation
- Handles section creation if missing

**`remove_worktree_task(session_path, slug, worktree_branch)`** (lines 217-262)
- Finds task in Worktree Tasks by slug marker
- Checks if task completed in worktree branch via `git show <branch>:agents/session.md`
- Only removes if task no longer in branch's Pending Tasks
- Uses `_task_is_in_pending_section()` helper to check branch state

### 8. Utility Functions

**Location:** `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/utils.py`

**`_git(*args, check=True, env=None, input_data=None)`** (lines 7-21)
- Subprocess wrapper for git commands
- Captures stdout, strips whitespace
- Supports custom env dict and stdin input
- Respects check flag for error handling

**`wt_path(slug, create_container=False)`** (lines 24-38)
- Calculates worktree path in sibling `-wt` container
- If already in `-wt` directory, returns path in same container
- Otherwise creates path in `<project>-wt/<slug>`
- Optionally creates container directory

### 9. Additional Commands

**`new --task`** (lines 270-296 of cli.py)
- CLI command with `--task` option for task-specific worktree creation
- Derives slug from task name via `derive_slug()`
- Calls `focus_session()` to generate focused session.md
- Invokes `_setup_worktree()` which creates parent and submodule worktrees
- Calls `move_task_to_worktree()` to update session.md

**`focus_session(task_name, session_md_path)`** (lines 62-84)
- Generates focused session.md for single task
- Filters to just that task in Pending Tasks
- Includes relevant Blockers/Gotchas and Reference Files sections
- Returns formatted session content

**`derive_slug(task_name)`** (lines 23-35)
- Validates task name format
- Converts to lowercase, replaces non-alphanumeric with hyphens
- Strips leading/trailing hyphens
- Returns deterministic slug

**`clean-tree`** (lines 243-261)
- Verifies clean tree except for session context files
- Checks parent repo and agent-core submodule
- Exempts: session.md, jobs.md, learnings.md
- Exits code 1 if dirty files found (excluding exempts)

**`add-commit`** (lines 299-307)
- Stages multiple files
- Reads commit message from stdin
- Only commits if staged changes exist

### 10. Key Architectural Patterns

**Slug-Based Identity:**
- Slug is deterministic, repeatable identifier for worktrees
- Derived from task name via lowercase + hyphen normalization
- Used to track worktree in session.md via `→ \`slug\`` marker
- Enables `wt merge <slug>` to always operate on correct branch/worktree

**Session File Auto-Resolution:**
- Three-file conflict resolution strategy: session.md, learnings.md, jobs.md
- session.md: Keep ours base, extract new tasks from theirs (merge logic)
- learnings.md: Keep ours, append theirs-only lines (union)
- jobs.md: Keep ours (local plan status authoritative)
- All auto-resolved before manual resolution required

**Submodule Worktree Pattern:**
- Agent-core branch created alongside parent branch
- Shared object store approach (git worktree not --reference clone)
- Merge resolves submodule via ancestor test, fetch if needed, merge HEAD
- Phase 2 of merge handles submodule independently before parent merge

**Session.md Task Lifecycle:**
1. Pending Tasks → Worktree Tasks (with slug marker) on `wt new --task`
2. Worktree Tasks → (completed or deleted) based on branch state on `wt rm`
3. New tasks created in worktree branch merged back to main Pending Tasks on `wt merge`

**Dual Implementation Pattern:**
- Python CLI (`claudeutils _worktree`) provides primary implementation
- Justfile recipes (`wt-*`) provide convenience shortcuts
- Justfile recipes partially replicate Python logic (merge, rm) with bash implementations
- Python implementation used by Worktree skill; justfile used by terminal users

## Patterns & Conventions

### Naming
- Worktree containers use `-wt` suffix convention
- Slugs are lowercase, hyphen-separated (e.g., `my-task-name`)
- Branches named same as slugs

### Error Handling
- Exit codes: 0 (success), 1 (merge conflicts/precommit fail), 2 (fatal/validation fail)
- Warnings printed to stderr, suggestions for manual steps provided
- Destructive operations (branch -D) suggested but not auto-executed

### Session File Management
- Three file exemptions in merge clean tree check: session.md, jobs.md, learnings.md
- These are workflow-context files, not code files
- Auto-resolved in merge; no manual intervention needed for session conflicts

### Sandbox Permissions
- Worktree containers registered in `.claude/settings.local.json`
- Both parent container and local worktree settings receive permissions
- Enables Claude Code sandbox access to worktree directory

### Submodule Handling
- Agent-core worktrees created/removed with parent worktrees
- Submodule worktree removed FIRST (git constraint)
- Merge resolves submodule commits before parent merge

## Gaps & Observations

1. **Justfile merge/rm simplifications:** Justfile implementations have simplified conflict resolution (warn for manual merge, no actual merge logic for learnings/jobs). Python implementation is more complete.

2. **Focus session limitations:** `focus_session()` filters to single task and relevant context, but doesn't handle deeply nested blockers/dependencies.

3. **Slug validation:** Uses task name format validation, but no explicit slug length limits or character restrictions beyond alphanumeric + hyphens.

4. **Worktree discovery:** `wt-ls` and `wt-rm` both probe registration state, but no unified "get worktree status" command that shows incomplete state.

5. **Container path calculation:** `wt_path()` has heuristic for detecting if already in `-wt` directory (checks parent name), could be more explicit.

6. **Session move idempotency:** `move_task_to_worktree()` checks for task already in Worktree Tasks, but only for early return; doesn't prevent double-insertion if task appears in both sections.

7. **Merge conflict handling:** Auto-resolution is specific to three known files (session, learnings, jobs). Other files must be manually resolved; no batching or list provided to user.

## References

**Key Implementation Files:**
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/cli.py` — Primary CLI implementation
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/merge.py` — Merge orchestration
- `/Users/david/code/claudeutils-wt/design-workwoods/src/claudeutils/worktree/session.py` — Session parsing and task movement
- `/Users/david/code/claudeutils-wt/design-workwoods/justfile` — Justfile recipes (lines 54-326)
- `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/worktree/SKILL.md` — Skill definition and modes

**Test Coverage:**
- `/Users/david/code/claudeutils-wt/design-workwoods/tests/test_worktree_*.py` — 17+ test files covering CLI commands, merge phases, session parsing, and cleanup
