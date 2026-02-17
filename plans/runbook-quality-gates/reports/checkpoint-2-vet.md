# Vet Review: Phase 2 Checkpoint — lifecycle subcommand

**Scope**: `check_lifecycle()`, `cmd_lifecycle()`, lifecycle test fixtures and tests
**Date**: 2026-02-18
**Mode**: review + fix

## Summary

Phase 2 implements the `lifecycle` subcommand for `validate-runbook.py`. The core logic correctly detects modify-before-create and duplicate-creation violations. Tests cover the three required scenarios. `just dev` passes (983/984, 1 expected xfail). One major issue found: the report format deviates from the design spec (missing required fields). Two minor issues: a repeated-modify edge case produces a misleading violation message, and the report title format doesn't match the spec.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Report missing Runbook path and Date fields**
   - Location: `agent-core/bin/validate-runbook.py:48-53` (`write_report`)
   - Problem: Design spec (design.md) requires `**Runbook:** {path}` and `**Date:** {ISO timestamp}` in the report header. Both are absent. Downstream consumers parsing reports for runbook path or timestamp will find neither.
   - Fix: Add both fields to the report header after `**Result:**`.
   - **Status**: FIXED

2. **Report title format doesn't match spec**
   - Location: `agent-core/bin/validate-runbook.py:49`
   - Problem: Code generates `# Validation: {subcommand}`. Design spec says `# Validation Report: {subcommand}`.
   - Fix: Change to `# Validation Report: {subcommand}`.
   - **Status**: FIXED

### Minor Issues

1. **Repeated-modify produces misleading violation message**
   - Location: `agent-core/bin/validate-runbook.py:132-140`
   - Note: When a file appears first with a modify action (flagged as violation), a subsequent modify on the same file enters the `elif is_modify` branch and generates a second violation: "modified before creation (first seen in Cycle X as 'Modify')". The message is technically accurate but the "first seen as 'Modify'" phrasing is confusing — the original violation was already reported. This edge case is not tested and unlikely to appear in real runbooks, but the message quality could mislead.
   - **Status**: FIXED

## Fixes Applied

- `agent-core/bin/validate-runbook.py:49` — Changed `# Validation: {subcommand}` to `# Validation Report: {subcommand}`
- `agent-core/bin/validate-runbook.py:50-53` — Added `**Runbook:** {path}` and `**Date:** {date}` fields to report header after Result line
- `agent-core/bin/validate-runbook.py:133` — Added guard: if `orig_action` was already a modify-type (itself a prior violation), suppress the redundant "modified before creation" message to avoid confusing duplicate violation entries. Only flag when the original action was something other than modify (i.e., an unrecognized action that was not a creation).

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-3: Lifecycle validation (create before modify, no duplicate creation) | Satisfied | `check_lifecycle` detects both violations; 3 tests cover happy path, modify-before-create, duplicate-create |
| D-7: Changes section parsing with File/Action regex extraction | Satisfied | `re.findall(r"- File: ...Action: ...")` pattern at line 106-108 |
| Exit codes: 0 = pass, 1 = violations | Satisfied | `sys.exit(1 if violations else 0)` at line 153 |

---

## Positive Observations

- `check_lifecycle` correctly differentiates the two violation cases (modify-before-create vs duplicate creation) with distinct, informative messages
- Reuse of `extract_cycles()` from prepare-runbook.py avoids regex duplication (D-7 compliance)
- `VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE` fixture is minimal and directly exercises the bug — no extraneous structure
- Test discovery of the Cycle 2.3 over-implementation was correctly documented in the execution report rather than silently accepted
- `cmd_lifecycle` correctly mirrors `cmd_model_tags` pattern (directory vs file dispatch)
