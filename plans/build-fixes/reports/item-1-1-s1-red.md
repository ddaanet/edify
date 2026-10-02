# Item 1.1 / Slice 1 — RED

Test added: `tests/test_verify_step.py::test_exempt_paths_clean_in_any_porcelain_state`.

The SUT (`plugin/skills/build/scripts/verify-step.sh`) already implements the
behaviour this test pins, so per the item text the red comes from a mutant
copy, never from editing or reverting the tracked script.

## Fixture

The test builds, in one tree seeded by `_init_repo`, exactly the four
non-rename exempt XY states named in the slice and nothing else:

- `A  .claude/handoff-new.md` — new file, staged.
- ` D .claude/handoff-task.md` — the seeded committed file, deleted in the
  worktree only (not staged).
- `UU inbox/conflict.md` — a tracked file given a real two-branch merge
  conflict (`main` and a `feature` branch each change the same line
  differently; `git merge feature` is run directly via `subprocess.run`,
  not through `_run_git`, because a real conflict exits non-zero and that
  is the point of the call).
- `D  inbox/old.md` — a tracked file removed with `git rm`, staged and gone
  from the worktree.

Before running the script, the test asserts
`git status --porcelain --untracked-files=all` equals exactly:

```
A  .claude/handoff-new.md
 D .claude/handoff-task.md
UU inbox/conflict.md
D  inbox/old.md
```

so the test cannot pass on a fixture that drifted to a simpler state (e.g. a
merge that silently fast-forwarded instead of conflicting). `_stub_just` is
used so `just precommit` is stubbed.

## Per-test output

### Against the real script (expected PASS — behaviour already present)

```
PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_verify_step.py::test_exempt_paths_clean_in_any_porcelain_state -v
```

Result: `1/1 passed`.

Full-file regression check, same script:

```
PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_verify_step.py -v
```

Result: `7/7 passed` (the six pre-existing tests plus the new one).

## Mutation proof

The mutant lives only at `/tmp/claude/build-fixes/verify-step-mutant-s1.sh`
(a copy of the script, `mkdir -p /tmp/claude/build-fixes` first), never at the
tracked path. The one-line edit, confirmed present by grep before running and
distinct from every other line in the file:

- Before: `exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'`
- After: `exempt='^[ M?][ M?] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'`

Landing proof:

```
cp /Users/david/code/edify/plugin/skills/build/scripts/verify-step.sh /tmp/claude/build-fixes/verify-step-mutant-s1.sh
# Edit tool: swap the exempt= line as above
grep -n "exempt=" /tmp/claude/build-fixes/verify-step-mutant-s1.sh
# -> 19:exempt='^[ M?][ M?] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'
diff /Users/david/code/edify/plugin/skills/build/scripts/verify-step.sh /tmp/claude/build-fixes/verify-step-mutant-s1.sh
# -> only line 19 differs, confirming the tracked file carries the original
#    and the scratch copy carries the mutant
```

Rebinding `SCRIPT` without editing the test file: a throwaway pytest plugin,
`/tmp/claude/build-fixes/rebind_script_plugin.py`, implementing
`pytest_collection_modifyitems` to overwrite
`sys.modules["tests.test_verify_step"].SCRIPT` with the mutant path once
collection has imported the module (asserting the module was found and that
`SCRIPT` was not already the mutant, so a silent no-op would itself fail the
run).

Mutant run — FAILS on its own assertion, not an error:

```
PYTHONPATH=/tmp/claude/build-fixes PATH=/Users/david/code/edify/.venv/bin:$PATH \
  pytest -p rebind_script_plugin tests/test_verify_step.py::test_exempt_paths_clean_in_any_porcelain_state -v
```

Result: `0/1 passed, 1 failed`, on `assert result.returncode == 0`:

```
AssertionError: DIRTY: uncommitted changes
  A  .claude/handoff-new.md
   D .claude/handoff-task.md
  UU inbox/conflict.md
  D  inbox/old.md

assert 1 == 0
 +  where 1 = CompletedProcess(args=['/tmp/claude/build-fixes/verify-step-mutant-s1.sh'], returncode=1, ...).returncode
```

This shows the mutant distinctly ran (its distinct verdict: all four exempt
lines reported as dirt, because none of `A `, ` D`, `UU`, `D ` is drawn from
the narrowed `[ M?][ M?]` set) and the test reds on the `returncode == 0`
assertion, not on a missing symbol or setup exception.

Real-script run (same command, no mutant, reported above under "Per-test
output") — PASSES, confirming the mutant is what produced the red, not the
fixture or the harness.

No restore step: the tracked `verify-step.sh` was never touched. Confirmed:

```
git diff --quiet plugin/skills/build/scripts/verify-step.sh && echo "verify-step.sh untouched"
# -> verify-step.sh untouched
```

## Fixtures tried and rejected

- **Two independent single-file merges (one per exempt file) instead of one
  shared tree.** Rejected: the slice names one repo holding all four states
  "and nothing else" — splitting across repos would not exercise the exempt
  pattern against a porcelain listing that also contains the other three
  lines, which is exactly the shape `grep -vE` filters line-by-line. A red
  from the item's intended mutation (narrowing both XY columns) would have
  shown up identically in a single-file fixture, so the combined fixture is
  what makes this test non-redundant with four smaller ones, not a case
  this item's own mutation would have produced regardless.
- **Faking a conflict by hand-writing `<<<<<<<` markers into a non-conflicted
  index.** Rejected: that stages a file as merely modified (`M` or `MM`), not
  `UU` — git's unmerged status comes from the index holding stage 1/2/3
  entries, which only a real unresolved merge (or `update-index
  --unresolve`) produces. A hand-written-markers fixture would silently drift
  the test onto a state the slice does not name, which the pre-script
  porcelain assertion is there to catch — recording it here because a red
  from the item's intended mutation would equally have passed against such a
  drifted fixture, making the drift the case worth guarding, not the
  mutation itself.
- **Using `_run_git` for the conflicting `git merge`.** Rejected: `_run_git`
  asserts `returncode == 0`, and a genuine conflict exits 1 by design — using
  it would have turned the expected conflict into a hard setup failure. Used
  a direct `subprocess.run` call with the same env-insulation pattern
  instead, discarding its result deliberately (the state is verified
  afterward by the full porcelain-string assertion, not by the merge
  command's own exit code).
- **`None`** — no fixture considered and rejected beyond the three above.

## Scope discipline

No implementation code touched. `verify-step.sh` carries no diff
(`git diff --quiet` above). No other test in the file was edited or weakened;
the new test is purely additive. `tests/test_verify_step.py` is now 377
lines, under the 400-line hard cap.
