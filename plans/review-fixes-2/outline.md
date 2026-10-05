# Outline — review-fixes-2

Third pass on `build-fixes`. It covers every finding of its round-2
deliverable review except M3, which defect 21 owns. Goal: round 3 comes back
clean. Finding IDs are the review's (C1, M1–M6, m1–m23, from
`plans/build-fixes/reports/deliverable-review.md`). `build-fixes KD-N` means
`plans/build-fixes/outline.md`'s decision N. Classification:
`classification.md`. Every finding was verified against HEAD `79d0b687` and
every one reproduces. N-1 is not the review's. It turned up while verifying C1,
and my human partner put it in scope: an unrecognised classification label
falls through to `match`.

## Provenance

- **Derived from:** `plans/build-fixes/reports/deliverable-review.md`,
  superseding `plans/build-fixes/outline.md`
- **Base:** `d444630c01bd98851cddbedde3fbc9b85c18345d`

## Key decisions

**KD-1 — Triage measures the set the review gate reviewed (C1, M1, m4–m6,
N-1; amends D-90; my human partner's ruling).** The call becomes
`triage-feedback.sh <job>`, and the `<base>` argument goes. The script runs
`changed-files.sh <job>` itself. It finds that script relative to its own
path at `../skills/build/scripts/`, the idiom `verify-step.sh` uses for
`exempt-paths.sh`, and it reads the `BASE:` line and the list from the
output. The evidence:

- **Files changed:** the number of paths in the list.
- **Behavioral code:** the definition patterns, run over
  `git diff --no-color --no-ext-diff --no-renames <base> HEAD` limited to
  exactly those paths, given as literal pathspecs. An empty list reads `no`
  and runs no diff, because an empty pathspec diffs everything. A path
  holding a newline prints as two list lines and matches nothing. That is
  the residual bound of `changed-files.sh`'s line format, and a comment
  states it.
- **Reports:** reports the run committed beyond the one every item leaves.
  These are the paths directly under `plans/<job>/reports/` that
  `<base> HEAD` adds, minus the per-item `item-<N>-<M>.md`, where N and M
  are digits, and minus the review-gate reports (`review.md`,
  `review-*.md`, `final-review.md`). Slice, refactor and phase-boundary
  reports count. Planning reports committed before the base fall outside the
  range. That replaces the name exclusions `design-review*`,
  `outline-review*` and `recall-*`, which never covered `runbook-review.md`
  or `explore-*`.
- **Verdict rules:** unchanged. Simple is `underclassified` on behavioural
  code or `Reports > 0`. Complex is `overclassified` on files ≤ 2, no
  reports and no behavioural code. The thresholds stay ungrounded (L-2).
- **Failures:**
  - A usage error keeps exit 1 and its `Usage:` line.
  - `changed-files.sh` exiting 1 (`NO-BASE:`) or 2 (`ERROR:`) → print its
    output, then exit 2 with `ERROR:`. KD-3 makes `NO-BASE:` at finishing a
    fault.
  - A git or grep failure → exit 2 with `ERROR:`, never a verdict.
  - No failure appends a log row.
- **m4:** every git call puts its pathspecs after `--`.
- **m5:** no here-string. grep's exit 1 means "no", and exit ≥ 2 is an
  error, by `verify-step.sh`'s filter pattern. No input to the script
  provokes that failure without fault injection, so no test pins it; the
  code review checks the form.
- **m6:** the classification parse has no `xargs` and no `|| true`. grep
  finding no `Classification:` line is a result (no classification), its
  exit ≥ 2 is an error, and the value is trimmed by `sed` or parameter
  expansion, so an apostrophe reads literally.
- **N-1 (ruled IN):** the class is the trimmed value only when it is
  exactly `Simple`, `Moderate`, `Complex` or `Defect`. Any other value
  gives `no-classification` and an `unrecognised classification: <label>`
  line, and appends no row. Until now such a value fell through to `match`,
  and the log holds two rows logged that way.

Rejected:

- Triage keeping `<base>` and filtering the raw diff itself. That is a
  second copy of D-90's filters, and D-90 already rejects prose copies for
  drifting.
- Counting on-disk reports with `item-*` excluded by name. Planning reports
  outside the name list stay counted.

**KD-2 — The triage log holds one row per evidence (m7, ruled).** The append
is skipped when the log already holds a row equal to the new one in every
column but the date. A re-run on new evidence, such as a later item, still
appends.

**KD-3 — Work with no `Item N.M` is Item 1.1 (M4, ruled).** This covers
`/build` §1 option 3, the task taken from the invocation, and a design or
outline with no item structure. The work is one item, Item 1.1: its report
is `item-1-1.md`, and its commit is `<type>: <job> Item 1.1 — <title>`.
Every run therefore commits an item report, `NO-BASE:` at finishing is a
fault, and `finishing.md`'s STOP stands.

The files show no reason to treat item-less designs differently. D-83 gives
every behavioural change an item with `Slices:`, so a design with no items
carries general work only, and one item can execute that. The cost is resume
granularity: a kill mid-item re-runs the item, with its dirt examined
(`escalation.md` §Resuming step 2).

**KD-4 — A landed finishing stage is not re-run (m7, ruled for the
gate).** `finishing.md` §1 has landed when a commit after the last
item-report commit touches a `review-*.md` report. That last commit is
`L = git log -1 --format=%H -- ':(glob)plans/<job>/reports/item-*'`, and
the gate has landed when
`git log -1 --format=%H <L>..HEAD -- ':(glob)plans/<job>/reports/review-*.md'`
prints a hash. `review-skip.md` counts too. A landed gate goes straight to
§2. §3's final review and TDD audit skip the same way on `final-review.md`
and `tdd-audit.md`, an extension my human partner approved at the outline gate. As in D-89,
the key is the report path, never a subject.

**KD-5 — Nothing reverts by default, committed or not (M2, ruled
2026-10-03).** A committed failed fix escalates to my human partner with the
commits since the last clean commit and what the attempt found. The
`git revert --no-commit <sha>` recipe, newest first, then the commit by name
with the revert subject, runs only on the commits they decide to revert.

**KD-6 — Every committed step is verified (m13, ruled).** `SKILL.md` §4.4
adds a slice's refactor commit and its list-revision commit, and
`tdd-slice.md` steps 2 and 3 each end at §4.4. A refactor returning `error`
after leaving dirt reaches §4.4 like any other step. The README and
`design.md` §5.3 claims then hold as written, and stay.

**KD-7 — A list revision lives in the file hosting the item (M5).** That
file is `runbook.md`, or the `outline.md` or `design.md` routed to `/build`.
The revision is made there, and the commit takes that file alone:
`git commit -- plans/<job>/<host file>`, subject
`<type>: <job> Item N.M/k — list revision`. `tdd-auditor` accounts for a
list-revision commit touching the hosting file alone, and reads list
revisions from that file's history.

**KD-8 — The skill row covers the prose a skill loads (m11).** The rule is
stated once in `dispatch-composition.md`, with D-93 as its record. The
`review-requirement.md` table row conforms: skill definitions and the
agent-instruction prose they load, meaning their `references/` nodes and the
shared instruction files a skill loads from outside itself. An instruction
file no skill loads, such as `CLAUDE.md` or `.claude/rules/*.md`, matches no
row and takes the `review-code` default. All three texts say so in the same
words.

**KD-9 — A remediation dispatch after a slice step names its agent (m17).**
After a slice's GREEN, the fresh dispatch of `escalation.md` §Post-item
remediation step 2 is `edify:test-driver` in GREEN mode. After a
code-review, refactor or list-revision commit, it is `edify:artisan`. Either
dispatch carries the slice's entry and the dirt.

## Items

Items 1.x are scripts and tests, Items 2.x `/build` prose, Items 3.x the
design record. No phases. All edits to one prose file sit in one item.

- Item 1.1: `plugin/bin/triage-feedback.sh` — KD-1's evidence model.
  Requirements: C1, M1, m4, m5, m6, N-1.
  - The tests stay in `tests/test_triage_feedback.py`. The module is at 256
    lines and passes 400, so it splits on a seam, with a
    `triage_feedback_helpers.py` as `changed_files_helpers.py` does. Never
    shave docstrings.
  - Every fixture commits a `plans/j/reports/item-*` report, because the
    base comes from report history now.
  - Slice 1's RED moves the module's existing tests to the `<job>`-only
    call and that fixture. These are the files-changed,
    uncommitted-definition, forced-colour and failing-diff tests. They red
    on the usage exit, and the slice's own test reds on its assertion.
  - Slice 1's RED also deletes `test_simple_with_review_reports_matches`. It
    builds a run with no item report, which D-88 rules out and which now
    exits 2. Slice 2 replaces it.
  - Comments cite D-numbers, never an outline's KD (m8).

  Slices:
  1. `test_files_changed_is_the_review_gates_list`. Pre-run commit:
     `plans/j/reports/outline-review.md`. Run commit 1:
     `plans/j/reports/item-1-1.md`, `a.txt`, `inbox/x.md`,
     `.claude/handoff-task.md`. Run commit 2: `item-1-2.md` and `b.txt`.
     `triage-feedback.sh j` prints `- Files changed: 2` and exits 0. The
     stdout assertion comes before the exit-code one.
  2. `test_reports_exclude_the_per_item_report`. Before the base, commits
     add `plans/j/reports/runbook-review.md` and `explore-x.md`.
     `classification.md` holds `- **Classification:** Simple`. One run
     commit adds `item-1-1.md` and a plain `notes.txt`, and another adds
     `review-code.md`. Expect `- Reports: 0`, `- Behavioral code: no` and
     verdict `match`. With the label changed to `Complex`, the verdict is
     `overclassified`. With the label back at Simple and a commit adding
     `item-1-1-s1-code-review.md`, expect `- Reports: 1` and verdict
     `underclassified`.
  3. `test_behavioral_code_reads_the_lists_paths_only`. The run commits
     `item-1-1.md`, whose prose has a line starting `class with an explicit
     whitelist`, and `inbox/x.md` holding `def foo():`. Expect
     `- Behavioral code: no`. A further commit adds `a.py` holding
     `def foo():`, and the result reads `yes`.
  4. `test_unrecognised_label_is_no_classification` (N-1). The first
     `Classification:` value is
     `Simple / Moderate agentic-prose (one route)`. The run commits a
     `def foo():` in `a.py`, so a Simple reading would give
     `underclassified`. Expect:
     - verdict `no-classification`;
     - stdout carrying `unrecognised classification: ` followed by that
       label;
     - exit 0, and no log row.

     Only an exact `Simple`, `Moderate`, `Complex` or `Defect` is a class.
  5. `test_odd_names_and_labels_do_not_derail_triage`. Cases:
     - The run changes a tracked file named `HEAD`. Expect exit 0, with it
       counted in Files changed.
     - The classification line is
       `- **Classification:** Moderate (my human partner's call)`. Expect
       exit 0, no `xargs` text on stderr, and the unrecognised-label line
       carrying the label verbatim, apostrophe included.
     - `classification.md` has no `Classification:` line. Expect verdict
       `no-classification`, exit 0, no unrecognised-label line and no row.

     Where an earlier GREEN already wrote a behaviour, the slice proves it
     by mutation.

  Interfaces:
  - `triage-feedback.sh <job>`, exit 0. Output is `## Evidence` with
    `- Files changed: <n>`, `- Reports: <n>`, `- Behavioral code: yes|no`
    and `- Review artifact: review|skip|none`. Then `## Verdict` and the
    verdict, then the divergence line where under- or overclassified, and
    `WARNING: No corrector report` where the artifact is `none`.
  - Exit 1: `Usage: triage-feedback.sh <job>` on stderr.
  - Exit 2: `ERROR: <cause>` on stdout. It covers `NO-BASE:`, an
    `ERROR:` from `changed-files.sh`, and git or grep failure. No log row
    is written.
  - An unrecognised first `Classification:` value gives verdict
    `no-classification` and the line
    `unrecognised classification: <label>` (N-1).
  - Side effect: at most one row appended to
    `plans/reports/triage-feedback-log.md`, none on `no-classification`.

- Item 1.2: `plugin/bin/triage-feedback.sh` — KD-2's idempotent append.
  Requirements: m7. Depends on: Item 1.1. Slices:
  1. `test_rerun_appends_no_duplicate_row`. A run on the slice 1.1/2
     fixture leaves the header and one row. The same run again leaves
     exactly one row. The log, pre-seeded with that row under a different
     date, gains no row. A further run commit adding `item-1-2.md` and
     `c.txt` changes the evidence, so the next run appends a second row.

- Item 1.3: `tests/test_changed_files.py` — pin Item 1.2's NUL-delimited
  read. Requirements: M6.
  - The behaviour exists, so RED is a mutation red against
    `changed-files.sh` as it stands.
  - Both of the review's mutants must red the test, and the RED report
    records each under `Mutation proof`:
    - `for path in $(git diff --name-only …)`;
    - a newline `read` with `-z` dropped from the diff.
  - Each mutation is restored before the next.

  Slices:
  1. `test_paths_with_space_and_non_ascii_bytes_are_listed_whole`. The
     run commit adds `item-1-1.md`, `my file.txt`, `café.txt` and the
     exempt `inbox/é.md`. Expect stdout to be exactly `BASE: <pre-run
     sha>`, then `café.txt`, then `my file.txt`.

- Item 1.4: the `exempt-paths.sh` load guard, in `tests/test_changed_files.py`
  and `tests/test_verify_step.py` (the fail-closed module). Requirements: m23.
  - Each test copies the script under test into a `tmp_path` scripts
    directory beside a doctored `exempt-paths.sh`, and runs the copy.
  - RED is a mutation red: replace the guard with a bare `source`. `set -u`
    or `set -e` then exits 1.

  Slices:
  1. `test_unloadable_exempt_paths_is_an_error_not_no_base`. The repo
     holds a committed item report. Two cases: `exempt-paths.sh` absent,
     and present but defining nothing. In each, `changed-files.sh j` exits
     2, stdout carries
     `ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh`,
     and stdout has no `NO-BASE:`.
  2. `test_unloadable_exempt_paths_is_an_error_not_dirty`. The same two
     cases make `verify-step.sh` exit 2 with that line, never `DIRTY:`.

- Item 1.5: script hygiene, in `plugin/skills/build/scripts/changed-files.sh`,
  `verify-step.sh` and `exempt-paths.sh`. Requirements: m1, m8. Depends on:
  Items 1.3, 1.4, whose mutation reds run against the scripts as they stand.
  Load `shell-scripting:shell-gotchas`.
  - m1: drop `changed-files.sh`'s `exec 2>&1`. The script's own `ERROR:`
    and `NO-BASE:` lines stay on stdout, which is the interface, and git's
    diagnostics go to stderr. An exit 0 then prints only `BASE:` and paths,
    and an exit 2 prints `ERROR:` first. The header sentence citing
    `exec 2>&1` changes with it.
  - m8: every `KD-N` in these scripts' comments becomes its durable ID:
    - D-88 for the base;
    - D-89 for the phase base;
    - D-90 for the list and the one-script rule;
    - D-91 for the exemption and the clean tree;
    - D-94 for subjects.

    A citation with no D-ID says what it means instead.

- Item 1.6: test hygiene. Requirements: m20, m21, m22. Depends on: Items 1.2,
  1.4.
  - m20: the `tests/test_verify_step.py` and
    `tests/test_verify_step_exemption.py` docstrings say why the tests are
    split, to keep each module under its line cap, as
    `test_changed_files_phase.py`'s does.
  - m21: `test_verify_step_exemption.py`'s docstring states D-91's
    exemption: `memory`, `.claude/handoff-*.md` and `inbox/*.md`, in any
    porcelain state but a rename or copy.
  - m22: `test_no_item_report_exits_1` splits in two:
    - `test_git_failure_is_error_not_no_base` covers the unborn repo and
      the root-commit report, each exit 2 with `ERROR:`;
    - `test_no_item_report_exits_1` keeps the outline's scenario alone.

    Each docstring keeps the reason its name gives.
  - The `tests/test_line_limits_wc_padding.py` docstring cites
    `triage-feedback.sh:14`, `:21` as `wc -l` sites. Correct it to the
    sites after Items 1.1–1.2, by what they count rather than by line
    number, or drop the claim where none remains.

- Item 2.1: `plugin/skills/build/SKILL.md`. Requirements: M4, m7, m13.
  - §1, around line 39: option 3 and an item-less design or outline are
    one item, Item 1.1. Its report is `item-1-1.md` and its subject
    `<type>: <job> Item 1.1 — <title>` (KD-3).
  - §4.4: add a slice's refactor commit and its list-revision commit to the
    list (KD-6).
  - §5: one clause saying a review gate `finishing.md` §1 finds landed is
    not re-run (KD-4).
  - The hub ends below 200 lines. Room comes from §2's DIRTY bullet, whose
    enumeration of the three exempt paths repeats `exempt-paths.sh` and
    D-91: point at them instead. Never cram lines or shave other prose
    (recall `line-caps`).

- Item 2.2: `plugin/skills/build/references/finishing.md`. Requirements: C1,
  M1, M4, m7, m15, m16. Depends on: Item 1.1.
  - §1 opens with KD-4's landed check. A landed gate → §2.
  - §1 step 1: `NO-BASE:` is a fault, because every run commits an item
    report, Item 1.1 included (KD-3). An exit 0 with no paths has nothing
    to review: take `/build` §5's `review-skip.md` branch, which §1's report
    commit carries (m16).
  - §2: `plugin/bin/triage-feedback.sh <job>` takes no base (KD-1). Delete
    the paragraph on writing the hash into the command. A non-zero exit →
    STOP and report its output.
  - §3 steps 1–2: KD-4's landed skip for `final-review.md` and
    `tdd-audit.md`. `final-review`'s report gets the UNFIXABLE grep and
    validation that §1 runs, before the closing commit (m15).

- Item 2.3: `plugin/skills/build/references/escalation.md`. Requirements: m9,
  m12, m17.
  - Exit-1 bullet: the mask branch needs the optional `sandbox-lies`
    plugin's `phantom-untracked` hook. Without it no listing is annotated,
    so the branch never fires, and a masked listing reads as dirt (m9).
  - §Post-item remediation step 2: KD-9's agent types.
  - §Resuming step 2 names the verdicts instead of "every other verdict"
    (m12):
    - `DIRTY:` is examined;
    - `PRECOMMIT:` over a clean tree, and exit 2, STOP as `/build` §2
      does.

    Then state the bound: a dirty resume reaches no precommit at the gate,
    and the first remaining item's §4.4 verification is where precommit
    first runs, over the adopted prior work too.

- Item 2.4: `plugin/skills/build/references/tdd-slice.md`. Requirements: M5,
  m13.
  - §After the slice step 3 follows KD-7, with the hosting file in place of
    `runbook.md`.
  - Steps 2 and 3 each end at `SKILL.md` §4.4 once their commit lands
    (KD-6).

- Item 2.5: `plugin/agents/tdd-auditor.md`. Requirements: M5. Every place the
  agent treats `runbook.md` as the slices' host takes the hosting file
  (KD-7). These are §Inputs, check 2's list-revision commit, §List
  revisions recorded, and the report template's `Runbook:` line and
  `## List Revisions` hint.

- Item 2.6: `plugin/skills/build/references/dispatch-composition.md`.
  Requirements: m10, m11.
  - §Naming and resumption: resumption is `SendMessage` to the dispatch's
    name, and an agent spawned unnamed is resumed by its agent id, as
    `review-requirement.md` §UNFIXABLE Detection Protocol step 4 does
    (m10, ruled). Delete "an unnamed agent cannot be resumed".
  - The `review-skill` row states KD-8.

- Item 2.7: `plugin/fragments/review-requirement.md`. Requirements: m11. The
  routing table's skill row conforms to KD-8. Step 4 (`c458a726`) stays as
  it is (ruled).

- Item 2.8: `plugin/fragments/delegation.md` §Delegate Resume. Requirements:
  m10. Resuming is `SendMessage` to the name, or to the agent id where the
  agent was spawned unnamed.

- Item 2.9: `plugin/fragments/escalation-acceptance.md`. Requirements: M2,
  m14.
  - §Rollback protocol, "Fix committed": KD-5.
  - §Verification sequence step 3: the commit takes
    `<type>: <job> Item N.M[/k] — <title>`. Then one re-run:
    - `PRECOMMIT:` → step 2;
    - a second `DIRTY:`, or exit 2 → escalate.

    This replaces "re-run until it exits 0".

- Item 2.10: `plugin/skills/build/references/review-dispatch-template.md`
  §Example. Requirements: m18. The return line asks for an UNFIXABLE with
  its subcategory code and a three-gate investigation summary, in
  §Report-only variant's wording.

- Item 2.11: `plugin/README.md`. Requirements: C1, M1, m9, m13. Depends on:
  Item 1.1.
  - Name `sandbox-lies` as an optional dependency, with Item 2.3's
    consequence.
  - The `verify-step.sh` call sites add the refactor and list-revision
    commits (KD-6).
  - The `changed-files.sh` bullet: triage reads the list, not just the
    base (KD-1).

- Item 3.1: `docs/references/build-run-state.md` and `docs/decisions.md`.
  Requirements: C1, M1, M2, m2, m3, m9, m11, m19. Depends on: Item 1.1.
  Load `craft:design-doc-writing`.
  - D-90:
    - Triage runs the script and counts its list: the length of the list,
      and the `<base> HEAD` diff of those paths only. This replaces "two
      diffs take the same `<base> HEAD` form".
    - Its report count excludes the report every item leaves.
    - `NO-BASE:` covers a repo with commits, and an unborn `HEAD` is a git
      failure, exit 2 (m3).
    - A **Limitation** paragraph covers merge-shaped history (m2). A merge
      of `main` into the job branch, or another session committing on the
      branch, lists commits that are not the run's. A report added only in
      a merge commit is invisible to the base query, which gives
      `NO-BASE:`. Frequency is unmeasured.
  - D-91: `sandbox-lies` is optional, with its consequence (m9).
  - D-92: KD-5's committed case. The revert operand reads
    `<tracked or indexed paths>` (m19).
  - D-93: KD-8's wording.
  - Rejected alternatives: add KD-1's first rejection.
  - `decisions.md`:
    - D-90's conclusion line becomes "… and one script produces it, for the
      phase boundary, the review gate and triage alike".
    - The build-run-state *Rejected* line adds the same alternative.

- Item 3.2: `docs/design.md` §8 L-2. Requirements: C1, M1. Depends on: Item
  1.1. The log's fields are the review gate's files changed, the reports
  beyond one per item, behavioural code and the verdict. The column keeps
  its header, and rows before this job counted every report. This replaces
  "agent count".

- Item 3.3: `docs/changelog/<date>-triage-measures-the-review-gates-set.md`,
  `<date>` the day it is written, and its line in the `docs/changelog.md`
  index. Requirements: C1, M1, M2. A dated entry: triage now measures the
  review gate's set, which D-90 recorded wrongly, and a committed failed fix
  no longer reverts by default. Load `craft:design-doc-writing`.

- Item 3.4: `plans/build-fixes/outline.md`, a revision after the fact.
  Requirements: m3, m20.
  - Item 1.2 Interfaces: exit 1 `NO-BASE:` for a repo with commits and no
    committed item report. Exit 2 `ERROR:` on usage or git failure, an
    unborn `HEAD` included (m3, ruled).
  - Items 1.1 and 1.4 name the modules the tests landed in:
    `tests/test_verify_step_exemption.py` and
    `tests/test_changed_files_phase.py` (m20).

## Scope

IN: the files the items name.

- Scripts: `triage-feedback.sh`, `changed-files.sh`, `verify-step.sh`,
  `exempt-paths.sh`.
- Tests: `test_triage_feedback.py` (and its split), `test_changed_files.py`,
  `test_verify_step.py`, `test_verify_step_exemption.py`,
  `test_line_limits_wc_padding.py`.
- `/build` prose: `build/SKILL.md`, five `build` references.
- Fragments: `escalation-acceptance.md`, `delegation.md`,
  `review-requirement.md`.
- Agents: `tdd-auditor.md`.
- Docs: `plugin/README.md`, `build-run-state.md`, `decisions.md`,
  `design.md`, a changelog entry and `plans/build-fixes/outline.md`.

OUT:

- M3, the `review-design` row against `corrector.md` §0. Defect 21 owns it.
- The two log rows already logged with an unrecognised label, both
  `Simple / Moderate agentic-prose (one route)`. They are history, and N-1
  changes only rows written after it.
- The repo-relative `plugin/…` invocation form. It belongs to the
  repo-relative-paths job, as in build-fixes.

## Author-corrector coupling

The author change is `/build`, the T4/T5 executor of D-26. Its coupled
reviewers, and whether each needs an update:

- `tdd-auditor`: yes, Item 2.5.
- The T5 gate `triage-feedback.sh`: yes, Items 1.1–1.2.
- `corrector`: no. Its prompt shape changes only through the template
  example (Item 2.10), and `corrector.md` itself is defect 21's.

## Execution shape

`/design` → `/build`, no runbook (ruled). The route-to-execution
preconditions hold:

- No decision is left to the executor once the gate's questions are
  answered.
- Every target is named at section level.
- Every behavioural change has its slices.

No runbook discriminator holds. The prose edits commute, and the only
ordering is the declared `Depends on:` lines.
