# Review: build-fixes §5 review gate, `review-skill` group

**Group**: `review-skill`
**Reviewer**: `plugin-dev:skill-reviewer` (report-only; findings returned in
four parts, written here and applied by the calling session)
**Baseline**: `d415f22daf94eb5ae5424a927e126f4010ff7a21`
**Date**: 2026-10-03
**Files in scope**:

- `plugin/skills/build/SKILL.md`
- `plugin/skills/build/references/escalation.md`
- `plugin/skills/build/references/phase-boundary.md`
- `plugin/skills/build/references/finishing.md`
- `plugin/skills/build/references/review-dispatch-template.md`
- `plugin/skills/build/references/dispatch-composition.md`
- `plugin/skills/build/references/tdd-slice.md`
- `plugin/fragments/escalation-acceptance.md`
- `plugin/fragments/review-requirement.md`

## Part 1

Summary: every bullet of Items 2.1–2.9 has a matching change. Line counts: SKILL.md 194 (cap 200); escalation 131, phase-boundary 79, finishing 134, review-dispatch-template 170, dispatch-composition 140, tdd-slice 98; escalation-acceptance 88, review-requirement 264. All under their caps. What the prose claims about changed-files.sh, verify-step.sh and exempt-paths.sh (BASE:/NO-BASE:/ERROR: exit codes, the `<base> HEAD` form, the plans/<job>/ and exempt drops, --phase taking the latest phase-*-corrector.md commit in `<run base>..HEAD` and otherwise the run base) agrees with their header comments and code. Every §-citation resolves. The citations into escalation-acceptance.md point at bold labels, not headings, which is the file's existing form.

Findings: 2 major, 11 minor, no UNFIXABLE.

MAJOR 1. The resume path's entry gate contradicts itself across three surfaces.
- SKILL.md §1 (lines 46-49) says that on resume you Read escalation.md §Resuming "before §2". Read literally, §2 still runs afterwards, and §2 STOPs on any dirt.
- escalation.md §Resuming step 2 says it replaces §2 (it runs the gate with dirt examined, not refused), and step 3 goes straight to §3.
- escalation.md §Post-item remediation's exit-1 bullet (lines 17-19) sends the entry gate's mask re-run verdict back to "SKILL.md §2, whose STOP governs it ... never remediated". Step 2 sends a resumed run's masked listing to that same bullet, so a resumed run whose re-run comes back with real dirt hits §2's STOP instead of being examined.
Verdict on Item 2.2's judgement call (step 2 stands in for §2's gate): accept the design, since KD-3's resume branch requires it. The two other surfaces must say so.
Fix A, SKILL.md §1: old "the run is resumed: Read `references/escalation.md` §Resuming before §2. None → fresh." new "the run is resumed: Read `references/escalation.md` §Resuming, whose step 2 runs §2's gate with the run's dirt examined, not refused. None → fresh."
Fix B, escalation.md lines 17-19: old "At the entry gate, the re-run's verdict goes back to `SKILL.md` §2, whose STOP governs it: dirt there predates the run and is never remediated." new "At a fresh run's entry gate, the re-run's verdict goes back to `SKILL.md` §2, whose STOP governs it: dirt there predates the run and is never remediated. On a resumed run it goes back to §Resuming step 2."

MAJOR 2. review-dispatch-template.md §Template has no slot for KD-5's design-row criteria.
KD-5 and the routing table's design row (review-requirement.md:54) both say `craft:design-doc-writing` is named in the dispatch prompt as the criteria source. finishing.md §1 step 4 builds every prompt from this template. The template's Review criteria list has a placeholder only for the agent group (line 40). A dispatcher following the template sends `review-design` to `edify:corrector` with no criteria source, and nothing tells it to note the `craft`-absent fallback.
Fix: after line 40 add: "- <design-graph group only: the `craft:design-doc-writing` skill is the criteria source — graph structure, hub/node agreement, decision records; where `craft` is not installed, say so in the report>". Optionally, append to the agent-group placeholder: "; where `plugin-dev` is not installed, review against the existing agent definitions and say so in the report".

## Part 2 — minor findings

m1. review-requirement.md:141, older slip. old: "Give corrector full design.md when reviewing phase checkpoint" new: "Give corrector full design.md when reviewing at a phase boundary"

m2. review-requirement.md:240, older slip (the protocol lists three gates). old: "missing investigation summary — complete 4-gate checklist or downgrade" new: "missing investigation summary — complete the three-gate investigation or downgrade"

m3. review-requirement.md:51, the code row reads "Code, tests, plans | `edify:corrector`". It contradicts the same table's design row (line 54, `plans/<job>/design.md` to `edify:design-corrector`), finishing.md §1 and D-26 (`runbook.md` to `edify:runbook-corrector`), and KD-5's default-for-unnamed-kinds. Verdict on Item 2.9's "plans left in the code row" call: reject. new: "| Code, tests, and any file kind no other row names | `edify:corrector` | Default — general quality review. Planning artifacts route by artifact (pipeline-contracts.md D-26) |"

m4. finishing.md:37-39, the fix-capable list is stale after KD-5: it names design-, outline- and runbook-corrector though lines 50-54 say planning artifacts never route through this gate. new: "- **Fix-capable reviewers** (`edify:corrector`, which takes every row but the skill row, and that row too without `plugin-dev`): delegate,"

m5. review-dispatch-template.md:88-89, Item 2.5's `blocked:` routing lands on a file with no bullet for a `blocked:` return. Verdict: accept the direction; make the pointer land. new: "STOP and report the reason to the user, as `references/escalation.md` §Escalation's \"Unexpected result\" bullet does: the structural proof has no report to Read." (Or add a `blocked:` bullet to escalation.md §Escalation.)

m6. escalation-acceptance.md:36-37, Item 2.8's `git revert HEAD` is right only when the failed fix is one commit at HEAD; the revert commit's "Revert …" subject is outside KD-8's forms. Verdict: accept keeping a committed-fix revert; correct the mechanics. new: "- Fix committed: revert each commit the failed fix landed, newest first, with `git revert <sha>` — never `git reset`, which discards history". Whether KD-3's "nothing reverts by default" should also cover committed work (escalate first) is a call for my human partner — flagged, not decided.

## Part 3 — minor findings, continued

m7. escalation.md:104-110, the resume case "report present, uncommitted and complete" commits the report "as phase-boundary.md commits it", but phase-boundary.md §Commit commits only "once no validated UNFIXABLE stands"; the resume path skips that check. new: "Apply in session the fixes that did not land, check the report for UNFIXABLE as `references/phase-boundary.md` §Review does, then commit the report"

m8. escalation.md:32-35, remediation step 2's "a fresh dispatch composed from the item" is undefined at finishing.md §1's review-gate commit and §3's closing commit. Fix: append "At the review gate or the closing commit there is no item to compose from: go to step 3."

m9. escalation.md:94-100, the inventory omits the refactor: a kill before tdd-slice step 2 silently loses a flagged refactor. Fix: append to the slice list "and, where that code-review report flags a refactoring, `item-N-M-s<k>-refactor`", phrased on the report's history.

m10. SKILL.md §4.2, lines 130-132: the review-item commit gives `git commit -- <paths>` but no subject. Fix: add ", subject `<type>: <job> Item N.M — <title>`".

m11. Low priority: SKILL.md §4.4 omits the list-revision and refactor commits (only if §4.4 should be exhaustive); dispatch-composition.md:19-20 says tdd-audit's inputs are "the slice reports and the commit range" while finishing.md §3.2 says git only resolves each report to its adding commit — align to "the slice reports and the commits that add them".

## Part 4 — verdicts on the judgement calls, and priorities

- 2.1: "Sections 4 and 5" and "Section 4 and finishing.md call the same one": accept.
- 2.2, resume step 2 stands in for §2's gate: accept the design; the hub and the remediation bullet still contradict it (MAJOR 1).
- 2.2, `PRECOMMIT:` over a clean tree in the live-run resume message: accept.
- 2.2, "the user" voice: accept.
- 2.3, the P>1 landed query for P-1 with STOP on an empty result: accept (KD-2 requires it; `--phase` alone cannot detect a skipped boundary commit).
- 2.3, the extra STOP when the P-1 hash differs from `--phase`'s `BASE:`: accept and keep (agree in normal flow; a mismatch is an anomaly; costs nothing on the happy path).
- 2.3, the new section headings: accept.
- 2.4, `NO-BASE:` → STOP at finishing: accept. Whether SKILL.md §1 option 3 (task from the invocation) names its report `item-1-1` is not settled by the outline; stays open.
- 2.4, a single review-gate commit: accept.
- 2.4, nothing to commit at §3 while verify still runs: accept.
- 2.5, `blocked:` routed to escalation.md: accept in direction; pointer unspecific (m5).
- 2.5, subcategory glosses inline: accept.
- 2.6, item subject added to item 4: accept.
- 2.6, "nothing mechanical" keys on a subject: accept.
- 2.6, no design-row reviewer in dispatch-composition: accept; the prompt-side gap belongs to the template (MAJOR 2).
- 2.7, GREEN subject moved to KD-8 form: accept.
- 2.7, `SKILL.md` named in the m14 fix: accept.
- 2.8, `git revert HEAD` kept: accept for scope; fix the mechanics (m6).
- 2.8, "commit the fix by name" in step 3: accept.
- 2.8, the `DIRTY:` trigger: accept.
- 2.9, working-tree form also covers §4.1's corrector: accept.
- 2.9, untracked files added by name: accept.
- 2.9, UNFIXABLE step 4 resumes by name, fresh delegation as fallback: accept.
- 2.9, "plans" left in the code row: reject (m3).
- Older slips in review-requirement.md: both still present (m1, m2).

Priority: (1) MAJOR 1; (2) MAJOR 2; (3) m7, m3, m4; (4) m1, m2, m5, m6, m8, m9, m10, m11.

Out of scope, as instructed: corrector.md §0's design-document rejection against KD-5's design row.

## Fixes Applied

Each finding was checked against the file before editing; every one held at
the cited location.

- **MAJOR 1, Fix A** — FIXED. `SKILL.md` §1: the resume branch now reads "Read
  `references/escalation.md` §Resuming and follow it in place of §2, whose gate
  its step 2 runs with the run's dirt examined, not refused." Adapted from the
  suggested wording: "in place of §2" states the act (do not run §2 as well)
  rather than leaving it to be inferred from the description of step 2.
- **MAJOR 1, Fix B** — FIXED as suggested. `escalation.md` §Post-item
  remediation, exit-1 bullet: "At a fresh run's entry gate … On a resumed run it
  goes back to §Resuming step 2."
- **MAJOR 2** — FIXED. `review-dispatch-template.md` §Template: added the
  design-graph placeholder (`craft:design-doc-writing` criteria — graph
  structure, hub/node agreement, decision records; `craft` absent → say so in
  the report), and appended the optional `plugin-dev` fallback clause to the
  agent-group placeholder. Adapted: the design line opens "the
  `craft:design-doc-writing` criteria —", the agent line's form, instead of
  "the skill is the criteria source".
- **m1** — FIXED as suggested. `review-requirement.md` §Execution Context
  anti-pattern: "phase checkpoint" → "at a phase boundary".
- **m2** — FIXED as suggested. `review-requirement.md` §UNFIXABLE validation:
  "complete 4-gate checklist" → "complete the three-gate investigation".
- **m3** — FIXED. `review-requirement.md` routing table, code row: "Code,
  tests, and any file kind no other row names", with "Planning artifacts route
  by artifact (`docs/references/pipeline-contracts.md` D-26)" in the Why cell.
  Adapted only in giving the path in full and in backticks, the form the file
  already uses for that node.
- **m4** — FIXED as suggested. `finishing.md` §1 fix-capable list: names
  `edify:corrector` only, "which takes every row but the skill row, and that
  row too without `plugin-dev`".
- **m5** — FIXED via the first option. `review-dispatch-template.md`
  §Report-only variant: a `blocked:` reply leaves no report for the structural
  proof to Read: "STOP and report the reason to the user, as
  `references/escalation.md` §Escalation's \"Unexpected result\" bullet does."
  The alternative (a `blocked:` bullet in `escalation.md` §Escalation) was not
  taken.
- **m6** — FIXED (mechanics only). `escalation-acceptance.md` §Rollback
  protocol: revert each commit the failed fix landed, newest first, with
  `git revert --no-commit <sha>`, then commit the reverted paths by name
  (`git commit -- <paths>`), subject
  `<type>: <job> Item N.M[/k] — revert failed fix`; never `git reset`. Adapted
  from the suggested `git revert <sha>`: the plain form commits on its own,
  outside KD-4's `git commit -- <paths>` form, under a "Revert …" subject
  outside KD-8's forms (the reviewer's own observation), and it requires the
  index to match `HEAD`, which a staged exempt path such as a
  `.claude/handoff-*.md` breaks. `--no-commit` lifts that requirement (`man
  git-revert`: "when this option is used, your index does not have to match the
  HEAD commit") and leaves the commit to the KD-4/KD-8 form. The policy
  question stays open below.
- **m7** — FIXED. `escalation.md` §Resuming step 1, "present, uncommitted and
  complete": apply the fixes that did not land, "check the report for
  UNFIXABLE as `references/phase-boundary.md` §Review does, then commit the
  report … as its §Commit commits it". Adapted: names §Commit explicitly and
  keeps the existing "every fix, landed and applied" and second-review-bound
  sentences.
- **m8** — FIXED, widened. `escalation.md` remediation step 2: "At a phase
  boundary, the review gate or the closing commit there is no item to compose
  from: go to step 3." Adapted: the suggestion named only the review gate and
  the closing commit, but the phase-boundary commit (`SKILL.md` §4.4's list,
  `phase-boundary.md` §Commit) reaches §Post-item remediation with no item to
  compose from too.
- **m9** — FIXED. `escalation.md` §Resuming step 1 inventory: adds ", and,
  where that code-review report flags a refactoring, `item-N-M-s<k>-refactor`
  (its refactoring commit)". Verified against `plugin/agents/refactor.md` Step
  6: the refactor commit carries that report, so the report-history rule covers
  it.
- **m10** — FIXED as suggested. `SKILL.md` §4.2: the review-item commit gains
  "subject `<type>: <job> Item N.M — <title>`".
- **m11, first bullet** (§4.4 omits the list-revision and refactor commits) —
  NOT APPLIED: the reviewer made it conditional on §4.4 being meant as
  exhaustive, which is for the deliverable review to settle.
- **m11, second bullet** — FIXED as suggested. `dispatch-composition.md`
  §Prompt contents item 2: tdd-audit's inputs are "the slice reports and the
  commits that add them", matching `finishing.md` §3.2.

`phase-boundary.md` and `tdd-slice.md` drew no finding and are unchanged.
Line counts after `just format`: `SKILL.md` 196 (cap 200); `escalation.md`
136, `review-dispatch-template.md` 172, `finishing.md` 134,
`dispatch-composition.md` 140; `escalation-acceptance.md` 91,
`review-requirement.md` 265.

The report-only second pass (`finishing.md` §1) is the calling session's step
and was not run here.

## Open for my human partner

- **(a) m6 — committed failed fixes.** KD-3 says nothing reverts by default,
  but its scope is dirt, uncommitted work. `escalation-acceptance.md` §Rollback
  protocol still reverts a committed failed fix without asking. Should "nothing
  reverts by default" cover committed work too, so a committed failed fix
  escalates before any `git revert`? This report fixed only the revert
  mechanics and did not decide the policy.
- **(b) Item 2.4 — `NO-BASE:` at finishing.** `finishing.md` §1 step 1 STOPs on
  `changed-files.sh`'s `NO-BASE:`. Whether that can happen legitimately turns on
  whether work taken from the invocation (`SKILL.md` §1 option 3) names its
  report `item-1-1`. If it does, every run that reaches finishing has a
  committed `item-*` report and `NO-BASE:` there is always an anomaly. If not,
  an invocation-only run reaches finishing with no base, and the STOP blocks a
  legitimate run. The outline does not settle this; the reviewer left it open.

## Second pass

The reviewer was resumed once over the fixes above. It returned three minor
findings:

N1. escalation-acceptance.md:36-39 — m6 narrowed the revert scope to "each
commit the failed fix landed", but line 53 still says "After rollback,
re-execute the item from clean state". Fix: "- Fix committed: revert every
commit since the last clean commit before the failed item, newest first, with"
… keep the `--no-commit`, `git commit -- <paths>`, subject and never-`git reset`
parts; reflow.

N2. Same bullet — the `git revert --no-commit <sha>` (several, newest first)
then `git commit -- <paths>` sequence is unprobed. Probe it in a scratch repo
under $TMPDIR (not this repo): two commits to revert, plus a staged path the
commit must not take. Confirm the pathspec commit succeeds, takes only the named
paths, and leaves no `.git/REVERT_HEAD` and no `.git/sequencer`. If clean,
append "(probed on git <version>)" as escalation.md's restore recipe does. If it
leaves state or refuses, adapt the recipe (e.g. a cleanup step such as
`git revert --quit`, verified by the same probe) and record what the probe
showed.

N3. escalation.md — the m8 widening has no route: "After an item, any other
exit 1 → remediate, below." becomes "After an item, or after a phase-boundary,
review-gate or closing commit, any other exit 1 → remediate, below."; "At a
phase boundary, the review gate or the closing commit there is no item to
compose from: go to step 3." becomes "After a phase-boundary, review-gate or
closing commit there is no item to compose from: go to step 3." Also retitle the
bold lead "**Remediation after an item.**" to "**Remediation after a committed
step.**" and adjust its premise sentence if it says "the item" where it now
covers non-item steps too.

Per `finishing.md` §1, these fixes get no further review.

### Second-pass fixes applied

- **N1** — FIXED as suggested. `escalation-acceptance.md` §Rollback protocol:
  "revert every commit since the last clean commit before the failed item,
  newest first, with `git revert --no-commit <sha>`", with the pathspec commit,
  subject and never-`git reset` parts kept. The bullet now agrees with "After
  rollback, re-execute the item from clean state".
- **N2** — FIXED, probe clean, recipe unchanged. Probed on git 2.47.3 in a
  scratch repo under `$TMPDIR`, which was deleted afterwards. Setup: a base
  commit, `fix1` (changing `a.txt`), `fix2` (changing `a.txt` and `b.txt`),
  then an unrelated change to `s.txt`, staged. Steps: `git revert --no-commit`
  on `fix2`, then on `fix1`, as two separate calls (both exit 0). After the
  reverts, `.git/REVERT_HEAD`, `MERGE_MSG` and `AUTO_MERGE` were present and
  there was no `.git/sequencer`. `git commit -- a.txt b.txt` exited 0. The
  commit holds exactly `a.txt` and `b.txt`, both back to `base`. Afterwards
  `REVERT_HEAD`, `MERGE_MSG` and `AUTO_MERGE` were gone, there was still no
  `sequencer`, and `s.txt` was still staged (`M  s.txt`) and not committed.
  Appended "(probed on git 2.47.3)" after the subject. No cleanup step was
  needed. The probe covered one `<sha>` per call only. A single call with
  several shas was not probed, and the recipe does not prescribe one.
- **N3** — FIXED as suggested. `escalation.md` §Post-item remediation: the
  exit-1 bullet now routes "After an item, or after a phase-boundary,
  review-gate or closing commit" to remediation, and step 2's sentence now reads
  "After a phase-boundary, review-gate or closing commit there is no item to
  compose from: go to step 3." The bold lead is now "**Remediation after a
  committed step.**", and its premise sentence now says "the step" and "the
  step's own work" instead of "the item". A search for "after an item" over
  `plugin/` and `docs/` found one more hit, in
  `docs/changelog/2026-10-03-build-reads-run-state-from-report-history.md:24`.
  That is a dated changelog entry and out of scope, so it is left untouched.
