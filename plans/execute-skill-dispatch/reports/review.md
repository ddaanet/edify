# Review: execute-skill-dispatch fix findings

**Scope**: Uncommitted changes addressing deliverable-review.md findings — 3 files (agent-core submodule hook, inference.py, test file)
**Date**: 2026-03-01
**Mode**: review + fix

## Summary

Three targeted changes address all four findings from the deliverable review: the Major private API import replaced with `infer_state()`, and three Minor issues (docstring accuracy, missing `r` mode test, fragile split assertion). Each change is minimal and correctly scoped. All 8 tests in `test_userpromptsubmit_execute.py` pass.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Behavior difference in empty-artifact edge case**
   - Location: `agent-core/hooks/userpromptsubmit-shortcuts.py:874-888`
   - Note: Old code called `_determine_status` → `_derive_next_action` for any existing plan directory, including those with no recognized artifacts (returns `"requirements"` status → `/design plans/{name}/requirements.md`). New code calls `infer_state` which returns `None` for empty-artifact directories (line 163-164 of inference.py), falling back to the session.md command. This is a behavior difference in a degenerate edge case (plan dir exists, zero artifacts). The new behavior is safer — planstate should not derive a command from an empty directory.
   - **Status**: DEFERRED — edge case doesn't occur in practice; new behavior is safer than the old behavior.

## Fixes Applied

None — all findings resolved by the changes being reviewed. No further edits needed.

## Review Criteria Evaluation

### 1. Does the `infer_state()` replacement preserve identical behavior?

Mostly yes, with one degenerate edge case (classified DEFERRED above).

For all normal cases:
- Plan dir doesn't exist → old: `plan_dir.exists()` guard → None. New: `infer_state` returns None (line 159). **Identical.**
- Plan dir exists with artifacts → old: `_determine_status` → `_derive_next_action` → command. New: `infer_state` runs same chain internally, returns `state.next_action`. **Identical.**
- Post-ready states (rework, reviewed, delivered) → old: `_derive_next_action` returns `""` → None. New: `infer_state` returns state with `next_action=""` → None. **Identical.**

Edge case: plan dir exists, zero recognized artifacts → old: returns `/design plans/{name}/requirements.md`. New: returns None, falls back to session.md command. **Behavior differs, new is safer.**

The `plan_dir.exists()` guard from the old code is subsumed by `infer_state`'s own existence check. No behavioral regression on the happy path.

### 2. Does the new `r` mode test correctly verify C-3 backward compatibility?

Yes. `test_r_does_not_inject` calls `call_hook("r")` with a session.md containing a pending task, then asserts:
- `"[#resume]" in ctx` — confirms the `r` expansion fired correctly
- `"Invoke:" not in ctx` — confirms no task injection occurred

The implementation gate is `if first_command == "x":` at line 991, which correctly excludes `"r"`. The test proves this gate fires as expected, matching C-3's explicit call-out of `#resume`.

### 3. Is the docstring fix accurate against the actual `_determine_status` implementation?

Yes. `_determine_status` (inference.py:65-84) implements: lifecycle → ready → planned → designed → outlined → requirements. The updated `infer_state` docstring now reads "Priority: lifecycle > ready > planned > designed > outlined > requirements" which matches exactly. The old docstring omitted `lifecycle` which is checked first and has highest priority.

### 4. Is the assertion fix equivalent to the original intent?

Yes, and stronger. The original:
```python
assert "/commit" not in ctx.split("Invoke:")[-1]
```
Split on `"Invoke:"`, took the last segment, and checked for `/commit`. Fragile: if no `"Invoke:"` is present, `split()[-1]` is the whole string, making the assertion trivially pass. The new:
```python
assert "Invoke: /commit" not in ctx
```
Directly tests the injected form — simpler, not fragile, and directly expresses the requirement.

---

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
