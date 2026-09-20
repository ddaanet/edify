# Item 1.2 / slices 4-8 — RED batch (proof by mutation)

Deviation from ordinary RED: slices 4-8's behaviours were already implemented
by slice 1's and 2's GREEN. Each test is written and run **unmutated first**
(expected PASS, proving the current script already satisfies it), then proved
by one targeted mutation of `plugin/bin/edify-review-range.sh` per slice,
showing the targeted test FAILED on its own assertion, then restored
byte-for-byte before the next mutation. No GREEN or code-review dispatch —
the implementation does not change.

## Unmutated run — all 11 tests PASS

```
tests/test_review_range.py::test_first_pass_emits_range PASS
tests/test_review_range.py::test_second_pass_matching_base_emits_range PASS
tests/test_review_range.py::test_second_pass_recomputed_base_is_conflict PASS
tests/test_review_range.py::test_missing_provenance_reported[no-section] PASS
tests/test_review_range.py::test_missing_provenance_reported[only-derived-from] PASS
tests/test_review_range.py::test_unresolvable_base_reported PASS
tests/test_review_range.py::test_missing_prior_artifact_reported PASS
tests/test_review_range.py::test_prior_without_base_reported[base-absent] PASS
tests/test_review_range.py::test_prior_without_base_reported[base-short] PASS
tests/test_review_range.py::test_wrapped_derived_from_with_spaced_path PASS
tests/test_review_range.py::test_first_pass_none_with_rationale_emits_range PASS
```

Summary: 11/11 passed.

New tests added (3 existing tests from slices 1-3 untouched):

- `test_missing_provenance_reported` (slice 4) — parametrized: no `##
  Provenance` heading at all, and a heading present with only `Derived
  from:` (no `Base:`). Both assert `returncode == 1`, `stdout ==
  "NO-PROVENANCE:\n"`.
- `test_unresolvable_base_reported` (slice 5) — `Base:` = 40 hex chars
  naming no commit. Asserts `returncode == 1`, `stdout ==
  f"UNRESOLVED: {fake}\n"`.
- `test_missing_prior_artifact_reported` (slice 6) — `Derived from:` names
  a path that does not exist. Asserts `returncode == 1`, `stdout ==
  "NO-PRIOR: plans/missing-job/outline.md\n"`.
- `test_prior_without_base_reported` (slice 7) — parametrized: prior
  artifact's `Base:` bullet absent, and `Base:` = `abc123` (short). Both
  assert `returncode == 1`, `stdout ==
  "NO-PRIOR: plans/prior-job/outline.md\n"`.
- `test_wrapped_derived_from_with_spaced_path` (slice 8, case 1) — wrapped
  `Derived from:` naming a prior under `plans/my job/outline.md` (space in
  the path). Asserts `returncode == 0`, `stdout == f"RANGE:
  {sha}..HEAD\n"`. The run helper already invokes from a CWD outside the
  repo with the artifact given as an absolute path — this test asserts
  nothing new for that; it holds because the existing `_run_review_range`
  helper is reused unchanged.
- `test_first_pass_none_with_rationale_emits_range` (slice 8, case 2) —
  `Derived from: none — this job originates from the task frame`. Asserts
  `returncode == 0`, `stdout == f"RANGE: {sha}..HEAD\n"`.

Fixture additions in `tests/test_review_range.py`: `_write_artifact_with_
only_derived` (Provenance heading, `Derived from:` bullet, no `Base:`),
`_write_artifact_no_provenance_section` (no `## Provenance` heading at
all), `_write_prior_without_base` (prior artifact whose `Base:` bullet is
absent or an arbitrary short value).

## Mutation cycle 1 — slice 4 (`test_missing_provenance_reported[no-section]`)

Mutation: replaced the "provenance section absent" branch
(`plugin/bin/edify-review-range.sh:85-87`) to emit `RANGE:` unconditionally
instead of `NO-PROVENANCE:`:

```diff
-if [[ -z "$provenance" ]]; then
-    echo "NO-PROVENANCE:"
-    exit 1
+if [[ -z "$provenance" ]]; then
+    printf 'RANGE: %s..HEAD\n' "0000000000000000000000000000000000000000"
+    exit 0
 fi
```

Run: only `test_missing_provenance_reported[no-section]` FAILED —
`AssertionError: RANGE: 0000...0000..HEAD` vs expected `returncode == 1`.
All other 10 tests still passed. Restored: `git checkout --
plugin/bin/edify-review-range.sh`; `git diff --stat
plugin/bin/edify-review-range.sh` empty.

## Mutation cycle 2 — slice 5 (`test_unresolvable_base_reported`)

Mutation: removed the `git rev-parse --verify --quiet` resolution
(`:112-115`), so an unresolvable base is trusted verbatim:

```diff
-if ! resolved_base=$(git -C "$root" rev-parse --verify --quiet "${base}^{commit}"); then
-    echo "UNRESOLVED: $base"
-    exit 1
-fi
+resolved_base="$base"
```

Run: only `test_unresolvable_base_reported` FAILED —
`AssertionError: RANGE: 0000...0001..HEAD` vs expected `returncode == 1`.
All other 10 tests passed. Restored, `git diff --stat` empty.

## Mutation cycle 3 — slice 6 (`test_missing_prior_artifact_reported`)

Mutation: removed the prior-file-exists guard (`:135-138`):

```diff
-    if [[ ! -f "$prior" ]]; then
-        echo "NO-PRIOR: $prior_path"
-        exit 1
-    fi
-
     prior_provenance=$(provenance_of "$prior")
```

Run: only `test_missing_prior_artifact_reported` FAILED — `awk: cannot
open ".../plans/missing-job/outline.md"`, `returncode == 2` vs expected
`1`. The mutation surfaces as a different failure mode (script error
rather than a false match) but the test's own assertion still catches it;
all other 10 tests passed. Restored, `git diff --stat` empty.

## Mutation cycle 4 — slice 7 (`test_prior_without_base_reported`)

Mutation: removed the prior-base sha-shape check (`:144-147`):

```diff
-    if [[ ! "$prior_base" =~ ^[0-9a-fA-F]{40}$ ]]; then
-        echo "NO-PRIOR: $prior_path"
-        exit 1
-    fi
-
     if [[ "$resolved_base" == "$prior_base" ]]; then
```

Run: both parametrized cases of `test_prior_without_base_reported`
FAILED — `base-absent` and `base-short` each got `CONFLICT: base <sha> !=
<empty|abc123> inherited from ...` instead of `NO-PRIOR:`. All other 9
tests passed. Restored, `git diff --stat` empty.

## Mutation cycle 5 — slice 8 (`test_first_pass_none_with_rationale_emits_range`)

Mutation: changed the `none` match from prefix (first word) to whole-value
equality (`:117`):

```diff
-if [[ "${derived_from%% *}" == "none" ]]; then
+if [[ "$derived_from" == "none" ]]; then
```

Run: only `test_first_pass_none_with_rationale_emits_range` FAILED —
`NO-PROVENANCE:`, `returncode == 1` vs expected `0`. All other 10 tests
passed. Restored, `git diff --stat` empty.

## Lint

```
ruff check tests/test_review_range.py         → All checks passed!
mypy tests/test_review_range.py               → exit 0, no output
docformatter -c tests/test_review_range.py    → exit 0
```

## Final state

`git diff --stat plugin/bin/edify-review-range.sh` — empty (byte-for-byte
restored after all five cycles). Only `tests/test_review_range.py` carries
changes. Nothing committed, per instruction.
