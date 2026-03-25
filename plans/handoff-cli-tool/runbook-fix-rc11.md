# Runbook: Fix RC11 Findings (handoff-cli-tool)

**Tier:** 2 (Lightweight Delegation)
**Type:** TDD
**Source:** `plans/handoff-cli-tool/reports/deliverable-review.md` (RC11)
**Design:** `plans/handoff-cli-tool/outline.md` (H-2, H-4)

## Recall Context

Resolve before execution:
- `when cli commands are llm-native` — all stdout, exit code signal
- `when cli error messages are llm-consumed` — facts only, STOP directive
- `when writing error exit code` — `_fail()` pattern, Never return
- `when testing CLI tools` — Click CliRunner, in-process
- `when preferring e2e over mocked subprocess` — real git repos, mock only for error injection

## Phase 1: H-4 step_reached (type: tdd)

Add `step_reached` field to `HandoffState` for granular resume. Must land before H-2 because H-2 makes writes non-idempotent, making step_reached necessary for correct resume.

### Cycle 1.1: step_reached field in HandoffState

**RED:** Test that `save_state()` accepts and persists `step_reached`, and `load_state()` returns it.

```python
# tests/test_session_handoff.py
def test_save_state_includes_step_reached(tmp_path):
    state_file = tmp_path / "tmp" / ".handoff-state.json"
    # save_state with step_reached="write_session"
    # load back, assert state.step_reached == "write_session"

def test_load_state_backward_compat_missing_step_reached(tmp_path):
    # Write state file without step_reached field
    # load_state() returns state with step_reached default (None or "write_session")
```

**GREEN:** Add `step_reached: str = "write_session"` to `HandoffState`. Update `save_state()` signature to accept `step_reached` parameter.

### Cycle 1.2: CLI resume from step_reached

**RED:** Test that CLI resume skips already-completed steps based on `step_reached`.

```python
def test_handoff_resume_from_diagnostics_skips_writes(tmp_path, ...):
    # Set up state file with step_reached="diagnostics"
    # Invoke handoff_cmd with no stdin
    # Assert: overwrite_status NOT called, write_completed NOT called
    # Assert: git_changes() IS called, state file cleared
```

**GREEN:** Update `cli.py` pipeline flow:
- `save_state(stdin_text, step_reached="write_session")` at start
- After session writes succeed: update state to `step_reached="diagnostics"`
- On resume: check `state.step_reached`, skip writes if `"diagnostics"`

## Phase 2: H-2 committed detection (type: tdd)

Implement three write modes for completed section based on `git diff HEAD -- agents/session.md`.

### Cycle 2.1: Detect committed state — no diff (overwrite)

**RED:** Test that when session.md matches HEAD (committed), `write_completed` overwrites.

```python
def test_write_completed_overwrite_when_committed(tmp_path):
    # Create session.md with Completed section, git init + commit
    # Call write_completed with new_lines
    # Assert: section contains only new_lines (old content replaced)
```

**GREEN:** This is the existing behavior. Test should pass with current code. Bootstrap cycle — establishes baseline.

### Cycle 2.2: Detect uncommitted prior — old removed, new present (append)

**RED:** Test that when HEAD has old completed content and working tree has different content (agent cleared old, wrote new), calling `write_completed` appends.

```python
def test_write_completed_append_when_old_removed(tmp_path):
    # Create session.md with Completed "old items", git commit
    # Modify Completed to "new items" (simulates prior handoff)
    # Call write_completed with additional_lines
    # Assert: section contains "new items" + additional_lines
```

**GREEN:** Add `_detect_write_mode()` function in pipeline.py:
- Run `git diff HEAD -- <session_path>`
- Extract completed section from both HEAD and working tree
- If no diff in completed section → overwrite
- If old removed, new present → append
- Return mode enum/string

Update `write_completed()` to call `_detect_write_mode()` and branch:
- `overwrite` → current `_write_completed_section()` behavior
- `append` → append new_lines after existing content

### Cycle 2.3: Detect uncommitted prior — old preserved with additions (auto-strip)

**RED:** Test that when HEAD completed content is preserved AND new content added (uncommitted), calling `write_completed` strips committed content and keeps new + incoming.

```python
def test_write_completed_autostrip_when_old_preserved(tmp_path):
    # Create session.md with Completed "committed items", git commit
    # Append "new uncommitted items" to Completed section
    # Call write_completed with additional_lines
    # Assert: "committed items" gone, "new uncommitted items" + additional_lines present
```

**GREEN:** Add auto-strip branch to `write_completed()`:
- Extract committed completed content from HEAD (`git show HEAD:<path>`)
- Extract current completed content from working tree
- Strip lines matching committed content
- Append new_lines to remaining (uncommitted) content

### Cycle 2.4: CLI integration — step_reached update between write phases

**RED:** Test full CLI flow: state file updated to `step_reached="diagnostics"` after successful writes.

```python
def test_handoff_cli_updates_step_reached_after_writes(tmp_path):
    # Set up stdin with valid handoff input
    # Invoke handoff_cmd
    # Read state file mid-pipeline (or check it exists with diagnostics step)
    # Tricky to test mid-pipeline — alternative: mock write_completed to fail
    # Verify state file has step_reached="write_session" (not yet advanced)
```

**GREEN:** Wire step_reached updates in cli.py between overwrite_status and clear_state.

## Phase 3: Minor fixes (type: general)

Batch the non-behavioral minor fixes. Each is a targeted edit with verification.

### Step 3.1: Code minors (m-2, m-3, m-5, m-7)

**m-2** `commit_pipeline.py:276-282` — Missing submodule message exit code: change exit 1 → exit 2 (S-3: malformed input).
**m-3** `commit_pipeline.py:263-267` — Redundant missing-message check: remove or change to exit 2.
**m-5** `commit_gate.py:51-68` — `_dirty_files` uses `-u` flag: document or limit scope.
**m-7** `render.py:105-127` — `_build_dependency_edges` substring matching: add comment documenting conservative bias.

**Verify:** `just precommit`

### Step 3.2: Remaining code minors (m-1, m-4, m-6, m-8, m-9, m-10)

**m-1** `task_parsing.py:21` — `WORKTREE_MARKER_PATTERN` backtick requirement: document or relax.
**m-4** `commit_pipeline.py:193-213` — `_strip_hints` ambiguous continuation: add clarifying comment.
**m-6** `handoff/cli.py:60-61` — `git_changes()` unconditional: acceptable, add comment.
**m-8** `status/cli.py:67` — `list_plans(Path("plans"))` relative path: acceptable, add comment.
**m-9** `commit_pipeline.py:22-37,40-55` — "Patchable" comment: update to clarify monkeypatch usage.
**m-10** `commit_gate.py:31-48` — `_git_output` duplication: add TODO or extract shared helper with `cwd`.

**Verify:** `just precommit`

### Step 3.3: Test minors (m-11 through m-15)

**m-11** `test_session_status.py:280-298` — Move `SESSION_FIXTURE` before first usage.
**m-12** `test_session_commit_pipeline.py:121-134` — Improve assertion strings (carried from RC10).
**m-13** `test_planstate_aggregation.py:102-197` — Split positive/negative paths.
**m-14** `test_session_handoff.py:235-261` — Deduplicate near-redundant tests.
**m-15** `test_session_commit_pipeline.py:157-212` — Consolidate submodule setup helpers.

**Verify:** `just test`

## Execution Notes

- Phase 1 before Phase 2: step_reached is prerequisite for non-idempotent writes
- H-2 requires a real git repo in tests (e2e pattern: tmp_path with git init + commits)
- `_detect_write_mode()` needs subprocess call to `git diff` — use `_git()` helper from `git.py`
- Phase 3 minors are independent of Phase 1/2 — could run in parallel but sequential is fine for Tier 2
