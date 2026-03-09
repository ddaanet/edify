# Review: bootstrap-tag-support implementation

**Scope**: agent-core/bin/prepare-runbook.py, tests/test_prepare_runbook_bootstrap.py
**Date**: 2026-03-08T00:00:00
**Mode**: review + fix

## Summary

Implementation adds Bootstrap marker detection to `split_cycle_content` (3-tuple return), generates `step-X-Y-bootstrap.md` files when Bootstrap section is present, adds BOOTSTRAP role to orchestrator plan, and fixes mixed-type Common Context injection in `assemble_phase_files`. Full test suite passes (1621/1622, 1 pre-existing xfail). Two minor issues found and fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`split_cycle_content` silently ignores malformed Bootstrap (no `---` separator)**
   - Location: `agent-core/bin/prepare-runbook.py:1351-1358`
   - Note: When `**Bootstrap:**` marker is found but no `---` separator follows, `bootstrap_part` stays `""` and `remainder` stays as the full content. The bootstrap text leaks into the RED phase step file without any warning. The no-separator case degrades silently — the author gets a test step containing bootstrap instructions, no error, no indication something is wrong.
   - **Status**: FIXED

2. **`TestBootstrapSplit` missing malformed-Bootstrap coverage**
   - Location: `tests/test_prepare_runbook_bootstrap.py` — `TestBootstrapSplit` class
   - Note: The split tests cover the with-bootstrap and without-bootstrap paths but not the case where `**Bootstrap:**` is present but `---` separator is missing. This is the silent-failure path identified above. Adding a test makes the behavior explicit (documented degradation vs. warning).
   - **Status**: FIXED

## Fixes Applied

- `agent-core/bin/prepare-runbook.py:1353-1363` — Added `else` branch when `**Bootstrap:**` marker found but no `---` separator: prints WARNING to stderr. Degradation behavior preserved (bootstrap text included in remainder/RED); warning surfaces the misconfiguration to the author.
- `tests/test_prepare_runbook_bootstrap.py:110-127` — Added `test_split_bootstrap_missing_separator` to `TestBootstrapSplit` class. Asserts empty bootstrap, leaked bootstrap text in RED, and WARNING in stderr. Uses `capsys` fixture consistent with pytest patterns.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Fix mixed-type Common Context injection (any phase has cycles, not just first) | Satisfied | `assemble_phase_files` uses `has_any_cycles` flag set in loop over all phase files; `TestMixedCommonContext.test_mixed_assembly_injects_default_common_context` covers it |
| `split_cycle_content` returns 3-tuple (bootstrap, red, green) | Satisfied | `prepare-runbook.py:1335-1367`; `TestBootstrapSplit` covers both paths |
| Generate `step-X-Y-bootstrap.md` files when Bootstrap section present | Satisfied | `prepare-runbook.py:1801-1810`; `TestBootstrapStepFiles.test_bootstrap_generates_three_step_files` covers it |
| Add BOOTSTRAP role to orchestrator plan | Satisfied | `generate_default_orchestrator` builds BOOTSTRAP item with ordering offset; `TestBootstrapOrchestrator.test_orchestrator_includes_bootstrap_items` + ordering assertion cover it |
| Backward compatibility: cycles without Bootstrap produce same output | Satisfied | `TestBootstrapStepFiles.test_no_bootstrap_generates_two_step_files` + `TestBootstrapOrchestrator.test_orchestrator_no_bootstrap_unchanged` cover it |

---

## Positive Observations

- `has_any_cycles` scan over all phase files (not just first) is the correct fix for mixed-type detection. Comment at line 895 explains the intent.
- Bootstrap ordering in the orchestrator uses `minor - 1.0` sort key. Verified empirically with two-cycle scenario: 1.2-bootstrap correctly sorts after 1.1-impl.
- `split_cycle_content` docstring accurately describes the 3-way split behavior and edge cases.
- Test class structure clearly separates the three behavioral concerns (mixed context injection, split function, file generation, orchestrator).
- Integration tests (`TestBootstrapStepFiles`) use `setup_git_repo` and `setup_baseline_agents` helpers consistently with existing test patterns.
- `generate_default_orchestrator` calls `split_cycle_content` to detect bootstrap presence — no duplication of the detection logic.
