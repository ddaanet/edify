# Report digest — summary, 2026-09-23

This summary merges four digests of what the 2026-09-21 and 2026-09-22 passes
left open. Each item was checked against the tree at `0b4c46f8`. The part files
carry the evidence for every entry:

- `remaining-sweep.md` — `plans/remaining-sweep/reports/`
- `skill-reviews.md` — `plans/skill-reviews/reports/`
- `implementation-reports.md` — review-fixes, allowlist-ownership,
  proof-verdict-prompt, release-decision-record
- `open-items-and-provenance.md` — open-items-sweep, and the
  provenance-enforcement-and-routing deliverable review

| Part | In frame | Missing | Resolved since | Unclear |
|---|---|---|---|---|
| remaining-sweep | 11 | 9 | 22 | 2 |
| skill-reviews | 31 | 28 | 3 | 1 → 0 |
| implementation reports | 13 | 3 | 16 | 3 |
| open-items + provenance | 6 | 8 | 17 | 0 |

Both patches under `plans/open-items-sweep/reports/` are applied.

## Frame corrections

- **R3, second sentence, is stale.** The 0.3.0 release has run. The `edify`
  marketplace entry now matches `plugin.json`'s description. Only the README
  half remains.
- **R2 omits `formalize` 2.** `formalize/SKILL.md:59` runs a bare
  `edify check`, which works only in the dev checkout. The fix waits on D-12's
  open `${CLAUDE_PLUGIN_DATA}` probe.
- **R8 omits the awk `\r` case.** The CRLF fix in `edify-review-range.sh` was
  probed on mawk only. The same macOS run exercises it through
  `test_crlf_artifact_emits_range`.
- **R4 undercounts.** It names 27 open-design findings and 3 disputed ones.
  The 21 migrated `build/` defects are neither, so the frame carries none of
  them (see below).
- **Two "F-6"s.** The deliverable review's F-6 (the review range is unbounded
  at `..HEAD`) is a different item from brief-triage F-6. The frame carries
  only the latter.

## Unclear → settled

- **`allowed-tools` grants tools; it does not restrict them.**
  `plugin-craft:skill-authoring` settles this, verified against the CC 2.1.250
  docs. So the blocking half of runbook M7 is wrong. Review C2's mechanism note
  holds: a tool left out of the list costs a permission prompt, not a block.
  Both findings' mechanical halves were already applied, so nothing remains
  open from this item.

## Rulings

- **Ratified 2026-09-24** by my human partner: the allowlist-ownership Q1–Q3
  and release-decision-record Q1–Q5 defaults below, as shipped in `5f860e07`.
  Nothing to reverse.
- **Ruled 2026-09-24:** provenance DR F-6 stays as `0b4c46f8` records it — the
  review range is `Base..HEAD`, no end bound. The proof-verdict-prompt outline's
  skipped `/proof` is accepted.

## Rulings taken (were: needs my human partner's ruling)

- **allowlist-ownership Q1–Q3 were shipped on defaults in `5f860e07`** —
  ratified, see above:
  - `/build`'s References recap and `/requirements`' Key Principles deleted;
  - one extra Read added;
  - requirements m10 folded in.
- **release-decision-record Q1–Q5 were shipped on defaults in `5f860e07`** —
  ratified, see above:
  - the 2026-07-17 changelog entry left as it was;
  - the publishing non-goal deleted;
  - D-87 in "Do not re-litigate";
  - three hub edits;
  - D-87's numbering.
- **Provenance DR F-6: the review range `..HEAD` has no end bound.** Commits
  made after the job fall inside its review. The report offers three options:
  leave it, add an optional end ref, or have `/build` record the terminal
  commit. `0b4c46f8` records "the review range stays Base..HEAD", which may
  already be this ruling — confirm.
- **The proof-verdict-prompt outline never went through `/proof`.** The change
  shipped anyway. Either run `/proof` retroactively or accept the skip.

## Missing from frame — work items

### `build/` defects migrated from the retired inline/orchestrate skills

These are 21 items. Fix text is in `verify-inline.md` and
`verify-orchestrate.md`, and `skill-reviews.md` §Missing lists them with
current line numbers. They fall into five clusters:

- **Changed-files reference point** (orchestrate C1 and M8; inline M2, m10 and
  m12). The phase-boundary halt diffs an empty working tree after committed
  dispatches, so it fires on well-behaved runs. This is the most severe
  cluster.
- **Dispatch contracts** (inline M1, m15, m16 first half, m6, m11). Two
  report-path rules and two return contracts contradict each other.
- **Triage script** (inline M3). `reports_count` misclassifies a reviewed
  Simple job.
- **Tool availability** (orchestrate M1, m7, M7; inline m2):
  - `TaskOutput` does not resolve;
  - `TaskStop` is presented as procedure;
  - `git clean -fd` is unconfirmed;
  - an `&&` guards nothing.
- **`build/SKILL.md` body** (orchestrate M4, C2, m3, m4, m5; inline m9).

### Other skill-review leftovers

- `apply-review.md` accepted four items without fixing them:
  - runbook §1 substeps render as paragraphs;
  - §-citations point at bold labels;
  - `write-design.md` §C.1 loses its own recall triggers;
  - two `not recorded` rows in the example report.
- `CLAUDE.md:248` still shows the non-runnable pipeline
  `edify list | extract <prefix> | collect`.
- `runbook/SKILL.md:71` calls `Skill(edify:recall)` a second time. This is the
  same pattern as requirements m3, which was fixed.
- Deliverable-review C3 is carried only generically, by R4. The skill disclaims
  queueing follow-up work, against D-58 and D-60.
- The `argument-hint` half of inline m16 is disputed.

### Scripts and gates

- **`edify-review-range.sh`:**
  - three different causes share one bare `NO-PROVENANCE:`;
  - `UNRESOLVED:` does not say which artifact's base failed;
  - `none,` followed by a comma yields `NO-PROVENANCE:`.
- **`check_design_links.sh`:**
  - a temp file leaks when the second `mktemp` fails (`:76-80`);
  - violation order depends on the filesystem (`:112`).
- **`tests/line_limits_helpers.py:97-100`:** combining `second_root` with
  `omit_root=True` tests the wrong root. No caller does this today.
- **D-86:** no mechanical check that a report commit carries the work it
  reports.
- **Mutate-and-run script** (brief C-x, "script" half): the triage recorded no
  disposition for it. Only the M7 guard half was routed.
- **`bash_prolog` duplication:** the root `justfile` still duplicates it.
  A consumer that overrides the prolog without defining `run-project-checks`
  hits "command not found".
- **Two lines over 80 columns** that rumdl cannot reflow:
  `outline-corrector.md:61` and `design-corrector.md:105`. They ride with
  defect 21.

### Docs and records

- D-52, D-53 and D-54 placement: move them from `quality-gates.md` to
  `agent-instructions.md`, or leave them.
- `design/SKILL.md` gained `Edit` in `allowed-tools` with no recorded
  rationale.
- Two tests and the outline attribute "exit 2 outranks exit 1" to KD-7, but
  KD-7 does not state it.
- Nothing records why the 2026-08-04 publication reversal happened. The report
  names the gap but no action.
- Nit: `plans/review-fixes/reports/red.md:193` says 39 lines where the file
  has 38.

### Deliberately dropped or not work

- The just-recipe test harness was dropped from the frame in `a3697f15`.
- The "multiple rounds" claim for deliverable reviews is an evidence-scope
  limit. It already fed "the review range stays Base..HEAD".

## Unclear, left open

- **Brief A's `claude-plugin-dev` line citations** (another repo). Read-only
  checks could not show whether they were fixed or had moved.
- **Toolkit `release.just` against `release.sh`** on an unset
  `MARKETPLACE_DIR` (another repo). D-87 does not need the answer.
- **No review found for `formalize/SKILL.md` and `grounding-criteria.md`.**
  Nothing shows they were reviewed after their concurrent edits, and
  `5f860e07` edited them again.
