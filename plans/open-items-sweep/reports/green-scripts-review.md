# Code review — GREEN of the five reviewed RED tests

Review of the GREEN work for `plugin/bin/edify-review-range.sh` and
`scripts/check_line_limits.sh`, against the five RED tests, the RED review
(`red-scripts-review.md`), and the Robustness items at
`plans/provenance-enforcement-and-routing/reports/deliverable-review.md:185-275`
(Minor 4-9).

Every finding below is fixed. Three fixes applied, all in the working tree.
**No commit was made** — see §State, which is the one thing a reader needs
before anything else here.

## State: the commit under review no longer exists at HEAD

The target named for review, commit `257b4828`, was reset out of HEAD before
this review began. Reflog `HEAD@{0}` reads `reset: moving to HEAD~1`,
`ORIG_HEAD` is `257b4828`, HEAD and `main` are both `5f860e07`, and
`git merge-base --is-ancestor 257b4828 HEAD` reports not reachable. The
commit object survives, so nothing was lost, and the review below is against
that object plus the current working tree.

The reset was not an agent's. The team lead confirms it as my human partner's,
and reads it as meaning the `edify-review-range.sh` change must land through
an approved edit rather than by hand. Separately, `green-scripts.md` records
that `Edit` and `Write` both failed on that one path with
`The server-side auto mode classifier gave no verdict`. The reset was mixed,
then `git checkout HEAD -- plugin/bin/edify-review-range.sh` restored that
single file. The script's four fixes are held as an unapplied patch at
`plans/open-items-sweep/reports/edify-review-range.patch`, which still
applies cleanly.

Consequences for this review, per the lead's instruction:

- `plugin/bin/edify-review-range.sh` was reviewed from the commit object and
  probed by applying the patch to a copy under `$TMPDIR`. It was not written
  to by any means, and the patch was not reapplied. Findings against it would
  appear below as exact proposed hunks; there are none, and §No proposed hunks
  says why.
- The three fixes below are all in the eight files already unstaged in the
  tree, which the lead permits editing in place. Nothing else was touched.
- Nothing was committed. `just precommit` is red on exactly four tests because
  the patch is unapplied, which is the chosen state rather than a defect.

## Major

**1. The `wc -l` residual-bound comment rested on a false claim.** FIXED.

`scripts/check_line_limits.sh` `check_cap()` carried:

```
    # `wc -l` counts newlines, so a file with no terminating newline
    # under-counts by one — low realism for markdown here, since `rumdl fmt`
    # terminates files, so this residual is not itself guarded against.
```

`rumdl fmt` does not terminate files in this project. `.rumdl.toml` sets
`enable = ["MD013"]` and its own header comment says "hard-wrap markdown
prose at 80 columns, and nothing else"; MD047, the
file-should-end-with-newline rule, is not enabled and appears nowhere in the
repo. Probed: a markdown file whose last line has no newline survives both
`rumdl fmt` and `rumdl check` unchanged, each reporting "No issues found".
The whole low-realism argument therefore rested on a formatter behaviour that
does not happen — the §No Confabulation case, where an ungrounded mechanism
claim is asserted as established fact.

The comment also scoped itself to markdown while sitting in `check_cap()`,
which the script calls for Python under `src/` and `tests/` as well.

Replaced with the measured position. `ruff format` does terminate files
(probed: `x = 1` gains a trailing newline) and every checking recipe runs it,
so Python is covered; markdown is not covered by anything:

```
    # Residual, unguarded: `wc -l` counts newlines, so a file whose last
    # line carries no terminating newline counts one short — a cap+1-line
    # file passes. Python source is terminated by `ruff format`, which every
    # checking recipe runs; markdown is not, since `.rumdl.toml` enables
    # MD013 alone and no other gate here requires a trailing newline.
```

Empirically the residual is still unrealised: scanning every file in the
script's scope found one unterminated file, `docs/superpowers/specs/._…md`,
an AppleDouble sidecar inside a directory the script already excludes. So
the spec's judgement that a comment beats code stands — the *reason* was
wrong, not the conclusion.

## Minor

**1. The `# noqa: PLR0913` justification called all six parameters
keyword-only.** FIXED.

`tests/line_limits_helpers.py` claimed "each param is an independent,
keyword-only test-fixture toggle". Only `omit_root` and `second_root` are
keyword-only; `root`, `allowlist`, `path_prepend` and `script` sit before the
`*`. `root` is also not a toggle — it is the required subject of the call,
and the one parameter the docstring does not document individually, so
"already documented individually below" over-reached too. Rewritten to what
the signature actually is:

```python
def _run_check_line_limits(  # noqa: PLR0913 — `root` plus five independent
    # toggles, each documented in the docstring below and each selecting a
    # different invocation shape (argv, argv[0], CWD or PATH); bundling them
    # into a struct would only add an indirection layer for this file's own
    # tests, the sole caller.
```

Each of the five is now a checkable claim: `allowlist` and `second_root`
change argv, `script` changes argv[0], `omit_root` changes argv and CWD,
`path_prepend` changes PATH. All five are documented in the docstring.

Verified the suppression is real and not stale: bare `ruff check` passes on
the file; deleting the noqa reproduces
`PLR0913 Too many arguments in function definition (6 > 5)`; `RUF100`
does not flag it as unused.

**2. "already at its line cap" was not true of a 377-line file.** FIXED.

`tests/test_line_limits_exit_codes.py`'s new paragraph justified the test's
placement by saying `tests/test_line_limits.py`, "its natural home, is
already at its line cap". That file is 377 lines against a cap of 400. The
substantive point holds — the test and its separators run to 32 lines, so
adding it there would breach the cap — but a file with that much headroom
left is not at its cap, and the shared conventions
warn specifically that a file parked at its cap has stopped emitting a
signal. Reworded to "has no room left under its line cap", which is the true
claim and does not bake in a count that rots.

Worth noting where the phrasing came from: the RED review's own Minor 3 wrote
it accurately, as "at its line cap (377 lines; the test would push it over
400)". The parenthetical that made it checkable was dropped on the way into
the docstring, leaving only the part that overstates.

## No proposed hunks for `plugin/bin/edify-review-range.sh`

I found no defect in the patch, so there is nothing to propose. What I
checked, and the four things I considered proposing and rejected:

**The `CONFLICT:` line now prints canonical shas, not the artifact's bytes.**
No test asserts this, so it is the one change beyond minimal. Rejected as a
finding: it is deliberate, documented in situ, and the better output — an
operator comparing two bases wants them in one form. The existing conflict
test stays green because its fixture shas come from `git rev-parse` already.

**`UNRESOLVED: <sha>` still does not say which artifact's base failed.** The
RED review handed this to GREEN explicitly as a residual, and said in the same
breath that it "does not change the verdict here" and would be "worth a KD-2
note if the verdict line is ever revisited". GREEN discharged it the only way
open without changing the verdict: the header table now states that
`UNRESOLVED:` covers this artifact's own `Base:` or a prior's, one hop back.
That informs a script reader, not the operator reading the line. Left as
designed, and consistent with how the deliverable review treated the three
causes sharing one bare `NO-PROVENANCE:`.

**A backticked `none` carrying a comma-attached rationale.**
`` - **Derived from:** `none`, first pass `` yields `NO-PROVENANCE:`. So does
the bare `none, first pass` — the first-word split keeps the comma either way.
The fix's comment claims only that `` `none` `` "reads the same as bare
`none`", which is exactly true, limitation included. The tree's real idiom is
the space-separated `none — <rationale>`, pinned by
`test_first_pass_none_with_rationale_emits_range` and passing. Pre-existing
and symmetrical, so not this patch's business.

**`\r` inside an awk bracket expression is unverified off this box.** If an
awk read `\r` as a literal `r`, `[ \t\r]+$` would strip trailing `r`
characters instead. Probed here: mawk 1.3.4 handles it correctly, and the
CRLF probe passes end to end. I am not raising it as a risk, because nothing
grounds one — the shell-gotchas catalogue does not list this among the
GNU-versus-BSD divergences, and `\t` has sat in the same bracket expression
since before this patch, so the escape class is not new. Recording it only as
the same kind of unverified-on-macOS claim that
`_write_padded_wc_shim`'s docstring marks explicitly for BSD `wc` padding.
Unlike that one, the CRLF fix has no shim test locking it against a stricter
awk, which is the option if it ever seems worth buying.

## Checked and clean

**Minimality against each test.** Each of the five fixes is the smallest
change that turns its test green, and no fix is unreachable from a test. One
change goes marginally beyond: the `CONFLICT:` `printf` now prints
`$resolved_prior_base` rather than the prior artifact's raw text, which no
test asserts. It is correct, deliberate and documented in situ, and the
existing conflict test stays green because its fixture shas come from
`git rev-parse` and are already canonical. Flagging it as scope, not as a
defect: an operator now sees canonical shas in the conflict line rather than
the literal bytes in the artifact, which is the more useful pair.

**`\r` handling covers every line that is read, not one site.** The fix is
one character class in `provenance_of`'s per-line strip,
`sub(/[ \t\r]+$/, "")`, and `provenance_of` is the sole reader of artifact
text — for this artifact and for the prior one. Everything downstream
(`grep -m1`, `base_value_of`, the `derived_from` sed) reads its already
stripped output. With CRLF the `\r` is always line-final, so a trailing-strip
is sufficient. Probed on the hardest shape available: a whole-file-CRLF
artifact with a *wrapped* second-pass `Derived from:` naming a prior artifact
that is itself whole-file CRLF. Result `RANGE: <sha>..HEAD`, exit 0. Both
casualties the RED review named, `Base:` and `Derived from:`, are fixed by
the single site.

**No stderr suppression and no masking `|| true`.** The new resolution is
`git -C "$root" rev-parse --verify --quiet "${prior_base}^{commit}"` inside
an `if !`, with no `2>/dev/null` and no `|| true`. `--quiet` suppresses only
git's unknown-revision message, which is the verdict rather than a failure;
genuine diagnostics still reach stderr. Probed: a prior `Base:` naming a real
blob prints `UNRESOLVED: <sha>` on stdout and git's
`expected commit type, but the object dereferences to blob type` on stderr —
the verdict is right and the diagnostic is not swallowed. That is identical
to the pre-existing own-base path, so the two are consistent. The `if !`
form also keeps the exit status visible, which a bare assignment under
`set -e` would not.

**The compare uses the resolved canonical sha on both sides.** Confirmed at
both sites, the equality test and the `printf`. Probed: an uppercase prior
`Base:` naming the same commit yields `RANGE:` exit 0; a phantom 40-`f` prior
`Base:` yields `UNRESOLVED: ffff…` exit 1 with clean stderr; a genuinely
divergent pair still yields `CONFLICT:` exit 1 with both shas.

**KD-2's "one hop only" clause survives the new resolution step.** Adding a
`rev-parse` of the prior's base is the change most likely to have started
walking the chain. It does not: only the prior's `Base:` is read, never its
own `Derived from:`. Probed with a three-deep chain whose grandprior base
mismatches while the prior's matches — result `RANGE:`, exit 0, the
grandprior ignored. `test_one_hop_only_ignores_grandprior_mismatch`, which
the deliverable review singles out as the only test pinning that clause,
stays green.

**The header verdict table is still true.** The `CONFLICT:` format line
matches the `printf`, and the new parenthetical correctly states that
`UNRESOLVED:` now covers this artifact's own `Base:` or a prior's, one hop
back. The extension is outside what KD-2's table enumerates, and the header
says so in the clause rather than silently widening it.

Checked the one operator-facing copy of the same table,
`plugin/skills/deliverable-review/SKILL.md:46-47`: it routes
`UNRESOLVED: <base>` to "ask the user", which stays correct when `<base>` is
a prior's. No edit needed, and the spec's own reasoning about three causes
sharing one `NO-PROVENANCE:` line applies — the operator's action does not
branch on which base failed.

**The second-positional arm matches the `-*)` arm and exits 2.** Same
diagnostic shape, same stream, same code. Probed:
`check_line_limits.sh <a> <b>` prints
`check_line_limits: unexpected extra argument: <b>` on stderr, nothing on
stdout, exit 2, and does not walk either root — the 401-line file under the
first root is not reported, which is what distinguishes rejection from
silently walking the second. The single-positional control still exits 1 with
the overage, so the guard did not break the happy path.

**Whitespace safety.** No splitting introduced anywhere. The shell guard uses
`"$1"`; the helper appends `str(second_root)` to an argv list. Probed both
directions with a root path containing a space: as a sole positional it walks
correctly and reports the overage; as a second positional it is rejected with
the full spaced path intact in the diagnostic.

**Line limits.** Every touched file is under 400: the patched script 186,
`check_line_limits.sh` 210 after my edit, `line_limits_helpers.py` 169,
`test_line_limits_exit_codes.py` 113, and the five `test_review_range_*`
modules 244, 77, 69, 68, 44.

**shellcheck.** Clean on `scripts/check_line_limits.sh` and on the patched
`edify-review-range.sh`, so the patch introduces no new finding either.

**The five module docstrings say what is true.** Verified as history, not
just as a claim: `tests/test_review_range.py` was added by `78206a83` and
deleted by `5594a753`, whose own message reads "`tests/test_review_range.py`
is split by verdict". It stood at 396 lines against a 400 cap immediately
before the split, so "to keep each module under its line cap" is the real
reason and not a retrofitted one. KD-2 records that name. Five modules, one
per verdict, plus `review_range_helpers.py`, which is not a test module — so
"one of five" is right.

## One latent trap in the tree, left alone deliberately

`tests/line_limits_helpers.py`: `second_root` combined with
`omit_root=True` would become the *first* positional, so a test written that
way would silently exercise the wrong root rather than fail. The RED review
found this, named it, and scoped it out because no caller does it. I am
leaving that decision standing rather than quietly overriding it — a guard
here would be speculative hardening, and reversing a prior review's explicit
scoping call is the lead's to make, not mine. Raising it so it is not lost:
if a future test ever passes both, it will pass for the wrong reason.

## Full `just precommit` output

Run after the three fixes above.

````
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 356/361 passed, 4 failed, 1 xfail

## Failures

### tests/test_review_range_range.py::test_prior_base_uppercase_same_commit_emits_range FAILED

```python
tests/test_review_range_range.py:112: in test_prior_base_uppercase_same_commit_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: CONFLICT: base a18fd84c9d55e7389902fc9634ccdff404eda7db != A18FD84C9D55E7389902FC9634CCDFF404EDA7DB inherited from plans/prior-job/outline.md
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-752/test_prior_base_uppercase...9634ccdff404eda7db != A18FD84C9D55E7389902FC9634CCDFF404EDA7DB inherited from plans/prior-job/outline.md\n', stderr='').returncode
```

### tests/test_review_range_range.py::test_backticked_none_emits_range FAILED

```python
tests/test_review_range_range.py:212: in test_backticked_none_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: NO-PROVENANCE:
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-752/test_backticked_none_emits_ran0/repo/plans/job/outline.md'], returncode=1, stdout='NO-PROVENANCE:\n', stderr='').returncode
```

### tests/test_review_range_range.py::test_crlf_artifact_emits_range FAILED

```python
tests/test_review_range_range.py:243: in test_crlf_artifact_emits_range
    assert result.returncode == 0, result.stdout + result.stderr
E   AssertionError: UNRESOLVED: b47b76becff0d65b0c4b0ed9147afde64fed4ae4
E
E   assert 1 == 0
E    +  where 1 = CompletedProcess(args=['edify-review-range.sh', '/tmp/claude-1000/pytest-of-david/pytest-752/test_crlf_artifact_emits_.../repo/plans/job/outline.md'], returncode=1, stdout='UNRESOLVED: b47b76becff0d65b0c4b0ed9147afde64fed4ae4\n', stderr='').returncode
```

### tests/test_review_range_unresolved.py::test_unresolvable_prior_base_reported FAILED

```python
tests/test_review_range_unresolved.py:69: in test_unresolvable_prior_base_reported
    assert result.stdout == f"UNRESOLVED: {phantom}\n"
E   AssertionError: assert 'CONFLICT: ba.../outline.md\n' == 'UNRESOLVED: ...fffffffffff\n'
E
E     - UNRESOLVED: ffffffffffffffffffffffffffffffffffffffff
E     + CONFLICT: base b47b76becff0d65b0c4b0ed9147afde64fed4ae4 != ffffffffffffffffffffffffffffffffffffffff inherited from plans/prior-job/outline.md
```
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✗ Precommit failed
````

Reading that output:

- **The four failures are the unapplied patch, nothing else.** Each is one of
  the five reviewed tests, and each fails against the pre-fix script exactly
  as the RED phase recorded. The fifth test,
  `test_two_positional_roots_exits_2_with_usage_diagnostic`, passes, because
  its fix is in `check_line_limits.sh`, which was not reverted.
- **`run-checks` passed.** `precommit` runs it first and it printed nothing:
  bare `ruff check -q`, `ruff format --check -q`, `docformatter -c src tests`
  and `mypy` are all clean on my edits. Confirmed separately against the
  venv's `ruff` for the two files I changed.
- **The three `oversized-file:` lines are pre-existing and allowlisted** at
  their measured counts, reported on every run by design.
- **`rumdl fmt --check` passed**, as did version consistency and design links.

Applying the patch would take the suite to 360/361 with 1 xfail and the gate
green, which is what `257b4828` measured before it was reset.

## What is left for my human partner to decide

1. Whether `plans/open-items-sweep/reports/edify-review-range.patch` lands,
   and by what route. It still applies cleanly; `git apply --check` exits 0.
   The review above clears its content, so the open question is the route, not
   the change.
2. Whether to commit. The three fixes above plus the eight files already in
   the tree are ready. The gate cannot go green until (1) is settled, and
   `--no-verify` is not an option here.
