# Runbook Quality Gates — Phase B Runbook Outline

**Context:** Phase A (prose edits) is complete. All 6 architectural artifacts delivered:
- `runbook-simplification-agent.md` ✓
- `runbook/SKILL.md` Phase 0.86 + Phase 3.5 ✓
- `review-plan/SKILL.md` Section 12 ✓
- `plan-reviewer.md` model assignment line ✓
- `pipeline-contracts.md` T2.5/T4.5 ✓
- `memory-index.md` two new entries ✓

**This runbook:** Phase B — implement `validate-runbook.py` (4 subcommands) with TDD.

**Design:** `plans/runbook-quality-gates/design.md`

---

## Requirements Mapping

| Requirement | Phase | Cycles | Notes |
|-------------|-------|--------|-------|
| FR-2 (mechanical) | Phase 1 | 1.2–1.3 | model-tags subcommand |
| FR-3 | Phase 2 | 2.1–2.3 | lifecycle subcommand |
| FR-5 | Phase 3 | 3.1–3.3 | test-counts subcommand |
| FR-4 (structural) | Phase 4 | 4.1–4.3 | red-plausibility subcommand |
| FR-4 (semantic, exit 2) | Phase 4 | 4.3 | exit code 2 for ambiguous |
| FR-6 (scaling) | — | — | Addressed by design: mandatory uniform execution for all Tier 3 runbooks |
| NFR-2 (incremental) | Phase 5 | 5.1 | --skip flags + directory input (consolidated) |
| NFR-1 (integration) | All | 1.1, 5.1 | argparse CLI, directory input |

---

## Phase Structure

### Phase 1: Script infrastructure + `model-tags` subcommand (type: tdd)

Complexity: Medium | Target: `agent-core/bin/validate-runbook.py` (new), `tests/test_validate_runbook.py` (new)

**Context:** D-7 resolved — import `parse_frontmatter`, `extract_cycles`, `extract_sections`, `assemble_phase_files`, `extract_file_references`, `extract_step_metadata` from `prepare-runbook.py` via `importlib.util.spec_from_file_location`.

- Cycle 1.1: Script scaffold — argparse with 4 subcommands, importlib import of prepare-runbook.py functions, report writer, exit codes
- Cycle 1.2: model-tags — happy path (no violations, exit 0, report written to `plans/<job>/reports/validation-model-tags.md`)
- Cycle 1.3: model-tags — violation detection (skill/fragment/agent file with non-opus `**Execution Model**:` tag, exit 1, violation in report)

Checkpoint after Phase 1: Run `just test tests/test_validate_runbook.py`

### Phase 2: `lifecycle` subcommand (type: tdd)

Complexity: Medium | Target: `agent-core/bin/validate-runbook.py` (modify), `tests/test_validate_runbook.py` (modify)
Depends on: Phase 1 (script scaffold, importlib infrastructure, report writer)

- Cycle 2.1: lifecycle — happy path (correct create→modify ordering, exit 0)
- Cycle 2.2: lifecycle — modify-before-create violation (file modified before created in runbook, exit 1)
- Cycle 2.3: lifecycle — duplicate creation violation (file marked Created in two separate cycles, exit 1)

Checkpoint after Phase 2: Run `just test tests/test_validate_runbook.py`

### Phase 3: `test-counts` subcommand (type: tdd)

Complexity: Medium | Target: `agent-core/bin/validate-runbook.py` (modify), `tests/test_validate_runbook.py` (modify)
Depends on: Phase 1 (script scaffold, importlib infrastructure, report writer)

- Cycle 3.1: test-counts — happy path (checkpoint "All 3 tests pass" with 3 `**Test:**` fields, exit 0)
- Cycle 3.2: test-counts — count mismatch (checkpoint claims 5 when 3 tests exist, exit 1)
- Cycle 3.3: test-counts — parametrized test accounting (`test_foo[param1]` and `test_foo[param2]` count as 1 unique test function, exit 0)

Checkpoint after Phase 3: Run `just test tests/test_validate_runbook.py`

### Phase 4: `red-plausibility` subcommand (type: tdd)

Complexity: High | Target: `agent-core/bin/validate-runbook.py` (modify), `tests/test_validate_runbook.py` (modify)
Depends on: Phase 1 (script scaffold, importlib infrastructure, report writer)

- Cycle 4.1: red-plausibility — happy path (RED function not created in prior GREENs, exit 0)
- Cycle 4.2: red-plausibility — clear violation (function created in prior GREEN, RED expects ImportError on same function, exit 1)
- Cycle 4.3: red-plausibility — ambiguous case (function exists from prior GREEN, RED tests different behavior — not clear if passing, exit 2)

Checkpoint after Phase 4: Run `just test tests/test_validate_runbook.py`

### Phase 5: Integration — directory input and --skip flags (type: tdd)

Complexity: Low | Target: `agent-core/bin/validate-runbook.py` (modify), `tests/test_validate_runbook.py` (modify)
Depends on: Phases 1-4 (all 4 subcommands implemented -- integration exercises them together)
1 cycle (consolidated from 2: directory input + skip flags are same-module argparse additions)

- Cycle 5.1: directory input + skip flags — assemble runbook-phase-*.md files and run all checks (existing assembly via `assemble_phase_files`); `--skip-model-tags`, `--skip-lifecycle`, `--skip-test-counts`, `--skip-red-plausibility` skip respective checks (NFR-2). Parametrized test covers each skip flag.

Final checkpoint: Run `just test tests/test_validate_runbook.py` — all tests pass (count depends on parametrization decisions during expansion)

---

## Fixture Plan

Fixtures are inline strings in `tests/test_validate_runbook.py` (not separate `.md` files). Simpler for parametrization, no file I/O in tests. Exception: directory-input test (Cycle 5.1) uses `tmp_path` with real files.

| Fixture Constant | Used By | Purpose |
|---|---|---|
| `VALID_TDD` | phases 1–4 happy path | Valid TDD runbook, passes all checks |
| `VALID_GENERAL` | phase 1 (model-tags) | General steps, correct model tags, no TDD |
| `VIOLATION_MODEL_TAGS` | cycle 1.3 | Skill file with `haiku` Execution Model |
| `VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE` | cycle 2.2 | File modified before created in earlier cycle |
| `VIOLATION_LIFECYCLE_DUPLICATE_CREATE` | cycle 2.3 | File created in two separate cycles |
| `VIOLATION_TEST_COUNTS` | cycle 3.2 | Checkpoint claims 5 when 3 tests defined |
| `VIOLATION_TEST_COUNTS_PARAMETRIZED` | cycle 3.3 | test_foo[param1]/[param2] counted correctly |
| `VIOLATION_RED_IMPLAUSIBLE` | cycle 4.2 | RED expects ImportError on fn created in prior GREEN |
| `AMBIGUOUS_RED_PLAUSIBILITY` | cycle 4.3 | Function exists, behavior test ambiguous |

---

## Key Design Constraints

**D-7 (import approach):** `prepare-runbook.py` has `if __name__ == '__main__':` guard (line 985). Import reusable functions via:
```
importlib.util.spec_from_file_location("prepare_runbook", Path(__file__).parent / "prepare-runbook.py")
```
Reuse: `parse_frontmatter`, `extract_cycles`, `extract_sections`, `assemble_phase_files`, `extract_file_references`, `extract_step_metadata`

**Parsing targets for each subcommand:**
- model-tags: `**Execution Model**:` tags + `File:` references in Changes sections
- lifecycle: `File:` + `Action:` fields across all cycles/steps
- test-counts: `**Test:**` fields in RED phases + "All N tests pass" checkpoint claims
- red-plausibility: RED `**Expected failure:**` text + GREEN `**Changes:**` sections

**Exit codes:** 0 = pass, 1 = violations (blocking), 2 = ambiguous (red-plausibility only)

**Report location:** `plans/<job>/reports/validation-{subcommand}.md` (written regardless of exit code)

**D-5 output:** Subcommand invoked as `validate-runbook.py <subcommand> <path>`. Path can be single .md file or directory with phase files.

**Script entry:** `agent-core/bin/validate-runbook.py` with shebang, `if __name__ == '__main__':` guard.

---

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion.

**Cycle 1.1 (scaffold):** Start here. Test should verify: (a) script imports without error, (b) `--help` shows 4 subcommands, (c) missing subcommand exits with code 1. Report writer function signature: `write_report(subcommand, path, violations, ambiguous=None)` → writes to `plans/<job>/reports/validation-{subcommand}.md`. Note: `<job>` derived from path stem. The `model-tags` subcommand needs `extract_step_metadata` (line 539 in prepare-runbook.py) — include in importlib block.

**Cross-phase dependency:** All subcommand implementations share the importlib import block. Cycle 1.1 establishes this; cycles 1.2+ depend on it. Dependency declarations added to phase headers.

**Checkpoint claims parsing:** Pattern to detect: `"All \d+ tests? pass"` or `"\d+ tests? pass"`. Location in runbook: often in `**Verify GREEN:**` or explicit checkpoint sections. See design Architecture > validate-runbook.py > Subcommand: `test-counts` for full spec.

**Test parametrization:** Use `@pytest.mark.parametrize` for violation fixture pairs. Each subcommand test: valid fixture → exit 0, violation fixture → exit 1. Do not hardcode final test counts in checkpoints — parametrization decisions during expansion determine unique function count.

**Consolidation applied:**
- Phase 5 merged from 2 cycles to 1. Skip flags are argparse-only additions tested via parametrization alongside directory input.

**Growth projection:**
- `validate-runbook.py`: ~40 lines scaffold (argparse, importlib, report writer) + ~50 lines per subcommand (model-tags, lifecycle, test-counts, red-plausibility) + ~20 lines integration = ~260 lines projected. Under 350-line threshold.
- `test_validate_runbook.py`: ~20 lines fixture constants + ~15 lines per test function x ~13 cycles + ~30 lines helpers = ~245 lines projected. Under 350-line threshold.
- No split needed for either file.

**References to include:**
- Design Architecture > validate-runbook.py section for subcommand specs
- Design D-7 for importlib approach
- `prepare-runbook.py` lines 539–572 for `extract_step_metadata` signature and regex
