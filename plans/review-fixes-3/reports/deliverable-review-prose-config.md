# Deliverable Review — prose and docs: review-fixes-3

## Scope

Layer 1, prose and docs partition, read-only. The review judges the final state
at HEAD over `daad4769..HEAD` (36 commits). The baseline is
`plans/review-fixes-3/outline.md`: KD-1 to KD-7, Item 2.4 (prose side), Items
3.1–3.6 and 4.1, and the traceability rows m3, m11–m17, C-1 and C-2. Findings
are checked against `plans/review-fixes-2/reports/deliverable-review.md`
(round 3).

Files:

- Agentic prose: `plugin/skills/build/references/{dispatch-composition,finishing,escalation,phase-boundary,tdd-slice}.md`,
  `plugin/skills/design/references/triage.md`, `plugin/agents/refactor.md`,
  `plugin/agents/tdd-auditor.md`, `agents/learnings.md`.
- Human docs: `docs/references/build-run-state.md`, `docs/decisions.md`,
  `docs/references/pipeline-contracts.md`, `plugin/README.md`.
- Read for the seams: `docs/design.md`, `plugin/fragments/review-requirement.md`,
  `plugin/skills/build/references/review-dispatch-template.md`,
  `plugin/bin/triage-feedback.sh`, `plugin/skills/build/scripts/changed-files.sh`,
  `tests/test_build_prose_git_log.py` (its scanned set only), and
  `plans/review-fixes-3/classification.md`.

The review-gate commit `b4e1cf11` applied the skill-review fixes after
`review-design` had reviewed the graph. Two of those fixes are what each docs
node was re-read against:

- the single gate commit, which now holds `review-plan-*` reports and planning
  correctors' edits;
- the `<step name>-list-revision-fix` name.

The same commit also edited `build-run-state.md`: D-88's "reads as hashes" and
D-90's test-module path. Those two edits are `review-design`'s own fixes, as its
§Fixes Applied lists them.

Findings here are numbered P1–P6. That keeps them apart from round 3's m1–m18,
which the Checked clean section cites.

Out of scope, per the brief, and not reported: the bash 3.2 `source` defect in
`changed-files.sh`, test D's `printf '%b'` gap, final-review fixes landing after
triage, `plugin/skills/build/SKILL.md`, the corrector-family agents, and the
dated changelog entries.

## Critical

None.

## Major

None.

## Minor

**P1. `docs/references/build-run-state.md`, D-93 (and D-89's finishing-stage
paragraph): the design record presents the `review-*.md` match as a feature.
It does not record the one-commit rule that makes the match safe.**

- Axes: human docs consistency and completeness (a seam between the prose and
  the decision record).
- D-93 says: "the name matches `review-*.md`, so the gate's landed check (D-89),
  triage's report exclusion and its `Review artifact` probe all read its report
  as a review report".
- D-89 says the review gate lands "on a `review-*.md` report … in the range
  after the run's last item-report commit".
- `finishing.md` §1, after the gate commit `b4e1cf11`, carries a hazard and a
  rule that answers it. The hazard: "A `review-plan-*` report committed on its
  own, ahead of the group reports, would read as the gate landed to the check
  above". The rule: "make the report commit yourself, one commit for the whole
  gate: every report this gate dispatched … a planning corrector's edits to the
  source job's plan file included".
- No docs node states that rule, or that the report sits under the running
  job's `reports/`, never the source job's.
- The answer to the brief's question: D-89's widened check still holds with
  `review-plan-*.md` matching `review-*.md`, but only because of `finishing.md`
  §1's one-commit rule. The node whose job is to argue the landed mechanism
  omits both the hazard and the rule. A later edit that relaxes the single
  commit would find nothing in D-89 or D-93 to stop it.
- Nothing in the docs contradicts the change. D-86's "the phase-boundary and
  review-gate commits carry their corrector's report" and D-94's subject list
  stay true (see Checked clean). So this is an omission, not a conflict.

**P2. `plugin/README.md` §Optional plugins: the `plugin-dev` entry under-states
what is lost without it.**

- Axes: human docs completeness and accuracy.
- The section opens with "Each entry says what is lost without it". The
  `plugin-dev` entry then lists only the review gate's consequences: the skill
  row falls back, and the agent row loses its criteria source.
- Other edify prose also names `plugin-dev` skills as the ones to load:
  - `plugin/skills/design/references/write-outline.md` §Skill dependency
    indicators (`plugin-dev:agent-development`, `plugin-dev:skill-development`,
    `plugin-dev:hook-development`, `plugin-dev:plugin-structure`,
    `plugin-dev:mcp-integration`);
  - `plugin/skills/requirements/references/formats-and-exit.md` (the
    indicator → skill table);
  - `plugin/skills/build/SKILL.md` §3.3 ("e.g. `plugin-dev:skill-development`
    for skill work").
- So the entry does not say everything that is lost.
- Conformance with Item 3.6 holds: both review-gate consequences match
  `review-requirement.md` §"When plugin-dev or craft is not installed". The gap
  is the section's own completeness claim. A fix is either a clause for the
  design- and requirements-time skill loading, or wording that scopes the claim
  to the review gate.

**P3. `plugin/skills/design/references/triage.md` §Classification Gate,
persistence paragraph: "Open the file with" is stricter than what the rule
needs, and this job's own file does not meet it.**

- Axes: agentic prose constraint precision.
- The paragraph says: "Open the file with one job-level
  `- **Classification:** <label>` line, at the start of its line, before any
  per-item block, so that no other `Classification:` line, bulleted or bare,
  can precede it."
- `plans/review-fixes-3/classification.md` opens differently: first a
  `# Classification — review-fixes-3` heading, then a prose paragraph, one of
  whose lines begins "`` `Classification:` it finds and takes it as a class
  …``". `- **Classification:** Moderate` comes after both.
- The script still reads `Moderate`. Its pattern
  `^-?[[:space:]]*(\*\*Classification:\*\*|Classification:)` is anchored, and
  the backtick keeps that line from matching. The triage log shows the job's
  row as `Moderate … match`.
- The directive leaves open whether a heading or prose may precede the line.
  "Open the file with" says no. The purpose clause says yes, so long as no
  `Classification:` line comes earlier. A writer cannot tell which of the two
  is the rule.
- The file is otherwise consistent with KD-3. Its label is bare. Its per-cluster
  classes run Moderate, Moderate, Simple, Moderate, Moderate, so its job label
  is the most demanding one, as KD-3 requires.

**P4. `plugin/skills/design/references/triage.md` §Classification Gate,
persistence paragraph: the composite rule leaves Defect's rank unstated, and
the paragraph closes on a state clause.**

- Axes: agentic prose determinism and actionability.
- The text: "A composite job's label is its most demanding item's class, in the
  order Simple < Moderate < Complex … `Defect` is the job-level label only when
  every item is a Defect."
- Defect is outside the order. For a composite that mixes Defect and Moderate
  items, the reader has to infer that Defect items are ignored and the label is
  the most demanding non-Defect class. This matches KD-3's wording, so it
  conforms, but the directive is not deterministic as written.
- The closing sentence: "No calibration data backs this ordering yet; the
  triage log is where it will come from, once composite jobs have logged rows."
- The No Confabulation rule justifies flagging the ordering as ungrounded. The
  forward-looking clauses ("yet", "will come from", "once composite jobs have
  logged rows") are another matter. They are state that no later edit is bound
  to touch, and an agent writing a classification has no act to take on them.
  A single "ungrounded" clause would carry the flag alone.

**P5. `agents/learnings.md` §"When calling triage-feedback.sh", the
Anti-pattern bullet: it copies the script's error text verbatim and narrates
the output.**

- Axes: agentic prose excess.
- The bullet quotes the whole message, "(`ERROR: usage: changed-files.sh <job>
  [--phase]; not a job name: plans/outline-proofing`)". It then narrates
  triage's two output lines and adds "It never reaches a double-prefixed
  `plans/plans/outline-proofing/reports`".
- At 654 characters it is the longest line in the file. The next longest is
  471.
- A prose copy of a script message drifts when the message changes.
- What Item 3.1 asked for fits in one clause: `$1` holding `/` is refused as
  not a job name, exit 2 and not a double prefix, and a two-argument call exits
  1 with `Usage:`.
- Everything the bullet states is accurate against `changed-files.sh` and
  `triage-feedback.sh` at HEAD. The finding is excess, not accuracy.

**P6. `plugin/skills/build/references/finishing.md` §1, the planning-artifact
paragraph, with D-93 in `docs/references/build-run-state.md`: "do not route
through this gate" now reads against the gate's own steps.**

- Axes: agentic prose constraint precision, and human docs consistency.
- `finishing.md` §1 says: "Planning artifacts do not route through this gate.
  They route by artifact …".
- The same gate now handles planning artifacts throughout:
  - step 2 sets them aside "for the planning-artifact paragraph below";
  - that paragraph dispatches them;
  - the structural proof Reads their reports;
  - the single gate commit carries their reports and the correctors' edits.
- D-93 has the same shape. It opens "The `/build` review gate routes
  implementation files only", and its next sentence is "A planning artifact on
  the gate's list is dispatched as `review-plan-<source job>-<stem>`".
- Read as "not through the routing table's four rows", both sentences are
  true, but the word "route" carries a meaning neither text states. Read as
  "this gate does not handle them", both are contradicted by the text that
  follows.
- The sentences predate this range. This job's KD-1 changes are what made them
  ambiguous. Saying "not through the four group rows" would settle it.

## Checked clean

**Round-3 findings, each resolved as contracted.**

- **m3:** D-90 now bounds the claim that a re-run stays on the same set. It
  says "The bound is the reports committed under `plans/<job>/reports/` after
  Finish, which still count, such as the `deliverable-review*.md` …". It adds
  that a re-run can log a second row and that a Simple job's verdict can flip
  to `underclassified`. The final-review clause was not added, as ruled. The
  dated changelog is untouched.
- **m11:**
  - The correct pattern is `triage-feedback.sh outline-proofing`, with the base
    derived from report history (D-88).
  - The anti-pattern is `plans/<job>` as `$1`, which exits 2 and does not
    double-prefix. A two-argument call exits 1 with `Usage:`. Both are verified
    against the `case` guard in `changed-files.sh` and against triage's
    `$# -gt 1` check.
  - The bullets keep the file's unwrapped, one-line-per-bullet style.
- **m12:** `review-plan-<source job>-<stem>` is consistent across the four
  surfaces:
  - `dispatch-composition.md` §Naming lists it as "a name and not a group",
    with the `review-plan-build-fixes-outline` example and the review-report
    clause;
  - `finishing.md` §1 has one bullet per artifact and gives the report path
    under the running job, "never the source job's `reports/`";
  - D-93 has KD-1's sentence;
  - `decisions.md`'s D-93 line is unchanged, as contracted.

  No corrector definition changed in the range: no
  `plugin/agents/*-corrector.md` appears in the numstat. That closes Item 3.2's
  "No corrector definition changes".

  The claim that triage's `Review artifact` probe reads these reports holds:
  `triage-feedback.sh` tests `compgen -G "$reports_dir/review-*.md"`, so a
  `review-plan-*.md` gives `review`. Triage's report-count exclusion lists
  `review-*.md`, which also matches.
- **m13:** `refactor.md` §Step 5's reason covers every named file. The hosting
  file takes the list-revision commits, and "the rest are the plan the run
  executes against", which covers `requirements.md` and the files not hosting
  the item. The prohibition is unchanged.
- **m14 / KD-7:**
  - Every `git log … --format=%H` in the scanned prose carries
    `--no-show-signature`: `phase-boundary.md`, `tdd-slice.md`,
    `escalation.md` §Resuming step 1, `tdd-auditor.md` check 2, D-88, D-89,
    D-86 and `finishing.md`. The escalation change is the flag plus a reflow,
    with the wording unchanged.
  - D-88 states the reason once and cites
    `test_read_git_log_commands_print_hashes_only_on_signed_history`. No other
    node restates it.
  - The D-86 diff in `pipeline-contracts.md` is the flag alone, as the outline's
    list revision after 2.4/1 explains. That file is in the test's `SCANNED`
    set.
  - The gate's narrowing to "reads as hashes" matches KD-7's scope sentence.
  - Two `git log` forms sit at the edge of that scope, and neither is a
    finding. `tdd-auditor.md` §Inputs names git forms as permitted tools, which
    KD-7 rules out. `dispatch-composition.md` §Prompt contents item 5's "resolves
    it with `git log --diff-filter=A` over the report's path" is a pointer, not
    a hash-list command, and carries no `--format=%H`.
- **m15 / KD-3:** the template and the persistence paragraph require the bare
  job-level line and give the reason (`no-classification`, the row lost to
  calibration). The paragraph states the composite rule. Its wording is
  instruction, not narration, apart from P3 and P4 above.
- **The template line** `- **Classification:** <label> — exactly one of … with
  nothing after it` carries trailing text. The other template lines use the
  same `— explanation` form, and this line describes its own constraint, so it
  is not a finding.
- **m16:** D-89's conclusion and body widen to the finishing stages: the
  review gate on `review-*.md` with `review-skip.md` included, the final review
  on `final-review.md`, and the TDD audit on `tdd-audit.md`. Each is keyed
  after the last item-report commit, which matches `finishing.md` §1 and §3's
  `<L>..HEAD` queries. D-90 states KD-2's row sentence in its own words.
  `decisions.md`'s D-89 line matches the node's conclusion word for word.
- **m17:** the Rejected entry reads "Triage filtering its own log path out of
  the list on its side". It has a reason that does not contradict D-90, and
  `decisions.md`'s *Rejected:* line carries the same label.
- **m2 record:** D-90 says `ERROR:` alone, with no `BASE:` line and no path,
  and cites `tests/test_changed_files_errors.py`,
  `test_late_diff_failure_prints_error_alone`.
- **C-1:**
  - `<step name>-fix` is defined in `dispatch-composition.md` §Naming and used
    in `escalation.md` §Post-item remediation step 2. The two agree on the
    examples (`item-1-2-fix`, `item-1-1-s2-green-fix`) and on the in-session
    list-revision case (`item-N-M-s<k>-list-revision` → `item-1-1-s2-list-revision-fix`).
  - No docs node names the remediation dispatch. D-92 describes it only as "a
    fresh dispatch composed from the item", so no node is left naming only
    `<step name>-fix`.
  - A `-fix` report matches `item-*`, but it lands after the item report. The
    D-88 base and the `<L>` of `finishing.md` §1 therefore stay before the gate,
    and escalation sends post-gate dirt to step 3, not to a `-fix` dispatch.
  - `tdd-auditor.md` check 2 accounts for a marker-bearing commit "a report …
    accounts for", which covers a `-fix` commit.
- **C-2:** `plugin/README.md` names `plugin-dev`, `craft` and `sandbox-lies` in
  one place. The `plugin-dev` and `craft` consequences follow
  `review-requirement.md`'s wording, and `sandbox-lies` points at the
  `verify-step.sh` bullet under Scripts. The README's `agents/` is
  plugin-relative, like its other paths (`skills/build/scripts/`). It is
  consistent with the fragment's `plugin/agents/`.

**Docs against the gate commit's two changes.**

- No node says the gate commit holds only review reports. D-86's "the
  phase-boundary and review-gate commits carry their corrector's report" is
  singular in wording, but the principle that a report rides the commit whose
  work it reports still holds.
- D-94 lists subjects, not contents.
- D-90's "`plans/<job>/` goes too: the run's reports and the list revisions in
  the file hosting its items" concerns the running job. A planning corrector's
  edit lands in another job's plan file, which was already on the list.
- `pipeline-contracts.md` D-24's "a list revision is an edit to the file
  hosting the item" and `tdd-auditor.md` §Inputs's "orchestrator commits
  touching that file alone" both concern the running job's hosting file. The
  gate commit touches many files, so the auditor cannot mistake it for a list
  revision.
- `docs/design.md` restates no D-89 or D-93 conclusion. It cites D-88 to D-90
  and D-94 only, and those citations stay true.
- `review-dispatch-template.md` §Field Rules says "under the dispatch name
  `review-<group>`". That template structures group dispatches only:
  `finishing.md` §1 step 2 sets planning artifacts aside before step 4 uses the
  template. The two do not conflict.

**Format.**

- Every changed line in the docs and in the `/build` and `/design` prose is
  within 80 columns, counted in characters. The only exceptions are the two
  `agents/learnings.md` bullets, which follow that file's unwrapped style.
- Line counts: `build-run-state.md` 273, `pipeline-contracts.md` 315,
  `decisions.md` 215, `finishing.md` 189, `dispatch-composition.md` 157,
  `escalation.md` 156, `triage.md` 132, and `plugin/README.md` 118. All are
  under the 400-line cap.
- No changelog entry was added, as contracted.
- No broken references: `finishing.md` §1 points at `dispatch-composition.md`
  §Naming and resumption and §Prompt contents item 5, and `escalation.md`
  points at `dispatch-composition.md`. Both sections exist.

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| Major | 0 |
| Minor | 6 |

Every round-3 finding in this partition is resolved as contracted: m3,
m11–m17, C-1 and C-2. KD-1's name is consistent across the four surfaces.
KD-7's flag is on every hash-reading `--format=%H` command, and D-88 gives the
reason once. None of the six minors comes from the fixes going wrong:

- P1: the design record lags the review gate's one-commit rule.
- P2: the README's optional-plugin section claims a completeness it lacks.
- P3 and P4: precision in triage's persistence directive.
- P5: excess in the learnings bullet.
- P6: "route" is ambiguous now that the gate handles planning artifacts.
