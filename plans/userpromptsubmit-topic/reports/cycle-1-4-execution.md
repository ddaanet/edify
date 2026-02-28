# Cycle 1.4: Resolve matched entries with error-path coverage

**Timestamp:** 2026-03-01

## Execution Report

**Status:** GREEN_VERIFIED

**Test command:** `pytest tests/test_recall_topic_matcher.py::test_resolve_entries -v`

**RED result:** FAIL as expected (ImportError: cannot import name 'resolve_entries')

**GREEN result:** PASS (3/3 parametrized test cases pass)

**Regression check:** 1371/1372 passed, 1 xfail (no new regressions)

**Refactoring:**
- Fixed docstring formatting (D205: 1 blank line required between summary and description)
- Restructured as proper multi-line docstring with test case description

**Files modified:**
- `/Users/david/code/claudeutils-wt/ups-topic-injection/src/claudeutils/recall/topic_matcher.py` — added `ResolvedEntry` dataclass, `_capitalize_heading()` helper, `resolve_entries()` function; imported `extract_section` and `Path`
- `/Users/david/code/claudeutils-wt/ups-topic-injection/src/claudeutils/when/resolver.py` — renamed `_extract_section()` → `extract_section()` (public API), updated internal callers at lines 117 and 225
- `/Users/david/code/claudeutils-wt/ups-topic-injection/tests/test_recall_topic_matcher.py` — added parametrized test with 3 cases (happy path, missing file, missing section); added import for `resolve_entries` and `Path`

**Stop condition:** none

**Decision made:**
- `ResolvedEntry` dataclass holds content, source_file Path, and original entry
- Heading capitalization replicates resolver.py pattern: preserve all-caps, capitalize normal words
- Both "When {key}" and "How to {key}" patterns tried; first match wins (silent skip if neither matches)
- Test parametrization covers: file + section exist, file missing, section missing (all silent skip scenarios per FR-3)
- Happy path verifies content extraction includes heading text and body text
