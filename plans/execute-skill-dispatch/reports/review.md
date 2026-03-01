# Review: Execute Skill Dispatch — UPS hook + execute-rule prose + tests

**Scope**: Uncommitted working tree changes implementing FR-1/2/3 for execute-skill-dispatch
**Date**: 2026-03-01
**Mode**: review + fix

## Summary

The implementation adds `_extract_execute_command()`, `_try_planstate_command()`, and `_extract_plan_name()` to the UPS hook, injects the first eligible task's command into additionalContext when `x` fires, updates execute-rule.md MODE 2 prose to explicitly state the invocation contract, and moves the TestExecuteCommandInjection class from the shortcuts test file into a dedicated `test_userpromptsubmit_execute.py` with proper fixture types.

Requirements FR-1, FR-2, FR-3 are satisfied. C-1 (performance) is satisfied via lazy planstate import inside `_try_planstate_command`. C-2 (structural fix) is satisfied. C-3 (backward compat) is satisfied — non-`x` paths are unchanged.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`_extract_execute_command` docstring misstates priority ordering**
   - Location: `agent-core/hooks/userpromptsubmit-shortcuts.py:899`
   - Note: "Priority: planstate-derived > in-progress [>] > pending [ ]" is misleading. Planstate doesn't supersede in-progress task selection — it overrides the command *for whichever task is selected*. The actual logic is: select in-progress first (or pending if none), then substitute planstate command if available.
   - **Status**: FIXED

2. **Canceled task fixture uses wrong marker character**
   - Location: `tests/test_userpromptsubmit_execute.py:43` and `tests/test_userpromptsubmit_shortcuts.py:373` (removed class)
   - Note: `test_x_skips_non_eligible_tasks` uses `[-]` (ASCII hyphen) for the canceled task marker, but execute-rule.md specifies `[–]` (en-dash U+2013). Both are filtered correctly by `pending_pattern` (which only matches `\[\s*\]`), so the test is functionally correct. However, the fixture doesn't match canonical session.md format — a test should use real-world input.
   - **Status**: FIXED

3. **`test_x_uses_planstate_command_over_session` assertion is weak**
   - Location: `tests/test_userpromptsubmit_execute.py:125`
   - Note: `assert "/runbook" in ctx.split("Invoke:")[-1]` checks only that `/runbook` appears after the Invoke directive. The planstate infers `designed` from presence of `design.md`, yielding `/runbook plans/my-plan/design.md`. Asserting the full expected command is more precise and catches regressions in the command template.
   - **Status**: FIXED

4. **No backward-compat test for `xc` not injecting**
   - Location: `tests/test_userpromptsubmit_execute.py`
   - Note: C-3 states backward compatibility must be preserved for non-`x` modes. `xc` also executes tasks but injection is intentionally not added. A test confirming `xc` doesn't inject confirms the scope boundary is enforced.
   - **Status**: FIXED

## Fixes Applied

- `agent-core/hooks/userpromptsubmit-shortcuts.py:899` — Rewrote `_extract_execute_command` docstring priority note to accurately describe task selection then command override logic
- `tests/test_userpromptsubmit_execute.py:43` — Changed canceled task marker from `[-]` to `[–]` (en-dash) to match canonical session.md format
- `tests/test_userpromptsubmit_execute.py:125` — Strengthened planstate priority assertion to check full command string instead of just `/runbook` prefix
- `tests/test_userpromptsubmit_execute.py` — Added `TestExecuteBackwardCompat.test_xc_does_not_inject` to confirm xc mode doesn't inject Invoke directive (C-3 backward compat)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Execute mode invokes task command as skill call | Satisfied | `execute-rule.md:101` explicitly states "Invoke the task's backtick command — via Skill tool for `/skill` commands, or Bash for script commands" |
| FR-2: UPS hook injects task command for execute mode | Satisfied | `_extract_execute_command()` + main() injection at `userpromptsubmit-shortcuts.py:996-998`; planstate priority at `:929-932` and `:943-946` |
| FR-3: Execute-rule prose aligns with structural enforcement | Satisfied | `execute-rule.md:101` MODE 2 behavior updated; no contradiction with hook injection |
| C-1: Hook performance budget | Satisfied | `_try_planstate_command` imports planstate lazily (inside try block); only called when plan metadata is present |
| C-2: Structural fix, not prose strengthening | Satisfied | Hook injection (structural) is primary; prose update is reinforcement |
| C-3: Backward compat — non-skill commands, resume mode unchanged | Satisfied | Injection is gated on `first_command == "x"` only; `xc`/`r`/`s` paths unchanged |

---

## Positive Observations

- Lazy import of `claudeutils.planstate.inference` inside `_try_planstate_command` is correct C-1 design — zero overhead for prompts without plan metadata
- Two-pass search (in-progress first, then pending) matches the priority semantics from execute-rule.md without explicit skip-list logic
- `pending_pattern` and `in_progress_pattern` filter all non-pending/non-in-progress markers by construction (pattern only matches `\[\s*\]` and `\[>\]`) — no explicit blocklist needed, cleaner than alternatives
- Test file split is clean: `test_userpromptsubmit_execute.py` covers FR-2 exclusively, proper fixture types (`Path`/`pytest.MonkeyPatch`), no `Any` leakage
- Exception-swallowing in `_try_planstate_command` with `except Exception: return None` is correct for a hook — planstate failure should degrade gracefully to session.md command, not abort injection

## Recommendations

- `xc` inject gap: if `xc` should also inject (same task-start semantics), that's a separate FR with its own acceptance criteria. Current scope correctly excludes it per requirements.
