# GREEN: Item 1.2 / Slice 2 — F-1/F-2 pinning tests

**Mode**: GREEN, confirm-and-commit. `plugin/skills/build/scripts/verify-step.sh`
is OUT for this dispatch — the behaviour under test (F-1: rename/copy guard,
quoted-path allowance, `git status` failure exit code; F-2: missing-`just`
exit code) is already implemented and committed at `4a24c0fe`. **No SUT edit
was made.**

## SUT untouched — evidence

```
git status --porcelain --untracked-files=all -- plugin/skills/build/scripts/verify-step.sh
```

produced no output (empty), confirming the tracked script carries no diff.

## Test run

`PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_verify_step.py -v`:

```
5/5 passed
- test_conventional_dirt_is_clean_and_other_dirt_is_not
- test_rename_out_of_exempt_path_is_dirty
- test_quoted_exempt_path_is_clean
- test_git_status_failure_exits_2
- test_missing_just_exits_2
```

All five pass against the tracked, already-implemented script. No
implementation growth was needed or performed; this run reconfirms the RED
report's and the test review's post-fix verification against the tracked
file, in the GREEN dispatch's own sandbox.

## `just precommit` — full output

Run with the sandbox disabled (needed for the gitlore hook path):

```
# version consistency
Version consistent: 0.3.0
# Test Report

**Summary:** 366/367 passed, 1 xfail
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

Gate verdict: **Precommit OK**. The line-limit warnings on
`plugin/agents/corrector.md`, `plugin/agents/outline-corrector.md` and
`plugin/agents/design-corrector.md` are pre-existing and out of this slice's
scope (per the GREEN-mode rule that precommit warnings are the code review's
judgement call, not this dispatch's) — this slice touched no agent
definitions.

## Sentinel hash

`tmp/.test-sentinel`: `605277097 563628`

## Commit scope

No implementation file changed. This commit carries only:
`tests/test_verify_step.py`, and the RED, test-review and this GREEN report
for slice 2.
