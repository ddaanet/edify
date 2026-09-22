# RED — script minor-defect tests

Five failing tests pinned against unchanged `plugin/bin/edify-review-range.sh`
and `scripts/check_line_limits.sh`, per the "Minor Findings" section of
`plans/provenance-enforcement-and-routing/reports/deliverable-review.md`
(lines 185-275). Neither script was touched.

## 1. CRLF `Base:` line resolves like a clean line

- **File:** `tests/test_review_range_unresolved.py`
- **Test:** `test_crlf_base_line_resolves_like_a_clean_line`
- **Behaviour pinned:** a `Base:` bullet whose line ends `\r\n` (the sha
  itself is resolvable) must emit `RANGE: <sha>..HEAD` and exit 0, the same
  as a clean LF line — not `UNRESOLVED:`.
- **Placement rationale:** the bug's current output is a spurious
  `UNRESOLVED:`, so the test lives beside the other `UNRESOLVED:` tests.
- **Failing output (`just test tests/test_review_range_unresolved.py::test_crlf_base_line_resolves_like_a_clean_line`):**

```
tests/test_review_range_unresolved.py:58: in test_crlf_base_line_resolves_like_a_clean_line
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: UNRESOLVED: d53eeb976bbb4dd41480cb070eb407b11adb64c1
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '.../repo/plans/job/outline.md'], returncode=1, stdout='UNRESOLVED: d53eeb976bbb4dd41480cb070eb407b11adb64c1\n', stderr='').returncode
```

(The printed `UNRESOLVED:` line carries a trailing `\r` after the sha —
invisible in this rendering but present in `result.stdout`, which is exactly
the defect: `:40` strips `[ \t]+$` but not `\r`.)

## 2. Prior `Base:` written uppercase, same commit, is not `CONFLICT:`

- **File:** `tests/test_review_range_conflict.py`
- **Test:** `test_prior_base_uppercase_same_commit_is_not_conflict`
- **Behaviour pinned:** a prior artifact's `Base:` written in uppercase hex,
  naming the same commit as the current artifact's resolved base, must emit
  `RANGE: <sha>..HEAD` and exit 0 — not `CONFLICT:`.
- **Failing output:**

```
tests/test_review_range_conflict.py:71: in test_prior_base_uppercase_same_commit_is_not_conflict
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: CONFLICT: base 95c4dfbd671c42a32f1a0ca688bb50aab68082d7 != 95C4DFBD671C42A32F1A0CA688BB50AAB68082D7 inherited from plans/prior-job/outline.md
E
E   assert 1 == 0
```

## 3. Prior `Base:` naming no commit is `UNRESOLVED:`, not `CONFLICT:`

- **File:** `tests/test_review_range_conflict.py`
- **Test:** `test_prior_base_names_no_commit_is_unresolved_not_conflict`
- **Behaviour pinned:** a prior artifact's `Base:` is 40 hex chars that name
  no commit in the repo. Chosen verdict: `UNRESOLVED: <prior's sha>`, exit 1
  — not `CONFLICT:` presenting the phantom sha as an inherited base.
  **Verdict choice and why:** the script already uses `UNRESOLVED: <base>`
  (`:107`) for the case where *its own* `Base:` is syntactically valid but
  the repo cannot resolve it — a sha that looks like a commit reference but
  isn't. A prior's unresolvable `Base:` is the identical failure mode, just
  hit one hop away, so `UNRESOLVED:` carrying the prior's sha is the verdict
  already defined for exactly this condition. `CONFLICT:` is reserved (KD-2)
  for adjudicating between two *real, resolvable* bases that disagree;
  `NO-PRIOR:` is reserved for a missing prior file or a prior `Base:` that
  fails the *syntactic* 40-hex check — neither fits a syntactically valid
  sha that the repo simply doesn't have. This was given as an explicit
  instruction in the dispatch ("Assert the verdict the script should produce
  instead: `UNRESOLVED:`"); the reasoning above is why it also matches the
  script's own vocabulary.
- **Failing output:**

```
tests/test_review_range_conflict.py:109: in test_prior_base_names_no_commit_is_unresolved_not_conflict
    assert result.stdout == f"UNRESOLVED: {phantom}\n"
E   AssertionError: assert 'CONFLICT: ba.../outline.md\n' == 'UNRESOLVED: ...fffffffffff\n'
E
E     - UNRESOLVED: ffffffffffffffffffffffffffffffffffffffff
E     + CONFLICT: base 95c4dfbd671c42a32f1a0ca688bb50aab68082d7 != ffffffffffffffffffffffffffffffffffffffff inherited from plans/prior-job/outline.md
```

## 4. Backticked `` `none` `` in `Derived from:` treated as `none`

- **File:** `tests/test_review_range_no_provenance.py`
- **Test:** `test_derived_from_backticked_none_is_treated_as_none`
- **Behaviour pinned:** `` - **Derived from:** `none` `` (backticked) must
  emit `RANGE: <sha>..HEAD` and exit 0, the same verdict the unbackticked
  `none` form gets — not `NO-PROVENANCE:`.
- **Placement rationale:** the bug's current output is a spurious
  `NO-PROVENANCE:`, so the test lives beside the other `NO-PROVENANCE:`
  tests.
- **Failing output:**

```
tests/test_review_range_no_provenance.py:68: in test_derived_from_backticked_none_is_treated_as_none
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: NO-PROVENANCE:
E
E   assert 1 == 0
```

## 5. Two positional `ROOT` arguments is a usage error

- **File:** `tests/test_line_limits_exit_codes.py`
- **Test:** `test_two_positional_roots_exits_2_with_usage_diagnostic`
- **Behaviour pinned:** `check_line_limits.sh --allowlist <empty> A B` (two
  positional `ROOT` arguments) must exit 2 with a usage diagnostic on
  stderr — not silently walk only `B` and exit 0.
- **Helper change:** `tests/line_limits_helpers.py`'s `_run_check_line_limits`
  gained an optional `second_root: Path | None = None` parameter, appended
  as an extra positional after `root` when given. No existing call site
  passes it, so every other test is unaffected — verified by running the
  full `test_line_limits*` suite below.
- **Failing output:**

```
tests/test_line_limits_exit_codes.py:76: in test_two_positional_roots_exits_2_with_usage_diagnostic
    assert result.returncode == 2, result.stdout + result.stderr
E   AssertionError:
E   assert 0 == 2
E    +  where 0 = CompletedProcess(args=['.../scripts/check_line_limits.sh', '--allowlist', '.../a', '.../b'], returncode=0, stdout='', stderr='').returncode
```

## Full-suite confirmation

Ran all nine `test_review_range_*` and `test_line_limits*` modules together:
the five new tests fail (exactly the five above, no others), every
pre-existing test in those modules still passes. No collateral breakage.

## Files touched

- `tests/test_review_range_unresolved.py` — added test 1
- `tests/test_review_range_conflict.py` — added tests 2 and 3
- `tests/test_review_range_no_provenance.py` — added test 4
- `tests/test_line_limits_exit_codes.py` — added test 5
- `tests/line_limits_helpers.py` — added `second_root` parameter to
  `_run_check_line_limits` (no other change)

Line counts after edits, all under the 400 cap: `test_review_range_conflict.py`
109, `test_review_range_no_provenance.py` 101, `test_review_range_unresolved.py`
59, `test_line_limits_exit_codes.py` 101, `line_limits_helpers.py` 165.

Neither `plugin/bin/edify-review-range.sh` nor `scripts/check_line_limits.sh`
was modified. No commit was made.
