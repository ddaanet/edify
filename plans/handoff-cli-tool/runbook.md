# RC4 Fix Runbook: handoff-cli-tool

**Input:** plans/handoff-cli-tool/reports/deliverable-review.md (0C/2M/9m)
**Date:** 2026-03-23
**Tier:** 2 — Lightweight Delegation

## Recall

Resolve before executing: `plans/handoff-cli-tool/recall-artifact.md`

Additional for this round:
- `when preferring e2e over mocked subprocess` — real git repos for M-1 committed-state test
- `when fixture shadowing creates dead code` — verify M-2 replacements don't create shadows
- `when test setup steps fail` — use check=False + stderr assert in init_repo_minimal
- `when docstring formatting conflicts` — keep docstrings under 70 chars

## Phase 1: Test Refactoring (type: general)

### Step 1.1: init_repo_minimal helper — M-2

**Goal:** Centralize common git init + user config to eliminate 5 duplicate `_init_repo` local functions.

**Add to `tests/pytest_helpers.py`:**

Function `init_repo_minimal(path: Path) -> None`:
- Runs: `git init`, `git config user.email test@test.com`, `git config user.name Test`
- Uses `cwd=path` (not `-C` style — matches local variant pattern)
- Self-diagnosing failure: use `check=False` and assert `returncode == 0` with stderr in message
- Docstring summary ≤70 chars total

**Replace local `_init_repo` in 5 files.** For each, remove the function definition and update call sites:

- `tests/test_session_commit.py` — full replacement: `_init_repo(path)` → `init_repo_minimal(path)`
- `tests/test_session_handoff.py` — full replacement; function does init+config only
- `tests/test_session_handoff_cli.py` — full replacement
- `tests/test_session_commit_pipeline_ext.py` — partial: replace init+config block; keep `(path/"README.md").write_text("init")` inline at call site
- `tests/test_session_integration.py` — partial: replace init+config block; keep session.md creation, git add, git commit inline at call site

**Import:** Add `from tests.pytest_helpers import init_repo_minimal` where needed (check existing import style per file — some may use conftest, some direct import).

**Verify:** `just test tests/test_session_commit.py tests/test_session_handoff.py tests/test_session_handoff_cli.py tests/test_session_commit_pipeline_ext.py tests/test_session_integration.py`

---

## Phase 2: Test Coverage (type: general)

### Step 2.1: write_completed committed-state test — M-1

**Prerequisite:** Read `tests/test_session_handoff.py:175-270` — understand existing write_completed tests and _init_repo usage.

**Goal:** Verify write_completed overwrites correctly even when session.md has been committed.

**Add to `tests/test_session_handoff.py`:**

Function `test_write_completed_overwrites_committed_state(tmp_path)`:
- Setup: call `init_repo_minimal(tmp_path)`, create `agents/` dir + session.md with standard format including `## Completed This Session` containing "- Committed prior work."
- Commit: git add + git commit session.md (real subprocess, not mocked)
- Action: call `write_completed(session_file, ["- New work done."])`
- Assert:
  - session.md text contains `"- New work done."`
  - session.md text does NOT contain `"Committed prior work"`
  - Completed section holds exactly the new lines (no accumulation)

**Verify:** `just test tests/test_session_handoff.py`

---

### Step 2.2: Test quality batch — m-5, m-6, m-7

**Goal:** Three independent test improvements.

**m-5 — Parallel cap test** in `tests/test_session_status.py`:

Add `test_detect_parallel_caps_at_five(...)`:
- Create 7 ParsedTask objects: `checkbox=" "`, distinct `name` and `plan_dir` (no shared plans)
- Call `detect_parallel(tasks, [])`
- Assert: result is a list of length exactly 5

**m-6 — Fix or-disjunction assertions** in `tests/test_session_commit_pipeline.py` lines ~40, ~75:

Replace `assert "foo" in result.output or "1 file" in result.output` with specific assertions appropriate to each test's intent. Read the surrounding test to determine which branch is actually guaranteed, then assert that.

**m-7 — Extend integration test** in `tests/test_session_integration.py::test_handoff_then_status`:

After existing status assertion, add:
- Read session.md text; assert `**Status:**` line contains the status from the handoff input
- Assert Completed section contains the completed task lines from handoff input

**Verify:** `just test tests/test_session_status.py tests/test_session_commit_pipeline.py tests/test_session_integration.py`

---

## Phase 3: Behavioral Fixes (type: tdd)

### Cycle 3.1: _strip_hints continuation lines — m-4

**Prerequisite:** Read `src/claudeutils/session/commit_pipeline.py:187-191`

**RED Phase:**

**Test:** `test_strip_hints_filters_continuation_lines`
**Module:** Add to `tests/test_session_commit_pipeline.py` (import `_strip_hints` from `claudeutils.session.commit_pipeline` directly)
**Assertions:**
- Input: `"hint: use --force\n  (helpful continuation)\nother line"` → result contains `"other line"`, does NOT contain `"helpful continuation"` or `"hint:"`
- Input: `"advice: do this\n\tcontinuation here\nnormal line"` → result contains `"normal line"`, does NOT contain `"continuation here"`
- Input: `"regular line\nhint: tip\n  more tip"` → result contains `"regular line"`, does NOT contain `"more tip"`

**Expected failure:** `AssertionError` — continuation lines appear in output (current impl filters only hint:/advice: prefix lines)

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_strip_hints_filters_continuation_lines -v`

**GREEN Phase:**

**Implementation:** Replace `_strip_hints` list comprehension with stateful loop.

**Behavior:**
- Lines starting with `"hint:"` or `"advice:"` → skip, set `in_hint=True`
- When `in_hint=True` and line starts with whitespace → skip
- When `in_hint=True` and line does NOT start with whitespace → reset `in_hint=False`, include line

**Changes:**
- File: `src/claudeutils/session/commit_pipeline.py`
  Action: Replace `_strip_hints` function body with loop + `in_hint` state variable
  Location hint: `def _strip_hints` around line 187

**Verify GREEN:** `just green`

---

### Cycle 3.2: HandoffState step_reached field — m-1

**Prerequisite:** Read `src/claudeutils/session/handoff/pipeline.py:14-45`

**RED Phase:**

**Test:** `test_handoff_state_includes_step_reached`
**Module:** `tests/test_session_handoff.py`
**Setup:** Monkeypatch `claudeutils.session.handoff.pipeline._STATE_FILE` to `tmp_path/"state.json"` so test is isolated
**Assertions:**
- Call `save_state("sample markdown")`
- Call `load_state()` → result is not None
- `result.step_reached == "write_session"`
- `json.loads((tmp_path/"state.json").read_text())` contains key `"step_reached"`

**Expected failure:** `AttributeError: 'HandoffState' object has no attribute 'step_reached'`

**Verify RED:** `pytest tests/test_session_handoff.py::test_handoff_state_includes_step_reached -v`

**GREEN Phase:**

**Implementation:** Add `step_reached` field with default to HandoffState.

**Behavior:**
- `HandoffState` gains `step_reached: str = "write_session"` (dataclass default, placed after `timestamp`)
- `asdict(state)` serializes `step_reached` automatically
- Backward compat: old state files without `step_reached` still load via `HandoffState(**data)` because field has a default

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Add `step_reached: str = "write_session"` after `timestamp: str` in HandoffState
  Location hint: line ~19

**Verify GREEN:** `just green`

---

### Cycle 3.3: ▶ format fix — m-3

**Prerequisite:** Read `src/claudeutils/session/status/render.py:38-54`; grep `tests/test_session_status.py` for existing ▶ format assertions

**RED Phase:**

**Test:** `test_render_pending_next_task_format` (new, or update existing ▶ format test if one exists)
**Module:** `tests/test_session_status.py`
**Assertions:**
- For task: name="Build widget", command="/design plans/w/brief.md", model="sonnet", restart=True
- `render_pending([task], {})` contains a line matching `"▶ Build widget (sonnet) | Restart: yes"` (no `" — "`, no inline backtick-cmd)
- Output contains a line matching `"  \`/design plans/w/brief.md\`"` (2-space indent + backtick-wrapped cmd)

**Expected failure:** `AssertionError` — output uses old format `▶ Build widget — \`...\` | sonnet | restart: yes`

**Verify RED:** `pytest tests/test_session_status.py::test_render_pending_next_task_format -v`

**GREEN Phase:**

**Implementation:** Update `render_pending` ▶ line to two-line design spec format.

**Behavior:**
- Line 1: `▶ {name} ({model}) | Restart: {Yes/No}` (capitalize Yes/No)
- Line 2: `  \`{cmd}\`` (2-space indent, cmd in backticks)

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Replace single `lines.append(f"▶ ...")` with two appends
  Location hint: lines ~43-44
  Also: grep test suite for any other assertions checking old ▶ format and update them to new spec

**Verify GREEN:** `just green`

---

### Cycle 3.4: ANSI color in _status — m-2

**Prerequisite:** Read full `src/claudeutils/session/status/render.py`; read `src/claudeutils/session/status/cli.py`

**RED Phase:**

**Test:** `test_render_pending_color_mode`
**Module:** `tests/test_session_status.py`
**Assertions:**
- `render_pending([task], {}, color=True)` → output string contains `"\x1b["` (ANSI escape present)
- `render_pending([task], {})` (default) → output does NOT contain `"\x1b["`
- `render_pending([task], {}, color=False)` → output does NOT contain `"\x1b["`

**Expected failure:** `TypeError: render_pending() got an unexpected keyword argument 'color'`

**Verify RED:** `pytest tests/test_session_status.py::test_render_pending_color_mode -v`

**GREEN Phase:**

**Implementation:** Add `color: bool = False` to `render_pending`; style ▶ line with click.

**Behavior:**
- When `color=True`: wrap the ▶ header line with `click.style(line, bold=True, fg="green")` before appending
- When `color=False` (default): no change (existing tests pass without modification)
- CLI passes `color=sys.stdout.isatty()` to `render_pending`

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Add `import click` at top of imports; add `color: bool = False` kwarg to `render_pending`; apply style to ▶ header line when color=True
  Location hint: imports block + render_pending signature + ▶ append (after Cycle 3.3)
- File: `src/claudeutils/session/status/cli.py`
  Action: Pass `color=sys.stdout.isatty()` to `render_pending` call
  Location hint: render_pending call around line 80

**Verify GREEN:** `just green`
