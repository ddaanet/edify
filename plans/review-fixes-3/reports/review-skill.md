# Review: review-fixes-3 review gate — `review-skill`

**Reviewer**: `plugin-dev:skill-reviewer` (report-only, opus), first pass
returned in one part ending `END OF REPORT`. The orchestrator wrote this report
from the returned text and applied the fixes in session (see §Fixes applied).
**Baseline**: `daad4769e5eb694f151b9972ed51555033d0e1ca`
**Files**: `plugin/skills/build/references/{dispatch-composition,escalation,finishing,phase-boundary,tdd-slice}.md`,
`plugin/skills/design/references/triage.md`

## First pass — reviewer findings (verbatim)

### Summary

All four items are delivered at their named sites. Two limits on this review:

- Without Bash I could not diff against daad4769. Item 2.4's "no other
  wording change" is checked only by reading the result: the flag is present
  and the surrounding wording reads unchanged.
- I cannot tell whether triage.md's `(C-2)` label predates the baseline.

Findings: 0 critical, 1 major, 5 minor, 1 deferred. The major and all the
minors are seams between surfaces. None is a defect at a named site.

Verified per item:

- **2.4 (KD-7):** `--no-show-signature` is present at phase-boundary.md:31
  (§Base and changed files); tdd-slice.md:57 (the GREEN-commit query);
  escalation.md:107 (§Resuming step 1); finishing.md:17, 18 and 151, which
  already carried it. No other `git log … --format=%H` command lacks the flag
  in the six files.
- **3.2 (KD-1):** dispatch-composition.md:131-136 lists
  `review-plan-<source job>-<stem>` as "a name and not a group", with the
  worked example and the reason in one clause. finishing.md:73-86 gives the
  name for each of the three artifacts, and says the prompt assigns the report
  path by §Prompt contents item 5.
- **3.3 (C-1):** escalation.md:36-47, step 2, names `<step name>-fix` with both
  examples, and step 3 escalates. dispatch-composition.md:109-113 lists the
  name with its one-clause reason.
- **3.5 (KD-3):** triage.md:104-131 covers every contract point: the job-level
  line first, the label exactly one of four with nothing after it, the reason
  (the script reads the first `Classification:` line; any other value gives
  `no-classification`, so the row is lost), and the composite rule. The text is
  directive. The script's `label_prefix_re` agrees with "at the start of its
  line".
- **Earlier rounds:** finishing.md §2 agrees with triage-feedback.sh on the
  exit codes, the bare job name, the no-row-on-non-zero rule and the
  `unrecognised classification:` line. finishing.md §1 step 1 and
  phase-boundary.md agree with changed-files.sh on `BASE:`, `NO-BASE:`,
  `ERROR:` alone, the exclusions and `--phase`.

### Major

**M1. finishing.md §1, the report-commit paragraph: nothing commits a
`review-plan-*` report or the fixes its corrector applied.** The sentence
commits "every group's report, with the fixes applied". KD-1 and
dispatch-composition.md define `review-plan-<source job>-<stem>` as "a name
and not a group", so that sentence does not reach it. None of the planning
correctors commits anything. The report and the corrector's edits to
`plans/<source job>/<stem>.md` would stay uncommitted, `verify-step.sh`
returns `DIRTY:`, and escalation.md step 2 has no item to compose from after a
review-gate commit, so the run escalates. Second hazard: committing these
separately before the group reports would let the landed check's `review-*.md`
read the gate as landed on a resume. Change: commit every report this gate
dispatched — each `review-<group>` and each `review-plan-<source job>-<stem>`
— with the fixes applied, including a planning corrector's edits to the source
job's plan file, in the one gate commit. **Status: FIXED**

### Minor

**m1. finishing.md §1 UNFIXABLE paragraph names only `review-<group>`** — no
referent when the UNFIXABLE comes from a planning corrector. Change: resume the
reviewer that raised it by its dispatch name, `review-<group>` or
`review-plan-<source job>-<stem>`. **Status: FIXED**

**m2. finishing.md §1 step 2 files planning artifacts under `review-code`** —
step 2 groups every listed file into the four rows and `review-code` is the
default; the carve-out sits ~20 lines below. Change: open step 2 by setting
planning artifacts aside for the planning-artifact paragraph. **Status: FIXED**

**m3. finishing.md planning paragraph does not say the report goes under the
running job** — the correctors' own defaults sit under the source job. Change:
name `plans/<job>/reports/review-plan-<source job>-<stem>.md` under the running
job. **Status: FIXED**

**m4. No `<step name>` after a list-revision commit** (escalation.md
§Post-item remediation step 2, dispatch-composition.md `-fix` bullet) — the
list revision is the orchestrator's in-session commit, with no dispatch name to
build from. Change: after a list-revision commit, `<step name>` is
`item-N-M-s<k>-list-revision`, in both files. **Status: FIXED**

**m5. triage.md `(C-2)` label dangles** — no `C-2` resolves in docs/ or
plugin/, and in this job C-2 means the README item. Orchestrator check: the
label predates the baseline (`git show daad4769:…/triage.md` line 118), on the
paragraph Item 3.5 rewrote. Change: drop it. **Status: FIXED**

### Non-blocking note

triage.md says "Open the file with one job-level … line"; the stated reason
justifies only "the file's first `Classification:` line", since the script
accepts a heading or prose before it. The stricter rule is the outline's and is
safer. Optional clause so it is not read as what the script enforces.
**Status: FIXED** (one clause added).

### Deferred

**D1. A `-green-fix` commit vs. `tdd-auditor.md` check 2** — a slice finished
by a `-fix` dispatch spans two commits, which check 2 calls a violation.
DEFERRED: agent definitions are another group's files; Item 3.3's contract
covers naming only; the auditor flagging a remediation commit arguably surfaces
the RCA escalation.md already asks for. No change.

### Not flagged (checked)

- dispatch-composition.md `git log --diff-filter=A` has no `--format=%H`,
  outside KD-7's literal rule.
- escalation.md §Resuming step 1's unranged query: pre-existing, next to the
  deferred "resume tracking a list revision" candidate.
- The correctors' default report paths: corrector family is Scope OUT; KD-1
  overrides them through the prompt.

**Overall rating (first pass):** Needs Improvement — one major seam (M1), the
rest minor.

## Fixes applied (orchestrator, in session)

- M1 — `finishing.md` §1 report-commit paragraph: one commit for the whole
  gate, carrying every report the gate dispatched (`review-<group>` and
  `review-plan-<source job>-<stem>`) with the fixes, a planning corrector's
  edits to the source job's plan file included; one sentence on why a
  `review-plan-*` report committed alone would read as the gate landed.
- m1 — `finishing.md` §1 structural-proof paragraph: resume the reviewer that
  raised the UNFIXABLE by its dispatch name, `review-<group>` or
  `review-plan-<source job>-<stem>`.
- m2 — `finishing.md` §1 step 2: opens by setting planning artifacts aside for
  the planning-artifact paragraph, then groups the rest.
- m3 — `finishing.md` §1 planning paragraph: the report path is
  `plans/<job>/reports/review-plan-<source job>-<stem>.md` under the running
  job, never the source job's `reports/`.
- m4 — `dispatch-composition.md` `-fix` bullet: after the in-session
  list-revision commit, `<step name>` is `item-N-M-s<k>-list-revision`;
  `escalation.md` §Post-item remediation step 2 gains the example
  `item-1-1-s2-list-revision-fix`.
- m5 — `design/references/triage.md`: `(C-2)` dropped from the persistence
  label.
- Note — `triage.md`: "so that no other line beginning `Classification:` can
  precede it" added.

See §Second pass for the independent review of these edits.

## Second pass — reviewer findings over the applied fixes

Resumed once by `SendMessage`; one part ending `END OF REPORT`.

**Verified:** every fix correct at its site, no new seam with
`build-run-state.md` D-89/D-93, `tdd-slice.md` §After the slice,
`triage-feedback.sh` or `changed-files.sh`. M1's single gate commit keeps D-89's
landed check atomic; m2's "under another job's `plans/` directory" matches
`changed-files.sh` dropping `plans/<job>/`; m4's
`item-N-M-s<k>-list-revision` collides with no dispatch name and its `-fix`
report counts under Reports like the other `-fix` reports.

**Minor (3):**

- **n1.** `finishing.md` structural-proof paragraph said "the reviewer that
  raised it" twice. Change: from the colon on, "; a report-only group's
  reviewer replies in parts as on the first pass, and this session rewrites the
  report from it." **Status: FIXED**
- **n2.** `triage.md`: "no other line beginning `Classification:`" is narrower
  than `label_prefix_re`, which accepts the bulleted form too. Change: "no other
  `Classification:` line, bulleted or bare, can precede it". **Status: FIXED**
- **n3.** Lines the in-session edits left unwrapped in `finishing.md` and
  `triage.md`. Change: run the formatter before the report commit. **Status:
  FIXED** (`just format` reflowed `escalation.md` and `finishing.md`;
  `just precommit` green.)

**Unchanged:** D1 stays DEFERRED; it applies equally to `-list-revision-fix`.
Agent definitions are Scope OUT.

**Overall rating (second pass):** Pass. The second pass's fixes go unreviewed
by design (`finishing.md` §1).

**Verification:** `just precommit` green (`Tests cached`); touched modules run
directly — `tests/test_build_prose_git_log.py`, `tests/test_changed_files.py`,
`tests/test_triage_feedback*.py`: 48 passed.
