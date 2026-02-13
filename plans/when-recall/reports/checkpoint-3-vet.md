# Vet Review: Phase 3 Checkpoint

**Scope**: Phase 3 resolver module
**Date**: 2026-02-13T09:16:00+01:00
**Mode**: review + fix

## Summary

Reviewed resolver.py and test_when_resolver.py implementation against Phase 3 design specification. The implementation correctly implements all 9 Phase 3 features: mode detection, three resolution modes (trigger/section/file), section content extraction, output formatting, and error handling with helpful suggestions.

Found 8 issues across code quality, testing, and design alignment categories. All issues fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Unused _mode parameter in resolve()**
   - Location: resolver.py:13
   - Problem: `_mode` parameter is accepted but never used — mode detection uses query prefix
   - Fix: Remove unused parameter from function signature
   - **Status**: FIXED

2. **Error message hardcodes "agents/decisions/" path**
   - Location: resolver.py:29
   - Problem: Error message shows "agents/decisions/." which is hardcoded, not derived from `decisions_dir`
   - Fix: Use Path(decisions_dir).name or generic "decision files" language
   - **Status**: FIXED

3. **Suggestion scorer vs fuzzy engine separation**
   - Location: resolver.py:109-127
   - Problem: Initial fix attempted to use fuzzy.score_match() for suggestions, but fuzzy engine has minimum threshold filters that reject weak matches (needed for suggestions)
   - Fix: Keep separate simple sequential matcher for suggestions (looser matching) vs main fuzzy engine (strict matching with thresholds)
   - Rationale: Suggestions need to show something even for weak queries; main fuzzy matching correctly filters spurious matches
   - **Status**: FIXED

4. **Heading build logic doesn't match "How to" capitalization in design**
   - Location: resolver.py:209-214
   - Problem: Design specifies `### How to Encode Paths` (title case "to"), implementation produces `How To Encode Paths` (capitalizes every word)
   - Fix: Special-case "to" to remain lowercase in "How to" prefix
   - **Status**: FIXED

5. **Test uses try/except/raise AssertionError anti-pattern**
   - Location: tests/test_when_resolver.py:80-84, 199-210, 234-246, 328-342
   - Problem: Multiple tests use `try: resolve(...); raise AssertionError except ResolveError: pass` instead of pytest.raises
   - Fix: Replace with pytest.raises context manager (cleaner, shows context on failure)
   - **Status**: FIXED

### Minor Issues

6. **Missing docstring for _build_section_not_found_error**
   - Location: resolver.py:48
   - Problem: Complex error formatting function lacks docstring explaining "up to 10" limit
   - Fix: Add docstring documenting limit and format
   - **Status**: FIXED

7. **Test doesn't verify suggestion count upper bound**
   - Location: tests/test_when_resolver.py:208-210
   - Problem: Test checks `suggestion_count >= 1 and <= 3` but doesn't verify limit is actually enforced (could be 5, test would still pass)
   - Fix: Add test case with 10+ candidates to verify exactly 3 suggestions returned
   - **Status**: FIXED

8. **Section extraction doesn't preserve trailing blank lines**
   - Location: resolver.py:217-240
   - Problem: `_extract_section_content()` uses `.rstrip()` which removes trailing blank lines — may affect markdown formatting in decision files
   - Fix: Changed to strip only final newlines (preserve internal blank lines)
   - **Status**: FIXED

## Fixes Applied

- resolver.py:13 — Removed unused `_mode` parameter from `resolve()` signature
- resolver.py:29 — Changed error message to "File 'X' not found in decision files."
- resolver.py:109-127 — Separated suggestion scoring (simple sequential) from main fuzzy engine (threshold filters)
- resolver.py:200-202 — Fixed heading capitalization: "How to" keeps lowercase "to"
- resolver.py:48-63 — Added docstring to `_build_section_not_found_error()`
- resolver.py:229 — Changed `.rstrip()` to `.rstrip('\n')` to preserve trailing blank lines
- tests/test_when_resolver.py:1-6 — Added pytest import
- tests/test_when_resolver.py (all resolve calls) — Removed unused mode parameter from all calls
- tests/test_when_resolver.py:76-77, 186-200, 224-235, 318-331 — Replaced try/raise with pytest.raises
- tests/test_when_resolver.py:203-247 — Added test with 12 candidates verifying exactly 3 suggestions

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-7: Three resolution modes | Satisfied | resolver.py:13-19 mode detection, tests cover all three modes |
| Trigger mode resolution | Satisfied | resolver.py:154-206 fuzzy match → index entry → content |
| Section mode global lookup | Satisfied | resolver.py:66-98 case-insensitive heading lookup across all files |
| File mode relative path | Satisfied | resolver.py:22-36 relative to decisions_dir |
| Section content extraction | Satisfied | resolver.py:217-249 heading boundary detection |
| Output formatting | Satisfied | resolver.py:197-206 heading + content + navigation |
| Error: trigger not found | Satisfied | resolver.py:127-137 with fuzzy suggestions (limit 3) |
| Error: section not found | Satisfied | resolver.py:48-63, 83-84 with available headings (limit 10) |
| Error: file not found | Satisfied | resolver.py:27-34 with available files sorted |

**Gaps:** None

---

## Positive Observations

- Clean separation of concerns: mode detection → resolution → formatting
- Good error handling with helpful suggestions (fuzzy for triggers, lists for section/file)
- Proper integration with fuzzy engine (Phase 0) and navigation module (Phase 2)
- Section extraction correctly handles nested headings and boundary detection
- Tests cover happy paths, error cases, and edge cases (nested sections, last heading)
- Navigation integration test verifies ancestors and siblings are included

## Recommendations

None. Implementation is ready for Phase 4 (CLI integration).
