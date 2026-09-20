# Item 1.2 slice 2 — code review

Scope: `plugin/bin/edify-review-range.sh` only. `tests/test_review_range.py`
was read and run, never edited or moved (`git diff --stat` below confirms).

Verdict: **one Minor fixed** (a stale comment). No behavioural defect found.
The implementation already satisfies every row of KD-2's table that slices 3,
6 and 7 are written to pin — those GREENs will be no-ops. Two notes left
unfixed, both deliberate, both recorded below for the orchestrator.

## 1. Mutation probes — both survive, as the dispatch predicted

Applied to the real file, run against `pytest tests/test_review_range.py`,
restored with `git checkout --` and verified byte-identical against a
pre-mutation copy each time.

| Mutation | Result | Reading |
|---|---|---|
| (a) skip reading the prior — `prior_base="$resolved_base"` inserted before the compare | 2/2 **passed** | not a defect: slice 2's fixture gives prior and artifact the *same* base, so a compare against self is indistinguishable from a correct inheritance read. Slice 3 (conflict) is what discriminates. |
| (b) `prior_provenance=$(provenance_of "$artifact")` instead of `"$prior"` | 2/2 **passed** | same reason, same discriminator. |

Both are the expected outcome, not evidence of a weak test. Slice 2's
specified assertion is "prior with a matching base ⇒ exit 0 and the `RANGE:`
line", and that is exactly what it asserts; the inheritance *read* is only
observable when the two bases differ. Verified instead by direct probe §2,
which does exercise the read.

## 2. Direct probes under `$TMPDIR`

Throwaway two-commit repo at `<tmp>/my repo/` (spaces in the repo directory
itself), script invoked **by bare name** with `plugin/bin` on `PATH`, CWD
outside the repo, artifact given as an absolute path. `FIRST` and `SECOND`
are the two commit shas; `<prior>`/`<path>` in the table are verbatim from
stdout.

| # | Input | stdout | exit |
|---|---|---|---|
| P1 | prior `Base:` = FIRST, artifact `Base:` = SECOND | `CONFLICT: base 9cccacd2…bf264 != 38b55250…e0855 inherited from plans/prior-job/outline.md` | 1 |
| P2 | `superseding` names a path that does not exist | `NO-PRIOR: plans/nope/outline.md` | 1 |
| P3 | prior exists, its `Base:` is `TODO` | `NO-PRIOR: plans/prior-todo/outline.md` | 1 |
| P4 | prior exists, has `## Provenance` but **no `Base:` bullet** | `NO-PRIOR: plans/prior-nobase/outline.md` | 1 |
| P5 | prior exists, has **no `## Provenance`** at all | `NO-PRIOR: plans/prior-noprov/outline.md` | 1 |
| P15 | prior's `Base:` is a 12-char abbreviated sha | `NO-PRIOR: plans/prior-short/outline.md` | 1 |
| P13 | `superseding` names a **directory** | `NO-PRIOR: plans/adir/outline.md` | 1 |
| P6 | prior path with a space, backtick-quoted (`plans/my job/outline.md`) | `RANGE: 38b55250…e0855..HEAD` | 0 |
| P7b | backticked prior path followed by `, because reasons.` | `RANGE: 38b55250…e0855..HEAD` | 0 |
| P11 | `Derived from: none — originates from the task frame.` | `RANGE: 38b55250…e0855..HEAD` | 0 |
| P12 | prior matches, prior's **own** `Derived from:` names a grandparent whose `Base:` differs | `RANGE: 38b55250…e0855..HEAD` | 0 |
| P14 | artifact's own `Base:` is a 12-char abbreviated sha | `UNRESOLVED: 38b552504574` | 1 |
| P10 | `Derived from:` names only the report, no `superseding` | `NO-PROVENANCE:` | 1 |
| P7 | **bare** (unbackticked) prior path ending a sentence: `superseding plans/prior-job/outline.md.` | `NO-PRIOR: plans/prior-job/outline.md.` | 1 |
| P8 | prior path written `./plans/prior-job/outline.md` | `RANGE: 38b55250…e0855..HEAD` | 0 |
| P9 | prior path written absolute | `NO-PRIOR: /tmp/…/my repo/plans/prior-job/outline.md` | 1 |

Every exit-1 row wrote exactly one verdict line to stdout and **nothing to
stderr**. No row produced an exit other than 0 or 1.

**Against KD-2's table:** P1 matches the `CONFLICT:` wording character for
character, including `inherited from <path>`. P2 is slice 6's behaviour; P3,
P4, P5, P15 are slice 7's, and all four already return `NO-PRIOR: <path>` —
KD-2's "missing or carries no full-sha `Base:`" is fully covered. **Slices 3,
6 and 7's GREENs are no-ops against the current implementation.** Their RED
phases still have work: each must produce a genuine red, which here means
red-against-a-mutation rather than red-against-unimplemented-behaviour, or
the slice reports must say plainly that the behaviour pre-existed.

## 3. Real artifacts

Bare name, CWD `$TMPDIR`, absolute artifact path.

| Artifact | stdout | exit |
|---|---|---|
| `plans/provenance-enforcement-and-routing/outline.md` (prior: `plans/provenance-reach-and-sweep/outline.md`) | `RANGE: 926e372d02a0366202b2bb6a684551128d1f2a66..HEAD` | 0 |
| `plans/provenance-reach-and-sweep/outline.md` (prior: `plans/design-routing-and-provenance/outline.md`) | `RANGE: 926e372d02a0366202b2bb6a684551128d1f2a66..HEAD` | 0 |
| `plans/design-routing-and-provenance/outline.md` (first pass) | `RANGE: 926e372d02a0366202b2bb6a684551128d1f2a66..HEAD` | 0 |

All three expected, and the second-pass rows are the inheritance path running
end to end on real wrapped `Derived from:` values. This is the row slice 1's
code review left at `NO-PRIOR:`; slice 2 closed it.

## 4. Prior-path extraction

The value after `superseding` is matched by two regexes in order:
backtick-quoted (`` superseding[[:space:]]+`([^`]+)` ``) first, bare
(`superseding[[:space:]]+([^[:space:]]+)`) as fallback.

- **Backticks stripped:** yes — the capture group is inside the backticks.
- **Spaces survive:** yes, P6. The quoted form is tried first precisely for
  this, and `"$prior_path"`/`"$prior"` are quoted at every use. Slice 8's
  `plans/my job/outline.md` case already passes.
- **Trailing `,`/`.` stripped:** **no**, and only the bare fallback is
  affected (P7b shows the quoted form is immune because the backtick ends the
  capture). See F2.

## 5. One hop only

Confirmed by P12: the prior's `Derived from:` is never read. Only
`grep -m1 '\*\*Base:\*\*'` is applied to `prior_provenance`; no code path
inspects a `**Derived from:**` bullet in the prior. Matches KD-2's "One hop
only — each artifact in a chain was compared against its predecessor at its
own review."

**Double parse cost:** the prior is parsed with the same `provenance_of` and
`base_value_of` the artifact uses — one awk pass over a short section, no
duplicated parsing rules. Correct factoring; nothing to change.

## 6. Error handling and style

Audited against `CLAUDE.md` §Error Handling:

- **No `2>/dev/null` anywhere.** `grep -n '2>/dev/null'` → no match.
- **`|| true` at three sites only**, all `grep -m1` for a `**Base:**` or
  `**Derived from:**` bullet (lines 90, 91, 141). Each is the sanctioned
  case: a missing bullet is a *verdict* (`NO-PROVENANCE:` / `NO-PRIOR:`), and
  grep's exit 1 encodes "no match", not failure. Kept.
- **Git failures reach the terminal.** Both `git` calls were checked:
  `rev-parse --show-toplevel` is unredirected, so git's own `fatal:` lands on
  stderr ahead of the script's message (exit 2, stdout empty);
  `rev-parse --verify --quiet "${base}^{commit}"` uses `--quiet` because its
  non-zero exit *is* the `UNRESOLVED:` result. Neither captures-and-drops a
  diagnostic. This is slice 1's F3 fix, still intact.
- **Exit-2 paths print nothing on stdout**: no argument, missing file, not in
  a repo — all three re-measured, all stdout-empty with a message on stderr.
- **No `TODO`.** Slice 1's `TODO(slices 2-8)` marker is gone, as its F7
  required. `grep -n TODO` → no match.
- **No dead code.** Every branch is reachable and was reached by a probe
  above: both `superseding` regexes (P6/P7b quoted, P7 bare), the
  `NO-PROVENANCE:` fall-through (P10), `base_value_of`'s empty-argument early
  return (P4).
- **Function order.** `provenance_of` and `base_value_of` precede the entry
  point, which inverts the `entry points first` convention — but a bash
  function must be defined before the line that calls it executes, so this is
  the convention's genuine evaluation-order exception. The entry point still
  reads top-to-bottom from `artifact="${1:-}"`. Left as is.
- **`[ \t]` instead of `[[:space:]]` inside awk.** Portability claim about
  one-true-awk on older macOS; plausible, documented in the comment, and
  harmless either way. Left as is per the dispatch.
- **`set -euo pipefail`** present; `base_value_of`'s
  `[[ -z "$1" ]] && return 0` is in non-final position within the function
  body, so its exit-1 does not trip `set -e` — and P4 exercises that path
  live, reaching `NO-PRIOR:` rather than dying.

## Findings

### F1 — Minor, **fixed**. Comment described behaviour the line does not have

`plugin/bin/edify-review-range.sh:99-101` read:

```bash
# Take the `Derived from:` value's first word — it may carry an optional
# trailing rationale clause after the value.
derived_from=$(sed -E 's/^- \*\*Derived from:\*\* *//' <<<"$derived_line")
```

The `sed` strips the label and nothing else — it keeps the whole value, which
is required, since the `superseding` marker is reached only *after* the
motivating report path. The "first word" behaviour belongs to
`${derived_from%% *}` at the `none` test, 20 lines further down, and to
`base_value_of` for `Base:`. As written the comment invites a future editor
to "restore" a truncation that would break every conforming second-pass
artifact. Replaced with a comment stating what the line does and why
`Derived from:` is handled unlike `Base:`.

Comment only; no behaviour change. Tests and shellcheck re-run after the
edit, both clean.

### F2 — Minor, **not fixed** (out of contract). Bare prior path keeps trailing punctuation

P7: `superseding plans/prior-job/outline.md.` yields
`NO-PRIOR: plans/prior-job/outline.md.` — the sentence-ending period is taken
as part of the filename, so an existing prior is reported missing.

Not fixed, deliberately. `design-content-rules.md` §Provenance Section
prescribes the backticked form (`` superseding `plans/<prior-job>/outline.md` ``),
which P7b shows is immune; the bare regex is a lenience beyond the contract,
and KD-2 says nothing about punctuation. Stripping a trailing `[,.]` from the
bare capture would be three characters of regex, but it is behaviour no slice
specifies and no test would cover, and adding untested behaviour to the SUT
during a code review is the wrong direction. **Orchestrator's call** — if it
should hold, it wants a slice, not a review-time edit.

### F3 — Note, not a defect. Prior path forms outside the contract

- **Leading `./`** (P8) happens to work: `"$root/./plans/…"` resolves.
- **Absolute path** (P9) yields `NO-PRIOR:` with the absolute path echoed,
  because it is concatenated as `"$root/$prior_path"` → `<root>//<abs>`.

Neither form is in KD-2 or in the prescribed shape, so both are left as the
dispatch directs. Recorded because P9's verdict line is *wrong* rather than
merely unhandled — it says the prior is missing when it exists. A future
hardening pass would reject a non-repo-relative path explicitly rather than
letting it fall into `NO-PRIOR:`.

### F4 — Note, unchanged from slice 1. `Derived from:` naming only the report

P10 gives `NO-PROVENANCE:` for a value that names the motivating report with
no `superseding` clause. KD-1's sixth row treats this as a real, expected
shape (`Derived from:` names only the report → `TODO` in `Base:` only), and
KD-2's table has no verdict for it. Slice 1's review flagged it as a design
question and it is still open: the current answer, "the §Provenance section
is absent", is plainly false about such an artifact. Not a slice-2 defect and
not fixable as a code-review call — it needs a KD-2 amendment naming the
verdict.

## In-scope-unfixable refactorings

None. The script is 160 lines, one entry point, two helpers, every branch
measured.

## Final checks

```
$ pytest tests/test_review_range.py -v
# Test Report

**Summary:** 2/2 passed

## Passes

- tests/test_review_range.py::test_first_pass_emits_range
- tests/test_review_range.py::test_second_pass_matching_base_emits_range
```

```
$ shellcheck plugin/bin/edify-review-range.sh
(exit 0, no output)
```

```
$ git diff --stat
 plugin/bin/edify-review-range.sh | 6 ++++--
 1 file changed, 4 insertions(+), 2 deletions(-)
```

`tests/test_review_range.py` absent from the diff, as scope required. Not
committed, per the dispatch.
