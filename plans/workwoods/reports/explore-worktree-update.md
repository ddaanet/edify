# Worktree Update Implementation — Comprehensive Exploration

## Summary

The worktree-update plan delivered a complete refactor of worktree operations, replacing justfile recipes with a Python CLI (`claudeutils _worktree`) and a coordinating Bash skill. The implementation spans three modules (`cli.py`, `merge.py`, `utils.py`) providing creation, removal, merging, and session manipulation. The worktree-merge-data-loss plan identified and designed fixes for two compounding bugs: single-parent merge commits (data loss) and rm suggesting destructive commands that agents execute. This exploration documents the current state and identifies integration points for workwoods FR-4 (bidirectional merge) and FR-5 (additive task combine).

## Current Implementation

### Module Structure

**Location:** `/Users/david/code/claudeutils/src/claudeutils/worktree/`

**Files:**
- `utils.py` — Shared helpers (`_git`, `wt_path`)
- `cli.py` — Click commands (new, rm, merge, ls, clean-tree, add-commit)
- `merge.py` — Four-phase merge orchestration with conflict resolution
- `session.py` — Session.md parsing and editing utilities

### Core Functions

#### `wt_path(slug, create_container=False) -> Path` (utils.py)

Computes sibling container worktree path. **Key design: isolated from CLAUDE.md inheritance.**

```python
def wt_path(slug: str, create_container: bool = False) -> Path:
    current_path = Path.cwd()
    parent_name = current_path.parent.name
    container_path = (
        current_path.parent
        if parent_name.endswith("-wt")
        else current_path.parent / f"{current_path.name}-wt"
    )
    if create_container and not parent_name.endswith("-wt"):
        container_path.mkdir(parents=True, exist_ok=True)
    return container_path / slug
```

**Behavior:**
- If running from within a `-wt` container, use sibling path (stay in container)
- Otherwise create `<repo>-wt>` sibling container
- Returns absolute Path to `<container>/<slug>`
- **NFR satisfaction:** Prevents CLAUDE.md scope pollution in worktrees

#### `derive_slug(task_name: str) -> str` (cli.py)

Converts task name to slug via regex. **Used by `new --task` mode.**

```python
def derive_slug(task_name: str) -> str:
    if not task_name or not task_name.strip():
        raise ValueError("task_name must not be empty")
    format_errors = validate_task_name_format(task_name)
    if format_errors:
        raise ValueError(format_errors[0])
    return re.sub(r"[^a-z0-9]+", "-", task_name.lower()).strip("-")
```

**Process:** lowercase → replace non-alphanumeric with hyphens → strip trailing hyphens

#### `focus_session(task_name: str, session_md_path: str | Path) -> str` (cli.py)

Generates focused session.md from full session file. **Core of Mode A task-based creation.**

```python
def focus_session(task_name: str, session_md_path: str | Path) -> str:
    content = Path(session_md_path).read_text()
    blocks = extract_task_blocks(content, section="Pending Tasks")
    task_block = next((b for b in blocks if b.name == task_name), None)
    if not task_block:
        raise ValueError(f"Task '{task_name}' not found in session.md")

    task_lines_str = "\n".join(task_block.lines)
    plan_dir = (m.group(1) if (m := re.search(r"[Pp]lan:\s*(\S+)", task_lines_str)) else None)

    result = (
        f"# Session: Worktree — {task_name}\n\n"
        f"**Status:** Focused worktree for parallel execution.\n\n"
        f"## Pending Tasks\n\n{task_lines_str}\n"
    )
    for section in ["Blockers / Gotchas", "Reference Files"]:
        if filtered := _filter_section(content, section, task_name, plan_dir):
            result += f"\n{filtered}"
    return result
```

**Output:** String with H1, Status, Pending Tasks (single task), relevant Blockers/Gotchas and Reference Files.

#### `add_sandbox_dir(container: str, settings_path: str | Path) -> None` (cli.py)

Registers container in `.claude/settings.local.json` for sandbox access.

```python
def add_sandbox_dir(container: str, settings_path: str | Path) -> None:
    path = Path(settings_path)
    if path.exists():
        settings = json.loads(path.read_text())
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        settings = {"permissions": {"additionalDirectories": []}}
    dirs = settings.setdefault("permissions", {}).setdefault(
        "additionalDirectories", []
    )
    if container not in dirs:
        dirs.append(container)
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False))
```

**Behavior:**
- Creates `.claude/settings.local.json` if missing
- Appends container path to `permissions.additionalDirectories` (no duplication)
- Writes to both main repo and worktree

### Commands

#### `new` Command

**Modes:**
1. **Explicit slug:** `claudeutils _worktree new <slug> [--base HEAD] [--session <path>]`
2. **Task-based:** `claudeutils _worktree new --task "<name>" [--base HEAD] [--session-md <path>]`

**Subcommands invoked:**
- `_create_parent_worktree()` — Creates branch and parent worktree
- `_create_submodule_worktree()` — Creates worktree-based agent-core worktree (not `--reference` clone)
- `add_sandbox_dir()` — Registers container directory
- `initialize_environment()` — Runs `just setup` if available

**Key behaviors:**
- Existing branch reuse: if branch exists, skips `--session` with warning and uses existing branch
- Worktree-based submodule: `git -C agent-core worktree add <path>/agent-core <slug>` (shared object store, bidirectional visibility)
- Output: task mode prints `<slug>\t<path>` (tab-separated), explicit mode prints path only

#### `merge` Command

**Signature:** `claudeutils _worktree merge <slug>`

**Four-phase implementation:**

##### Phase 1: Validation (`_phase1_validate_clean_trees`)

Checks branch exists and trees are clean.

```python
def _phase1_validate_clean_trees(slug: str) -> None:
    r = subprocess.run(
        ["git", "rev-parse", "--verify", slug],
        capture_output=True, text=True, check=False
    )
    if r.returncode != 0:
        click.echo(f"Branch {slug} not found")
        raise SystemExit(2)

    # Check main repo tree (OURS with exemptions)
    _check_clean_for_merge(
        exempt_paths={
            "agents/session.md",
            "agents/jobs.md",
            "agents/learnings.md",
            "agent-core",
        }
    )
    # Check worktree tree (THEIRS strict, no exemptions)
    _check_clean_for_merge(path=wt_path(slug), label="worktree")
```

**Exit codes:** 0 (pass), 1 (dirty tree), 2 (branch not found)

**Key detail:** THEIRS clean tree is strict (no session file exemption) — uncommitted state would be lost by merge.

##### Phase 2: Submodule Resolution (`_phase2_resolve_submodule`)

Merges agent-core submodule if worktree and local versions differ.

```python
def _phase2_resolve_submodule(slug: str) -> None:
    wt_ls_output = _git("ls-tree", slug, "--", "agent-core", check=False)
    if not wt_ls_output:
        return  # No submodule to resolve

    wt_commit = wt_ls_output.split()[2]
    local_commit = _git("-C", "agent-core", "rev-parse", "HEAD", check=False)

    if wt_commit == local_commit:
        return  # Already at same commit

    # Check ancestry
    result = subprocess.run(
        ["git", "-C", "agent-core", "merge-base", "--is-ancestor", wt_commit, local_commit],
        check=False
    )

    if result.returncode != 0:
        # Not ancestor — need to merge
        # Verify commit is reachable
        result = subprocess.run(
            ["git", "-C", "agent-core", "cat-file", "-e", wt_commit],
            check=False
        )
        if result.returncode != 0:
            # Unreachable — fetch from worktree
            wt_agent_core = wt_path(slug) / "agent-core"
            _git("-C", "agent-core", "fetch", str(wt_agent_core), "HEAD")

        # Merge submodule
        _git("-C", "agent-core", "merge", "--no-edit", wt_commit)
        _git("add", "agent-core")

        # Commit if staged changes exist
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet", "agent-core"],
            check=False
        )
        if result.returncode != 0:
            _git("commit", "-m", f"🔀 Merge agent-core from {slug}")
```

**Key behavior:** Creates intermediate commit on main if submodule differs. **This is a known trigger for MERGE_HEAD disappearance** (worktree-merge-data-loss root cause).

##### Phase 3: Parent Merge (`_phase3_merge_parent`)

Initiates merge with auto-resolution for known conflicts.

```python
def _phase3_merge_parent(slug: str) -> None:
    result = subprocess.run(
        ["git", "merge", "--no-commit", "--no-ff", slug],
        capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        return  # Clean merge

    # Conflicts occurred
    conflicts = _git("diff", "--name-only", "--diff-filter=U", check=False).split("\n")
    conflicts = [c for c in conflicts if c.strip()]

    # Auto-resolve agent-core (handled in Phase 2)
    if "agent-core" in conflicts:
        _git("checkout", "--ours", "agent-core")
        _git("add", "agent-core")
        conflicts = [c for c in conflicts if c != "agent-core"]

    # Auto-resolve session.md (extract new tasks from theirs, keep ours)
    conflicts = _resolve_session_md_conflict(conflicts)

    # Auto-resolve learnings.md (append theirs-only lines to ours)
    conflicts = _resolve_learnings_md_conflict(conflicts)

    # Auto-resolve jobs.md (keep ours, warn)
    conflicts = _resolve_jobs_md_conflict(conflicts)

    if conflicts:
        _git("merge", "--abort")
        _git("clean", "-fd")
        conflict_list = ", ".join(conflicts)
        click.echo(f"Merge aborted: conflicts in {conflict_list}")
        raise SystemExit(1)
```

**Exit codes:** 0 (clean or resolved), 1 (unresolved conflicts)

**Conflict resolution strategies:**
- `agent-core`: Take ours (already merged in Phase 2)
- `session.md`: Keep ours, extract new tasks from theirs (additive combination)
- `learnings.md`: Keep ours, append theirs-only lines (union)
- `jobs.md`: Keep ours with warning
- Source files: Abort with conflict list (manual resolution required)

##### Phase 4: Commit and Precommit (`_phase4_merge_commit_and_precommit`)

Commits merge and validates with precommit.

```python
def _phase4_merge_commit_and_precommit(slug: str) -> None:
    merge_in_progress = (
        subprocess.run(
            ["git", "rev-parse", "--verify", "MERGE_HEAD"],
            capture_output=True, check=False
        ).returncode == 0
    )

    staged_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        check=False
    )

    if merge_in_progress:
        _git("commit", "--allow-empty", "-m", f"🔀 Merge {slug}")
    elif staged_check.returncode != 0:
        _git("commit", "-m", f"🔀 Merge {slug}")

    precommit_result = subprocess.run(
        ["just", "precommit"],
        capture_output=True, text=True, check=False
    )

    if precommit_result.returncode == 0:
        click.echo("Precommit passed")
    else:
        click.echo("Precommit failed after merge")
        click.echo(precommit_result.stderr)
        raise SystemExit(1)
```

**Exit codes:** 0 (success), 1 (precommit failure)

**Current bug:** If MERGE_HEAD is absent (due to Phase 2 intermediate commit) and staged changes exist, takes `elif` path → single-parent commit instead of two-parent merge commit. **Files from worktree branch are lost.**

#### `rm` Command

**Signature:** `claudeutils _worktree rm <slug>`

**Current behavior:**

```python
def rm(slug: str) -> None:
    """Remove worktree and its branch."""
    worktree_path = wt_path(slug)
    parent_reg, submodule_reg = _probe_registrations(worktree_path)

    if worktree_path.exists():
        status = _git("-C", str(worktree_path), "status", "--porcelain", check=False)
        if status:
            count = len(status.strip().split("\n"))
            click.echo(f"Warning: worktree has {count} uncommitted files")

    session_md_path = Path("agents/session.md")
    if session_md_path.exists():
        remove_worktree_task(session_md_path, slug, slug)

    if parent_reg or submodule_reg:
        _remove_worktrees(worktree_path, parent_reg, submodule_reg)
    else:
        _git("worktree", "prune")

    r = subprocess.run(
        ["git", "branch", "-d", slug], capture_output=True, text=True, check=False
    )
    if r.returncode != 0 and "not found" not in r.stderr.lower():
        click.echo(f"Branch {slug} has unmerged changes — use: git branch -D {slug}")

    if worktree_path.exists():
        shutil.rmtree(worktree_path)

    container = worktree_path.parent
    if container.exists() and not list(container.iterdir()):
        container.rmdir()

    click.echo(f"Removed worktree {slug}")
```

**Current issues:**
1. **Suggests destructive command:** Output line `"use: git branch -D {slug}"` — agents follow this instruction and force-delete unmerged branches, losing work
2. **No guard for unmerged real history:** Removes worktree directory (line `shutil.rmtree(worktree_path)`) before detecting branch merge status
3. **No distinction:** Treats all unmerged branches the same, including focused-session-only (auto-generated) vs real-history branches

**Submodule-first ordering:**

```python
def _remove_worktrees(
    worktree_path: Path,
    parent_registered: bool,
    submodule_registered: bool,
) -> None:
    """Remove worktrees (submodule first, force flag)."""
    if submodule_registered:
        _git(
            "-C", "agent-core",
            "worktree", "remove", "--force",
            str(worktree_path / "agent-core")
        )
    if parent_registered:
        _git("worktree", "remove", "--force", str(worktree_path))
```

**Correct behavior:** Removes submodule worktree first (git refuses parent removal while submodule exists).

#### `ls` Command

**Output:** Parses `git worktree list --porcelain`, excludes main, prints tab-separated: `<slug>\t<branch>\t<path>`

### Session Manipulation

**Module:** `session.py`

#### Core Parsing

**`extract_task_blocks(content: str, section: str | None = None) -> list[TaskBlock]`**

Extracts task blocks from session.md, optionally filtered by section ("Pending Tasks", "Worktree Tasks").

```python
@dataclass
class TaskBlock:
    name: str              # Task name from "**<name>**"
    lines: list[str]       # Full task block (task line + continuations)
    section: str           # Section name containing the task
```

**Parsing rules:**
- Recognizes task lines: `- [[ x>]] **<name>**`
- Collects continuation lines (indented following the task)
- Stops at next task, next section header, or blank line
- Filters by section if requested

#### Conflict Resolution: Session.md

**`_resolve_session_md_conflict(conflicts: list[str]) -> list[str]`**

Automatically resolves session.md conflicts during merge.

**Algorithm:**
1. Extract task blocks from both sides (`:2:` = ours, `:3:` = theirs)
2. Compare by task name → find new tasks (in theirs but not ours)
3. Insert new tasks into ours content before next section header
4. Write merged result, stage it
5. Return updated conflict list (session.md removed)

**Behavior:** **Additive merge — combines tasks from both sides.**

#### Conflict Resolution: Learnings.md

**`_resolve_learnings_md_conflict(conflicts: list[str]) -> list[str]`**

Resolves learnings.md conflicts by union.

**Algorithm:**
1. Extract ours and theirs content
2. Find theirs-only lines (lines in theirs not in ours)
3. Append theirs-only lines to ours
4. Write merged result, stage it
5. Return updated conflict list

#### Task Movement

**`move_task_to_worktree(session_path: Path, task_name: str, slug: str) -> None`**

Moves task from Pending Tasks to Worktree Tasks with slug marker.

```python
# Input line: - [ ] **Task Name** — metadata
# Output line: - [ ] **Task Name** → `slug` — metadata
```

**Flow:**
1. Find task in Pending Tasks
2. Add slug marker via regex substitution
3. Remove from Pending Tasks section
4. Create Worktree Tasks section if missing
5. Insert task block
6. Write result

**`remove_worktree_task(session_path: Path, slug: str, worktree_branch: str) -> None`**

Removes task from Worktree Tasks only if completed (no longer in branch's Pending Tasks).

**Flow:**
1. Find task in Worktree Tasks by slug marker
2. Check if task still pending in worktree branch (via `git show <branch>:agents/session.md`)
3. If completed: remove from Worktree Tasks
4. If still pending: keep entry
5. Write result

## Test Suite Coverage

**Location:** `/Users/david/code/claudeutils-wt/design-workwoods/tests/`

**Core test files:**

| Test File | Purpose | Count |
|-----------|---------|-------|
| `fixtures_worktree.py` | Shared fixtures (repo_with_submodule, commit_file, mock_precommit) | ~150 lines |
| `test_worktree_commands.py` | CLI command behavior | — |
| `test_worktree_new_creation.py` | `new` command with various modes | — |
| `test_worktree_rm.py` | `rm` command removal logic | — |
| `test_worktree_merge_*.py` | Phase-specific merge tests (parent, conflicts, jobs, session, submodule) | 835 total lines |
| `test_worktree_session*.py` | Session.md parsing and manipulation | — |

**Test patterns:**
- Real git repos via `repo_with_submodule` fixture (no mocked subprocess except precommit)
- E2E scenarios with actual branch creation, commits, merges
- Exit code validation for all branches
- Conflict resolution verification

## Known Issues and Design Debt

### Bugs Fixed by worktree-merge-data-loss Plan

**Bug 1: Single-parent merge commits (data loss)**
- **Location:** `merge.py` Phase 4 (lines 284-285)
- **Trigger:** MERGE_HEAD absent + staged changes + unmerged branch
- **Result:** Regular commit instead of merge commit → branch parent missing → files lost
- **Root cause:** Phase 2 intermediate commit (submodule merge) makes MERGE_HEAD disappear between Phase 3 and Phase 4
- **Fix in design.md:** MERGE_HEAD checkpoint — exit 2 if branch not merged and MERGE_HEAD absent
- **Additional check:** `_validate_merge_result()` — post-merge ancestry check (defense-in-depth)

**Bug 2: `rm` suggests destructive commands**
- **Location:** `cli.py` lines 372-373
- **Trigger:** Branch has unmerged changes, `-d` fails
- **Result:** Output message "use: git branch -D {slug}" → agents execute it → permanent data loss
- **Fix in design.md:** Track 1 removal safety guard — classify branch before removal, refuse unmerged real-history branches (exit 1), only allow focused-session-only unmerged branches
- **Guard function:** `_classify_branch()` — distinguish 1-commit focused-session vs real-history branches via marker text

### Current Limitations

**`_filter_section()` continuation handling (M1 from recovery notes)**
- Non-bullet lines can leak into filtered output for Blockers/Gotchas section
- Affects `focus_session()` filtering quality
- Deferred to post-merge cleanup (low impact)

**`plan_dir` regex case-sensitivity (M2)**
- Won't match title-case "Plan:" in metadata lines
- Minor impact, deferred to recovery phase

## Workwoods Integration Points

### FR-4: Bidirectional Merge (Modify `merge` behavior)

**Current behavior:** Merge succeeds, deletes worktree (design doesn't explicitly delete, but skill does via separate `rm` call)

**Required change:** `merge` should NOT delete worktree. Worktree remains active after merge, can receive updates and merge back.

**Impact on `merge` command:**
- No behavior change needed — already doesn't delete
- Skill Mode C needs update: merge then optionally rm (user decision, not automatic)

**Impact on `rm` command:**
- Add guard (worktree-merge-data-loss Track 1) — refuse removal of unmerged real-history branches
- Focused-session branches (auto-generated) can still be removed even if unmerged

### FR-5: Additive Task Merge (Session.md combine behavior)

**Current implementation:** `_resolve_session_md_conflict()` already does additive merge!

**Algorithm:**
1. Extract tasks from both sides (ours + theirs)
2. Find new tasks (theirs-only by name comparison)
3. Insert new tasks into ours section before next section header
4. Write merged result

**Behavior:** **Union by task name — tasks combine across trees.**

**Integration with R1 (worktree-update recovery):**

Worktree-update recovery plan defers R1 (auto-combine session.md/jobs.md) to workwoods. The current implementation already does session.md additive merge. **R1 overlap:** workwoods FR-5 implements the deferred R1 requirement (additive task combine).

**Implementation note:** Session.md auto-combine is deterministic (code-driven), not agent-driven. No special handoff needed — merge command applies it automatically.

### FR-3: Plan State Inference (New feature, not modifying current code)

Requires new status-discovery logic outside worktree module. Current module provides:
- `wt_path(slug)` — locate worktree directory
- `ls` command output — list active worktrees with branches

**Data sources for plan inference:**
- Filesystem: `plans/<name>/` directory structure, artifact mtimes
- Git: `git log -1 --format=%H -- agents/session.md` (work count anchor)
- Session.md: base status from file content (design/planned/complete)

**Not in current worktree module:** Plan state inference is new, independent of merge/rm/new logic.

### FR-1: Cross-tree Status Display (wt-ls upgrade)

**Current `ls` command:** Parses `git worktree list --porcelain`, outputs `<slug>\t<branch>\t<path>`.

**Workwoods upgrade required:**
- Read across all trees (main + all worktrees)
- Per-tree status: session.md base status, commit count, latest commit, tree clean/dirty, recency
- Sort by recency (most recent first)
- Include vet artifact validity (design/runbook vet chain status)

**Not modifying current `ls` command:** New CLI command or upgraded recipe, not integration into existing `ls`.

## Key Design Patterns

### Sibling Container Isolation

Worktrees in `../<repo>-wt>/<slug>/` (not `wt/<slug>` inside repo).

**Rationale:** Claude Code loads CLAUDE.md from all parents. Inside-repo worktrees inherit main repo's CLAUDE.md context → scope pollution.

**Implementation:** `wt_path()` detects parent `-wt` suffix, creates container if needed.

**Benefit for workwoods:** Cross-tree status reads don't need to load each tree's CLAUDE.md; trees are isolated, reads are read-only.

### Worktree-Based Submodule (Not --reference Clone)

`git -C agent-core worktree add <path>/agent-core <slug>` creates worktree of submodule.

**Rationale:** Shared object store (inherent in worktree), bidirectional commit visibility (objects shared, not cloned).

**Phase 2 consequence:** If worktree's agent-core differs from local, Phase 2 may create intermediate commit on main. **This is the trigger for MERGE_HEAD disappearance** (addressed by worktree-merge-data-loss checkpoint).

### Deterministic Conflict Resolution

Session.md, learnings.md, jobs.md conflicts are resolved deterministically by code, not agent judgment.

**Strategies:**
- Session.md: Additive (union by task name)
- Learnings.md: Additive (append theirs-only lines)
- Jobs.md: Keep ours (plan status is local authority)
- Source files: Abort with conflict list (manual resolution required)

**Behavior:** Agents never need to make judgment calls; merge either succeeds automatically or fails with concrete conflict list.

### Four-Phase Merge Ceremony

Validation → Submodule Resolution → Parent Merge → Commit + Precommit

**Rationale:** Separates concerns (clean tree, submodule divergence, parent merge conflicts, validation). Each phase is idempotent — merge can resume after conflict resolution.

**Order sensitivity:** Phase 2 (submodule) must precede Phase 3 (parent merge) because Phase 2 may create intermediate commit that affects MERGE_HEAD presence in Phase 4.

## File Locations (Absolute Paths)

**Source code:**
- `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py` — Commands (new, rm, merge, ls, clean-tree, add-commit)
- `/Users/david/code/claudeutils/src/claudeutils/worktree/merge.py` — Four-phase merge with auto-conflict resolution
- `/Users/david/code/claudeutils/src/claudeutils/worktree/utils.py` — `_git()`, `wt_path()`
- `/Users/david/code/claudeutils/src/claudeutils/worktree/session.py` — Session.md parsing and editing

**Design documents:**
- `/Users/david/code/claudeutils-wt/design-workwoods/plans/worktree-update/design.md` — Complete refactor design (scope, architecture, test updates)
- `/Users/david/code/claudeutils-wt/design-workwoods/plans/worktree-merge-data-loss/design.md` — Bug fixes (removal safety guard, merge correctness, skill update)
- `/Users/david/code/claudeutils-wt/design-workwoods/plans/worktree-skill/design.md` — Original skill/CLI coordination design

**Tests:**
- `/Users/david/code/claudeutils-wt/design-workwoods/tests/fixtures_worktree.py` — Shared fixtures
- `/Users/david/code/claudeutils-wt/design-workwoods/tests/test_worktree_*.py` — Phase-specific test files

## Key Insights for Workwoods

### 1. Session.md Additive Merge Already Implemented

`_resolve_session_md_conflict()` in `merge.py` implements FR-5 (additive task combine). No code changes needed — merge automatically unions tasks from both trees by name.

**Implication for R1:** Worktree-update recovery deferred R1 (auto-combine) because workwoods would redesign it. Current implementation satisfies R1. Integration is transparent.

### 2. Phase 2 (Submodule) Creates Intermediate Commits

If worktree's agent-core differs from local, Phase 2 commits the submodule merge to main BEFORE Phase 3 (parent merge) begins.

**Consequence:** MERGE_HEAD may be absent when Phase 4 runs, triggering the single-parent commit bug (addressed by worktree-merge-data-loss checkpoint).

**For workwoods:** When designing bidirectional merge, be aware submodule resolution creates intermediate commits. Design must account for merge-in-progress state loss between phases.

### 3. Removal Guard Must Distinguish Branch Types

Current `rm` command doesn't distinguish:
- Focused-session-only branches (1 commit with marker text, safe to delete even if unmerged)
- Real-history branches (multiple commits or user-authored content, must be merged first)

**Worktree-merge-data-loss Track 1** implements guard via `_classify_branch()` — counts commits since merge-base and checks for marker text.

**For workwoods:** When implementing FR-4 (no auto-delete), the removal guard becomes critical. Users will manually call `rm` on long-lived worktrees after merge. Guard must prevent accidental loss of unmerged real history.

### 4. No Jobs.md Dependency in Merge Logic

Merge operates on git state (branches, commits, files) and session.md state (task blocks). Does not read/write jobs.md.

**FR-6 (eliminate jobs.md)** can be designed independently. Merge logic is unaffected.

### 5. Sibling Container Pattern Enables Cross-tree Reads

Worktrees in `../<repo>-wt>/<slug>/` are outside main repo. Status discovery can read all trees' session.md and artifacts without inheriting CLAUDE.md scope pollution.

**For FR-1/FR-3 (status display, plan inference):** Design can safely read across all trees without needing Claude Code context manipulation.

## Recommendations for Workwoods Design

1. **Session.md additive merge:** Leverage existing implementation. No code changes needed for FR-5 — just document the behavior in workwoods spec.

2. **Removal guard deployment:** Worktree-merge-data-loss design is ready for implementation. Deploy Track 1 (guard) and Track 2 (merge correctness fixes) BEFORE workwoods design executes, to prevent data loss incidents during bidirectional merge testing.

3. **Merge idempotency:** Current implementation is idempotent (can resume after conflict resolution). FR-4 (no auto-delete) doesn't require idempotency changes; merge already supports it.

4. **Plan inference data sources:** Current worktree module provides `ls` (tree listing) and `wt_path()` (locate tree). Plan inference needs new logic to read filesystem + git state + session.md across trees. Design as independent feature.

5. **Status display integration point:** `ls` command output is tab-separated structure (`<slug>\t<branch>\t<path>`). Upgrade can extend format or create new command; current `ls` is sufficient for basic discovery.
