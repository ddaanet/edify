# Item 1.2 / Slice 1 — RED

`test_conventional_dirt_is_clean_and_other_dirt_is_not` in
`tests/test_verify_step.py`.

## Mode

No stub written. Item 1.2 is slice 1 of the item and the SUT
(`plugin/skills/build/scripts/verify-step.sh`) already exists with the
pre-fix behaviour the slice targets (KD-7: the script exempts only
` M memory`, so a staged `.claude/handoff-task.md` and an untracked
`inbox/` both count as dirt). The RED procedure's inert-stub step applies
only when the SUT does not exist; here it does, and the item's own SUT note
predicts the red directly ("the first assertion (exit 0 / `CLEAN:`) should
red with no stub"), so the test reds against the unchanged script with no
mutation needed.

## Test run

```
PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_verify_step.py -v
```

1 failed, 0 passed.

### `test_conventional_dirt_is_clean_and_other_dirt_is_not`

Failed on its own assertion (not ImportError/AttributeError):

```
tests/test_verify_step.py:110: in test_conventional_dirt_is_clean_and_other_dirt_is_not
    assert result.returncode == 0, result.stdout + result.stderr
AssertionError: DIRTY: uncommitted changes
  M  .claude/handoff-task.md
  ?? inbox/

assert 1 == 0
 +  where 1 = CompletedProcess(args=['/Users/david/code/edify/plugin/skills/build/scripts/verify-step.sh'], returncode=1, stdout='DIRTY: uncommitted changes\nM  .claude/handoff-task.md\n?? inbox/\n', stderr='').returncode
```

The script's `git status --porcelain` (no `--untracked-files=all`) collapses
the untracked `inbox/` directory to one line and applies no exemption for
either that line or the staged, modified `.claude/handoff-task.md` — only
` M memory` is filtered — so it reports `DIRTY:` and exits 1 where the slice
requires `CLEAN:` and exit 0. This is exactly the KD-7 gap the item exists to
close, on the first named assertion, for the named reason. Because pytest
halts a test function at its first failing assertion, the later DIRTY-branch
assertions (`?? stray.txt` present, no line naming `inbox/`) did not get a
chance to run in this dispatch; the single test still reds genuinely, since
the failure above is on real behaviour, not a missing symbol.

Confirmed by direct probe that the fixture actually exercises the
`--untracked-files=all` distinction GREEN must add: `git status --porcelain`
on a repo with only `inbox/brief.md` untracked prints `?? inbox/` (collapsed),
while `git status --porcelain --untracked-files=all` prints
`?? inbox/brief.md` (exploded) — the exemption GREEN adds must match the
exploded form since the outline requires the status be taken under
`--untracked-files=all`.

## Mutation proof

Not needed. The behaviour the test pins (the KD-7 `.claude/handoff-*.md` and
`inbox/*.md` exemptions, and the `--untracked-files=all` status mode) is
*absent* from the current SUT — inspection of `verify-step.sh` shows only a
single `grep -vx ' M memory'` filter over a bare `git status --porcelain` —
so ordering alone supplies the red per `genuine-red.md`'s stub-then-assert
rule; no mutation is required to manufacture an absence that already exists.
No mutation was performed and none restored.

## Fixtures tried and rejected

- **Passing the stub `just`'s marker path via an environment variable read
  inside the stub script.** Rejected in favor of baking the absolute marker
  path directly into the stub's file content at write time (an f-string),
  removing one moving part (no extra env var to thread through
  `subprocess.run`'s `env=` for both the setup git calls and the script run).
- **Two separate test functions, one for the CLEAN case and one for the
  DIRTY case.** Rejected: the slice names one test,
  `test_conventional_dirt_is_clean_and_other_dirt_is_not`, as a single
  continuous scenario (clean tree, then add `stray.txt`, same repo) — a two-
  test rewrite would need to duplicate the whole CLEAN setup for the DIRTY
  half and no longer matches the slice text.
- **`"inbox/" not in result.stdout` (whole-output substring) instead of a
  per-line `not any(...)` check for "not naming `inbox/`".** Both catch
  `?? inbox/` and `?? inbox/brief.md` per the scope note. Kept the per-line
  form to match the sibling test's and D-21's house preference for
  whole-line comparison over substring matching, and because a per-line
  check pinpoints the offending line in the failure message rather than
  dumping the whole stdout blob.
- **Asserting `"DIRTY:" in result.stdout` (substring) instead of
  `lines[0] == "DIRTY: uncommitted changes"` (whole line).** Rejected per
  the DIRTY-substring vacuous-green shape in `vacuous-green.md`: a substring
  match on `"DIRTY:"` would also pass if the script's header text changed
  around it or if `DIRTY:` appeared inside a later data line; anchoring on
  the exact first line is unambiguous and still fails for the right reason
  here (the actual first line is that same string, but the test never gets
  that far — it reds one assertion earlier).
- **Reusing `tests/test_triage_feedback.py`'s `_run_git`/`_init_repo` via
  import instead of local copies.** Rejected: that module keeps its helpers
  private (no `__all__`/export convention, no shared `conftest.py` fixture
  for git-repo setup across these two scripts' tests), and the two scripts'
  fixtures diverge immediately (this one needs a `.claude/handoff-task.md`
  committed up front so it can later be modified and staged, which the
  triage fixture has no need for), so a shared helper would need
  parameterizing for a single caller — not worth the indirection.
- **Stubbing `just` by mutating the test process's own `os.environ["PATH"]`
  instead of passing a modified `env=` dict to `subprocess.run` for the
  script call.** Rejected: mutating the test process's environment leaks the
  stub across any other code running in-process during the test and after
  it if not carefully restored; passing `env=` to the one `subprocess.run`
  call that launches the script keeps the stub scoped to that single
  invocation.
