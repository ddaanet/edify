# Worktree Skill — Design

## Problem Statement

Worktree operations span 5 justfile recipes with known defects: blind `--ours` session.md resolution loses worktree-side tasks, missing focus-session.py breaks `wt-task`, no session file merge intelligence. Replace with a `claudeutils _worktree` CLI subcommand (TDD) and a `/worktree` skill orchestrating ceremony and session manipulation.

## Requirements

**Source:** `plans/worktree-skill/outline.md` (validated, vet-clean)

**Functional:**

- FR-1: CLI subcommand `_worktree` with new/rm/merge/ls/clean-tree/add-commit — addressed by CLI Specification
- FR-2: Submodule merge resolution (ancestry check, fetch, merge, verify) — addressed by Merge Flow Phase 2
- FR-3: Session file conflict resolution extracting new tasks before merge — addressed by Conflict Resolution: Session Files
- FR-4: Source code conflict resolution (take-ours + precommit gate + fallback) — addressed by Conflict Resolution: Source Code
- FR-5: SKILL.md orchestrating session manipulation, ceremony, parallel detection — addressed by Skill Design
- FR-6: execute-rule.md Mode 5 update to reference skill — addressed by Documentation Updates
- FR-7: Delete justfile wt-* recipes — addressed by Documentation Updates (Justfile recipe deletion)
- FR-8: Integration tests with real git repos + submodules — addressed by Testing Strategy

**Non-functional:**

- NFR-1: Merge is idempotent — can resume after conflict resolution
- NFR-2: All session/learnings/jobs conflict resolution is deterministic (no agent judgment)
- NFR-3: Submodule commits use direct git plumbing, not `/commit` skill
- NFR-4: Post-merge precommit is mandatory correctness gate
- NFR-5: CLI follows existing claudeutils patterns (Click, error to stderr, exit codes)

**Out of scope:**

- Parallel detection scripting (prose in skill, not CLI)
- focus-session.py implementation changes (use as-is or generate manually)
- Stale worktree cleanup automation
- Backward compatibility with `wt/<name>` branch naming

## Architecture

### Package Structure

```
src/claudeutils/worktree/
├── __init__.py        # Empty (minimal __init__.py convention)
├── cli.py             # Click group + subcommand handlers
├── merge.py           # Merge orchestration + conflict resolution
└── utils.py           # Path utilities and helper functions
```

Registration in main `cli.py`:
```python
from claudeutils.worktree.cli import worktree
cli.add_command(worktree, "_worktree")
```

Test structure:
```
tests/
├── test_worktree_cli.py       # new, rm, ls, clean-tree, add-commit
├── test_worktree_merge.py     # Full merge flow + submodule resolution
└── test_worktree_conflicts.py # Session file + source code conflicts
```

**Implementation note:** Conflict resolution functions are in `merge.py`, not a separate `conflicts.py` module. The design initially specified `conflicts.py`, but implementation consolidated all merge-related logic into `merge.py` for cohesion.

### Conventions and Naming

| Item | Convention | Rationale |
|------|-----------|-----------|
| Branch name | `<slug>` (no prefix) | User requirement. Collision check on create. |
| Directory | `../<repo>-wt/<slug>/` (sibling container) | Avoids CLAUDE.md inheritance from parent directories. |
| Merge commit | `🔀 Merge <slug>` (or `🔀 <custom>` via `--message`) | Hardcoded gitmoji — always correct for merges. |
| Submodule merge commit | `🔀 Merge agent-core from <slug>` | Deterministic, no `/commit` skill. |
| CLI name | `_worktree` (underscore prefix) | Internal subcommand — skill invokes it, users don't. |

### Directory Layout: Sibling Container

**Implementation:** `../<repo>-wt/<slug>/` (sibling to project root)

**Rationale:** Claude CLI loads CLAUDE.md from all parent directories. Worktrees inside the project (`wt/<slug>/`) would inherit the main repo's CLAUDE.md, causing context pollution. Sibling containers isolate worktree sessions.

**Container detection:**
- If parent directory ends in `-wt`, already in container (use sibling)
- Otherwise create `<repo>-wt/` sibling directory

**Sandbox registration:** Both main and worktree register the container in `.claude/settings.local.json` under `permissions.additionalDirectories`

**No `.gitignore` entry needed:** Worktrees are outside the project root, so no gitignore entry required.

## CLI Specification

### _worktree new \<slug\> [--base HEAD] [--session \<path\>]

Creates a new worktree with optional pre-committed focused session.

**Flow:**
1. Validate: no existing sibling container worktree, no existing `<slug>` branch
2. **If `--session`:** Pre-commit session.md via git plumbing (uses temp index to avoid polluting main):
   - `GIT_INDEX_FILE=<tmpfile>` for all index operations below
   - `git hash-object -w <session-path>` → blob
   - `git read-tree --index-output=<tmpfile> <base>` (populate temp index from base)
   - `GIT_INDEX_FILE=<tmpfile> git update-index --cacheinfo 100644,<blob>,agents/session.md`
   - `GIT_INDEX_FILE=<tmpfile> git write-tree` → tree
   - `git commit-tree <tree> -p <base> -m "Focused session for <slug>"` → commit
   - `git branch <slug> <commit>`
   - `git worktree add <sibling-path> <slug>`
   - Clean up temp index file
3. **Else:** `git worktree add <sibling-path> -b <slug> <base>`
4. **Submodule via worktree:** `git -C agent-core worktree add <sibling-path>/agent-core <slug>`
   - Creates worktree of the submodule (shares object store with main submodule)
   - Bidirectional commit visibility (objects shared, not cloned)
5. Environment: `cd <sibling-path> && uv sync` (creates .venv)
6. Direnv: `cd <sibling-path> && direnv allow 2>/dev/null || true`

**Output (stdout):** `<sibling-container-path>/<slug>` (machine-readable path)
**Status (stderr):** Progress messages
**Exit:** 0 success, 1 error

**Note:** Steps 5-6 (uv sync, direnv) require network/filesystem access outside sandbox. The skill invokes these with `dangerouslyDisableSandbox: true`. The CLI itself doesn't manage sandbox — the caller does.

### _worktree rm \<slug\>

Removes worktree and branch.

**Flow:**
1. Check if sibling container worktree exists (worktree may already be removed, branch-only cleanup is valid)
2. If worktree exists:
   a. Check uncommitted changes — warn to stderr if dirty
   b. Remove submodule worktree first: `git -C agent-core worktree remove <sibling-path>/agent-core`
   c. Remove parent worktree: `git worktree remove --force <sibling-path>`
3. `git branch -d <slug>` — if unmerged, warn to stderr (don't force-delete)
4. Clean up empty container if no other worktrees remain

**Output:** Success message to stderr
**Exit:** 0 success, 1 error

### _worktree merge \<slug\> [--message \<text\>]

Combined submodule + parent merge. Idempotent — safe to re-run after conflict resolution.

See **Merge Flow** section below for full specification.

**Output (stdout):** Merge commit hash
**Output (stderr):** Progress messages
**Exit:** 0 success, 1 conflicts remain, 2 error

### _worktree ls

**Flow:** `git worktree list --porcelain` parsed into structured output.
**Output:** One line per worktree: `<slug>\t<branch>\t<path>`
**Exit:** 0 always

### _worktree clean-tree

Reports dirty state for parent repo + submodules, excluding session context files.

**Flow:**
1. `git status --porcelain` — filter out `agents/session.md`, `agents/jobs.md`, `agents/learnings.md`
2. `git -C agent-core status --porcelain` — same filter
3. If anything remains: print dirty files to stdout, exit 1
4. If clean: exit 0 silently

### _worktree add-commit \<files...\>

One-shot stage + commit utility. Commit message from stdin.

**Flow:**
1. `git add <files>`
2. Read message from stdin
3. `git diff --quiet --cached && exit 0` (nothing staged = no-op, idempotent)
4. `git commit -m <message>`

**Output (stdout):** Commit hash (or empty if no-op)
**Exit:** 0 success, 1 error

## Merge Flow

The `merge` subcommand orchestrates three phases. Each phase is idempotent — the merge can be interrupted and resumed.

### Phase 1: Pre-checks

1. Run clean-tree logic (same as `clean-tree` subcommand) — exit 1 if dirty
2. Validate branch `<slug>` exists: `git rev-parse --verify <slug>`
3. Validate worktree exists: check `wt/<slug>/` directory (warn if missing — branch-only merge still works)

### Phase 2: Submodule Resolution

**Goal:** Merge worktree's agent-core commits into local agent-core before parent merge.

1. Extract worktree's submodule commit: `git ls-tree <slug> -- agent-core` → `<wt-commit>`
2. Extract local submodule commit: `git -C agent-core rev-parse HEAD` → `<local-commit>`
3. If same commit: skip (no divergence)
4. Ancestry check: `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>`
   - If true: local already includes worktree's changes → skip
   - If false or error (commit not found locally): proceed to fetch + merge
5. Fetch: `git -C agent-core fetch wt/<slug>/agent-core HEAD`
   - Source path is worktree's submodule checkout: `wt/<slug>/agent-core`
   - Brings worktree-only commits into local object store
6. Merge: `git -C agent-core merge --no-edit <wt-commit>`
7. Stage: `git add agent-core`
8. Commit if staged: `git diff --quiet --cached || git commit -m "🔀 Merge agent-core from <slug>"`
9. **Post-verification:** Both `<wt-commit>` and `<local-commit>` must be ancestors of `git -C agent-core rev-parse HEAD`

**If merge conflicts in submodule:** Exit with message. User resolves in `agent-core/`, commits there, then re-runs `_worktree merge <slug>`.

### Phase 3: Parent Merge

1. `git merge --no-commit --no-ff <slug>`
   - `--no-commit`: allows custom merge commit message
   - `--no-ff`: ensures merge commit even if fast-forwardable (audit trail)
2. **If clean merge:** proceed to step 4 (commit)
3. **If conflicts:** identify and resolve:
   a. Get conflict list: `git diff --name-only --diff-filter=U`
   b. **agent-core conflicts:** `git checkout --ours agent-core && git add agent-core` (already merged in Phase 2)
   c. **Session context files:** Apply deterministic resolution (see Conflict Resolution)
   d. **Source code files:** Apply take-ours strategy (see Conflict Resolution)
   e. Check remaining: `git diff --name-only --diff-filter=U`
   f. If any remain: `git merge --abort`, clean debris, exit 1 with conflict list
4. Commit: `git commit -m "<merge-message>"`
   - Default message: `🔀 Merge wt/<slug>`
   - With `--message`: `🔀 <custom-text>`
5. **Post-merge precommit** (mandatory correctness gate):
   - Run `just precommit`
   - If fails: report which checks failed to stderr, exit 1
   - Precommit failure does NOT roll back the merge commit — user fixes and amends
6. Output merge commit hash to stdout

### Merge Debris Cleanup

After `git merge --abort`, check for untracked files materialized from source branch:
- `git clean -n` to list what would be removed
- `git clean -fd -- <affected-dirs>` to remove merge debris
- Only clean paths that didn't exist before the merge attempt

## Conflict Resolution

### Session Files (deterministic, FR-3)

Three files have deterministic resolution strategies. All logic lives in `conflicts.py`.

**session.md — keep-ours with task extraction:**

```python
def resolve_session_conflict(ours: str, theirs: str) -> str:
    """Keep ours as base, extract new tasks from theirs."""
```

Algorithm:
1. Parse task names from both sides: regex `^- \[ \] \*\*(.+?)\*\*` (with `re.MULTILINE`)
2. Compute new tasks: theirs_tasks - ours_tasks (set difference on task names)
3. For each new task: extract full task block (task line + any indented continuation lines)
4. If new tasks exist: append to ours's Pending Tasks section (before next `##` heading)
5. Remove merged worktree entry from Worktree Tasks section (match on slug)
6. Return merged content

**learnings.md — keep-both (append strategy):**

```python
def resolve_learnings_conflict(ours: str, theirs: str) -> str:
    """Keep ours, append new entries from theirs."""
```

Algorithm:
1. Parse learning entries from both sides (split on `## ` headings)
2. Identify entries in theirs not present in ours (match on `## Title` heading)
3. Append new entries from theirs to end of ours
4. Return merged content

Since learnings.md is append-only, theirs's additions are always at the end. This avoids fragile conflict marker parsing.

**jobs.md — keep-ours with status advancement:**

```python
def resolve_jobs_conflict(ours: str, theirs: str) -> str:
    """Keep ours, apply status advancements from theirs."""
```

Algorithm:
1. Parse both sides into plan→status maps (regex on table rows)
2. For each plan in theirs: if theirs-status > ours-status (ordering: requirements < designed < planned < complete), update ours
3. Return updated content

**Status ordering:** `requirements` < `designed` < `outlined` < `planned` < `complete`

**Note:** The canonical progression in `agents/jobs.md` lists four statuses (`requirements` -> `designed` -> `planned` -> `complete`). The `outlined` status exists in practice (e.g., worktree-skill) but is not in the canonical progression. This conflict resolution algorithm includes it for correctness. The planner should update `agents/jobs.md` to document `outlined` as a valid intermediate status.

**Application in merge flow:**
- `git show :2:<path>` → ours version (during merge conflict state)
- `git show :3:<path>` → theirs version
- Run resolution function
- Write result to working tree
- `git add <path>`

### Source Code (judgment-assisted, FR-4)

Non-session conflicts require judgment. Strategy is heuristic with precommit as correctness gate.

**Take-ours strategy:**
1. For each conflicted source file: `git checkout --ours <file> && git add <file>`
2. After all resolved: `just precommit`
3. If precommit passes: ours subsumes theirs (validated)
4. If precommit fails on specific files: try take-theirs for those files, re-run precommit
5. If neither passes alone: exit with conflict list for manual resolution

This is a CLI-level heuristic, not agent judgment. The precommit result is the oracle.

## Skill Design

### Location

`agent-core/skills/worktree/SKILL.md`

Symlinked to `.claude/skills/worktree/SKILL.md` via `just sync-to-parent`.

### Skill Requirements

**SR-1:** Handle three invocation modes: single-task (`wt <task>`), parallel group (`wt`), merge ceremony (`wt merge <slug>`)
**SR-2:** Derive slug from task name (deterministic, max 30 chars)
**SR-3:** Generate focused session.md content for worktree (task + relevant blockers + references)
**SR-4:** Manipulate session.md: move tasks between Pending Tasks and Worktree Tasks sections
**SR-5:** Orchestrate merge ceremony: handoff → commit → CLI merge → cleanup → session update
**SR-6:** Parallel group detection via prose analysis (no scripted detection)
**SR-7:** Communicate errors with resolution guidance (conflicts, precommit failures)
**SR-8:** Every step opens with a tool call (D+B hybrid pattern — prevents execution mode skipping)
**SR-9:** Follow imperative/infinitive writing style per plugin-dev:skill-development
**SR-10:** Progressive disclosure: core workflow in SKILL.md, detailed reference material in `references/`

### Frontmatter

```yaml
---
name: worktree
description: >-
  This skill should be used when the user asks to "create a worktree",
  "set up parallel work", "merge a worktree", "branch off a task",
  or uses the `wt` shortcut. Handles worktree lifecycle: creation with
  focused sessions, merge with ceremony, and parallel task setup.
allowed-tools: Read, Write, Edit, Bash(claudeutils _worktree:*), Bash(just precommit), Bash(git status:*), Bash(git worktree:*), Skill
user-invocable: true
continuation:
  cooperative: true
  default-exit: []
---
```

### Skill Body Structure

The skill has three modes matching execute-rule.md Mode 5:

**Mode A: Single-task worktree** (`wt <task-name>`)
1. Read session.md, find task by name
2. Derive slug: lowercase, replace spaces/special chars with hyphens, truncate to 30 chars
3. Generate focused session.md content (or invoke focus-session.py if available)
4. Write to `tmp/wt-<slug>-session.md`
5. Invoke: `claudeutils _worktree new <slug> --session tmp/wt-<slug>-session.md`
6. Edit session.md: move task from Pending Tasks to Worktree Tasks with `→ wt/<slug>` marker
7. Print launch command: `cd wt/<slug> && claude`

**Mode B: Parallel group** (`wt` with no args)
1. Read session.md + jobs.md
2. Identify parallel group (prose analysis — same logic as STATUS detection):
   - No shared plan directory
   - No logical dependency
   - Compatible model tier
   - No restart requirement
3. If no parallel group found (all tasks have dependencies): report "No independent parallel group detected" and stop
4. For each task in group: execute Mode A steps
5. Print all launch commands

**Mode C: Merge ceremony** (`wt merge <slug>`)
1. Invoke `/handoff --commit` (ceremony before merge — ensures clean tree)
2. Wait for commit to complete. If handoff or commit fails: stop and report (merge requires clean tree)
3. Invoke: `claudeutils _worktree merge <slug>`
4. If merge exit 0: edit session.md — remove task from Worktree Tasks
5. If merge exit 1 (conflicts or precommit failure): report guidance and stop (user resolves, re-runs)
6. Invoke: `claudeutils _worktree rm <slug>` (cleanup)
7. Print result

**Error communication:**
- Conflict resolution guidance (which files, what to do)
- Precommit failure guidance (which checks, how to fix)
- Never auto-resolve source conflicts — report and wait

### Slug Derivation

Pure function, implemented in CLI (`worktree/cli.py`):

```python
def derive_slug(task_name: str, max_length: int = 30) -> str:
    """Convert task name to worktree slug."""
    slug = re.sub(r'[^a-z0-9]+', '-', task_name.lower()).strip('-')
    return slug[:max_length].rstrip('-')
```

Exposed as utility but also used by skill directly (same logic, either location).

## Key Design Decisions

### D-1: Directory inside project root

`wt/<slug>/` instead of `../<repo>-<slug>/`. Eliminates sandbox bypass for most operations. Requires `.gitignore` entry. Git allows worktrees inside the main worktree when path is untracked.

### D-2: No branch prefix

Branches are `<slug>` not `wt/<slug>`. User requirement. Collision risk mitigated by validation on create. Tracking marker in session.md uses directory path `wt/<slug>` regardless.

### D-3: Merge uses --no-commit --no-ff

`--no-commit` enables custom merge message with `🔀` gitmoji. `--no-ff` ensures merge commit exists even for fast-forward cases (audit trail). Both are needed for consistent merge commit formatting.

### D-4: Precommit as correctness oracle

Post-merge `just precommit` validates the take-ours conflict resolution strategy. This is mechanical — precommit passes = merge correct, fails = needs manual resolution. Not agent judgment.

### D-5: CLI does git plumbing, skill does ceremony

CLI handles deterministic git operations. Skill handles session.md manipulation, handoff/commit ceremony, and user communication. Clean boundary: CLI is testable with real git repos, skill coordinates the workflow.

### D-6: Session conflict resolution extracts before resolving

Critical fix for FR-3: parse worktree-side Pending Tasks before `--ours` resolution. Prevents losing worktree-created tasks. Deterministic algorithm — match on task name, append new ones.

### D-7: Submodule merge before parent merge

Phase 2 (submodule) must complete before Phase 3 (parent). The parent merge will show agent-core as conflicted (different submodule pointers). By pre-merging the submodule, Phase 3 can safely `checkout --ours agent-core` knowing the local pointer is already correct.

### D-8: Idempotent merge

Each phase checks current state before acting. Phase 2 skips if submodule already merged. Phase 3 detects if merge is in progress (`git merge --abort` cleanup). Re-running after manual conflict resolution picks up where it left off.

### D-9: No plan-specific agent needed

The worktree skill doesn't need a `.claude/agents/` agent definition. The CLI subcommand is the implementation. The skill is the user interface. No sub-agents needed — all operations are direct tool calls.

### D-10: add-commit is idempotent

`add-commit` exits 0 with no output if nothing is staged after `git add`. Prevents "nothing to commit" errors in merge flow when submodule already committed.

## Testing Strategy

**Approach:** Integration-first with `tmp_path` creating real git repos + submodules.

**Shared fixtures** (in `conftest.py` or test file):
- `base_repo`: Git repo with initial commit, `.gitignore` with `wt/` entry
- `base_submodule`: Separate git repo serving as submodule origin
- `repo_with_submodule`: Base repo + submodule initialized, session.md + learnings.md + jobs.md present

Each test gets a fresh `git clone` of the fixture repos. This isolates tests without recreating repos.

**Mocking:** Only for error injection (lock files, permission errors, disk full). Never for behavior validation.

**Critical test scenarios (from outline):**

| Scenario | Module | Key Assertions |
|----------|--------|----------------|
| Submodule merge (diverged commits) | test_worktree_merge | Both original commits are ancestors of merged HEAD |
| Submodule merge (already included) | test_worktree_merge | Ancestry check detects local includes worktree changes, merge skipped |
| Session keep-ours + task extraction | test_worktree_conflicts | New tasks from worktree side present in result |
| Learnings keep-both | test_worktree_conflicts | All entries from both sides preserved |
| Jobs status advancement | test_worktree_conflicts | Higher status wins per ordering |
| Take-ours + precommit gate | test_worktree_merge | Precommit called, result determines success |
| Conflict resolution + resume | test_worktree_merge | Re-run after manual fix succeeds |
| Idempotent merge | test_worktree_merge | Running merge twice yields same result |
| New with --session pre-commit | test_worktree_cli | Worktree created with focused session.md at HEAD, main index unmodified |
| Clean-tree gate | test_worktree_cli | Dirty tree exits 1, session files exempt |
| Merge debris cleanup | test_worktree_merge | Untracked files from aborted merge removed |
| Task recovery from worktree session.md | test_worktree_conflicts | Tasks created during worktree work are preserved |

**Test file line limits:** Each test file stays under 400 lines. Split if exceeded.

## Documentation Updates

### execute-rule.md Mode 5

Update to reference `/worktree` skill instead of inline prose. Mode 5 triggers (`wt`, `wt <task-name>`) invoke the skill.

### .gitignore

Add `wt/` entry.

### Shortcut vocabulary (execute-rule.md)

`wt` entry already exists — update description to reference skill.

### sandbox-exemptions.md

Add worktree skill patterns. Note: most operations no longer need sandbox bypass with `wt/` inside project. Exception: `uv sync` and `direnv allow` in new worktrees.

### Handoff template

Worktree Tasks section format already documented — no changes needed.

### Justfile recipe deletion

Delete recipes: `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, `wt-merge`. Update `.cache/just-help.txt`.

## Dependencies

- **focus-session.py:** Currently missing. The skill needs focused session generation. Two options:
  1. Skill generates focused session content inline (Read session.md, extract task, Write focused file) — no dependency
  2. Implement focus-session.py as prerequisite task

  **Decision:** Option 1 for initial implementation. The focused session format is simple enough to generate inline. focus-session.py can be implemented later for richer extraction (plan context, reference files).

- **Continuation passing:** Already merged. Skill uses cooperative continuation with empty default-exit.

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/cli.md` — CLI patterns (Click, error output, entry points)
- `agents/decisions/testing.md` — TDD approach, behavioral verification, integration tests
- `plans/worktree-skill/outline.md` — Validated outline (binding scope)
- `plans/worktree-skill/reports/explore-integration.md` — Integration point analysis

**Skill creation guidance:**
- Load `plugin-dev:skill-development` before writing SKILL.md
- Load `plugin-dev:agent-development` if agent definition needed (D-9 says not needed)

**Context7 references:** None needed — all operations are git plumbing and Python Click.

**Additional research allowed:** Planner may explore existing test fixtures in `tests/conftest.py` for shared fixture patterns.

## Next Steps

1. `/plan-tdd plans/worktree-skill/design.md` — TDD runbook from this design
2. Load `plugin-dev:skill-development` before writing SKILL.md phase
3. Execution model: opus for SKILL.md authoring (workflow artifact), sonnet for CLI implementation, haiku for mechanical steps
