# Review: Fix when-resolve.py

**Scope**: Uncommitted changes to `src/claudeutils/when/cli.py`, `src/claudeutils/when/resolver.py`, `tests/test_when_cli.py`, `tests/test_when_resolver.py`; staged deletion of `src/claudeutils/when/navigation.py` and `tests/test_when_navigation.py`
**Date**: 2026-02-27
**Mode**: review + fix

## Summary

The implementation delivers all five stated design intents: stdin support, deduplication, navigation removal, `Source:` reference, and `click.UsageError` for no-queries. Helpers are cleanly extracted (`_collect_queries`, `_resolve_queries`). Eight new tests cover the added behaviour. One stale docstring was found and fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Stale docstring in `test_resolve_output_format`**
   - Location: `tests/test_when_resolver.py:189`
   - Note: Docstring says "combines content and navigation links" — navigation was removed. Describes old behaviour.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_when_resolver.py:189` — Updated docstring from "combines content and navigation links" to "combines content with source reference"

## Requirements Validation

| Design intent | Status | Evidence |
|---|---|---|
| Deduplicate fuzzy matches | Satisfied | `_resolve_queries` uses `seen: set[str]`, tests `test_dedup_identical_results` / `test_dedup_preserves_distinct` |
| Accept queries on stdin | Satisfied | `_collect_queries` reads `sys.stdin` when not a tty; 5 stdin tests |
| Remove sibling/related navigation links | Satisfied | `navigation.py` deleted (staged), `fuzzy, navigation` import removed from `resolver.py` |
| Replace broader links with `Source:` path | Satisfied | `resolver.py:234` builds `source_path = f"agents/decisions/{section_filename}"`, `test_resolve_output_format` asserts `"Source: agents/decisions/testing.md"` in result |
| `click.UsageError` with `# noqa: TRY003` for no-queries | Satisfied | `cli.py:72`; lint passes clean |

## Positive Observations

- Helper extraction is appropriate: `_collect_queries` and `_resolve_queries` have single responsibilities and are individually testable.
- `required=False` on the Click argument plus manual guard (`if not all_queries`) is the correct pattern for supporting stdin as the query source — Click's built-in `required=True` would reject stdin-only invocations.
- Deduplication uses exact string equality on resolved content, not a prefix heuristic — appropriate given resolved entries are structured, repeatable strings.
- Narration comments removed from `cli.py` (removed "Print successes first" and "Then errors to stdout" banners).
- 27/27 tests pass, lint clean.
