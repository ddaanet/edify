# Review: Phase 2 Checkpoint — `derive_slug` ValueError catch

**Scope**: `src/claudeutils/worktree/cli.py`, `tests/test_worktree_new_creation.py`
**Date**: 2026-02-23
**Mode**: review + fix

## Summary

Phase 2 implemented the `derive_slug` ValueError catch in `new()` and added `test_new_invalid_task_name_clean_error`. The implementation correctly uses `_fail()` from Phase 1, outputs to stdout (via `click.echo`), and exits with code 2. All 11 tests in the file pass; full suite clean.

No issues were found. Design anchoring verified against outline.md Key Decision 2 and Key Decision 3.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

None required.

## Design Anchoring

Verified against `plans/worktree-error-output/outline.md`:

- **Key Decision 2** (catch ValueError, exit 2): `_fail(str(e), code=2)` at cli.py:192. Satisfied.
- **Key Decision 3** (`_fail()` helper): Used correctly — `click.echo(msg)` + `raise SystemExit(code)`. Satisfied.
- **stdout, not stderr**: `_fail()` calls `click.echo(msg)` without `err=True`. Output goes to stdout. Satisfied.
- **No traceback**: `try/except ValueError` wraps the call; exception is caught before propagation. `"Traceback" not in result.output` and `"ValueError" not in result.output` assertions pass. Satisfied.

## Test Quality

`test_new_invalid_task_name_clean_error` (cli.py:326–341):

- **Behavior-focused**: Asserts exit code, output content, and absence of raw exception artifacts — not implementation details.
- **Meaningful assertions**: Exit code 2 (not just non-zero), specific error substring `"forbidden character '_'"`, explicit traceback absence.
- **Correct setup**: Uses `init_repo` fixture matching the pattern from sibling tests. No unnecessary mocking.
- **Assertion accuracy**: `"forbidden character '_'" in result.output` matches the actual validation message `"contains forbidden character '_'"`. Substring match is correct.

## Implementation Quality

`new()` ValueError catch (cli.py:188–192):

- Catch placed inside the `if task_name:` block, correctly scoped — only fires when task_name is provided (the only call path to `derive_slug`).
- `_fail(str(e), code=2)` uses the Phase 1 helper as specified.
- `return type Never` on `_fail()` means the outer `try/except` block structure remains clean — no dead code after the catch.

## Phase 3 Scope (OUT — not flagged)

Remaining `err=True` sites (11 occurrences in cli.py) are Phase 3 scope. Not flagged.

## Positive Observations

- TDD cycle executed cleanly: RED confirmed exit code 1 with traceback, GREEN achieved exit code 2 with clean message.
- `_fail()` return type `Never` prevents any control-flow confusion at the call site.
- Test uses CliRunner's default `mix_stderr=True`, consistent with all sibling tests in this file.
