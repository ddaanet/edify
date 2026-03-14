---
name: handoff-cli-tool
model: sonnet
---

# Session CLI Tool

**Context**: `claudeutils _handoff`, `_commit`, `_status` — mechanical CLI commands for handoff, commit, and status operations. Internal (underscore prefix, hidden from `--help`). Skills remain the user interface; CLI handles writes, validation, subprocess orchestration.
**Design**: `plans/handoff-cli-tool/outline.md`
**Status**: Ready
**Created**: 2026-03-07

---

## Weak Orchestrator Metadata

**Total Steps**: 26

**Execution Model**:
- Steps 1.1-1.3: Sonnet (infrastructure extraction, package setup, git CLI)
- Cycles 2.1-2.2: Sonnet (session.md parser)
- Cycles 3.1-3.4: Sonnet (status subcommand rendering + CLI wiring)
- Cycles 4.1-4.4, 4.6-4.7: Sonnet (handoff pipeline with state caching)
- Step 4.8: Opus (handoff skill precommit gate — agentic prose)
- Cycles 5.1-5.3: Sonnet (commit parser + vet check)
- Cycles 6.1-6.6: Sonnet (commit pipeline + submodule coordination)
- Cycle 7.1: Sonnet (integration tests)

**Step Dependencies**: Sequential within phases, phases sequential (2 depends on 1, 3 on 2, 4 on 2, 5 independent, 6 on 5, 7 on all)

**Error Escalation**:
- Sonnet → User: Architectural ambiguity, design gaps, test failures after 2 attempts

**Report Locations**: `plans/handoff-cli-tool/reports/`

**Success Criteria**: All three commands (`_status`, `_handoff`, `_commit`) functional with full test coverage. `just precommit` passes.

**Prerequisites**:
- `src/claudeutils/worktree/git_ops.py` exists with `_git()` function (verified via Glob)
- `src/claudeutils/cli.py` exists with `cli.add_command()` pattern (verified via Glob)
- `src/claudeutils/validation/task_parsing.py` exists with `ParsedTask` (verified via Glob)
- `src/claudeutils/worktree/session.py` exists with `extract_task_blocks()` (verified via Glob)

---

## Common Context

**Requirements (from design):**
- S-1: Package structure — `_handoff`, `_commit`, `_status` top-level commands registered individually in main cli.py via `cli.add_command()`
- S-2: `_git()` extraction — move from worktree to shared `claudeutils/git.py` with submodule discovery
- S-3: Output/error — all stdout, exit code carries signal, no stderr
- S-4: Session.md parser — shared parser extending existing `worktree/session.py`
- S-5: `_git changes` — unified parent + submodule status+diff in one call
- Handoff: stdin parsing, session.md writes, committed detection, state caching, diagnostics (git status/diff only — precommit is pre-handoff gate)
- Commit: stdin parsing, scripted vet check, submodule coordination, structured output
- Status: pure data transformation, session.md + filesystem → STATUS format

**Scope boundaries:**
- IN: `_handoff`, `_commit`, `_status` commands, `_git changes`, shared parser, git extraction, tests
- OUT: Gate A (LLM judgment), commit message drafting, gitmoji, skill modifications, pending task mutations

**Key Constraints:**
- All output to stdout as structured markdown — no stderr (S-3)
- Exit codes: 0=success, 1=pipeline error, 2=input validation
- `_fail()` pattern with `Never` return type for error termination
- CliRunner + real git repos via `tmp_path` for all tests
- Reuse existing `ParsedTask`, `extract_task_blocks()`, `find_section_bounds()` — do not duplicate

**Project Paths:**
- `src/claudeutils/worktree/git_ops.py`: Source of `_git()`, `_is_submodule_dirty()` for extraction
- `src/claudeutils/worktree/session.py`: Existing session.md parsing (TaskBlock, extract_task_blocks, find_section_bounds)
- `src/claudeutils/validation/task_parsing.py`: ParsedTask, parse_task_line, TASK_PATTERN
- `src/claudeutils/cli.py`: Main CLI with `cli.add_command()` registration pattern
- `src/claudeutils/exceptions.py`: Project exception hierarchy

**Stop/Error Conditions (all cycles):**
- RED fails to fail → STOP, diagnose test (assertion may be vacuous)
- GREEN passes without implementation → STOP, test too weak
- `just precommit` fails after GREEN → fix lint/test issues before proceeding
- Implementation needs architectural decision → STOP, escalate to user

**Dependencies (all cycles):**
- Phases are sequential: Phase N depends on Phase N-1 unless noted otherwise
- Phase 5 is independent of Phases 3-4 (commit parser has no dependency on status/handoff)
- Phase 6 depends on Phase 5 (commit pipeline uses commit parser + vet check)
- Phase 7 depends on Phases 3-4 (cross-subcommand contract test between status and handoff)

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

## Step 1.2: Create `claudeutils/session/` flat package structure

**Objective:** Create flat package with individual module files for all three commands. Register `_handoff`, `_commit`, `_status` as individual hidden commands in main CLI.

**Script Evaluation:** Small (~30 lines, mostly stubs)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/cli.py:145-152` — understand existing `cli.add_command(worktree)` registration pattern to replicate for individual session commands.

**Implementation:**

Create flat directory structure (no subdirectories):
```
src/claudeutils/session/
  __init__.py           (empty)
  cli.py                Individual Click commands: _handoff, _commit, _status
  parse.py              (placeholder — session.md parser, Phase 2)
  handoff.py            (placeholder — handoff pipeline, Phase 4)
  commit.py             (placeholder — commit parser + pipeline, Phases 5-6)
  commit_gate.py        (placeholder — scripted vet check, Phase 5)
  status.py             (placeholder — STATUS rendering, Phase 3)
```

`session/cli.py`:
- Define individual Click commands (stubs for now): `handoff_cmd`, `commit_cmd`, `status_cmd`
- Each command is a `@click.command()` with `hidden=True` — not a group

Main `cli.py` registration:
- `from claudeutils.session.cli import handoff_cmd, commit_cmd, status_cmd`
- `cli.add_command(handoff_cmd, "_handoff")` — same `cli.add_command()` pattern as worktree
- `cli.add_command(commit_cmd, "_commit")`
- `cli.add_command(status_cmd, "_status")`
- Each command registered with `hidden=True` so it does not appear in `--help`

**Expected Outcome:** `claudeutils _handoff --help`, `claudeutils _commit --help`, `claudeutils _status --help` all work. `claudeutils --help` does NOT show them (hidden).

**Error Conditions:**
- Missing `__init__.py` → import failures

**Validation:** `claudeutils _handoff --help` succeeds; `just precommit` passes.

---

## Step 1.3: Add `claudeutils _git changes` command

**Objective:** Unified parent + submodule view returning BOTH status AND diff in one call. Consumers: commit skill (input for `## Files` and `## Submodule`), handoff CLI (H-3 diagnostics).

**Script Evaluation:** Medium (~80 lines new code + tests)

**Execution Model:** Sonnet

**Prerequisite:** Read `src/claudeutils/git.py` (Step 1.1 output) — uses `_git()` and `discover_submodules()`

**Implementation:**

Create `src/claudeutils/git_cli.py` (CLI commands for the `_git` group):
- `@click.group(name="_git", hidden=True)` group
- `@git_group.command(name="changes")` — runs `git status --porcelain` AND `git diff` for parent, then for each discovered submodule. Output is a data transformation — paths are rewritten, not raw git passthrough. If tree is clean, output says so. If dirty, output includes both the file list AND the diff. Output format:

**Path prefixing:** Submodule file paths must be prefixed with submodule directory. `git -C agent-core status --porcelain` outputs relative paths — prefix each with `agent-core/`. This is a data transformation, not git passthrough.

**Clean sections omitted:** Only dirty repos shown in output. Token economy — only report deviations.

**Blank line separation:** Within a section, status and diff are separated by a blank line.

```markdown
## Parent
<git status --porcelain output>

<git diff output>
```

**Whole-tree clean:**
```markdown
Tree is clean.
```

When submodules present and dirty:
```markdown
## Parent
<status + diff>

## Submodule: agent-core
<status + diff (paths prefixed with agent-core/)>
```

Register in main `cli.py`: `from claudeutils.git_cli import git_group` + `cli.add_command(git_group)`

Internal Python functions (`git_status()`, `git_diff()` in `git.py`) serve commit CLI validation (C-2/C-3) separately from the unified CLI command.

**Tests:** `tests/test_git_cli.py`
- Tests use `tmp_path` to create real git repos with submodules
- `test_git_changes_clean_repo`: CliRunner invokes `_git changes`, output contains "clean"
- `test_git_changes_dirty_repo`: Create dirty file, output contains filename and diff under `## Parent`
- `test_git_changes_with_submodule`: Create repo with dirty submodule, output contains `## Submodule:` section with status and diff. Must verify submodule file paths include the submodule prefix (e.g., `agent-core/fragments/foo.md` not `fragments/foo.md`)
- `test_git_changes_clean_submodule_omitted`: Parent dirty + submodule clean → only parent section shown, no submodule section present in output

**Expected Outcome:** `claudeutils _git changes` produces structured markdown output with both status and diff. Exit 0 always (informational).

**Error Conditions:**
- Not in a git repo → `_git()` raises CalledProcessError. Let it propagate (informational command).

**Validation:** `just precommit` — all tests pass.

---

**Phase 1 Checkpoint:** `just precommit` — all existing tests pass, new infrastructure tests pass.

### Phase 2: Session.md parser (type: tdd, model: sonnet)

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

---

## Cycle 2.1: Parse all session.md sections with parametrized tests

**RED Phase:**

**Test:** `test_parse_session_sections[status_line]`, `test_parse_session_sections[completed]`, `test_parse_session_sections[in_tree_tasks]`, `test_parse_session_sections[worktree_tasks]`
**File:** `tests/test_session_parser.py`

**Assertions:**
- `parse_status_line(content)` returns the text between `# Session Handoff:` date line and first `## ` heading, stripped
- `parse_completed_section(content)` returns list of lines under `## Completed This Session` heading (up to next `## `)
- `parse_tasks(content, section="In-tree Tasks")` returns list of `ParsedTask` objects with `model`, `command`, `restart`, `worktree_marker` fields populated. Task with `→ slug` has `worktree_marker="slug"`. Task with `→ wt` has `worktree_marker="wt"`
- `parse_tasks(content, section="Worktree Tasks")` returns same structure for worktree section
- Each task has `plan_dir` attribute populated from continuation lines (`Plan:` or `plans/<name>/` in command)

**Edge case tests:**
- `test_parse_status_line_missing` — content without `# Session Handoff:` returns None
- `test_parse_tasks_old_format` — task line without pipe-separated metadata raises `SessionFileError` (mandatory metadata — no silent defaults)
- `test_parse_tasks_empty_section` — section heading present but no tasks returns `[]`
- `test_parse_completed_section_empty` — heading present, no content returns `[]`

**Fixture:** `SESSION_MD_FIXTURE` — realistic session.md with:
```markdown
# Session Handoff: 2026-03-07

**Status:** Phase 1 complete — infrastructure ready.

## Completed This Session

### Phase 1 infrastructure
- Extracted git helpers
- Created package structure

## In-tree Tasks

- [ ] **Build parser** — `/runbook plans/parser/design.md` | sonnet
  - Plan: parser | Status: outlined
- [ ] **Fix bug** — `just fix-bug` | haiku
- [x] **Done task** — `/commit` | sonnet

## Worktree Tasks

- [ ] **Parallel work** → `my-slug` — `/design plans/parallel/problem.md` | opus | restart
- [ ] **Future work** → `wt` — `/design plans/future/problem.md` | sonnet
```

**Expected failure:** `ImportError` or `AttributeError` — functions don't exist yet

**Why it fails:** No `session/parse.py` module with these functions

**Verify RED:** `pytest tests/test_session_parser.py -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/parse.py` with section parsing functions

**Behavior:**
- `parse_status_line(content: str) -> str | None` — find `# Session Handoff:` line, return text between it and first `## ` heading. Uses existing `find_section_bounds()` pattern from `worktree/session.py`
- `parse_completed_section(content: str) -> list[str]` — extract lines under `## Completed This Session` heading up to next `## ` or EOF
- `parse_tasks(content: str, section: str = "In-tree Tasks") -> list[ParsedTask]` — reuse `extract_task_blocks(content, section=section)` from `worktree/session.py` to get TaskBlocks, then call `parse_task_line()` from `validation/task_parsing.py` for each block's first line. Extend `ParsedTask` with `plan_dir` by calling existing `_extract_plan_from_block()` from `worktree/session.py`
- Section name parameter makes in-tree and worktree parsing identical — single function, different section argument

**Approach:** Compose existing functions rather than rewriting. Import `find_section_bounds`, `extract_task_blocks`, `_extract_plan_from_block` from `worktree/session.py` and `parse_task_line` from `validation/task_parsing.py`.

**Changes:**
- File: `src/claudeutils/session/parse.py`
  Action: Create with `parse_status_line`, `parse_completed_section`, `parse_tasks`
  Location hint: New file

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_parser.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 2.2: Full session.md parse — SessionData dataclass

**RED Phase:**

**Test:** `test_parse_session`, `test_parse_session_missing_file`, `test_parse_session_old_format`
**File:** `tests/test_session_parser.py`

**Assertions:**
- `parse_session(path)` returns `SessionData` with fields: `status_line: str | None`, `completed: list[str]`, `in_tree_tasks: list[ParsedTask]`, `worktree_tasks: list[ParsedTask]`, `date: str | None`
- All fields populated from the fixture session.md file
- `data.in_tree_tasks[0].name == "Build parser"` and `data.in_tree_tasks[0].plan_dir == "parser"`
- `data.worktree_tasks[0].worktree_marker == "my-slug"`
- `data.date` extracted from `# Session Handoff: 2026-03-07` → `"2026-03-07"`

**Error handling tests:**
- `test_parse_session_missing_file` — `parse_session(Path("nonexistent.md"))` raises `SessionFileError` (custom exception, not generic FileNotFoundError) — ST-2 fatal error
- `test_parse_session_old_format` — session.md with tasks lacking pipe-separated metadata → raises `SessionFileError` (exit 2). Mandatory metadata enforces plan-backed task rule — no silent defaults

**Expected failure:** `ImportError` — `SessionData` class doesn't exist

**Why it fails:** No `SessionData` dataclass or `parse_session()` function

**Verify RED:** `pytest tests/test_session_parser.py::test_parse_session -v`

---

**GREEN Phase:**

**Implementation:** Add `SessionData` dataclass and `parse_session()` to `session/parse.py`

**Behavior:**
- `SessionData` dataclass with typed fields for all sections
- `parse_session(path: Path) -> SessionData` — reads file, calls section parsers from Cycle 2.1, assembles into `SessionData`
- Missing file → raise `SessionFileError` (defined in `session/parse.py` or `claudeutils/exceptions.py`)
- Date extraction: parse from `# Session Handoff: YYYY-MM-DD` header line via regex

**Approach:** Thin orchestration function composing the section parsers.

**Changes:**
- File: `src/claudeutils/session/parse.py`
  Action: Add `SessionData` dataclass and `parse_session()` function
  Location hint: After section parser functions
- File: `src/claudeutils/exceptions.py` (if appropriate)
  Action: Add `SessionFileError(ClaudeUtilsError)` if exceptions are centralized there

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_parser.py -v`
**Verify no regression:** `just precommit`

---

**Phase 2 Checkpoint:** All parser tests pass, `just precommit` clean.

### Phase 3: Status subcommand (type: tdd, model: sonnet)

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

## Cycle 3.1: Render Next task

**RED Phase:**

**Test:** `test_render_next_task`, `test_render_next_skips_worktree_markers`, `test_render_next_no_pending`
**File:** `tests/test_session_status.py`

**Assertions:**
- `render_next(tasks)` where first task is pending (checkbox `" "`) with no `→` marker returns:
  ```
  Next: Build parser
    `/runbook plans/parser/design.md`
    Model: sonnet | Restart: no
  ```
- `render_next(tasks)` where first task has `worktree_marker="my-slug"` and second has `worktree_marker="wt"` and third is plain pending → returns third task's info
- `render_next([])` returns `""` (empty string, no Next section)
- Tasks with checkbox `"x"`, `"!"`, `"†"`, `"-"` are all skipped (only `" "` without marker is eligible)

**Expected failure:** `ImportError` — `render_next` doesn't exist

**Why it fails:** No `session/status.py` module

**Verify RED:** `pytest tests/test_session_status.py::test_render_next_task -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/status.py` with `render_next()`

**Behavior:**
- Iterate tasks, find first with `checkbox == " "` and `worktree_marker is None`
- If the next task is the first in-tree task (single-task case or next == first), suppress the separate `Next:` section. Instead, return a marker value (e.g., task index) so the caller merges Next metadata (command, model, restart) into the in-tree item with `▶` marker
- Otherwise, format as `Next:` block with command, model, restart
- Model defaults to "sonnet" if None. Restart shows "yes" if True, "no" if False

**Changes:**
- File: `src/claudeutils/session/status.py`
  Action: Create with `render_next(tasks: list[ParsedTask]) -> str`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.2: Render list sections with parametrized tests

**RED Phase:**

**Test:** `test_render_section[pending]`, `test_render_section[worktree]`, `test_render_section[unscheduled]`, `test_render_empty_section[pending]`, `test_render_empty_section[worktree]`, `test_render_empty_section[unscheduled]`
**File:** `tests/test_session_status.py`

**Assertions — In-tree section:**
- `render_pending(tasks, plan_states)` with two tasks returns:
  ```
  In-tree:
  ▶ Build parser (sonnet)
    `/runbook plans/parser/design.md`
    Plan: parser | Status: outlined
  - Fix bug (haiku)
  ```
- First pending task gets `▶` marker with command when Next is suppressed (single-task or first-in-tree case)
- Task with non-default model shows `(model)`. Default (sonnet) omitted
- Task with associated plan directory shows nested plan/status line
- Completed tasks (`checkbox == "x"`) excluded

**Assertions — Worktree section:**
- `render_worktree(tasks)` with branched task returns:
  ```
  Worktree:
  - Parallel work → my-slug
  - Future work → wt
  ```
- `→ slug` for branched tasks, `→ wt` for destined-but-not-yet-branched

**Assertions — Unscheduled Plans section:**
- `render_unscheduled(all_plans, task_plan_dirs)` with plans not associated to any task returns:
  ```
  Unscheduled Plans:
  - orphan-plan — designed
  ```
- Plans with status `delivered` excluded
- Sorted alphabetically
- Plans associated to any pending task excluded

**Empty section assertions (all three):**
- Each render function returns `""` when input list is empty

**Additional test:** `test_render_session_continuation`
**Assertions:**
- `render_session_continuation(is_dirty=True, review_pending_plans=[])` returns `Session: uncommitted changes — \`/handoff\`, \`/commit\``
- `render_session_continuation(is_dirty=True, review_pending_plans=["foo"])` returns `Session: uncommitted changes — \`/handoff\`, \`/commit\`, \`/deliverable-review plans/foo\``
- `render_session_continuation(is_dirty=False, review_pending_plans=[])` returns `""` (omit entirely when clean)

**Expected failure:** `ImportError` — render functions don't exist

**Why it fails:** No rendering functions for these sections

**Verify RED:** `pytest tests/test_session_status.py -k "render_section or render_empty or render_session" -v`

---

**GREEN Phase:**

**Implementation:** Add `render_pending()`, `render_worktree()`, `render_unscheduled()`, `render_session_continuation()` to `session/status.py`

**Behavior:**
- `render_pending(tasks, plan_states, next_task_idx)`: Filter to pending tasks (checkbox `" "`), format with optional plan status. First pending task gets `▶` marker and merged Next metadata when `next_task_idx` indicates suppression. Non-default model shown in parens. Plan status from `plan_states` dict mapping plan name → status string
- `render_worktree(tasks)`: Format worktree tasks with `→` markers
- `render_unscheduled(all_plans, task_plan_dirs)`: Filter plans not in `task_plan_dirs` set, exclude `delivered`, sort alphabetically, format with `—` separator
- `render_session_continuation(is_dirty, review_pending_plans)`: When dirty, render `Session: uncommitted changes — /handoff, /commit` header. If any review-pending plans, append `/deliverable-review plans/<name>`. Omit when clean
- All output uses ANSI colors for status section headers

**Approach:** Each function produces a section string or empty string. Caller concatenates non-empty sections.

**Changes:**
- File: `src/claudeutils/session/status.py`
  Action: Add rendering functions including session continuation

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.3: Parallel group detection

**Note: Design revision pending.** ST-1 "largest independent group" selection replaced with "first eligible consecutive group" (document order, cap 5). The "top priority unblocked items" change primarily affects the cap and consecutive constraint retention — both are implemented here. Outline update required before orchestration to align wording.

**RED Phase:**

**Test:** `test_detect_parallel_group`, `test_detect_parallel_no_group`, `test_detect_parallel_shared_plan`
**File:** `tests/test_session_status.py`

**Assertions:**
- `detect_parallel(tasks, blockers)` with 3 consecutive tasks having different `plan_dir` values and no blockers returns group of all 3 task names
- `detect_parallel(tasks, blockers)` with single task returns `None` (no group)
- `detect_parallel(tasks, blockers)` with 2 tasks sharing `plan_dir="parser"` returns `None` (shared plan = dependent)
- `detect_parallel(tasks, blockers)` with tasks where a dependency breaks consecutive run → returns first eligible consecutive group (before the break)
- `detect_parallel(tasks, blockers)` with 7 consecutive independent tasks → returns first 5 (cap at 5 concurrent sessions)
- Blocker text mentioning task name creates dependency (breaks consecutive run)

**Expected failure:** `ImportError` — `detect_parallel` doesn't exist

**Why it fails:** No parallel detection function

**Verify RED:** `pytest tests/test_session_status.py::test_detect_parallel_group -v`

---

**GREEN Phase:**

**Implementation:** Add `detect_parallel()` to `session/status.py`

**Behavior:**
- `detect_parallel(tasks: list[ParsedTask], blockers: list[list[str]]) -> list[str] | None`
- Only consecutive independent tasks form a group (not arbitrary subsets)
- Walk tasks in document order, building a consecutive run of independent tasks. A task is dependent if it shares `plan_dir` with any task in the current run, or is mentioned in blocker text
- A dependency breaks the consecutive run — start a new run
- First eligible group in document order (2+ consecutive independent tasks)
- Cap at 5 concurrent sessions
- Return task names if group has 2+ members, else None

**Approach:** Linear scan — iterate tasks, extend current consecutive group while independent. On dependency, check if current group qualifies (2+), return it. If not, reset and continue. Cap group size at 5.

**Changes:**
- File: `src/claudeutils/session/status.py`
  Action: Add `detect_parallel()` function

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.4: CLI wiring — `claudeutils _status`

**RED Phase:**

**Test:** `test_status_cli`, `test_status_missing_session`, `test_status_old_format_fatal`
**File:** `tests/test_session_status.py`

**Assertions:**
- CliRunner invoking `_status` with a real session.md file in cwd produces output containing:
  - In-tree section with first pending task (with `▶` marker if single-task)
  - Output exits with code 0
- CliRunner invoking `_status` without session.md file → exit code 2, output contains `**Error:**`
- CliRunner invoking `_status` with session.md containing tasks without pipe-separated metadata → exit code 2 (old format = fatal, mandatory metadata)

**Expected failure:** Command `_status` not registered — Click returns non-zero with "No such command"

**Why it fails:** No `_status` command registered in main CLI

**Verify RED:** `pytest tests/test_session_status.py::test_status_cli -v`

---

**GREEN Phase:**

**Implementation:** Wire the `status_cmd` Click command in `src/claudeutils/session/cli.py`, already registered in main `cli.py` from Step 1.2

**Behavior:**
- `status_cmd` Click command implementation
- Read `agents/session.md` (cwd-relative) → `parse_session()`
- Call `claudeutils _worktree ls` via subprocess for plan states
- Parse `_worktree ls` output for plan status: lines matching `  Plan: {name} [{status}] → ...` — extract name and status into a dict `{name: status}` passed to `render_pending()`
- Check git tree dirty state for session continuation header
- Check plan states for any `review-pending` plans
- Call render functions (session continuation, Next/merged, Pending, Worktree, Unscheduled, Parallel)
- Concatenate non-empty sections with blank line separators, ANSI-colored output
- Output to stdout, exit 0
- Missing session.md → `_fail("**Error:** Session file not found: agents/session.md", code=2)`
- Old format (missing metadata) → exit 2 (fatal, propagated from parser)

**Changes:**
- File: `src/claudeutils/session/cli.py`
  Action: Implement `status_cmd` with full pipeline
  Location hint: Status command stub from Step 1.2

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

**Phase 3 Checkpoint:** `just precommit` — status subcommand fully functional.

### Phase 4: Handoff pipeline (type: tdd, model: sonnet)

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

## Cycle 4.1: Parse handoff stdin

**RED Phase:**

**Test:** `test_parse_handoff_input`, `test_parse_handoff_missing_status`, `test_parse_handoff_missing_completed`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `parse_handoff_input(text)` with valid input returns `HandoffInput` with:
  - `status_line == "Design Phase A complete — outline reviewed."`
  - `completed_lines` is list of strings under `## Completed This Session`
- `parse_handoff_input(text)` without `**Status:**` line raises `HandoffInputError` with message containing "Status"
- `parse_handoff_input(text)` without `## Completed This Session` heading raises `HandoffInputError` with message containing "Completed"

**Input fixture:**
```
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

### Handoff CLI tool design (Phase A)
- Produced outline
- Review by outline-review-agent
```

**Expected failure:** `ImportError` — no `parse_handoff_input` function

**Why it fails:** No `session/handoff.py` module with parsing

**Verify RED:** `pytest tests/test_session_handoff.py::test_parse_handoff_input -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/handoff.py`

**Behavior:**
- `HandoffInput` dataclass: `status_line: str`, `completed_lines: list[str]`
- `parse_handoff_input(text: str) -> HandoffInput` — locate `**Status:**` line, extract text after marker. Locate `## Completed This Session` heading, extract all lines until next `## ` or EOF
- `HandoffInputError` exception for missing required markers

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Create with `HandoffInput`, `HandoffInputError`, `parse_handoff_input()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.2: Status line overwrite in session.md

**RED Phase:**

**Test:** `test_overwrite_status_line`, `test_overwrite_status_line_multiline`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `overwrite_status(session_path, "New status text.")` modifies file: line after `# Session Handoff:` heading becomes `**Status:** New status text.`
- Subsequent call with different text overwrites again (not append)
- Other sections of session.md unchanged
- When status text has multiple lines, each line preserved between heading and first `##`

**Expected failure:** `AttributeError` — `overwrite_status` doesn't exist

**Why it fails:** No status overwrite function

**Verify RED:** `pytest tests/test_session_handoff.py::test_overwrite_status_line -v`

---

**GREEN Phase:**

**Implementation:** Add `overwrite_status()` to `src/claudeutils/session/handoff.py`

**Behavior:**
- Read session.md, find line after `# Session Handoff:` and before first `## ` heading
- Replace that region with `**Status:** {new_text}\n`
- Preserve blank line between status and first `##`
- Write back to file

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Add `overwrite_status(session_path: Path, status_text: str) -> None`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.3: Completed section write with committed detection (H-2)

**RED Phase:**

**Test:** `test_write_completed_overwrite`, `test_write_completed_append`, `test_write_completed_auto_strip`
**File:** `tests/test_session_handoff.py`

Tests use real git repos via `tmp_path` — committed detection requires `git diff HEAD`. Fixture must have a committed `agents/session.md` with an existing `## Completed This Session` section so that diff modes can be distinguished.

**Assertions — overwrite mode (no prior diff):**
- First handoff or prior content already committed → `write_completed(session_path, new_lines)` overwrites `## Completed This Session` section entirely with `new_lines`; section contains exactly `new_lines` and no prior content

**Assertions — append mode (old removed by agent):**
- Agent cleared old completed content from working tree, new additions provided → `write_completed()` writes only `new_lines` to section (prior committed lines NOT restored); resulting section contains exactly `new_lines`

**Assertions — auto-strip mode (old preserved with additions):**
- Prior committed content still present + new additions → `write_completed()` strips content that matches HEAD version, keeps only new additions

**Detection mechanism:**
- `git diff HEAD -- agents/session.md` extracts completed section from both sides
- If no diff in completed section region → overwrite
- If diff shows old lines removed → append
- If diff shows old lines preserved + new lines → auto-strip committed

**Expected failure:** Function doesn't exist

**Why it fails:** No committed detection logic

**Verify RED:** `pytest tests/test_session_handoff.py::test_write_completed_overwrite -v`

---

**GREEN Phase:**

**Implementation:** Add `write_completed()` to `session/handoff.py`

**Behavior:**
- Compare completed section in working tree vs HEAD via `git diff HEAD -- agents/session.md`
- Parse diff to determine which mode applies
- Execute appropriate write (overwrite, append, or strip-committed-then-keep-new)

**Approach:** Use `_git("diff", "HEAD", "--", str(session_path))` to get diff. Parse for completed section hunk. Absence of hunk → overwrite mode. Hunk with only additions → append mode. Hunk with preserved old + new → auto-strip mode.

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Add `write_completed(session_path: Path, new_lines: list[str]) -> None`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.4: State caching (H-4)

**RED Phase:**

**Test:** `test_state_cache_create`, `test_state_cache_resume`, `test_state_cache_cleanup`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `save_state(input_md, step="write_session")` creates `tmp/.handoff-state.json` with `input_markdown`, `timestamp` (ISO format), `step_reached` fields
- `load_state()` returns `HandoffState` with same fields, or `None` if no state file
- `clear_state()` removes the state file
- `step_reached` values: `"write_session"`, `"diagnostics"`
- State file survives across function calls (not deleted on load)

**Expected failure:** `ImportError` — state caching functions don't exist

**Why it fails:** No state management module

**Verify RED:** `pytest tests/test_session_handoff.py::test_state_cache_create -v`

---

**GREEN Phase:**

**Implementation:** Add state caching to `src/claudeutils/session/handoff.py`

**Behavior:**
- `HandoffState` dataclass: `input_markdown: str`, `timestamp: str`, `step_reached: str`
- `save_state(input_md: str, step: str) -> None` — write JSON to `tmp/.handoff-state.json`. Create `tmp/` if needed
- `load_state() -> HandoffState | None` — read and parse JSON, return None if file missing
- `clear_state() -> None` — delete state file if exists

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Add `HandoffState`, `save_state()`, `load_state()`, `clear_state()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

**Mid-phase checkpoint:** `just precommit` — mutations + recovery established before diagnostics integration.

---

## Cycle 4.6: Diagnostic output (H-3)

**RED Phase:**

**Test:** `test_diagnostics_output`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `format_diagnostics(git_output)` returns structured markdown containing the git status/diff output
- `format_diagnostics("")` with empty git output returns empty string (nothing to report)

**Expected failure:** `ImportError`

**Why it fails:** No diagnostics formatting function

**Verify RED:** `pytest tests/test_session_handoff.py::test_diagnostics_output -v`

---

**GREEN Phase:**

**Implementation:** Add `format_diagnostics()` to `session/handoff.py`

**Behavior:**
- `format_diagnostics(git_output: str) -> str`
- If git output non-empty: return it as structured markdown
- If empty: return empty string
- No precommit result (precommit is pre-handoff gate, not CLI responsibility)
- No learnings age/weight (SessionStart hook concern, not actionable mid-session)

**Changes:**
- File: `src/claudeutils/session/handoff.py`
  Action: Add `format_diagnostics()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.7: CLI wiring — `claudeutils _handoff`

**RED Phase:**

**Test:** `test_handoff_cli_fresh`, `test_handoff_cli_resume`, `test_handoff_cli_no_stdin_no_state`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- CliRunner invoking `_handoff` with stdin input → exit 0, session.md status line updated, completed section written, diagnostics output
- CliRunner invoking `_handoff` without stdin but with existing state file → exit 0, resumes from `step_reached`
- CliRunner invoking `_handoff` without stdin and no state file → exit 2, output contains error message about missing input

**Expected failure:** Command not registered

**Why it fails:** No `_handoff` command implementation

**Verify RED:** `pytest tests/test_session_handoff.py::test_handoff_cli_fresh -v`

---

**GREEN Phase:**

**Implementation:** Wire the `handoff_cmd` Click command in `src/claudeutils/session/cli.py`, already registered in main `cli.py` from Step 1.2

**Behavior:**
- `handoff_cmd` Click command implementation
- Read stdin (if available) → `parse_handoff_input()`
- If no stdin: check for state file → `load_state()` → resume
- If no stdin and no state: `_fail("**Error:** No input on stdin and no state file", code=2)`
- Fresh pipeline: parse → save_state → overwrite_status → write_completed → diagnostics (git status/diff via _git changes) → clear_state
- Resume: load state → skip to `step_reached` → continue pipeline

**Changes:**
- File: `src/claudeutils/session/cli.py`
  Action: Implement `handoff_cmd` with full pipeline
  Location hint: Handoff command stub from Step 1.2

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Step 4.8: Update handoff skill — add pre-handoff precommit gate

**Objective:** Add `just precommit` as a gate in the handoff skill (`agent-core/skills/handoff/SKILL.md`). The handoff CLI no longer runs precommit (removed from pipeline); the skill must run it before STATUS display. Without this update, precommit validation drops out of the handoff flow entirely.

**Script Evaluation:** Small (~10 lines skill edit)

**Execution Model:** Opus (agentic prose — skill file, wording determines downstream agent behavior)

**Actions:**
1. Read `agent-core/skills/handoff/SKILL.md`
2. Add a precommit gate step after all writes (session.md, learnings, plan-archive, trim) and before Step 7 (Display STATUS):
   - Run `just precommit`
   - On failure: output precommit result, stop (agent fixes issues and retries)
   - On success: continue to STATUS display
3. Verify the step integrates coherently with the existing protocol flow — precommit validates all writes made during handoff (session.md, learnings.md, plan-archive.md)

**Changes:**
- File: `agent-core/skills/handoff/SKILL.md`
  Action: Add precommit gate step between current Step 6 (Trim Completed Tasks) and Step 7 (Display STATUS)

**Expected Outcome:** Handoff skill runs `just precommit` after all writes and before STATUS display. Failed precommit surfaces output and stops the flow so agent can fix issues. Passing precommit proceeds to STATUS display unchanged.

**Validation:** Read modified skill, verify precommit gate is positioned after all writes and before STATUS display.

---

**Phase 4 Checkpoint:** `just precommit` — handoff subcommand and skill precommit gate complete.

### Phase 5: Commit parser + vet check (type: tdd, model: sonnet)

Markdown stdin parser (commit-specific format) and scripted vet check.

---

## Cycle 5.1: Parse commit markdown stdin — all sections with parametrized tests

**RED Phase:**

**Test:** `test_parse_commit_input[files]`, `test_parse_commit_input[options]`, `test_parse_commit_input[submodule]`, `test_parse_commit_input[message]`, `test_parse_commit_input_edge_cases`
**File:** `tests/test_session_commit.py`

**Input fixture:**
```markdown
## Files
- src/commit/cli.py
- src/commit/gate.py
- agent-core/fragments/vet-requirement.md

## Options
- no-vet
- amend

## Submodule agent-core
> 🤖 Update vet-requirement fragment
>
> - Add scripted gate classification reference

## Message
> ✨ Add commit CLI with scripted vet check
>
> - Structured markdown I/O
> - Submodule-aware commit pipeline
```

**Assertions — Files:**
- `result.files == ["src/commit/cli.py", "src/commit/gate.py", "agent-core/fragments/vet-requirement.md"]`

**Assertions — Options:**
- `result.options == {"no-vet", "amend"}`
- Input with unknown option `"foobar"` raises `CommitInputError` with message containing "Unknown option"
- Input without `## Options` → `result.options == set()`

**Assertions — Submodule:**
- `result.submodules` is dict mapping path → message: `{"agent-core": "🤖 Update vet-requirement fragment\n\n- Add scripted gate classification reference"}`
- Multiple `## Submodule <path>` sections each parsed independently
- Blockquote `> ` prefix stripped from message lines

**Assertions — Message:**
- `result.message == "✨ Add commit CLI with scripted vet check\n\n- Structured markdown I/O\n- Submodule-aware commit pipeline"`
- Blockquote `> ` prefix stripped
- `## ` lines within blockquote treated as message body (not section boundaries)
- Missing `## Message` → `CommitInputError` (unless `amend` + `no-edit` in Options)
- Missing `## Files` → `CommitInputError`
- `no-edit` in Options without `amend` → `CommitInputError` with message indicating `no-edit` requires `amend`
- `amend` + `no-edit` without `## Message` → valid (message not required)
- `no-edit` with `## Message` present → `CommitInputError` (contradictory input — no-edit means keep existing message)

**Expected failure:** `ImportError` — no commit parser module

**Why it fails:** No `session/commit.py`

**Verify RED:** `pytest tests/test_session_commit.py -k "parse_commit" -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit.py`

**Behavior:**
- `CommitInput` dataclass: `files: list[str]`, `options: set[str]`, `submodules: dict[str, str]`, `message: str | None`
- `parse_commit_input(text: str) -> CommitInput` — section-based parsing
- Split on `## ` at line start. Known section names: `Files`, `Options`, `Submodule <path>`, `Message`
- `## Message` is always last — everything from `## Message` to EOF is message body
- Blockquote stripping: remove leading `> ` or `>` from each line
- Valid options: `no-vet`, `just-lint`, `amend`, `no-edit`. Unknown → raise `CommitInputError`
- `no-edit` without `amend` → raise `CommitInputError` (exit 2 — `no-edit` requires `amend`)
- When `amend` + `no-edit`: `## Message` section not required in input, `message` is `None`
- `CommitInputError` exception for missing required sections or unknown options

**Approach:** Sequential parsing — find each `## ` boundary, classify section, delegate to section-specific parser. Message section greedily consumes to EOF (safe for `## ` in blockquotes).

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Create with `CommitInput`, `CommitInputError`, `parse_commit_input()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 5.2: Input validation — clean files check (C-3)

**RED Phase:**

**Test:** `test_validate_files_dirty`, `test_validate_files_clean_error`, `test_validate_files_amend`
**File:** `tests/test_session_commit.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `validate_files(files, amend=False)` with all files appearing in `git status --porcelain` → returns normally (no error)
- `validate_files(files, amend=False)` with a clean file (not in `git status --porcelain`) → raises `CleanFileError` with:
  - `clean_files` attribute listing the clean file paths
  - String representation matching exact format: `**Error:** Listed files have no uncommitted changes\n- <path>\n\nSTOP: Do not remove files and retry.`
- `validate_files(files, amend=True)` with a file that's clean in working tree but present in HEAD commit (via `git diff-tree`) → returns normally (amend allows HEAD-committed files)
- `validate_files(files, amend=True)` with a file in neither working tree changes nor HEAD commit → raises `CleanFileError`

**Expected failure:** `ImportError`

**Why it fails:** No validation function

**Verify RED:** `pytest tests/test_session_commit.py::test_validate_files_dirty -v`

---

**GREEN Phase:**

**Implementation:** Add `validate_files()` to `src/claudeutils/session/commit_gate.py`

**Behavior:**
- `CleanFileError` exception with `clean_files: list[str]` attribute
- `validate_files(files: list[str], amend: bool = False) -> None`
- Get dirty files: `_git("status", "--porcelain")` → parse paths (column 3+)
- If amend: also get HEAD files: `_git("diff-tree", "--no-commit-id", "--name-only", "HEAD")`
- For each file in `files`: check presence in dirty set (or HEAD set if amend)
- Collect clean files → raise `CleanFileError` with STOP directive

**Changes:**
- File: `src/claudeutils/session/commit_gate.py`
  Action: Create with `CleanFileError`, `validate_files()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 5.3: Scripted vet check (C-1)

**RED Phase:**

**Test:** `test_vet_check_no_config`, `test_vet_check_pass`, `test_vet_check_unreviewed`, `test_vet_check_stale`
**File:** `tests/test_session_commit.py`

Tests use `tmp_path` with pyproject.toml and plan report directories.

**Assertions:**
- `vet_check(files)` with no `[tool.claudeutils.commit]` section in pyproject.toml → passes (opt-in, returns `VetResult(passed=True)`)
- `vet_check(files)` with `require-review = ["src/**/*.py"]` and file `src/foo.py` in files, with report `plans/bar/reports/vet-review.md` newer than `src/foo.py` → passes
- `vet_check(files)` with matching pattern but no report file → fails with `VetResult(passed=False, reason="unreviewed", unreviewed_files=["src/foo.py"])`
- `vet_check(files)` with report older than newest matching file → fails with `VetResult(passed=False, reason="stale", stale_info=...)`
- Files not matching any pattern are not checked (non-production files pass freely)

**Expected failure:** `ImportError`

**Why it fails:** No vet check function

**Verify RED:** `pytest tests/test_session_commit.py::test_vet_check_no_config -v`

---

**GREEN Phase:**

**Implementation:** Add vet check to `src/claudeutils/session/commit_gate.py`

**Behavior:**
- `VetResult` dataclass: `passed: bool`, `reason: str | None`, `unreviewed_files: list[str]`, `stale_info: str | None`
- `vet_check(files: list[str]) -> VetResult`
- Read `pyproject.toml` (cwd-relative), parse `[tool.claudeutils.commit].require-review` patterns
- No section or no patterns → return `VetResult(passed=True)`
- Match files against patterns using `fnmatch` or `pathlib.PurePath.match`
- For matched files: discover reports in `plans/*/reports/` matching `*vet*` or `*review*` (excluding `tmp/`)
- No reports → unreviewed. Reports exist → check freshness: `mtime` of newest production file vs newest report
- Stale (production newer) → fail with stale info

**Changes:**
- File: `src/claudeutils/session/commit_gate.py`
  Action: Add `VetResult`, `vet_check()`
  Note: Hardcode `agent-core/bin/**`, `agent-core/skills/**/*.sh` patterns (not configurable). Config model for submodule patterns (unified parent config vs per-repo pyproject.toml) deferred to separate plan.

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

**Phase 5 Checkpoint:** `just precommit` — parser and vet check tests pass.

### Phase 6: Commit pipeline + output (type: tdd, model: sonnet)

Staging, submodule coordination, amend semantics, structured output.

---

## Cycle 6.1: Parent-only commit pipeline

**RED Phase:**

**Test:** `test_commit_parent_only`, `test_commit_precommit_failure`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `commit_pipeline(commit_input)` with files in parent repo only (no submodule files), precommit passing:
  - Stages listed files via `git add`
  - Runs `just precommit`
  - Commits with message from `CommitInput.message`
  - Returns `CommitResult(success=True, output="[branch hash] message\n N files changed...")` — raw git output
  - Exit code 0
- `commit_pipeline(commit_input)` with precommit failure:
  - Returns `CommitResult(success=False, output="**Precommit:** failed\n\n<error output>")`
  - Files staged but NOT committed
  - Exit code 1

**Expected failure:** `ImportError` — no commit pipeline

**Why it fails:** No commit pipeline in `session/commit.py`

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_parent_only -v`

---

**GREEN Phase:**

**Implementation:** Add commit pipeline to `src/claudeutils/session/commit.py`

**Behavior:**
- `CommitResult` dataclass: `success: bool`, `output: str`
- `commit_pipeline(input: CommitInput) -> CommitResult`
- Stage files via `git add`
- Run `just precommit` (validation level dispatch added in Cycle 6.4)
- Run vet check via `vet_check(input.files)` (option-gating added in Cycle 6.4)
- Commit with message from `CommitInput.message`
- Return raw git commit output on success

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Add `CommitResult`, `commit_pipeline()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.2: Submodule coordination (C-2)

**RED Phase:**

**Test:** `test_commit_with_submodule`, `test_commit_submodule_no_message`, `test_commit_submodule_orphan_message`, `test_commit_no_submodule_changes`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos with submodules via `tmp_path` (shared fixture).

**Assertions — four-cell matrix from C-2:**

| Submodule files in Files | `## Submodule` present | Expected |
|---|---|---|
| Yes | Yes | Submodule committed first, pointer staged, parent committed. Output has `<path>:` prefix for submodule |
| Yes | No | `CommitResult(success=False)`, output contains `**Error:**` about missing submodule message. Exit 1 |
| No | Yes | `CommitResult(success=True)`, output contains `**Warning:**` about orphaned submodule message. Warning prepended to git output |
| No | No | Parent-only commit (same as 6.1) |

**Submodule commit sequence:**
- Files partitioned by submodule path prefix
- Per-submodule: `git -C <path> add <files>` → `git -C <path> commit -m <submodule_message>`
- Stage submodule pointer: `git add <path>`
- Parent commit includes pointer change

**Expected failure:** Pipeline doesn't handle submodule files

**Why it fails:** No submodule partitioning or coordination logic

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_with_submodule -v`

---

**GREEN Phase:**

**Implementation:** Add submodule coordination to `commit_pipeline()`

**Behavior:**
- Partition `input.files` by submodule path prefix (using `discover_submodules()`)
- For each submodule with files:
  - Check `input.submodules` has message for this path → error if missing
  - Stage submodule files: `_git("-C", path, "add", *submod_files)`
  - Commit submodule: `_git("-C", path, "commit", "-m", submod_message)`
  - Stage pointer: `_git("add", path)`
- For orphaned submodule messages (path in `input.submodules` but no files): emit warning
- Commit parent with remaining files + staged pointers
- Output: submodule output prefixed with `<path>:`, parent output unlabeled

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Add submodule partitioning and coordination to `commit_pipeline()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.3: Amend semantics (C-5)

**RED Phase:**

**Test:** `test_commit_amend_parent`, `test_commit_amend_submodule`, `test_commit_amend_validation`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `commit_pipeline(input)` with `amend` in options:
  - Passes `--amend` to `git commit`
  - Output shows amend format with `Date:` line
  - Message is the full provided message (no `--no-edit`)
- Amend with submodule files:
  - Submodule amended first → pointer re-staged → parent amended
  - Output labeled correctly
- Amend validation:
  - File present in HEAD commit but not in working tree changes → valid for amend (no error)
  - File in neither HEAD nor working tree → `CleanFileError` (same as non-amend)

**Expected failure:** Pipeline doesn't pass `--amend` flag

**Why it fails:** No amend support in pipeline

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_amend_parent -v`

---

**GREEN Phase:**

**Implementation:** Add amend support to `commit_pipeline()`

**Behavior:**
- If `amend` in `input.options`: add `--amend` to `git commit` args
- If `no-edit` in `input.options`: add `--no-edit` to `git commit` args, `## Message` section not used
- Pass `amend=True` to `validate_files()` — enables HEAD file acceptance
- Submodule amend: `_git("-C", path, "commit", "--amend", "-m", message)` then re-stage pointer
- Submodule amend + `no-edit`: `_git("-C", path, "commit", "--amend", "--no-edit")` then re-stage pointer

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Add amend and no-edit flag handling throughout pipeline

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.4: Validation levels (C-4)

**RED Phase:**

**Test:** `test_commit_just_lint`, `test_commit_no_vet`, `test_commit_combined_options`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- `just-lint` option → pipeline runs `just lint` instead of `just precommit`
- `no-vet` option → vet check skipped entirely
- `just-lint` + `no-vet` → lint only, no vet
- `amend` + `no-vet` → full precommit, amend, no vet
- `amend` + `just-lint` → lint only, amend
- Options are orthogonal — any combination valid

**Expected failure:** Options not affecting validation behavior

**Why it fails:** No option dispatch for validation levels

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_just_lint -v`

---

**GREEN Phase:**

**Implementation:** Add option-based validation dispatch to `commit_pipeline()`

**Behavior:**
- Inspect `input.options` set before dispatching validation:
  - `just-lint` present → run `just lint` instead of `just precommit`
  - `no-vet` present → skip vet check entirely
  - Both absent → default: `just precommit` + vet check
  - Orthogonal: each option controls one aspect independently

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Add option dispatch logic before validation calls

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.5: Output formatting

**RED Phase:**

**Test:** `test_format_success_parent`, `test_format_success_submodule`, `test_format_warning`, `test_format_failure`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- `format_commit_output(result)` with parent-only success:
  ```
  [session-cli-tool a7f38c2] ✨ Add commit CLI
   3 files changed, 142 insertions(+), 8 deletions(-)
  ```
  Raw git output, no prefix
- With submodule success:
  ```
  agent-core:
  [session-cli-tool 4b2c1a0] 🤖 Update fragment
   1 file changed, 5 insertions(+), 2 deletions(-)
  [session-cli-tool a7f38c2] ✨ Add commit CLI
   4 files changed, 142 insertions(+), 8 deletions(-)
  ```
  Submodule output labeled with `<path>:`, parent unlabeled
- Warning + success:
  ```
  **Warning:** Submodule message provided but no changes found for: agent-core. Ignored.

  [session-cli-tool a7f38c2] ✨ Add commit CLI
  ```
  Warning prepended to git output
- Failure: gate-specific diagnostic (vet, precommit, clean-files) — format varies by gate

**Expected failure:** No dedicated formatting function

**Why it fails:** Output formatting inline in pipeline, not testable in isolation

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_format_success_parent -v`

---

**GREEN Phase:**

**Implementation:** Extract output formatting to testable functions

**Behavior:**
- Extract output formatting to a dedicated function that accepts submodule outputs (keyed by path), parent output string, and any warning messages
- Submodule outputs labeled with `<path>:` prefix
- Parent output appended unlabeled
- Warnings prepended as `**Warning:**` lines with blank line separator
- Strip git `hint:` and advice lines from output — LLM agents interpret these as instructions (e.g., "remove index.lock" → agent deletes the file)
- For failures: separate formatting per gate type already produces structured markdown

**Changes:**
- File: `src/claudeutils/session/commit.py`
  Action: Extract `format_commit_output()` from pipeline logic, include hint-line stripping

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.6: CLI wiring — `claudeutils _commit`

**RED Phase:**

**Test:** `test_commit_cli_success`, `test_commit_cli_validation_error`, `test_commit_cli_vet_failure`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- CliRunner invoking `_commit` with valid commit markdown on stdin (real git repo via `tmp_path`, file staged) → exit 0, stdout contains `[branch hash] message` format line
- CliRunner invoking `_commit` with files that have no changes → exit 2, stdout contains `**Error:**` and `STOP:`
- CliRunner invoking `_commit` with empty stdin → exit 2, stdout contains `**Error:**` and references missing required section
- CliRunner invoking `_commit` with files matching `require-review` patterns in pyproject.toml, no vet report present → exit 1, stdout contains `**Vet check:**` and `unreviewed`

**Expected failure:** Command not registered

**Why it fails:** No `_commit` command implementation

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_cli_success -v`

---

**GREEN Phase:**

**Implementation:** Wire the `commit_cmd` Click command in `src/claudeutils/session/cli.py`, already registered in main `cli.py` from Step 1.2

**Behavior:**
- `commit_cmd` Click command implementation
- Read all stdin → `parse_commit_input()`
- Call `commit_pipeline(input)` → `CommitResult`
- Output `result.output` to stdout
- Exit 0 on success, 1 on pipeline error, 2 on input validation error

**Changes:**
- File: `src/claudeutils/session/cli.py`
  Action: Implement `commit_cmd` with full pipeline
  Location hint: Commit command stub from Step 1.2

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

**Phase 6 Checkpoint:** `just precommit` — commit subcommand fully functional.

### Phase 7: Integration tests (type: tdd, model: sonnet)

Cross-subcommand contract test. Verifies parser consistency between handoff writes and status reads.

---

## Cycle 7.1: Cross-subcommand — handoff then status

**RED Phase:**

**Test:** `test_handoff_then_status`
**File:** `tests/test_session_integration.py`

**Assertions:**
- Create `tmp_path` git repo with `agents/session.md`
- CliRunner invokes `_handoff` with stdin (updates session.md)
- Then CliRunner invokes `_status` (reads updated session.md)
- Status output reflects the new status line from handoff input
- Status output reflects the updated completed section
- Verifies parser consistency: handoff writes → status reads the same format

**Expected failure:** Parser asymmetry between write and read paths

**Why it fails:** Integration verifies round-trip consistency

**Verify RED:** `pytest tests/test_session_integration.py::test_handoff_then_status -v`

---

**GREEN Phase:**

**Implementation:** Fix any format asymmetries between handoff writes and status reads

**Behavior:**
- Handoff writes status line and completed section in format that status parser expects
- Any format divergence between write and read is a bug

**Changes:**
- Fix any discovered format mismatches

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---

**Phase 7 Checkpoint (full):** `just precommit` — all tests pass, full suite green. Final checkpoint covers all 7 phases.

---

## Outstanding Design Revisions

All revisions applied (2026-03-14). Outline and runbook-outline updated:

- **ST-1 semantics:** ✓ Outline already had correct wording (consecutive + cap 5). Runbook-outline notes updated.
- **Handoff pipeline reordering:** ✓ Precommit removed from handoff pipeline (H-1, pipeline steps, H-3, H-4 step_reached). Added to OUT scope as skill responsibility. Runbook-outline Cycle 4.5 removed, H-3 notes simplified.
