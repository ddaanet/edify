# Runbook: Fix handoff-cli round 3 (Moderate items)

**Tier:** 2 (Lightweight Delegation)
**Phase type:** tdd
**Model:** sonnet

## Scope

Three findings from deliverable-review.md RC3:
- **M-pre-1:** Parallel detection ignores Blockers/Gotchas — `detect_parallel` receives `[]` hardcoded
- **M-pre-2:** Stale vet output lacks file-level detail — returns time delta, not per-file info
- **m-pre-3:** Completed parser strips blank lines between `###` groups

## Recall Context

Resolve at execution time: `plans/handoff-cli-tool/recall-artifact.md`

Key entries for delegation:
- `when testing CLI tools` — Click CliRunner, in-process
- `when preferring e2e over mocked subprocess` — real git repos via tmp_path
- `when writing red phase assertions` — behavioral not structural

## Phase 1: Blocker detection wiring (type: tdd)

### Cycle 1.1: Parser extracts blockers for status

**Prerequisite:** Read `src/claudeutils/worktree/session.py:84-117` — `extract_blockers()` returns `list[list[str]]`. Read `src/claudeutils/session/parse.py` — `SessionData` dataclass, `parse_session()`.

**RED Phase:**

**Test:** `test_parse_session_extracts_blockers` in `tests/test_session_parser.py`
**Assertions:**
- Session fixture with `## Blockers / Gotchas` section containing two bullet items
- `data.blockers` is a list of length 2
- First blocker group's first element contains the expected bullet text

**Expected failure:** `AttributeError` — `SessionData` has no `blockers` field

**Why it fails:** `SessionData` doesn't include blockers; `parse_session` doesn't call `extract_blockers`

**Verify RED:** `pytest tests/test_session_parser.py::test_parse_session_extracts_blockers -v`

---

**GREEN Phase:**

**Implementation:** Add `blockers` field to `SessionData`, wire `extract_blockers` into `parse_session`.

**Behavior:**
- `SessionData` gains `blockers: list[list[str]]` field (default `[]`)
- `parse_session` calls `extract_blockers(content)` and passes result to `SessionData`

**Changes:**
- File: `src/claudeutils/session/parse.py`
  Action: Add import of `extract_blockers` from `claudeutils.worktree.session`. Add `blockers` field to `SessionData`. Pass `blockers=extract_blockers(content)` in `parse_session`.

**Verify GREEN:** `just green`

### Cycle 1.2: Status CLI wires blockers to detect_parallel

**Prerequisite:** Read `src/claudeutils/session/status/cli.py:98-99` — hardcoded `[]`. Read `src/claudeutils/session/status/render.py:134-160` — `detect_parallel` signature.

**RED Phase:**

**Test:** `test_status_parallel_uses_blockers` in `tests/test_status_rework.py`
**Assertions:**
- Session fixture with two tasks (different plan dirs) and `## Blockers / Gotchas` section mentioning both task names as dependent
- CLI invocation via CliRunner with `_status` command
- Output does NOT contain "Parallel" (blocker creates dependency between the two tasks)
- Exit code 0

**Expected failure:** `AssertionError` — output contains "Parallel" because blockers are ignored (passed as `[]`)

**Why it fails:** `cli.py:99` passes `[]` instead of `data.blockers` to `detect_parallel`

**Verify RED:** `pytest tests/test_status_rework.py::test_status_parallel_uses_blockers -v`

---

**GREEN Phase:**

**Implementation:** Wire `data.blockers` from parsed session into `detect_parallel` call.

**Behavior:**
- Replace `detect_parallel(data.in_tree_tasks, [])` with `detect_parallel(data.in_tree_tasks, data.blockers)`

**Changes:**
- File: `src/claudeutils/session/status/cli.py`
  Action: Change line 99 from `[]` to `data.blockers`

**Verify GREEN:** `just green`

## Phase 2: Vet stale output file detail (type: tdd)

### Cycle 2.1: VetResult includes per-file detail

**Prerequisite:** Read `src/claudeutils/session/commit_gate.py:93-168` — `VetResult` dataclass and `vet_check()`. Read `plans/handoff-cli-tool/outline.md:202-207` — design spec stale output format.

**RED Phase:**

**Test:** `test_vet_stale_includes_file_detail` in `tests/test_session_commit_validation.py`
**Assertions:**
- Set up tmp_path with pyproject.toml containing `require-review = ["src/**/*.py"]`
- Create `plans/test/reports/review.md` with mtime in the past
- Create `src/foo.py` with mtime newer than the report
- Call `vet_check(["src/foo.py"])`
- `result.passed` is False
- `result.reason` is "stale"
- `result.stale_info` contains `src/foo.py` (the newest source file name)
- `result.stale_info` contains the report file name

**Expected failure:** `AssertionError` — `stale_info` contains only time delta string like `"Source newer than reports by 5s"`, not file names

**Why it fails:** Current implementation computes `_newest_mtime` but doesn't track which file is newest

**Verify RED:** `pytest tests/test_session_commit_validation.py::test_vet_stale_includes_file_detail -v`

---

**GREEN Phase:**

**Implementation:** Track newest source file and newest report file, include paths in `stale_info`.

**Behavior:**
- Replace `_newest_mtime` calls with a helper that returns both mtime and path
- Format `stale_info` as `"Newest change: {path} ({timestamp})\nNewest report: {report_path} ({timestamp})"` matching design spec

**Changes:**
- File: `src/claudeutils/session/commit_gate.py`
  Action: Add helper `_newest_file(files) -> tuple[float, Path]` returning (mtime, path). Modify `vet_check` to use it, format stale_info with file paths and human-readable timestamps.

**Verify GREEN:** `just green`

## Phase 3: Completed parser blank line preservation (type: tdd)

### Cycle 3.1: parse_completed_section preserves inter-group blank lines

**Prerequisite:** Read `src/claudeutils/session/parse.py:70-81` — `parse_completed_section`. Read `src/claudeutils/worktree/session.py:120-130` — `find_section_bounds`.

**RED Phase:**

**Test:** `test_parse_completed_preserves_blank_lines` in `tests/test_session_parser.py`
**Assertions:**
- Content with `## Completed This Session` containing two `### ` sub-groups separated by a blank line:
  ```
  ### Group A
  - Item 1

  ### Group B
  - Item 2
  ```
- `parse_completed_section(content)` returns a list where at least one element is `""` (blank line between groups)
- The blank line appears between the "Item 1" line and the "### Group B" line
- Both `### Group A` and `### Group B` are present in the result

**Expected failure:** `AssertionError` — result contains no empty strings because `if line.strip()` filters them out

**Why it fails:** Line 81 filters blank lines: `[line for line in section_lines if line.strip()]`

**Verify RED:** `pytest tests/test_session_parser.py::test_parse_completed_preserves_blank_lines -v`

---

**GREEN Phase:**

**Implementation:** Preserve blank lines within the section, only strip trailing blank lines.

**Behavior:**
- Keep all lines from the section (including blank lines between groups)
- Strip only leading/trailing blank lines from the section

**Changes:**
- File: `src/claudeutils/session/parse.py`
  Action: Replace list comprehension at line 81 with logic that preserves internal blank lines but strips leading/trailing empties. Use `.strip()` only for the overall section boundaries, not individual lines.

**Verify GREEN:** `just green`

### Cycle 3.2: Handoff input parser preserves blank lines

**Prerequisite:** Read `src/claudeutils/session/handoff/parse.py:47-53` — same blank-line stripping in `parse_handoff_input`.

**RED Phase:**

**Test:** `test_parse_handoff_preserves_blank_lines` in `tests/test_session_handoff.py`
**Assertions:**
- Handoff input text with `**Status:**` line and `## Completed This Session` containing two sub-groups with blank line between them
- `parse_handoff_input(text).completed_lines` contains at least one `""` element
- Both sub-group headings present in result

**Expected failure:** `AssertionError` — blank lines stripped by `if line.strip()` filter at line 52

**Why it fails:** `parse_handoff_input` only appends lines where `line.strip()` is truthy

**Verify RED:** `pytest tests/test_session_handoff.py::test_parse_handoff_preserves_blank_lines -v`

---

**GREEN Phase:**

**Implementation:** Preserve blank lines in completed section parsing.

**Behavior:**
- Append all lines from completed section (including blank)
- Strip only trailing blank lines

**Changes:**
- File: `src/claudeutils/session/handoff/parse.py`
  Action: Replace `if line.strip(): completed.append(line)` with unconditional append, then strip trailing empties after the loop.

**Verify GREEN:** `just green`

## Consolidation Self-Check

- Cycles 1.1 and 1.2 are sequential (1.2 depends on 1.1's `blockers` field)
- Cycle 2.1 is independent of Phase 1 and Phase 3
- Cycles 3.1 and 3.2 address the same bug in two parsers — both needed, no subset overlap
- No cycle's assertions are a subset of another's — each tests distinct behavior in distinct code paths
