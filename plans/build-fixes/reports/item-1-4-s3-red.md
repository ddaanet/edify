# Item 1.4 slice 3 (list-revised) — RED report

Test file: `tests/test_changed_files_phase.py` (now ~202 lines). SUT untouched:
`git diff --quiet plugin/skills/build/scripts/changed-files.sh` exits 0.
`ruff check` clean, `ruff format --check` clean, `docformatter -c` exit 0.

## Per-test output

- `test_phase_list_keeps_the_filters`: PASSES against the current SUT, as
  expected (filters and the `:(glob)` fix already shipped, shared code).
  Proven non-vacuous by mutation below; one test carries all three
  behaviours (filters + `:(glob)` pin), fixture folded in.
- Suite after restore: `tests/test_changed_files.py` +
  `tests/test_changed_files_phase.py` 7/7 passed.

## Mutation proof

Each mutation was a single exact-string replacement in
`plugin/skills/build/scripts/changed-files.sh` (asserted to occur once),
restored by the inverse replacement. After each restore: grep for the
mutation text, no hit; final run green (7/7); SUT diff-clean.

1. Disable exempt drop. `if [[ $path =~ $exempt_re ]]; then` -> `if false; then`.
   `test_phase_list_keeps_the_filters` reds on its list assertion
   (`AssertionError: BASE: e36c6d1c…`, list differs: exempt paths listed).
2. Disable `plans/<job>/` drop. `"$exclude_prefix"*) continue ;;` ->
   `NOMATCH_X) continue ;;`. Same test reds on the list assertion
   (`plans/j/...` entries appear: `assert ['BASE: a3360...ctor.md', ...] == [...]`).
3. Remove `:(glob)` magic. `":(glob)plans/$job` -> `"plans/$job`
   (restored by `"plans/$job/reports/phase-*-corrector.md")` ->
   `":(glob)plans/$job/reports/phase-*-corrector.md")`). Same test reds:
   BASE becomes the decoy commit (`67d13eef…` instead of the boundary),
   list is `['BASE: …']` only.

## Deviation from the slice text

The prompt's decoy `plans/j/reports/sub/phase-9-corrector.md` does not match
`phase-*-corrector.md` even without `:(glob)` (the literal `reports/phase-`
prefix excludes it; the slice-2 code review recorded this). It could not red
the mutation. The pin uses `plans/j/reports/phase-9/old-corrector.md`, the
path the review found matching without `:(glob)`. The `sub/` path is kept in
the same decoy commit as a near-miss that must not become the base.

## Fixtures tried and rejected

- `plans/j/reports/sub/phase-9-corrector.md` alone as the `:(glob)` decoy:
  rejected, matches neither with nor without the magic, so mutation 3 would
  not red it (verified from the review's probe, and the combined fixture
  reds only via the `phase-9/old-corrector.md` path).
- Putting the decoy commit before the kept files: rejected, a wrongly moved
  base would then hide nothing and the list would be identical.
