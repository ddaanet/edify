# Deliverable Review — prose and config

Scope: the agentic prose, human docs and configuration changed over
`d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`, judged at HEAD against
`plans/review-fixes-2/outline.md` (KD-1..KD-9, Items 2.1–2.11, 3.1–3.4). The
files are `plugin/skills/build/SKILL.md`, six `build` references, three agents,
three fragments, `plugin/README.md`, `build-run-state.md`, `decisions.md`,
`design.md`, `pipeline-contracts.md`, the changelog index and its two entries,
`plans/build-fixes/outline.md`, `justfile`, `plugin/portable.just`, `CLAUDE.md`,
`.claude/rules/workflow-work.md` and `.gitignore`. The two scripts the list and
count descriptions must match, `changed-files.sh` and `triage-feedback.sh`, were
read as ground truth. Recall: the plan's recall artifact and its five memory
files were read, and `craft:design-doc-writing` was loaded with its state-layer,
maintaining-entries and writing-style nodes. Line caps: `SKILL.md` is at 199
lines, under its 200 cap. Every other prose and doc file is under 400, apart
from the frozen plan `plans/build-fixes/outline.md` at 451, where the plan cap
is soft.

**Cross-surface check of the list and the report count.** The scripts define
the list as `<base> HEAD` minus `plans/<job>/`, `plans/reports/triage-feedback-log.md`
by exact name, and the `exempt-paths.sh` alternation. They define the count as
the paths that `<base> HEAD` adds directly under `plans/<job>/reports/`, minus
`item-[0-9]+-[0-9]+.md`, `review.md`, `review-*.md`, `final-review.md` and
`tdd-audit.md`. Every surface checked agrees with that in substance:

- the D-90 body and its `decisions.md` conclusion line;
- `finishing.md` §1 step 1 and §2;
- `phase-boundary.md` §Base and changed files;
- `review-requirement.md` §Execution Context;
- the `plugin/README.md` `changed-files.sh` bullet;
- the 2026-10-06 changelog entry;
- `design.md` L-2;
- the outline's KD-1.

The changelog names `tdd-audit.md` apart from "the review reports", where D-90
and the README list it among them. That difference is wording only.

## Round-2 findings status

- **C1 / M1 (prose surfaces): resolved.** D-90 now reads "Triage,
  `plugin/bin/triage-feedback.sh <job>`, takes no base: it runs the script
  itself and counts its list". `design.md` L-2 replaces "agent count" with "the
  files changed in the set the review gate reviewed, the reports committed
  beyond the one every item leaves and the review reports". The README bullet
  says triage "runs it itself and measures that list". `finishing.md` §2 says
  "It takes no base: it runs `changed-files.sh <job>` itself and measures that
  list". It also deletes the hash-substitution paragraph and states the exit
  codes as the script implements them.
- **M2: resolved.** `escalation-acceptance.md` §Rollback protocol now opens
  "Fix committed: escalate to the user with the commits since the last clean
  commit before the failed item … Nothing reverts them by default." D-92 and the
  2026-10-06 entry say the same. The 2026-10-03 entry's "A revert happens only
  by my human partner's decision" is now true.
- **M4: resolved.** `SKILL.md` §1 says "Work with no `Item N.M` … is one item,
  Item 1.1: its report is `item-1-1.md`". `finishing.md` §1 step 1 says
  "`NO-BASE:` here is a fault, not an empty run", and D-88 carries the
  resume-granularity cost.
- **M5: resolved, with one residual clause (Minor 3).** `tdd-slice.md` step 3,
  `tdd-auditor.md` (Inputs, check 2, List revisions recorded, the template's
  `Hosting file:` line and its List Revisions hint) and `pipeline-contracts.md`
  all name the hosting file. The commit takes `plans/<job>/<hosting file>` alone.
- **m2: resolved.** D-90 carries a **Limitation** paragraph on merge-shaped
  history: "How often either happens is unmeasured."
- **m3: resolved.** D-90 says "an unborn `HEAD` is a git failure, so it exits 2
  too, never `NO-BASE:`". `plans/build-fixes/outline.md` Item 1.2 Interfaces
  matches, and also names the `exempt-paths.sh` load failure.
- **m7, gate half (KD-4): resolved.** `finishing.md` §1 opens with the landed
  check, which keys `<L>..HEAD` on `review-*.md` paths, counts `review-skip.md`
  and STOPs on an empty `<L>` or a failed command. §3 steps 1 and 2 skip on
  `final-review.md` and `tdd-audit.md`. `SKILL.md` §5 adds "a review gate
  `finishing.md` §1 finds already landed is not re-run".
- **m9: resolved.** `escalation.md`, D-91 and the README say the same thing:
  "the optional `sandbox-lies` plugin's Bash hook. Without that plugin no listing
  is annotated, so … a masked listing reads as dirt."
- **m10: resolved.** `dispatch-composition.md` says "An agent spawned unnamed is
  resumed by `SendMessage` to its agent id". `delegation.md` adds "or to the
  agent id where the agent was spawned unnamed", and the "cannot be resumed"
  wording is gone, as `rg` confirms.
- **m11: resolved.** `dispatch-composition.md`, the `review-requirement.md`
  table row with the paragraph after it, and D-93 carry the same words. Each
  covers "the agent-instruction prose they load, meaning their `references/`
  nodes and the shared instruction files a skill loads from outside itself", and
  each routes "`CLAUDE.md` or `.claude/rules/*.md`" to the `review-code`
  default.
- **m12: resolved.** `escalation.md` §Resuming step 2 names each verdict:
  `CLEAN:`, `DIRTY:`, and "`PRECOMMIT:` over a clean tree, and exit 2 → STOP".
  It states the bound "a dirty resume reaches no precommit at the gate", with
  the finishing-stage variant.
- **m13: resolved.** `SKILL.md` §4.4 now reads "a slice's GREEN, its code
  review, its refactor and its list revision". `tdd-slice.md` steps 2 and 3
  each run §4.4, and step 2 also runs it on `error`. The README's call-site list
  matches.
- **m14: resolved.** `escalation-acceptance.md` §Verification sequence step 3
  gives the subject `<type>: <job> Item N.M[/k] — <title>`. A single re-run
  follows, branching on `CLEAN:`, `PRECOMMIT:`, and "a second `DIRTY:`, or exit
  2 → escalate".
- **m15: resolved.** `finishing.md` §3 step 1 says "Its report gets §1's
  structural proof before the closing commit". It covers the UNFIXABLE
  validation, the resume of `final-review` and the STOP.
- **m16: resolved.** `finishing.md` §1 step 1: "Exit 0 with no path after
  `BASE:` → … take `/build` §5's `review-skip.md` branch".
- **m17: resolved.** `escalation.md` §Post-item remediation step 2 reads "after
  its GREEN, `edify:test-driver` in GREEN mode; after its code-review, refactor
  or list-revision commit, `edify:artisan`".
- **m18: resolved.** The `review-dispatch-template.md` §Example return line now
  carries the subcategory codes and the three-gate summary, word for word as in
  §Report-only variant. §Template's placeholder points at it.
- **m19: resolved.** D-92 reads
  `git restore … -- <tracked or indexed paths> && rm -- <untracked paths>`.
- **Leg-4 open items 1–2:** the reviewed prose makes neither worse.
  Refinement to item 2: D-90 says "Both drops keep a re-run on the set the first
  run measured". A `final-review` whose fixes land in the closing commit breaks
  that, and D-90 does not state that bound.
- **Leg-4 open items 3 and 5: confirmed open.**
  - `runbook-format.md` has no guidance on one slice per failure clause.
  - `test-driver.md` and `tdd-slice.md` say nothing about out-of-batch
    contract, formatters during GREEN, or carrying code-review recommendations
    forward.
- **Leg-4 open item 6: confirmed open, and refined.**
  - The finishing stages' landed checks (KD-4) and the one-row-per-evidence
    append (KD-2) are recorded as no decision in `build-run-state.md`. KD-2 shows
    only as a consequence clause in D-90 ("the log's skip of a row equal past its
    date"). The Rejected entry "A landed check on triage keyed on the triage log"
    therefore stands against a positive decision the node never states.
  - `plugin/README.md` names `sandbox-lies` as optional, but not `plugin-dev` or
    `craft`, both of which `review-requirement.md` treats as optional.
  - No surface states the `phantom-untracked` two-name threshold. D-91,
    `escalation.md` and the README give only the bound for an absent plugin.
- **Leg-4 open items 4 and 7:** outside this partition. Item 4 concerns script
  arms, and item 7 concerns agents outside the listed files.

## Critical

None.

## Major

None.

## Minor

**1. `plugin/skills/build/references/finishing.md` §1 (the planning-artifact
paragraph), with `dispatch-composition.md` §Naming and resumption.**

- Axes: functional completeness and determinism.
- The review gate routes a planning artifact on the list "by artifact"
  (`outline.md` → `edify:outline-corrector`, and so on), but no surface gives
  that dispatch a name or a report path. §Naming lists every other dispatch:
  "Give every dispatch a `name`".
- The report's name now carries mechanism. KD-4's landed check fires only on
  `review-*.md`, triage's count excludes only the review-report names, and
  triage's `Review artifact` probe looks for `review*.md`.
- The run invented a slug. This job's own gate committed
  `plans/review-fixes-2/reports/review-outline.md` (in `🐛 review-fixes-2 Review
  gate`) for `plans/build-fixes/outline.md`. That slug works only because it
  happens to match `review-*.md`.
- Taking the agent's own default, `outline-review.md` (`outline-corrector.md`:
  "Create review file at `plans/<job>/reports/outline-review.md`"), has three
  consequences:
  - it overwrites the job's own planning report of that name;
  - a gate whose list holds only planning artifacts never reads as landed;
  - triage warns `No corrector report`.
- Severity rests on frequency: a list holding planning artifacts from another
  job is uncommon. This is a robustness edge case.

**2. `docs/references/build-run-state.md` §Rejected alternatives, and the
`decisions.md` *Rejected:* line.**

- Axes: clarity and consistency.
- The entry "**Triage dropping its own log path from the list** — a second copy
  of the list's filters, as above (D-90)" now sits beside the adopted design,
  in which the list does drop that path: "the triage log,
  `plans/reports/triage-feedback-log.md`, removed".
- What is rejected is triage filtering it on its own side. Read as a one-line
  conclusion, as `decisions.md` presents it ("triage dropping its own log path
  from the list"), it contradicts D-90.
- A label such as "Triage filtering its own log path out of the list itself"
  would carry the distinction.

**3. `plugin/agents/refactor.md` §Step 5 (the plan-sources paragraph).**

- Axes: accuracy, and a residual of M5.
- The prohibition covers every plan source ("Never write into a plan's own
  sources — `runbook.md`, `design.md`, `outline.md`, `requirements.md`"), but
  the reason still names only one: "You run inside a slice, where `runbook.md` is
  the orchestrator's artifact and a second writer collides with it".
- Under KD-7 the orchestrator's list-revision commit writes whichever of
  `runbook.md`, `outline.md` or `design.md` hosts the item. The rule holds; the
  stated reason undercovers it.

**4. `plugin/skills/build/references/phase-boundary.md` §Base and changed files,
and D-89.**

- Axes: robustness and consistency.
- `changed-files.sh` and `finishing.md`'s landed checks pass
  `--no-show-signature`. The script's own comment gives the reason: it "keeps a
  user's `log.showSignature` from printing verification lines ahead of the
  shas".
- The phase-boundary landed query does not pass it:
  "`git log -1 --format=%H <run base>..HEAD -- plans/<job>/reports/phase-<P>-corrector.md`".
  At P>1 that output is compared against `--phase`'s `BASE:` ("A hash other
  than `--phase`'s `BASE:` → STOP"). Signature lines would turn the comparison
  into a spurious STOP.
- The same omission sits in `tdd-auditor.md` check 2. There "More than one hash
  back, or none, is a violation" counts output lines.
- This is reasoned from the script's stated rationale and was not probed with a
  signed commit.

**5. `plans/review-fixes-2/outline.md` KD-1, the Reports bullet.**

- Axis: clarity.
- The bullet reads: "minus the review-gate reports (`review.md`, `review-*.md`,
  `final-review.md`, and `tdd-audit.md`, added at the review gate with the
  list's drop of the triage log, …)".
- "Added at the review gate" means added to the exclusions at the review-gate
  decision. It reads as saying that `tdd-audit.md` is written at the review
  gate, when `finishing.md` §3 step 2 writes it. It also calls `tdd-audit.md` a
  review-gate report.
- D-90 and the README avoid both readings.

**6. `plugin/skills/design/references/triage.md` §Classification Gate (outside
the listed files; a seam with N-1).**

- Axes: consistency, consumer against producer.
- `triage-feedback.sh` now treats a first `Classification:` value as a class
  only when it is exactly `Simple`, `Moderate`, `Complex` or `Defect`.
- The producer still renders the block "**per-item if composite**" with the
  template `- **Classification:** [Simple / Moderate / Complex / Defect]`, and it
  says nothing about the value having to be one bare label. It only notes "This
  file is consumed by `triage-feedback.sh`".
- Labels like the logged `Simple / Moderate agentic-prose (one route)` therefore
  keep being produced. They now yield `no-classification`, which `finishing.md`
  §2 surfaces correctly, and the rows are lost to calibration.
- A composite job's triage compares the whole run against its first item's
  class.
- Proposed only: the file sits outside this review's file list and outside the
  outline's scope.
