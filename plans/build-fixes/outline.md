# Outline — build-fixes

Second pass on `build-defects`: Majors 1–6 and 21 of the 25 minors of its
deliverable review, merged with the queued tdd job (a)(b)(c) from
`.claude/handoff-todo.md`. Finding IDs are the review's: `Major N` from
`plans/build-defects/reports/deliverable-review.md`, `mN` from
`deliverable-review-prose.md`, `F-N` from `deliverable-review-code-tests.md`.
`build-defects KD-N` means `plans/build-defects/outline.md`'s decision N.
Classification: `classification.md`.

## Provenance

- **Derived from:** `plans/build-defects/reports/deliverable-review.md`,
  superseding `plans/build-defects/outline.md`
- **Base:** `d444630c01bd98851cddbedde3fbc9b85c18345d`

## Key decisions

**KD-1 — A run is resumed exactly when its baseline file exists.** Major 1,
(b). The baseline moves to `tmp/build-baseline-<job>`, so two jobs no longer
share one file. The test for being resumed moves into `/build` §1, before the
entry gate, and it is mechanical: `tmp/build-baseline-<job>` exists → the run
is resumed and Reads `references/escalation.md` §Resuming before §2. When the
file is absent, the run is fresh, and §2 captures it. An invocation that says
"resume" when the file is absent → STOP and ask my human partner for the base
commit. Recapturing would drop every earlier item from the review gate, from
triage and from phase 1's base. `/deliverable-review` deletes the file once its
report is written, per my human partner's ruling on (b). Rejected: the
reports-exist test that `escalation.md` states today. The hub cannot reach it,
and "this run's reports" has no mechanical reading when a job directory holds
an earlier run's reports.

**KD-2 — A phase boundary has landed when this run holds a commit touching
its corrector report.** Major 2, my human partner's 2026-09-26 ruling. Phase P
has landed when `git log -1 --format=%H <baseline>..HEAD --
plans/<job>/reports/phase-<P>-corrector.md` prints a hash, and that hash is
phase P+1's base. Three choices follow from the query:

- The range `<baseline>..HEAD` excludes an earlier run's commit.
- Dropping `--diff-filter=A` counts a report the run modified rather than
  added.
- `-1` takes the latest commit, so a report committed twice resolves to one
  base, the one carrying the later fix.

An empty result during a live run means the boundary commit was skipped.
→ STOP. Never substitute an empty base: `git diff --name-only HEAD` is a
working-tree diff that passes the empty-field check with the wrong list.

On resume, the inventory covers boundaries as well as items. For each phase
whose items have all landed but whose boundary has not:

- **`phase-<P>-corrector.md` is absent** → the boundary review has not run.
  Run `references/phase-boundary.md` for P before phase P+1's first item.
- **The report is present, uncommitted and complete** → inspect the source to
  decide which of its fixes landed, because the corrector writes its report
  before it applies fixes. Apply the fixes that did not land in session.
  Then commit the report with every fix, landed and applied, as
  `phase-boundary.md` commits it. The fixes applied in session get no second
  review, the same bound as the report-only second pass.
- **The report is present but partial** → no fix was applied, for the same
  reason. Delete the report and run the boundary.

A report is complete when it carries every section of `corrector.md` §4's
template through `## Fixes Applied`. The sections after it are conditional or
optional there.

**KD-3 — Reverting dirt is a mode of `verify-step.sh`, bound to the listing
my human partner confirmed.** Major 5, (a), m6. This decision succeeds
build-defects KD-5 and keeps its chain unchanged: resume the owning agent,
then dispatch a fresh `edify:artisan`, then escalate. What changes is the
final step. The unconfirmed `git checkout -- . && git clean -fd` and the
§Rollback `git checkout -- .` are gone.

When `/build` escalates a dirty tree to my human partner, the orchestrator:

1. Shows the `DIRTY:` listing.
2. On confirmation, runs `verify-step.sh --revert <token>`.
3. Runs `verify-step.sh` again.

The orchestrator is the actor, and only after that confirmation.

- **Token.** A `DIRTY:` verdict ends with `REVERT-TOKEN: <hash>`, which is
  `git hash-object --stdin` over the listing lines exactly as printed. Revert
  mode recomputes the listing and proceeds only when it hashes to the token.
  Otherwise it touches nothing and prints `STALE:` with the current listing and
  its new token. The token keeps the revert from touching dirt nobody saw: a
  dispatch's late write, or a sandbox mask that appears between the listing and
  the revert (recall `sandbox-effects`). `git hash-object` is used because it
  is the same everywhere git is; `sha1sum` and `shasum` split between GNU and
  macOS.
- **Revert.** Paths tracked in `HEAD` or in the index go to
  `git restore --source=HEAD --staged --worktree`. That one command reverts
  added, modified, deleted and renamed paths (probed on git 2.47.3). `??` paths
  are removed. Exempt paths are never touched. The script takes paths from a
  NUL-delimited status, never by unquoting the printed listing.
- **Resumed agents.** An agent resumed to revert its own work reverts the
  paths it wrote, by name. It never runs `git checkout -- .` or
  `git clean -fd`.

Rejected: a revert that recomputes the set with no token. It would revert
whatever is dirty at run time, and "exactly the set the listing reports" would
hold only when nothing moved in between.

**KD-4 — Every orchestrator commit uses `git commit -- <paths>`, and no gate
runs over an uncommitted artifact of an earlier step.** Majors 3, 4.
build-defects KD-7's safety argument covers only the commits made in that form.
This job adds the two missing sites:

- `tdd-slice.md` §After the slice: the code-review commit and the `runbook.md`
  list-revision commit.
- `finishing.md`: the report commit of §1 takes `review-skip.md` too when
  review was skipped. §3 closes with one commit before the run summary. It
  carries the triage log line (`plans/reports/triage-feedback-log.md`),
  `final-review`'s report and fixes, and `tdd-audit.md`. `verify-step.sh` must
  then exit 0.

**KD-5 — Review-gate groups are the routing table's rows, with fixed slugs.**
(c), m9. There are four slugs, one per row of `review-requirement.md`'s
routing table:

- `review-code` — code, tests, plans
- `review-skill` — skill definitions
- `review-agent` — agent definitions
- `review-design` — design documents

A file kind that no row names goes to the row marked Default, `review-code`,
and never to a new group. edify's `plugin/fragments/` is such a kind, which is
where leg 6's `review-fragments` came from. The rule is stated once, in
`dispatch-composition.md` §Naming and resumption. `finishing.md` §1 step 2
groups by those rows and points there.

**KD-6 — A changed-files list is `git diff --name-only <base> HEAD` minus the
exempt paths.** m1, m2, m18. The `HEAD` form keeps uncommitted exempt dirt out.
It does not keep out the exempt paths that a `/handoff` or memory-pointer
commit lands during the run. Those are not the run's work, so the list drops
them, as `verify-step.sh` does. `triage-feedback.sh`'s two diffs take the same
`<base> HEAD` form. `review-requirement.md` keeps the working-tree form for
`/review` of uncommitted work, and it names the `/build` form separately.

**KD-7 addendum — rename lines.** F-3. build-defects KD-7's "in any porcelain
state" excludes `R` and `C` lines, even when both sides are exempt paths. Such
a line fails closed as DIRTY. That is deliberate, because an `old -> new` line
is two paths that one match cannot judge. The script comment already says so;
this records it in the design.

## Items

- Item 1.1: `tests/test_verify_step.py` — pin the exemption's porcelain states
  and its single-level globs. Requirements: Major 6, F-4. The script already
  behaves, so each slice's RED is a mutation red. The mutant is a copy of the
  script with the test module's `SCRIPT` rebound. The tracked file is never
  reverted. Fixtures are the module's existing `_init_repo` and `_stub_just`.
  Slices:
  1. `test_exempt_paths_clean_in_any_porcelain_state`. The repo holds these
     exempt states and nothing else:
     - staged add `A  .claude/handoff-new.md`
     - staged delete `D  inbox/old.md`
     - worktree delete ` D .claude/handoff-task.md`
     - unmerged `UU inbox/conflict.md`, from a two-branch conflict on that
       tracked file

     Assert exit 0 and stdout starting `CLEAN:`. The mutant restricts both
     XY columns to `[ M?]`.
  2. `test_nested_path_under_exempt_dir_is_dirty`. Untracked
     `inbox/sub/x.md` and `.claude/handoff-dir/x.md` give exit 1, and the
     DIRTY listing carries both `??` lines. The mutant widens both `[^/]+` to
     `.+`.

- Item 1.2: `plugin/skills/build/scripts/verify-step.sh` — revert mode
  (KD-3). Requirements: Major 5, (a). The tests go in
  `tests/test_verify_step.py`, on the same fixtures. Load
  `shell-scripting:shell-gotchas` (recall `macos-gate-target`).
  Slices:
  1. `test_revert_restores_listed_dirt_and_keeps_exempt_dirt`. The repo
     holds a modified tracked `t.txt`, an untracked `my stray.txt` (git quotes
     it), an untracked `inbox/brief.md`, and a staged, modified
     `.claude/handoff-task.md`. A default run exits 1, and its last line
     matches `REVERT-TOKEN: [0-9a-f]{40}`. `--revert <that token>` exits 0,
     and stdout starts `REVERTED:`. Afterwards:
     - `t.txt` equals its committed content.
     - `my stray.txt` no longer exists.
     - `inbox/brief.md` and `.claude/handoff-task.md` keep their content and
       their porcelain lines.
  2. `test_revert_refuses_a_changed_listing`. Take the token, then create
     untracked `late.txt`. `--revert <token>` exits 1 with stdout starting
     `STALE:`. It lists both `?? late.txt` and the original lines, plus a new
     `REVERT-TOKEN:` that differs from the old one. Every dirty file is still
     present, unchanged.
  3. `test_revert_staged_add_and_rename`. A staged `A  new.txt` and a staged
     `R  t.txt -> moved.txt` → `--revert <token>` exits 0. `new.txt` and
     `moved.txt` are gone from the disk and the index. `t.txt` is restored,
     and `git status --porcelain` is empty.
  4. `test_revert_without_token_exits_2`. `--revert` alone exits 2, and stdout
     carries `ERROR:` and the usage line. The tree is untouched.

  Interfaces:
  - `verify-step.sh` → unchanged verdicts, except that a `DIRTY:` verdict
    ends with `REVERT-TOKEN: <40-hex>`, which is `git hash-object --stdin`
    over the listing lines as printed.
  - `verify-step.sh --revert <token>` → exit 0 `REVERTED:` plus the reverted
    lines. Exit 1 `STALE:` plus the current listing and its token, with
    nothing touched. Exit 2 `ERROR:` on usage or git failure. Revert mode never
    runs `just precommit`.

- Item 1.3: `plugin/bin/triage-feedback.sh` — both diffs take
  `"$baseline_commit" HEAD` (KD-6). Requirements: m18. The tests go in
  `tests/test_triage_feedback.py`, on its existing fixtures.
  Slices:
  1. `test_files_changed_counts_committed_changes_only`. After the baseline,
     one commit changes `a.txt`, and tracked `b.txt` is modified but left
     uncommitted. Assert stdout carries `- Files changed: 1`.
  2. `test_uncommitted_definition_is_not_behavioral`. The committed change is
     plain text. An uncommitted edit adds a `def foo():` line to a tracked
     `.py` file. Assert `Behavioral code: no`.

- Item 2.1: `plugin/skills/build/SKILL.md`. Requirements: Major 1, (b), Major
  4, m16.
  - §1: replace the resumed-run sentence with KD-1's test, including the STOP
    for a "resume" with no file.
  - §2: capture `tmp/build-baseline-<job>` when it is absent, and keep it
    otherwise.
  - §5: `review-skip.md` is committed at `finishing.md` §1's report commit
    (KD-4).
  - §6: delete the 2-level paragraph, which repeats `escalation.md`
    §Escalation's opening word for word. Keep the pointer. The hub must end
    below 200 lines, since a file parked at its cap no longer signals (recall
    `line-caps`).

- Item 2.2: `plugin/skills/build/references/escalation.md`. Requirements:
  Majors 1, 2, 5; (a), (b); m5, m6, m7.
  - Exit-1 bullet: at the entry gate, the mask re-run's verdict goes back to
    `SKILL.md` §2's STOP. Remediation is only for a verdict after an item
    (m5).
  - The resume message tells the agent to revert only the paths it wrote, by
    name, and never to run `git checkout -- .` or `git clean -fd` (KD-3).
  - Closing paragraph: KD-3's final step replaces the `git checkout -- . &&
    git clean -fd` sentence. Name the actor, the confirmation and the
    handling of `STALE:`.
  - "Agent never returns": if the check finds the report written or the
    commit landed, treat the agent as returned. If the resume produces the
    report, proceed (m7).
  - §Resuming: KD-1's test replaces the reports-exist sentence, with the
    per-job baseline. Step 3's inventory takes KD-2's boundary rule.

- Item 2.3: `plugin/skills/build/references/phase-boundary.md`. Requirements:
  Major 2, (b), m1, m3.
  - Base resolution per KD-2: phase 1 from `tmp/build-baseline-<job>`, and
    empty → STOP.
  - Changed-files list per KD-6, which corrects the "exempt paths stay out"
    claim.
  - UNFIXABLE is validated by `review-requirement.md` §UNFIXABLE Detection
    Protocol before it stops the run. The boundary commit comes after the
    resumed corrector has reviewed the fix (m3).

- Item 2.4: `plugin/skills/build/references/finishing.md`. Requirements:
  Major 4, (b), (c), m1, m4.
  - §1 step 1: the per-job baseline and KD-6's list, which corrects the claim
    that "no commit carries those".
  - §1 step 2: group by the routing rows, with the slugs of KD-5.
  - §1 report commit: add `review-skip.md` when review was skipped (KD-4).
  - Structural proof: validation of a report-only UNFIXABLE resumes
    `review-<group>` by name for reclassification. The protocol names
    "corrector" for this step (m4).
  - §2: the per-job baseline.
  - §3: the closing commit and `verify-step.sh` exit 0 before the run summary
    (KD-4).

- Item 2.5: `plugin/skills/build/references/review-dispatch-template.md`.
  Requirements: (b), m4, m11, m19.
  - §Field Rules, Baseline: the per-job file.
  - §Report-only variant:
    - Ask for UNFIXABLE with its subcategory code (U-REQ, U-ARCH or U-DESIGN)
      and a three-gate investigation summary, which is what the protocol
      validates (m4).
    - Allow a `blocked: <reason>` return (m19).
  - §Example: say that it shows the fix-capable template used when
    `plugin-dev` is not installed (m11).

- Item 2.6: `plugin/skills/build/references/dispatch-composition.md`.
  Requirements: (c), m8, m10.
  - §Naming and resumption: KD-5's four slugs and the default-row rule.
    `final-review` is the §3.1 closing corrector, for a skipped review or an
    unreviewed group (m10).
  - §Prompt contents item 5: a part ending in neither `CONTINUED` nor
    `END OF REPORT` is truncated. Resume the reviewer for the rest of that
    part (m8).

- Item 2.7: `plugin/skills/build/references/tdd-slice.md`. Requirements:
  Major 3, m14.
  - §After the slice, steps 1 and 3: `git commit -- <paths>` (KD-4).
  - Step 1: "the same step §5 takes at a phase boundary" becomes §4.5's.

- Item 2.8: `plugin/fragments/escalation-acceptance.md`. Requirements: Major
  5, (a), m13, and the review's recovery-copy minor.
  - §Required and §Verification sequence: a clean tree is `/build`'s
    `verify-step.sh` exit 0, which tolerates the three exempt paths. It is not
    an empty `git status --porcelain` (m13).
  - §Rollback protocol: an uncommitted failed fix is reverted by KD-3's
    confirmed revert, not by `git checkout -- .`.
  - §Dirty tree recovery: reduce it to the pointer at `escalation.md`
    §Post-item remediation. Its second copy has already drifted.

- Item 2.9: `plugin/fragments/review-requirement.md` §Execution Context,
  Changed files. Requirements: m2. The `/build` form is KD-6's, and the
  working-tree form is for `/review` only.

- Item 2.10: `plugin/skills/deliverable-review/SKILL.md` Phase 4. Requirements:
  (b). Once the report is written, delete `tmp/build-baseline-<plan>` where it
  exists (KD-1). The file is at 198 of its 200 lines. Fold the step into the
  write sentence rather than adding a paragraph.

- Item 2.11: `plugin/agents/tdd-auditor.md` §Inputs. Requirements: m15.
  "Phase checkpoints" becomes "Phase boundaries".

- Item 2.12: `plugin/README.md` §Scripts. Requirements: m17, (a).
  - The `verify-step.sh` call sites are every committing dispatch: GREEN, code
    review, a review item, §4.1's corrector, the phase-boundary commit, the
    review gate and §3's closing commit.
  - Add the `--revert <token>` mode.

- Item 2.13: `docs/references/pipeline-contracts.md`, the D-86 argument.
  Requirements: m17. "which tolerates nothing but ` M memory`" goes into the
  past tense, since it describes the script at the time of the defect.

## Scope

IN: the files the items name. That is two scripts, two test files,
`build/SKILL.md`, five `build` references, two fragments,
`deliverable-review/SKILL.md`, `tdd-auditor.md`, `plugin/README.md` and
`pipeline-contracts.md`.

OUT:

- Major 7, the self-review in §4.1 after the commit. A later session owns it,
  per the task frame.
- m12, the return-contract drift in `corrector.md`, `artisan.md`,
  `delegation.md` and `review-requirement.md`'s delegation template. It goes
  to defect 21, which owns the corrector edits whose allowlist ceilings are
  pinned. It rides that job's report-shape item.
- F-2, `memory` exempt in any state and not only as a gitlink. The exposure
  needs a dispatch that leaves a file named exactly `memory`. Accepted, and
  not routed.
- F-5, test subprocesses that inherit `GIT_DIR` and friends. The pattern is
  shared with `tests/review_range_helpers.py`, so it goes to the
  script-robustness job.
- F-6, the BSD behaviour of `[[:space:]]`. It is covered by the pending macOS
  `just test` run.
- The path form of every `plugin/…` pointer. New text copies the form its file
  already uses. That belongs to the repo-relative-paths job.
- The "D+B anchor" term. It is a repo-wide job.

## Open questions

- **Q-1 — The design graph never recorded build-defects' decisions.** No node
  in `docs/references/` carries build-defects KD-5 or KD-7, the successor
  KD-3 above, or KD-1's resume test. `pipeline-contracts.md` is the natural
  node. Default: out of this job, add a task-frame item for a docs pass after
  `/build`. What would settle it: my human partner wanting them recorded in
  this job instead.
