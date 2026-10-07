# Outline — review-fixes-3

Fourth pass on the `/build` run-state work. It covers the 18 minors of
`review-fixes-2`'s round-3 deliverable review. Goal: round 4 comes back clean.
Finding IDs are the review's (m1–m18, from
`plans/review-fixes-2/reports/deliverable-review.md`; the per-axis
sub-reports beside it carry the probes). `review-fixes-2 KD-N` means
`plans/review-fixes-2/outline.md`'s decision N. Classification:
`classification.md`.

**Verification against HEAD.** Only `5775ac00` landed after the review, and it
touches none of the eighteen sites. Each finding was re-read at its site and
reproduces as written. None is already fixed, and none has a false premise.
m3's premise holds, and my human partner ruled its fix: a bound stated in
D-90, no code change. The 2026-10-06 changelog entry repeats the re-run claim
(its line 24). Dated entries are write-time records, so it stays as written,
and the ruling scopes the fix to D-90.

## Provenance

- **Derived from:** `plans/review-fixes-2/reports/deliverable-review.md`
- **Base:** this job's own run base, from its first item report (D-88)

## Key decisions

**KD-1 — A planning artifact on the review gate's list is dispatched as
`review-plan-<source job>-<stem>` (m12).** `<source job>` is the directory the
artifact sits in, and `<stem>` is `design`, `outline` or `runbook`. For
`plans/build-fixes/outline.md` on this job's list, that gives
`review-plan-build-fixes-outline`. The report path follows from the name, as
`dispatch-composition.md` §Prompt contents item 5 rules for every dispatch:
`plans/<job>/reports/review-plan-<source job>-<stem>.md`, under the running
job. That is the one rule for report paths, whatever default the agent's own
definition carries. The name is fixed by four constraints:

- It matches `review-*.md`, so the gate's landed check (`finishing.md` §1),
  triage's Reports exclusion and its `Review artifact` probe all read it as a
  review report.
- It collides with none of the four group slugs. A planning `design.md` named
  `review-design` would collide with the design-graph row.
- It is not the agent's default. `outline-review.md` overwrites a job's own
  planning report.
- It is unique per artifact. Two jobs' `outline.md` on one list get two
  names, which `review-plan-<stem>` would not.

The list never holds the running job's own plan, because it drops
`plans/<job>/`, so `<source job>` is always another job.

**KD-2 — The finishing stages' landed checks and triage's one row per
evidence become positive decisions (m16).** D-89 widens from the phase
boundary to every stage keyed on a report path.

- D-89's conclusion becomes: a phase boundary or a finishing stage has landed
  when the run holds a commit touching its report.
- The body adds the finishing stages, as `finishing.md` runs them:
  - the review gate lands on a `review-*.md` report, `review-skip.md`
    included, committed after the run's last item-report commit;
  - the final review lands on `final-review.md`;
  - the TDD audit lands on `tdd-audit.md`.
- D-90 states review-fixes-2 KD-2 as a sentence of its own: triage commits no
  report, so it has no landed check, and its log appends at most one row per
  evidence. A row equal to the new one past the date column skips the append.

The Rejected entry "A landed check on triage keyed on the triage log" then
stands against a decision the node states. A new D-95 was the alternative.
It is not taken, because the finishing stages share D-89's mechanism and the
row rule already lives in D-90's triage paragraph.

**KD-3 — `classification.md` opens with one bare job-level label (m15).**
`/design`'s triage persists a file whose first `Classification:` line is the
job's. Its value is exactly one of `Simple`, `Moderate`, `Complex` or
`Defect`, with nothing after it. Per-item blocks follow it for a composite
job. A composite job's label is its most demanding item's class, in the order
Simple < Moderate < Complex, because triage measures the whole run's evidence
against that one label. `Defect` is the job-level label only when every item
is a Defect. My human partner accepted this rule at the outline gate. The
ordering, Simple < Moderate < Complex with Defect only when every item is
one, is ungrounded: no calibration data backs it. The triage log is where
that data would come from, once composite jobs have logged rows.

**KD-4 — `changed-files.sh` prints nothing on a failure exit but `ERROR:`
(m2).** The list is built in full before `BASE:` prints. A diff that fails
part-way then leaves stdout holding the `ERROR:` line alone, which makes
review-fixes-2 Item 1.5's "an exit 2 prints `ERROR:` first" true, instead of
retracting it in D-90.

**KD-5 — Every triage failure arm gets a test, the behavioural grep's
included (m4).** This reverses review-fixes-2 KD-1's m5 exemption ("no test
pins it; the code review checks the form"). That exemption rested on fault
injection being out of reach, and the suite already injects faults with a
`PATH` shim (`test_failing_reports_diff_is_an_error_not_none`). The reversal
is the review's own finding m4, inside the m1–m18 scope, not a reopened
ruling.

**KD-6 — Triage changes to the repository root itself (m1).** It reads
`git rev-parse --show-toplevel`, as `changed-files.sh` does, and changes
there before it runs `changed-files.sh`. Every pathspec, `classification.md`,
`reports_dir` and the log path are then root-relative, from any CWD in the
work tree. The script's own directory is resolved to an absolute path before
the change, because a relative `BASH_SOURCE` would break after it. A
`rev-parse` or `cd` failure exits 2 with one `ERROR:` line, before
`changed-files.sh` runs.

**KD-7 — Every `git log` whose output `/build` reads passes
`--no-show-signature` (m14).** The finding names `phase-boundary.md`, D-89
and `tdd-auditor.md` check 2. The same reasoning reaches three more sites:

- `tdd-slice.md`'s query for the GREEN commit (a count);
- `escalation.md` §Resuming step 1 ("prints a hash");
- D-88's base query, which mirrors the script, which already passes the flag.

D-88 states the reason once: a user's `log.showSignature` prints
verification lines ahead of the shas. The other sites carry the flag only.
KD-7 covers `git log` commands carrying `--format=%H`, whose output is a hash
list that the reader compares, counts or tests for emptiness.
`tdd-auditor.md` §Inputs names `git log` forms only as permitted tools, not
as commands to parse, so it is out.

**The claim is probed, not reasoned (my human partner's ruling).** At
planning time, on git 2.47.3, a repo-local SSH signing key
(`gpg.format=ssh`, `user.signingkey`, `gpg.ssh.allowedSignersFile`) produced
signed commits. With `log.showSignature=true`, `git log -1 --format=%H` put
`Good "git" signature for … with ED25519 key …` on stdout, ahead of the
hash. With `--no-show-signature` it printed the hash alone. A signed-commit
fixture is therefore feasible with `ssh-keygen` alone, and needs no gpg
agent or keyring. Item 2.4 turns this into a test.

The scripts already pass the flag, so no script reds. The unflagged commands
are in the prose, and the orchestrator runs them. Item 2.4's test therefore
runs the prose's own commands, extracted from the files, against a signed
history. Its red on the current prose is genuine.

**No changelog entry.** Nothing here reverses a decision or adds or drops a
requirement. KD-2 records what is already in force, and the rest are fixes.

## Items

The four groups are ordering only. Work routed to `/build` with no runbook has
no phase boundaries (`/build` §4.5), so `Depends on:` lines carry the order.
Every tdd item's RED runs against the scripts as they stand at its turn.

### Group 1 — test module splits (general)

- Item 1.1: split `tests/test_changed_files.py` on its exit-code seam.
  - Type: general
  - Requirements: m10
  - Files: `tests/test_changed_files.py`, new
    `tests/test_changed_files_errors.py`, `tests/test_changed_files_phase.py`,
    `tests/changed_files_helpers.py`
  - Contract:
    - `test_changed_files_errors.py` holds these four tests, bodies
      unchanged: `test_git_failure_is_error_not_no_base`,
      `test_no_item_report_exits_1`, `test_unsafe_job_name_is_a_usage_error`
      and `test_unloadable_exempt_paths_is_an_error_not_no_base`.
    - Each module docstring says what it holds. Each split module says it was
      split to keep each module under its line cap, as
      `test_changed_files_phase.py` does, and the hub points at both.
    - No `KD-N` remains in the three changed-files test modules or the
      helpers. Each becomes its durable ID:
      - build-fixes KD-1 → D-88;
      - KD-2 → D-89;
      - KD-6 → D-90, or D-91 where the citation is the exempt paths;
      - KD-8 → D-94.

      A citation with no D-ID says what it means instead.
    - "Item 1.2 reads the diff NUL-delimited" cites D-90. Any other
      `Item N.M` naming another plan's item takes the decision it implements.
      An `Item N.M` naming the fixture's own item commit stays.
    - The collected test count over the changed-files modules is the same
      before and after.
    - No docstring is shaved (recall `line-caps`). Summary lines stay at 70
      characters or fewer (recall `edify-docformatter-d205`).

- Item 1.2: split `tests/test_triage_feedback.py` on its failure seam, and
  fix the triage and verify-step docstrings.
  - Type: general
  - Requirements: m7, m8, m9
  - Files: `tests/test_triage_feedback.py`, new
    `tests/test_triage_feedback_failures.py`,
    `tests/test_triage_feedback_log.py`, `tests/verify_step_helpers.py`
  - Contract:
    - `test_triage_feedback_failures.py` holds
      `test_failing_reports_diff_is_an_error_not_none` and
      `test_no_base_is_an_error_with_no_log_row`, bodies unchanged. Its
      docstring says it holds the failure arms of the entry, the reports
      count and the classification parse. The behavioural-code and log
      failures stay in their own modules.
    - m7: the hub docstring names all three sibling modules, each with what
      it holds, and gives the reason for the split: each module stays under
      its line cap.
    - m8: `verify_step_helpers.py` points at
      `tests/triage_feedback_helpers.py` for the subprocess-run pattern.
    - m9: the log module's docstring says the *append* is skipped, not the
      run. The run still prints its evidence and verdict.
    - The collected test count over the triage modules is the same before
      and after, and no docstring is shaved.

### Group 2 — script behaviour and failure pins (tdd)

Load `shell-scripting:shell-gotchas` and `craft:test-discipline`. Comments
cite D-numbers, never an outline's KD.

- Item 2.1: `plugin/skills/build/scripts/changed-files.sh` prints `ERROR:`
  alone on a late diff failure (KD-4).
  - Type: tdd
  - Requirements: m2, m18
  - Depends on: Item 1.1
  - Files: `plugin/skills/build/scripts/changed-files.sh`,
    `tests/test_changed_files_errors.py`, `tests/changed_files_helpers.py`
    if the runner needs a `PATH` prepend
  - Slices:
    1. `test_late_diff_failure_prints_error_alone`. The run commit adds
       `item-1-1.md`, `a.txt` and `b.txt`. A `git` shim ahead on `PATH` runs
       the real git, and when its first argument is `diff`, exits 128 after
       the real command's output. Expect exit 2 and stdout exactly
       `ERROR: git diff failed`, with no `BASE:` line and no path. Today
       stdout holds `BASE:`, `a.txt` and `b.txt` above the error, so the red
       is genuine.

       GREEN's edit of the header comment states the order and reflows the
       D-90 paragraph at 80 columns, line 26 included (m18). The other lines
       over 80 in the file are code and stay.
  - Interfaces:
    - Exit 0: `BASE: <sha>`, then one path per line, unchanged.
    - Exit 1: `NO-BASE: …` alone.
    - Exit 2: `ERROR: <cause>` alone, with no `BASE:` line and no path.

- Item 2.2: `plugin/bin/triage-feedback.sh` measures from the repository root
  whatever the CWD (KD-6).
  - Type: tdd
  - Requirements: m1
  - Depends on: Item 1.2
  - Files: `plugin/bin/triage-feedback.sh`, `tests/test_triage_feedback.py`,
    `tests/triage_feedback_helpers.py` if the runner needs a relative
    invocation
  - Notes (list revision after 2.1/1):
    - The script must still parse and pass under bash 3.2: GREEN and the
      code review run `bash -n` and the triage suite with a bash 3.2.57
      binary first on `PATH` where one is available. Slice 2.1/1's code
      review found a bare `case` pattern inside `$(…)` that bash 3.2 reads
      as the substitution's end, which the Linux suite did not catch.
  - Slices:
    1. `test_subdirectory_run_measures_the_repository_root`.
       - Fixture:
         - before the base, a committed `sub/keep.txt`;
         - `classification.md` holds `- **Classification:** Simple`;
         - the run commit adds `item-1-1.md`, `item-1-1-s1-red.md` and
           `a.py` holding `def foo():`.
       - Run the script by its path relative to `repo/sub`, with CWD
         `repo/sub`.
       - Expect:
         - `- Files changed: 1`, `- Reports: 1`, `- Behavioral code: yes`;
         - verdict `underclassified` and exit 0;
         - one row in `repo/plans/reports/triage-feedback-log.md`;
         - no `repo/sub/plans`.

       Today it reads `Reports: 0`, `Behavioral code: no` and
       `no-classification`.
    2. `test_outside_a_work_tree_is_one_error_line`. CWD is a directory in
       no work tree, with `GIT_CEILING_DIRECTORIES` set to its parent.
       Expect:
       - exit 2;
       - stdout exactly one line, starting `ERROR:`, and no
         `changed-files.sh exited` text;
       - nothing created under the CWD.

       Today stdout carries `changed-files.sh`'s line and triage's second
       one.

       List revision after 2.2/1: slice 2 gains
       `test_cdpath_does_not_move_the_script_dir`. 2.2/1's code review
       found that an exported `CDPATH` made `cd "$script_dir"` print the
       destination into the capture, and fixed it with `unset CDPATH`.
       Nothing pins that fix. CDPATH applies only to a path not starting
       with `/`, `.` or `..`, so the run invokes the script as
       `plugin/bin/triage-feedback.sh`, through a `plugin` symlink at the
       fixture's root, with CWD the root and `CDPATH=.` in the environment.
       Expect slice 1's evidence, verdict, row and exit 0. The behaviour
       exists, so its red is a mutation red: drop `unset CDPATH`.
  - Interfaces:
    - `triage-feedback.sh <job>` from any directory in the work tree prints
      the evidence and verdict a run from the root prints, and appends to the
      root's `plans/reports/triage-feedback-log.md`.
    - Outside a work tree: exit 2, one `ERROR: <cause>` line, no row.
    - Every other exit unchanged (Item 2.3).
    - Residual bound, stated in a comment: the `cd` failure after a
      successful `rev-parse` is the one new arm with no test. No input
      provokes it without fault injection.

- Item 2.3: pin triage's untested failure arms (KD-5).
  - Type: tdd
  - Requirements: m4, m5, m6
  - Depends on: Item 1.2
  - Files: `tests/test_triage_feedback_failures.py`,
    `tests/test_triage_feedback_behavioral.py`,
    `tests/test_triage_feedback_log.py`
  - Notes:
    - The behaviour exists, so every RED is a mutation red against
      `triage-feedback.sh` as it stands (`tdd-slice.md` §Mutation proof):
      one named mutant per test or case, restored and proven restored before
      the next.
    - The two `grep failed` arms, the behavioural grep's `*)` arm and the
      classification grep's, are textually identical. A mutation's exact
      string must take in a differing line of context.
    - A shim passes every other call through to the real tool. Probe a shim
      with `command grep`, never the Bash tool's `grep` (recall
      `cc-grep-shell-function`).
    - A shim embeds the real tool's path with `shlex.quote`, not double
      quotes (list revision after 2.1/1's test review).
    - Permission fixtures skip as root and restore modes before cleanup, as
      `test_unreadable_log_is_an_error_and_appends_nothing` does.
    - List revision after 2.2/2: Item 2.2 added a second
      `if [[ $status -ne 0 ]]; then`, the `rev-parse` guard's. Slice 1's
      `$status` mutant must take in the `changed-files.sh` call line above
      it. The run-location tests now sit in
      `tests/test_triage_feedback_location.py`, and the hub is at 308
      lines.
  - Slices:
    1. Entry clauses, in the failures module.
       - `test_usage_error_exits_1`, parametrized:
         - `no-args`: no argument;
         - `stale-base`: `j HEAD`, in a fixture where `j` alone would log a
           row.

         Expect exit 1, stderr `Usage: triage-feedback.sh <job>`, empty
         stdout and no log row. Mutants: drop `[[ -z "$job_dir" ]] ||` for
         `no-args` (the run then exits 2), and drop `|| [[ $# -gt 1 ]]` for
         `stale-base` (it then exits 0 with a verdict).
       - `test_changed_files_error_is_printed_then_exit_2` (m5). An unborn
         repo, with `classification.md` on disk. Expect:
         - stdout carrying `ERROR: git log failed`, then
           `ERROR: changed-files.sh exited 2`;
         - no `## Evidence`, exit 2 and no row.

         Mutant: `[[ $status -ne 0 ]]` → `[[ $status -eq 1 ]]`.
    2. Classification arms, in the failures module.
       - `test_unreadable_classification_is_an_error`. A run that would
         reach a verdict, with `classification.md` at mode 000. Expect
         `ERROR: grep failed`, no `## Evidence`, exit 2 and no row. Mutant:
         the classification grep's `*)` arm.
       - `test_failing_label_sed_is_an_error`. A `sed` shim exiting 4.
         Expect `ERROR: sed failed`, exit 2 and no row. Mutant: the
         `if ! classification=$(…sed…)` guard dropped.
    3. Remaining arms.
       - `test_failing_definition_grep_is_an_error_not_no`, in the
         behavioural module. A non-empty list holding `a.py` with
         `def foo():`, and a `grep` shim exiting 2 when called with `-qE`.
         Expect `ERROR: grep failed`, exit 2 and no row. Mutant: the
         behavioural grep's `*)` arm.
       - In the log module, `test_unwritable_log_is_an_error_not_a_usage_exit`
         gains a `directory` case. `plans/` is at mode 555 with no
         `plans/reports/`. Expect stdout ending
         `ERROR: cannot write plans/reports/triage-feedback-log.md`, and
         exit 2. Mutant: the `|| { … }` after `mkdir -p` dropped, which
         exits 1.
  - Interfaces (unchanged, pinned here):
    - Exit 1: `Usage: triage-feedback.sh <job>` on stderr, for zero or two
      or more arguments.
    - Exit 2: `ERROR: <cause>` on stdout and no log row, for:
      - `changed-files.sh` exiting 1 or 2, its output printed first;
      - a failing git, grep or sed;
      - an unreadable `classification.md`;
      - a log directory, header or row that cannot be written.

- Item 2.4: every hash-reading `git log` in `/build`'s prose prints hashes
  only on signed history (KD-7).
  - Type: tdd
  - Requirements: m14
  - Files:
    - new `tests/test_build_prose_git_log.py`;
    - GREEN edits `plugin/skills/build/references/phase-boundary.md` §Base
      and changed files, `plugin/skills/build/references/tdd-slice.md` (the
      GREEN-commit query), `plugin/skills/build/references/escalation.md`
      §Resuming step 1, `plugin/agents/tdd-auditor.md` check 2, and the D-88
      and D-89 query blocks in `docs/references/build-run-state.md`.
  - Scanned files: those five, plus
    `plugin/skills/build/references/finishing.md`. Its commands already
    carry the flag and stay pinned as regressions.
  - Slices:
    1. `test_read_git_log_commands_print_hashes_only_on_signed_history`,
       parametrized over the extracted commands, with ids `<file>:<n>`.
       - Extraction: every `git log` command carrying `--format=%H`, from a
         fenced block, with backslash continuations joined, or from an
         inline code span. Every scanned file yields at least one command,
         so an extraction that finds nothing fails rather than passing
         vacuously.
       - Fixture:
         - a repo with repo-local SSH signing: an `ssh-keygen -t ed25519
           -N ''` key under `tmp_path`, `gpg.format=ssh`, `user.signingkey`,
           `gpg.ssh.allowedSignersFile`, `commit.gpgSign=true` and
           `log.showSignature=true`;
         - `GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` set to the null
           device;
         - signed commits adding, in order: `plans/j/outline.md`;
           `plans/j/reports/item-1-1.md`;
           `item-1-1-s1-green.md`; `phase-1-corrector.md`;
           `review-code.md`; `final-review.md`; `tdd-audit.md`.
       - Placeholders, substituted before `shlex.split`:
         - `<job>` → `j`, `N-M` → `1-1`, `<k>` → `1`, `<P>` → `1`;
         - `<name>` → `item-1-1`, `<hosting file>` → `outline.md`;
         - `<run base>` → the parent of the `item-1-1.md` commit;
         - `<L>` → the `item-1-1.md` commit.

         A `<…>` left after substitution fails the test, which keeps the
         table in step with the prose.
       - Expect, per command: exit 0, non-empty stdout, and every stdout
         line a 40-hex sha.
       - Red today: every command in the five unflagged files puts
         `Good "git" signature for …` on stdout ahead of its hash, so the
         red is genuine and needs no mutation. `finishing.md`'s commands
         pass.
       - Skip only when `ssh-keygen` is absent or git lacks SSH signing
         (before 2.34), with the reason in the skip message. Both were
         present here at planning time (KD-7).

       GREEN adds `--no-show-signature` to each failing command and changes
       no other wording. D-88's reason sentence is Item 4.1's.
  - Interfaces:
    - Each command's stdout is hash lines only, whatever the reader's
      `log.showSignature`.

### Group 3 — cross-surface prose (general)

- Item 3.1: `agents/learnings.md` §"When calling triage-feedback.sh".
  - Type: general
  - Requirements: m11
  - Contract:
    - The correct pattern is `triage-feedback.sh <job>`, the job name alone,
      with the base derived from report history.
    - The anti-pattern is `plans/<job>` as `$1`, which `changed-files.sh`
      now refuses as no job name: exit 2, not a double prefix.
    - A two-argument call exits 1 with `Usage:`.
    - The section keeps the file's existing line style.

- Item 3.2: name the planning-artifact dispatch (KD-1).
  - Type: general
  - Requirements: m12
  - Files: `plugin/skills/build/references/dispatch-composition.md`
    §Naming and resumption, `plugin/skills/build/references/finishing.md`
    §1, the planning-artifact paragraph
  - Contract:
    - §Naming lists `review-plan-<source job>-<stem>` beside the four
      group slugs, as a name and not a group, with KD-1's reason in one
      clause: its report reads as a review report.
    - `finishing.md` §1's paragraph gives that name for each planning
      artifact it routes by artifact.
    - The prompt assigns the report path by §Prompt contents item 5. No
      corrector definition changes. `outline-corrector.md` sits at its
      allowlist ceiling, and defect 21 owns the corrector family.

- Item 3.3: name the fresh remediation dispatch `<step name>-fix`.
  - Type: general
  - Requirements: C-1 (`review-skill` Minor 7, ruled into scope)
  - Depends on: Item 3.2, which edits the same §Naming list
  - Files: `plugin/skills/build/references/dispatch-composition.md`
    §Naming and resumption, `plugin/skills/build/references/escalation.md`
    §Post-item remediation step 2
  - Contract:
    - Step 2's fresh dispatch is named `<step name>-fix`, where
      `<step name>` is the dispatch whose dirt it finishes: `item-1-2-fix`
      after a general item, `item-1-1-s2-green-fix` after a slice's GREEN.
    - §Naming lists the name, with the reason in one clause: reusing the
      step's name would overwrite the report its commit already carries.
    - The report path follows from §Prompt contents item 5.
      `item-N-M-fix.md` matches `item-*`, but it lands only after the item's
      own report, so neither the resume test nor the base moves. It does not
      match `item-<N>-<M>.md`, so triage counts it as a report beyond the
      item's own.
    - Step 3 escalates when that dispatch fails, so no second `-fix` name
      is needed.

- Item 3.4: `plugin/agents/refactor.md` §Step 5, the plan-sources paragraph.
  - Type: general
  - Requirements: m13
  - Contract: the stated reason covers every file the prohibition names. The
    file hosting the item (`runbook.md`, or the `outline.md` or `design.md`
    routed to `/build`) takes the orchestrator's list-revision commits, and
    the rest are the plan the run executes against. A second writer collides
    with either. The prohibition itself is unchanged.

- Item 3.5: `plugin/skills/design/references/triage.md` §Classification Gate
  (KD-3).
  - Type: general
  - Requirements: m15
  - Contract:
    - The block template and the persistence paragraph require the persisted
      file to open with one job-level line, before any per-item block.
    - The line's value is exactly one of the four labels, with nothing after
      it. The paragraph says why: `triage-feedback.sh` reads the first
      `Classification:` line, and any other value gives `no-classification`,
      with the row lost to calibration.
    - The paragraph states the composite rule of KD-3.
    - Load `craft:directive-writing`. The template stays instruction, not
      narration.

- Item 3.6: `plugin/README.md` names `plugin-dev` and `craft` as optional.
  - Type: general
  - Requirements: C-2 (leg-4 open item 6, ruled into scope)
  - Contract:
    - The README names its optional plugins in one place: `sandbox-lies`,
      `plugin-dev` and `craft`, each with what is lost without it.
    - Without `plugin-dev`, the review gate's skill row falls back to
      `edify:corrector`, and the agent row loses its criteria source.
      Without `craft`, the design-graph row loses its criteria source. Both
      consequences are worded as `review-requirement.md` §"When plugin-dev or
      craft is not installed" states them.
    - The `sandbox-lies` consequence stays in the existing `verify-step.sh`
      bullet. The new place points at it rather than restating it.

### Group 4 — design record (general)

- Item 4.1: `docs/references/build-run-state.md` and `docs/decisions.md`.
  - Type: general
  - Requirements: m3, m12, m14, m16, m17
  - Depends on: Items 2.4, 3.2
  - Load `craft:design-doc-writing`.
  - Contract:
    - D-88 (m14): Item 2.4 has already added the flag to its query block.
      One sentence gives the reason, which covers every `git log` `/build`
      reads, and cites the signed-history test.
    - D-89 (m16): the conclusion and body widen per KD-2 to the finishing
      stages: the review gate after the last item-report commit, the final
      review and the TDD audit, each keyed on its report path.
    - D-90 (m3): "Both drops keep a re-run on the set the first run
      measured" gains its bound. Reports committed under
      `plans/<job>/reports/` after Finish still count, such as the
      `deliverable-review*.md` that `/deliverable-review plans/<job>` writes.
      A re-run after one can therefore log a second row, and for a Simple
      job its verdict can flip from `match` to `underclassified`. The
      final-review fixes clause is ruled unchanged and is not added.
    - D-90 (m16): KD-2's row sentence.
    - D-90 (m2, list revision after 2.1/1): "A usage error or a git failure
      exits 2 with `ERROR:`" says `ERROR:` alone, with no `BASE:` line and
      no path, as KD-4 makes true and
      `test_late_diff_failure_prints_error_alone` pins.
    - D-93 (m12): where it says planning artifacts route by artifact, one
      sentence gives KD-1's name and why it matches `review-*.md`.
    - Rejected (m17): the entry becomes "Triage filtering its own log path
      out of the list on its side". The list does drop it (D-90), and what
      was rejected is a second copy of that filter in triage.
    - `decisions.md`: D-89's conclusion line follows KD-2, and the
      build-run-state *Rejected:* line takes m17's label. D-88, D-90 and
      D-93 keep their conclusion lines.
    - No changelog entry.

## Finding → item traceability

| Finding | Item | Note |
|---|---|---|
| m1 | 2.2 | KD-6 |
| m2 | 2.1 | KD-4 |
| m3 | 4.1 | bound in D-90 only, as ruled |
| m4 | 2.3 | slices 2–3; KD-5 reverses review-fixes-2's m5 exemption |
| m5 | 2.3 | slice 1 |
| m6 | 2.3 | slice 1 |
| m7 | 1.2 | |
| m8 | 1.2 | |
| m9 | 1.2 | |
| m10 | 1.1 | split, and citations in the sibling modules too |
| m11 | 3.1 | |
| m12 | 3.2, 4.1 | KD-1 |
| m13 | 3.4 | |
| m14 | 2.4, 4.1 | KD-7 widens to three more sites; signed-history test |
| m15 | 3.5 | KD-3, ordering ungrounded |
| m16 | 4.1 | KD-2 |
| m17 | 4.1 | |
| m18 | 2.1 | rides slice 1's header edit |
| C-1 | 3.3 | `<step name>-fix`, ruled into scope |
| C-2 | 3.6 | README optional plugins, ruled into scope |

## Scope

IN: the files the items name.

- Scripts: `triage-feedback.sh`, `changed-files.sh`.
- Tests: the changed-files and triage modules, their helpers,
  `verify_step_helpers.py`, and the new `test_build_prose_git_log.py`.
- Prose: `dispatch-composition.md`, `finishing.md`, `phase-boundary.md`,
  `tdd-slice.md`, `escalation.md`, `design/references/triage.md`,
  `refactor.md`, `tdd-auditor.md`, `agents/learnings.md`.
- Docs: `plugin/README.md`, `build-run-state.md`, `decisions.md`.

OUT:

- `plugin/skills/build/SKILL.md`, at 199 lines of its 200 cap. No item
  touches it.
- Test D's output-side `printf '%b'` gap, and final-review fixes landing after
  triage. Both were ruled unchanged.
- The 2026-10-06 changelog entry's re-run sentence, a dated record.
- The corrector-family agents. Defect 21 owns them, and three sit at their
  allowlist ceilings.
- The four deferred candidates below.

## Author-corrector coupling

The author changes are `/build` prose and scripts, and `/design`'s triage
template. Coupled reviewers, and whether each needs an update:

- `tdd-auditor`: its check 2 query only, in Item 2.4.
- The T5 gate `triage-feedback.sh`: Items 2.2 and 2.3.
- The planning correctors: no. KD-1 assigns their report path through the
  prompt, which already overrides an agent's default.

## Execution shape

`/build` reads this outline directly, with no runbook. Every target is named
at section level, every behavioural change has its slices, and the decisions
are KD-1 to KD-7. The review gate's list will hold code, tests and
`plugin/README.md` (`review-code`), `build` and `design` references
(`review-skill`), two agents (`review-agent`), and the design graph
(`review-design`).

My human partner accepted the outline's length, over the soft 400-line plan
cap, rather than a split.

## Deferred candidates

These come from `plans/review-fixes-2/reports/build-leg4.md` §Open items 3–6.
My human partner ruled two of the six into scope, as Items 3.3 (C-1) and 3.6
(C-2). The four below stay deferred. Each line gives the item, its overlap
with a round-3 finding, the files, and the reason for deferring it.

- **One slice per failure clause** (tdd-audit Important 1). Overlap: the
  cause behind m4–m6. Files:
  `plugin/skills/runbook/references/runbook-format.md` and the outline route.
  **Deferred:** it should land with
  `inbox/brief-runbook-slice-enumerates-predicate-boundaries.md`, a sibling
  rule for the same paragraph.
- **tdd-audit minors**: GREEN reports out-of-batch contract rather than
  writing it; formatters off tests during GREEN; code-review recommendations
  carried into the next slice's dispatch; a full-suite count in GREEN reports
  on a cache hit. Overlap: none. Files: `plugin/agents/test-driver.md`,
  `plugin/skills/build/references/tdd-slice.md`, `dispatch-composition.md`.
  **Deferred:** each changes the slice loop's protocol and wants its own
  evidence and review coupling.
- **`sandbox-lies` `phantom-untracked` two-name threshold stated.** Overlap:
  none. Files: `escalation.md`, D-91 in `build-run-state.md`,
  `plugin/README.md`. **Deferred:** a foreign plugin's detector threshold
  rots in edify's docs, and the absent-plugin bound is already stated.
- **Resume tracking a list revision still owed** (`review-skill` Minor 8).
  Overlap: none. Files: `escalation.md` §Resuming step 1, possibly
  `tdd-slice.md`. **Deferred:** it needs a detection rule from report
  history, not a sentence.
