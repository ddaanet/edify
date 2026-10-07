# Outline Review: review-fixes-2 Item 3.4 (build-fixes outline, revised after the fact)

**Artifact**: plans/build-fixes/outline.md, only the spots that
`git diff 888eda7a312e962a28ba59c2695eecd5f34c6e14 HEAD` revised
**Date**: 2026-10-06
**Mode**: review + fix-all, limited to the revised spots

## Summary

Item 3.4 changed three spots: the Item 1.1 header, the Item 1.2 Interfaces exit
codes, and the Item 1.4 test placement. All three match what landed. The
modules and test names are correct, and the unborn-`HEAD` exit is right. Two
minor gaps came from the revision itself, and both are fixed. In Item 1.1,
moving the module left the frozen sentences after it pointing at fixtures and a
`SCRIPT` that module does not define. In Item 1.2, the rewritten exit-2 sentence
leaves out the `exempt-paths.sh` load failure, which landed in build-fixes Item
1.2/2.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|---|---|---|---|
| m3 | Item 1.2 Interfaces | Complete | Exit 1 is limited to a repo with commits. Exit 2 covers an unborn `HEAD`, as `changed-files.sh` lines 86–89 do (`ERROR: git log failed`) and as `test_git_failure_is_error_not_no_base` pins. The load-failure clause was added in review (Minor 2). |
| m20 | Item 1.1 header, Item 1.4 body | Complete | `test_exempt_paths_clean_in_any_porcelain_state` (l.167) and `test_nested_path_under_exempt_dir_is_dirty` (l.214) are in `tests/test_verify_step_exemption.py`. Slices 1–3 are `test_phase_without_boundary_gives_run_base`, `test_phase_base_is_latest_boundary_commit` and `test_phase_list_keeps_the_filters`, all in `tests/test_changed_files_phase.py`. Slice 4, `test_quotepath_false_does_not_hide_dirt`, is in `tests/test_verify_step.py` (l.73). |

**Traceability Assessment**: All requirements covered.

## Scope-to-Component Traceability

| Scope IN Item | Component | Notes |
|---|---|---|
| Item 1.2 Interfaces exit codes (m3) | build-fixes Item 1.2 | Direct match |
| Item 1.1 test module (m20) | build-fixes Item 1.1 | Direct match |
| Item 1.4 test module (m20) | build-fixes Item 1.4 | Direct match |

**Scope Assessment**: All items assigned. The rest of the outline is frozen and
was not reviewed. That includes its Provenance section, which Item 3.4 did not
touch.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Item 1.1's moved module leaves the frozen fixture sentences pointing at
   nothing**
   - Location: Item 1.1 header, lines 198–203
   - Problem: The revision makes `tests/test_verify_step_exemption.py` "the
     module". The unrevised sentences after it still say "the test module's
     `SCRIPT` rebound" and "the module's existing `_init_repo` and
     `_stub_just`". That module imports `_init_repo` and `_stub_just` from
     `tests/verify_step_helpers.py` and does not import `SCRIPT` at all.
     `SCRIPT` (l.13), `_init_repo` (l.45) and `_stub_just` (l.61) all live in
     the helpers module. Read after the revision, the frozen text names
     locations that do not exist.
   - Fix: added one clause inside the revision note: "the `SCRIPT` and
     fixtures named below now sit in `tests/verify_step_helpers.py`". The
     frozen sentences are unchanged.
   - **Status**: FIXED

2. **Item 1.2's exit-2 sentence leaves out the `exempt-paths.sh` load
   failure**
   - Location: Item 1.2 Interfaces, lines 242–248
   - Problem: The revised sentence reads "Exit 2: `ERROR:` on usage or git
     failure, an unborn `HEAD` included". `changed-files.sh` lines 69–72 also
     exit 2, printing `ERROR: cannot load EXEMPT_PATHS_ALTERNATION from
     exempt-paths.sh`. That is not a usage or git failure. The guard landed in
     build-fixes itself (`4229525e`, "Item 1.2/2 — code-review fixes"), so it
     belongs to this item's interface. It now has a test
     (`test_unloadable_exempt_paths_is_an_error_not_no_base`). The brief asks
     for the revised text to be checked against the script's exits.
   - Fix: the sentence now ends "…an unborn `HEAD` included, or on an
     `exempt-paths.sh` that does not load". m3's ruled wording is kept
     word for word, and this clause only adds to it.
   - **Status**: FIXED

## Fixes Applied

- Item 1.1 header: the revision note now says `SCRIPT` and the fixtures live in
  `tests/verify_step_helpers.py`.
- Item 1.2 Interfaces: the exit-2 clause now includes the `exempt-paths.sh`
  load failure.
- The outline grew from 449 to 451 lines. It was already over the soft
  400-line plan cap and was not split, as instructed. `just precommit`, run in
  the foreground, exited 0 and printed "Precommit OK". Checks: version
  consistency, tests cached (inputs unchanged), line limits, and design links
  (94 decisions indexed, defined once, conclusions match, 9 nodes present).
  The three `oversized-file` lines are agent files this review did not touch.

## Positive Observations

- Each revised spot carries "(revised after the fact by `plans/review-fixes-2/`
  Item 3.4)", so a reader of the frozen plan can see which text came after its
  execution.
- The m3 wording rests on a test that pins both exit-2 branches
  (`test_git_failure_is_error_not_no_base`). It is not just read off the
  script.
- Item 1.4 places slice 4 in `tests/test_verify_step.py`. That is correct and
  more precise than the original "the `verify-step.sh` tests".

## Recommendations

- Two exit-2 branches are still not named: `cd` to the repository root failing
  (l.81–84) and the `BASE:` write failing (l.114). Both are environmental
  defences and not contract states. I left them out deliberately, because
  listing them would turn an interface into a list of every branch. That is my
  judgement and not a rule. If round 3 treats the exit-2 sentence as a
  complete list, the wording to use is "on any other failure".
- `tests/test_changed_files_phase.py` also holds
  `test_phase_flag_only_as_exact_second_argument`, which is not one of Item
  1.4's slices. "Slices 1–3's tests landed in" makes no claim that this
  module holds only those, so nothing needed to change.

---

**Ready for user presentation**: Yes
