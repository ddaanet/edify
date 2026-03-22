---
name: handoff-cli-tool
model: sonnet
---

## Outline

Rework runbook fixing 19 findings from deliverable review (5C/11M + 3 co-located minor).

### Phase 1: Commit Pipeline Correctness (type: tdd)
- Cycle 1.1: `_git_commit` returncode propagation (C#2 + MN-1)
- Cycle 1.2: Validation before submodule commit (C#3)
- Cycle 1.3: Exit code 2 for CleanFileError (C#4)

### Phase 2: Bug Fixes (type: tdd)
- Cycle 2.1: `git_status()` strip bug (M#10)
- Cycle 2.2: Handoff uses shared git changes (M#11)

### Phase 3: Status Completeness (type: tdd)
- Cycle 3.1: Plan state discovery (M#7 + MN-5)
- Cycle 3.2: Session continuation header (M#8)
- Cycle 3.3: Output format alignment (M#9)
- Cycle 3.4: Old format enforcement (M#12)

### Phase 4: Test Additions (type: general)
- Step 4.1: Missing test coverage (C#5, M#13, M#14, M#15, M#16, m-4)

### Phase 5: Cleanup (type: inline)
- Delete dead code (M#6)
- Fix SKILL.md allowed-tools (C#1)

## Common Context

**Rework scope:** Fixing deliverable review findings for handoff-cli-tool plan. Full review at `plans/handoff-cli-tool/reports/deliverable-review.md`.

**Key findings by area:**

Commit pipeline (`src/claudeutils/session/commit_pipeline.py`, `cli.py`):
- C#2: `_git_commit` ignores non-zero returncode — `check=False` + no returncode check = silent failure
- C#3: Submodule committed before validation gate — irrevocable commit before precommit/vet
- C#4: `CleanFileError` exits 1, design says exit 2 (input validation)
- MN-1: Uncaught `CalledProcessError` from `_stage_files` (`check=True`)

Bug fixes (`src/claudeutils/git.py`, `session/handoff/cli.py`):
- M#10: `git_status()` uses `.strip()` — corrupts first porcelain line's XY code (known bug class, see learnings.md)
- M#11: Handoff CLI uses inline subprocess, not `_git changes` utility — misses submodule changes

Status (`src/claudeutils/session/status/cli.py`, `render.py`):
- M#7: Plan state discovery not implemented (empty strings)
- M#8: Session continuation header missing (git dirty check + review-pending)
- M#9: Output format diverges — separate Next: section instead of ▶ marker in In-tree list
- M#12: Old format silently accepted, design says fatal exit 2

**Recall entries (resolve before implementing):**
- `when raising exceptions for expected conditions` — custom types not ValueError
- `when adding error handling to call chain` — context at failure, display at top
- `when writing error exit code` — `_fail` pattern, `Never` return
- `when cli commands are llm-native` — exit code signal, no stderr
- `when testing CLI tools` — Click CliRunner, in-process
- `when preferring e2e over mocked subprocess` — real git repos via tmp_path
- `when extracting git helper functions` — `_git` pattern

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: 1) RED: Write failing test, 2) Verify RED, 3) GREEN: Minimal implementation, 4) Verify GREEN, 5) Verify Regression, 6) REFACTOR (optional)

**Stop/Error Conditions (all cycles):**
STOP IMMEDIATELY if: RED phase test passes (expected failure) • RED phase failure message doesn't match expected • GREEN phase tests don't pass after implementation • Any existing tests break (regression)

Actions when stopped: 1) Document in reports/cycle-{X}-{Y}-notes.md 2) Test passes unexpectedly → Investigate if feature exists 3) Regression → STOP, report broken tests 4) Scope unclear → STOP, document ambiguity

**Conventions:**
- Use Read/Write/Edit/Grep tools (not Bash for file ops)
- Report errors explicitly (never suppress)
- Docstring summaries ≤70 chars (docformatter wraps at 80, ruff D205 rejects two-line)

### Phase 1: Commit Pipeline Correctness (type: tdd)

## Cycle 1.1: git commit returncode propagation

**Finding:** C#2 + MN-1

**Prerequisite:** Read `src/claudeutils/session/commit_pipeline.py:62-84, 110-148, 215-291`

---

**RED Phase:**

**Test:** `test_commit_pipeline_git_failure`
**Assertions:**
- When git commit subprocess returns non-zero exit, `commit_pipeline()` returns `CommitResult(success=False)` with output containing git's stderr
- When `_stage_files` raises `CalledProcessError`, `commit_pipeline()` returns `CommitResult(success=False)` with structured error message, not unhandled traceback
- Same for `_commit_submodule`'s internal `git add` — failure returns structured error

**Expected failure:** `AssertionError` — pipeline currently ignores returncode, unconditionally returns `success=True`

**Why it fails:** `_git_commit` discards `result.returncode`, returns only `result.stdout.strip()`. `commit_pipeline` wraps it in `CommitResult(success=True)` unconditionally.

**Verify RED:** `pytest tests/test_session_commit_pipeline_ext.py::test_commit_pipeline_git_failure -v`

---

**GREEN Phase:**

**Implementation:** Add returncode propagation to commit helpers

**Behavior:**
- `_git_commit` returns `tuple[bool, str]` — `(returncode == 0, stdout or stderr)`
- `_commit_submodule` returns `tuple[bool, str]` with same pattern
- `commit_pipeline` checks boolean, returns `CommitResult(success=False)` on failure
- `_stage_files` and `_commit_submodule` git-add `CalledProcessError` caught in pipeline, returned as `CommitResult(success=False, output="**Error:** staging failed: {stderr}")`

**Changes:**
- File: `commit_pipeline.py`
  Action: Change `_git_commit` to return `(result.returncode == 0, result.stdout.strip() if ok else result.stderr.strip())`
  Location: `_git_commit` function (lines 62-84)

- File: `commit_pipeline.py`
  Action: Same pattern for `_commit_submodule` return value
  Location: `_commit_submodule` function (lines 110-148)

- File: `commit_pipeline.py`
  Action: Wrap staging calls in try/except CalledProcessError, check commit return tuples
  Location: `commit_pipeline` function (lines 254-290)

**Verify GREEN:** `just green`

## Cycle 1.2: Validation before submodule commit

**Finding:** C#3

**Prerequisite:** Read `src/claudeutils/session/commit_pipeline.py:215-291` — current pipeline ordering

---

**RED Phase:**

**Test:** `test_pipeline_validates_before_submodule_commit`
**Assertions:**
- When `_validate` returns failure result, `_commit_submodule` has not been called
- Mock `_commit_submodule` and `_validate` (failing) — assert `_commit_submodule` call count is 0
- When validation passes, submodule commits proceed normally

**Expected failure:** `AssertionError` — submodule commit at line 256-264 runs before `_validate` at line 271

**Why it fails:** Pipeline order is: commit submodules → stage parent → validate. Submodules committed before validation gate.

**Verify RED:** `pytest tests/test_session_commit_pipeline_ext.py::test_pipeline_validates_before_submodule_commit -v`

---

**GREEN Phase:**

**Implementation:** Reorder pipeline: validation before irrevocable commits

**Behavior:**
- New order: validate_files → stage parent → validate (precommit/vet) → commit submodules → commit parent
- If validation fails, no submodule commits made — clean recovery possible
- Staging parent files before validation lets precommit see the staged state

**Changes:**
- File: `commit_pipeline.py`
  Action: Move parent staging and `_validate` call before submodule commit loop
  Location: `commit_pipeline` function — reorder the four blocks

**Verify GREEN:** `just green`

## Cycle 1.3: Exit code 2 for CleanFileError

**Finding:** C#4

**Prerequisite:** Read `src/claudeutils/session/cli.py:16-32` and `commit_pipeline.py:227-236`

---

**RED Phase:**

**Test:** `test_commit_cli_clean_file_exits_2`
**Assertions:**
- CLI returns exit code 2 when `commit_pipeline` raises `CleanFileError`
- CLI returns exit code 1 for other pipeline failures (validation fail, git error)
- Output contains the CleanFileError message

**Expected failure:** `AssertionError` — CLI exits 1 for all `success=False` results

**Why it fails:** `cli.py:31-32` exits 1 unconditionally for all failures. CleanFileError caught inside pipeline, never reaches CLI.

**Verify RED:** `pytest tests/test_session_commit_cli.py::test_commit_cli_clean_file_exits_2 -v`

---

**GREEN Phase:**

**Implementation:** Let CleanFileError propagate to CLI for exit code routing

**Behavior:**
- Remove `try/except CleanFileError` from `commit_pipeline` — let it propagate
- CLI catches `CleanFileError` specifically, displays message, exits 2
- Per "context at failure, display at top" — validate_files provides context, CLI routes exit code
- Other failures continue through `CommitResult(success=False)` → exit 1

**Changes:**
- File: `commit_pipeline.py`
  Action: Remove lines 229-236 (try/except CleanFileError), let it propagate
  Location: `commit_pipeline` function

- File: `cli.py`
  Action: Add `except CleanFileError as e` before the pipeline call result check, echo and exit 2
  Location: `commit_cmd` function

**Verify GREEN:** `just green`

### Phase 2: Bug Fixes (type: tdd)

## Cycle 2.1: git_status strip bug

**Finding:** M#10

**Prerequisite:** Read `src/claudeutils/git.py:84-98`

---

**RED Phase:**

**Test:** `test_git_status_preserves_porcelain_format`
**Assertions:**
- In a repo with a modified (unstaged) file, `git_status()` output line starts with ` M ` (space-M-space), not `M ` (M-space)
- Full XY status code preserved for every line, not just first
- Empty repo returns empty string (backward compat)

**Expected failure:** `AssertionError` — `.strip()` removes leading space from first line, ` M file` becomes `M file`

**Why it fails:** `result.stdout.strip()` strips all leading/trailing whitespace from entire output. First line's leading space (part of XY code) is removed.

**Verify RED:** `pytest tests/test_git_cli.py::test_git_status_preserves_porcelain_format -v`

---

**GREEN Phase:**

**Implementation:** Replace `.strip()` with format-preserving trim

**Behavior:**
- `git_status()` returns `result.stdout.rstrip('\n')` — preserves leading spaces per line
- Empty stdout → empty string (unchanged)
- `git_diff()` similarly changed for consistency (though diff doesn't have same issue)

**Changes:**
- File: `git.py`
  Action: Change `return result.stdout.strip()` to `return result.stdout.rstrip('\n')`
  Location: `git_status` (line 98), optionally `git_diff` (line 118)

**Verify GREEN:** `just green`

## Cycle 2.2: Handoff uses shared git changes

**Finding:** M#11

**Prerequisite:** Read `src/claudeutils/session/handoff/cli.py:57-72` and `src/claudeutils/git_cli.py:41-76`

---

**RED Phase:**

**Test:** `test_handoff_shows_submodule_changes`
**Assertions:**
- In a repo with dirty submodule, handoff output includes submodule path-prefixed file status
- Output contains `## Submodule:` section header (matching `_git changes` format)
- Parent-only changes still work correctly

**Expected failure:** `AssertionError` — inline subprocess calls `git status --porcelain` and `git diff HEAD` on parent only, ignoring submodules

**Why it fails:** Handoff CLI uses raw subprocess without submodule discovery (lines 57-72).

**Verify RED:** `pytest tests/test_session_handoff.py::test_handoff_shows_submodule_changes -v`

---

**GREEN Phase:**

**Implementation:** Extract git changes logic into shared function

**Behavior:**
- New `git_changes() -> str` function in `git_cli.py` containing `changes_cmd`'s output logic
- `changes_cmd` delegates to `git_changes()`
- Handoff CLI imports `git_changes()` and uses it instead of inline subprocess
- Submodule changes now visible in handoff diagnostics

**Changes:**
- File: `git_cli.py`
  Action: Extract function `git_changes() -> str` from `changes_cmd` body
  Location: Before `changes_cmd`

- File: `git_cli.py`
  Action: `changes_cmd` calls `git_changes()` and echoes result
  Location: `changes_cmd` body

- File: `handoff/cli.py`
  Action: Replace lines 57-72 with `from claudeutils.git_cli import git_changes` and call
  Location: After `write_completed` / before `clear_state`

**Verify GREEN:** `just green`

### Phase 3: Status Completeness (type: tdd)

## Cycle 3.1: Plan state discovery

**Finding:** M#7 + MN-5

**Prerequisite:** Read `src/claudeutils/session/status/cli.py:31-34, 55-60`. Discover `list_plans` import path — `Grep` for `def list_plans` in `src/`.

---

**RED Phase:**

**Test:** `test_status_shows_plan_states`
**Assertions:**
- Task with `plan_dir = "plans/foo"` where `plans/foo/lifecycle.md` exists → status output contains actual lifecycle state (e.g., `Status: planned`), not `Status: ` (empty)
- `render_unscheduled` receives populated dict → orphan plans shown in output
- Task with plan_dir but no lifecycle.md → `Status:` line omitted (not blank)

**Expected failure:** `AssertionError` — `plan_states` populated with empty strings, `render_unscheduled` always receives empty dict

**Why it fails:** Lines 31-34 hardcode empty strings; lines 55-60 pass empty dict.

**Verify RED:** `pytest tests/test_session_status.py::test_status_shows_plan_states -v`

---

**GREEN Phase:**

**Implementation:** Populate plan states from filesystem

**Behavior:**
- Import plan discovery from worktree module (`list_plans` or equivalent)
- Populate `plan_states` with actual lifecycle states from `plans/*/lifecycle.md`
- Pass real `all_plans` dict to `render_unscheduled`
- `render_pending` skips `Status:` line when state is empty/None

**Changes:**
- File: `status/cli.py`
  Action: Replace placeholder with plan discovery call
  Location: Lines 31-34 and 55-60

- File: `status/render.py`
  Action: Conditionalize Status line — omit when empty
  Location: `render_pending` (lines 53-56)

**Verify GREEN:** `just green`

## Cycle 3.2: Session continuation header

**Finding:** M#8

---

**RED Phase:**

**Test:** `test_status_continuation_header`
**Assertions:**
- Dirty git tree → output starts with `Session: uncommitted changes — \`/handoff\`, \`/commit\``
- Clean git tree → no continuation header in output
- When plan_states contains `review-pending` for plan `foo` → header includes `, \`/deliverable-review plans/foo\``

**Expected failure:** `AssertionError` — continuation header feature entirely absent

**Why it fails:** No code checks git dirty state or renders continuation header.

**Verify RED:** `pytest tests/test_session_status.py::test_status_continuation_header -v`

---

**GREEN Phase:**

**Implementation:** Add continuation header rendering

**Behavior:**
- New `render_continuation(is_dirty: bool, plan_states: dict) -> str` function
- Checks dirty state (import `_is_dirty` from `git.py`)
- If dirty, builds "Session: uncommitted changes — `/handoff`, `/commit`"
- Scans plan_states for `review-pending`, appends deliverable-review command
- Continuation header is first section in output

**Changes:**
- File: `status/render.py`
  Action: Add `render_continuation` function
  Location: New function at module level

- File: `status/cli.py`
  Action: Call `_is_dirty()`, call `render_continuation`, prepend to sections
  Location: Before In-tree sections

**Verify GREEN:** `just green`

## Cycle 3.3: Output format alignment

**Finding:** M#9

**Prerequisite:** Read `src/claudeutils/session/status/render.py:8-57` — current rendering

---

**RED Phase:**

**Test:** `test_status_format_merged_next`
**Assertions:**
- First eligible pending task in In-tree list is prefixed with `▶`
- No separate `Next:` section in output when first in-tree is next task
- First task line includes command in backticks, model, and restart metadata
- Non-first tasks show model (if non-default) but not command/restart

**Expected failure:** `AssertionError` — separate `Next:` section always rendered, `render_pending` uses `- name` without `▶`

**Why it fails:** `render_next` always generates separate section; `render_pending` doesn't distinguish first task.

**Verify RED:** `pytest tests/test_session_status.py::test_status_format_merged_next -v`

---

**GREEN Phase:**

**Implementation:** Merge next-task metadata into In-tree list

**Behavior:**
- `render_pending` marks first eligible pending task with `▶` prefix
- First task includes command, model, restart on its line
- Remove `render_next` call from CLI (Next section eliminated)
- Non-first tasks: name + model (if non-default) only

**Changes:**
- File: `status/render.py`
  Action: Modify `render_pending` — first eligible task gets `▶` + full metadata
  Location: `render_pending` function

- File: `status/cli.py`
  Action: Remove `render_next` call and its section append
  Location: Lines 38-41

**Verify GREEN:** `just green`

## Cycle 3.4: Old format enforcement

**Finding:** M#12

**Prerequisite:** Read `src/claudeutils/session/parse.py:84-109` and `src/claudeutils/validation/task_parsing.py` — understand what `parse_task_line` returns for old-format lines

---

**RED Phase:**

**Test:** `test_status_rejects_old_format`
**Assertions:**
- Session.md with old-format task lines (e.g., `- [ ] Task name` without `—` command/model metadata) → CLI exits with code 2
- Error output contains message about mandatory metadata
- Well-formed sessions (with metadata) parse and render successfully

**Expected failure:** `AssertionError` — parser returns `None` for unparseable lines (silently filtered), CLI exits 0

**Why it fails:** `parse_task_line` returns `None` for old-format, `parse_tasks` filters None, CLI renders whatever parsed successfully.

**Verify RED:** `pytest tests/test_session_status.py::test_status_rejects_old_format -v`

---

**GREEN Phase:**

**Implementation:** Add metadata validation after parsing

**Behavior:**
- After `parse_session`, validate in_tree_tasks have required metadata
- Tasks without command metadata → `_fail("**Error:** Old-format tasks ...")` with exit 2
- Detection: compare raw block count to parsed task count, or check metadata
- Alternative: validate task.command is not None for each parsed task

**Changes:**
- File: `status/cli.py`
  Action: Add validation comparing raw block count to parsed task count, or check metadata
  Location: After `parse_session` call, before rendering

**Verify GREEN:** `just green`

### Phase 4: Test Additions (type: general)

## Step 4.1: Missing test coverage

**Findings:** C#5, M#13, M#14, M#15, M#16, m-4

**Prerequisite:** Read each test file and corresponding production code.

**Tasks (batch — all test-only, no production changes):**

1. **C#5 — amend+no-edit pipeline test** → `test_session_commit_pipeline_ext.py`
   Integration test: construct `CommitInput` with `options={"amend", "no-edit"}` and `message=None`. Exercise `commit_pipeline`. Verify git commit used `--amend --no-edit` flags. Verify existing commit message preserved.

2. **M#13 — no-vet skip test** → `test_session_commit_validation.py`
   Add `test_commit_skips_vet_when_no_vet`. Construct input with `options={"no-vet"}`. Mock `vet_check`. Assert `vet_check` not called. (Existing `test_commit_no_vet` tests default path — rename to `test_commit_default_calls_vet` for clarity.)

3. **M#14 — strengthen changes assertion** → `test_git_cli.py:106`
   Change `or` assertion to `and`: verify output includes BOTH status text AND diff text.

4. **M#15 — H-2 append mode test** → `test_session_handoff.py`
   Add test: pre-populate Completed section with old content, call `write_completed` with new content. Verify old content replaced (current simplified implementation overwrites — test confirms this is correct for mode 2).

5. **M#16 — _validate edge cases** → `test_session_commit_validation.py`
   Add `test_validate_stale_vet_failure`: mock `vet_check` returning `VetResult(passed=False, reason="stale", stale_info="...")`. Verify output contains `stale` and `stale_info`. Add `test_validate_unknown_reason`: mock returning `reason=None`. Verify output contains `unknown`.

6. **m-4 — fix weak CLI assertion** → `test_session_commit_cli.py:103`
   Change `or` to `and` — verify both conditions hold.

**Verify:** `just test`

### Phase 5: Cleanup (type: inline)

1. **M#6 — Delete dead code:** Remove `src/claudeutils/session/handoff/context.py`. Remove tests `test_diagnostics_precommit_pass`, `test_diagnostics_precommit_fail`, `test_diagnostics_learnings_age` from `tests/test_session_handoff.py`. Remove any imports of `PrecommitResult` or `format_diagnostics`.

2. **C#1 — Fix SKILL.md allowed-tools:** In `agent-core/skills/handoff/SKILL.md` frontmatter, change `Bash(wc:*)` to `Bash(just:*,wc:*,git:*)` to allow `just precommit`, `git status`, and `git diff`.

**Verify:** `just precommit`

## Deferred Findings

Not in rework scope (Minor, non-blocking):

- MN-2: `_fail` duplication (pre-existing)
- MN-3: `_strip_hints` limited (acceptable risk)
- m-1: `_init_repo` helper duplication (infrastructure)
- m-2: `_build_dependency_edges` blocker matching (test quality)
- m-3: `SESSION_FIXTURE` ordering (test style)
- m-5: Test comment (documentation)
- No ANSI coloring (cosmetic)
