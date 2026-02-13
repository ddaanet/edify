# Phase 4: Focused Session Generation

**Complexity:** Medium (3 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** Parse session.md and generate focused content for worktree — extract task, filter relevant context.

**Dependencies:** None

---

## Cycle 4.1: Task extraction by name — with metadata and formatting

**Objective:** Extract task block from session.md by matching task name.

**Prerequisite:** Read `agents/session.md` lines 1-100 — understand task block format with metadata (task name, command, model, restart flag) and continuation lines.

**RED Phase:**

**Test:** `test_focus_session_task_extraction`
**Assertions:**
- Given session.md with task `- [ ] **Implement feature X** — \`/plan-adhoc\` | sonnet`
- `focus_session("Implement feature X", session_path)` returns string containing task line
- Returned string includes task metadata (command, model)
- Returned string includes H1 header: `# Session: Worktree — Implement feature X`
- Returned string includes status line: `**Status:** Focused worktree for parallel execution.`
- Returned string has Pending Tasks section with single extracted task
- Task checkbox preserved: `- [ ]` format maintained

**Expected failure:** NameError: function `focus_session` not defined

**Why it fails:** Function doesn't exist yet

**Verify RED:** `pytest tests/test_worktree_cli.py::test_focus_session_task_extraction -v`

---

**GREEN Phase:**

**Implementation:** Create function to parse session.md and extract matching task

**Behavior:**
- Read session.md file content
- Parse to find task by matching `**<task-name>**` pattern
- Extract full task line (including metadata after task name)
- Generate focused session with:
  - H1: `# Session: Worktree — <task-name>`
  - Status: `**Status:** Focused worktree for parallel execution.`
  - Pending Tasks section with single extracted task
- Return formatted string (not write to file)

**Approach:** Regex to find task line, string formatting to build focused session structure

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add new function `focus_session(task_name: str, session_md_path: str | Path) -> str` at module level
  Location hint: After `derive_slug()` function, before command definitions
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement task extraction — read file, regex match for `- [ ] **<task-name>**`, extract line
  Location hint: Function body uses `Path.read_text()`, `re.search()` or `re.findall()`, string formatting for output

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_focus_session_task_extraction -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 tests still pass

---

## Cycle 4.2: Section filtering — Blockers and Reference Files

**Objective:** Include only blockers/gotchas and reference file entries relevant to the extracted task.

**Prerequisite:** Read `agents/session.md` Blockers/Gotchas and Reference Files sections — understand entry format and how entries reference tasks or plan directories.

**RED Phase:**

**Test:** `test_focus_session_section_filtering`
**Assertions:**
- Given session.md with Blockers/Gotchas section containing:
  - Entry mentioning task name directly
  - Entry mentioning task's plan directory (e.g., `plans/feature-x/`)
  - Entry NOT related to task
- And Reference Files section containing:
  - Entry relevant to task (mentions task name or plan directory)
  - Entry NOT relevant to task
- `focus_session("task-name", session_path)` returns string containing only relevant blocker and reference entries
- Unrelated entries NOT included in output
- Blockers section header present only if relevant entries exist
- Reference Files section header present only if relevant entries exist
- If no relevant blockers: Blockers section omitted entirely
- If no relevant references: Reference Files section omitted entirely

**Expected failure:** AssertionError: all entries included (no filtering) or sections always included even when empty

**Why it fails:** Function doesn't filter blockers or references yet, includes everything or nothing

**Verify RED:** `pytest tests/test_worktree_cli.py::test_focus_session_section_filtering -v`

---

**GREEN Phase:**

**Implementation:** Add section filtering logic to `focus_session()` function

**Behavior:**
- Parse Blockers/Gotchas section from session.md
- Parse Reference Files section from session.md
- For each entry in both sections, check if it mentions:
  - Task name (exact match or substring)
  - Plan directory associated with task (if task has plan metadata)
- Include only matching entries in focused session
- Omit each section entirely if no relevant entries

**Approach:** Section parsing, relevance checking per entry, conditional section inclusion. Same filtering logic applies to both Blockers and References sections.

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add section parsing to `focus_session()` function for both Blockers and References
  Location hint: After task extraction, before building output string
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement relevance check — search for task name or plan directory in entry text
  Location hint: Shared filter function applied to both sections
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditionally include each section in output (only if filtered list non-empty)
  Location hint: String formatting with conditional sections

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_focus_session_section_filtering -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_focus_session_task_extraction -v`
- Cycle 4.1 test still passes

---

## Cycle 4.3: Missing task error handling

**Objective:** Raise clear error when task name doesn't exist in session.md.

**RED Phase:**

**Test:** `test_focus_session_missing_task`
**Assertions:**
- Given session.md without task named "nonexistent-task"
- `focus_session("nonexistent-task", session_path)` raises ValueError
- Error message contains task name: "Task 'nonexistent-task' not found in session.md"
- Error message is actionable (helps user understand what went wrong)

**Expected failure:** No error raised (returns empty string or None) or wrong exception type

**Why it fails:** Function doesn't validate task existence before processing

**Verify RED:** `pytest tests/test_worktree_cli.py::test_focus_session_missing_task -v`

---

**GREEN Phase:**

**Implementation:** Add task existence validation to `focus_session()` function

**Behavior:**
- After parsing session.md, check if task was found
- If task extraction returns None or empty: raise ValueError with clear message
- Message includes task name for debugging
- Validation happens before any section filtering (fail fast)

**Approach:** Check task extraction result, raise ValueError if None/empty with f-string message

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add task validation check in `focus_session()` function
  Location hint: After task extraction attempt, before blocker/reference filtering
- File: `src/claudeutils/worktree/cli.py`
  Action: Raise ValueError if task not found, with message including task name
  Location hint: Conditional check on task extraction result

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_focus_session_missing_task -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 4 tests still pass

---
