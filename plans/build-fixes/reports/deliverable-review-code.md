# Deliverable Review — code

Scope: `plugin/skills/build/scripts/changed-files.sh`,
`plugin/skills/build/scripts/exempt-paths.sh`,
`plugin/skills/build/scripts/verify-step.sh`, `plugin/bin/triage-feedback.sh`,
at HEAD, over `d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`. Baseline:
`plans/build-fixes/outline.md` (KD-1..KD-8, Items 1.1–1.4), with D-88..D-94 in
`docs/references/build-run-state.md` as the living record. Probes ran on git
2.47.3 and bash 5.2.37 in throwaway repos under `$TMPDIR/dr-probe`, with
`GIT_CONFIG_GLOBAL=GIT_CONFIG_SYSTEM=/dev/null`. None was run on macOS.

## Critical

### C1 — `triage-feedback.sh`, `reports_count` and the verdict block: every Simple `/build` run is logged `underclassified`

- **Axes:** functional correctness, vacuity
- **Severity:** Critical (incorrect behaviour, persisted to
  `plans/reports/triage-feedback-log.md`)

`reports_count` counts every file in `plans/<job>/reports/` except planning and
review-gate reports, so `item-*.md` counts. This job made an item report
universal. D-88 says "every item leaves a report", and Item 2.1 has §4.1 direct
execution write `item-N-M.md` too. At the base, §4.1 wrote no report. So after
any item, `reports_count >= 1`, and the consequences are:

- Simple → `underclassified` on every `/build` run, whether or not the evidence
  supports it.
- The Complex → `overclassified` branch needs `reports_count -eq 0` and can no
  longer be reached. It is dead code.

build-defects Q-2 recorded this for *delegated* Simple jobs and left it out of
scope. build-fixes KD-1 / Item 2.1 widened it to every Simple job, and no item
revisited the script. `tests/test_triage_feedback.py::test_simple_with_review_reports_matches`
pins the current behaviour: it asserts that a single `item-*` report flips
Simple to `underclassified`.

Evidence: a Simple job with one §4.1 item editing one text file, its
`item-1-1.md` and a `review-code.md`:

```
$ bash changed-files.sh j          # BASE: c27696e…  /  doc.txt
$ bash triage-feedback.sh j c27696e…
- Files changed: 3
- Reports: 1
- Behavioral code: no
## Verdict
underclassified
```

## Major

### M1 — `triage-feedback.sh`, `files_changed` and `committed_diff`: the evidence includes the job's own record and the exempt paths

- **Axes:** functional correctness, conformance to KD-6's definition of the
  run's changes
- **Severity:** Major

KD-6 / D-90 define the run's changes as the `<base> HEAD` diff minus
`plans/<job>/` and the exempt paths. Triage takes only `changed-files.sh`'s
`BASE:` and runs raw `git diff <base> HEAD` for two values:

- **Files changed** counts the run's reports, `runbook.md` revisions and any
  committed `inbox/`, `.claude/handoff-*` or `memory` paths.
- **Behavioral code** greps the reports' prose.

This conforms to the letter of D-90, which says triage's "two diffs take the
same `<base> HEAD` form", so the fix runs through the design. The probe above
shows the effect: 3 files changed against a changed-files list of 1. Measured on
this job's range:

- 152 files in `git diff --name-only d444630c..HEAD`, 110 of them under
  `plans/build-fixes` or `plans/build-defects`.
- The behavioural-code regex matches 4 `+` lines under `plans/`, all of them
  prose: `+class with an explicit whitelist…`, `+module over the line cap…`,
  `+  def counted.`, `+module was split three ways…`.

Fixing C1 does not fix this. With C1 fixed, a Simple job whose reports happen
to wrap a line onto `module `, `class ` or `def ` still reads as behavioural.

## Minor

### m1 — `changed-files.sh`, top level `exec 2>&1`: git diagnostics enter the data stream

- **Axes:** robustness, error signaling

On exit 0, a git warning prints among the `BASE:` line and the paths, where a
consumer reads it as a path. On exit 2, git's `fatal:` line comes before
`ERROR:`, so the first stdout line is not `ERROR:` as the Item 1.2 interface
implies. Exit codes still discriminate correctly.

Evidence:

```
$ git update-ref refs/tags/HEAD HEAD; bash changed-files.sh "my job"
warning: refname 'HEAD' is ambiguous.
BASE: ea9164c…
warning: refname 'HEAD' is ambiguous.
a b.txt
…  exit=0
$ (unborn repo) bash changed-files.sh j
fatal: your current branch 'main' does not have any commits yet
ERROR: git log failed   exit=2
```

### m2 — `changed-files.sh`, base and diff: merge-shaped history

- **Axes:** robustness (git edge cases)

1. Commits that are not the run's, made after the base, are listed as the run's
   work. This covers `main` merged into the job branch, and another session
   committing on the same checked-out branch. Probe: after
   `git merge --no-ff main` into the job branch, `unrelated-main.txt` is listed.
   This follows from KD-1/KD-6 (a two-point tree diff from a commit base), not
   from a coding slip. How often it happens is unmeasured.
2. A report added only in a merge commit (conflict resolution) is invisible: a
   path-limited `git log` does not diff merges by default. Probe: `NO-BASE:`,
   exit 1. This is unlikely in practice.

### m3 — `changed-files.sh`, unborn HEAD: exit 2 where the interface's exit-1 condition literally holds

- **Axes:** conformance (interface wording)

Item 1.2 says "no committed item report → exit 1 `NO-BASE:`". An unborn repo
has none, yet exits 2 with `ERROR: git log failed`. `test_no_item_report_exits_1`
pins exit 2 deliberately, so the code and the test agree and only the
interface text is ambiguous. `/build` cannot reach this state, because the entry
gate needs a commit.

### m4 — `triage-feedback.sh`, both `git diff "$baseline_commit" HEAD` calls: no `--`

- **Axes:** robustness

If the work tree holds a file named `HEAD`, both calls fail. `changed-files.sh`
guards the same form with `--`, so the two scripts are inconsistent.

Evidence:

```
fatal: ambiguous argument 'HEAD': both revision and filename   exit=128
```

The failure is surfaced, not swallowed.

### m5 — `triage-feedback.sh`, the behavioural-code test: a here-string inside `if`

- **Axes:** error signaling

`grep -qE … <<< "$committed_diff"` sits in an `if`. Two failures would both
read as "no":

- the here-string's temp-file creation fails;
- grep exits 2.

`verify-step.sh`'s own comment rejects here-strings for exactly this reason
("a failure to create it also exits 1"). This is not verified by probe; it is
reasoned from bash's here-string implementation as that comment describes it.

### m6 — `triage-feedback.sh`, `classification=$(… | xargs || true)`: the error is masked (pre-existing, on a line edited in range)

- **Axes:** error signaling, robustness

An apostrophe in the classification line makes `xargs` fail ("unmatched single
quote"). The parsed value then depends on how far that `xargs` got: GNU produced
a value that still matched `Simple`. BSD behaviour is unverified. The stderr
message does surface.

### m7 — `triage-feedback.sh`, the log append: not idempotent

- **Axes:** idempotency

Each run appends a row. Two paths in the range now re-run triage on the same
job:

- `finishing.md` §2's new "rerun §2" after the missing-corrector warning;
- KD-1's "a finished job re-invoked reads as resumed … goes to finishing".

Probe: two runs give two identical rows,
`| 2026-10-04 | j | Simple | 3 | 1 | no | underclassified |`.

### m8 — script comments cite plan-outline KD numbers from two different outlines

- **Axes:** clarity, modularity of references

In `triage-feedback.sh`:

- "(KD-3)" on the review-report exclusion is build-defects KD-3.
- "(KD-6)" two paragraphs later is build-fixes KD-6, and build-fixes KD-3 means
  dirt.

In `verify-step.sh`, "KD-6" is build-fixes and "(KD-7)" is build-defects. The
scripts ship in the plugin, and in other repos neither outline exists. The
durable IDs are D-88..D-94 (D-91 for the exemption, D-90 for the list).

## Checked and found sound

- **Item 1.2 interface:**
  - `BASE: <sha>` then one path per line.
  - Exit 1 `NO-BASE:` with no committed `item-*` report.
  - Exit 2 `ERROR:` on usage errors: `j*`, `a/b`, `..`, empty, `x[1]`, `x\y`,
    `x?`, a bare `--phase`, `--phase` in first position.
  - Exit 2 on a root-commit report, outside a repo, and in shallow clones whose
    graft hides the parent. All fail closed.
- **KD-1 base:** correct for linear history, with a pre-run planning report,
  and with an item report on a side branch merged `--no-ff`. The `:(glob)`
  pathspec keeps `item-*` and `phase-*-corrector.md` to a single component.
  Probe: a nested `reports/phase-1/old-corrector.md` is ignored.
- **KD-2 `--phase`:**
  - Without a boundary it gives the run base.
  - It gives the latest boundary commit, including under committer-date skew on
    linear history.
  - It ignores a boundary committed before the run base.
  - It applies the same filters.
  - Detecting a skipped P-1 boundary belongs to `phase-boundary.md`, per D-89,
    which the script's fallback matches.
- **KD-6 filters:** `plans/<job>/` is matched as a literal prefix through a
  quoted `case` pattern. Job names with `. ( ) + $ : -` and spaces each resolve
  their own base and exclude only their own directory. Exempt paths are matched
  per path inside the NUL-delimited loop, with paths read by `read -r -d ''`.
  Spaces and non-ASCII names are handled; a name holding a newline splits into
  two lines, the residual bound the comment states. `--no-renames` lists both
  sides of a rename. The script works from a subdirectory.
- **`exempt-paths.sh`:** a single source of the alternation, mode 100644. Both
  callers validate that it loaded and exit 2, never 1, when it did not.
- **`verify-step.sh`, unchanged verdicts with the shared pattern:**
  - Spaced, non-ASCII and quoted exempt paths are CLEAN.
  - A non-`.md` file in `inbox/` is DIRTY.
  - A staged rename inside `inbox/` is DIRTY, per the KD-7 addendum.
  - A `memory` submodule with untracked content is CLEAN.
  - `core.quotePath` is forced on.
  - A missing `just` exits 2.
  - A symlinked invocation exits 2, as documented.
- **`triage-feedback.sh` changes in range:** the Item 1.3 `<base> HEAD` form,
  `--no-color --no-ext-diff`, the capture before grep so a `git diff` failure
  is no longer read as "no", a newline-safe report count, and POSIX
  `[[:space:]]` in place of `\s`.
- **Lint:** `shellcheck -x` at default severity is clean on all four files.
  `--enable=all` adds only SC2250, SC2249 and SC2312 style and info notes.
- **bash 3.2:** `$'\n'` in a pattern, `read -d ''`, and `[[ =~ $var ]]` are
  within 3.2. This was not executed on 3.2 or macOS.
