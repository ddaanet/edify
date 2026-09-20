# Item 1.2 slice 2 — test review (RED phase)

Verdict: **RED confirmed.**

Slice: `test_second_pass_matching_base_emits_range` — prior artifact carries
the same `Base:`; asserts exit 0 and the `RANGE:` line.

## Pytest before fixes

```
# Test Report

**Summary:** 1/2 passed, 1 failed

## Failures

### tests/test_review_range.py::test_second_pass_matching_base_emits_range FAILED

```python
tests/test_review_range.py:141: in test_second_pass_matching_base_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: NO-PRIOR: plans/prior-job/outline.md
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '.../repo/plans/job/outline.md'], returncode=1, stdout='NO-PRIOR: plans/prior-job/outline.md\n', stderr='').returncode
```

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
```

Slice 1's test PASSED. Slice 2's FAILED on the `returncode` assertion — a
FAILED, not an ERROR: the script resolved by bare name, parsed §Provenance,
reached the `superseding` arm and emitted its skeleton verdict
`NO-PRIOR: plans/prior-job/outline.md` with exit 1. Reproduced verbatim from
the RED report (`item-1-2-s2-red.md`), same output, different tmpdir.

## Findings

### 1. Major — the fixture's wrapped shape was not the shape real artifacts write

`_second_pass_derived_from` put the motivating report **on the bullet line**
and only `superseding \`<path>\`` on a continuation:

```
- **Derived from:** `plans/prior-job/reports/deliverable-review.md`,
  superseding `plans/prior-job/outline.md`
```

The real second-pass shape — `plans/provenance-enforcement-and-routing/outline.md`'s
own `## Provenance`, which is the artifact KD-2's script was specified
against — puts **nothing** after the label and carries the whole value on two
indented continuation lines:

```
- **Derived from:**
  `plans/provenance-reach-and-sweep/reports/deliverable-review.md`,
  superseding `plans/provenance-reach-and-sweep/outline.md`
```

The two differ in the awk join path they exercise: the label-only bullet line
is the case where the joiner must carry an *empty* value across the first
continuation. The fixture did not cover it, so the contract test would have
declared the script good against a shape no real artifact uses.

**Change (applied):** `_second_pass_derived_from` now returns a value opening
with a newline, and `_write_artifact` strips trailing whitespace line by line
so the bullet line reads exactly `- **Derived from:**` with no trailing
blank — byte-identical to how a real artifact is written, not merely
tolerated by awk's own trailing-space strip. Fixture output now:

```
'# Outline'
''
'## Provenance'
''
'- **Derived from:**'
'  `plans/prior-job/reports/deliverable-review.md`,'
'  superseding `plans/prior-job/outline.md`'
'- **Base:** `<sha>`'
''
'## Requirements'
```

Report path, comma, `` superseding `plans/prior-job/outline.md` `` with
backticks — as the brief specified.

### 2. Checked by measurement — the test does require the prior artifact

Reasoning about this would be a guess, so I measured it. I copied the SUT to
`$TMPDIR/probe/edify-review-range.sh` and patched the copy's
`TODO(slices 2-8)` arm into a working inheritance check (resolve the prior
against `$root`, read its `**Base:**`, compare), then drove the **fixture
itself** — the real `_write_artifact` / `_second_pass_derived_from` /
`_run_review_range` helpers, imported from the test module with `BIN_DIR`
repointed — against it. `plugin/bin/edify-review-range.sh` was never touched;
`git diff --stat` on it is empty and it does not appear in `git status`.

Against the **fixed** fixture:

| Fixture variation | Patched script | Slice 2's assertion |
|---|---|---|
| prior present, matching `Base:` | `RANGE: <sha>..HEAD`, exit 0 | **passes** |
| prior file absent at the named path | `NO-PRIOR: plans/prior-job/outline.md`, exit 1 | fails |
| prior present, different `Base:` | `CONFLICT: base <sha> != 000…0 inherited from plans/prior-job/outline.md`, exit 1 | fails |

Row 1 proves the test is satisfiable — the red is a missing implementation,
not an unreachable assertion. Row 2 proves the fixture **requires** the prior
artifact to exist at the path named after `superseding`: delete it and the
test fails. Row 3 is slice 3's case, confirming the fixture reaches it.

### 3. Accepted as specified — a script ignoring the prior still passes

A script that emitted its own `Base:` whenever `Derived from:` is not `none`,
never reading the prior at all, would pass this test. That is inherent to the
matching-base case: a matching base is indistinguishable from an unread
prior. Per the brief this is **slice 3's** job (conflict) and no conflict
assertion was added here. Likewise a script emitting the *prior's* base
rather than its own is indistinguishable in this slice.

The one wrong-reason script this slice's scope can exclude — `git rev-parse
HEAD` instead of reading `Base:` — is already excluded by slice 1's
two-commit `_init_repo`, whose returned sha is the first commit and therefore
not `HEAD`. Verified still in place.

### 4. No drift into slice 1

`_write_artifact`'s emitted body is unchanged for `derived_from="none"`: the
new per-line `rstrip` is a no-op on a single-line value. Dumped and compared —
`'# Outline\n\n## Provenance\n\n- **Derived from:** none\n- **Base:** `<sha>`\n\n## Requirements\n'`,
exactly what slice 1 asserted against. `test_first_pass_emits_range` still
passes, unmodified.

### 5. Also correct, checked

- The prior is a well-formed **first-pass** artifact: `Derived from: none`,
  `Base:` the same sha, full 40 hex, backtick-quoted, under `## Provenance`
  with `## Requirements` terminating the section.
- The assertion is exact equality on the whole stream —
  `result.stdout == f"RANGE: {sha}..HEAD\n"`, trailing newline included — not
  a substring or an `in`. Exit code asserted separately with both streams
  attached to the failure message (D-21).
- `sha` is the fixture's own `rev-parse` output, never hardcoded.
- Invocation unchanged from slice 1: bare name, `plugin/bin` on `PATH`, CWD
  in `tmp_path/elsewhere` outside the repo, artifact passed absolute.
- Conforms to D-18 (asserts output content, not structure) and D-19 (real git
  repo under `tmp_path`, no subprocess mocks).

## Flags for slices 3–8 — fixture shape

Not fixed here; nothing in the current shape is wrong, but two of the six
need a writer the fixture does not yet have.

| Slice | Needs | Current fixture |
|---|---|---|
| 3 | prior with a different `Base:` | works — `_write_artifact(prior, "none", other_sha)`; measured above |
| 4 | no `## Provenance` section at all | **needs a new writer** — `_write_artifact` always emits the section |
| 5 | non-resolving sha | works — pass `"0"*40` as `base` |
| 6 | `Derived from:` naming a missing path | works — build the value, do not write the prior; measured above |
| 7 | prior with no `Base:` | **needs a writer variant** — `_write_artifact` always emits the bullet |
| 8 | spaced path `plans/my job/`, `none — rationale` | works — the backticks in `_second_pass_derived_from` keep a spaced path whole, and the script takes the first word of `Derived from:`, so a trailing rationale is inert |

Recommendation for 4 and 7: give `_write_artifact` `derived_from: str | None`
and `base: str | None`, `None` meaning "omit this bullet", plus a separate
writer (or a `section: bool` flag) for the no-section case. Not designed now.

## Lint

```
$ ruff check tests/test_review_range.py
All checks passed!          (exit 0)
$ mypy tests/test_review_range.py
Success: no issues found in 1 source file   (exit 0)
$ docformatter -c tests/test_review_range.py
(exit 0)
```

## Pytest after fixes

```
# Test Report

**Summary:** 1/2 passed, 1 failed

## Failures

### tests/test_review_range.py::test_second_pass_matching_base_emits_range FAILED

```python
tests/test_review_range.py:147: in test_second_pass_matching_base_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: NO-PRIOR: plans/prior-job/outline.md
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '.../repo/plans/job/outline.md'], returncode=1, stdout='NO-PRIOR: plans/prior-job/outline.md\n', stderr='').returncode
```

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
```

Still red, still a FAILED on the assertion, still `NO-PRIOR:` with exit 1, no
ERROR. Slice 1 still green.

## Scope

Touched `tests/test_review_range.py` only. The probe in finding 2 ran against
a copy under `$TMPDIR`; `plugin/bin/edify-review-range.sh` is unmodified.
Nothing committed. `git status --porcelain`:

```
 M tests/test_review_range.py
?? plans/provenance-enforcement-and-routing/reports/item-1-2-s2-red.md
```
