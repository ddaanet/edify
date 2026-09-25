# RED: Item 1.2 / Slice 2 — F-1/F-2 pinning tests

**Scope**: four new tests added to `tests/test_verify_step.py`, pinning
`31fe4a16`'s code-review F-1 (rename/copy guard, quoted-path allowance,
`git status` failure exit code) and F-2 (missing-`just` exit code), both
already committed at `4a24c0fe`. `plugin/skills/build/scripts/verify-step.sh`
was not touched.

**Mode**: RED, mutation-red variant per the dispatch's "How to prove red"
(the behaviour is already implemented, so red is proved against a
pre-F-1 mutant copy, never by reverting the tracked file).

## Tests added

- `test_rename_out_of_exempt_path_is_dirty`
- `test_quoted_exempt_path_is_clean`
- `test_git_status_failure_exits_2`
- `test_missing_just_exits_2`

`_run_script` gained an optional `extra_env: dict[str, str] | None` parameter,
applied after the `PATH`-prepend line so a `PATH` key in `extra_env` replaces
it outright (needed by `test_missing_just_exits_2` to exclude the real `just`
from `PATH` entirely, and by `test_git_status_failure_exits_2` to set
`GIT_CEILING_DIRECTORIES`). No other helper was duplicated. File is 258
lines, under the 400-line cap.

## Per-test output against the tracked script (plain pytest)

`PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_verify_step.py -v`:

```
5/5 passed
- test_conventional_dirt_is_clean_and_other_dirt_is_not
- test_rename_out_of_exempt_path_is_dirty
- test_quoted_exempt_path_is_clean
- test_git_status_failure_exits_2
- test_missing_just_exits_2
```

All five pass against the tracked (post-F-1/F-2) script, as expected — the
behaviour is already implemented.

## Mutation proof

Setup (`tmp/` is gitignored, `verify-step.sh` never touched):

```
mkdir -p tmp/mutants
git show 31fe4a16:plugin/skills/build/scripts/verify-step.sh > tmp/mutants/pre-f1.sh
chmod +x tmp/mutants/pre-f1.sh
cp plugin/skills/build/scripts/verify-step.sh tmp/mutants/current.sh
chmod +x tmp/mutants/current.sh
```

`tmp/mutants/rebind.py`, a scratch pytest plugin, rebinds the test module's
`SCRIPT` to `$MUTANT` in `pytest_collection_modifyitems`, run as:

```
MUTANT=tmp/mutants/<file> PYTHONPATH=tmp/mutants pytest -p rebind tests/test_verify_step.py -v
```

### Control: `current.sh` (identical copy of the tracked script) via rebind

`MUTANT=tmp/mutants/current.sh`: **5/5 passed** — same five tests as above.
Proves the rebind harness itself introduces no breakage.

### Mutant: `pre-f1.sh` (`31fe4a16`'s script, pre-F-1/F-2) via rebind

`MUTANT=tmp/mutants/pre-f1.sh`: **1 passed, 4 failed**.

- `test_conventional_dirt_is_clean_and_other_dirt_is_not` — **PASS** (slice 1
  test, unaffected by F-1/F-2; confirms the rebind took effect without
  collaterally breaking unrelated coverage).

- `test_rename_out_of_exempt_path_is_dirty` — **FAILED** on
  `assert result.returncode == 1, result.stdout + result.stderr`. Observed:
  `returncode=0`, stdout `CLEAN: tree clean, just precommit passed`. The
  pre-F-1 pattern `^.. (memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)$`
  matches the `old -> new` tail of the `R  inbox/a.md -> notes.md` line, so
  the rename is wrongly filtered out as exempt.

- `test_quoted_exempt_path_is_clean` — **FAILED** on
  `assert result.returncode == 0, result.stdout + result.stderr`. Observed:
  `returncode=1`, stdout `DIRTY: uncommitted changes\n?? "inbox/my brief.md"`.
  The pre-F-1 pattern has no quote allowance, so the quoted path is wrongly
  treated as dirt.

- `test_git_status_failure_exits_2` — **FAILED** on
  `assert result.returncode == 2, result.stdout + result.stderr`. Observed:
  `returncode=128`, stdout
  `fatal: not a git repository (or any of the parent directories): .git`.
  The pre-F-1 script has no `|| { echo "ERROR: git status failed"; exit 2; }`
  guard on the `git status` assignment, so `set -e` propagates git's own
  128 exit code with no `ERROR:` line.

- `test_missing_just_exits_2` — **FAILED** on
  `assert result.returncode == 2, result.stdout + result.stderr`. Observed:
  `returncode=1`, stdout
  `.../pre-f1.sh: line 36: just: command not found\nPRECOMMIT: validation failed`.
  The pre-F-1 script has no `command -v just` guard (F-2 not yet applied), so
  a missing `just` falls into the `just precommit || { … exit 1; }` branch
  and is misreported as a precommit failure.

None of the four failures is an `ImportError` or `AttributeError` — each
fails on its own named assertion with a concrete, wrong exit code/stdout, and
the slice 1 test staying green confirms the rebind mechanism itself is not
what produced the reds.

### Cleanup

`tmp/mutants/` is gitignored (`tmp/` is gitignored repo-wide) and was left in
place for reproducibility; nothing under it is tracked or staged.
`plugin/skills/build/scripts/verify-step.sh` shows no diff:
`git status --porcelain --untracked-files=all -- plugin/skills/build/scripts/verify-step.sh`
is empty.

## Fixtures tried and rejected

- **Reverting the tracked script in place, then restoring it** — the
  dispatch's own override explicitly forbids this: the behaviour under test
  is already committed, so mutating the tracked file (even temporarily) risks
  leaving it in a bad state if a later step in this dispatch failed, and the
  slice text requires a copy-based mutant instead. Rejected in favor of the
  `tmp/mutants/pre-f1.sh` copy + `SCRIPT` rebind.
- **`git stash` / `git checkout <rev> -- <path>` to materialize the mutant** —
  forbidden by the dispatch rules (`Never git stash, git reset, git
  checkout`), and would touch the one file this slice is scoped OUT of
  editing. Rejected in favor of `git show 31fe4a16:<path> > tmp/mutants/pre-f1.sh`,
  which reads a historical blob without touching the working tree.
  A red produced by leaving `verify-step.sh` genuinely reverted would be
  indistinguishable from one produced by the intended copy-based mutant — the
  point of the override is to avoid that ambiguity by never reverting the
  tracked file at all.
- **A single "run once against pre-f1.sh, once against current.sh" pytest
  invocation without a control run** — considered, but the dispatch requires
  the control run as its own step (proving the rebind harness introduces no
  breakage independent of the mutant's content), so both runs were kept and
  reported separately rather than collapsed into one.
- **Building the missing-`just` `PATH` by filtering the real `PATH` for
  entries lacking a `just` binary** — rejected because a directory elsewhere
  on `PATH` could still resolve `git`/`grep`/`bash` via a different path or
  omit them, making the fixture depend on the ambient `PATH` layout. Built an
  explicit `bin_dir` instead, populated only with symlinks to
  `shutil.which("bash"|"git"|"grep")`, and asserted
  `shutil.which("just", path=str(bin_dir)) is None` as a fixture guard before
  running. `_run_script`'s `extra_env={"PATH": str(bin_dir)}` fully replaces
  `PATH` (rather than the default prepend) so no other `just` on the outer
  `PATH` can be found.
- **Reusing `_stub_just`/`bin_dir` conventions for the missing-`just` test** —
  rejected; that helper exists to make `just` succeed, and this test needs
  the opposite (guarantee `just` cannot be found), so a bespoke `PATH`
  directory of real-tool symlinks was built inline instead of extending
  `_stub_just` with a "don't create just" flag, which would have made the
  helper's contract ambiguous for its one other caller.
