# Review gate — skill group (`plugin-dev:skill-reviewer`, report-only)

Reviewer findings, returned as text in parts and written here verbatim by the
dispatching session (build leg 6) per `review-dispatch-template.md`
§Report-only variant. The fixes this session applied, and the re-dispatch
pass, follow the findings.

## Findings (reviewer, verbatim)

### Part 1

## Review: build-defects Items 2.1–2.6 (review gate, skill group)

**Summary.** Every bullet of Items 2.1–2.6 has its deliverable, and each KD is stated where its item puts it. The problems are at the seams, found by reading rule, enforcer and consumer against each other: 3 major and 11 minor. Nothing is UNFIXABLE. Line counts, taken from Read: SKILL.md 200, finishing.md 97, phase-boundary.md 41, escalation.md 77, dispatch-composition.md 114, review-dispatch-template.md 148.

### Check 1: finishing.md §1 report-only re-dispatch (lines 40–43)

The reading is sound. KD-2's "once" caps it at one pass. Adding the second pass to the same `review-<group>.md` keeps the structural proof at one Read per group. Leaving the second pass's fixes unreviewed is the cost "once" accepts. The wording is ambiguous in three places:

- (a) "re-dispatch" could mean a fresh dispatch or a resume.
  - A fresh dispatch needs a name, and §Naming gives none.
  - Reusing `review-<group>` puts two agents on one name, but the CONTINUED protocol resumes by `SendMessage` to that name.
  - phase-boundary.md handles the same case by resuming the reviewer. Make this one a resume too.
- (b) In "Add what it returns … and apply it", the "it" has no clear referent.
- (c) The cite "(`/build` §4.1)" points at a section that *allows* self-review under §Proportionality. The reason it gives contradicts a re-dispatch that has no conditions.

Replace lines 40–43 with:

"**Report-only re-dispatch:** where this session applied a report-only reviewer's fixes, resume that reviewer (`review-<group>`) once by `SendMessage`, naming the fixes applied, over the same files: the gate's edits get an independent review, and this session's would otherwise have none. Append its findings to the group's report under a second-pass heading and apply them. There is no further pass; the second pass's fixes go unreviewed by design."

### Check 2: template pointers into dispatch-composition.md

- **§Prompt contents resolves.** Item 5 now holds the report-path rule, the return contract, UNFIXABLE inside the report and the report-only exception. The template's placeholders at lines 45 and 47, and §Field Rules line 94, all land there.
- **There is no §Naming pointer.** §Field Rules restates the name instead (see Check 3).
- **Heading form.** The section heading is "Naming and resumption". finishing.md §3 cites it in full, but dispatch-composition.md item 5 (line 41) writes "§Naming". Use "§Naming and resumption" in item 5 and in the Check 3 fix.

CONTINUED

### Part 2

### Check 3: template §Field Rules restates `<group>` (lines 94–98)

Confirmed. "`<group>` being the artifact group `finishing.md` §1 routed" lacks the one-word-slug clause that §Naming carries. Someone reading only the template can produce `review-code/tests/plans.md`. That path is nested, and `triage-feedback.sh`'s `-maxdepth 1` misses it. Replace the bullet with:

"- **Report path and return contract:** `dispatch-composition.md` §Prompt contents is the one rule for both, under the dispatch name `review-<group>` that `dispatch-composition.md` §Naming and resumption defines. The structural proof reads the path actually dispatched, so the prompt and the proof must name the same file."

Optional, in §Naming: fix the four slugs (`code`, `skill`, `agent`, `design`) instead of leaving each run to choose. The choice is mechanical, so it belongs in the text.

### Seam: `git diff --name-only <base>` picks up exempt dirt

The other reviewer is correct. `git diff <commit>` compares the working tree to the commit, so tracked exempt dirt lands in the list:
- ` M memory`
- a modified or staged `.claude/handoff-*.md`
- a modified tracked `inbox/*.md`

Untracked inbox files never appear.

`<base> HEAD` is the right fix. Both call sites run right after a `verify-step.sh` exit 0:
- phase-boundary.md runs after the phase's last §4.4.
- finishing §1 runs after the last §4.4, plus, for a phased run, the last phase-boundary commit (see m5).

So HEAD holds all the work, and by KD-7's premise no commit carries exempt dirt. Filtering the list by the exemption pattern instead would copy verify-step.sh's list into a third place.

finishing.md line 13:

"1. List changed files: `git diff --name-only "$(cat tmp/build-baseline)" HEAD`. This lists committed changes only: apart from them the tree holds only paths `verify-step.sh` exempts, and no commit carries those."

phase-boundary.md lines 7–11:

"The changed-files list is the phase's committed diff against its base. It is taken against `HEAD`, not the working tree, so the paths `verify-step.sh` exempts stay out:

```bash
git diff --name-only <phase base> HEAD
```"

A consequence, not a flag: `review-requirement.md` §Execution Context is outside this list, but it prescribes the same `<base>` form and needs the same `HEAD` in its own item.

CONTINUED

### Part 3

### Major (3)

**M1: SKILL.md §4.1 line 117 commits without a pathspec.** It reads "apply the edits, `just precommit`, commit." This is the last orchestrator commit in the six files without KD-7's form. It is also the most exposed one: an in-session `/handoff` leaves `.claude/handoff-task.md` staged, and this repo's status shows exactly that right now (`M  .claude/handoff-task.md`). Replace it with:

"Read the targets, apply the edits, `just precommit`, then stage the edited paths by name and commit with `git commit -- <paths>`."

**M2: SKILL.md §4.1 lines 119–123 vs §4.4: nothing commits §4.1's corrector.**
- §4.1 dispatches `edify:corrector` "scoped to this item's changes". Under dispatch-composition item 4, that corrector commits nothing.
- §4.2's new commit paragraph covers only "Where the item is a review".
- So §4.4 runs on a tree still holding the corrector's report and fixes, gets DIRTY, and escalation.md resumes a corrector with "Fix and commit".
- The dispatch also has no name in §Naming, so its report path is undefined.

Append to §4.1:

"Name it `item-N-M`, which is free because the item itself was not delegated. It commits nothing, so commit its report and fixes as §4.2 does for a review item, before §4.4."

In §4.4, change "a review item once §4.2's commit lands" to "a review item or §4.1's corrector once its commit lands". The `item-N-M` name is my proposal, not established; §Naming in dispatch-composition.md would need to list it.

**M3: SKILL.md §2 lines 71–80 vs escalation.md §Resuming lines 59–62: a resumed run overwrites the baseline before it learns not to.**
- escalation.md says a resumed run keeps `tmp/build-baseline`.
- But a re-invoked `/build` runs §2's capture first. Only §6, which comes later, routes to escalation.md.
- Recapturing silently shrinks the whole-run diff (finishing §1 and triage) and the phase-1 base.
- The §2 entry gate also STOPs on a killed run's dirty tree instead of remediating it.

Fix:
- In SKILL.md §1, after the KD-6 sentence, add: "A resumed run Reads `references/escalation.md` §Resuming before §2, and skips §2's baseline capture."
- In §2 "Capture the baseline", add: "(not on a resumed run, which keeps the file)".

Open question, not a fix I can ground: nothing deletes `tmp/build-baseline` at completion, so the file existing cannot be the resume test, because a stale one from an earlier job looks the same. Whether to scope it by job (`tmp/build-baseline-<job>`) is a design call.

CONTINUED

### Part 4

### Minor (11)

**m1: finishing.md §1 lines 25–27 and template lines 71–74 do not carry the part protocol.** Item 5 now handles CONTINUED and END OF REPORT (item-2-5-review Major 1). But the two texts the orchestrator actually follows still say to read the findings and write the report, with no pointer to item 5.
- finishing.md: "delegate, collect the findings it returns in parts as `dispatch-composition.md` §Prompt contents item 5 says, then write the report…"
- Template line 71: "The **calling session** then collects the parts (`dispatch-composition.md` §Prompt contents item 5) and writes them to the group's report path…"

**m2: dispatch-composition.md §Agent behaviour contract (lines 111–114) restates the return contract and conflicts with item 5.**
- "returns only the filepath or an error" repeats item 5 in different words and drops its exceptions.
- "resumed at most once before a fresh launch" contradicts item 5's repeated part-resumes.

Replace the sentence with: "…resolves recall by reading the artifact's listed files itself, returns per §Prompt contents item 5, and after a failure is resumed at most once before a fresh launch. The report-only reviewer's part-resumes are its return protocol, not recovery."

**m3: escalation.md §Resuming (lines 59–73) has three problems:**
- It restates phase-boundary.md's base resolution word for word, though review-requirement.md names phase-boundary.md as the resolver.
- Steps 1–2 still say "checkpoint commit" and "that checkpoint's verification", which no longer mean anything now that "checkpoint form" is gone.
- The base paragraph is not tied to the steps.

Replace lines 59–73 with:

"Where the work is a phased runbook, the current phase's base resolves as `references/phase-boundary.md` says. A resumed run keeps `tmp/build-baseline`, phase 1's base, rather than recapturing it.

1. Find the last committed item or phase-boundary commit in `git log` (`Item N.M` subjects, `phase-<P>-corrector.md` reports).
2. Run `plugin/skills/build/scripts/verify-step.sh`.
3. Build the inventory of remaining work from its output.
4. Resume from the next item."

**m4: escalation.md exit-1 (lines 18–23) resumes an agent that cannot commit.** It is reached from finishing §1 line 60 and from §4.4's review-item case. It resumes "the named agent" with "Fix and commit", but:
- a review dispatch commits nothing (item 4);
- `plugin-dev:skill-reviewer` has no tools;
- the commit was the orchestrator's.

After "remediate:", add: "where the named agent commits nothing (a review dispatch) or holds no edit tools, skip the resume and go to the fresh `edify:artisan`."

**m5: phase-boundary.md lines 35–38: the commit that closes a phase is never verified.** SKILL.md §4.4 now lists §4.2's review commit but not this one, and Item 2.2 removed the only run here. A stray corrector edit outside the named paths first shows up at the next item's §4.4, where remediation resumes the wrong agent. Add to §4.4's list: "a phase-boundary corrector once its commit lands".

CONTINUED

### Part 5

**m6: SKILL.md §1 line 26 defines `<job>` in terms of itself.** It reads "`<job>` is the `plans/<job>` path". If `<job>` means the path, `plans/<job>/runbook.md` doubles `plans/`, and finishing §2 needs the bare name. Replace with: "`<job>` is the job directory named by the invocation's `plans/<job>` path."

**m7: SKILL.md §2 lines 56–60: the DIRTY bullet says STOP before the mask exception.** Put the exception first: "Exit 1 with `DIRTY:` → if the `sandbox-lies` hook annotates the listing as sandbox masks, re-run per `references/escalation.md` §Post-item remediation; otherwise STOP: "Dirty tree. …". Any change is dirt…"

**m8: leftover "checkpoint" wording.** dispatch-composition.md line 98 says "`phase-P-corrector` for checkpoints", and phase-boundary.md line 40 says "**final checkpoint**". Items 2.1 and 2.2 removed this term elsewhere. Change them to "for phase boundaries" and "the **last phase's boundary**".

**m9: review-dispatch-template §Field Rules line 106 has a naming clash.** The "**Constraint:**" bullet (implementation only) sits beside the new `**Constraints:**` block and reads as that block's rule, while the block has no rule of its own.
- Rename the bullet to "**Implementation only:**".
- Add: "- **Constraints:** the scope-OUT bar, verbatim; add any the design names."

**m10: finishing.md §2 lines 75–77: "investigate before §3" gives no way out.** Append: "then run §1, or write `/build` §5's `review-skip.md`, before §3."

**m11: SKILL.md is at the hub cap.** It is 200 lines against the ~200-line cap, and M1–M3 add lines. Rather than tightening lines, cut §3's rationale paragraph (lines 84–88) and §2's "A file, not a shell variable…" (lines 77–80) to one clause each, or move them to a reference.

### Positive aspects

- Each KD is stated where its item puts it: KD-3's WARNING handling, KD-4's procedure and tool removal, KD-5's ownership and confirmation clauses, KD-7's exemption list and mask re-run.
- The pathspec commit form matches across item 4, §4.2, phase-boundary.md and finishing §1.
- Item 5 is now one rule, and the template's placeholders point at it instead of restating it.
- The phase-boundary halt names all five §Execution Context fields.

### Overall rating: Needs Improvement

### Priority recommendations

1. M2 then M1: the §4.1 commit gap fires on every delegated §4.1 review.
2. M3: the baseline gets recaptured on resume.
3. The `<base> HEAD` seam, and the resume wording from Check 1.

END OF REPORT

## Fixes applied by the dispatching session (build leg 6)

- **Check 1:** `finishing.md` §1 report-only re-dispatch replaced with the
  reviewer's text: a resume of `review-<group>` by `SendMessage`, findings
  appended under a second-pass heading, no further pass.
- **Check 2 / Check 3:** `dispatch-composition.md` item 5 cites
  "§Naming and resumption"; `review-dispatch-template.md` §Field Rules now
  points at that section for `review-<group>` instead of restating `<group>`.
  The optional fixed slug list was **not** applied: this run's groups were
  `code`, `agents`, `fragments`, `skill`, and fixing the list is a naming
  decision left to my human partner.
- **`<base> HEAD` seam:** `finishing.md` §1 step 1 and `phase-boundary.md` now
  diff `<base> HEAD`. This refines KD-1's literal command
  (`git diff --name-only <phase base>`) to its stated intent, the committed
  diff. `review-requirement.md` keeps the working-tree form: its fragments-group
  reviewer judged it right for `/review` of uncommitted work.
- **M1:** `SKILL.md` §4.1 commits with `git commit -- <paths>`.
- **M2:** `SKILL.md` §4.1 names its corrector `item-N-M` and commits its report
  and fixes before §4.4; §4.4 lists that commit; `dispatch-composition.md`
  §Naming lists the `item-N-M` use.
- **M3:** `SKILL.md` §1 routes a resumed run to `escalation.md` §Resuming
  before §2, and §2's baseline capture is skipped on a resumed run. The open
  question (scoping `tmp/build-baseline` per job) was **not** acted on — a
  design call.
- **m1:** `finishing.md` §1 and the template's calling-session paragraph point
  at item 5 for collecting parts.
- **m2:** `dispatch-composition.md` §Agent behaviour contract defers to item 5
  and separates part-resumes from recovery resumes.
- **m3:** `escalation.md` §Resuming no longer restates the phase-base
  resolution; steps 1–2 name concrete commits and `scripts/verify-step.sh`.
- **m4:** `escalation.md` exit-1 skips the resume where the named agent commits
  nothing or holds no edit tools.
- **m5:** `SKILL.md` §4.4 lists the phase-boundary corrector's commit.
- **m6:** `SKILL.md` §1 defines `<job>` as the job directory.
- **m7:** `SKILL.md` §2 DIRTY bullet puts the mask re-run first.
- **m8:** "checkpoints" / "final checkpoint" become "phase boundaries" /
  "last phase's boundary".
- **m9:** template §Field Rules: a `**Constraints:**` rule and the renamed
  "**Implementation only:**" bullet.
- **m10:** `finishing.md` §2 gives the WARNING path its way out.
- **m11:** `SKILL.md` held at 200 lines (the checker's hard cap for
  `SKILL.md`): §2's baseline-file rationale and §3's rationale were condensed
  to one clause each, keeping their reasons, and a duplicate resume clause in
  §1 was dropped in favour of §2's.

`just format` then `just precommit`: Precommit OK (the three allowlisted
agent-definition `oversized-file` lines only).

## Second pass (reviewer, verbatim)

SECOND PASS, PART 1 of 2

I checked every fix recorded under "Fixes applied by the dispatching session" against the six files as they now stand.

**Applied correctly (no issue):** Check 1–3, the `<base> HEAD` seam, M1, M2, m1, m2, m4's main case, m6, m7, m8 and m11. On the two cuts to the `SKILL.md` rationale:
- §2 keeps its reason ("no shell variable survives to Section 5"; gitignored, so outside the diff).
- §3 keeps its core reason (a warm-context token would fail open, invisibly). It loses the cost side, "one cheap duplicate recall is the cheaper side". That is acceptable at the cap.

### Major (1)

**S1: `escalation.md` §Resuming, steps 2–3 (lines 67–68).** This is a regression, and it comes from my own m3 text.
- Step 3 builds "the inventory of remaining work from its output", but `verify-step.sh` prints CLEAN/DIRTY and precommit output. It lists no work.
- A DIRTY verdict at step 2, which a killed run makes likely, has no route. The run then reaches `SKILL.md` §2 and STOPs "Dirty tree. Commit or stash". So M3's second bullet, remediate rather than STOP on resume, is still open.

Replace steps 2–3 with:

"2. Run `scripts/verify-step.sh`. Anything but exit 0 → §Post-item remediation above, before anything else; the entry gate then finds the tree clean.
3. Build the inventory of remaining work: the work's items minus those step 1 shows landed."

### Minor (8)

**S2: `escalation.md` §Resuming step 1 (lines 65–66).**
- The evidence it names is "`Item N.M` subjects". Only slice commits are required to carry that marker (`dispatch-composition.md` item 4). General and directly executed items have no subject rule.
- Name the reports as well: "(`Item N.M` subjects, `item-N-M*.md` and `phase-<P>-corrector.md` reports)".
- A directly executed, self-reviewed item still leaves neither a report nor a guaranteed marker. Closing that gap needs `SKILL.md` §4.1's commit to carry `Item N.M` in its subject, which is your call at the line cap.

**S3: `SKILL.md` §1 line 28 and §2 lines 72–73.**
- "Resumed run" now gates skipping the baseline capture, but no test for it is stated. Before this change the question never arose.
- Resuming also ends with "Resume from the next item", which can read as a jump straight to §4. That would skip §3's recall in the fresh session.

Replace line 28 with: "A resumed run (the invocation says so, or `plans/<job>/reports/` already holds this run's reports) Reads `references/escalation.md` §Resuming before §2, then runs §2 and §3 and starts §4 at the item §Resuming names."

This does not settle the stale-file design call, which stays yours.

**S4: `phase-boundary.md` lines 37–40.** m5 put the phase commit in `SKILL.md` §4.4's list, but a reader following `phase-boundary.md` ends at "commit and continue" and does not go back to §4.4. Append: "Then run `/build` §4.4's verification."

SECOND PASS, PART 2 of 2

**S5: `escalation.md` exit-1, lines 18–20 (the m4 fix).** The skip condition covers an agent that commits nothing or holds no edit tools. It does not cover dirt with *no* named agent: a directly executed item that was only self-reviewed, which §4.4 also verifies. Extend the condition: "Where there is no named agent (an item executed in session and self-reviewed), or the named agent commits nothing (a review dispatch) or holds no edit tools, skip the resume and go to the fresh `edify:artisan`."

**S6: `finishing.md` §1 line 43.** The heading still says "Report-only re-dispatch", but the text now resumes the reviewer. Rename it "**Report-only second pass:**" so it matches.

**S7: `finishing.md` §2 lines 80–83 (the m10 fix).**
- The text says "before §3" twice.
- After running §1 late, §2's triage has to run again, because its WARNING came from the missing report.

Replace from "— then run" with: "— run §1, or write `/build` §5's `review-skip.md`, then rerun §2."

**S8: `review-dispatch-template.md` §Field Rules line 107 (the m9 fix, my wording).** "the scope-OUT bar, verbatim" does not say what is verbatim. Replace it with: "- **Constraints:** keep the template's scope-OUT bullet as written; add any constraint the design names."

### Noted, not flagged

- **Report counting.** Naming §4.1's corrector `item-N-M` makes its review report match the `item-*` reports that `triage-feedback.sh` counts in `reports_count`. Any `review-*` name would instead break the script's skip detection. This is Q-2's territory, so it is OUT.
- **Pre-existing, not a regression.** `SKILL.md` §4.1 commits before review, and "Self-review via `git diff`" after a commit shows nothing: the fragment's `git diff HEAD` is empty too.

### Rating

Pass after S1. S2–S8 are minor wording and routing fixes.

END OF REPORT

## Second-pass fixes applied by the dispatching session

All of S1–S8 applied; no further pass, per `finishing.md` §1.

- **S1, S2:** `escalation.md` §Resuming steps rewritten as proposed: step 1
  names `item-N-M*.md` reports too; step 2 routes a non-zero verify to
  §Post-item remediation; step 3 builds the inventory from the work's items.
  For S2's residual gap, `SKILL.md` §4.1's commit now carries an `Item N.M`
  subject.
- **S3:** the resume test and the "§2 then §3, then §4" order live in
  `escalation.md` §Resuming (a new sentence and step 4), not in `SKILL.md` §1,
  which already routes a resumed run there — this keeps `SKILL.md` at its
  200-line hard cap. The stale-baseline design call stays open.
- **S4:** `phase-boundary.md` ends its commit step with "Then run `/build`
  §4.4's verification."
- **S5:** `escalation.md` exit-1 skip condition covers dirt with no named
  agent.
- **S6:** `finishing.md` heading renamed "Report-only second pass".
- **S7:** `finishing.md` §2: "run §1, or write … `review-skip.md`, then rerun
  §2."
- **S8:** template §Field Rules Constraints bullet reworded as proposed.

`just format` then `just precommit`: Precommit OK; `SKILL.md` 200 lines.
