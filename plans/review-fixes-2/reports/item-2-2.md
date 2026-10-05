# Item 2.2 — finishing.md: landed checks, triage without a base, empty list

Target: `plugin/skills/build/references/finishing.md` (164 lines after
`just format`; was 135). Requirements: C1, M1, M4, m7, m15, m16.

## Edits

- **Opening paragraph** — "Reached once per job" became "Reached after the last
  item, in the session that completes it", since §1 now states that a
  re-invoked job or a run killed inside this file reaches the file again.
- **§1, new opening paragraph "Landed check first" (m7)** — the two
  `git log -1 --format=%H` commands from the outline's landed-gate decision:
  `<L>` is the last commit touching `:(glob)plans/<job>/reports/item-*`, and the
  gate has landed when `<L>..HEAD` touches
  `:(glob)plans/<job>/reports/review-*.md` (`review-skip.md` counts). A landed
  gate goes to §2. `<L>` is written in as the hash itself, and §3 reuses it. It
  cites D-89 for keying on the report path, never a subject. An empty `<L>` (the
  `NO-BASE:` fault) or a failing command → STOP.
- **§1 step 1 (M4, m16)** — `NO-BASE:` is a fault, not an empty run, because
  every run commits an item report, work with no `Item N.M` included, as Item
  1.1 (`/build` §1, D-88). Exit 0 with no path after `BASE:` → take `/build`
  §5's `review-skip.md` branch, saying the list came back empty, and go
  straight to the report commit, which carries it.
- **§2 (C1, M1)** — the command is `plugin/bin/triage-feedback.sh <job>`. The
  paragraph on writing `<base>` into the command as a hash is deleted. In its
  place: the script takes no base, runs `changed-files.sh <job>` itself and
  measures the set §1 reviewed (D-90). A non-zero exit (1 for usage; 2 for
  `ERROR:`, after `NO-BASE:`/`ERROR:` from `changed-files.sh` or on its own
  failure) writes no row and gives no verdict → STOP and report its output.
  "Read the script output" now begins "On exit 0".
- **§3 step 1 (m7, m15)** — the final review is skipped when
  `git log -1 --format=%H <L>..HEAD -- plans/<job>/reports/final-review.md`
  prints a hash. Before the closing commit, its report gets §1's structural
  proof: a Read, then UNFIXABLE validated by `review-requirement.md` §UNFIXABLE
  Detection Protocol, resuming `final-review` by `SendMessage` where the
  protocol resumes the corrector. STOP on each UNFIXABLE that holds, giving its
  path.
- **§3 step 2 (m7)** — the TDD audit is skipped in the same way when the query
  over `plans/<job>/reports/tdd-audit.md` prints a hash.
- **§3 step 3** — this one is a consequence of the skips, not in the item text.
  "each where it exists" / "where none of them exists" became "each where this
  pass changed it" / "where none changed". Once a stage has landed and been
  skipped, its report still exists, committed and unchanged. Under the old
  wording the closing commit would try to commit it anyway.

## Verification

- Probed the landed-check commands against this repo. For `build-fixes`
  (finished), the second command prints `2da5bbef…`, its review-gate commit. For
  `review-fixes-2` (in progress), it prints nothing and exits 0.
- Agreement checked against `build/SKILL.md` §1 (the Item 1.1 rule, D-88) and §5
  ("a review gate `finishing.md` §1 finds already landed is not re-run";
  `review-skip.md` carried by §1's report commit). Also checked against
  `triage-feedback.sh` as it stands: `Usage: triage-feedback.sh <job>` with exit
  1, and `ERROR:` with exit 2 after printing `changed-files.sh`'s output. And
  against `changed-files.sh`: `BASE:` then paths on exit 0, `NO-BASE:` exit 1,
  `ERROR:` exit 2.
- No "KD-N" appears in the file.

## Observations (not acted on, out of item scope)

- §2's "On match or no-classification with no warning → proceed silently" also
  covers the new `unrecognised classification: <label>` line (N-1). That line
  currently goes unsurfaced. Item 2.2's requirements do not include N-1, so the
  text is unchanged.
- The landed-check commands follow the outline's exact form, without
  `--no-show-signature`. `changed-files.sh` adds that flag so a user's
  `log.showSignature` cannot print lines ahead of the hash.
- Recall artifact skills (`shell-scripting:shell-gotchas`,
  `craft:test-discipline`, `craft:design-doc-writing`) are scoped to script,
  tdd and docs items. None applies to this prose item, so I did not load them.
  `plugin-dev:skill-development` was loaded as the dispatch asked.
