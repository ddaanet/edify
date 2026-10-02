# build-fixes — leg 1 report

Run started fresh at `d415f22d`; `tmp/build-baseline` holds
`d415f22daf94eb5ae5424a927e126f4010ff7a21`. Entry gate: `verify-step.sh` exit 0
(CLEAN). Recall ran: the artifact's four memory files, plus
`edify-commit-hook-gotchas.md` from the index; skills `craft:test-discipline`
and `shell-scripting:shell-gotchas` loaded. `craft:design-doc-writing` was not
loaded yet; it is for Item 2.14.

**Stopped at a design question about Item 2.3. It is set out at the end of this
report.**

## Items completed

Each slice was four dispatches: RED (sonnet), test review (opus), GREEN
(sonnet), code review (opus). The orchestrator committed each code review.
Post-item `verify-step.sh` came back exit 0 after every commit.

| Item | Commits |
|---|---|
| 1.1/1 | `✅ Item 1.1/1 — exempt paths clean in any porcelain state`; `✅ Item 1.1/1 — code-review fixes` |
| 1.1/2 | `✅ Item 1.1/2 — nested path under exempt dir is dirty`; `🐛 Item 1.1/2 — code-review fixes` |
| 1.2/1 | `✨ Item 1.2/1 — base is parent of first item report commit`; `🐛 Item 1.2/1 — code-review fixes` |
| 1.2/2 | `✨ Item 1.2/2 — exempt paths committed in the run are dropped`; `🐛 Item 1.2/2 — code-review fixes` |
| 1.2/3 | `✨ Item 1.2/3 — no item report exits 1`; `🐛 Item 1.2/3 — code-review fixes` |
| 1.3/1 | `🐛 Item 1.3/1 — files changed counts committed changes only`; `🐛 Item 1.3/1 — code-review fixes` |
| 1.3/2 | `🐛 Item 1.3/2 — uncommitted definition is not behavioral`; `🐛 Item 1.3/2 — code-review fixes` |
| 2.1 | `📝 Item 2.1 — build hub resume test, review before the item commit` (SKILL.md 200 → 193 lines) |
| 2.2 | `📝 Item 2.2 — escalation: dirt examined and finished, resume by report history` |

Every slice report and item report is under `plans/build-fixes/reports/`
(`item-1-*-s*-{red,test-review,green,code-review}.md`, `item-2-1.md`,
`item-2-2.md`). List revision: none. The job has no runbook.

## Items remaining

2.3 (blocked, see the question below), then 2.4 to 2.14, then §5 Finish. The
work has no phases, so §5 is the only semantic review left: the review gate,
triage, the TDD audit and completion. Items 2.1 to 2.4 went to one opus artisan,
which committed 2.1 and 2.2 and stopped before 2.3. It can be resumed by
`SendMessage` with the answer; it holds the context for 2.3 and 2.4.

## Gate results

- `just precommit` is green at HEAD (`2aa3e000`): 374/375 passed, 1 xfail. The
  three `oversized-file` lines for the `*-corrector.md` agents were there before
  this run and are allowlisted.
- `just lint` fails on `tests/line_limits_helpers.py:32` RUF100. It fails at the
  baseline too. `lint` passes `--ignore=PLR0913`, so the file's
  `# noqa: PLR0913` reads as unused there, while `precommit` enables PLR0913.
  This was not acted on; it is a candidate for a separate fix.
- Some executors' full-suite runs reported 16 skipped
  (`test_full_pipeline_remark`, skipped when `remark` is not on PATH). The
  gate's own runs report 1 xfail and no skips, so this depends on PATH.

## Deviations

1. **Which skill text governed.** The Skill tool loaded
   `dist/plugin/skills/build/`. That is a gitignored, stale build copy and
   predates the build-defects fixes. Its references have no `tmp/build-baseline`
   resume and no reports-exist rule. The rules you named (baseline file,
   reports-exist resume) exist only in `plugin/skills/build/` at `d415f22d`, so
   I followed that text. I snapshotted it to `/tmp/claude-1000/build-rules/`, so
   the job's own edits did not change the rules mid-run. A fresh delegate can
   read the same text with `git show d415f22d:plugin/skills/build/<file>`.
2. **Unnamed dispatches**, per your instruction, against the skill's naming
   rule. I resumed agents by agent id.
3. **Item 1.1's mutation proof.** Following the item text, the mutant was a copy
   under `/tmp/claude/build-fixes/` with `SCRIPT` rebound through a throwaway
   pytest plugin. `tdd-slice.md` says to mutate in place, but the item text
   governed.
4. **Code reviews with no implementation change** (1.1/1, 1.1/2). I still
   dispatched them, scoped to `verify-step.sh`. The 1.1/2 review found a real
   fail-open. With a user's `core.quotePath=false`, an invalid UTF-8 byte in a
   dirty path makes grep drop the line, and the gate read CLEAN. The fix,
   `git -c core.quotePath=true status`, is committed but **no test pins it**.
   The reviewer's suggested test: repo-local `core.quotePath false`, an
   untracked `inbox/x\377/y.md`, expect exit 1, skipped on macOS. It is not in
   any outline item. It needs your call, or the review gate's.
5. **I fixed a test file in session.** `tests/test_changed_files.py`'s `_commit`
   docstring failed D205 once `docformatter` had wrapped it. GREEN may not edit
   tests, so I fixed it before GREEN committed. The 1.2/1 GREEN report records
   this.
6. **Item 1.3/1's expected count is 3, not 1.** The test review added a second
   commit after the baseline. With only one, `HEAD~1..HEAD`, `--cached` and a
   hardcoded 1 all passed.
7. **Fixes made in code review, beyond the slice text**:
   - `changed-files.sh` rejects job names that are unsafe as pathspecs, works
     from a subdirectory, passes `--no-show-signature`, turns rename detection
     off, and reports exit 2 when the source fails or the variable is unset.
   - `triage-feedback.sh`: a failing `git diff` no longer reads as "no
     behavioral code".

   Details are in each `*-code-review.md`.
8. **Executor notes on 2.1 and 2.2**, for the review gate:
   - `escalation.md` §Resuming step 2 stands in for `SKILL.md` §2's gate on a
     resumed run.
   - A `PRECOMMIT:` verdict over a clean tree got its own resume-message
     variant.
   - `escalation.md` points to `phase-boundary.md` for the landed-boundary
     query. That query does not exist until Item 2.3 lands.

## Pending question: the phase P>1 changed-files list (Item 2.3)

Item 2.3 says that at a phase boundary the changed-files list comes from
`changed-files.sh` (KD-6), with phase P>1's base set by KD-2's report-path
query. But `changed-files.sh <job>` always diffs from the run's base (KD-1), and
nothing lets a caller pass another base. That gives phase 1 the right list and
gives phase P>1 every earlier phase's files too. A bare
`git diff --name-only <phase base> HEAD` brings back the exempt paths and
`plans/<job>/`, which is the m1 defect. KD-6 rejected spelling the filter out in
prose at each site. The outline does not settle this, so it is a design
decision.

1. **Optional base argument (recommended default).**
   `changed-files.sh <job> [<base>]`, where `<base>` overrides the KD-1
   derivation and still prints `BASE:`. This needs a new tdd item before 2.3:
   one slice, a test in `tests/test_changed_files.py`, and the outline's Item
   1.2 interface amended. 2.3 then calls `changed-files.sh <job> <phase base>`
   for P>1. It keeps the mechanical filter in the script.
2. **Intersection in prose.** Phase P>1 keeps the paths that appear both in
   `changed-files.sh <job>` and in `git diff --name-only <phase base> HEAD`. No
   script change. The cost is mechanical filtering in prose, and a path a later
   phase reverted to its run-base content drops out.
3. **Hand filtering.** Use `git diff --name-only <phase base> HEAD` and drop the
   exempt and `plans/<job>/` paths by hand. KD-6 rejects this.

If you answer option 1, I add the item as **Item 1.4** with one slice,
`test_explicit_base_overrides_derivation`: a run with item reports over two
phases, where `changed-files.sh j <phase-2 base>` prints `BASE: <phase-2 base>`
and only phase 2's files. I run it through the four slice dispatches, amend the
outline's Item 1.2 interface line in the same commit, then resume the artisan
for 2.3 and 2.4.
