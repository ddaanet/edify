### Phase 0: Task name constraints (type: tdd)

**Scope:** FR-1, FR-2 — validation infrastructure
**Complexity:** Low
**Model:** haiku

---

## Cycle 0.1: `validate_task_name_format()` valid names

**RED Phase:**

**Test:** `test_validate_task_name_format_valid`
**Assertions:**
- `validate_task_name_format("Build docs")` returns empty list
- `validate_task_name_format("Fix bug-123")` returns empty list
- `validate_task_name_format("Add v2.0 support")` returns empty list
- `validate_task_name_format("a")` returns empty list (minimum length)
- `validate_task_name_format("12345678901234567890ABCDE")` returns empty list (exactly 25 chars)

**Expected failure:** `ImportError: cannot import name 'validate_task_name_format' from 'claudeutils.validation.tasks'`

**Why it fails:** Function does not exist in module

**Verify RED:** `pytest tests/test_validation_tasks.py::test_validate_task_name_format_valid -v`

**GREEN Phase:**

**Implementation:** Add `validate_task_name_format()` function to `src/claudeutils/validation/tasks.py`

**Behavior:**
- Accept string input `name`
- Return `list[str]` (empty list = valid)
- For valid names, return empty list
- No rejection logic yet — character and length checks added in cycles 0.2 and 0.3

**Approach:** Minimal stub that returns `[]` for all inputs. Tests only assert valid names return empty list.

**Changes:**
- File: `src/claudeutils/validation/tasks.py`
  Action: Add `validate_task_name_format()` function after TASK_PATTERN definition
  Location hint: Before `extract_task_names()` function

**Verify GREEN:** `pytest tests/test_validation_tasks.py::test_validate_task_name_format_valid -v`
**Verify no regression:** `pytest tests/test_validation_tasks.py -v`

---

## Cycle 0.2: `validate_task_name_format()` invalid characters rejected

**RED Phase:**

**Test:** `test_validate_task_name_format_invalid_chars`
**Assertions:**
- `validate_task_name_format("task_name")` returns list containing "forbidden character '_'"
- `validate_task_name_format("task@host")` returns list containing "forbidden character '@'"
- `validate_task_name_format("task/path")` returns list containing "forbidden character '/'"
- `validate_task_name_format("task:colon")` returns list containing "forbidden character ':'"
- Each error message includes the forbidden character

**Expected failure:** Assertions fail — function returns empty list for invalid characters

**Why it fails:** Cycle 0.1 returns `[]` for all inputs — no character validation

**Verify RED:** `pytest tests/test_validation_tasks.py::test_validate_task_name_format_invalid_chars -v`

**GREEN Phase:**

**Implementation:** Add character set validation using regex

**Behavior:**
- When name contains characters outside `[a-zA-Z0-9 .\-]`, return list with error message
- Error format: `"contains forbidden character 'X'"` where X is the first forbidden character found
- Identify forbidden character by testing regex match failure

**Approach:** Use `re.fullmatch(r"[a-zA-Z0-9 .\-]+", name)` — if None, iterate to find first forbidden char and return error list

**Changes:**
- File: `src/claudeutils/validation/tasks.py`
  Action: Update `validate_task_name_format()` to detect and report forbidden characters
  Location hint: Inside function body, before length check

**Verify GREEN:** `pytest tests/test_validation_tasks.py::test_validate_task_name_format_invalid_chars -v`
**Verify no regression:** `pytest tests/test_validation_tasks.py -v`

---

## Cycle 0.3: `validate_task_name_format()` length constraint

**RED Phase:**

**Test:** `test_validate_task_name_format_length`
**Assertions:**
- `validate_task_name_format("12345678901234567890ABCDEF")` (26 chars) returns list containing "exceeds 25 character limit (26 chars)"
- `validate_task_name_format("This is a very long task name")` (30 chars) returns list containing "exceeds 25 character limit (30 chars)"
- `validate_task_name_format("")` returns list containing "empty or whitespace-only"
- `validate_task_name_format("   ")` returns list containing "empty or whitespace-only"

**Expected failure:** Assertions fail — function does not check length or emptiness

**Why it fails:** Length and empty/whitespace validation not implemented

**Verify RED:** `pytest tests/test_validation_tasks.py::test_validate_task_name_format_length -v`

**GREEN Phase:**

**Implementation:** Add length and emptiness validation

**Behavior:**
- When `len(name) > 25`, return error message with actual length
- When `name.strip()` is empty, return error message
- Error formats: `"exceeds 25 character limit (N chars)"` and `"empty or whitespace-only"`

**Approach:** Check `len(name)` after character validation, check `name.strip()` before character validation

**Changes:**
- File: `src/claudeutils/validation/tasks.py`
  Action: Add length check and empty/whitespace check to `validate_task_name_format()`
  Location hint: Empty check first, character check second, length check last

**Verify GREEN:** `pytest tests/test_validation_tasks.py::test_validate_task_name_format_length -v`
**Verify no regression:** `pytest tests/test_validation_tasks.py -v`

---

## Cycle 0.4: `derive_slug()` fail-fast with format validation

**Prerequisite:** Read `src/claudeutils/worktree/cli.py:17-24` — understand current `derive_slug()` implementation

**RED Phase:**

**Test:** `test_derive_slug_validates_format`
**Assertions:**
- `derive_slug("task_name")` raises `ValueError` with message containing "forbidden character '_'"
- `derive_slug("task@host")` raises `ValueError` with message containing "forbidden character '@'"
- `derive_slug("This is a very long task name that exceeds limit")` raises `ValueError` with message containing "exceeds 25 character limit"
- `derive_slug("")` raises `ValueError` with message containing "empty"

**Expected failure:** `ValueError` not raised — function transforms invalid names into slugs

**Why it fails:** No validation call before transformation

**Verify RED:** `pytest tests/test_worktree_utils.py::test_derive_slug_validates_format -v`

**GREEN Phase:**

**Implementation:** Add `validate_task_name_format()` call to `derive_slug()` before transformation

**Behavior:**
- Call `validate_task_name_format(task_name)` before slug transformation
- If errors returned, raise `ValueError` with first error message
- Import validation function from `claudeutils.validation.tasks`

**Approach:** Call validation early, raise if errors exist, then proceed with existing transformation logic

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Import `validate_task_name_format` and add validation call at start of `derive_slug()`
  Location hint: After empty check, before `re.sub()` transformation

**Verify GREEN:** `pytest tests/test_worktree_utils.py::test_derive_slug_validates_format -v`
**Verify no regression:** `pytest tests/test_worktree_utils.py -v`

---

## Cycle 0.5: `derive_slug()` lossless transformation `[REGRESSION]`

**RED Phase:**

**Test:** `test_derive_slug_lossless`
**Assertions:**
- `derive_slug("Build docs")` returns `"build-docs"`
- `derive_slug("Fix bug-123")` returns `"fix-bug-123"`
- `derive_slug("Add v2.0 support")` returns `"add-v2-0-support"`
- `derive_slug("a")` returns `"a"`
- `derive_slug("Test   multiple   spaces")` returns `"test-multiple-spaces"` (collapsing multiple spaces into single hyphen)

**Expected:** Tests pass (regression — constrained names already produce correct slugs with current implementation)

**Why it passes:** Valid task names (≤25 chars) produce slugs well under `max_length=30`. No truncation occurs.

**Verify RED:** `pytest tests/test_worktree_utils.py::test_derive_slug_lossless -v` — expect PASS

**GREEN Phase:**

**Implementation:** Remove `max_length` parameter and truncation logic (cleanup — validation now enforces length constraints)

**Behavior:**
- Remove `max_length` parameter from function signature
- Remove `[:max_length]` slice from transformation
- Keep `task_name.lower()` and `re.sub(r"[^a-z0-9]+", "-", ...)` transformation
- Keep `.strip("-")` and `.rstrip("-")` cleanup

**Approach:** Delete parameter, delete slice. Tests still pass — this is signature cleanup, not behavior change.

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Remove `max_length: int = 30` parameter and `[:max_length]` from transformation
  Location hint: Function signature line 17, transformation line 23

**Design Decision:** `validate_task_name_format()` ensures names ≤25 chars. After transformation (spaces→hyphens), slugs remain short. `max_length` is dead code — remove it.

**Verify GREEN:** `pytest tests/test_worktree_utils.py::test_derive_slug_lossless -v`
**Verify no regression:** `pytest tests/test_worktree_utils.py -v`

---

## Cycle 0.6: Precommit integration in `validate()` function

**Prerequisite:** Read `src/claudeutils/validation/tasks.py:246-309` — understand existing `validate()` function structure

**RED Phase:**

**Test:** `test_validate_task_name_format_integration`
**Assertions:**
- Create `tmp_path / "agents/session.md"` with task containing underscore: `- [ ] **Fix_bug** — details`
- Call `validate(str(tmp_path / "agents/session.md"), str(tmp_path / "agents/learnings.md"), tmp_path)`
- Assert returned error list contains message matching `"Fix_bug"` and `"forbidden character '_'"`
- Create session.md with 26-character task name
- Call `validate()` again
- Assert returned error list contains message matching `"exceeds 25 character limit"`

**Expected failure:** Assertions fail — format validation not called in `validate()` function

**Why it fails:** No integration of `validate_task_name_format()` into existing validator

**Verify RED:** `pytest tests/test_validation_tasks.py::test_validate_task_name_format_integration -v`

**GREEN Phase:**

**Implementation:** Integrate `validate_task_name_format()` into `validate()` function

**Behavior:**
- After extracting task names with `extract_task_names()`, call `validate_task_name_format()` on each task name
- Append format errors to errors list with line number
- Error format: `"Task '{name}' (line {n}): {error_message}"` where error_message is from `validate_task_name_format()`
- Run format validation alongside existing uniqueness/disjointness checks

**Approach:** Loop over extracted task names, call validation function, format errors with line numbers

**Changes:**
- File: `src/claudeutils/validation/tasks.py`
  Action: Add format validation loop in `validate()` function after task extraction
  Location hint: After `task_names = extract_task_names(session_lines)`, before uniqueness check

**Design Decision:** Defense in depth — `derive_slug()` validates at creation time (fail-fast), precommit validator catches manual edits that bypass CLI.

**Verify GREEN:** `pytest tests/test_validation_tasks.py::test_validate_task_name_format_integration -v`
**Verify no regression:** `pytest tests/test_validation_tasks.py -v`

---

## Checkpoint: Phase 0

**Type:** Full (Fix + Vet + Functional)

**Fix:**
1. Run `just dev`
2. If failures: delegate to sonnet quiet-task with report path `plans/worktree-fixes/reports/phase-0-fix.md`
3. Read report, apply fixes
4. Commit when passing

**Vet:**
1. Delegate to `vet-fix-agent` with execution context:
   - Scope IN: `validate_task_name_format()` in validation/tasks.py, `derive_slug()` changes in cli.py, format validation integration in validation/tasks.py
   - Scope OUT: Session merge logic (Phase 1), task movement automation (Phase 2)
   - Changed files: `src/claudeutils/validation/tasks.py`, `src/claudeutils/worktree/cli.py`, `tests/test_validation_tasks.py`, `tests/test_worktree_utils.py`
   - Requirements: FR-1 (task name constraints, lossless slugs), FR-2 (precommit validation)
2. Read report path from vet-fix-agent return value
3. Grep report for UNFIXABLE
4. If UNFIXABLE found: STOP, escalate to user
5. If all fixed: commit

**Functional:**
1. Sonnet reviews implementations against design
2. Check: Are validators actually enforcing constraints? Is `derive_slug()` truly lossless?
3. If stubs/constants found: STOP, report which need real behavior
4. If all functional: proceed to Phase 1
