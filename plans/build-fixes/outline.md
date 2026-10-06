# Outline — build-fixes

Second pass on `build-defects`: Majors 1–6, §4.1's share of Major 7, and 21 of
the 25 minors of its deliverable review, merged with the queued tdd job
(a)(b)(c) from `.claude/handoff-todo.md`. Finding IDs are the review's:
`Major N` from `plans/build-defects/reports/deliverable-review.md`, `mN` from
`deliverable-review-prose.md`, `F-N` from `deliverable-review-code-tests.md`.
`build-defects KD-N` means `plans/build-defects/outline.md`'s decision N.
Classification: `classification.md`.

## Provenance

- **Derived from:** `plans/build-defects/reports/deliverable-review.md`,
  superseding `plans/build-defects/outline.md`
- **Base:** `d444630c01bd98851cddbedde3fbc9b85c18345d`

## Key decisions

**KD-1 — A run is resumed when it has an item report, and report history gives
its base.** Major 1; replaces (b). §1 checks at every start: any
`plans/<job>/reports/item-*.md` on disk → the run is resumed, and Reads
`references/escalation.md` §Resuming before §2; none → fresh. The `item-*` scope
matters: planning reports (`outline-review.md`, `runbook-review.md`, `explore-*`
and others) share the directory.

Every item leaves a report, and its first commit carries it (D-86). §4.1's
self-review writes `item-N-M.md`, so §4.1 reviews the uncommitted diff —
self-review or its `item-N-M` corrector — before its one commit, which carries
the edits, any fixes and the report.

The base is the parent of the earliest commit adding an `item-*` report:
`git log --diff-filter=A --reverse --format=%H -- 'plans/<job>/reports/item-*'`,
first line, then its parent. `changed-files.sh` re-derives it wherever it is
needed (KD-6); before the first item commit nothing needs it. No baseline file,
no STOP, no deletion step. A finished job re-invoked reads as resumed: its
inventory finds every item landed and goes to finishing.

Rejected: `tmp/build-baseline-<job>` (lost with a worktree, a clone or
`just clean`, and silently recaptured); commit subjects as the resume key (a
typo breaks a convention, where a committed report is structural — KD-8); a
committed start marker (a commit to say what the log already says).

**KD-2 — A phase boundary has landed when this run holds a commit touching its
corrector report.** Major 2, my human partner's 2026-09-26 ruling. Phase P has
landed when
`git log -1 --format=%H <base>..HEAD -- plans/<job>/reports/phase-<P>-corrector.md`
prints a hash, and that hash is phase P+1's base. The boundary keys on its
report's history, not on the commit subject: a boundary always commits its
corrector report, so the path is structural, and subjects are labels only
(KD-8). Three choices follow from the query:

- The range `<base>..HEAD` excludes an earlier run's commit.
- Dropping `--diff-filter=A` counts a report the run modified rather than added.
- `-1` takes the latest commit, so a report committed twice resolves to one
  base, the one carrying the later fix.

An empty result during a live run means the boundary commit was skipped. → STOP.
Never substitute an empty base: `git diff --name-only HEAD` is a working-tree
diff that passes the empty-field check with the wrong list.

On resume, the inventory covers boundaries as well as items. For each phase
whose items have all landed but whose boundary has not:

- **`phase-<P>-corrector.md` is absent** → the boundary review has not run. Run
  `references/phase-boundary.md` for P before phase P+1's first item.
- **The report is present, uncommitted and complete** → inspect the source to
  decide which of its fixes landed, because the corrector writes its report
  before it applies fixes. Apply the fixes that did not land in session. Then
  commit the report with every fix, landed and applied, as `phase-boundary.md`
  commits it. The fixes applied in session get no second review, the same bound
  as the report-only second pass.
- **The report is present but partial** → no fix was applied, for the same
  reason. Delete the report and run the boundary.

A report is complete when it carries every section of `corrector.md` §4's
template through `## Fixes Applied`. The sections after it are conditional or
optional there.

**KD-3 — Dirt is unfinished work to examine and finish; nothing reverts by
default.** Major 5, (a), m6. This succeeds build-defects KD-5.
`git checkout -- . && git clean -fd` and §Rollback's `git checkout -- .` are
gone.

- **Live run, after an item.** The gate held the tree clean before the item, so
  non-exempt dirt is the item's own work, unless someone touched the tree in
  between.
  1. Resume the named agent: "Your dispatch left uncommitted work: finish it and
     commit it by name."
  2. No owner to resume, or no progress → a fresh dispatch composed from the
     item (`dispatch-composition.md`), carrying the dirt as a prior attempt's
     work to examine and finish. It replaces the context-free "recovery is
     mechanical" artisan.
  3. That fails → escalate with the listing and the dispatch's findings.
- **Resume after a kill.** The orchestrator examines each dirty path's diff for
  relevance to the first remaining item and for quality. What is relevant and
  sound goes into that item's dispatch as prior work; anything else escalates
  with the examination. For tdd: without its `-red.md` and `-test-review.md` on
  disk, a slice's implementation-side dirt cannot enter RED, whose proof needs
  unchanged code, so it escalates too.
- **My human partner decides escalated dirt path by path.** A path they decide
  to revert, the orchestrator reverts in session with one call:

  ```bash
  git restore --source=HEAD --staged --worktree -- <tracked or indexed paths> && rm -- <untracked paths>
  ```

  Paths come from `git status -z`. Where one side has no paths, drop that half:
  both commands error on an empty operand list. `git restore` in that form
  reverts added, modified, deleted and renamed paths (probed on git 2.47.3). The
  orchestrator still never cleans up on its own judgement.

Rejected: a default revert (it discards work the run already paid for); a
`verify-step.sh --revert` mode (a tested wrapper around two commands on a path
reached only by explicit decision); a listing token (it guards only against a
concurrent session on the same tree); a mechanical item scope (every plan would
have to declare one).

**KD-4 — Every orchestrator commit uses `git commit -- <paths>`, and no gate
runs over an uncommitted artifact of an earlier step.** Majors 3, 4.
build-defects KD-7's safety argument covers only the commits made in that form.
This job adds the two missing sites:

- `tdd-slice.md` §After the slice: the code-review commit and the `runbook.md`
  list-revision commit.
- `finishing.md`: the report commit of §1 takes `review-skip.md` too when review
  was skipped. §3 closes with one commit before the run summary. It carries the
  triage log line (`plans/reports/triage-feedback-log.md`), where
  `triage-feedback.sh` wrote one, `final-review`'s report and fixes, and
  `tdd-audit.md`. `verify-step.sh` must then exit 0.

**KD-5 — Review-gate groups are fixed rows, with fixed slugs.** (c), m9.
`/build` routes implementation files only, never planning artifacts (D-26).
There are four groups:

- `review-code` — code and tests, and the default for any file kind no row
  names.
- `review-skill` — skill definitions and the agent-instruction prose they load:
  a skill's `references/` nodes and any shared instruction file a repo keeps
  outside a skill.
- `review-agent` — agent definitions.
- `review-design` — the living design graph under `docs/`. `edify:corrector`
  reviews it with `craft:design-doc-writing` named in the prompt as its criteria
  source, as the agent row names `plugin-dev:agent-development`; when `craft` is
  absent, the report notes the fallback, as for `plugin-dev`.
  `edify:design-corrector` is not this row's reviewer: it reviews
  `plans/<job>/design.md`, a planning artifact.

A file kind is always classed into an existing row, never a new group. The rule
is stated once, in `dispatch-composition.md` §Naming and resumption, and
`finishing.md` §1 step 2 groups by it. edify's `plugin/fragments/` is such a
shared instruction file, and was leg 6's `review-fragments`; the text `/build`
ships names the class, not the directory.

**KD-6 — A changed-files list is the committed diff since the base, minus the
exempt paths and the job's own record, and one script produces it.** m1, m2,
m18. The `HEAD` form keeps uncommitted exempt dirt out. It does not keep out the
exempt paths that a `/handoff` or memory-pointer commit lands during the run.
Those are not the run's work, so the list drops them, as `verify-step.sh` does.
It also drops `plans/<job>/`: the run's reports and `runbook.md` list revisions
are its record, not its implementation.

`scripts/changed-files.sh <job>` derives the base per KD-1, prints
`BASE: <sha>`, then prints the diff with those paths removed. With no committed
item report it exits 1 with `NO-BASE:`. `changed-files.sh <job> --phase`
implements KD-2 instead: its base is the latest commit in `<run base>..HEAD`
touching `plans/<job>/reports/phase-*-corrector.md`, or the run base when no
boundary has landed, and the list is the same filtered diff since that base. The
exempt alternation moves to one sourced file, `scripts/exempt-paths.sh`, which
it and `verify-step.sh` both read. Every site that needs the list or the base
calls the script; `triage-feedback.sh` takes its `BASE:` and its two diffs take
the same `<base> HEAD` form. `review-requirement.md` keeps the working-tree form
for `/review` of uncommitted work, and names the `/build` form separately.

Rejected: the query and the regex spelled out in prose at each site (four sites,
and a prose copy of a script's regex drifts).

**KD-7 addendum — rename lines.** F-3. build-defects KD-7's "in any porcelain
state" excludes `R` and `C` lines, even when both sides are exempt paths. Such a
line fails closed as DIRTY. That is deliberate, because an `old -> new` line is
two paths that one match cannot judge. The script comment already says so; this
records it in the design.

**KD-8 — `/build` commit subjects name the job.** Every `/build` commit uses one
of these subjects:

- `<type>: <job> Item N.M[/k] — <title>` for items and slices, including
  code-review and list-revision commits
- `<type>: <job> Phase P boundary`
- `<type>: <job> Review gate`
- `<type>: <job> Finish`

This is for a human reading `git log`, and to keep two jobs' commits apart.
Nothing mechanical keys on the subject: resume, inventory and base read report
history (KD-1, KD-2). The commit-msg hook rewrites only the type prefix.

## Items

- Item 1.1: `tests/test_verify_step_exemption.py` — pin the exemption's
  porcelain states and its single-level globs. Requirements: Major 6, F-4. The
  tests landed in that module, split from `tests/test_verify_step.py` to keep
  each under its line cap (revised after the fact by
  `plans/review-fixes-2/` Item 3.4). The script already
  behaves, so each slice's RED is a mutation red. The mutant is a copy of the
  script with the test module's `SCRIPT` rebound. The tracked file is never
  reverted. Fixtures are the module's existing `_init_repo` and `_stub_just`.
  This item lands before Item 1.2 extracts the alternation, so its tests guard
  that extraction; its mutants edit `verify-step.sh` as it stands then. Slices:
  1. `test_exempt_paths_clean_in_any_porcelain_state`. The repo holds these
     exempt states and nothing else:
     - staged add `A  .claude/handoff-new.md`
     - staged delete `D  inbox/old.md`
     - worktree delete ` D .claude/handoff-task.md`
     - unmerged `UU inbox/conflict.md`, from a two-branch conflict on that
       tracked file

     Assert exit 0 and stdout starting `CLEAN:`. The mutant restricts both XY
     columns to `[ M?]`.
  2. `test_nested_path_under_exempt_dir_is_dirty`. Untracked `inbox/sub/x.md`
     and `.claude/handoff-dir/x.md` give exit 1, and the DIRTY listing carries
     both `??` lines. The mutant widens both `[^/]+` to `.+`.

- Item 1.2: `plugin/skills/build/scripts/changed-files.sh` and
  `scripts/exempt-paths.sh`, a sourced file holding the exempt alternation;
  `verify-step.sh` sources it too (KD-6). Requirements: Major 1, m1, m2, m18.
  The tests go in a new `tests/test_changed_files.py`, with fixtures modelled on
  `test_verify_step.py`'s `_init_repo`. RED is stub-then-assert: an inert script
  that exits 0 and prints nothing. Load `shell-scripting:shell-gotchas` (recall
  `macos-gate-target`). Slices:
  1. `test_base_is_parent_of_first_item_report_commit`. The repo holds a pre-run
     commit P that adds `plans/j/reports/outline-review.md`, then a commit
     adding `plans/j/reports/item-1-1.md` and `a.txt`, then a commit adding
     `item-1-2.md` and changing `b.txt`. Assert the first line is `BASE: <P>`
     and the list is exactly `a.txt` and `b.txt`.
  2. `test_exempt_paths_committed_in_the_run_are_dropped`. A run commit also
     touches `inbox/x.md`, `.claude/handoff-task.md` and a file named `memory`.
     None of them appears in the list.
  3. `test_no_item_report_exits_1`. No `item-*` report is committed: exit 1,
     stdout starting `NO-BASE:`.

  Interfaces:
  - `changed-files.sh <job> [--phase]` → exit 0: `BASE: <sha>`, then one path
    per line. Exit 1: `NO-BASE:`, for a repo with commits and no committed
    item report. Exit 2: `ERROR:` on usage or git failure, an unborn `HEAD`
    included (revised after the fact by `plans/review-fixes-2/` Item 3.4).
    Paths are read from a NUL-delimited diff, never split on whitespace.
    `--phase` takes the phase base (Item 1.4).
  - `verify-step.sh` → unchanged verdicts, its exempt pattern composed from
    `exempt-paths.sh`.

- Item 1.3: `plugin/bin/triage-feedback.sh` — both diffs take
  `"$baseline_commit" HEAD` (KD-6). Requirements: m18. Its interface is
  unchanged; `finishing.md` §2 passes `changed-files.sh`'s `BASE:`. The tests go
  in `tests/test_triage_feedback.py`, on its existing fixtures. Slices:
  1. `test_files_changed_counts_committed_changes_only`. After the baseline, one
     commit changes `a.txt`, and tracked `b.txt` is modified but left
     uncommitted. Assert stdout carries `- Files changed: 1`.
  2. `test_uncommitted_definition_is_not_behavioral`. The committed change is
     plain text. An uncommitted edit adds a `def foo():` line to a tracked `.py`
     file. Assert `Behavioral code: no`.

- Item 1.4: `changed-files.sh <job> --phase`, added at Item 2.3 by my human
  partner's ruling. The base is the latest commit in `<run base>..HEAD` touching
  `plans/<job>/reports/phase-*-corrector.md` (KD-2's path rule, never the commit
  subject, per KD-8). If no commit matches, the base is the run base (KD-1). It
  prints `BASE: <that sha>` and the same filtered list since that base. Without
  `--phase` nothing changes. Slices 1–3's tests landed in
  `tests/test_changed_files_phase.py`, split from `tests/test_changed_files.py`
  to keep each under its line cap, and slice 4's in `tests/test_verify_step.py`
  (revised after the fact by `plans/review-fixes-2/` Item 3.4). Slices:
  1. `test_phase_without_boundary_gives_run_base` — no boundary landed, so
     `--phase` gives the run base.
  2. One boundary landed: the base is that boundary commit, and only later files
     are listed.
  3. The exempt-path and `plans/<job>/` filters still apply under `--phase`.
  4. The `core.quotePath` regression test from the 1.1/2 code review: repo-local
     `core.quotePath false` and an untracked `inbox/x\377/y.md` make
     `verify-step.sh` exit 1. Skipped on macOS. It pins an existing fix, so its
     RED is a mutation red, as in Item 1.1.

- Item 2.1: `plugin/skills/build/SKILL.md`. Requirements: Major 1, Major 4,
  Major 7 (§4.1), m16.
  - §1: KD-1's test — an `item-*` report on disk → resumed. No STOP.
  - §2: delete the baseline capture.
  - §4.1: edit, `just precommit`, review the uncommitted diff (self-review, or
    the `item-N-M` corrector), write or take `item-N-M.md`, then one commit
    `<type>: <job> Item N.M — <title>` carrying edits, fixes and report (KD-1,
    KD-8). §4.4's "§4.1's corrector once its commit lands" follows.
  - §5: `review-skip.md` is committed at `finishing.md` §1's report commit
    (KD-4).
  - §6: delete the 2-level paragraph, which repeats `escalation.md`
    §Escalation's opening word for word. Keep the pointer. The hub must end
    below 200 lines, since a file parked at its cap no longer signals (recall
    `line-caps`).

- Item 2.2: `plugin/skills/build/references/escalation.md`. Requirements: Majors
  1, 2, 5; (a); m5, m6, m7.
  - Exit-1 bullet: at the entry gate, the mask re-run's verdict goes back to
    `SKILL.md` §2's STOP. Remediation is only for a verdict after an item (m5).
  - §Post-item remediation per KD-3's live-run chain: the resume message asks
    the agent to finish and commit its work by name; a fresh dispatch composed
    from the item replaces the mechanical artisan; escalation hands my human
    partner the listing and findings.
  - Closing paragraph: KD-3's per-path decision and one-call revert replace the
    `git checkout -- . && git clean -fd` sentence; the rule at `:31` narrows to
    "never on its own judgement".
  - "Agent never returns": if the check finds the report written or the commit
    landed, treat the agent as returned. If the resume produces the report,
    proceed (m7).
  - §Resuming: KD-1's test replaces the reports-exist sentence and the
    "invocation says so" wording; the base comes from `changed-files.sh`; step
    1's inventory reads report history and KD-2's boundary rule; step 2 becomes
    KD-3's examine-and-adopt, with the tdd limit.

- Item 2.3: `plugin/skills/build/references/phase-boundary.md`. Requirements:
  Major 2, m1, m3.
  - Base resolution: `changed-files.sh <job> --phase` at every boundary; its
    `BASE:` is the phase base. KD-2's report-path rule is the definition
    `--phase` implements (Item 1.4).
  - The changed-files list comes from `changed-files.sh` (KD-6), which corrects
    the "exempt paths stay out" claim.
  - UNFIXABLE is validated by `review-requirement.md` §UNFIXABLE Detection
    Protocol before it stops the run. The boundary commit comes after the
    resumed corrector has reviewed the fix (m3).
  - The boundary commit's subject is `<type>: <job> Phase P boundary` (KD-8).

- Item 2.4: `plugin/skills/build/references/finishing.md`. Requirements: Major
  4, (c), m1, m4.
  - §1 step 1: `changed-files.sh` (KD-6), which corrects the claim that "no
    commit carries those".
  - §1 step 2: group by KD-5's rows and slugs.
  - §1 report commit: add `review-skip.md` when review was skipped (KD-4);
    subject `<type>: <job> Review gate`.
  - Structural proof: validation of a report-only UNFIXABLE resumes
    `review-<group>` by name for reclassification. The protocol names
    "corrector" for this step (m4).
  - §2: the base is `changed-files.sh`'s `BASE:`.
  - §3: the closing commit, subject `<type>: <job> Finish`, and `verify-step.sh`
    exit 0 before the run summary (KD-4).

- Item 2.5: `plugin/skills/build/references/review-dispatch-template.md`.
  Requirements: Major 1, m4, m11, m19.
  - §Field Rules, Baseline: `changed-files.sh`'s `BASE:`.
  - §Report-only variant:
    - Ask for UNFIXABLE with its subcategory code (U-REQ, U-ARCH or U-DESIGN)
      and a three-gate investigation summary, which is what the protocol
      validates (m4).
    - Allow a `blocked: <reason>` return (m19).
  - §Example: say that it shows the fix-capable template used when `plugin-dev`
    is not installed (m11).

- Item 2.6: `plugin/skills/build/references/dispatch-composition.md`.
  Requirements: (c), m8, m10.
  - §Naming and resumption: KD-5's four slugs and the class rule; `item-N-M`
    also names §4.1's self-review report. `final-review` is the §3.1 closing
    corrector, for a skipped review or an unreviewed group (m10).
  - §Prompt contents item 4: the matchable part becomes `<job> Item N.M/k`, a
    label only (KD-8).
  - §Prompt contents item 5: a part ending in neither `CONTINUED` nor
    `END OF REPORT` is truncated. Resume the reviewer for the rest of that part
    (m8).

- Item 2.7: `plugin/skills/build/references/tdd-slice.md`. Requirements: Major
  3, m14.
  - §After the slice, steps 1 and 3: `git commit -- <paths>` (KD-4), with KD-8's
    subjects.
  - Step 1: "the same step §5 takes at a phase boundary" becomes §4.5's.

- Item 2.8: `plugin/fragments/escalation-acceptance.md`. Requirements: Major 5,
  (a), m13, and the review's recovery-copy minor.
  - §Required and §Verification sequence: a clean tree is `/build`'s
    `verify-step.sh` exit 0, which tolerates the three exempt paths. It is not
    an empty `git status --porcelain` (m13).
  - §Rollback protocol: an uncommitted failed fix escalates; a revert happens
    only on my human partner's decision, by name (KD-3), never by
    `git checkout -- .`.
  - §Dirty tree recovery: reduce it to the pointer at `escalation.md` §Post-item
    remediation. Its second copy has already drifted.

- Item 2.9: `plugin/fragments/review-requirement.md`. Requirements: m2, (c).
  - §Execution Context, Changed files: the `/build` form is `changed-files.sh`'s
    (KD-6), and the working-tree form is for `/review` only.
  - Routing table: the skill row covers `references/` nodes and shared
    instruction files; the design row becomes the `docs/` design graph, reviewed
    by `edify:corrector` with `craft:design-doc-writing` as its criteria source,
    and the `craft`-absent fallback joins the `plugin-dev` paragraph (KD-5).

- Item 2.10: `plugin/agents/tdd-auditor.md` §Inputs. Requirements: m15. "Phase
  checkpoints" becomes "Phase boundaries". Any subject matching it prescribes
  takes KD-8's form.

- Item 2.11: `plugin/README.md` §Scripts. Requirements: m17.
  - The `verify-step.sh` call sites are every committing dispatch: GREEN, code
    review, a review item, §4.1's commit, the phase-boundary commit, the review
    gate and §3's closing commit.
  - Add `changed-files.sh` and `exempt-paths.sh`.

- Item 2.12: `docs/references/pipeline-contracts.md`, the D-86 argument.
  Requirements: m17. "which tolerates nothing but ` M memory`" goes into the
  past tense, since it describes the script at the time of the defect.

- Item 2.13: `plugin/agents/test-driver.md`, `plugin/agents/refactor.md`, and
  any other file prescribing a `/build` commit subject — KD-8's form. The
  executor finds them by grepping `Item N.M` and `<type>:` over `plugin/`.

- Item 2.14: `docs/references/pipeline-contracts.md` and `docs/decisions.md` —
  record KD-1, KD-2, KD-3, KD-5, KD-6, KD-8 and build-defects KD-7 as decisions:
  the argument in the node, the conclusion line and its rejected alternatives in
  the index. Load `craft:design-doc-writing`.

- Item 2.15: `plugin/portable.just` and `justfile` — make `just lint` agree with
  `precommit` on `tests/line_limits_helpers.py:32`, added at leg 2 by my human
  partner's ruling. `lint` passes `--ignore=PLR0913`, so that line's
  `# noqa: PLR0913` reads as unused there (RUF100), while `precommit` enables
  PLR0913. Remove `PLR0913` from `run-lint-checks`' `ruff_ignores` and leave the
  rest of that list unchanged. Never ignore RUF100. If removing it surfaces
  PLR0913 hits under `just lint` that `precommit` does not already flag, stop
  and report them; add no suppressions. `justfile`'s prolog carries its own copy
  of `run-lint-checks`, which overrides the imported one, so both copies change.

## Scope

IN: the files the items name. That is four scripts (`verify-step.sh`,
`triage-feedback.sh`, and the new `changed-files.sh` and `exempt-paths.sh`),
three test files (`test_verify_step.py`, `test_triage_feedback.py`, and the new
`test_changed_files.py`), `build/SKILL.md`, six `build` references, two
fragments, `tdd-auditor.md`, `test-driver.md`, `refactor.md`,
`plugin/README.md`, `pipeline-contracts.md`, `docs/decisions.md`,
`plugin/portable.just` and `justfile`.

OUT:

- Major 7's generalisation, self-review before the commit everywhere after the
  superpowers example. A later session owns it, per the task frame. §4.1's own
  ordering is fixed here, because KD-1's report forces it.
- m12, the return-contract drift in `corrector.md`, `artisan.md`,
  `delegation.md` and `review-requirement.md`'s delegation template. It goes to
  defect 21, which owns the corrector edits whose allowlist ceilings are pinned.
  It rides that job's report-shape item.
- F-2, `memory` exempt in any state and not only as a gitlink. The exposure
  needs a dispatch that leaves a file named exactly `memory`. Accepted, and not
  routed.
- F-5, test subprocesses that inherit `GIT_DIR` and friends. The pattern is
  shared with `tests/review_range_helpers.py`, so it goes to the
  script-robustness job.
- F-6, the BSD behaviour of `[[:space:]]`. It is covered by the pending macOS
  `just test` run.
- The path form of every `plugin/…` pointer. New text copies the form its file
  already uses. That belongs to the repo-relative-paths job.
- The "D+B anchor" term. It is a repo-wide job.
