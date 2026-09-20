# Item 1.2 slice 1 — GREEN

## Approach

`plugin/bin/edify-review-range.sh` now implements the first-pass path of
KD-2's contract (`plans/provenance-enforcement-and-routing/outline.md`):

1. Validate the argument and resolve the artifact's repo root with
   `git -C "$(dirname "$artifact")" rev-parse --show-toplevel`, exiting 2 with
   a stderr message on either failure (missing argument, missing file, not a
   repo) — the "any other exit" row of KD-2's table.
2. Extract the `## Provenance` section with `awk`, joining each `- **Field:**`
   bullet with its indented continuation lines into one logical line before
   any pattern match runs (see below), stopping the section at the next
   `## ` heading.
3. `grep -m1` the joined lines for the `**Base:**` and `**Derived from:**`
   bullets; either missing emits `NO-PROVENANCE:` (exit 1).
4. `sed -E` extracts the 40-hex sha from `**Base:**` (backtick-quoting
   optional, matching both slice 1's fixture and the KD-2 sha shape) and the
   value after `**Derived from:**`. A base that isn't 40 hex chars emits
   `UNRESOLVED: <base>` before any git call — no sha-shaped input ever reaches
   `git rev-parse`.
5. `git -C "$root" rev-parse --verify "<base>^{commit}"` resolves the base
   against the repo; a failure (bad sha, sha not in this repo) emits
   `UNRESOLVED: <base>`.
6. A `case` on `derived_from`: `none` prints `RANGE: <base>..HEAD` and exits
   0 (slice 1's contract); `superseding <path>` is structured but not
   implemented — it currently emits `NO-PRIOR: <path>` unconditionally, with a
   `TODO` comment naming what slices 2–8 add (resolve the prior artifact
   against `$root`, read its `Base:`, compare: match → `RANGE`, differ →
   `CONFLICT: base <a> != <b> inherited from <path>`, missing/base-less prior
   → `NO-PRIOR`); anything else falls through to `NO-PROVENANCE:`.

The base sha is read only from the artifact text (via the `awk`/`sed`
pipeline above) — never from `HEAD`, `git log`, or `merge-base` — matching
KD-2's ban on recomputation and the "genuine red" the RED/test-review reports
document (a two-commit fixture that a `git rev-parse HEAD` script would fail).

## Wrapped-bullet parse method

The `awk` script tracks a `bullet` accumulator inside `## Provenance`:

- A line starting `- **` closes the previous bullet (printing it) and starts
  a new one.
- A line that is *not* a new bullet but is indented (`^[[:space:]]+[^[:space:]]`)
  is a continuation: strip leading whitespace and append with a single space
  — this is what joins a hard-wrapped `**Derived from:**` value onto its
  bullet before any `grep`/`sed` match runs.
- A blank or unindented non-bullet line closes the current bullet without
  starting a new one (defends against stray prose inside the section).
- `END` flushes a bullet still open at EOF (covers `## Provenance` being the
  artifact's last section).

This slice's test doesn't exercise wrapping (that's slice 8), but the
structure handles it without a later rewrite, per the dispatch's "leave room
for other verdicts without a rewrite" instruction.

## Test output

Slice test:

```
# Test Report

**Summary:** 1/1 passed

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
```

Full suite:

```
**Summary:** 291/307 passed, 16 skipped
```

No new failures; the 16 skips are pre-existing (unrelated to this slice).

## Shellcheck

One SC2016 info hit on the `sed -E 's/^- \*\*Base:\*\*...` line — a false
positive: the sed script is single-quoted deliberately so `\1` and the
literal `*` characters are sed syntax, not shell expansions. Suppressed
inline with `# shellcheck disable=SC2016` and a one-line justification.
After that:

```
$ shellcheck plugin/bin/edify-review-range.sh
$ echo $?
0
```

Clean.

## Precommit

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
✓ Precommit OK
```

## Commit

`feat: Item 1.2/1 — first-pass range from the artifact's Base` (subject
rewritten by the commit-msg hook per the repo's gitmoji convention).

## Scope

Touched: `plugin/bin/edify-review-range.sh` (implementation). No change to
`tests/test_review_range.py` — slice 1's test needed no fixture adjustment.
