# Item 3.3 — changelog: triage measures the review gate's set

Targets: `docs/changelog/2026-10-06-triage-measures-the-review-gates-set.md`
(new) and its line in `docs/changelog.md`. Requirements: C1, M1, M2.
`craft:design-doc-writing` loaded; the entry follows its rule that a dated
entry leads with the motivating fact, then the positive design, with no
deletion inventory.

## Date

`<date>` is the day the entry was written. The dispatch named 2026-10-05; the
clock had passed midnight by the time of writing (`date +%Y-%m-%d` printed
`2026-10-06`), so the file and index line carry 2026-10-06 per the item's own
rule. The file path is therefore
`docs/changelog/2026-10-06-triage-measures-the-review-gates-set.md`, not the
`2026-10-05-…` path the dispatch's target list spelled out.

## Edits

### New entry — three paragraphs

1. Motivating fact (C1, M1), from `plans/build-fixes/reports/deliverable-review.md`:
   D-90 recorded triage taking `BASE:` and running two raw `<base> HEAD` diffs,
   which counted `plans/<job>/` and the exempt paths (103 files, 69 under
   `plans/build-fixes/`, against 34 from `changed-files.sh` — the review's
   measurement); the behavioural grep matched report prose; the report count
   took the item reports, so every Simple run logged `underclassified` and the
   Complex `overclassified` branch was unreachable. The script conformed to
   D-90's letter, so the error was in the design record.
2. The design: `triage-feedback.sh <job>` takes no base, runs `changed-files.sh`
   and counts its list; behavioural code from those paths' diff only; the
   report count looks past the list minus the per-item and review reports. The
   rejected alternative (a second copy of the filters in triage) and L-2's
   unchanged columns are named.
3. M2: the rollback protocol reverted a committed failed fix with no decision,
   contradicting the 2026-10-03 entry; nothing reverts by default now,
   committed or not (D-92). Also names D-91's optional `sandbox-lies` and
   D-93's one wording.

"The report count took the item reports on disk with the rest" avoids "every
report": the old script excluded the name list and the review reports
(see `item-3-2.md` §Deviation).

### `docs/changelog.md`

Added as the first index line:

```markdown
- **2026-10-06** —
  [triage measures the review gate's set; a committed failed fix no longer reverts by default](changelog/2026-10-06-triage-measures-the-review-gates-set.md)
```

## Verification

- `just format` reflowed the entry; it is 30 lines.
- `just precommit`: Precommit OK — version consistency, tests cached (inputs
  unchanged), line limits, design links (94 decisions indexed, defined once,
  conclusions match, 9 nodes present). The three `oversized-file` lines are
  files this item does not touch.
