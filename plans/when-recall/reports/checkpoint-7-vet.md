# Vet Review: Phase 7 Checkpoint

**Scope**: Phase 7 — Key compression module (compress.py) and CLI wrapper
**Date**: 2026-02-13T14:00:00Z
**Mode**: review + fix

## Summary

Phase 7 implements key compression functionality: load heading corpus from decision files, generate candidate triggers via word-drop algorithm, verify uniqueness via fuzzy scoring, and suggest minimal unique triggers. Implementation includes compress.py module, comprehensive tests, and CLI wrapper.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Test assertion too weak — compress_key fallback not verified**
   - Location: tests/test_when_compress_key.py:138-141
   - Problem: Test 3 creates tight corpus but doesn't assert fallback to full heading. Current assertions (`isinstance`, `len > 0`) pass for any non-empty string.
   - Suggestion: Assert `result3 == "how to encode paths"` to verify fallback behavior explicitly.
   - **Status**: FIXED

2. **CLI wrapper error output inconsistent with project convention**
   - Location: agent-core/bin/compress-key.py:12
   - Problem: Usage message prints to stderr, but project convention is `sys.stderr` for errors and `sys.stdout` for usage (based on `agents/decisions/implementation-notes.md` "Error output pattern").
   - Suggestion: Keep stderr for actual errors, but this is usage which is often stdout.
   - **Status**: DEFERRED — Further investigation shows both patterns exist. Usage to stderr is acceptable (prevents pollution of piped output).

### Minor Issues

1. **Missing edge case test — empty corpus**
   - Location: tests/test_when_compress_key.py
   - Note: `verify_unique` has empty corpus guard (`if not corpus: return False`) but no test coverage for this case.
   - **Status**: FIXED

2. **Missing edge case test — single-heading corpus**
   - Location: tests/test_when_compress_key.py
   - Note: `verify_unique` returns True when `len(ranked) == 1` but no test verifies this path.
   - **Status**: FIXED

3. **Comment typo in compress.py**
   - Location: src/claudeutils/when/compress.py:60
   - Note: `"drop trailing 's'"` — technically removing trailing 's', not "dropping trailing s from word list". Minor clarity issue.
   - **Status**: DEFERRED — Comment is sufficiently clear in context.

## Fixes Applied

1. **tests/test_when_compress_key.py:138-141** — Added explicit fallback assertion
2. **tests/test_when_compress_key.py** — Added `test_verify_unique_edge_cases()` for empty corpus and single-heading corpus

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Load heading corpus | Satisfied | compress.py:10-34, test_load_heading_corpus |
| Generate candidate triggers | Satisfied | compress.py:37-69, test_generate_candidates |
| Verify uniqueness | Satisfied | compress.py:72-100, test_uniqueness_verification |
| Suggest minimal trigger | Satisfied | compress.py:103-126, test_suggest_minimal_trigger |
| CLI wrapper | Satisfied | agent-core/bin/compress-key.py, shebang present |

**Gaps:** None. All Phase 7 features implemented and tested.

---

## Positive Observations

- Test coverage is comprehensive — edge cases, empty directory, structural heading exclusion
- Fuzzy integration is clean — proper use of `rank_matches` with limit=2
- Algorithm correctness — word-drop via combinations, singularization, sorting by length
- CLI wrapper follows project patterns — shebang, sys.argv handling, default decisions_dir
- Edge case handling in `verify_unique` — empty corpus guard, single-match return
- Test assertions are behavior-focused — verify actual outputs, not just structure
- Code clarity — clear function names, docstrings explain behavior

## Recommendations

None. Implementation is complete and correct. Minor issues fixed.
