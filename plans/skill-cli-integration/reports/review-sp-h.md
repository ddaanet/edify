# Review: SP-H Stop Hook Status Display

**Scope**: SP-H implementation — hooks package, stop_status_display.py, tests, settings.json
**Date**: 2026-03-30
**Mode**: review + fix

## Summary

The Stop hook status display implementation is structurally correct: loop guard, trigger detection, ANSI formatting, error fallback, and hook registration all work. Tests pass (12/12) and linter is clean. Two issues found: the hook response omits `additionalContext` (required by D-1 to prevent agent re-render), and the trigger regex uses `$` which permits a trailing newline, creating a potential false positive.

**Overall Assessment**: Needs Minor Changes

---

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Missing `additionalContext` in hook response**
   - Location: `src/edify/hooks/stop_status_display.py:92`
   - Problem: D-1 specifies "`additionalContext` tells agent status was displayed (prevents re-render)". The `process_hook` return value is `{"systemMessage": formatted}` — no `additionalContext` key. Without it the agent has no signal that status was displayed and may re-render by calling `_status` directly or re-emitting the trigger.
   - Fix: Add `"additionalContext": "Status displayed via Stop hook."` to the return dict.
   - **Status**: FIXED

### Minor Issues

1. **Trigger regex permits trailing newline**
   - Location: `src/edify/hooks/stop_status_display.py:21`
   - Note: `re.fullmatch(r"^Status\.$", message)` — Python's `$` matches before a trailing `\n` even in `fullmatch` mode. So `"Status.\n"` is a false positive trigger. The `^` and `$` anchors are also redundant with `fullmatch` (which already anchors to the full string). Using `\Z` instead of `$` matches only at the true end of string.
   - **Status**: FIXED

2. **Missing test for trailing-newline false positive**
   - Location: `tests/test_stop_hook_status.py:15-31`
   - Note: Parametrized table covers `"Status.\nMore text"` → False, but not `"Status.\n"` → should be False. The subtle `$` behavior would not be caught.
   - **Status**: FIXED

---

## Fixes Applied

- `src/edify/hooks/stop_status_display.py:21` — Replace `r"^Status\.$"` with `r"Status\.\Z"` (drop redundant anchors, use `\Z` for true end-of-string)
- `src/edify/hooks/stop_status_display.py:92` — Add `additionalContext` key to hook response per D-1 contract
- `tests/test_stop_hook_status.py:21` — Add `("Status.\n", False)` parametrize case

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-1: Trigger `^Status\.$` exact match | Satisfied (after fix) | `re.fullmatch(r"Status\.\Z", msg)` |
| Loop guard: return None when `stop_hook_active` | Satisfied | `stop_status_display.py:76` |
| ANSI reset: `\033[0m` per line | Satisfied | `format_ansi()` line 54-55 |
| Error handling: "Status unavailable" fallback | Satisfied | `process_hook()` line 87-90 |
| Hook registration: Python hook in Stop array | Satisfied | `settings.json:157` |
| Self-contained: stdlib only | Satisfied | imports: json, re, subprocess, sys |
| Testable: status_fn injection | Satisfied | `process_hook(status_fn=...)` |
| `additionalContext` in response | Partial (before fix) | Missing — fixed at line 92 |

---

## Positive Observations

- `status_fn` injection pattern is clean — no monkeypatching, no mocking framework needed in tests
- Loop guard check is first, before any other work — correct ordering per requirement
- `format_ansi` handles empty string correctly via `splitlines(keepends=True)` semantics
- PEP 758 unparenthesized except (`except A, B, C:`) used correctly for Python 3.14+
- `get_status` raises on failure (doesn't swallow) — `process_hook` catches at the right level
- Hook registered alongside existing `stop-health-fallback.sh` without disrupting it

## Recommendations

None beyond the fixes applied.
