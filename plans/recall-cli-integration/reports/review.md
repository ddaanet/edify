# Review: recall-cli-integration implementation

**Scope**: `recall_cli/` package, tests, CLI registration — git diff from 423d4cd4
**Date**: 2026-02-28T00:00:00
**Mode**: review + fix

## Summary

Implementation delivers a correct `_recall` Click group with three subcommands (`check`, `resolve`, `diff`). All 28 tests pass, precommit is clean. Code follows established patterns and satisfies all FRs and constraints. Four minor issues found: a dead code branch in `artifact.py`, a trivial docstring on `parse_trigger`, a `NoReturn`/`Never` inconsistency with `worktree/cli.py`, and a non-empty `__init__.py` where the outline specified empty.

**Overall Assessment**: Ready (minor issues fixed inline)

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Dead `else []` branch in `parse_entry_keys_section`**
   - Location: `src/claudeutils/recall_cli/artifact.py:42`
   - Note: `heading_found` is only set `True` inside a block that immediately `return`s, so the outer `return None if not heading_found else []` can only be reached with `heading_found == False`. The `else []` branch is unreachable. Simplify to `return None`.
   - **Status**: FIXED

2. **Trivial docstring on `parse_trigger`**
   - Location: `src/claudeutils/recall_cli/artifact.py:5-8`
   - Note: The docstring ("Strips annotation (text after em dash), then detects operator (when/how). If entry lacks operator prefix, prepends 'when'.") restates information already captured by the in-body comments. Per project code quality rules, docstrings should only cover non-obvious behavior; the comments in the body are sufficient.
   - **Status**: FIXED

3. **`NoReturn` instead of `Never` in `_fail`**
   - Location: `src/claudeutils/recall_cli/cli.py:7,16`
   - Note: Outline specifies "`_fail(msg, code=1) -> Never` — same 3-line pattern as `worktree/cli.py:38`". `worktree/cli.py` uses `Never` from `typing`. Implementation uses `NoReturn`. Both are semantically equivalent, but project requires Python ≥3.14 where `Never` is available. Fix for consistency with stated pattern.
   - **Status**: FIXED

4. **Non-empty `__init__.py`**
   - Location: `src/claudeutils/recall_cli/__init__.py:1`
   - Note: Outline specifies `__init__.py` as "empty". File contains `"""Recall artifact validation and resolution tool."""`. The docstring provides no value on a package init that serves only as namespace marker. However, ruff D104 requires a docstring in public packages — so the fix is to replace with a minimal module-purpose docstring rather than empty.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/recall_cli/artifact.py:42` — Removed dead `else []` branch; simplified to `return None`; also removed now-unused `heading_found` variable (ruff F841)
- `src/claudeutils/recall_cli/artifact.py:5-8` — Replaced verbose multi-line `parse_trigger` docstring with minimal one-liner `"Strip annotation and normalize operator prefix for resolver lookup."` (ruff D103 requires at least a one-liner for public functions; in-body comments carry the detail)
- `src/claudeutils/recall_cli/cli.py:7,16` — Changed `NoReturn` import to `Never`, updated `_fail` return annotation to match `worktree/cli.py` pattern
- `src/claudeutils/recall_cli/__init__.py:1` — Replaced wordy module docstring with minimal `"Recall artifact validation and resolution CLI."` (ruff D104 requires module docstring on public packages)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: `_recall check <job>` structural validation | Satisfied | `cli.py:32-56`; three failure modes (missing file, missing section, no entries); exit 0 on ≥1 entry |
| FR-2: `_recall resolve` artifact + argument modes | Satisfied | `cli.py:86-135`; artifact strict exit 1 on any failure; argument best-effort exit 0 if ≥1 resolves |
| FR-3: `_recall diff <job>` files since artifact mtime | Satisfied | `cli.py:138-200`; git log --since mtime; excludes artifact; dedup+sort; exit 0 always |
| FR-4: Click group registered as hidden `_recall` | Satisfied | `cli.py:25`; `hidden=True`; `cli.py:148` registration in main CLI |
| FR-5: LLM-native output — all stdout, exit codes | Satisfied | `_fail` writes to stdout; no stderr calls in `recall_cli/`; exit codes match spec |
| C-1: Delegate to `when.resolver.resolve()` | Satisfied | `cli.py:11,115`; no independent resolution |
| C-2: Project root via `CLAUDE_PROJECT_DIR` | Satisfied | `cli.py:37,98,147`; `Path(os.getenv("CLAUDE_PROJECT_DIR", "."))` |
| C-3: No hardcoded paths in module code | Satisfied | Paths derived dynamically from `project_root` |
| C-4: `## Entry Keys` is terminal section | Satisfied | `artifact.py:36`; inner loop reads to EOF with no stop on next heading |

**Prototype deletion:** `recall-check.sh`, `recall-resolve.sh`, `recall-diff.sh` removed from `agent-core/bin/`. No dangling references in active code (agent-core skills, .claude/, agents/ all use `claudeutils _recall` correctly). Remaining references in `plans/recall-cli-integration/requirements.md` and `plans/recall-cli-integration/runbook.md` are historical plan artifacts, not active invocations.

---

## Positive Observations

- `artifact.py` separation is clean — `parse_entry_keys_section` and `parse_trigger` have clearly distinct responsibilities; `check` uses only the former, `resolve` uses both
- Null entry handling is correct: `check` exits 0 for null entry (count check passes), `resolve` silently skips it (`query == "null"` branch at `cli.py:111`)
- Content-level dedup via `seen: set[str]` is correctly placed — deduplicates resolved content, not triggers, matching the design spec
- `diff` tests use real git repos in `tmp_path` per the "When Preferring E2E Over Mocked Subprocess" decision
- Error messages are facts-only with no suggested causes or recovery actions — satisfies "When CLI Error Messages Are LLM-Consumed" decision
- Integration test file correctly verifies both `_recall` hidden from `--help` and `recall` (effectiveness analysis) unaffected
