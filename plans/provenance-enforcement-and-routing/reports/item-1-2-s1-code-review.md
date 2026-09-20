# Item 1.2 slice 1 — code review

Scope: `plugin/bin/edify-review-range.sh` only. `tests/test_review_range.py`
was read and run, never edited or moved.

Verdict: **fixes applied.** Two defects made the script emit the wrong
verdict for the repo's own real artifacts — one of them on slice 1's own
contract path. Both fixed. Nothing left unfixable.

## 1. Mutation probe — the base comes only from the artifact text

Replaced the base derivation with `git rev-parse HEAD`:

```
-if ! resolved_base=$(git -C "$root" rev-parse --verify "${base}^{commit}" 2>&1); then
+if ! resolved_base=$(git -C "$root" rev-parse HEAD 2>&1); then
```

`pytest tests/test_review_range.py` **redded**:

```
### tests/test_review_range.py::test_first_pass_emits_range FAILED

tests/test_review_range.py:104: in test_first_pass_emits_range
    assert result.stdout == f"RANGE: {sha}..HEAD\n"
E   AssertionError: assert 'RANGE: 8b448...5c781..HEAD\n' == 'RANGE: 52177...979c4..HEAD\n'
E     - RANGE: 521774b6863971ca3666895504a06262789979c4..HEAD
E     + RANGE: 8b448ba8377eb01906470fe26942670feab5c781..HEAD
```

Two visibly different shas — the two-commit fixture discriminates as the
test review intended. Restored with `git checkout --`, confirmed
byte-identical to `78206a83`, test green again.

## 2. Real artifacts

Run by bare name with `plugin/bin` on PATH, CWD `/tmp`.

### Before the fixes

| Artifact | stdout | exit |
|---|---|---|
| `plans/design-routing-and-provenance/outline.md` | `NO-PROVENANCE:` | 1 |
| `plans/provenance-enforcement-and-routing/outline.md` | `NO-PROVENANCE:` | 1 |

Both wrong. The `awk` join is correct in both cases — the parsed
`$derived_from` is exactly:

- first pass: `none — this job originates from the task frame, not from a
  deliverable-review.`
- second pass: `` `plans/provenance-reach-and-sweep/reports/deliverable-review.md`,
  superseding `plans/provenance-reach-and-sweep/outline.md` ``

It is the `case` classification that fails on both.

### After the fixes

| Artifact | stdout | exit |
|---|---|---|
| `plans/design-routing-and-provenance/outline.md` | `RANGE: 926e372d02a0366202b2bb6a684551128d1f2a66..HEAD` | 0 |
| `plans/provenance-enforcement-and-routing/outline.md` | `NO-PRIOR: plans/provenance-reach-and-sweep/outline.md` | 1 |

The first is correct and is the base copied verbatim from the artifact. The
second is `NO-PRIOR:` by design for this slice, but now reaches the
superseding arm with the prior path correctly extracted, rather than falling
through to `NO-PROVENANCE:`.

## Findings

### F1 — Critical, fixed. A real first-pass artifact got `NO-PROVENANCE:`

`case "$derived_from" in none)` matches only the bare word. The repo's own
first-pass artifact writes `none — this job originates from the task frame,
…`, and `design-content-rules.md` §Provenance Section shows the same
trailing-rationale idiom on the `Base:` line of its template. So slice 1's
own contract path — `Derived from: none` emits `RANGE:` — failed against the
only real first-pass artifact in the tree, and failed by reporting that a
well-formed §Provenance section was absent.

Fixed: the value's first word decides.

```bash
if [[ "${derived_from%% *}" == "none" ]]; then
```

**Not covered by slice 1's test**, which writes a bare `none`. Flagged for
the orchestrator: a case with a trailing rationale clause belongs in a later
slice's test (slice 4 or 8 is the natural home) — this fix is currently
verified only by the real-artifact run above.

### F2 — Major, fixed. The `superseding` arm was unreachable

`superseding\ *` requires the value to *begin* with `superseding`. The
prescribed shape begins with the motivating report path and reaches
`superseding` only after it, so every conforming second-pass artifact fell
through to `*)` → `NO-PROVENANCE:`.

This is worse than incomplete, which is why I fixed it rather than leaving
it: the arm reads as a wired-up branch awaiting a body, so slice 2's GREEN
would fill in the TODO and get a passing test only by writing a fixture in a
shape the spec does not prescribe, with the real shape still routed to the
wrong verdict. The classification is now:

```bash
superseding_quoted='superseding[[:space:]]+`([^`]+)`'
superseding_bare='superseding[[:space:]]+([^[:space:]]+)'
```

Backtick-quoted tried first, so a path containing spaces (slice 8) stays
whole; the bare form is the fallback. The arm's *body* is untouched — still
the `NO-PRIOR:` skeleton with its TODO. No inheritance behaviour was
implemented.

Left for slices 2–8, flagged not fixed: a `Derived from:` naming **only** the
report, with no `superseding` (KD-1's sixth row treats this as a real case),
still falls through to `NO-PROVENANCE:`. Which of KD-2's verdicts that shape
deserves is a design question for the slice that implements inheritance, not
a code-review call.

### F3 — Major, fixed. Two `2>&1` captures silenced git's diagnostic

- `root=$(git … rev-parse --show-toplevel 2>&1)` captured git's `fatal:` into
  a variable that was never printed. Redirect removed; git's message now
  reaches stderr ahead of the script's own. Verified — an artifact outside
  any repo prints `fatal: not a git repository …` then
  `edify-review-range.sh: not inside a git repo: <dir>`, exit 2, nothing on
  stdout.
- `resolved_base=$(git … rev-parse --verify "${base}^{commit}" 2>&1)` was the
  same pattern, but here the non-zero exit *encodes a result* (the base names
  no commit) rather than a failure. Switched to
  `git rev-parse --verify --quiet`, the documented form for exactly that
  test, so nothing is captured-and-dropped and the `UNRESOLVED:` line carries
  the diagnostic.

Both `grep -m1 … || true` are the legitimate no-match case (a missing
`**Base:**` or `**Derived from:**` bullet is a verdict, `NO-PROVENANCE:`).
Confirmed and kept.

### F4 — Minor, fixed. A non-sha `Base:` printed the whole bullet

The old `sed -E 's/^- \*\*Base:\*\* *`?([0-9a-fA-F]{40})`?.*/\1/'` leaves the
line untouched when it does not match, so `- **Base:** TODO` — KD-1's own
repair value — emitted `UNRESOLVED: - **Base:** TODO`. Now the value is taken
first, then its first word, then backticks stripped; the hex check is
unchanged. Measured: `UNRESOLVED: TODO`. The `# shellcheck disable=SC2016` on
that line went with the capture group it justified.

### F5 — Minor, fixed. `${derived_from%% }` stripped one trailing space only

`%%` with a fixed (non-glob) pattern behaves as `%`. Intent was clearly to
strip trailing whitespace left by the join. Replaced with
`sub(/[ \t]+$/, "")` inside the `awk` block, which strips it from every line
before joining — covering trailing whitespace on the bullet line itself and
on each continuation line, which the bash-side strip could not reach.
Measured against a fixture whose continuation line ends in three spaces: the
extracted path is `plans/my job/outline.md`, clean.

### F6 — Minor, fixed. `[[:space:]]` inside `awk`

`sed -E` with `{40}` is POSIX ERE and fine on BSD; `grep -m1` is in both GNU
and BSD grep; `[[ =~ ]]` is bash and the shebang is bash — all fine. The one
real portability hazard was `[[:space:]]` in the `awk` regexes: the
one-true-awk on older macOS reads it as a plain bracket set of `[`, `:`, `s`,
`p`, `a`, `c`, `e`, which mis-parses **silently**. Replaced with `[ \t]`.
(`[[:space:]]` in the two bash `=~` patterns stays — bash uses the system
regex library, where the class is reliable.)

### F7 — Note, not a defect. `TODO(slices 2-8)`

Acceptable as a skeleton marker. **It must not survive Item 1.2** — slice 2's
GREEN removes it when it implements the inheritance compare. Recorded here so
the orchestrator can hold the item open on it.

No dead branches remain: the `case` became three sequential guards, each
reachable, each measured above.

## Edge cases measured

All against a throwaway two-commit repo at `<tmp>/my repo/` (spaces in the
repo directory itself), script invoked by bare name from an unrelated CWD
with the artifact as an absolute path.

| Case | stdout | exit |
|---|---|---|
| spaced dirs, `Derived from: none` | `RANGE: <first sha>..HEAD` | 0 |
| wrapped real-shape value, trailing spaces, spaced prior path | `NO-PRIOR: plans/my job/outline.md` | 1 |
| `Base:` is `TODO` | `UNRESOLVED: TODO` | 1 |
| 40 hex naming no commit | `UNRESOLVED: 0123…6789`, stderr empty | 1 |
| no `## Provenance` section | `NO-PROVENANCE:` | 1 |
| artifact outside any repo | *(stdout empty)*, git `fatal:` + script message on stderr | 2 |
| no argument | *(stdout empty)*, usage on stderr | 2 |
| missing file | *(stdout empty)*, `no such artifact:` on stderr | 2 |

Every exit-2 path writes nothing to stdout and something to stderr; every
exit-1 path writes exactly one verdict line to stdout. `dirname --` was
already correct, and every expansion in the script is quoted.

## Final checks

```
$ shellcheck plugin/bin/edify-review-range.sh
$ echo $?
0
```

```
$ pytest tests/test_review_range.py -v
# Test Report

**Summary:** 1/1 passed

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
```

Full suite:

```
**Summary:** 291/307 passed, 16 skipped
```

`just precommit`:

```
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 306/307 passed, 1 xfail
✓ Precommit OK
```

```
$ git diff --stat
 plugin/bin/edify-review-range.sh | 82 +++++++++++++++++++++++++---------------
 1 file changed, 51 insertions(+), 31 deletions(-)
```

124 lines, well under the cap. Not committed — `plugin/bin/edify-review-range.sh`
is the only modified path in the tree.
