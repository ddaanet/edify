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

**Why it fails:** No `session/commit/pipeline.py`

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_parent_only -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit/pipeline.py`

**Behavior:**
- `CommitResult` dataclass: `success: bool`, `output: str`
- `commit_pipeline(input: CommitInput) -> CommitResult`
- Stage files via `git add`
- Run `just precommit` (validation level dispatch added in Cycle 6.4)
- Run vet check via `vet_check(input.files)` (option-gating added in Cycle 6.4)
- Commit with message from `CommitInput.message`
- Return raw git commit output on success

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Create with `CommitResult`, `commit_pipeline()`

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
- File: `src/claudeutils/session/commit/pipeline.py`
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
- Pass `amend=True` to `validate_files()` — enables HEAD file acceptance
- Submodule amend: `_git("-C", path, "commit", "--amend", "-m", message)` then re-stage pointer
- Message always provided (never `--no-edit`)

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Add amend flag handling throughout pipeline

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
- File: `src/claudeutils/session/commit/pipeline.py`
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
- For failures: separate formatting per gate type already produces structured markdown

**Changes:**
- File: `src/claudeutils/session/commit/pipeline.py`
  Action: Extract `format_commit_output()` from pipeline logic

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 6.6: CLI wiring — `claudeutils _session commit`

**RED Phase:**

**Test:** `test_session_commit_cli_success`, `test_session_commit_cli_validation_error`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- CliRunner with valid commit markdown on stdin (real git repo via `tmp_path`, file staged) → exit 0, stdout contains `[branch hash] message` format line
- CliRunner with files that have no changes → exit 2, stdout contains `**Error:**` and `STOP:`
- CliRunner with empty stdin → exit 2, stdout contains `**Error:**` and references missing required section

**Expected failure:** Command not registered

**Why it fails:** No commit subcommand

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_session_commit_cli_success -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit/cli.py` with Click command

**Behavior:**
- `@click.command(name="commit")` function
- Read all stdin → `parse_commit_input()`
- Call `commit_pipeline(input)` → `CommitResult`
- Output `result.output` to stdout
- Exit 0 on success, 1 on pipeline error, 2 on input validation error

**Changes:**
- File: `src/claudeutils/session/commit/cli.py`
  Action: Create with `commit` Click command
- File: `src/claudeutils/session/cli.py`
  Action: Import and register the commit command with the session group (same pattern as worktree subcommand registration in main cli.py)

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit_pipeline.py -v`
**Verify no regression:** `just precommit`

---

**Phase 6 Checkpoint:** `just precommit` — commit subcommand fully functional.
