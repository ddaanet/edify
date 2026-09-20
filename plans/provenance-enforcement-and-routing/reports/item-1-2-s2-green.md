# Item 1.2 slice 2 — GREEN

Slice: `test_second_pass_matching_base_emits_range` — prior artifact carries
the same `Base:`; asserts exit 0 and the `RANGE:` line.

## Approach

Factored the artifact-provenance parsing out of the top-level script body
into two functions so the prior artifact is read with the exact same rules
as the artifact under review, no copy-paste:

- `provenance_of <path>` — the awk join, unchanged, now callable on any
  path.
- `base_value_of <base-bullet-line>` — the `sed`/`%%`/`//` value-extraction
  that used to run inline against `$base_line`; takes the joined bullet line
  (or empty string) and prints the sha-or-garbage first word, or nothing.

The `TODO(slices 2-8)` arm is replaced with the inheritance path: extract the
prior path from `${BASH_REMATCH[1]}` (unchanged from slice 1 — set by
whichever of the two `superseding` regexes matched), resolve it as
`"$root/$prior_path"` (quoted throughout — slice 8 will exercise a spaced
path), and:

- prior file missing → `NO-PRIOR: $prior_path`, exit 1 (unchanged verdict
  text from slice 1's skeleton, now reached only when the file truly isn't
  there).
- prior has no `## Provenance`, no `**Base:**` bullet, or a `Base:` that
  isn't a full 40-hex sha → `NO-PRIOR: $prior_path`, exit 1 (slice 7's case;
  falls out of `base_value_of` returning empty/non-matching and the same
  regex check the artifact's own base already uses).
- prior's base equals the artifact's own `resolved_base` → `RANGE:
  <resolved_base>..HEAD`, exit 0 — this slice's case.
- otherwise → `CONFLICT: base <resolved_base> != <prior_base> inherited
  from <prior_path>`, exit 1 — falls out of the comparison naturally
  (slice 3 pins it).

The prior's base is compared as the literal string from its own artifact
text, not re-resolved through `git rev-parse --verify` — KD-2 only requires
resolving *this* artifact's `Base:` to a commit; the prior's `Base:` is
compared directly, matching the verdict table's `CONFLICT: base <a> != <b>`
wording (both sides are as-written shas, not derived objects). A prior base
that is present but not a well-formed sha is treated as absent (`NO-PRIOR`),
per the outline's "missing or without a full-sha `Base:`" wording.

## Whitespace safety

`prior_path` and `prior` are quoted at every use (`"$prior"` in `[[ -f
"$prior" ]]`, `provenance_of "$prior"`, the `printf` argument list) — no step
word-splits the prior path, so slice 8's `plans/my job/` case is not
special-cased, just not broken.

## Pytest — slice tests

```
# Test Report

**Summary:** 2/2 passed

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
- tests/test_review_range.py::test_second_pass_matching_base_emits_range
```

## Pytest — full suite

```
**Summary:** 292/308 passed, 16 skipped
```

No failures; the 16 skips are pre-existing (unrelated to this change).

## shellcheck

```
$ shellcheck plugin/bin/edify-review-range.sh
(exit 0, no output)
```

## just precommit

```
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 307/308 passed, 1 xfail
✓ Precommit OK
```

## Scope

Touched `plugin/bin/edify-review-range.sh` only; `tests/test_review_range.py`
untouched by this slice (its fixture fix landed in the test-review pass
that preceded this GREEN, per `item-1-2-s2-test-review.md`).

Commit subject: `feat: Item 1.2/2 — inherit the range from the prior
artifact's Base`.
