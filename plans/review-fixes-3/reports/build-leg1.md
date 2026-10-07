# Build leg 1 — review-fixes-3

`/build plans/review-fixes-3/outline.md`, run fresh (no `item-*` report on
disk at start). The entry gate was `CLEAN`. Recall read the artifact's eight
files, plus `edify-commit-hook-gotchas` and `cc-subagent-approval`.

## Completed

| Item | Commits (subjects) | Reports |
|---|---|---|
| 1.1 split `test_changed_files.py` | `Item 1.1 — split test_changed_files.py on its exit-code seam` | `item-1-1.md` |
| 1.2 split `test_triage_feedback.py` | `Item 1.2 — split test_triage_feedback.py on its failure seam` | `item-1-2.md` |
| 2.1/1 late diff failure prints `ERROR:` alone | `Item 2.1/1 — changed-files.sh prints ERROR: alone on a late diff failure`; `Item 2.1/1 — code-review fixes`; `Item 2.1/1 — list revision` | `item-2-1-s1-{red,test-review,green,code-review}.md` |

Every committed step was followed by a `verify-step.sh` run, and each one was
`CLEAN`. Items 1.1 and 1.2 kept their collected test counts, 15 and 23. Item
2.1's RED was genuine, with no mutation needed.

## Run summary notes

- **2.1/1's code review found a critical regression and fixed it.** GREEN
  moved the `case` into `paths=$(…)`, and bash 3.2 (macOS `/bin/bash`) cannot
  parse a bare pattern's `)` there. The fix is a leading `(` on the pattern.
  The reviewer also kept the exit-0 output byte-identical with an `x`
  sentinel. The reviewer built upstream bash 3.2.57 from the GNU tarball, at
  `/tmp/claude-1000/bash32/bin/bash`. That is scratch space, so it may not
  survive.
- **List revision after 2.1/1**, in the outline:
  - Item 2.2 now requires a bash 3.2 check, where a 3.2 binary is available.
  - Item 2.3's shims embed the real tool's path with `shlex.quote`.
  - Item 4.1's D-90 bullet adds "`ERROR:` alone".
- **Wording nit for the review gate.** Item 1.1 rewrote a docstring in
  `tests/test_changed_files.py`, around line 214, to "D-90 reads the diff
  NUL-delimited". A decision does not read anything, and "The list is read
  NUL-delimited (D-90)" would be better. It was left for the review gate.
- **Item 1.2 kept two `KD-3` strings** in `tests/test_triage_feedback.py`, at
  lines 264 and 276. They are fixture label values that the test asserts
  verbatim, not citations.

## Open question for my human partner

1. 2.1/1's code review found a macOS defect that predates this job: with
   `exempt-paths.sh` absent, bash 3.2 makes the failed `source` in
   `changed-files.sh` fatal and exits 1, which is `NO-BASE:`'s code.
   `test_unloadable_exempt_paths_is_an_error_not_no_base[absent]` fails under
   bash 3.2. The upstream-built binary showed this; it has not been checked on
   a real Mac. It falls outside m1–m18. **Default:** leave it out of this
   job, and record it as a defect of its own. A related gap: nothing in the
   suite runs under bash 3.2. That also goes to my human partner, as a
   tooling item with no scope added here.

## Current state

`main` is clean, apart from the two untracked `inbox/brief-*.md` files, which
belong to another session. `just precommit` is green.

## Next leg resumes at

**Item 2.2, slice 1 RED** (`test_subdirectory_run_measures_the_repository_root`).
The resume test finds `item-*` reports, so it is a resume: follow
`references/escalation.md` §Resuming. Still to do: Items 2.2 (two slices),
2.3 (three slices), 2.4, then 3.1–3.6 and 4.1, then Finish
(`references/finishing.md`).

Dispatch notes the orchestrator relied on:

- Tell every dispatch to set `dangerouslyDisableSandbox: true` for
  git/just/pytest, since a hook refuses them when sandboxed.
- Tell it to run `PATH=…/.venv/bin:$PATH just precommit` in the foreground.
- Tell it to count tests with `pytest -p no:markdown_report`.
- Point a skill body at `~/.claude/plugins/cache/ddaanet/<plugin>/<newest>/…`,
  because test-driver, artisan and corrector have no `Skill` tool.
- `just precommit` may report `Tests cached` right after a dispatch ran it.
  Run the touched modules directly to confirm.
