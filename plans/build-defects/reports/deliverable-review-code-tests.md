# Deliverable review (Layer 1) — code and tests

Job: `plans/build-defects`. Range: `d444630c01bd98851cddbedde3fbc9b85c18345d..HEAD`.
Baseline: `plans/build-defects/outline.md` KD-3, KD-7, Items 1.1 and 1.2.
Axes: `docs/references/deliverable-review.md` D-56.

## Scope

| File | Type |
|---|---|
| `plugin/bin/triage-feedback.sh` | Code |
| `plugin/skills/build/scripts/verify-step.sh` | Code |
| `tests/test_triage_feedback.py` | Test |
| `tests/test_verify_step.py` | Test |
| `justfile` `run-pytest` sentinel hunk | Configuration (sufficiency check only) |

## Severity counts

Critical 0 · Major 1 · Minor 5

## Findings

### F-1 — Major — `tests/test_verify_step.py` (module; `test_conventional_dirt_is_clean_and_other_dirt_is_not`, `test_memory_gitlink_is_clean_and_a_sibling_name_is_not`) — Test: coverage

KD-7 exempts the three paths "in any porcelain state" and names the handoff
file's staged state specifically. The tests pin only `MM` and `??`. No test
covers staged-add (`A `), deleted (`D ` / ` D`) or unmerged states. A mutation
that restricts the XY columns to modification states survives the whole
module. That mutation would report a staged new `.claude/handoff-*.md` or a
deleted `inbox/*.md` brief as DIRTY, which contradicts KD-7.

Probe: I copied `verify-step.sh` with
`exempt='^[ M?][ M?] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'`
and rebound `SCRIPT` in a copy of the test module. All 6 tests passed against
the mutant. The shipped script itself is correct here. In a scratch repo,
`D  inbox/old.md` and ` D .claude/handoff-task.md` each gave exit 0 and
`CLEAN:`.

### F-2 — Minor — `plugin/skills/build/scripts/verify-step.sh` (`exempt` pattern) — Code: conformance / robustness

KD-7 exempts `memory` as "the gitlore submodule at rest". The pattern cannot
tell a gitlink from an ordinary path, so any path named `memory` is exempt in
any state. An untracked regular file named `memory`, or a tracked regular file
by that name, clears the tree. Probe: in a scratch repo with no submodule,
`echo x > memory` gave the porcelain line `?? memory`, and the script printed
`CLEAN: tree clean, just precommit passed` with exit 0. The practical exposure
is small, because it needs a dispatch to leave behind a file with exactly that
name. The exemption is still wider than the design states. One way to narrow
it is to exempt `memory` only when `git ls-files -s memory` reports mode
`160000`. That fix is unverified.

### F-3 — Minor — `plugin/skills/build/scripts/verify-step.sh` (`exempt` pattern) — Code: conformance (fails closed)

Every `R`/`C` line is rejected, including a rename whose source and
destination are both exempt. Probe: `git mv inbox/old.md inbox/new.md` gave
`R  inbox/old.md -> inbox/new.md`, which printed `DIRTY:` with exit 1. KD-7's
"any porcelain state" covers this line. The script over-reports: it fails
closed and never hides dirt. The in-file comment presents rejecting all
renames as deliberate, but KD-7 does not record the carve-out.

### F-4 — Minor — `tests/test_verify_step.py` (module) — Test: coverage

The single-level reading of `inbox/*.md` and `.claude/handoff-*.md` (`[^/]+`)
is not pinned. A mutation that widens both to `.+` survives all 6 tests. That
mutant would exempt `inbox/sub/x.md` and `.claude/handoff-dir/x.md`. The
shipped script reports both as DIRTY: `?? inbox/sub/x.md` gave exit 1, and
`?? .claude/handoffs/x` gave exit 1. KD-7's glob does not say whether `*`
crosses `/`, so this is Minor rather than a gap in a specified scenario.

### F-5 — Minor — `tests/test_verify_step.py` and `tests/test_triage_feedback.py` (`_run_git`, `_run_script`, `_triage_lines`) — Test: independence

The subprocess environments copy `os.environ` and override only
`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM`. If the suite ever runs under a
git hook, an inherited `GIT_DIR`, `GIT_INDEX_FILE` or `GIT_WORK_TREE` would
point `git init`, `add`, `mv` and `commit` at the outer repository instead of
`tmp_path`. It would also defeat `test_git_status_failure_exits_2`'s
`GIT_CEILING_DIRECTORIES`. I found no current trigger: this repo's
`.git/hooks/pre-commit` only execs the gitlore gate. The same pattern already
exists in `tests/review_range_helpers.py`, so these tests inherit it rather
than introduce it.

### F-6 — Minor — `plugin/bin/triage-feedback.sh` (classification extraction) — Universal: excess

The `\s` → `[[:space:]]` change in the `grep -E` and `sed -E` that extract
`classification` is not specified by KD-3 or Item 1.1. It came in as a
code-review fix in commit `7cc0e5c2`. It is a portability improvement, since
`\s` is not POSIX ERE. It is untestable on this GNU box, so any behavioural
difference on BSD is unverified.

## Verified conformant

Every item below was checked by a probe or test run:

- **`reports_count` (KD-3).** It excludes exactly `review.md`, `review-*.md`
  and `final-review.md`, on top of the pre-existing `design-review*`,
  `outline-review*` and `recall-*`. Probe: I built a reports dir holding
  `review.md`, `review-skill.md`, `review-report.md`, `final-review.md`,
  `review-a b.md`, `review-nl<LF>x.md`, `review-x.txt`, `review.md.bak`,
  `final-review-2.md`, `phase-1-corrector.md`, `item-1-1.md`, `tdd-audit.md`,
  `deliverable-review.md` and `item<LF>nl.md`. The script reported
  `- Reports: 8`: the first six were excluded and the rest counted. The
  newline-safe `-exec printf x \; | wc -c` count holds.
- **The `review-*` glob.** Per `dispatch-composition.md` §Naming, it catches
  no `/build` execution dispatch name. Execution names are `item-…`,
  `phase-P-corrector` and `tdd-audit`. It does additionally exclude
  `/review`'s `plans/<job>/reports/review-report.md`
  (`plugin/skills/review/SKILL.md` §5). That fits KD-3's rationale, since the
  file records a review and not execution, though the script comment names
  only review-gate and closing-review reports. I recorded this as an
  observation, not a finding.
- **`verify-step.sh` against KD-7:**
  - The status is taken with `--untracked-files=all`.
  - The three exemptions hold in any XY state except `R`/`C` (see F-3).
  - DIRTY echoes the non-exempt porcelain lines verbatim.
  - A rename out of an exempt path is DIRTY (`R  inbox/a.md -> notes.md`), and
    so is a rename into one (`R  README -> inbox/x.md`).
  - Quoted paths are exempt when they are `*.md` under `inbox/`: space,
    non-ASCII (`"inbox/\303\251.md"`), embedded quote, embedded newline and a
    literal ` -> ` in the name all gave CLEAN.
  - A crafted `inbox/a.md" -> "b.txt` is DIRTY.
  - `inbox/x.txt`, `inbox/sub/x.md` and `.claude/handoffs/x` are DIRTY.
    `.claude/handoff-x.md` is CLEAN.
  - Submodule dirty content (modified or untracked inside `memory/`) shows as
    ` M memory` under porcelain v1 and gives CLEAN.
  - `status.branch=true` and `status.showStash=true` add no lines to
    `--porcelain`.
- **Error signalling.** A `git status` failure exits 2 with
  `ERROR: git status failed`. A missing `just` exits 2. A filter failure exits
  2. A clean tree with an empty porcelain reaches `just precommit`, which the
  `test_missing_just_exits_2` path confirms.
- **Test runs.** `pytest tests/test_triage_feedback.py tests/test_verify_step.py`
  gave 7/7 passed. I ran `.venv/bin/python -m pytest` directly because
  `uv run` could not write its cache in the sandbox.
- **Mutation reds, as the outline specifies:**
  - `test_triage_feedback` fails against `d444630c`'s script.
  - Against `31fe4a16`'s script, the four Item 1.2 slice-2 tests fail and the
    two slice-1-level tests pass.
  - Against `d444630c`'s script, all tests fail except
    `test_rename_out_of_exempt_path_is_dirty`, which is expected: the base
    treated everything as dirt.
- **Test specificity.** The triage test's second phase
  (`item-1-1-s1-code-review.md` → `Reports: 1`) catches an over-broad
  `*review*` exclusion. The verify-step decoys (`.claude/notes.md`,
  `.claude/handoff-notes.txt`, `inbox/notes.txt`, `memory.md`,
  `"inbox/my notes.txt"`) catch over-broad exemptions and a missing
  `--untracked-files=all`.
- **`justfile` `run-pytest` sentinel.** Adding `plugin/skills/build/scripts/`
  makes `verify-step.sh` a hash input. `triage-feedback.sh` was already
  covered by `plugin/bin/`, and the new tests by `tests/`. The hunk is correct
  and sufficient.

## Observation outside assigned files

The range also changes the `justfile` `clean` recipe, from commit `18890cfc`
(`.bin/claude` dist/plugin sync, touching `.bin/claude`, `.gitignore` and
`memory`). No outline item names it. I did not review it; it is flagged for the
Layer 2 excess check.
