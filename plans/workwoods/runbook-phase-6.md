### Phase 6: jobs.md Elimination + Archive (type: mixed)

**Purpose:** Complete jobs.md elimination by creating plan archive, updating consuming code, and removing obsolete files.

**Scope (TDD):**
- `src/claudeutils/validation/planstate.py` - New validator
- `tests/test_validation_planstate.py` - Validator tests

**Scope (General):**
- `agents/plan-archive.md` - Completed plan summaries (migration from jobs.md)
- Skill/fragment updates (handoff, design, worktree)
- File removals (jobs.md, jobs.py)

**Dependencies:** Phases 1 + 5 (completes elimination after adoption)

**Execution Model:** Sonnet (TDD + removals), Opus (skill edits)

**Estimated Complexity:** Medium (validator + mechanical removals)

---

## TDD Portion (Cycles 6.1-6.6)

### Cycle 6.1: Validator detects missing artifacts (no recognized files)

**Prerequisite:** Read validation/jobs.py (lines 47-79) to understand validator structure and pattern.

**RED Phase:**

**Test:** `test_validator_detects_missing_artifacts`
**Assertions:**
- Plan directory with no recognized artifacts returns error
- Error message: "Plan '<name>' has no recognized artifacts"
- Empty directory treated as no artifacts
- plans/reports/ excluded from validation (not a plan)

**Expected failure:** ImportError (planstate validator doesn't exist)

**Why it fails:** No validation/planstate.py module yet

**Verify RED:** `pytest tests/test_validation_planstate.py::test_validator_detects_missing_artifacts -v`

**GREEN Phase:**

**Implementation:** Create planstate validator with artifact detection

**Behavior:**
- Call list_plans(plans_dir) from planstate module
- For each plan: check if infer_state() returned None (no artifacts)
- If None: add error "Plan '<name>' has no recognized artifacts"
- Return list of error messages

**Approach:** Scan all plans/, check for None results from infer_state()

**Changes:**
- File: `src/claudeutils/validation/planstate.py`
  Action: Create validate(root: Path) -> list[str] function
  Location hint: New file, follow validation/jobs.py structure

- File: `tests/test_validation_planstate.py`
  Action: Create test with tmp_path, empty plan directory
  Location hint: New file

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_validator_detects_missing_artifacts -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---

### Cycle 6.2: Validator checks artifact consistency (steps/ without runbook-phase-*.md)

**RED Phase:**

**Test:** `test_validator_checks_artifact_consistency`
**Assertions:**
- Plan with steps/ directory but no runbook-phase-*.md files returns error
- Error message: "Plan '<name>' has steps/ without runbook-phase-*.md files"
- Plan with orchestrator-plan.md but no steps/ returns error
- Consistent artifacts (all present) pass validation

**Expected failure:** No consistency checking, only artifact presence validated

**Why it fails:** Consistency logic not implemented

**Verify RED:** `pytest tests/test_validation_planstate.py::test_validator_checks_artifact_consistency -v`

**GREEN Phase:**

**Implementation:** Add consistency checks for ready status artifacts

**Behavior:**
- If steps/ exists: verify runbook-phase-*.md files exist (at least one)
- If orchestrator-plan.md exists: verify steps/ exists
- Both conditions must hold for ready status
- Return error for inconsistent state

**Approach:** Explicit checks after artifact detection

**Changes:**
- File: `src/claudeutils/validation/planstate.py`
  Action: Add consistency checking in validate() function
  Location hint: After artifact presence check

- File: `tests/test_validation_planstate.py`
  Action: Create tests with inconsistent artifact combinations
  Location hint: New test functions for each inconsistency type

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_validator_checks_artifact_consistency -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---

### Cycle 6.3: Validator warns on plan-archive orphans (referenced plans not deleted)

**RED Phase:**

**Test:** `test_validator_warns_on_archive_orphans`
**Assertions:**
- Plan referenced in plan-archive.md but still in plans/ directory returns warning
- Warning message: "Plan '<name>' archived but directory still exists"
- Plans in archive without directories are valid (expected state)

**Expected failure:** No plan-archive.md checking

**Why it fails:** Archive orphan detection not implemented

**Verify RED:** `pytest tests/test_validation_planstate.py::test_validator_warns_on_archive_orphans -v`

**GREEN Phase:**

**Implementation:** Read plan-archive.md, check for orphan references

**Behavior:**
- Read agents/plan-archive.md (if exists)
- Extract H2 headings as archived plan names
- Check if any archived plan still has directory in plans/
- If found: add warning (not error — may be intentional)

**Approach:** Parse markdown H2 headings, cross-reference with plans/ listing

**Changes:**
- File: `src/claudeutils/validation/planstate.py`
  Action: Add archive orphan checking in validate() function
  Location hint: After consistency checks

- File: `tests/test_validation_planstate.py`
  Action: Create test with plan-archive.md and orphaned directory
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_validator_warns_on_archive_orphans -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---

### Cycle 6.4: Integration with validation CLI (replace jobs validator)

**RED Phase:**

**Test:** `test_cli_integration_calls_planstate_validator`
**Assertions:**
- `claudeutils validate` calls planstate validator
- `claudeutils validate planstate` subcommand exists
- Validator errors appear in CLI output
- Exit code 1 on validation errors

**Expected failure:** Planstate validator not registered in CLI

**Why it fails:** CLI doesn't know about planstate validator yet

**Verify RED:** `pytest tests/test_validation_planstate.py::test_cli_integration_calls_planstate_validator -v`

**GREEN Phase:**

**Implementation:** Register planstate validator in validation/cli.py

**Behavior:**
- Import validate_planstate from validation.planstate
- Add _run_validator("planstate", validate_planstate, all_errors, root) in _run_all_validators()
- Add @validate.command() for planstate subcommand

**Approach:** Follow same pattern as jobs validator (lines 70, 148-156 in cli.py)

**Changes:**
- File: `src/claudeutils/validation/cli.py`
  Action: Add planstate validator to _run_all_validators()
  Location hint: After jobs validator call (line ~70)

- File: `src/claudeutils/validation/cli.py`
  Action: Add planstate subcommand
  Location hint: After jobs subcommand (after line 156)

- File: `tests/test_validation_planstate.py`
  Action: Create CLI integration test using CliRunner
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_cli_integration_calls_planstate_validator -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---

### Cycle 6.5: Validator registration in cli.py

**Note:** This cycle merges with 6.4 (registration IS the integration). Keeping as separate cycle for clarity.

**RED Phase:**

**Test:** `test_planstate_validator_registered`
**Assertions:**
- validate_planstate imported in cli.py
- _run_validator called with "planstate" name
- Planstate command appears in `claudeutils validate --help`

**Expected failure:** Test passes if 6.4 completed correctly

**Why it might pass:** Already implemented in 6.4

**Verify RED:** `pytest tests/test_validation_planstate.py::test_planstate_validator_registered -v`

**GREEN Phase:**

**Implementation:** Verify registration is complete and tested

**Behavior:**
- Confirm import statement exists
- Confirm _run_validator call exists
- Confirm subcommand decorator exists

**Approach:** This is a verification cycle, no new code unless 6.4 missed something

**Changes:**
- File: `tests/test_validation_planstate.py`
  Action: Add registration verification test
  Location hint: New test function checking imports and calls

**Verify GREEN:** `pytest tests/test_validation_planstate.py::test_planstate_validator_registered -v`
**Verify no regression:** `pytest tests/test_validation_planstate.py -v`

---

### Cycle 6.6: Remove jobs validator tests, add planstate validator tests

**RED Phase:**

**Test:** `test_jobs_validator_removed`
**Assertions:**
- tests/test_validation_jobs.py file deleted
- No imports of validate_jobs in test files
- All jobs validator references removed from test suite

**Expected failure:** jobs validator tests still exist

**Why it fails:** Test deletion not yet performed

**Verify RED:** `pytest tests/ -k "jobs" -v` shows test_validation_jobs.py tests

**GREEN Phase:**

**Implementation:** Delete jobs validator test file

**Behavior:**
- Remove tests/test_validation_jobs.py
- Verify no other test files import or reference it
- All planstate validator tests (6.1-6.5) serve as replacement

**Approach:** File deletion

**Changes:**
- File: `tests/test_validation_jobs.py`
  Action: Delete file
  Location hint: Entire file removed

**Verify GREEN:** `pytest tests/ -k "jobs" -v` shows no test_validation_jobs.py tests
**Verify no regression:** `pytest tests/test_validation_planstate.py -v` (all new tests pass)

---

## TDD Checkpoint

**After Cycle 6.6:**

1. Run `just dev` to verify code quality
2. Functional review: Verify planstate validator catches all expected issues
3. CLI integration check: Run `claudeutils validate` and verify planstate validator runs
4. Commit: All TDD implementations and tests before general steps

**Expected state:**
- validation/planstate.py exists with complete validator
- All 6 tests pass (or 5 if 6.5 merged with 6.4)
- Validator registered in CLI
- jobs validator tests deleted

---

## General Portion (Steps 6.7-6.15)

### Step 6.7: Create agents/plan-archive.md via jobs.md migration

**Model:** Sonnet (data migration task)

**Objective:** Migrate completed plans from jobs.md to rich archive format.

**Implementation:**

1. Read agents/jobs.md "Complete (Archived)" section
2. For each completed plan:
   - Extract plan name
   - Run: `git log --all --oneline -- plans/<name>/` to get commit history
   - Extract commit messages describing deliverables
   - Synthesize 2-4 sentence summary: what was delivered, affected modules, key decisions
3. Write agents/plan-archive.md with H2 entries (plan name) + paragraph summaries

**Format:**
```markdown
# Plan Archive

Completed plans with summaries. Loaded on demand during design research (Phase A.1)
and diagnostic/RCA sessions.

## plan-name

Summary paragraph (2-4 sentences). Delivered: [what]. Affected: [modules].
Key decision: [architectural choice].
```

**Expected Outcome:** plan-archive.md created with all archived plans from jobs.md.

**Validation:** Count archived plans in jobs.md vs plan-archive.md H2 headings (match).

---

### Step 6.8: Update handoff skill (write plan-archive.md instead of jobs.md)

**Model:** Opus (skill modification per design directive)

**File:** `agent-core/skills/handoff/SKILL.md`

**Objective:** Plan completion writes to plan-archive.md, not jobs.md.

**Implementation:**

Read handoff skill to locate jobs.md update logic.

**Changes needed:**
- Find section describing plan completion handling
- Replace "Update agents/jobs.md status to complete" with "Write plan summary to agents/plan-archive.md"
- Update logic: Extract plan summary from design.md or session.md, write H2 + paragraph to archive

**Expected Outcome:** Handoff skill references plan-archive.md, not jobs.md.

**Validation:** Grep handoff skill for "jobs.md" → no matches. Grep for "plan-archive.md" → found.

---

### Step 6.9: Update design skill (A.1 loads plan-archive.md on demand)

**Model:** Opus (skill modification per design directive)

**File:** `agent-core/skills/design/SKILL.md`

**Objective:** Phase A.1 research loads plan-archive.md instead of jobs.md.

**Implementation:**

Read design skill Phase A.1 (research phase) to locate jobs.md loading.

**Changes needed:**
- Find "Read agents/jobs.md for completed plans" instruction
- Replace with "Read agents/plan-archive.md for completed plan summaries (on demand, not in CLAUDE.md)"
- Note that plan-archive.md is NOT loaded by default (unlike jobs.md which was @-referenced)

**Expected Outcome:** Design skill references plan-archive.md in Phase A.1.

**Validation:** Grep design skill for "jobs.md" in Phase A.1 → no matches. Grep for "plan-archive.md" → found.

---

### Step 6.10: Remove jobs.md from CLAUDE.md @-reference

**Model:** Sonnet (configuration update)

**File:** `CLAUDE.md`

**Objective:** Remove `@agents/jobs.md` line from CLAUDE.md references.

**Implementation:**

1. Read CLAUDE.md
2. Locate `@agents/jobs.md` line (likely in "Current Work" section)
3. Delete line
4. Verify no other jobs.md references remain in CLAUDE.md

**Expected Outcome:** CLAUDE.md contains no jobs.md references.

**Validation:** Grep CLAUDE.md for "jobs.md" → no matches.

---

### Step 6.11: Remove validation/jobs.py and CLI integration

**Model:** Sonnet (file removal + cleanup)

**Files:**
- `src/claudeutils/validation/jobs.py` - Delete
- `src/claudeutils/validation/cli.py` - Remove import and call

**Objective:** Remove jobs validator module and CLI integration.

**Implementation:**

1. Delete src/claudeutils/validation/jobs.py
2. Edit src/claudeutils/validation/cli.py:
   - Remove: `from claudeutils.validation.jobs import validate as validate_jobs`
   - Remove: `_run_validator("jobs", validate_jobs, all_errors, root)` line
   - Remove: `@validate.command() def jobs():` function (lines 148-156)

**Expected Outcome:** No jobs validator code remains.

**Validation:**
- `ls src/claudeutils/validation/jobs.py` → file not found
- Grep cli.py for "validate_jobs" → no matches

---

### Step 6.12: Remove all jobs.md references from merge.py

**Model:** Sonnet (code cleanup)

**File:** `src/claudeutils/worktree/merge.py`

**Objective:** Remove jobs.md conflict resolution and exempt path references.

**Implementation:**

1. Remove _resolve_jobs_md_conflict() function (lines 143-156)
2. Remove call to _resolve_jobs_md_conflict() in _phase3_merge_parent() (line 251)
3. Remove "agents/jobs.md" from exempt_paths set in _phase1_validate_clean_trees() (line 179)

**Expected Outcome:** No jobs.md references in merge.py.

**Validation:** Grep merge.py for "jobs" → no matches.

---

### Step 6.13: Update focus_session() if it references jobs.md

**Model:** Sonnet (conditional cleanup)

**File:** `src/claudeutils/worktree/session.py` (or location of focus_session)

**Objective:** Remove or update any jobs.md reference in focus_session().

**Implementation:**

1. Grep for focus_session() function definition
2. If function references jobs.md: remove or update reference
3. If no reference: skip this step (no action needed)

**Expected Outcome:** focus_session() has no jobs.md references.

**Validation:** Grep focus_session() implementation for "jobs" → no matches (or function doesn't exist).

---

### Step 6.14: Delete agents/jobs.md

**Model:** Sonnet (file removal)

**File:** `agents/jobs.md`

**Objective:** Remove obsolete jobs.md file from repository.

**Implementation:**

1. Verify plan-archive.md created and populated (Step 6.7 complete)
2. Verify all consumers updated (Steps 6.8-6.13 complete)
3. Delete agents/jobs.md

**Expected Outcome:** jobs.md file no longer exists.

**Validation:** `ls agents/jobs.md` → file not found.

---

### Step 6.15: Update worktree skill Mode B (read planstate instead of jobs.md)

**Model:** Opus (skill modification per design directive)

**File:** `agent-core/skills/worktree/SKILL.md`

**Objective:** Mode B parallel group analysis uses list_plans() instead of parse_jobs_md().

**Implementation:**

Read worktree skill Mode B (lines 47-82) to locate jobs.md dependency logic.

**Changes needed:**
- Find "Read agents/jobs.md for plan directories" instruction
- Replace with "Call list_plans() from planstate module for plan status"
- Update independent group detection logic to use PlanState objects instead of jobs.md entries

**Expected Outcome:** Mode B uses planstate module, not jobs.md.

**Validation:** Grep worktree skill Mode B for "jobs.md" → no matches. Grep for "list_plans" → found.

---

## Phase 6 Complete

**After Step 6.15:**

1. Full checkpoint: Fix + Vet + Functional
2. Verify no jobs.md references remain in codebase: `rg "jobs\.md" --type md --type py`
3. Verify planstate validator runs in precommit: `just precommit`
4. Commit: All Phase 6 changes

**Expected state:**
- Planstate validator fully operational
- Plan-archive.md created and populated
- All jobs.md references removed from skills, fragments, and code
- jobs.md and jobs.py deleted
- No UNFIXABLE issues from vet
