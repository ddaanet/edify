### Phase 1: Shared infrastructure (type: general, model: sonnet)

Extract git utilities and establish package structure. Foundation for all subcommands.

---

## Step 1.1: Extract git helpers to `claudeutils/git.py`

**Objective:** Move `_git()` and `_is_submodule_dirty()` from `worktree/git_ops.py` to new `claudeutils/git.py`, add `discover_submodules()`, `_git_ok()`, and `_fail()`. Update all import sites.

**Script Evaluation:** Medium (~60 lines new code + import updates across 5 files)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/worktree/git_ops.py:9-23` (current `_git()` implementation) and `src/claudeutils/worktree/git_ops.py:78-112` (current `_is_parent_dirty()` at lines 78-97 and `_is_submodule_dirty()` at lines 100-112 — submodule check hardcodes `"agent-core"`)

**Implementation:**

Create `src/claudeutils/git.py` containing:

1. **`_git(*args, check=True, env=None, input_data=None) -> str`** — moved verbatim from `worktree/git_ops.py:9-23`

2. **`_git_ok(*args) -> bool`** — uses `subprocess.run(["git", *args], check=False, capture_output=True)` and returns `True` if returncode == 0. Must use `subprocess.run` directly (not `_git()`) because `_git()` returns stdout string, not returncode.

3. **`_fail(msg: str, code: int = 1) -> Never`** — `click.echo(msg)` (stdout, not stderr — S-3 convention) then `raise SystemExit(code)`. Return type `Never` informs type checkers.

4. **`discover_submodules() -> list[str]`** — parse `git submodule status` output. Each line starts with space/+/- then commit hash then space then path. Extract path field. Return empty list if no submodules.

5. **`_is_submodule_dirty(path: str) -> bool`** — generalized from `_is_submodule_dirty()`. Accepts submodule path instead of hardcoded `"agent-core"`. Checks `Path(path).exists()` before querying.

6. **`_is_dirty(exclude_path: str | None = None) -> bool`** — moved from `worktree/git_ops.py:78-97` (`_is_parent_dirty`). Renamed to `_is_dirty` in the new module (no callers outside git_ops.py so no import update needed).

**Import updates** (verify scope with `grep -r "from claudeutils.worktree.git_ops import" src/`):
- `worktree/git_ops.py`: Remove `_git`, `_is_submodule_dirty`, `_is_parent_dirty` definitions. Import from `claudeutils.git` instead. Keep worktree-specific functions (`wt_path`, `_classify_branch`, etc.)
- `worktree/cli.py`: Update `from claudeutils.worktree.git_ops import _git, _is_submodule_dirty` → `from claudeutils.git import _git, _is_submodule_dirty`
- `worktree/merge.py`: Same import update pattern
- `worktree/merge_state.py`: Same import update pattern
- `worktree/resolve.py`: Same import update pattern
- `worktree/remerge.py`: Update `from claudeutils.worktree.git_ops import _git` → `from claudeutils.git import _git`

**Tests:** `tests/test_git_helpers.py`
- `test_git_ok_success`: `_git_ok("status")` returns True in a valid git repo
- `test_git_ok_failure`: `_git_ok("log", "--invalidflag")` returns False
- `test_fail_exits`: `_fail("error msg", code=2)` raises SystemExit(2), output contains "error msg"
- `test_discover_submodules_none`: In repo without submodules, returns `[]`
- `test_discover_submodules_present`: In repo with submodule, returns `["submod-name"]`
- `test_is_submodule_dirty_parametrized`: Tests with clean/dirty submodule, nonexistent path

**Expected Outcome:** `just precommit` passes. All existing tests pass (no broken imports). New tests pass.

**Error Conditions:**
- Import site missed → existing tests fail (caught by precommit)
- Function signature change → grep for all call sites before modifying

**Validation:** `just precommit` (runs full test suite + lint)

---

## Step 1.2: Create `claudeutils/session/` package structure

**Objective:** Create package skeleton for all three subcommands. Register `_session` group in main CLI.

**Script Evaluation:** Small (~30 lines, mostly `__init__.py` stubs)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/cli.py:145-152` — understand existing `cli.add_command(worktree)` registration pattern to replicate for `_session` group.

**Implementation:**

Create directory structure:
```
src/claudeutils/session/
  __init__.py           (empty)
  cli.py                Click group: `_session`
  handoff/
    __init__.py          (empty)
  commit/
    __init__.py          (empty)
  status/
    __init__.py          (empty)
```

`session/cli.py`:
- Define `@click.group(name="_session", hidden=True)` group
- Add help text: "Session management (internal)"

Main `cli.py` registration:
- `from claudeutils.session.cli import session_group`
- `cli.add_command(session_group)` — same pattern as line 152 (`cli.add_command(worktree)`)

**Expected Outcome:** `claudeutils _session --help` shows group with no subcommands. `claudeutils --help` does NOT show `_session` (hidden).

**Error Conditions:**
- Missing `__init__.py` → import failures

**Validation:** `claudeutils _session --help` succeeds; `just precommit` passes.

---

## Step 1.3: Add `claudeutils _git status` and `claudeutils _git diff` subcommands

**Objective:** Unified parent + submodule git status/diff view as structured markdown. Consumers: commit skill, commit CLI validation, handoff diagnostics.

**Script Evaluation:** Medium (~80 lines new code + tests)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/git.py` (Step 1.1 output) — uses `_git()` and `discover_submodules()`

**Implementation:**

Create `src/claudeutils/git_cli.py` (CLI commands for the `_git` group):
- `@click.group(name="_git", hidden=True)` group
- `@git_group.command(name="status")` — runs `git status --porcelain` for parent, then for each discovered submodule. Output format:

```markdown
## Parent
<git status --porcelain output or "(clean)">

## Submodule: agent-core
<git -C agent-core status --porcelain output or "(clean)">
```

- `@git_group.command(name="diff")` — same pattern with `git diff` (staged + unstaged). Output format:

```markdown
## Parent
<git diff output or "(no changes)">

## Submodule: agent-core
<git -C agent-core diff output or "(no changes)">
```

Register in main `cli.py`: `from claudeutils.git_cli import git_group` + `cli.add_command(git_group)`

**Tests:** `tests/test_git_cli.py`
- Tests use `tmp_path` to create real git repos with submodules
- `test_git_status_clean_repo`: CliRunner invokes `_git status`, output contains `## Parent` and `(clean)`
- `test_git_status_dirty_repo`: Create dirty file, output contains filename in parent section
- `test_git_status_with_submodule`: Create repo with submodule, output contains `## Submodule:` section
- `test_git_diff_with_changes`: Stage a change, verify diff output appears under correct section

**Expected Outcome:** `claudeutils _git status` and `claudeutils _git diff` produce structured markdown output. Exit 0 always (status is informational).

**Error Conditions:**
- Not in a git repo → `_git()` raises CalledProcessError. Let it propagate (informational command).

**Validation:** `just precommit` — all tests pass.

---

**Phase 1 Checkpoint:** `just precommit` — all existing tests pass, new infrastructure tests pass.
