# Review: review-fixes-3 review gate — `review-design`

**Scope**: the design-graph files changed since
`daad4769e5eb694f151b9972ed51555033d0e1ca`: `docs/references/build-run-state.md`
(D-88, D-89, D-90, D-93, Rejected), `docs/decisions.md` (the build-run-state
section) and `docs/references/pipeline-contracts.md` (D-86's query block, from
Item 2.4's list revision).
**Date**: 2026-10-08
**Mode**: review + fix
**Criteria source**: `craft:design-doc-writing` (loaded, craft 0.2.1); no
fallback needed.

## Summary

Item 4.1's amendments are all present and agree with the scripts and prose
they record: `changed-files.sh`, `triage-feedback.sh`, `finishing.md` and
`dispatch-composition.md`. Read against each other, they show no seam. Hub and
node agree, which the `design links` check confirms mechanically. The D-86
query block matches `tdd-slice.md` and `tdd-auditor.md` exactly. Two minor
issues were found and fixed. D-88's reason sentence claimed more than KD-7
scopes. D-90's test citation named no module.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **D-88's reason sentence was wider than KD-7 and the test it cites**
   - Location: `docs/references/build-run-state.md:36-41`
   - Note: the sentence read "Every `git log` whose output `/build` reads
     passes `--no-show-signature`". Two forms fall outside that claim.
     `tdd-auditor.md:60-61` permits `git log -- plans/<job>/<hosting file>`,
     whose output the auditor reads, and it carries no flag. KD-7 rules that
     form out explicitly, because it is a permitted tool, not a command whose
     output is parsed. KD-7's own scope is commands whose output is a hash
     list. The cited test extracts only `git log` commands carrying a
     hash-format flag (`_extract`, `tests/test_build_prose_git_log.py`). So
     "each such command" overclaimed what the test covers.
   - Fix: "whose output `/build` reads as hashes". The sentence still covers
     every `git log` `/build` parses, and it now matches KD-7 and the test. The
     literal format flag is not written into the prose: `_flag_count` counts
     every occurrence of it in the file, so it would add a `:missed` case.
   - **Status**: FIXED

2. **D-90's test citation named no module**
   - Location: `docs/references/build-run-state.md:89`
   - Note: D-88 cites its test as `tests/test_build_prose_git_log.py` plus the
     test name. D-90 cited only `test_late_diff_failure_prints_error_alone`,
     which lives in `tests/test_changed_files_errors.py:174`, a module that
     Item 1.1 created. Without the module, a reader has to search the suite
     to find the test.
   - Fix: the module path was added beside the test name, in the same form as
     D-88. The paragraph was reflowed to rumdl's 80-column output.
   - **Status**: FIXED

## Fixes Applied

- `docs/references/build-run-state.md:37`: "whose output `/build` reads" became
  "whose output `/build` reads as hashes".
- `docs/references/build-run-state.md:89-100`: `tests/test_changed_files_errors.py`
  was added to the D-90 citation, and the following lines were reflowed as
  rumdl MD013 required. No wording outside the citation changed.

The node is now 273 lines, against a 400 cap. No prose was shaved.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| D-88 (m14): flag in query block, one reason sentence covering `/build`'s hash-reading `git log`s, cites signed-history test | Satisfied | `build-run-state.md:28` carries the flag. Lines 36-41 give the reason (`log.showSignature` prints verification lines ahead of the shas) and cite `tests/test_build_prose_git_log.py::test_read_git_log_commands_print_hashes_only_on_signed_history`. |
| D-88 claim true of the design graph's own query blocks | Satisfied | Every `git log` in `docs/` outside `docs/changelog/` was grepped. The design graph has three query blocks: `build-run-state.md:28`, `build-run-state.md:51` and `pipeline-contracts.md:259`. All three carry `--no-show-signature`. `design.md:248` and `decisions.md:84` mention `git log --diff-filter=A` descriptively and are not commands. The seven files holding hash-reading `git log` commands match the test's `SCANNED` tuple exactly, and the test passes 10/10. |
| D-89 (m16, KD-2): conclusion and body widened to the finishing stages, each keyed on its report path | Satisfied | The conclusion at `build-run-state.md:47-48` is KD-2's wording. Lines 71-76 add the finishing stages. The review gate lands on `review-*.md`, `review-skip.md` included, after the run's last item-report commit; this matches `finishing.md:17-18` and 22. The final review lands on `final-review.md` (`finishing.md:151`) and the TDD audit on `tdd-audit.md` (`finishing.md:159-160`). Both use the same `<L>..HEAD` range. |
| D-90 (m2, KD-4): `ERROR:` alone, no `BASE:`, no path | Satisfied | `build-run-state.md:86-90` says this. `changed-files.sh:120-143` captures the list whole before printing `BASE:`, and every earlier failure exits before any print. `test_changed_files_errors.py:174` pins it. |
| D-90 (m16): KD-2's row sentence | Satisfied | `build-run-state.md:113-115`. `triage-feedback.sh:283-313` skips the append when a row matches past the date column. Triage commits no report; the closing commit carries the log (`finishing.md:167-172`). |
| D-90 (m3): the re-run bound, with no final-review fixes clause | Satisfied | `build-run-state.md:119-123`. `deliverable-review.md` and `deliverable-review-<type>.md` (`deliverable-review/SKILL.md:100,145`) do not match the exclusions at `triage-feedback.sh:87,98`, so they count. A Simple job with reports > 0 is `underclassified` (`triage-feedback.sh:202-204`). No final-review fixes clause was added. |
| D-93 (m12, KD-1): name and why it matches `review-*.md` | Satisfied | `build-run-state.md:185-190`. The name and the meanings of `<source job>` and `<stem>` match `dispatch-composition.md` §Naming and resumption and `finishing.md:73-86`. The three readers are `finishing.md:18` (the landed check), `triage-feedback.sh:98` (the report exclusion) and `triage-feedback.sh:227` (the `Review artifact` probe). It is stated as "a name and not a group", which is consistent with D-93's four-row conclusion. |
| Rejected (m17) | Satisfied | `build-run-state.md:243-245` relabels the entry and states the reason: the list already drops it, and a second filter would be a copy. |
| `decisions.md` | Satisfied | The D-89 line follows KD-2. The *Rejected:* line takes m17's label. The D-88, D-90 and D-93 lines are unchanged. `design links` reports "94 decisions indexed, defined once, conclusions match, 9 nodes present". |
| No changelog entry | Satisfied | `git diff --stat daad4769.. HEAD -- docs/` shows only the three files. |
| Item 2.4 list revision: D-86's query block | Satisfied | `pipeline-contracts.md:259-260` is identical to `tdd-slice.md:57-58` and `tdd-auditor.md:87-88`. The flag is in the same position, and the block is consistent with D-88's reason sentence. `pipeline-contracts.md` is in the test's `SCANNED` set, and its case passes. |
| Node length under 400, no shaving | Satisfied | 273 lines. |

**Gaps:** none.

## Validation

- `PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit` exited 0 (`✓ Precommit OK`). It ran these checks:
  - version consistency;
  - tests: 431/432 passed, 1 xfail;
  - rumdl;
  - line limits: the three `oversized-file` lines are the corrector agents, at their allowlisted ceilings (`check_line_limits.allow:15-17`), which is Scope OUT;
  - design links.
- `.venv/bin/pytest -p no:markdown_report tests/test_build_prose_git_log.py`: 10 passed.
- The first precommit run failed on rumdl, because the citation edit left the
  paragraph unreflowed. That paragraph was reflowed and the gate re-run green.
- The sibling dirt was expected and left untouched: `plugin/bin/triage-feedback.sh`, `tests/test_changed_files.py`, `tests/triage_feedback_helpers.py`, the other `review-*.md` reports and `inbox/brief-*.md`. Nothing was staged or committed.

## Positive Observations

- D-90 now states the row rule before the re-run argument. That makes the
  re-run sentence a counterfactual ("would differ … would not fire"), which
  reads correctly next to the bound that follows it.
- D-89 keeps one mechanism for the boundaries and the finishing stages,
  instead of adding a new D-95, as KD-2 argued.
- D-93 gives the three readers that depend on the `review-*.md` match, which
  makes the seam auditable from the design record.
