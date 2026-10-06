# Item 3.4 — build-fixes outline revised after the fact: exit codes and test modules

Target: `plans/build-fixes/outline.md`. Requirements: m3, m20.

Each revised spot carries "(revised after the fact by `plans/review-fixes-2/`
Item 3.4)", so a reader of the frozen plan sees which text postdates its
execution. The plan had no prior revision convention to follow.

## Edits — §Items

### Item 1.1 header (m20)

Was: "`tests/test_verify_step.py` — pin the exemption's porcelain states …".

Now: "`tests/test_verify_step_exemption.py` — pin the exemption's porcelain
states …", plus: the tests landed in that module, split from
`tests/test_verify_step.py` to keep each under its line cap. Checked:
`test_exempt_paths_clean_in_any_porcelain_state` and
`test_nested_path_under_exempt_dir_is_dirty` are in
`tests/test_verify_step_exemption.py` (lines 167, 214).

### Item 1.2 Interfaces (m3)

Was: "Exit 1: `NO-BASE:`. Exit 2: `ERROR:` on usage or git failure."

Now: "Exit 1: `NO-BASE:`, for a repo with commits and no committed item report.
Exit 2: `ERROR:` on usage or git failure, an unborn `HEAD` included." Checked
against `changed-files.sh` (the `git log` failure branch exits 2 with
`ERROR: git log failed`) and
`tests/test_changed_files.py::test_git_failure_is_error_not_no_base`.

### Item 1.4 test placement (m20)

Was: "The tests go in `tests/test_changed_files.py`, and slice 4's in the
`verify-step.sh` tests."

Now: slices 1–3's tests landed in `tests/test_changed_files_phase.py`, split
from `tests/test_changed_files.py` to keep each under its line cap, and slice
4's in `tests/test_verify_step.py`. Checked: the four `test_phase_*` tests are in
`tests/test_changed_files_phase.py`, and `test_quotepath_false_does_not_hide_dirt`
is in `tests/test_verify_step.py` (line 73).

## Verification

- `just format`; the outline is 449 lines (442 before). It was already over
  the soft 400-line plan cap before this item; the three revision notes add
  7 lines. Not split: it is a frozen plan revised in place, per the item.
- `just precommit`: Precommit OK — version consistency, tests cached (inputs
  unchanged), line limits, design links (94 decisions indexed, defined once,
  conclusions match, 9 nodes present). The three `oversized-file` lines are
  agent files this item does not touch; the plan cap is not gated.
