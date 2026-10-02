# Item 1.2 / slice 2 — GREEN report

## Scope

Grow `plugin/skills/build/scripts/changed-files.sh` and
`plugin/skills/build/scripts/verify-step.sh` to drop the exempt paths
`exempt-paths.sh` names, and create `exempt-paths.sh` itself (KD-6). The
batch is slice 2's one failing test,
`test_exempt_paths_committed_in_the_run_are_dropped`; slice 3's `NO-BASE:`
exit-1 path and Item 1.3 (`triage-feedback.sh`) are out of scope and
untouched.

## Implementation, one step at a time

1. **Created `plugin/skills/build/scripts/exempt-paths.sh`** — a sourced,
   shebang-less file (`# shellcheck shell=bash` instead; not executable as a
   command) defining one variable, `EXEMPT_PATHS_ALTERNATION`, holding the
   bare unanchored ERE alternation `memory|\.claude/handoff-[^/]+\.md|
   inbox/[^/]+\.md`. The comment explaining the three conventional paths
   (gitlore submodule, `/handoff`/`/precompact` artifacts, dropped briefs)
   moved here from `verify-step.sh`'s header; each script keeps its own
   porcelain- or diff-specific notes.
2. **`verify-step.sh` sources it** by `${BASH_SOURCE[0]}`'s directory,
   computed with bash parameter expansion
   (`case "${BASH_SOURCE[0]}" in */*) script_dir="${BASH_SOURCE[0]%/*}" ;; esac`)
   rather than the external `dirname` command — ran this first and it broke
   `test_missing_just_exits_2`, which stubs a minimal PATH carrying only
   `bash`, `git` and `grep`; switched to pure parameter expansion and the
   test passed. The existing pattern `^[^RC][^RC] "?(<alt>)"?$` is now
   composed from the sourced `EXEMPT_PATHS_ALTERNATION`, concatenating
   single- and double-quoted segments so the variable's own backslashes are
   never reinterpreted; verdicts are byte-identical to the pre-extraction
   pattern. A sourcing failure exits 2 with `ERROR: cannot source
   exempt-paths.sh`.
3. **`changed-files.sh` sources the same file the same way** and builds
   `exempt_re='^('"${EXEMPT_PATHS_ALTERNATION}"')$'`. The NUL-delimited
   `git diff -z` read loop (`while IFS= read -r -d '' path`) now tests each
   path with bash's `[[ $path =~ $exempt_re ]]` before printing it — no
   second grep pass, so no NUL-handling concern — alongside the pre-existing
   `plans/$job/` prefix drop. `[[ =~ ]]` with the pattern held in a variable
   is bash-3.2-safe (`shell-scripting:shell-gotchas`).

Order run, one test at a time:

1. `tests/test_changed_files.py::test_exempt_paths_committed_in_the_run_are_dropped`
   — FAILED on first attempt (missing `exempt-paths.sh`, since the sourcing
   lines in `changed-files.sh` were added before the file existed) — wrote
   `exempt-paths.sh`, then PASSED.
2. `tests/test_verify_step.py::test_missing_just_exits_2` — FAILED after the
   first `dirname`-based `script_dir` resolution (`dirname: command not
   found` under the test's minimal stubbed PATH) — switched to parameter
   expansion, then PASSED.
3. Full suite, see below.

## Test runs

```
PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest tests/test_changed_files.py -vv
```
→ 2/2 passed (`test_base_is_parent_of_first_item_report_commit`,
`test_exempt_paths_committed_in_the_run_are_dropped`).

```
PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest tests/test_verify_step.py -vv
```
→ 8/8 passed, unchanged (`test_conventional_dirt_is_clean_and_other_dirt_is_not`,
`test_memory_gitlink_is_clean_and_a_sibling_name_is_not`,
`test_rename_out_of_exempt_path_is_dirty`, `test_quoted_exempt_path_is_clean`,
`test_exempt_paths_clean_in_any_porcelain_state`,
`test_nested_path_under_exempt_dir_is_dirty`, `test_git_status_failure_exits_2`,
`test_missing_just_exits_2`).

```
PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest
```
→ 356/372 passed, 16 skipped, 0 failed.

## Shellcheck

```
cd plugin/skills/build/scripts && PATH=.../.venv/bin:$PATH shellcheck -x -s bash verify-step.sh changed-files.sh exempt-paths.sh
```
→ clean (no output). Run from the scripts' own directory with `-x` so the
`# shellcheck source=exempt-paths.sh` directive resolves; run from the repo
root, shellcheck emits an informational `SC1091 Not following:
exempt-paths.sh: … does not exist` on the dynamic `source
"$script_dir/exempt-paths.sh"` line in both `verify-step.sh` and
`changed-files.sh` — an artifact of shellcheck resolving `source=` relative
to its own invocation cwd rather than the target script's directory, not a
defect in either script.

```
PATH=.../.venv/bin:$PATH shellcheck plugin/skills/build/scripts/exempt-paths.sh
```
→ clean.

## Gate recap

```
just lint
```
→ `tests/line_limits_helpers.py:32:30: RUF100 [*] Unused noqa directive
(non-enabled: PLR0913)`, "Lint failed". This is the pre-existing, known
finding named in the dispatch — recorded, not acted on; unrelated to this
slice's files.

```
just precommit
```
→ `✓ Precommit OK` (version consistency, tests, line limits, design links
all ran; line-limits reported three pre-existing allowlisted overages —
`plugin/agents/corrector.md`, `outline-corrector.md`, `design-corrector.md`
— none of them this slice's files).

`tmp/.test-sentinel`: `2521397377 580941`

## Out of scope, confirmed untouched

- Slice 3's `NO-BASE:` exit-1 path in `changed-files.sh` — not implemented.
- `plugin/bin/triage-feedback.sh` (Item 1.3) and every prose item.

## Files

- `plugin/skills/build/scripts/exempt-paths.sh` (new)
- `plugin/skills/build/scripts/verify-step.sh` (modified: sources
  `exempt-paths.sh`, composes its pattern from it)
- `plugin/skills/build/scripts/changed-files.sh` (modified: sources
  `exempt-paths.sh`, drops matching paths in the NUL-delimited read loop)
