# Item 2.3 — `plugin/skills/build/references/phase-boundary.md`

Requirements: Major 2, m1, m3.

## Changes per bullet

- **Base resolution.** The `git diff --name-only <phase base> HEAD` block, the
  `tmp/build-baseline` phase-1 base and the `git log --diff-filter=A` P>1 query
  are gone. A new §Base and changed files opens with
  `plugin/skills/build/scripts/changed-files.sh <job> --phase`, run at every
  boundary; its `BASE:` is the phase base. The file then states KD-2's landed
  query, `git log -1 --format=%H <run base>..HEAD -- plans/<job>/reports/phase-<P>-corrector.md`,
  with `<run base>` from `changed-files.sh <job>` without `--phase`, as the rule
  `--phase` implements. It keeps KD-2's three consequences of the query (range
  excludes an earlier run, no `--diff-filter=A`, `-1`) and keys on the path,
  never the subject (KD-8). This is the query `escalation.md` §Resuming points
  at ("Phase P's boundary has landed as `references/phase-boundary.md`
  resolves it").
- **Changed-files list (m1).** The list is the script's output after `BASE:`:
  committed diff from the phase base to `HEAD`, minus the exempt paths and
  `plans/<job>/` (KD-6). "So the paths `verify-step.sh` exempts stay out" is
  replaced: the `HEAD` form keeps uncommitted dirt out, but not exempt paths a
  `/handoff` or memory-pointer commit lands in the run, which the script drops.
  Exit 1 (`NO-BASE:`) or exit 2 (`ERROR:`) → STOP, with KD-2's "never
  substitute an empty base" and its `git diff --name-only HEAD` reason.
- **UNFIXABLE and ordering (m3).** "UNFIXABLE → STOP and escalate" became a
  check by `review-requirement.md` §UNFIXABLE Detection Protocol: one failing
  validation goes back to `phase-P-corrector` by `SendMessage` with the
  protocol's reclassification guidance; one that holds → STOP and escalate with
  the report path. The fix-and-resume sentence is kept. The ambiguous
  "Otherwise commit and continue" is replaced by a §Commit section that opens
  "Commit once no validated UNFIXABLE stands: none was raised, or the resumed
  corrector has reviewed the fix", so the commit is ordered after the resume.
- **Subject (KD-8).** The commit's subject is `<type>: <job> Phase P boundary`.
  The commit also carries any still-uncommitted fix applied for a decision, as
  well as the corrector's own fixes.

## Judgement calls for review

- **Where KD-2's STOP still applies.** KD-2: "An empty result during a live run
  means the boundary commit was skipped. → STOP." `--phase` falls back to the
  run base on an empty match, so it cannot detect the skip by itself. Decision:
  at every boundary P>1, before using `--phase`'s base, run KD-2's landed query
  for phase P-1. Empty → STOP: P-1's boundary commit was skipped, and using
  `--phase`'s fallback would widen phase P's review over phase P-1's work.
  Reasons:
  - A check on "`BASE:` equals the run base" (the example in the dispatch)
    misses one case: P-1's boundary skipped while P-2's landed. `--phase` then
    returns P-2's boundary commit, not the run base. KD-2's per-phase query
    catches both cases, and the file has to carry that query anyway for
    `escalation.md` §Resuming.
  - It applies on resume too, not only in a live run: the resume inventory
    (`escalation.md` §Resuming step 1) runs a missing boundary before the next
    phase's first item, so at boundary P>1 phase P-1 has always landed unless a
    commit was skipped.
  - At P=1 there is no earlier boundary, and `--phase`'s fallback to the run
    base is the correct base. No check.
  - Cost: one more `changed-files.sh <job>` call for the run base, and one
    `git log`, per boundary P>1.
- **Second STOP: the two bases disagree.** Where the P-1 query prints a hash
  other than `--phase`'s `BASE:`, the file STOPs too. KD-2 says P-1's hash is
  phase P's base; KD-6/Item 1.4 say the base is the latest commit touching any
  `phase-*-corrector.md`. They agree whenever boundaries commit in order. A
  mismatch means a later commit touched another phase's report, and neither
  definition is safe to pick. This rule is mine, not the outline's. Drop it if
  the reviewer finds it over-specified.
- **Command path form.** The bash block uses
  `plugin/skills/build/scripts/changed-files.sh`, the repo-root form that
  `SKILL.md` and `finishing.md` use for the scripts they run. The prose
  pointers keep this file's skill-base-relative `references/…` form. The
  path-form question belongs to the repo-relative-paths job (outline §Scope
  OUT).
- **Section headings.** The file had no headings. It now has three (§Base and
  changed files, §Review, §Commit), so the order — check, review, validate,
  commit — reads in the structure and `escalation.md`'s "as
  `references/phase-boundary.md` commits it" has a section to land on.
- "my human partner" is kept: it is this file's voice.

## Cross-references left for later items

- `../../fragments/review-requirement.md` §Execution Context, Changed files
  still says "the run's or phase's base as `phase-boundary.md` resolves it" with
  the working-tree `git diff --name-only <base>` form: Item 2.9 gives it
  `changed-files.sh`'s form.
- `review-requirement.md` §UNFIXABLE Detection Protocol step 4 says
  reclassification is a fresh delegation ("no continuation mechanism
  available"). This file resumes `phase-P-corrector` by `SendMessage`, as
  `finishing.md` and `dispatch-composition.md` do. Neither Item 2.9's bullets
  nor any other item's name this sentence. Flagged for the deliverable review
  or Item 2.9's executor.
- `plugin/README.md` lists the phase-boundary commit among `verify-step.sh`'s
  call sites: Item 2.11.
- KD-2 as a recorded decision in `docs/`: Item 2.14.

## Verification

- `just format`, then `just precommit` green (version consistency, cached
  tests, line limits — only the three allowlisted correctors reported — and
  design links).
- Self-review of the uncommitted diff against Item 2.3's four bullets, KD-2,
  KD-6 and KD-8, and against `escalation.md` §Resuming's two pointers into this
  file and `SKILL.md` §4.4/§4.5.
- 43 lines before, 79 after (`wc -l`, after `rumdl fmt`).
