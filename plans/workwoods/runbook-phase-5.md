### Phase 5: Merge Strategies + Skill Update (type: mixed)

**Purpose:** Implement per-section session.md merge strategies and update worktree skill for bidirectional merge.

**Scope (TDD):**
- `src/claudeutils/worktree/merge.py` - Per-section merge strategies
- `src/claudeutils/worktree/session.py` - Blockers extraction
- `tests/test_worktree_merge_sections.py` - Merge strategy tests

**Scope (General):**
- `agent-core/skills/worktree/SKILL.md` - Mode C no auto-rm
- `agent-core/fragments/execute-rule.md` - STATUS uses planstate

**Dependencies:** Phase 1 (execute-rule.md uses planstate), worktree-merge-data-loss deployment

**Execution Model:** Sonnet (TDD), Opus (skill edits per design directive)

**Estimated Complexity:** High (merge refactor + coordinated skill edits)

**Weak Orchestrator Metadata:**
- Total Steps: 11 (8 TDD cycles + 3 general steps)
- Restart required: No

**CRITICAL: Verify worktree-merge-data-loss deployment before starting this phase.**

---

## TDD Portion (Cycles 5.1-5.8)

### Cycle 5.1: Section identification via find_section_bounds()

**Prerequisite:** Read current _resolve_session_md_conflict() implementation (merge.py lines 58-113) and find_section_bounds() (session.py lines 85-115).

**RED Phase:**

**Test:** `test_section_identification`
**Assertions:**
- find_section_bounds(content, "Pending Tasks") returns tuple (2, 8) for content with Pending Tasks at line 2, next section at line 8
- find_section_bounds(content, "Worktree Tasks") returns tuple (9, 14) for section at line 9
- find_section_bounds(content, "Blockers / Gotchas") returns tuple (15, 20) for section with slash in name
- find_section_bounds(content, "Nonexistent") returns None
- Section at EOF: returns (N, len(lines)) where N is section start line

**Expected failure:** Test passes (find_section_bounds already exists) OR new test reveals edge cases

**Why it might pass:** find_section_bounds() already implemented in Phase 3 worktree-update

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_section_identification -v`

**GREEN Phase:**

**Implementation:** Use existing find_section_bounds(), add test coverage for merge use cases

**Behavior:**
- Verify find_section_bounds() works with all section names from D-5 table
- Test edge cases: sections at EOF, consecutive sections, missing sections
- Confirm existing implementation handles slash in "Blockers / Gotchas"

**Approach:** Test-only cycle if function works; fix if edge cases fail

**Changes:**
- File: `tests/test_worktree_merge_sections.py`
  Action: Create tests for all D-5 section names
  Location hint: New file, test each section type

- File: `src/claudeutils/worktree/session.py` (if needed)
  Action: Fix edge cases found by tests
  Location hint: find_section_bounds() function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_section_identification -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---

### Cycle 5.2: Status line strategy (keep ours)

**RED Phase:**

**Test:** `test_status_line_squash_strategy`
**Assertions:**
- Ours: `# Session Handoff: 2026-02-16` + `**Status:** Main work`
- Theirs: `# Session Handoff: 2026-02-15` + `**Status:** Worktree work`
- Result: Ours status line preserved, theirs discarded

**Expected failure:** Theirs status line appears in merged result

**Why it fails:** Per-section strategy not implemented, still using keep-ours for entire file

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_status_line_squash_strategy -v`

**GREEN Phase:**

**Implementation:** Refactor _resolve_session_md_conflict() to apply squash strategy for status line

**Behavior:**
- Status line = H1 title + `**Status:**` line
- Parse ours into sections
- For status line section: keep ours unchanged
- Discard theirs status line

**Approach:** Section-by-section processing, status line is special case (lines 0-2 typically)

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Refactor _resolve_session_md_conflict() to parse sections first
  Location hint: Beginning of function, before task extraction

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test with conflicting status lines
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_status_line_squash_strategy -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---

### Cycle 5.3: Completed This Session strategy (keep ours)

**RED Phase:**

**Test:** `test_completed_this_session_squash_strategy`
**Assertions:**
- Ours has "Completed This Session" with main work items
- Theirs has "Completed This Session" with worktree work items
- Result: Ours section preserved, theirs discarded (worktree completions are worktree-scoped)

**Expected failure:** Theirs completed items appear in merged result

**Why it fails:** Squash strategy not applied to Completed section

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_completed_this_session_squash_strategy -v`

**GREEN Phase:**

**Implementation:** Apply squash (keep ours) strategy for Completed This Session section

**Behavior:**
- Locate "Completed This Session" section in ours and theirs
- Keep ours section content unchanged
- Discard theirs section content

**Approach:** Section-by-section merge, Completed section uses keep-ours

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add Completed This Session to section strategy mapping
  Location hint: In _resolve_session_md_conflict() section processing

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test with completed items in both ours and theirs
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_completed_this_session_squash_strategy -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---

### Cycle 5.4: Pending Tasks strategy (existing additive logic preserved)

**RED Phase:**

**Test:** `test_pending_tasks_additive_strategy`
**Assertions:**
- Ours has tasks A and B
- Theirs has tasks B and C
- Result: tasks A, B, C (union by task name, B not duplicated)
- Existing behavior preserved from current _resolve_session_md_conflict()

**Expected failure:** Test passes (existing logic works) OR refactoring breaks additive merge

**Why it might pass:** Additive logic already implemented

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_pending_tasks_additive_strategy -v`

**GREEN Phase:**

**Implementation:** Preserve existing Pending Tasks additive logic in refactored function

**Behavior:**
- Extract tasks from ours and theirs via extract_task_blocks()
- Compare by task name to find new tasks
- Insert new tasks at Pending Tasks section end
- Existing logic from lines 70-108 preserved

**Approach:** Integrate existing additive logic into new section-based structure

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Preserve Pending Tasks additive merge in refactored code
  Location hint: Pending Tasks section processing in _resolve_session_md_conflict()

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test verifying task union behavior
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_pending_tasks_additive_strategy -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---

## Checkpoint 5.a: Section strategies (squash + additive)

**After Cycle 5.4:**

1. Run test suite: `pytest tests/test_worktree_merge_sections.py -v`
2. Verify 4 tests pass (section identification + 3 section strategies)
3. Functional check: Core merge refactor complete, remaining cycles build on this foundation

**Expected state:**
- Section-based merge architecture implemented
- Status line, Completed, Pending Tasks strategies working
- No regression in existing worktree merge tests

---

### Cycle 5.5: Keep-ours strategies (Worktree Tasks, Reference Files, Next Steps)

**Model:** Haiku (mechanical pattern — add 3 section names to existing strategy mapping)

**RED Phase:**

**Test:** `test_keep_ours_strategies` (parametrized)
**Parameters:**

| Section name | Description |
|-------------|-------------|
| Worktree Tasks | Main tracks worktree assignments; worktree's view is session-local |
| Reference Files | Worktree paths don't apply to main |
| Next Steps | Worktree direction is session-local |

**Assertions (per section):**
- Ours has section with main content
- Theirs has section with worktree content
- Result: Ours section preserved, theirs discarded

**Expected failure:** Theirs section content appears in merged result

**Why it fails:** Section not handled with keep-ours strategy

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_keep_ours_strategies -v`

**GREEN Phase:**

**Implementation:** Add all three section names to keep-ours strategy mapping

**Behavior:**
- Add "Worktree Tasks", "Reference Files", "Next Steps" to section strategy mapping
- All use identical keep-ours logic (already implemented for Status and Completed)

**Approach:** Add section names to existing strategy dict/mapping

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add Worktree Tasks, Reference Files, Next Steps to section strategy mapping with keep-ours
  Location hint: In _resolve_session_md_conflict() section processing

- File: `tests/test_worktree_merge_sections.py`
  Action: Create parametrized test covering all three sections
  Location hint: New test function with @pytest.mark.parametrize

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_keep_ours_strategies -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---

### Cycle 5.6: extract_blockers() function in session.py

**RED Phase:**

**Test:** `test_extract_blockers_function`
**Assertions:**
- extract_blockers(content) with single blocker `"- Issue X\n  Details here"` returns `[["- Issue X", "  Details here"]]`
- extract_blockers(content) with two blockers returns list of length 2, each containing their respective lines
- extract_blockers(content) with no Blockers section returns empty list `[]`
- Multi-line blocker with 3 continuation lines returns list item with 4 strings (bullet + 3 continuations)

**Expected failure:** NameError (extract_blockers not defined)

**Why it fails:** Function not implemented yet

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_extract_blockers_function -v`

**GREEN Phase:**

**Implementation:** Create extract_blockers() function in session.py

**Behavior:**
- Find "Blockers / Gotchas" section via find_section_bounds()
- Extract bullet items (same pattern as task extraction)
- Collect continuation lines per bullet
- Return list of line groups

**Approach:** Similar to extract_task_blocks() but simpler (no task name extraction)

**Changes:**
- File: `src/claudeutils/worktree/session.py`
  Action: Implement extract_blockers(content: str) -> list[list[str]]
  Location hint: New function after extract_task_blocks()

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test with Blockers section containing multi-line items
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_extract_blockers_function -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---

### Cycle 5.7: Blockers evaluation strategy (extract, tag, append)

**RED Phase:**

**Test:** `test_blockers_evaluate_strategy`
**Assertions:**
- Ours has "Blockers / Gotchas" section with main blockers
- Theirs has blockers specific to worktree work
- Result: Ours blockers preserved, theirs blockers appended with `[from: <slug>]` tag
- Tags appear at end of first line of each blocker

**Expected failure:** Theirs blockers not appended or not tagged

**Why it fails:** Blockers evaluation strategy not implemented

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_blockers_evaluate_strategy -v`

**GREEN Phase:**

**Implementation:** Extract theirs blockers, tag with [from: slug], append to ours

**Behavior:**
- Extract blockers from theirs via extract_blockers()
- For each blocker:
  - Add `[from: <slug>]` to end of first line
  - Append full blocker (all lines) to ours Blockers section
- Create Blockers section in ours if missing

**Approach:** Extract, tag, append pattern

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Implement Blockers evaluation in _resolve_session_md_conflict()
  Location hint: Blockers section processing, after keep-ours sections

- File: `src/claudeutils/worktree/merge.py`
  Action: Pass slug parameter to _resolve_session_md_conflict() (needed for tagging)
  Location hint: Function signature and call site in _phase3_merge_parent()

- File: `tests/test_worktree_merge_sections.py`
  Action: Create test with blockers in theirs, verify tagging and append
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_blockers_evaluate_strategy -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---

### Cycle 5.8: Integration test for per-section merge

**RED Phase:**

**Test:** `test_full_session_md_merge_integration`
**Assertions:**
- Status line: ours `"# Session Handoff: 2026-02-16"` preserved, theirs `"2026-02-15"` discarded
- Completed This Session: ours section with 2 items preserved, theirs section with 1 item discarded
- Pending Tasks: ours has task A+B, theirs has B+C → result contains A, B, C (no duplicate B)
- Worktree Tasks: ours section preserved, theirs discarded
- Blockers: ours has 1 blocker, theirs has 2 → result has 3 total, theirs two tagged with `[from: test-slug]`
- Reference Files: ours section preserved, theirs discarded
- Next Steps: ours section preserved, theirs discarded

**Expected failure:** Some sections not handled correctly in integration

**Why it fails:** Integration gaps between individual section strategies

**Verify RED:** `pytest tests/test_worktree_merge_sections.py::test_full_session_md_merge_integration -v`

**GREEN Phase:**

**Implementation:** End-to-end test verifying all strategies work together

**Behavior:**
- Create complete ours and theirs session.md files
- Simulate git conflict (write conflict markers)
- Run _resolve_session_md_conflict()
- Verify each section strategy applied correctly

**Approach:** Large integration test covering all sections

**Changes:**
- File: `tests/test_worktree_merge_sections.py`
  Action: Create comprehensive integration test
  Location hint: New test function with complete session.md fixtures

**Verify GREEN:** `pytest tests/test_worktree_merge_sections.py::test_full_session_md_merge_integration -v`
**Verify no regression:** `pytest tests/test_worktree_merge_sections.py -v`

---

## Checkpoint 5.mid: TDD Portion Complete

**After Cycle 5.8:**

1. Run `just dev` to verify code quality
2. Functional review: Verify all merge strategies pass tests
3. Integration check: Run existing worktree merge tests to ensure no regression
4. Commit: All TDD implementations and tests before proceeding to skill edits

**Expected state:**
- Per-section merge strategies fully implemented
- extract_blockers() function working correctly
- All 8 tests pass in test_worktree_merge_sections.py
- No regression in existing worktree merge test suite

---

## General Portion (Steps 5.9-5.11)

### Step 5.9: Update worktree skill Mode C (no auto-rm after merge)

**Prerequisite:** Read `agent-core/skills/worktree/SKILL.md` Mode C section (lines 84-114) — understand merge ceremony workflow and exit code 0 auto-rm behavior.

**Model:** Opus (skill modification per design directive)

**File:** `agent-core/skills/worktree/SKILL.md`

**Objective:** Decouple worktree deletion from merge success, enable bidirectional merge workflow.

**Implementation:**

Locate step 3 exit code 0 path in Mode C.

**Current behavior (lines ~97-101):**
```
Exit code 0 (merge success):
- Output merge success
- Use Bash to invoke: `claudeutils _worktree rm <slug>` to clean up
```

**New behavior:**
```
Exit code 0 (merge success):
- Output merge success message
- Inform user: worktree preserved for bidirectional workflow
- To remove: `wt-rm <slug>` (user decision)
```

**Changes:**
- Line ~98: Remove "Use Bash to invoke: `claudeutils _worktree rm <slug>`"
- Line ~99: Add "Worktree preserved. To remove when ready: `wt-rm <slug>`"

**Rationale:** D-4 — Bidirectional merge = skill update only. CLI already doesn't delete worktrees.

**Expected Outcome:** Mode C no longer auto-deletes worktrees after successful merge.

**Validation:** Read modified skill, verify no auto-rm in exit code 0 path.

---

### Step 5.10: Update execute-rule.md STATUS + Unscheduled Plans (full planstate transition)

**Depends on:** Phase 1 (list_plans(), PlanState model)

**Prerequisite:** Read `agent-core/fragments/execute-rule.md` STATUS mode section (lines 16-54) — understand current jobs.md data source and Unscheduled Plans display format.

**Model:** Opus (fragment modification per design directive)

**File:** `agent-core/fragments/execute-rule.md`

**Objective:** Replace jobs.md reads with planstate calls in STATUS mode.

**Implementation:**

Locate STATUS display format section and Unscheduled Plans subsection.

**Changes needed:**

1. **Pending list format subsection**:
   - Locate line `"Nested line: plan directory, status from jobs.md, notes if present"`
   - Replace with: `"Nested line: plan directory, status from planstate, notes if present"`

2. **Unscheduled Plans subsection**:
   - Locate line `"Read \`agents/jobs.md\` for all plans"`
   - Replace with: `"Call list_plans(Path('plans')) for all plans"`
   - Locate `"Status values: \`complete\`, \`planned\`, \`designed\`, \`requirements\`"`
   - Replace with: `"Status values: \`requirements\`, \`designed\`, \`planned\`, \`ready\`"` (Phase 1 PlanState enum values)

3. **Status source line**:
   - Locate `"Read \`agents/jobs.md\` as authoritative source for plan status and notes"`
   - Replace with: `"Call list_plans() as authoritative source for plan status; session.md for task notes"`

**Expected Outcome:** STATUS mode uses planstate exclusively, no jobs.md references remain.

**Validation:**
- Grep execute-rule.md for "jobs.md" → no matches in STATUS section
- Verify list_plans() usage is correct

---

### Step 5.11: Verify Phase 5 changes with integration test

**Model:** Sonnet (verification task)

**Objective:** Confirm all Phase 5 changes work together before proceeding to Phase 6.

**Implementation:**

1. Run merge strategy test suite:
   ```bash
   pytest tests/test_worktree_merge_sections.py -v
   ```
   Expected: All tests pass

2. Run full worktree test suite to check for regressions:
   ```bash
   pytest tests/test_worktree*.py -v
   ```
   Expected: No new failures (existing failures acceptable if documented)

3. Manual check: Read modified skill and fragment files, verify changes match design D-4 and D-5.

**Expected Outcome:** All tests pass, no regressions, skill/fragment changes verified.

**Error Conditions:**
- If any test fails: STOP, investigate, fix before Phase 6
- If skill changes don't match design: STOP, correct and re-vet

**Validation:** Test output shows all green, manual review confirms accuracy.

---

## Phase 5 Complete

**After Step 5.11:**

1. Full checkpoint: Fix + Vet + Functional
2. Commit: All Phase 5 changes (TDD + general)
3. Verify external dependency was deployed (worktree-merge-data-loss Track 1+2)

**Expected state:**
- Per-section merge strategies implemented and tested
- Worktree skill Mode C no longer auto-deletes
- execute-rule.md STATUS uses planstate instead of jobs.md
- All tests pass
- No UNFIXABLE issues from vet
