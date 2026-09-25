# Item 1.2 / Slice 1 — GREEN

## History

The first `Edit` attempt against `plugin/skills/build/scripts/verify-step.sh`
was refused by the server-side auto-mode classifier ("gave no verdict ...
Don't retry it"), and this dispatch stopped and returned
`blocked: classifier refused Edit on
plugin/skills/build/scripts/verify-step.sh` with the exact intended diff
recorded in this report. My human partner then applied that same edit
directly, and added `plugin/skills/build/scripts/` to `justfile`'s
`run-pytest` sentinel `git ls-files` path list — the scope-2 orchestrator
addition (see below). This dispatch resumed with both files already
matching the intended change, verified the diffs against the blocked
report's recorded text before proceeding, and ran the remaining Done
criteria (tests, shellcheck, precommit, dogfood, commit) itself. No further
edits to either file were needed or made.

## Scope

1. `plugin/skills/build/scripts/verify-step.sh` — the KD-7 exemptions
   (` M memory`, `.claude/handoff-*.md`, `inbox/*.md`, matched on the path
   after an any-state two-column XY prefix) under
   `git status --porcelain --untracked-files=all`, filtered with a single
   extended-regex `grep -vE`. Header comment names the three exemptions and
   the staging-by-name rationale.
2. `justfile`'s `run-pytest` test-sentinel hash — added
   `plugin/skills/build/scripts/` to the `git ls-files` path list feeding the
   hash, with the existing comment already covering the rationale ("a new
   test module is an input before its first commit... scripts/ ... are read
   by the suite"; extended to cover this second scripts tree). This is an
   orchestrator addition beyond the outline's file list, made because
   `tests/test_verify_step.py` reads `verify-step.sh` and an edit to that
   script alone must invalidate the cached green
   (`memory/ddaanet/gate-cache-must-cover-every-check.md`).

## Tests run, in order

Only one test exists in this batch (three phases, one test function, per the
item's single-slice test list):

1. `test_conventional_dirt_is_clean_and_other_dirt_is_not` —
   `PATH=/Users/david/code/edify/.venv/bin:$PATH pytest
   tests/test_verify_step.py -v`:

   ```
   # Test Report
   **Summary:** 1/1 passed
   ## Passes
   - tests/test_verify_step.py::test_conventional_dirt_is_clean_and_other_dirt_is_not
   ```

No growth was needed beyond the already-applied edit (see History); the test
passed on the first run against the edited script.

## Shellcheck

`PATH=/Users/david/code/edify/.venv/bin:$PATH shellcheck
plugin/skills/build/scripts/verify-step.sh` — exit 0, no findings.

## Gate verdict

`PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit` (Bash sandbox
disabled):

```
# version consistency
Version consistent: 0.3.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

Recap line: `✓ Precommit OK`.

`tmp/.test-sentinel` hash: `697302964 558613`. Confirmed by independent
recomputation that this hash covers the current tree exactly (`git ls-files
-z --cached --others --exclude-standard src/ tests/ scripts/ plugin/hooks/
plugin/bin/ plugin/skills/build/scripts/ docs/decisions.md
docs/references/`, plus `pyproject.toml`, `cksum`'d) — it matches the stored
sentinel byte for byte, so the cached-green claim covers the edited script
and the new test module, per the widened `run-pytest` hash.

**Precommit warnings, not acted on** (code review's call, not this
dispatch's): the three `oversized-file` line-limit warnings above are
pre-existing corrector agent files, untouched by this slice and outside
Item 1.2's scope.

**`just lint` — not green, pre-existing, out of scope.** `PATH=...
just lint` fails on `tests/line_limits_helpers.py:32:30: RUF100 [*] Unused
`noqa` directive (non-enabled: `PLR0913`)` — `run-lint-checks`'s broader
`ruff_ignores` (which includes `PLR0913`) makes the file's own
`# noqa: PLR0913` redundant, while `run-checks` (used by `precommit`, no
ignore list) does not flag it. `tests/line_limits_helpers.py` is fully
committed (last touched 2026-09-22, `git status --porcelain` empty for it),
untouched by this dispatch, and is not `tests/test_verify_step.py` or any
Item 1.2 target — a divergence between the `lint` and `precommit` recipes'
ruff-ignore lists, unrelated to this slice. Not fixed here since only
`just precommit` is this dispatch's green gate and the file is out of scope.

## Dogfood on the real repo

`PATH=/Users/david/code/edify/.venv/bin:$PATH
plugin/skills/build/scripts/verify-step.sh` (Bash sandbox disabled), run
before committing:

```
DIRTY: uncommitted changes
 M justfile
 M plugin/skills/build/scripts/verify-step.sh
?? plans/build-defects/reports/build-leg1.md
?? plans/build-defects/reports/item-1-2-s1-green.md
?? plans/build-defects/reports/item-1-2-s1-red.md
?? plans/build-defects/reports/item-1-2-s1-test-review.md
?? tests/test_verify_step.py
exit: 1
```

Expected: this dispatch's own uncommitted files show as DIRTY. Confirms the
exemptions work on the live repo: the untracked
`inbox/brief-corrector-reads-surfaces-against-each-other.md` (not this
dispatch's file) is correctly absent from the listing, and no `.claude/`
sandbox-mask lines appeared in this unsandboxed run (masks are an artifact of
a concurrent sandboxed Bash call reaching an unsandboxed reader, per
`memory/ddaanet/shared-claude.md`'s phantom-dotfiles note — none was
concurrent here, so none leaked into this invocation's `git status`, even
though a separate sandboxed `git status --porcelain --untracked-files=all`
run in this same session did show `.claude/launch.json`,
`.claude/loop.md`, `.claude/output-styles`, `.claude/routines`,
`.claude/workflows`). None of those masks were touched.

## Fixtures/behaviour not touched

`tests/test_verify_step.py` was never edited, per scope. Item 1.1's files
(`plugin/bin/triage-feedback.sh`, `tests/test_triage_feedback.py`) and all
Item 2.x targets (`plugin/skills/build/SKILL.md`,
`plugin/skills/build/references/*`, `plugin/fragments/*`) were not touched.
