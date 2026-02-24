### Phase 3: TDD agent generation (type: tdd, model: sonnet)

**Scope:** Extend prepare-runbook.py for ping-pong TDD: 4 agent types, step file splitting, orchestrator plan TDD markers, verify-red.sh.

**Files:** `agent-core/bin/prepare-runbook.py`, `agent-core/skills/orchestrate/scripts/verify-red.sh` (create), `tests/test_prepare_runbook_tdd_agents.py` (create), `tests/test_verify_red.py` (create)

**Depends on:** Phase 1 (agent caching model — `generate_task_agent` function, `read_baseline_agent`), Phase 2 (orchestrator plan format — pipe-delimited step list, `generate_default_orchestrator`)

**Key constraints:**
- TDD agents extend Phase 1's per-role model: 4 roles instead of 1 task + 1 corrector
- Agent naming: `<plan>-tester.md`, `<plan>-implementer.md`, `<plan>-test-corrector.md`, `<plan>-impl-corrector.md`
- Baseline selection: test-driver.md for tester/implementer, corrector.md for test-corrector/impl-corrector
- All 4 agents embed same Plan Context (design + outline) as task agent from Phase 1
- Generated only for TDD-typed runbooks (pure TDD or TDD phases in mixed)
- Step file splitting: each TDD cycle → `step-N-test.md` (RED) + `step-N-impl.md` (GREEN)
- Orchestrator plan TDD markers: TEST/IMPLEMENT role on step entries
- Tests in NEW file `tests/test_prepare_runbook_tdd_agents.py` — NOT in `test_prepare_runbook_agents.py` (353 lines, near 400-line threshold)
- verify-red.sh: deterministic script (non-cognitive → script, per recall "When Choosing Script vs Agent Judgment")
- Shell script testing: real git repos in tmp_path (per recall "When Preferring E2E Over Mocked Subprocess")

---

## Cycle 3.1: TDD agent type generation (4 agents)

**RED Phase:**

**Test:** `test_tdd_agents_generated_for_tdd_runbook` and `test_no_tdd_agents_for_general_runbook`
**File:** `tests/test_prepare_runbook_tdd_agents.py` (create)
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 821-876 (`read_baseline_agent`, `generate_agent_frontmatter`, `generate_phase_agent`) — understand current baseline selection and agent composition. Read `agent-core/agents/test-driver.md` first 5 lines and `agent-core/agents/corrector.md` first 5 lines — understand frontmatter structure for baseline matching.

**Assertions (TDD runbook):**
- `validate_and_create` with a pure-TDD runbook (all phases `type: tdd`) produces exactly 4 agent files in agents directory
- Agent filenames are `{name}-tester.md`, `{name}-implementer.md`, `{name}-test-corrector.md`, `{name}-impl-corrector.md`
- Tester agent body contains test-driver.md baseline content (match a distinctive string from test-driver.md body)
- Implementer agent body contains test-driver.md baseline content
- Test-corrector agent body contains corrector.md baseline content
- Impl-corrector agent body contains corrector.md baseline content
- All 4 agents contain `# Plan Context` section with `## Design` subsection
- Tester agent contains "test quality" directive (role-specific rule embedding)
- Implementer agent contains "implementation" or "coding" directive

**Assertions (general runbook):**
- `validate_and_create` with a general runbook produces NO tester/implementer/test-corrector/impl-corrector files
- Only task agent and (if multi-phase) corrector agent generated (Phase 1 behavior preserved)

**Expected failure:** AssertionError — current code generates `crew-{name}` per-phase agents, no TDD-specific agent types exist

**Why it fails:** `validate_and_create` only calls `generate_phase_agent` in a per-phase loop; no TDD agent generation path exists

**Verify RED:** `pytest tests/test_prepare_runbook_tdd_agents.py -v`

**GREEN Phase:**

**Implementation:** Add TDD agent generation path to `validate_and_create` and supporting functions

**Behavior:**
- Detect TDD presence: any phase with `type: tdd` in `phase_types` dict
- When TDD detected: generate 4 additional agents using role-specific baselines and footers
- Tester + implementer use test-driver.md baseline; test-corrector + impl-corrector use corrector.md baseline
- Each agent gets same Plan Context (design + outline) as Phase 1's task agent
- Role-specific rule sections appended: tester gets test quality rules, implementer gets coding rules, correctors get review-specific rules
- Skip TDD agent generation entirely for pure-general runbooks

**Approach:** Add a `generate_tdd_agents` function called from `validate_and_create` after the existing task agent generation. This function checks `phase_types` for any TDD phases, then generates 4 agents using `read_baseline_agent` with appropriate type parameter and role-specific footers. Reuse Plan Context construction from Phase 1's task agent path.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `generate_tdd_agents` function producing 4 role-specific agents
  Location hint: near `generate_phase_agent` (line 858)

- File: `agent-core/bin/prepare-runbook.py`
  Action: Call `generate_tdd_agents` from `validate_and_create` when TDD phases detected
  Location hint: after the per-phase agent generation loop (around line 1376)

**Verify GREEN:** `just check && just test`

---

## Cycle 3.2: Step file splitting (test/impl per TDD cycle)

**RED Phase:**

**Test:** `test_tdd_cycle_splits_into_test_and_impl_files`
**File:** `tests/test_prepare_runbook_tdd_agents.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 1377-1390 (current TDD cycle step file generation) — understand how cycles currently produce single `step-N-M.md` files. Read lines 1020-1062 (`generate_cycle_file`) — understand current cycle file content structure with RED/GREEN sections.

**Assertions:**
- For a TDD runbook with cycle 1.1: two step files created, not one
- Files named `step-1-1-test.md` and `step-1-1-impl.md`
- Test file (`step-1-1-test.md`) contains RED phase content (test function name, assertions, expected failure)
- Test file does NOT contain GREEN phase content (implementation hints, verify GREEN command)
- Impl file (`step-1-1-impl.md`) contains GREEN phase content (implementation description, behavior, changes)
- Impl file does NOT contain RED phase content (test assertions, expected failure)
- Both files have metadata headers (runbook source, phase number, execution model)
- For a general runbook step: single `step-N-M.md` file (no splitting — existing behavior preserved)

**Expected failure:** AssertionError — current code generates single `step-N-M.md` per cycle

**Why it fails:** `generate_cycle_file` produces one file containing both RED and GREEN sections; no splitting logic exists

**Verify RED:** `pytest tests/test_prepare_runbook_tdd_agents.py::test_tdd_cycle_splits_into_test_and_impl_files -v`

**GREEN Phase:**

**Implementation:** Split TDD cycle step generation into test and impl files

**Behavior:**
- For TDD cycles: generate two files instead of one
- Test file contains: metadata header + RED phase content (extracted from cycle content)
- Impl file contains: metadata header + GREEN phase content (extracted from cycle content)
- RED/GREEN split point: content before "**GREEN Phase:**" marker → test file; content after → impl file
- Both files get same metadata headers (runbook source, phase, model)
- General steps unchanged (no splitting)

**Approach:** Modify the TDD cycle step generation loop in `validate_and_create` (lines 1377-1390). Add a `split_cycle_content` helper that separates RED from GREEN using the `**GREEN Phase:**` heading as delimiter. Generate two files per cycle using `generate_cycle_file` (or a variant) for each half.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `split_cycle_content` function to separate RED and GREEN sections
  Location hint: near `generate_cycle_file` (line 1020)

- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify TDD cycle loop to generate two files per cycle
  Location hint: lines 1377-1390

**Verify GREEN:** `just check && just test`

---

## Cycle 3.3: Orchestrator plan TDD role markers

**RED Phase:**

**Test:** `test_orchestrator_plan_tdd_role_markers`
**File:** `tests/test_prepare_runbook_tdd_agents.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 1065-1196 (`generate_default_orchestrator`) — understand how items list is built and how step entries are formatted. Understand the pipe-delimited format from Phase 2 Cycle 2.1.

**Assertions:**
- For a TDD runbook: orchestrator plan step entries include role marker
- Test step entries: `- step-1-1-test.md | Phase 1 | sonnet | 25 | TEST`
- Impl step entries: `- step-1-1-impl.md | Phase 1 | sonnet | 25 | IMPLEMENT`
- TEST and IMPLEMENT markers alternate within each cycle (test before impl)
- For a general runbook: step entries have NO role marker (existing format preserved)
- Orchestrator plan header `**Agent:**` field lists tester agent for TEST steps, implementer for IMPLEMENT steps (or a mapping section)

**Expected failure:** AssertionError — current orchestrator plan generates single entry per cycle with no role marker

**Why it fails:** `generate_default_orchestrator` builds items from cycles as single entries; no TEST/IMPLEMENT distinction exists

**Verify RED:** `pytest tests/test_prepare_runbook_tdd_agents.py::test_orchestrator_plan_tdd_role_markers -v`

**GREEN Phase:**

**Implementation:** Add TDD role markers to orchestrator plan step entries

**Behavior:**
- When TDD cycles detected: split each cycle into two items in the orchestrator plan
- Test item: `step-N-M-test.md | Phase N | model | max_turns | TEST`
- Impl item: `step-N-M-impl.md | Phase N | model | max_turns | IMPLEMENT`
- TEST steps dispatch to tester agent; IMPLEMENT steps dispatch to implementer agent
- General steps unchanged (no role marker)
- Agent mapping in plan header: include tester/implementer agent names for TDD dispatch

**Approach:** Modify the items list construction in `generate_default_orchestrator`. When cycle items are added, expand each into two items (test + impl) with role markers. Add role field to the item tuple. Update the step entry formatting to include role when present.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Expand TDD cycle items into test/impl pairs with role markers in `generate_default_orchestrator`
  Location hint: lines 1109-1120 (cycle items construction)

- File: `agent-core/bin/prepare-runbook.py`
  Action: Include role marker in step entry formatting
  Location hint: lines 1159-1186 (step entry output loop)

**Verify GREEN:** `just check && just test`

---

## Cycle 3.4: verify-red.sh creation and testing

**RED Phase:**

**Test:** `test_verify_red_confirms_failing_test` and `test_verify_red_rejects_passing_test`
**File:** `tests/test_verify_red.py` (create)
**Prerequisite:** Read `agent-core/skills/orchestrate/scripts/` directory — confirm location for new script. Read design section "Ping-Pong TDD Orchestration (D-5)" for RED gate contract.

**Assertions (failing test = RED confirmed):**
- Script at `agent-core/skills/orchestrate/scripts/verify-red.sh` exists and is executable
- Given a test file containing a test that FAILS (assert False): script exits 0
- stdout contains "RED" or "CONFIRMED"

**Assertions (passing test = RED rejected):**
- Given a test file containing a test that PASSES (assert True): script exits 1
- stdout contains "FAIL" or "REJECTED" or indicates test unexpectedly passed

**Assertions (missing test):**
- Given a nonexistent test file path: script exits 1
- stdout contains error indication

**Test setup:** Create real Python test files in `tmp_path`:
- Failing test: `def test_example(): assert False`
- Passing test: `def test_example(): assert True`
- Run `verify-red.sh <test_file>` via subprocess in each case

**Expected failure:** FileNotFoundError or similar — script doesn't exist yet

**Why it fails:** `agent-core/skills/orchestrate/scripts/verify-red.sh` hasn't been created

**Verify RED:** `pytest tests/test_verify_red.py -v`

**GREEN Phase:**

**Implementation:** Create verify-red.sh script

**Behavior:**
- Accept test file path as argument
- Run `pytest <test_file> --no-header -q`
- If pytest exits non-zero (test fails) → script exits 0 with "RED CONFIRMED" on stdout
- If pytest exits zero (test passes) → script exits 1 with "RED REJECTED: test passed unexpectedly" on stdout
- If test file doesn't exist → script exits 1 with error message
- Validate argument count (exactly 1 argument required)

**Approach:** Write bash script using token-efficient pattern (`exec 2>&1; set -xeuo pipefail`). Validate input, run pytest, invert exit code logic.

**Changes:**
- File: `agent-core/skills/orchestrate/scripts/verify-red.sh` (create)
  Action: Create RED gate verification script per design contract
  Location hint: new file

**Verify GREEN:** `just check && just test`
