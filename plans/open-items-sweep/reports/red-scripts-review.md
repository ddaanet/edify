# Test review — RED, script minor-defect tests

Reviews the five tests written by `plans/open-items-sweep/reports/red-scripts.md`
against the "Minor Findings" items of
`plans/provenance-enforcement-and-routing/reports/deliverable-review.md:185-275`.
Neither script was modified; nothing was committed.

**Verdict: accepted with fixes.** All five reds are genuine — each fails on a
failed assertion against the unchanged script, for the reason the spec names.
One fixture (Major 1) under-constrained its fix and was rebuilt; four tests were
relocated to the modules their asserted verdict names (Major 2).

## Major

### Major 1 — the CRLF fixture greened under a fix that does not fix CRLF

`test_crlf_base_line_resolves_like_a_clean_line` wrote a CRLF ending on the
`Base:` line only, with every other line LF. The spec's condition is "a CRLF
artifact" (`deliverable-review.md:187`), and the difference is load-bearing:
`:40`'s `sub(/[ \t]+$/, "")` leaves a `\r` on *every* parsed value, so `Base:`
is only the first casualty. `Derived from:` is the second — its value reads
`none\r`, which fails the `none` test at `:119`.

Probed against two patched copies of the script under `$TMPDIR` (the real script
was never touched):

| Fix | single CRLF line | fully-CRLF artifact |
|---|---|---|
| strip `\r` in `base_value_of` (`:64`) | `RANGE:` | `NO-PROVENANCE:` |
| strip `\r` per line in awk (`:40`) | `RANGE:` | `RANGE:` |

So the original fixture accepted the narrow fix, which leaves a real CRLF
artifact broken and merely swaps `UNRESOLVED:` for a different wrong verdict.
This is the wrong-reason test the dispatch budget expects: the assertion was
correct, the fixture was not.

**Fix applied.** The test now writes the artifact through `_write_artifact` and
converts the whole file to CRLF, so only a per-line fix at the site the spec
names satisfies it. The hand-rolled artifact body was dropped, removing a second
copy of the §Provenance shape that would drift from the helper. The docstring
names both casualties and states why the whole file is CRLF.

### Major 2 — four tests sat in modules that name a different verdict

The five `test_review_range_*` modules split strictly by the verdict
**asserted** — each docstring reads "Contract tests for `edify-review-range.sh`'s
`<VERDICT>` verdict", and before this slice every test in each module asserted
that module's verdict. The RED phase placed tests by the verdict the bug
currently *emits* instead, which inverts the convention and would, repeated,
leave every module holding tests for verdicts it does not name.

**Fix applied.** Relocated, with no change to any assertion:

| Test | was | now |
|---|---|---|
| CRLF artifact → `RANGE:` | `unresolved.py` | `range.py` |
| uppercase prior base → `RANGE:` | `conflict.py` | `range.py` |
| backticked `none` → `RANGE:` | `no_provenance.py` | `range.py` |
| phantom prior base → `UNRESOLVED:` | `conflict.py` | `unresolved.py` |

Renamed to the sibling convention in each destination — `*_emits_range` in
`range.py` (matching `test_first_pass_emits_range`), `*_reported` in
`unresolved.py` (matching `test_unresolvable_base_reported`):

- `test_crlf_artifact_emits_range`
- `test_prior_base_uppercase_same_commit_emits_range`
- `test_backticked_none_emits_range`
- `test_unresolvable_prior_base_reported`

Each relocated docstring still names the spurious verdict it displaces, so the
"when must `CONFLICT:` *not* fire" story survives the move.
`test_review_range_conflict.py` and `test_review_range_no_provenance.py` are
back to their committed contents.

## Minor

### Minor 1 — verdict choice for the phantom prior base: confirmed

The dispatch asked this choice be confirmed or overruled. **Confirmed:
`UNRESOLVED: <prior sha>`.** Grounds, checked against KD-2
(`plans/provenance-enforcement-and-routing/outline.md:93-107`) and the script's
own vocabulary:

- KD-2 scopes `NO-PRIOR:` to a prior that is "missing or carries no full-sha
  `Base:`". A phantom 40-hex value *is* a full sha, so the stated scope excludes
  it. The existing `test_prior_without_base_reported` fixtures confirm the
  reading — `None` and `abc123`, both syntactic failures.
- KD-2 makes `CONFLICT:` the hard stop meaning one of two artifacts is wrong,
  adjudicated between two bases. A base that names no commit is not a rival
  base.
- `UNRESOLVED: <base>` is what the script already prints for its *own* base that
  passes the 40-hex regex and fails `git rev-parse` (`:107`, `:115`). Identical
  condition, one hop away.

Exit code and the skill's action are the same under any of the three (exit 1,
ask the user), so the choice is a diagnostics question only.

**Residual, for GREEN, not a test defect:** `UNRESOLVED: <sha>` does not say
*which* artifact's base failed. An operator reads it, checks their own `Base:`,
finds it resolves, and has to compare shas to discover the prior is at fault.
That is the same "verdict does not carry its subject" complaint the deliverable
review raises against the three `NO-PROVENANCE:` causes. Worth a KD-2 note if
the verdict line is ever revisited; it does not change the verdict here.

### Minor 2 — stale line citation

The phantom-prior docstring cited `:151` for the syntactic validation of
`$prior_base`. The validation is at `:146`; `:151` is the compare. **Fixed** —
the docstring now cites `:146` for the regex, `:151` for the compare, and
`:107`/`:115` for the verdict it borrows.

### Minor 3 — the two-roots test contradicted its module's docstring

`test_line_limits_exit_codes.py`'s docstring scopes the module to exit-code
precedence and explicitly reasons that parse-time exit-2 sites are out of scope
because they "cannot co-occur with an already-set `EXIT_CODE=1`". A second
positional `ROOT` is exactly such a parse-time site, and it was absent from that
docstring's enumeration of them.

**Fix applied.** Added the site to the enumeration and a sentence stating that
the test sits here, rather than in `tests/test_line_limits.py`, only because
that module is at its line cap (377 lines; the test would push it over 400).
That is the same cap-driven placement rationale the module already records for
its own split.

### Minor 4 — "two lines above" was four

The two-roots docstring described the `-*)` arm as "two lines above" the `*)`
arm. It is at `:52`, four lines above `:56`. **Fixed** to "just above
(`:52-55`)", which does not rot on a one-line edit.

### Minor 5 — the two-roots test under-asserted

It asserted exit 2 and non-empty stderr, but not that the run stopped before
walking. Both sibling tests in the module assert `"oversized-file:" not in
result.stdout`. **Fix applied** — added that assertion, plus a docstring
paragraph naming what the 401-line file under the first root buys: exit 0 means
the script silently walked the second root, exit 1 means it walked the first,
exit 2 means it rejected the invocation without walking either.

## Checked and clean

- **Fixtures match the spec's conditions exactly.** Uppercase hex of the *same*
  commit (`sha.upper()` against `_init_repo`'s lowercase return, not a second
  commit). A syntactically valid 40-hex sha the repo does not have (`"f" * 40`).
  Backticked `` `none` ``, not quoted or spaced. Two positional roots, verified
  in the failing argv. A full CRLF artifact after Major 1's rebuild.
- **All five pass under a minimal fix.** Patched copies under `$TMPDIR` (a
  per-line `\r` strip at `:40`, a backtick strip on `derived_from`'s first word,
  a `rev-parse --verify --quiet` of `$prior_base` before `:151`, and a `ROOT_SET`
  guard in the `*)` arm) turn all five green. Confirmed `git rev-parse` accepts
  uppercase hex and canonicalises it, which is what makes the uppercase test
  passable by that fix rather than by a bespoke lowercasing.
- **No regression from those fixes.** The same probes left `CONFLICT:`,
  `NO-PRIOR:` (short prior base), `NO-PROVENANCE:` (report-only) and the spaced
  prior path (`plans/my job/`) at their existing verdicts. The spaced-path test
  is the standing guard against a fix that strips backticks from the whole
  `Derived from:` value and breaks the `superseding` regex.
- **Helper change is minimal.** `second_root: Path | None = None` appends one
  positional after `root`; no existing call site passes it. One latent trap,
  left alone as out of scope: combined with `omit_root=True` it would become the
  *first* positional. No caller does that today.
- **No fixture splits on whitespace.** Paths cross the boundary as single argv
  elements and are quoted inside both scripts.
- **Every touched file is under the 400-line cap:** helpers 165, exit-codes 112,
  conflict 41, no-provenance 74, unresolved 66, range 242.
- **Neither script was modified.** `git diff --stat` over
  `plugin/bin/edify-review-range.sh` and `scripts/check_line_limits.sh` is empty.

## Final run

`just red-lint` → `Red Lint OK`.

`just test`:

```
**Summary:** 355/361 passed, 5 failed, 1 xfail
```

The five failures are exactly the five new tests, each on a failed assertion:

- `tests/test_line_limits_exit_codes.py::test_two_positional_roots_exits_2_with_usage_diagnostic`
- `tests/test_review_range_range.py::test_prior_base_uppercase_same_commit_emits_range`
- `tests/test_review_range_range.py::test_backticked_none_emits_range`
- `tests/test_review_range_range.py::test_crlf_artifact_emits_range`
- `tests/test_review_range_unresolved.py::test_unresolvable_prior_base_reported`

## Working tree

Modified, all test-side: `tests/line_limits_helpers.py`,
`tests/test_line_limits_exit_codes.py`, `tests/test_review_range_range.py`,
`tests/test_review_range_unresolved.py`.

Untracked and **not created by this review**, reported rather than filtered:
`.claude/launch.json`, `.claude/loop.md`, `.claude/output-styles/`,
`.claude/routines/`, `.claude/workflows/`, `plans/open-items-sweep/`. The
`.claude/` entries were absent from the session's opening `git status` snapshot
and appeared during the session.
