# Runbook Review: when-recall Phases 4-5

**Artifacts**:
- plans/when-recall/runbook-phase-4.md
- plans/when-recall/runbook-phase-5.md

**Date**: 2026-02-12T19:45:00Z
**Mode**: review + fix-all
**Phase types**: Mixed (Phase 4 TDD, Phase 5 general)

## Summary

Combined review of Phase 4 (CLI Integration, 5 TDD cycles) and Phase 5 (Bin Script Wrapper, 2 general steps).

**Issues found:**
- Critical: 0
- Major: 1 (metadata mismatch in Phase 4)
- Minor: 0

**Overall Assessment**: Ready (1 issue fixed)

## Findings

### Major Issues

#### Issue 1: Metadata inaccuracy in Phase 4
**Location**: Phase 4, line 5
**Problem**: Weak Orchestrator Metadata missing from Phase 4. TDD phases should include total cycle count for orchestration.
**Fix**: Added metadata section with cycle count (5 cycles).
**Status**: FIXED

## Fixes Applied

- Phase 4: Added "**Weak Orchestrator Metadata:** Total Cycles: 5" after line 12

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

## Detailed Analysis

### Phase 4: CLI Integration (TDD)

**Structure**: 5 well-scoped TDD cycles building Click CLI wrapper around resolver.

**Cycle quality:**
- **4.1 (Click command setup)**: Proper RED assertions checking importability and Click integration. GREEN focuses on command creation and registration.
- **4.2 (Operator argument)**: Clean validation cycle. RED tests both valid operators (`when`, `how`) and invalid rejection. GREEN uses Click's Choice type for automatic validation.
- **4.3 (Query variadic argument)**: Tests space-joining, dot-prefix preservation, and required argument validation. GREEN implementation clear.
- **4.4 (Invoke resolver)**: Integration cycle connecting CLI to resolver. RED tests output contains resolved content and navigation links. GREEN specifies root detection, resolve call, output.
- **4.5 (Error handling)**: Proper error routing to stderr with exit code 1. Multiple error scenarios tested (trigger not found, section not found, file not found).

**RED/GREEN sequencing**: All cycles follow proper TDD discipline. RED phases specify behavioral assertions before implementation exists.

**File references**: All referenced files validated:
- `src/claudeutils/cli.py` — exists
- `src/claudeutils/when/cli.py` — does not exist (will be created)
- `tests/test_when_cli.py` — does not exist (will be created)

**Prerequisite validation**: Cycle 4.1 includes prerequisite to read existing CLI structure for registration pattern.

**Dependencies**: Correctly states Phase 3 (resolver) dependency.

**No LLM failure modes detected:**
- No vacuous cycles (all test real behavior)
- Foundation-first ordering (setup → arguments → integration → error handling)
- No density issues (each cycle adds distinct behavior)
- No checkpoint gaps (5 cycles, Low-Medium complexity)

### Phase 5: Bin Script Wrapper (General)

**Structure**: 2 straightforward general steps creating thin wrapper script.

**Step quality:**
- **5.1**: Clear objective (create wrapper), implementation steps (shebang, import, chmod), error conditions specified.
- **5.2**: E2E verification step confirming wrapper matches CLI output.

**Validation**: Both steps include validation criteria (help text, output matching).

**File references**: All referenced files validated:
- `agent-core/bin/when-resolve.py` — does not exist (will be created)
- `claudeutils.when.cli.when_cmd()` — depends on Phase 4

**Dependencies**: Correctly states Phase 4 dependency (CLI must be registered).

**No issues detected**: Steps are clear, non-code artifact with appropriate verification.

---

**Ready for next step**: Yes — Phase 4-5 can proceed to execution after metadata fix.
