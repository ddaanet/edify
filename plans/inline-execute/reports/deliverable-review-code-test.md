# Deliverable Review: triage-feedback.sh + tests

**Scope**: `agent-core/bin/triage-feedback.sh` (83 lines), `tests/test_triage_feedback.py` (372 lines)
**Date**: 2026-02-27
**Mode**: review + fix
**Design reference**: plans/inline-execute/outline.md (D-2, FR-5, FR-6, FR-7, C-3, NFR-2)

## Summary

Script implements evidence collection and triage comparison per D-2. Three evidence signals (FR-5), divergence heuristics (FR-6), and log append (FR-7) all present. Tests cover the main paths (13 tests, all passing). Two conformance issues found: inline divergence message omits evidence summary (FR-7 format deviation), and files-changed counting uses a fragile grep filter. Test suite has one coverage gap (underclassified-via-reports path untested).

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Inline divergence message missing evidence summary**
   - Location: `agent-core/bin/triage-feedback.sh:65`
   - Axis: conformance
   - Problem: FR-7 specifies format: `"Triage: predicted [X], evidence suggests [Y] ([summary])."` Script outputs `"Triage: predicted $classification, evidence suggests $verdict"` without the parenthesized evidence summary.
   - **Status**: FIXED

2. **Underclassified-via-reports path untested**
   - Location: `tests/test_triage_feedback.py` (missing test)
   - Axis: coverage
   - Problem: FR-6 defines underclassified as Simple + (behavioral code **or** reports > 0). `test_underclassified_simple_with_behavioral_code` covers the behavioral_code path. No test covers Simple + reports > 0 + no behavioral code. This is the only untested branch in the underclassified condition.
   - **Status**: FIXED

### Minor Issues

1. **files_changed counting via grep filter is fragile**
   - Location: `agent-core/bin/triage-feedback.sh:15`
   - Axis: robustness
   - Problem: `grep -v "file.*changed"` to exclude the `--stat` summary line would false-exclude a filename containing "file" and "changed". `git diff --name-only | wc -l` is simpler and immune to this.
   - **Status**: FIXED

2. **Empty classification treated as "match"**
   - Location: `agent-core/bin/triage-feedback.sh:35-51`
   - Axis: robustness
   - Problem: If `classification.md` exists but the grep finds no `Classification:` line, `$classification` is empty. The script falls to the `else` branch (line 49) and reports `verdict="match"`. An empty classification is a parse failure, not a match. Should report a distinct status or fall through to no-classification.
   - **Status**: FIXED

3. **Overclassified test does not assert inline message**
   - Location: `tests/test_triage_feedback.py:239`
   - Axis: coverage
   - Problem: `test_overclassified_complex_minimal_changes` asserts "overclassified" in stdout but does not verify the `Triage: predicted Complex` inline message. The underclassified test does assert this (line 208).
   - **Status**: FIXED

4. **test_log_appends_multiple_entries uses same baseline for both runs**
   - Location: `tests/test_triage_feedback.py:325`
   - Axis: specificity
   - Problem: `second_baseline = baseline_sha` reuses the initial commit SHA. Both runs see changes from the same baseline. The test validates append behavior but doesn't exercise distinct baselines. Functionally harmless since the test's goal is append-not-overwrite, but variable naming is misleading.
   - Note: Renamed variable to clarify intent. Not worth creating a distinct baseline for this test since append behavior is the target assertion.
   - **Status**: FIXED

## Fixes Applied

- `agent-core/bin/triage-feedback.sh:15` — replaced `git diff --stat | grep -v "file.*changed" | wc -l` with `git diff --name-only "$baseline_commit" | wc -l`
- `agent-core/bin/triage-feedback.sh:35-51` — added empty-classification guard: if `$classification` is empty after parsing, set `verdict="no-classification"` instead of falling through to match
- `agent-core/bin/triage-feedback.sh:65` — added evidence summary to inline divergence message: `"Triage: predicted $classification, evidence suggests $verdict (files=$files_changed, reports=$reports_count, code=$behavioral_code)"`
- `tests/test_triage_feedback.py` — added `test_underclassified_simple_with_reports` test covering Simple + reports > 0 path
- `tests/test_triage_feedback.py:239` — added inline message assertion to overclassified test
- `tests/test_triage_feedback.py:325` — renamed misleading `second_baseline` to `baseline_sha` (same variable, clearer that it's intentionally reused)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-5 | Satisfied | Three signals: files changed (line 15), report count (line 19-23), behavioral code (line 26-29) |
| FR-6 | Satisfied | Heuristics at lines 37-51: Simple→underclassified, Complex→overclassified, else→match |
| FR-7 | Satisfied (after fix) | Log append at lines 69-81, inline message at line 65 (fixed to include summary) |
| C-3 | Satisfied | Heuristics are hardcoded initial estimates; log provides calibration data |
| NFR-2 | Satisfied | All detection is mechanical (grep, find, wc); no agent judgment in script |

## Positive Observations

- Clean separation between evidence collection, comparison, and logging
- Correct use of `set -euo pipefail` with appropriate `|| true` for grep no-match
- Test suite uses real git repos via tmp_path (not mocked subprocess) — tests actual behavior
- Report file exclusion patterns (design-review*, outline-review*, recall-*) correctly exclude pre-execution artifacts per FR-5
- Good error message on missing args (stderr + exit 1)

## Recommendations

- The behavioral code pattern `^\+[^#]*(def |class |function )` handles Python and JS but would match substring occurrences like `redef ine`. Word boundary `\bdef \b` would be more precise, though C-3 covers heuristic imprecision. Worth revisiting during calibration.
