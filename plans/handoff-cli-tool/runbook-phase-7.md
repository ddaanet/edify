### Phase 7: Integration tests (type: tdd, model: sonnet)

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

## Cycle 7.1: Status integration

**RED Phase:**

**Test:** `test_status_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Read `src/claudeutils/session/status/cli.py` — understand full pipeline from CLI entry

**Assertions:**
- Create `tmp_path` git repo with:
  - `agents/session.md` (realistic fixture with in-tree tasks, worktree tasks, reference files)
  - `plans/parser/` directory with design artifacts (triggers plan state inference)
  - At least one plan directory not referenced by any task (triggers unscheduled detection)
- CliRunner invokes `_session status`
- Output contains `Next:` section with correct task name and command
- Output contains `Pending:` section with plan status
- Output contains `Worktree:` section with slug markers
- Output contains `Unscheduled Plans:` section with orphan plan
- Exit code 0

**Expected failure:** Integration path not fully wired — individual components may work but full pipeline from CLI to output untested

**Why it fails:** End-to-end path through CliRunner exercises wiring gaps

**Verify RED:** `pytest tests/test_session_integration.py::test_status_integration -v`

---

**GREEN Phase:**

**Implementation:** Fix any wiring gaps discovered by integration test

**Behavior:**
- The test exercises: CLI command → parse_session() → render functions → formatted output
- Fixes are targeted at wiring issues (import paths, function signatures, data threading)
- No new production code expected — all components built in Phases 2-3

**Changes:**
- Fix any import or wiring issues discovered
- May require adjusting function signatures for data threading

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py::test_status_integration -v`
**Verify no regression:** `just precommit`

---

## Cycle 7.2: Handoff integration

**RED Phase:**

**Test:** `test_handoff_fresh_integration`, `test_handoff_resume_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Read `src/claudeutils/session/handoff/cli.py` — understand full pipeline

**Assertions — fresh mode:**
- Create `tmp_path` git repo with `agents/session.md` (committed initial state)
- CliRunner invokes `_session handoff` with stdin:
  ```
  **Status:** Phase 1 complete.

  ## Completed This Session

  **Infrastructure work:**
  - Extracted git helpers
  ```
- After invocation:
  - `agents/session.md` status line updated to "Phase 1 complete."
  - Completed section contains "Infrastructure work:" and "Extracted git helpers"
  - Output contains diagnostics (precommit result)
  - No state file remains (cleaned up on success)
  - Exit code 0

**Assertions — resume mode:**
- Create state file at `tmp/.handoff-state.json` with `step_reached: "precommit"`
- CliRunner invokes `_session handoff` without stdin
- Pipeline resumes from precommit step (skips write steps)
- Exit code 0

**Expected failure:** End-to-end pipeline wiring gaps

**Why it fails:** Fresh/resume modes exercise different pipeline paths

**Verify RED:** `pytest tests/test_session_integration.py::test_handoff_fresh_integration -v`

---

**GREEN Phase:**

**Implementation:** Fix wiring issues discovered by integration test

**Behavior:**
- Fresh mode exercises: stdin → parse → state cache → status overwrite → completed write → precommit → diagnostics → cleanup
- Resume mode exercises: state load → skip to step → precommit → diagnostics → cleanup
- Fixes targeted at data threading and error propagation

**Changes:**
- Fix any discovered wiring issues

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 7.3: Commit integration

**RED Phase:**

**Test:** `test_commit_parent_integration`, `test_commit_submodule_integration`, `test_commit_amend_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Shared `tmp_path` fixture creating git repo with submodule (from conftest)

**Assertions — parent-only:**
- Create modified file in `tmp_path` repo (uncommitted change, appears in `git status --porcelain`)
- CliRunner invokes `_session commit` with stdin specifying the file + message
- Git log shows new commit with expected message
- Output contains `[branch hash] message` format
- Exit code 0

**Assertions — submodule:**
- Create dirty file in submodule directory
- CliRunner with stdin specifying submodule file, submodule message, and parent message
- Submodule git log shows new commit
- Parent git log shows new commit (with submodule pointer update)
- Output contains `<path>:` labeled submodule output followed by parent output
- Exit code 0

**Assertions — amend:**
- Create initial commit, then create new dirty file
- CliRunner with `amend` option → amend the previous commit
- Git log shows only one commit (amended, not new)
- Output contains `Date:` line (amend output format)
- Exit code 0

**Expected failure:** End-to-end commit pipeline wiring

**Why it fails:** Full pipeline through real git operations

**Verify RED:** `pytest tests/test_session_integration.py::test_commit_parent_integration -v`

---

**GREEN Phase:**

**Implementation:** Fix wiring issues in commit pipeline

**Behavior:**
- Parent-only: stdin → parse → validate → precommit → stage → commit → output
- Submodule: partition → submodule commit → pointer stage → parent commit
- Amend: same pipeline with `--amend` flag propagation

**Changes:**
- Fix any discovered wiring issues

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_integration.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 7.4: Cross-subcommand — handoff then status

**RED Phase:**

**Test:** `test_handoff_then_status`
**File:** `tests/test_session_integration.py`

**Assertions:**
- Create `tmp_path` git repo with `agents/session.md`
- CliRunner invokes `_session handoff` with stdin (updates session.md)
- Then CliRunner invokes `_session status` (reads updated session.md)
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
