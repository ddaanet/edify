# Deliverable review — Layer 1, code and tests partition

Job: `plans/provenance-enforcement-and-routing/`. Baseline:
`plans/provenance-enforcement-and-routing/outline.md` (KD-2, KD-7, KD-8;
Items 1.2, 1.10, 1.11).

Partition: `plugin/bin/edify-review-range.sh`, `scripts/check_line_limits.sh`,
`scripts/check_line_limits.allow`, `tests/review_range_helpers.py`,
`tests/test_review_range_{range,conflict,no_prior,no_provenance,unresolved}.py`,
`tests/line_limits_helpers.py`, `tests/test_line_limits.py`,
`tests/test_line_limits_exit_codes.py`. All `.md`, `plugin/portable.just`,
`justfile`, `.rumdl.toml`, `pyproject.toml` and the design-links trio are
another reviewer's.

## Critical

None.

## Major

### 1. `wc -l` is unguarded against BSD left-padding, in a script that codes for macOS everywhere else

`scripts/check_line_limits.sh:124`:

```bash
    if ! line_count=$(wc -l <"$file"); then
```

The script invests deliberately in macOS portability at three separate
sites — `:106` "`#!/usr/bin/env bash` is bash 3.2 on macOS, which has no
`declare -A`", `:141` "`mapfile -d ''` is bash 4.4", `:154` "BSD `mktemp` has
no default one, so a bare `mktemp` is a usage error on macOS" — and then
consumes `wc -l` raw. BSD/macOS `wc` left-pads its count into a fixed field;
GNU `wc` reading stdin does not. This repo already knows that: both `wc -l`
calls in `plugin/bin/triage-feedback.sh:14` and `:21` are written
`| wc -l | tr -d ' '`, and my human partner's own
`ddaanet/gitlore` shell-gotchas audit plan names that idiom "the
`wc -l | tr -d ' '` BSD-padding guards". `check_line_limits.sh:124` is the
one `wc -l` in the tree with no guard.

Failure scenario: on macOS, `check_cap` prints
`oversized-file: docs/notes.md:      401 lines > 400` instead of KD-7's pinned
`oversized-file: <path>: <n> lines > <cap>`, and the four tests asserting
`result.stdout.splitlines() == [...]` exactly
(`tests/test_line_limits.py:43`, `:61`, `:128`, `:148`, `:173`, `:209`, `:321`)
go red. The `-gt` comparison itself survives, because bash's `[` arithmetic
tolerates leading blanks — so the gate still *works*, it just reports
malformed and reds its own suite.

**Unverified on macOS.** I ran on Linux (GNU coreutils 6.12 kernel, bash
5.2.37); `wc -l < f` printed `2` unpadded here. The claim rests on the two
in-repo `tr -d ' '` guards and the audit plan naming them, not on a macOS
execution. Fix is `line_count=$(wc -l <"$file" | tr -d ' ')` — or
`tr -d '[:space:]'`, which is what the shell-scripting plugin's own
`shellcheck-on-edit.sh` uses.

### 2. KD-7's "the Python loop adopts the same line" has no test at all

KD-7 (outline `:172`) specifies: "the Python loop adopts the same line".
`scripts/check_line_limits.sh:162-169` implements it — and this job changed
that branch's output from the pre-job `❌ $file: $line_count lines (exceeds
$MAX_LINES line limit)` (see
`git show 884359b1:scripts/check_line_limits.sh`) to `oversized-file:`. No
test in the partition touches `src/` or `tests/` `.py` files: every fixture
tree in `tests/line_limits_helpers.py` and both test modules writes only
`.md`.

Failure scenario: a future edit to the `for dir in src tests` loop — a
changed message prefix, a dropped `check_cap` call, a wrong cap — is caught
by nothing. The Python branch is also the only place the pre-existing
contract lived, so a regression there silently un-gates `src/` and `tests/`.

I probed it and it is correct today: a 401-line `src/pkg/big.py` and
`tests/big.py` both report `oversized-file: … 401 lines > 400`, exit 1, and
an allowlist entry `src/pkg/big.py<TAB>401` suppresses that file's failure
(Probes §8). Correct but unpinned.

### 3. Eight line-limits tests silently read the production allowlist

`tests/line_limits_helpers.py:29-47` omits `--allowlist` when `allowlist is
None`, so the script falls through to `scripts/check_line_limits.sh:64`,
`SCRIPT_DIR/check_line_limits.allow` — the repository's real, hand-maintained
allowlist. Tests running that way:
`test_line_limits_passes_clean_tree`, `…_fails_markdown_over_400`,
`…_fails_skill_hub_over_200`, `…_skips_frozen_docs`,
`…_checks_living_superpowers_docs`, `…_fails_when_find_cannot_walk`,
`…_handles_spaced_path`, and both tests in
`tests/test_line_limits_exit_codes.py`.

This is not inference. Under the basename-matching mutant (Probes §6),
`test_line_limits_fails_skill_hub_over_200` went red — and that test passes no
`--allowlist`. It could only have changed behaviour by matching a production
entry: `plugin/skills/build/SKILL.md<TAB>218` in
`scripts/check_line_limits.allow:19`, whose basename is `SKILL.md`, gave the
fixture's 201-line `plugin/skills/x/SKILL.md` a ceiling of 218 and turned
exit 1 into exit 0.

Failure scenario: the allowlist is maintained by hand and grows. An entry
named `docs/notes.md`, `docs/my notes.md`, `docs/over.md`,
`plugin/locked.md`, `docs/superpowers/design/living.md` or
`plugin/skills/x/SKILL.md` — every one a live fixture path — converts the
matching test from a real assertion into a permanent green, with nothing to
signal it. The two `_run_check_line_limits` call sites that do pass
`--allowlist` are insulated; the other eight are not. The fix is one line in
the helper: default to a written-empty allowlist file under `tmp_path` rather
than to the script's sidecar.

## Minor

### 4. A CRLF artifact yields `UNRESOLVED:` naming a sha that resolves fine

`plugin/bin/edify-review-range.sh:40` strips only `[ \t]+$`, so a `\r`
survives into `base`. Probed (Probes §2): a CRLF-terminated first-pass
artifact prints `UNRESOLVED: 2083da05e14c…` — 40 visible hex characters that
`git rev-parse` resolves without complaint. The operator is told the base is
unresolvable and shown a base that is not.

Never a false green (the regex at `:107` rejects before any RANGE is
emitted), which is why this is Minor. But the sibling script in this same job
grew *two* dedicated CRLF tests and an explicit diagnostic
(`scripts/check_line_limits.sh:82-85`,
`tests/test_line_limits.py:247`, `:281`), on the argument that a misleading
message "masks a genuine encoding problem instead of reporting one". The same
argument applies verbatim here and was not carried across.

### 5. The prior artifact's `Base:` is compared as raw text — never resolved, never case-folded

`plugin/bin/edify-review-range.sh:151` compares `$resolved_base` (git's
canonical lowercase, from `rev-parse --verify` at `:114`) against
`$prior_base`, which is raw artifact text validated only by the syntactic
regex at `:146`. Two probed consequences (Probes §2, §7):

- Prior writes the sha uppercase, this artifact lowercase, both naming the
  same commit → `CONFLICT: base 2083da05… != 2083DA05… inherited from
  plans/prior/outline.md`. KD-2 makes `CONFLICT:` the hard stop that means
  "one of two artifacts is wrong"; here neither is.
- Prior's `Base:` is 40 hex naming no commit → `CONFLICT: base 4e003c6d… !=
  0000000000000000000000000000000000000000 inherited from …`, presenting a
  nonexistent commit as an inherited base. KD-2 line `:100` assigns
  "carries no full-sha `Base:`" to `NO-PRIOR:`; a sha that resolves nowhere is
  arguably that case, and is certainly not a conflict between two positions.

One `git -C "$root" rev-parse --verify --quiet "${prior_base}^{commit}"`
before `:151` fixes both.

### 6. `` `none` `` backtick-quoted is not recognised, while `Base:` strips backticks

`plugin/bin/edify-review-range.sh:64` strips every backtick out of the `Base:`
value; `:119` tests `${derived_from%% *} == "none"` against the raw value.
Probed (Probes §2): `- **Derived from:** `` `none` `` ` → `NO-PROVENANCE:`.
The prescribed shape at
`plugin/skills/design/references/design-content-rules.md:139` backticks every
path, so a hand-writer backticking `none` for symmetry is a plausible slip,
and the verdict it earns says the section is missing rather than that the
value is malformed.

### 7. `NO-PROVENANCE:` carries no payload for three distinct causes

`plugin/bin/edify-review-range.sh:88`, `:96` and `:161` all print bare
`NO-PROVENANCE:` for, respectively: no `## Provenance` heading; a section
missing `Base:` or `Derived from:`; and a `Derived from:` that names only the
motivating report. Every other verdict carries its subject
(`UNRESOLVED: <base>`, `NO-PRIOR: <path>`, `CONFLICT: … <path>`). The skill's
action is the same in all three — ask my human partner for the range — but the
question it should ask differs, and the operator gets nothing to distinguish
them. KD-2's table does print it bare, so this is a note on the design as
landed rather than a deviation.

### 8. A second positional argument silently discards the first

`scripts/check_line_limits.sh:56-59`: the `*)` arm assigns `ROOT="$1"`
unconditionally, so the last positional wins with no diagnostic. Probed
(Probes §8): `check_line_limits.sh "$L/a" "$L/b"` — where `$L/a` holds a
401-line `docs/notes.md` and `$L/b` is clean — exits **0** with no output.
The overage in the tree the caller named first is never reported. Usage at
`:4` is `[ROOT]`, singular; a second positional should be
`echo "check_line_limits: unexpected argument: $1" >&2; exit 2`, consistent
with the `-*)` arm two lines above.

### 9. A file whose last line is unterminated is undercounted by one

`wc -l` counts newlines, not lines. Probed (Probes §8): a file of 401 lines
whose last line has no terminating newline exits 0 against cap 400.
`tests/line_limits_helpers.py:17-26` documents the fixture's newline
termination but nothing pins the unterminated case. Low realism for markdown
(`rumdl fmt` terminates files), so Minor, and worth at most a comment stating
the residual bound rather than code.

### 10. The review-range suite is split five ways with no in-situ rationale

Item 1.2 (`outline.md:212`) names `tests/test_review_range.py`; KD-2
(`:104`) says the report-only shape is "pinned by `tests/test_review_range.py`".
That file does not exist — the suite landed as five modules plus
`tests/review_range_helpers.py` (155 + 41 + 74 + 65 + 26 + 131 = 492 lines).
A split was needed (a single module would have cleared 400), but five was
not, and none of the five says why it exists. The sibling split does:
`tests/test_line_limits_exit_codes.py:7` — "Split from
`tests/test_line_limits.py` to keep that module under its line cap". Adding
the same sentence to each review-range module, or collapsing to two, closes
it. The dangling `tests/test_review_range.py` reference in KD-2 and Item 1.2
is `.md` and belongs to the other reviewer.

### 11. Six landed tests fall outside the outline's closing enumeration

`outline.md:322-328` ("Final list revision (TDD audit)") states "the landed
suites carry seven tests the reviews added beyond the slice lists" and names
them. Counting the tree: 11 review-range test functions against 8 slices
plus 3 named extras — `test_one_hop_only_ignores_grandprior_mismatch`
(`tests/test_review_range_range.py:111`) is unaccounted. 16 line-limits test
functions against 8 slices plus 2 named extras —
`test_line_limits_allowlisted_file_shrunk_below_cap_is_silent`,
`test_line_limits_rejects_crlf_on_full_entry_line`,
`test_line_limits_rejects_crlf_on_two_field_entry_line` and both functions in
`tests/test_line_limits_exit_codes.py` are unaccounted. All six are sound
tests doing real work — `test_one_hop_only…` is the only thing pinning KD-2's
"One hop only" clause, and the CRLF pair is the only thing pinning
`scripts/check_line_limits.sh:82-85`. The defect is the stale enumeration,
not the tests; the `.md` fix is the other reviewer's.

## Conformance table

| id | status | evidence |
|---|---|---|
| KD-2 exit 0 `RANGE: <base>..HEAD` | covered | `edify-review-range.sh:120`, `:152`; `test_first_pass_emits_range`, `test_second_pass_matching_base_emits_range` |
| KD-2 exit 1 `CONFLICT: base <a> != <b> inherited from <path>` | covered | `:156-158`; `test_second_pass_recomputed_base_is_conflict` asserts the exact line |
| KD-2 exit 1 `NO-PROVENANCE:` | covered | `:88`, `:96`, `:161`; 4 test nodes. See Minor 7 |
| KD-2 exit 1 `UNRESOLVED: <base>` | covered | `:108`, `:115`; `test_unresolvable_base_reported` |
| KD-2 exit 1 `NO-PRIOR: <path>` | covered | `:138`, `:147`; `test_missing_prior_artifact_reported`, `test_prior_without_base_reported[base-absent|base-short]` |
| KD-2 "invoked by bare name, no shim, directly in `bin/`" | covered | file is `plugin/bin/edify-review-range.sh`, mode `0755`; `review_range_helpers.py:120-131` puts `plugin/bin` on `PATH` and execs `["edify-review-range.sh", …]` |
| KD-2 "locates the repository from the artifact's directory" | covered | `:77-83`; probed from CWD outside the repo, from repo root, and outside any repo (Probes §1, §7) |
| KD-2 "resolves every path against `git rev-parse --show-toplevel`" | covered | `:135` `prior="$root/$prior_path"`; `:114` and `:80` both `git -C` |
| KD-2 "base from the artifact text, never recomputed" | covered | no `git log`/`merge-base`/`HEAD` read anywhere; `review_range_helpers.py:39-57` seeds two commits so a `rev-parse HEAD` implementation cannot pass |
| KD-2 "one hop only" | covered | `:137-158` inspects only the immediate prior; `test_one_hop_only_ignores_grandprior_mismatch`. Not in the outline's enumeration (Minor 11) |
| KD-2 "any other exit → script failed, nothing on stdout" | covered | `:70`, `:74`, `:82` all exit 2 to stderr; probed for no-args, missing file, directory-as-artifact, non-repo (Probes §1, §7) |
| Item 1.2 slices 1–8 | covered | all eight named test functions present; slice 8's two halves at `test_wrapped_derived_from_with_spaced_path` and `test_first_pass_none_with_rationale_emits_range` |
| Item 1.2 "Tests in `tests/test_review_range.py`" | deviating | landed as five modules + a helper, no in-situ rationale (Minor 10) |
| KD-7 markdown cap picked from path (200 `SKILL.md`, 400 otherwise) | covered | `check_line_limits.sh:180-181`; `test_line_limits_fails_skill_hub_over_200` both halves; probed for `docs/SKILL.md` outside `plugin/skills` (Probes §5) |
| KD-7 `oversized-file: <path>: <n> lines > <cap>` | deviating | `:129` emits it on Linux; unguarded `wc -l` deviates on BSD (Major 1) |
| KD-7 "the Python loop adopts the same line" | covered, untested | `:162-169` → `check_cap`; probed correct (Probes §8); no test (Major 2) |
| KD-7 allowlist is a sidecar beside the script | covered | `:34`, `:63-65`; `scripts/check_line_limits.allow` present, 21 lines |
| KD-7 allowlist overridable by argument for tests | covered | `:40-51`; `line_limits_helpers.py:33-40` |
| KD-7 entry records measured count + retiring job or "no job yet" | covered | all 7 entries carry a note; every ceiling equals the file's measured count today (Probes §9) |
| KD-7 "reported but does not fail unless it exceeds its ceiling" | covered | `:128-133`; `test_line_limits_reports_allowlisted_without_failing` asserts exit 0 **and** the line present |
| KD-7 "the ceiling only ratchets down" | covered as doc | `:25-28` and `check_line_limits.allow:8-12` state it; it is a human protocol, not mechanised — correctly not faked in code |
| Item 1.10 slices 1–8 | covered | all eight named test functions present; slice 8 lands as exit 2 with the vacuous assertion dropped, as the revision says |
| Item 1.10 exit contract `0/1/2` | covered | `:30`; `tests/test_line_limits_exit_codes.py` pins 2-outranks-1 at the only two sites where they can co-occur |
| KD-8 scope `plugin/`, `docs/`, root `*.md`, minus `docs/superpowers/{plans,specs}/` | covered | `:173-189`; `test_line_limits_skips_frozen_docs` (both dirs, separate trees) and `test_line_limits_checks_living_superpowers_docs` |
| Item 1.11 "delete the dead `agents/decisions` loop and its `2>/dev/null`" | covered | no `2>/dev/null` remains in the file; tree-wide sweep found the only shell `2>/dev/null` sites in `scripts/release.sh:54,63` (out of partition) |
| Item 1.10 test-file inventory | deviating | `tests/line_limits_helpers.py` and `tests/test_line_limits_exit_codes.py` are not named by the outline (Minor 11) |

## Probes run

1. **Dogfood against the tree's real artifacts.** `for f in plans/*/outline.md
   plans/*/design.md; do edify-review-range.sh "$f"; done` →
   `design-routing-and-provenance` `[0] RANGE: 926e372d…..HEAD`,
   `provenance-reach-and-sweep` `[0] RANGE: 926e372d…`,
   `provenance-enforcement-and-routing` `[0] RANGE: 926e372d…` (the real
   inherited compare, prior = `provenance-reach-and-sweep/outline.md`, runs
   and matches); `build-skill`, `pipeline-simplification`,
   `skill-reviews/design.md` `[1] NO-PROVENANCE:` (no section).

2. **Review-range edge fixtures** (throwaway repo under `$TMPDIR`, two
   commits): CRLF artifact → `[1] UNRESOLVED: <sha that resolves>` (Minor 4);
   `` `none` `` backticked → `[1] NO-PROVENANCE:` (Minor 6); uppercase 40-hex
   base, first pass → `[0] RANGE:` (git normalises); prior uppercase vs this
   lowercase → `[1] CONFLICT: … != 2083DA05… ` (Minor 5);
   `## Provenance Section` heading → `[0] RANGE:` (prefix match, benign);
   artifact under `plans/my job/` → `[0] RANGE:`; relative path from repo CWD
   → `[0] RANGE:`.

3. **Review-range failure arguments.** No args → `[2] Usage:…`; nonexistent
   path → `[2] … no such artifact:`; directory as artifact → `[2] … no such
   artifact:`; artifact outside any git repo → `[2]` with git's own `fatal:
   not a git repository` reaching stderr unredirected.

4. **`set -e` + `A && return` probe.**
   `bash -c 'set -euo pipefail; f(){ [[ -z "$1" ]] && return 0; printf …; };
   v=$(f hello); echo survived'` → prints `[got:hello]` then `survived`. The
   pattern at `edify-review-range.sh:60`, `check_line_limits.sh:78` and `:181`
   does not abort under `set -e`. Not a defect.

5. **Line-limits edge fixtures.** ROOT containing a space → `[1]
   oversized-file: docs/notes.md: 401 lines > 400`; `--allowlist` after ROOT
   → honoured; `--allowlist` naming a directory → `[2] no such file`;
   nonexistent ROOT → `[2]` via `cd`'s own diagnostic; symlinked over-cap
   `.md` → `[0]`, skipped (`-type f` excludes symlinks — the only symlink in
   scope is `plugin/.claude/skills`, a directory, so no live impact);
   `docs/SKILL.md` at 201 lines → `[1] … > 200`; ceiling field `401 ` with a
   trailing space → `[2] ceiling is not an integer`; allowlist entry written
   `./docs/notes.md` → not matched, `[1]` (exact matching, as documented).

6. **Mutation — basename allowlist matching.** Replaced
   `check_line_limits.sh:111` with
   `[ "$(basename "${ALLOWLIST_PATHS[$i]}")" = "$(basename "$1")" ]`;
   `.venv/bin/python -m pytest tests/test_line_limits.py --junitxml` → 12/14,
   failing `test_line_limits_fails_skill_hub_over_200` and
   `test_line_limits_matches_allowlist_paths_exactly`. The second is the
   intended red (the test's own docstring predicts it); the first is Major 3's
   proof. `git checkout -- scripts/check_line_limits.sh`; `git diff --stat`
   clean.

7. **Mutation — drop the backtick-quoted `superseding` regex.** Reduced
   `edify-review-range.sh:132-133` to the bare alternative alone;
   `pytest tests/test_review_range_range.py --junitxml` → 3/6, failing exactly
   `test_second_pass_matching_base_emits_range`,
   `test_wrapped_derived_from_with_spaced_path`,
   `test_one_hop_only_ignores_grandprior_mismatch`; the three `none`-path
   tests stayed green. The reds are specific to the mutated branch.
   `git checkout -- plugin/bin/edify-review-range.sh`; tree clean.

   Follow-on probes with the file restored: bare (unbackticked) `superseding
   plans/prior/outline.md` → `[0] RANGE:`; the same plus later backticks in a
   trailing rationale → `[0] RANGE:` (no cross-contamination, the quoted
   regex requires the backtick immediately after `superseding`);
   `superseding` with nothing after it → `[1] NO-PROVENANCE:`; `Base:` value
   on a continuation line → `[0] RANGE:` (the awk join works); prior path
   `../../../etc/hostname` and `/etc/hostname` → `[1] NO-PRIOR:` each.

8. **Line-limits behaviour probes.** 401-line `.py` under `src/pkg/` and
   `tests/` → `[1]` with two `oversized-file:` lines (Major 2's behaviour
   check); the same with `--allowlist` naming `src/pkg/big.py<TAB>401` → that
   file no longer drives the failure; two positional ROOTs `a b` where `a`
   holds a 401-line file → `[0]`, silent (Minor 8); 401-line file with no
   trailing newline → `[0]` (Minor 9).

9. **Allowlist ratchet integrity.** Read each entry and compared against
   `wc -l` of the named file: all 7 match exactly (403/682/460/450/218/277/354).
   `bash scripts/check_line_limits.sh` on the real tree → exit 0 with 7
   `oversized-file:` lines, which is KD-7's "reported but does not fail".

10. **Whole-tree form sweeps** (`rg -n -U`, excluding `plans/`, `memory/`):
    `2>\s*/dev/null` in shell → `scripts/release.sh:54,63` only (out of
    partition); neither script under review has one.
    `\|\|\s*true` in shell → `plugin/bin/edify-review-range.sh:92,93,143`
    (all three `grep` no-match, the sanctioned "non-zero encodes a result"
    case), `plugin/bin/triage-feedback.sh:44`, `scripts/release.sh:95` (out of
    partition). `for X in $(…)` → zero hits tree-wide. `find` without
    `-print0` where paths are consumed → zero hits; the two
    `triage-feedback.sh` sites pipe to `wc -l` and consume no path.
    `$(basename …)` / `$(dirname …)` unquoted → zero hits. `wc -l` → 3 shell
    sites, 2 guarded with `tr -d ' '`, 1 unguarded (Major 1).

11. **Static checks.** `shellcheck -S style` on both scripts → exit 0, no
    findings. `shfmt` is not installed on this box, so formatting was not
    checked. Exec bits: both scripts `0755`, `check_line_limits.allow` `0644`.

## Clean

Checks run that found nothing to report:

- **Whitespace safety, `edify-review-range.sh`.** Every expansion quoted;
  `dirname --` and `grep --` both use the `--` terminator; the prior path is
  captured through a backtick-delimited regex specifically so spaces survive,
  proven load-bearing by the mutation in Probes §7 and exercised end-to-end by
  `test_wrapped_derived_from_with_spaced_path` (`plans/my job/`).
- **Whitespace safety, `check_line_limits.sh`.** `find … -print0` into a
  spool file, `while IFS= read -r -d ''` at all three consumption sites
  (`:166`, `:176`, `:187`); allowlist parsed with `IFS=$'\t' read -r`, so a
  spaced path stays whole — `test_line_limits_allowlists_a_spaced_path` and
  `test_line_limits_handles_spaced_path` both assert the intact path, and I
  ran a spaced ROOT as well (Probes §5).
- **Error signalling, exit-code discipline.** Every failure-to-run path exits
  2 rather than letting `set -e` surface as 1 (which would read as an
  overage): `mktemp` `:156`, `wc -l` `:124`, `find` `:146`, `cd` `:100`,
  `--allowlist` arity `:44` (with the `shift 2` hazard documented in situ),
  unknown option `:52`, malformed and CRLF entries `:82-89`. Each carries an
  in-situ comment saying *why* 2 and not 1. `find`'s and `git`'s own
  diagnostics pass through to stderr unredirected, with a comment at
  `edify-review-range.sh:78` explaining that capturing git's stderr would
  silence it.
- **The three `|| true`s are the sanctioned exception**, not suppression:
  each is `grep -m1` where no-match encodes "field absent", and the absent
  case is handled explicitly on the next line (`:95`, `:146`).
- **bash 3.2 / BSD portability, everything except `wc`.** No `declare -A`
  (linear scan at `:107-116`, reason stated), no `mapfile -d ''` (reason
  stated), `mktemp` with an explicit template (reason stated),
  `awk '[ \t]'` rather than `[[:space:]]` (reason stated at
  `edify-review-range.sh:32-34`), `sed -E` and `grep -m1` both BSD and GNU,
  `find -maxdepth` first among the expressions at `:186`.
- **Idempotency.** Both scripts are pure readers — no writes outside the
  `mktemp` spool, which is removed by `trap … EXIT` at `:160`. Repeated runs
  against the real tree gave identical output and exit 0.
- **Modularity and testability.** `provenance_of` / `base_value_of` are
  reused unchanged for the prior artifact (`:142-144`), which is what makes
  the wrapped-value and trailing-rationale handling apply to both sides
  without duplication. `check_line_limits.sh` takes `[ROOT]` and
  `[--allowlist FILE]` precisely so the suite never touches the checkout —
  honoured everywhere except the eight default-allowlist calls in Major 3.
- **Test specificity, proven by mutation, not read.** Two mutations, both
  restored: the allowlist matcher (Probes §6) and the `superseding` regex
  (Probes §7). In each case the reds were confined to the tests whose stated
  contract the mutation broke, and the unrelated tests stayed green.
- **Tests verify behaviour, not implementation.** Every test runs the script
  as a subprocess and asserts on exit code, stdout and stderr only; nothing
  reaches inside. `review_range_helpers.py:39-57` builds two commits
  specifically so a `git rev-parse HEAD` implementation cannot pass, and
  `line_limits_helpers.py:65` puts a comment line and a blank line at the top
  of every allowlist fixture so a naive reader is caught.
- **Test assertions are exact where they should be.** `result.stdout ==
  "<line>\n"` or `.splitlines() == [...]` at every verdict site, so an extra
  or missing line fails — not `in`. Where exactness would have been
  unjustified the test says so and asserts the weaker thing with a reason
  (`test_line_limits_fails_when_find_cannot_walk:224-228`).
- **The two CRLF tests strip the allowlist path out of stderr before matching
  on wording** (`test_line_limits.py:266-271`, `:299-303`), because pytest's
  `tmp_path` name contains "crlf" and would otherwise satisfy the assertion
  on the path rather than the diagnostic. That is a real trap, caught.
- **`tests/test_line_limits_exit_codes.py:10-20`** justifies its fixture
  layout (`plugin` walked before `docs`) and enumerates why the other six
  exit-2 sites cannot co-occur with an already-set `EXIT_CODE=1`. The
  enumeration is correct against the script as landed.
- **Line caps.** Largest artifact in the partition is
  `tests/test_line_limits.py` at 323 lines; `check_line_limits.sh` 191,
  `edify-review-range.sh` 162. All under 400. `SKILL.md` files are the other
  reviewer's.
- **No excess.** Nothing in either script or any test module is unreferenced
  ceremony; the one unused-looking variable (`superseding_quoted`) is used at
  `:132` and only appeared unused under my mutation.

## Tree state

I mutated `scripts/check_line_limits.sh` and `plugin/bin/edify-review-range.sh`
and restored both with `git checkout --`; `git diff --stat` over `scripts/`,
`plugin/bin/` and `tests/` is empty. `git status --porcelain` at the end of
this review is **not** clean, but none of it is mine — modified `CLAUDE.md`,
`docs/changelog.md`, `docs/references/agent-instructions.md`,
`plugin/skills/proof/SKILL.md`, `plugin/skills/proof/references/item-review.md`,
and untracked `.claude/autodrive.exited`, `.claude/launch.json`,
`.claude/loop.md`, `.claude/output-styles`, `.claude/routines`,
`.claude/workflows`, `docs/changelog/`, `plans/changelog-split/`,
`plans/proof-verdict-prompt/`. Concurrent agents in this session are writing
those; my human partner decides what is ignorable.
