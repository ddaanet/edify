# Deliverable Review — prose and config

Range `d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`, final state at HEAD.
Baseline `plans/build-fixes/outline.md` (KD-1..KD-8, Items 2.1–2.15), and
`plans/build-defects/outline.md` Item 2.9 for `plugin/fragments/delegation.md`.
Partition: agentic prose, human docs, configuration. Sources under `plugin/`
only.

Counts: Critical 0, Major 4, Minor 10.

## Critical

None.

## Major

### M1. A committed failed fix is reverted by default

- **File / section:** `plugin/fragments/escalation-acceptance.md`, **Rollback
  protocol**. Also contradicted by
  `docs/changelog/2026-10-03-build-reads-run-state-from-report-history.md` and
  `docs/references/build-run-state.md` D-92.
- **Axis:** conformance (KD-3, Item 2.8); human-doc consistency.
- **Description:** Item 2.8's bullet reads "a revert happens only on my human
  partner's decision, by name (KD-3)". The uncommitted branch now escalates.
  The committed branch still reverts with no decision. Its scope is also wider
  than the fix: "every commit since the last clean commit before the failed
  item" reaches back to the item's own commits. That is the "discards work the
  run already paid for" outcome KD-3 rejects. History keeps the work, but the
  tree loses it.
- **Status:** the change log states the opposite policy as fact. The policy
  question is open (`build-leg4.md` open item 3, `review-skill.md` m6). It
  needs a decision and then one wording across the fragment, D-92 and the
  change log.
- **Evidence:**
  - Fragment: "Fix committed: revert every commit since the last clean commit
    before the failed item, newest first, with `git revert --no-commit <sha>`,
    then commit the reverted paths by name".
  - Change log: "A revert happens only by my human partner's decision, path by
    path."
  - D-92: "nothing reverts by default."

### M2. The `review-design` row is routed to an agent that refuses it

- **File / section:** `plugin/fragments/review-requirement.md`, routing table
  design row. Also `plugin/skills/build/references/dispatch-composition.md`
  §Naming and resumption, and `docs/references/build-run-state.md` D-93.
- **Axis:** functional correctness (rule against enforcer).
- **Description:** KD-5 sends the `docs/` design graph to `edify:corrector`.
  `plugin/agents/corrector.md` §0 "Validate Task Scope" refuses a
  single-file scope that is `design.md` or sits in a `design` path, and
  redirects to `design-corrector`. KD-5 explicitly rejects that agent for this
  row.
- **Effect:** a `review-design` group holding only `docs/design.md` fails at
  dispatch. So does a §4.1 `item-N-M` corrector over an item that edits only
  `docs/design.md`.
- **Status:** `corrector.md` is outside this job's scope (defect 21), and the
  conflict is a known open item (`build-leg4.md` open item 2). It needs a
  tracked route, because no text `/build` ships warns the orchestrator.
- **Evidence:**
  - `corrector.md`: "If the prompt's scope names a single file to review … Check
    if that file is `design.md` or in a `design` path — Design documents should
    go to `design-corrector`".
  - Routing table: "`edify:corrector` | … Not a job's `plans/<job>/design.md`:
    that is a planning artifact, reviewed by `edify:design-corrector`".

### M3. Work with no `Item N.M` ids has no defined report name

- **File / section:** `plugin/skills/build/SKILL.md` §1 "Load the work" (option
  3) and §4.1 "Direct execution". Also `references/finishing.md` §1 step 1.
- **Axis:** determinism / functional completeness.
- **Description:** KD-1 makes `item-*` reports the only resume key and the only
  source of the run base. `/build` accepts work that has no `Item N.M`
  numbering: "Neither — take the task from the invocation", and a `design.md`
  that is not item-structured. No text says what N.M such work uses for
  `item-N-M.md`.
- **Effect:**
  - If the agent improvises a name outside `item-*`, a killed run reads as
    fresh.
  - `finishing.md` STOPs on `NO-BASE:`, so a legitimate invocation-only run is
    blocked at the review gate.
- **Status:** known open question (`build-leg4.md` open item 4); still
  unresolved in the shipped text.
- **Evidence:**
  - `SKILL.md`: "3. Neither — take the task from the invocation."
  - `SKILL.md`: "write its report to `plans/<job>/reports/item-N-M.md`".
  - `finishing.md`: "Exit 1 (`NO-BASE:`, no committed item report) … → STOP".

### M4. List revisions for tdd items hosted in an outline or design are undefined

- **File / section:** `plugin/skills/build/references/tdd-slice.md` §After the
  slice, step 3. Also `plugin/agents/tdd-auditor.md` §Inputs/check text.
- **Axis:** functional completeness / determinism.
- **Description:** `tdd-slice.md` accepts slices "from a runbook, or from an
  outline or design routed to `/build`". Its list-revision step only names
  `runbook.md`. `tdd-auditor` accepts only a "`runbook.md`-only list revision"
  as an extra marker-bearing commit.
- **Effect:** for outline-hosted slices, a list revision has no target and no
  commit form. The audit then misreads the result, as it did on this job's own
  run: `tdd-audit.md` Violations 3–4 record that list changes rode a code-review
  commit or never reached the outline.
- **Evidence:**
  - "revise the remaining slices' test lists in `runbook.md` … commit with
    `git commit -- plans/<job>/runbook.md`".
  - `tdd-auditor.md`: "A marker-bearing commit that neither a report nor a
    `runbook.md`-only list revision accounts for is the violation".

## Minor

### m1. Resumption of unnamed agents contradicts the fragment

- **File / section:** `plugin/skills/build/references/dispatch-composition.md`
  §Naming and resumption.
- **Axis:** consistency.
- **Description:** This file says unnamed agents cannot be resumed.
  `review-requirement.md` step 4 (changed at HEAD, `c458a726`) resumes an
  unnamed corrector by agent id, and this run itself resumed by agent id.
- **Evidence:** "Resumption is `SendMessage` to that name; an unnamed agent
  cannot be resumed." versus "by `SendMessage` — to its name where the dispatch
  was named … otherwise to its agent id."

### m2. The KD-5 skill row is not stated identically

- **File / section:** `plugin/fragments/review-requirement.md` routing table
  skill row, against `dispatch-composition.md` §Naming and resumption and D-93.
- **Axis:** consistency / determinism.
- **Description:** `dispatch-composition.md` and D-93 limit the row to "the
  agent-instruction prose they load". The routing table takes every shared
  instruction file.
- **Effect:** a shared instruction file no skill loads (`CLAUDE.md`,
  `.claude/rules/*.md`) defaults to `review-code` by one text and goes to
  `review-skill` by the other.
- **Evidence:**
  - "skill definitions and the agent-instruction prose they load: a skill's
    `references/` nodes and any shared instruction file a repo keeps outside a
    skill".
  - "Skill definitions, their `references/` nodes, and shared instruction files
    kept outside a skill".

### m3. Resume step 2's "every other verdict" collides with §2's DIRTY STOP

- **File / section:** `plugin/skills/build/references/escalation.md`
  §Resuming, step 2.
- **Axis:** determinism.
- **Description:** §2 takes `DIRTY:` as a STOP. Step 2 says dirt is examined,
  not refused, and then defers "every other verdict" to §2. The intended set is
  presumably `PRECOMMIT:` and exit 2, but the text does not say so.
- **Gap:** a dirty resume never reaches `just precommit`, since `verify-step.sh`
  stops at the tree check. Committed-state precommit failures surface only
  after the first item.
- **Evidence:** "A masked listing is re-run first, as §2 says; every other
  verdict is taken as §2 takes it."

### m4. Refactor and list-revision commits get no post-step verification

- **File / section:** `plugin/skills/build/SKILL.md` §4.4, `plugin/README.md`
  §Scripts, and `docs/design.md` §5.3.
- **Axis:** completeness / accuracy.
- **Description:** Neither the refactor commit (`tdd-slice.md` step 2) nor the
  list-revision commit (step 3) is in §4.4's list or the README's call sites.
  `design.md` says `verify-step.sh` runs "after every step whose work is
  committed", which overclaims.
- **Effect:** a refactor that returns `error` after leaving dirt flows into the
  next slice's RED unchecked ("On `error` → log and continue"). This is
  `review-skill.md` m11 first bullet, left undecided.
- **Evidence:** §4.4 lists "a slice's GREEN, a slice's code review once its
  commit lands, a review item …, §4.1's one commit, a phase-boundary corrector
  …, and any general item" and no refactor commit.

### m5. The verification-sequence commit has no subject; its loop has no bound

- **File / section:** `plugin/fragments/escalation-acceptance.md`
  **Verification sequence**, step 3.
- **Axis:** conformance (KD-8); determinism.
- **Description:** The commit names no subject, while KD-8/D-94 say every
  `/build` commit takes one of four subjects. "re-run until it exits 0" has no
  bound and no branch for `PRECOMMIT:`.
- **Evidence:** "If `DIRTY:`: commit the fix by name (`git commit -- <paths>`),
  re-run until it exits 0".

### m6. `final-review` has no UNFIXABLE check before the closing commit

- **File / section:** `plugin/skills/build/references/finishing.md`
  §3 Completion, steps 1 and 3.
- **Axis:** constraint precision.
- **Description:** §1 explicitly greps and validates UNFIXABLE. §3.1 dispatches
  a corrector, and §3.3 commits its report and fixes with no check. The
  fragment's general rule may catch it, but the node that is followed does not
  say so.
- **Evidence:** "**Final review:** dispatch one `edify:corrector` over the whole
  diff, dispatch name `final-review`" … "Closing commit: … `final-review`'s
  report and its fixes".

### m7. An empty changed-files list is not handled

- **File / section:** `plugin/skills/build/references/finishing.md`
  §1 Review gate, step 1.
- **Axis:** completeness.
- **Description:** `changed-files.sh` can exit 0 with `BASE:` and no paths, for
  example when the only work is under `plans/<job>/` or in exempt paths. With
  no groups, nothing is dispatched or committed, and §2 then hits
  `WARNING: No corrector report`. The text does not route this case to the
  `review-skip.md` branch.
- **Evidence:** the exit-1 and exit-2 branches are covered ("Exit 1 … or exit
  2 … → STOP"). Exit 0 with no paths is not.

### m8. Remediation after a slice step does not name the agent type

- **File / section:** `plugin/skills/build/references/escalation.md`
  §Post-item remediation, step 2.
- **Axis:** determinism.
- **Description:** Dirt after a slice's code-review commit skips step 1, since
  the reviewer commits nothing. Step 2 then needs "a fresh dispatch composed
  from the item". For a tdd slice, `dispatch-composition.md` offers
  `test-driver` RED/GREEN, `artisan` or `corrector`, and nothing picks one.
- **Evidence:** "a fresh dispatch composed from the item by
  `references/dispatch-composition.md`, carrying the dirt".

### m9. The review-template example's UNFIXABLE line drops the subcategory code

- **File / section:** `plugin/skills/build/references/review-dispatch-template.md`
  §Example.
- **Axis:** consistency.
- **Description:** The UNFIXABLE validation in `review-requirement.md` requires
  U-REQ/U-ARCH/U-DESIGN plus a three-gate summary. The example prompt asks for
  the bare form, which invites a reclassification round-trip.
- **Evidence:** "Mark an issue you cannot fix "UNFIXABLE: [description]" inside
  the report."

### m10. D-92's revert recipe uses a looser operand

- **File / section:** `docs/references/build-run-state.md` D-92.
- **Axis:** accuracy / consistency.
- **Description:** The node writes `<paths>` where `escalation.md` writes
  `<tracked or indexed paths>`. The node is not executed, but it is the argued
  form.
- **Evidence:**
  `git restore --source=HEAD --staged --worktree -- <paths> && rm -- <untracked paths>`.

## Checked and found sound

- **KD-8 subjects.** Every subject prescribed in shipped text is in KD-8 form:
  - `SKILL.md` §4.1 and §4.2;
  - `dispatch-composition.md` item 4;
  - `tdd-slice.md` GREEN, code-review and list revision;
  - `phase-boundary.md` §Commit;
  - `finishing.md` Review gate and Finish;
  - `test-driver.md` and `refactor.md`;
  - the escalation-acceptance revert.

  Grepping `Item N.M` over `plugin/` and the docs finds no job-less form left in
  a `/build` commit context.
- **KD-4.** Every orchestrator and agent commit site uses
  `git commit -- <paths>`. The sites found by grepping `git commit` over
  `plugin/` are `SKILL.md`, `tdd-slice.md`, `phase-boundary.md`,
  `finishing.md`, `dispatch-composition.md`, `test-driver.md`, `refactor.md`
  and `escalation-acceptance.md`.
- **KD-3, uncommitted dirt.** No `git checkout -- .` or `git clean` remains as
  an instruction in `plugin/` or `docs/`. The only hits are a prohibition in
  `escalation-acceptance.md`, rejected-alternative text, and an unrelated
  example report.
- **KD-5.** The four slugs and the class rule are stated once in
  `dispatch-composition.md`. `finishing.md` §1 step 2 groups by them by pointer.
  The routing table matches except for m2. The template carries both
  criteria-source slots and both fallbacks.
- **KD-6.** Every base and changed-files site points at `changed-files.sh`
  rather than restating the query or regex:
  - `finishing.md` §1 and §2;
  - `phase-boundary.md`;
  - `escalation.md` §Resuming;
  - `review-dispatch-template.md` §Field Rules;
  - `review-requirement.md` §Execution Context.

  The prose matches the scripts: `BASE:`, `NO-BASE:` exit 1 and `ERROR:` exit
  2; the `<base> HEAD` form; the `plans/<job>/` and exempt drops; `--phase` as
  the latest `phase-*-corrector.md` commit in `<run base>..HEAD`, else the run
  base. `triage-feedback.sh` uses `"$baseline_commit" HEAD`, rejects an empty
  base with its usage line, prepends `plans/`, and writes
  `plans/reports/triage-feedback-log.md`, all as `finishing.md` states.
  `verify-step.sh`'s verdict prefixes and exit codes match `SKILL.md` §2 and
  §4.4.
- **KD-1 and KD-2.** Both are realised:
  - `SKILL.md` §1 has the resume test.
  - `escalation.md` §Resuming has the inventory by report history, including
    the boundary cases and the complete-report definition.
  - `phase-boundary.md` has the landed query, the P>1 check and UNFIXABLE
    validation before the commit.
- **Items 2.1–2.13.** Every bullet has a matching change, apart from the
  findings above. The m5 entry-gate routing, m7 "never returns", m8 truncated
  part, m10 `final-review` naming, m11 example note, m13 clean-tree definition,
  m14 §4.5 pointer, m15 "Phase boundaries" and m19 `blocked:` are all present.
- **build-defects Item 2.9 (`delegation.md`).** The single-script verdict is
  named by skill with no new path, and the `&&` failure is explained.
- **Decision records.**
  - `docs/decisions.md` D-88..D-94 conclusion lines match the node's bold
    headings word for word.
  - The index's 12 rejected alternatives match the node's 12
    rejected-alternative paragraphs one to one.
  - The KD-7 rename addendum is in D-91.
  - The `CLAUDE.md` routing bullet matches the node's scope.
  - `docs/changelog.md` indexes the entry.
  - `design.md` §5.3 agrees with the node, apart from the m4 overclaim.
  - The past tense in `pipeline-contracts.md` D-86 is correct.
- **Item 2.15.** `PLR0913` is removed from both `run-lint-checks` copies
  (`justfile` and `plugin/portable.just`) and nothing else in the lists changed.
  Running `.venv/bin/ruff check -q` with the lint ignore list exits 0. I did not
  run `just lint` itself, because it runs `format`, which writes files.
- **Line counts (`wc -l`).**
  - `SKILL.md`: 196, under the 200 hub cap.
  - References: 79–172.
  - Agents: 144–225.
  - Fragments: 91, 127 and 265.
  - Docs: `build-run-state.md` 188, `pipeline-contracts.md` 314, `design.md`
    339, `decisions.md` 211.

  All are under 400.
- **Non-job commits in the range.** These are not job deliverables and not
  excess:
  - the `justfile` `clean` change (`18890cfc`, the `.bin/claude` shim);
  - the `run-pytest` sentinel widening (`31fe4a16`, build-defects Item 1.2/1,
    justified);
  - the `CLAUDE.md` scraper line (`836ac12d`).
- **Noted, not a deliverable defect.** The run's own commits did not follow
  KD-8, for example `📝 Item 2.14 — …` and `🐛 Review gate — review-code
  fixes`. The run followed the pre-job text at `d415f22d`, as `build-leg4.md`
  records.
- **Out of scope per the outline, not reported.** The repo-relative
  `plugin/…` invocation form of the scripts, which will not resolve in a
  consumer repo. That belongs to the repo-relative-paths job.
