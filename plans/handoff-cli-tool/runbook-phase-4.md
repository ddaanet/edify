### Phase 4: Handoff pipeline (type: tdd, model: sonnet)

Stdin parsing, session.md writes, committed detection, state caching, diagnostics.

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

**Handoff CLI tool design (Phase A):**
- Produced outline
- Review by outline-review-agent
```

**Expected failure:** `ImportError` — no `parse_handoff_input` function

**Why it fails:** No `session/handoff/` module with parsing

**Verify RED:** `pytest tests/test_session_handoff.py::test_parse_handoff_input -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/handoff/parse.py`

**Behavior:**
- `HandoffInput` dataclass: `status_line: str`, `completed_lines: list[str]`
- `parse_handoff_input(text: str) -> HandoffInput` — locate `**Status:**` line, extract text after marker. Locate `## Completed This Session` heading, extract all lines until next `## ` or EOF
- `HandoffInputError` exception for missing required markers

**Changes:**
- File: `src/claudeutils/session/handoff/parse.py`
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

**Implementation:** Add `overwrite_status()` to `src/claudeutils/session/handoff/pipeline.py`

**Behavior:**
- Read session.md, find line after `# Session Handoff:` and before first `## ` heading
- Replace that region with `**Status:** {new_text}\n`
- Preserve blank line between status and first `##`
- Write back to file

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Create with `overwrite_status(session_path: Path, status_text: str) -> None`

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

**Implementation:** Add `write_completed()` to `session/handoff/pipeline.py`

**Behavior:**
- Compare completed section in working tree vs HEAD via `git diff HEAD -- agents/session.md`
- Parse diff to determine which mode applies
- Execute appropriate write (overwrite, append, or strip-committed-then-keep-new)

**Approach:** Use `_git("diff", "HEAD", "--", str(session_path))` to get diff. Parse for completed section hunk. Absence of hunk → overwrite mode. Hunk with only additions → append mode. Hunk with preserved old + new → auto-strip mode.

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
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
- `step_reached` values: `"write_session"`, `"precommit"`, `"diagnostics"`
- State file survives across function calls (not deleted on load)

**Expected failure:** `ImportError` — state caching functions don't exist

**Why it fails:** No state management module

**Verify RED:** `pytest tests/test_session_handoff.py::test_state_cache_create -v`

---

**GREEN Phase:**

**Implementation:** Add state caching to `src/claudeutils/session/handoff/pipeline.py`

**Behavior:**
- `HandoffState` dataclass: `input_markdown: str`, `timestamp: str`, `step_reached: str`
- `save_state(input_md: str, step: str) -> None` — write JSON to `tmp/.handoff-state.json`. Create `tmp/` if needed
- `load_state() -> HandoffState | None` — read and parse JSON, return None if file missing
- `clear_state() -> None` — delete state file if exists

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Add `HandoffState`, `save_state()`, `load_state()`, `clear_state()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

**Mid-phase checkpoint:** `just precommit` — mutations + recovery established before external tool integration.

---

## Cycle 4.5: Precommit integration

**RED Phase:**

**Test:** `test_handoff_precommit_pass`, `test_handoff_precommit_fail`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `run_precommit()` calls `just precommit` subprocess, returns `PrecommitResult` with `success: bool`, `output: str`
- On failure: `success == False`, `output` contains the precommit failure text
- On success: `success == True`, `output` contains passing summary

**Expected failure:** `ImportError` — `run_precommit` doesn't exist

**Why it fails:** No precommit integration

**Verify RED:** `pytest tests/test_session_handoff.py::test_handoff_precommit_pass -v`

---

**GREEN Phase:**

**Implementation:** Add `run_precommit()` to `session/handoff/pipeline.py`

**Behavior:**
- `PrecommitResult` dataclass: `success: bool`, `output: str`
- `run_precommit() -> PrecommitResult` — `subprocess.run(["just", "precommit"], capture_output=True, text=True, check=False)`. Return success based on returncode.

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Add `PrecommitResult`, `run_precommit()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.6: Diagnostic output (H-3)

**RED Phase:**

**Test:** `test_diagnostics_precommit_pass`, `test_diagnostics_precommit_fail`, `test_diagnostics_learnings_age`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- `format_diagnostics(precommit_result, git_status, learnings_age)` when precommit passed:
  - Contains precommit output
  - Contains git status/diff markdown
  - No learnings age warning if all entries < 7 days
- When precommit failed:
  - Contains precommit failure output
  - Does NOT contain git status/diff (conditional — only on pass)
  - Contains learnings age summary if any ≥ 7 days
- When learnings have entries ≥ 7 active days:
  - Output contains `**Learnings:** N entries ≥7 days — consider /codify`

**Expected failure:** `ImportError`

**Why it fails:** No diagnostics formatting function

**Verify RED:** `pytest tests/test_session_handoff.py::test_diagnostics_precommit_pass -v`

---

**GREEN Phase:**

**Implementation:** Add `format_diagnostics()` to `session/handoff/context.py`

**Behavior:**
- `format_diagnostics(precommit: PrecommitResult, git_output: str | None, learnings_age_days: int | None) -> str`
- Always include precommit result block
- If precommit passed: include git status/diff output
- If any learnings ≥ 7 days: append age summary line
- All output as structured markdown

**Changes:**
- File: `src/claudeutils/session/handoff/context.py`
  Action: Create with `format_diagnostics()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 4.7: CLI wiring — `claudeutils _session handoff`

**RED Phase:**

**Test:** `test_session_handoff_cli_fresh`, `test_session_handoff_cli_resume`, `test_session_handoff_cli_no_stdin_no_state`
**File:** `tests/test_session_handoff.py`

**Assertions:**
- CliRunner with stdin input → exit 0, session.md status line updated, completed section written, diagnostics output
- CliRunner without stdin but with existing state file → exit 0, resumes from `step_reached`
- CliRunner without stdin and no state file → exit 2, output contains error message about missing input

**Expected failure:** Command not registered

**Why it fails:** No handoff subcommand

**Verify RED:** `pytest tests/test_session_handoff.py::test_session_handoff_cli_fresh -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/handoff/cli.py` with Click command, wire full pipeline

**Behavior:**
- `@click.command(name="handoff")` function
- Read stdin (if available) → `parse_handoff_input()`
- If no stdin: check for state file → `load_state()` → resume
- If no stdin and no state: `_fail("**Error:** No input on stdin and no state file", code=2)`
- Fresh pipeline: parse → save_state → overwrite_status → write_completed → run_precommit → diagnostics → clear_state
- Resume: load state → skip to `step_reached` → continue pipeline
- On precommit failure: output result + diagnostics, leave state file, exit 1

**Changes:**
- File: `src/claudeutils/session/handoff/cli.py`
  Action: Create with `handoff` Click command orchestrating full pipeline
- File: `src/claudeutils/session/cli.py`
  Action: Register: `from claudeutils.session.handoff.cli import handoff; session_group.add_command(handoff)`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_handoff.py -v`
**Verify no regression:** `just precommit`

---

**Phase 4 Checkpoint:** `just precommit` — handoff subcommand fully functional.
