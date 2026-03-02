# Cycle 2.1 Execution Report: Orchestrator Plan Structured Format

**Date:** 2026-03-02
**Cycle:** 2.1 - Structured step list format
**Status:** GREEN_VERIFIED

## Test Command
```bash
just test tests/test_prepare_runbook_orchestrator.py::TestOrchestratorPlan -xvs
```

## RED Phase Result
Test written successfully. Expected failure confirmed:
- AssertionError: test expected structured header fields (**Agent:**, **Corrector Agent:**, **Type**)
- Current implementation generated prose format with "## Step Execution Order"
- Test assertions for pipe-delimited step list format all failed as expected

## GREEN Phase Result
Implementation completed and all tests pass:
- Modified `generate_default_orchestrator()` in `/Users/david/code/claudeutils-wt/orchestrate-evolution/agent-core/bin/prepare-runbook.py`
- Added structured header with **Agent**, **Corrector Agent**, and **Type** fields
- Changed step list format from prose H2 headers to pipe-delimited entries:
  - Format: `- step-N-M.md | Phase N | model | max_turns [| PHASE_BOUNDARY]`
  - Detects single-phase vs multi-phase to set corrector agent correctly
  - Preserves phase boundary detection and model information
- Maintained backward compatibility:
  - Kept Phase-Agent Mapping table (if phase_agents provided)
  - Added Phase Files section (when phase_dir provided)
  - Inline phases marked with "Execution: inline (Phase N)"
  - Kept Phase Models section (when phase_models provided)
- All 1433 tests pass (1 xfail expected)

## Regression Check
Full test suite results: **1433/1434 passed, 1 xfail**
No regressions introduced. Fixed 4 tests that expected old format:
- `test_prepare_runbook_orchestrator.py`: Updated assertions for new header format
- `test_prepare_runbook_agents.py`: Updated to check agent info in Phase-Agent Mapping table
- `test_prepare_runbook_inline.py`: Inline phase markers preserved
- `test_prepare_runbook_mixed.py`: Updated regex patterns for step entry format

## Refactoring
- Ran `just lint`: All checks passed
- Ran `just precommit`: Passed with no warnings

## Files Modified
- `/Users/david/code/claudeutils-wt/orchestrate-evolution/agent-core/bin/prepare-runbook.py` (lines 1288-1419)
  - Rewrote `generate_default_orchestrator()` function with new structured format
  - Detects runbook type (tdd vs general) from cycles presence
  - Calculates unique phases to determine corrector agent name
  - Builds pipe-delimited step list with phase/model/max_turns info
  - Preserves all existing sections (Phase-Agent Mapping, Phase Models, Phase Files)
- `/Users/david/code/claudeutils-wt/orchestrate-evolution/tests/test_prepare_runbook_orchestrator.py` (3 new tests)
  - `test_orchestrator_plan_structured_format()`: Validates structured header and pipe-delimited steps
  - `test_orchestrator_plan_single_phase_corrector_agent()`: Validates single-phase corrector as "none"
  - Existing tests updated to check Phase Files section
- `/Users/david/code/claudeutils-wt/orchestrate-evolution/tests/test_prepare_runbook_agents.py` (2 tests updated)
  - Updated assertion format to check Phase-Agent Mapping table instead of prose Agent: lines
- `/Users/david/code/claudeutils-wt/orchestrate-evolution/tests/test_prepare_runbook_mixed.py` (1 test updated)
  - Updated regex to match new step entry format
  - Adapted PHASE_BOUNDARY detection to new structured format

## Stop Condition
None - cycle completed successfully.

## Decision Made
Preserved backward compatibility by:
- Keeping all optional sections (Phase-Agent Mapping, Phase Models, Phase Files)
- Adding inline execution markers for inline phases
- Detecting phase count to determine corrector agent presence
- Determining runbook type from content (cycles vs steps)

## Output Format Changes Summary

### Old Format (Prose H2 per step)
```markdown
# Orchestrator Plan: test-job

Execute steps sequentially using crew-test-job agent.

## Step Execution Order

## step-1-1 (Cycle 1.1)
Execution: steps/step-1-1.md

## step-1-2 (Cycle 1.2) — PHASE_BOUNDARY
Execution: steps/step-1-2.md
[Last item of phase 1. Insert functional review checkpoint...]
```

### New Format (Structured header + Pipe-delimited)
```markdown
# Orchestrator Plan: test-job

**Agent:** test-job-task
**Corrector Agent:** test-job-corrector
**Type:** tdd

## Phase-Agent Mapping

...

## Steps

- step-1-1.md | Phase 1 | sonnet | 30
- step-1-2.md | Phase 1 | sonnet | 30 | PHASE_BOUNDARY
- step-2-1.md | Phase 2 | opus | 30 | PHASE_BOUNDARY
```

The new format is more machine-readable (pipe-delimited) and includes structured metadata fields while preserving all necessary information for execution.
