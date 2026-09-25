# Outline — build-defects

The 21 defects the skill reviews found in `/inline` and `/orchestrate` that
migrated into `/build` when those skills merged. Findings and fix text:
`plans/skill-reviews/reports/verify-inline.md` and `verify-orchestrate.md`.
IDs below are those reports' (`orch` = orchestrate). Classification:
`classification.md`.

## Provenance

- **Derived from:** none — the findings come from the skill-review sweep, not
  from a deliverable review of a prior job.
- **Base:** `d444630c01bd98851cddbedde3fbc9b85c18345d`

## Approach

The reports' fix text is the starting point, re-checked against today's files:
`build/SKILL.md` is 188 lines and off the allowlist, so their net-zero
constraint is gone, and several line numbers moved (`escalation.md` now holds
the remediation and escalation steps). Where fix text and a decision below
differ, the decision wins.

## Key decisions

**KD-1 — A phase's base is resolved from its predecessor's corrector report,
not stored.** orch C1, M8; inline M2, m10, m12. A bare `git diff --name-only`
is empty after every committed dispatch, so the phase-boundary halt fires on
every well-behaved run. The phase-P changed-files list is
`git diff --name-only <phase base>`, where the base for phase 1 is
`tmp/build-baseline` and for phase P>1 is the commit adding
`plans/<job>/reports/phase-<P-1>-corrector.md`, resolved by D-86's
`git log --diff-filter=A --format=%H -- <path>`. That commit always exists,
because the phase-boundary commit always happens. Rejected: a
`tmp/build-phase-base` file, which is one more piece of state a resumed run
must trust. Rejected: `HEAD~N`, because a phase's commit count varies with
slices and review commits.

The review gate keeps `tmp/build-baseline` and scopes each group to its share
of that list. Every Changed-files field becomes an explicit list, as
`review-requirement.md` §Execution Context requires, not a command for the
reviewer to run. The phase-boundary halt checks the full §Execution Context
set: IN, OUT, changed files, Requirements summary and Constraints. After the
review gate commits its reports and fixes, `verify-step.sh` must exit 0 before
triage feedback.

**KD-2 — `dispatch-composition.md` §Prompt contents is the only rule for report
path and return contract.** inline M1, m15, m16, m6, m11. The review gate's
dispatch name is `review-<group>`, added to §Naming, so its report path follows
from the one rule. Every dispatch returns the report path or
`blocked: <reason>`. UNFIXABLE is marked inside the report, which is what
`corrector.md` §Edge Cases already does. The report-only reviewer is the
second named exception beside `edify:refactor`: it returns its findings as text
in parts. The planning-artifact routing paragraph lives in `finishing.md` §1
only. UNFIXABLE is validated by `review-requirement.md` §UNFIXABLE Detection
Protocol before the stop. A report-only group whose fixes this session applied
is re-dispatched once, because §4.1 bars the executor from reviewing its own
edits.

**KD-3 — The review gate's reports stop counting as execution evidence.**
inline M3. `reports_count` also excludes `review.md`, `review-*.md` and
`final-review.md`. The script already reports review presence separately, in
`review_artifact`. `finishing.md` §2 surfaces `WARNING: No corrector report`
inline and investigates before §3, because §1 should have produced that
artifact.

**KD-4 — No `TaskOutput` or `TaskStop` in `/build`.** orch M1, m7. Both leave
`allowed-tools`. `TaskOutput` does not resolve, and on a running agent it can
dump the raw transcript. `TaskStop` is unprobed per
`escalation-acceptance.md` §Timeout handling. For an agent that never returns,
check its report path, `git log` and the tree, since silence or an idle reply
is not death. Then resume it by name once, and then escalate to my human
partner.

**KD-5 — `/build`'s remediation governs a dirty tree; `git clean -fd` needs
my human partner's confirmation.** orch M7. `escalation-acceptance.md` §Dirty
tree recovery defers to `escalation.md` §Post-item remediation. That means:
resume the owning agent to commit or revert its own work, then dispatch a fresh
`edify:artisan`, then escalate. The orchestrator never cleans up in its own
session. `git checkout -- . && git clean -fd` runs only where no agent owns the
dirt, and only after confirmation, because it destroys untracked work.

**KD-6 — `<job>` is always the path the invocation names.** orch C2. A run
resumed in a fresh session is re-invoked with the same `plans/<job>`, and
nothing infers it. `/build` never writes the task frame, so it cannot read the
job back from there either.

**KD-7 — Any change is dirt, except three paths dirty by convention.** orch
m5. A file a dispatch created and forgot to stage shows only as untracked, so
untracked counts. The exemptions, in any porcelain state: ` M memory` (the
gitlore submodule at rest), `.claude/handoff-*.md` (`/precompact` or
`/handoff` without a commit leaves them modified or staged) and `inbox/*.md`
(briefs dropped or updated uncommitted on purpose, so sessions need not
coordinate). They are safe to exempt because every committing dispatch stages
its paths by name and never `git add -A`, so exempt dirt cannot enter a
commit. It then commits with `git commit -- <paths>`, never a pathspec-less
`git commit`, so exempt dirt already staged stays out too. The list is hardcoded in `verify-step.sh`: all three are ddaanet
workflow conventions shared by every repo that runs this plugin. The status
runs with `--untracked-files=all`, so an untracked `inbox/` lists its files
rather than collapsing to one directory line the exemption cannot judge.

Sandbox masks are neither filtered nor gitignored. A filter hides real files
sharing the masked names, and those `.claude/` names are legitimately versioned
in other repos, whose `.gitignore` this plugin cannot rely on. Masks reach an
unsandboxed reader when a sandboxed Bash call runs concurrently. The
`sandbox-lies` plugin's `phantom-untracked` hook annotates a status listing
carrying two or more masked names, and `verify-step.sh`'s DIRTY output echoes
the porcelain lines it matches. A DIRTY verdict annotated as masks is re-run
once, not remediated.

## Items

- Item 1.1: `plugin/bin/triage-feedback.sh` — exclude review-gate and
  closing-review reports from `reports_count` (KD-3). Requirements: inline M3.
  New test file `tests/test_triage_feedback.py`: real `git` in a `tmp_path`
  repo, script run by path with CWD at the repo root, and a
  `plans/<job>/classification.md` whose classification is `Simple`. The diff
  since the baseline adds a plain text file with no definitions, so
  `Behavioral code: no`.
  Slices:
  1. `test_simple_with_review_reports_matches`: `reports/` holds what a
     reviewed Simple run leaves — `review-skill.md`, `review-skip.md` and
     `final-review.md` together. Assert stdout carries `- Reports: 0`, and that
     the line after `## Verdict` is `match`. One fixture covers every excluded
     name: a GREEN excluding only some still fails.

- Item 1.2: `plugin/skills/build/scripts/verify-step.sh` — the KD-7
  exemptions, with the status taken under `--untracked-files=all`.
  Requirements: orch m5. New test file `tests/test_verify_step.py`: real `git`
  in a `tmp_path` repo with one commit, the script run by absolute path with
  CWD at the repo root, and a stub `just` that exits 0 first on `PATH`.
  Slices:
  1. `test_conventional_dirt_is_clean_and_other_dirt_is_not`: the repo holds an
     untracked `inbox/brief.md` (the only file under `inbox/`) and a staged,
     modified `.claude/handoff-task.md`. Assert exit 0 and stdout starting
     `CLEAN:`. Then add an untracked `stray.txt`, and assert exit 1 with
     stdout carrying `DIRTY:` and `?? stray.txt` and not naming `inbox/`.
  2. Pins the slice 1 code review's F-1 and F-2, already committed. The RED is
     a mutation red: each test fails against `31fe4a16`'s script, run as a copy
     with the test module's `SCRIPT` rebound, never by reverting the tracked
     file.
     - `test_rename_out_of_exempt_path_is_dirty`: a staged
       `R  inbox/a.md -> notes.md` gives exit 1 and a DIRTY listing of that
       line.
     - `test_quoted_exempt_path_is_clean`: an untracked `inbox/my brief.md`,
       which git quotes, gives exit 0 and `CLEAN:`.
     - `test_git_status_failure_exits_2`: a run from a CWD outside any repo
       gives exit 2 and `ERROR: git status failed`.
     - `test_missing_just_exits_2`: a clean repo with no `just` on `PATH` gives
       exit 2 and `ERROR: just not found on PATH`.

- Item 2.1: `plugin/skills/build/SKILL.md`. Requirements: orch M1, m7, M4, C2,
  m3, m5; inline m9.
  - Frontmatter: drop `TaskOutput` and `TaskStop` from `allowed-tools` (KD-4).
  - §1: `<job>` is the invocation's `plans/<job>` path, and a resumed run is
    re-invoked with it (KD-6).
  - §2 DIRTY bullet: any change is dirt except the three KD-7 exemptions, named
    there; a DIRTY listing annotated as sandbox masks is re-run per
    `references/escalation.md`.
  - §3.2: turn "Patterns for implementing this, not for classifying it." into a
    sentence.
  - §4.1: replace "in its checkpoint form" with a dispatch scoped to this
    item's changes.
  - §4.2: a corrector item's report and fixes are committed by the orchestrator
    before §4.4, since the corrector never commits.
  - §4.4: add that case to the list of dispatches followed by verification.

- Item 2.2: `plugin/skills/build/references/phase-boundary.md`. Requirements:
  orch C1, M8, m3, m4.
  - Drop the `verify-step.sh` run: §4.4 already ran it for the phase's last
    item.
  - Replace the bare `git diff --name-only` with the KD-1 phase-base
    resolution.
  - Replace "checkpoint-form dispatch" with a dispatch scoped to the phase's
    items.
  - Widen the halt to the full §Execution Context set (KD-1).

- Item 2.3: `plugin/skills/build/references/finishing.md`. Requirements:
  inline m10, m11, m12, M3 (second half), m6.
  - §1 scope: each group's share of step 1's list, not "the uncommitted
    changes".
  - Structural proof: add UNFIXABLE validation and the report-only re-dispatch
    (KD-2).
  - After the report commit: run `verify-step.sh`, and require exit 0 before
    §2 (KD-1).
  - §2: handle `WARNING: No corrector report` (KD-3).
  - Keep the planning-artifact paragraph; it is the one copy.

- Item 2.4: `plugin/skills/build/references/review-dispatch-template.md`.
  Requirements: inline M1, m15, M2, m16, m6.
  - §Template and §Example: Changed files becomes an explicit list of the
    group's files.
  - Add a `**Constraints:**` block.
  - Add a criteria line for agent-definition groups: the
    `plugin-dev:agent-development` criteria.
  - Report path and return lines defer to `dispatch-composition.md` (KD-2).
  - §Field Rules: the Report path rule points at the one rule.
  - Replace the Constraint bullet's routing paragraph with a pointer to
    `finishing.md` §1.

- Item 2.5: `plugin/skills/build/references/dispatch-composition.md`.
  Requirements: inline M1, m15.
  - §Naming: add `review-<group>` for review-gate dispatches.
  - §Prompt contents item 5: name the report-only reviewer's return as the
    second exception, and state that UNFIXABLE lives inside the report (KD-2).
  - §Prompt contents item 4: a committing dispatch commits with
    `git commit -- <paths>`, naming the paths it staged (KD-7). Requirements:
    orch m5.
  - `plugin/agents/test-driver.md` and `plugin/agents/refactor.md`: their
    commit steps take the same form.

- Item 2.6: `plugin/skills/build/references/escalation.md`. Requirements: orch
  M1, m7, M7, C2.
  - Exit-1 bullet, at its head: a DIRTY verdict the `sandbox-lies` hook
    annotates as masks is re-run once, not remediated (KD-7). Requirements:
    orch m5.
  - "Agent never returns" takes the KD-4 procedure.
  - §Post-item remediation states that it governs the fragment's dirty-tree
    rule (KD-5).
  - §Resuming: re-invoke with the same `plans/<job>` (KD-6), and resolve the
    phase base per KD-1.

- Item 2.7: `plugin/fragments/review-requirement.md` §Execution Context,
  Changed files. The list comes from `git diff --name-only <base>` against the
  run's or phase's recorded base, never a bare `git diff --name-only`.
  Requirements: orch C1.

- Item 2.8: `plugin/fragments/escalation-acceptance.md` §Dirty tree recovery,
  per KD-5. Requirements: orch M7.

- Item 2.9: `plugin/fragments/delegation.md` §Multi-Step Verification. The
  correct pattern is one script owning the verdict, `/build`'s
  `verify-step.sh`. Say why the compound fails: `git status --porcelain` exits
  0 on a dirty tree too, so `&&` guards nothing. Name the script by skill,
  adding no new repo-relative path. Requirements: inline m2.

## Scope

IN: the files the items name — two scripts, two new test files, `SKILL.md`,
five references, three fragments and two agent definitions.

OUT:

- Path form of every `plugin/…` and `../../fragments/…` pointer, and where
  fragments live. That belongs to the repo-relative-paths job. New text here
  copies the form its file already uses.
- `corrector.md`'s missing "corrector never commits" prohibition (orch M5).
  That belongs to defect 21.
- The undefined "D+B anchor" term (inline m7). It is repo-wide.
- Flagging sandbox masks. That belongs to the `sandbox-lies` hook; this job
  only reads its annotation.
- `tdd-auditor.md`'s transcript fallback (orch M2). It is already fixed: no
  `transcript` or `subagents/` remains in that file.

## Open questions

- **Q-1 — D-86's mechanical check.** Default: no job, and D-86's gap stays as
  `green-report-commit.md` §Open records it. A check needs the dispatch kind,
  because a review commit legitimately carries only its report. Nothing in
  this job supplies that kind. What would settle it: an observed commit that
  adds a report without the work it describes.
- **Q-2 — `reports_count` as a complexity signal.** Default: out of scope,
  observation only. Delegation is decided per item, so a delegated Simple job
  writes `item-N-M.md` reports and still logs `underclassified`. KD-3 fixes
  only the review-report half the finding named.
