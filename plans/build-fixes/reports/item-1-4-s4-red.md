# Item 1.4 / Slice 4 — RED

Slice: `core.quotePath` regression test from the 1.1/2 code review. The fix is
already in `verify-step.sh` (`git -c core.quotePath=true status ...`), so the
red is a mutation red, as in Item 1.1.

**Moved at test review** (`item-1-4-s4-test-review.md`): the new test now
lives in `tests/test_verify_step.py`, the fail-closed module, and pins
`LC_ALL=C.UTF-8` for the script run. The paths and counts below are the RED
run's; to reproduce, run the mutation command against
`tests/test_verify_step.py tests/test_verify_step_exemption.py`, which gives
`8/9 passed, 1 failed`.

## Split (line cap)

`tests/test_verify_step.py` was 380 lines. Split, every test's body unchanged:

| File | Lines | Content |
|---|---|---|
| `tests/verify_step_helpers.py` (new) | 109 | `REPO_ROOT`, `SCRIPT`, `_run_git`, `_status`, `_init_repo`, `_stub_just`, `_run_script`, `_assert_dirty` |
| `tests/test_verify_step_exemption.py` (new) | 273 | the six exemption-pattern tests plus the new test |
| `tests/test_verify_step.py` (changed) | 54 | `test_git_status_failure_exits_2`, `test_missing_just_exits_2` |

Before adding the new test, all 8 pre-existing tests ran green against the
real script across the three files (`8/8 passed`).

## New test

`tests/test_verify_step_exemption.py::test_quotepath_false_does_not_hide_dirt`:
repo-local `core.quotePath false`; untracked `inbox/x\xffy` path built as bytes
(`os.fsencode` / `Path(os.fsdecode(...))` surrogateescape round-trip, written
with `Path.mkdir` / `write_bytes`); asserts exit 1, `DIRTY:` and the listing
exactly `?? "inbox/x\377/y.md"`, and that `just` was not invoked. Skipped when
`sys.platform == "darwin"` with reason "APFS rejects a path that is not valid
UTF-8, so the fixture cannot exist".

## Per-test output

Real script: `pytest tests/test_verify_step.py tests/test_verify_step_exemption.py -v`
-> `9/9 passed`, including the new test.

Mutant (below): `6/7 passed, 1 failed` in the exemption file; the failure is
`test_quotepath_false_does_not_hide_dirt` on its assertion:

```
tests/verify_step_helpers.py:107: in _assert_dirty
    assert result.returncode == 1, result.stdout + result.stderr
E   AssertionError: grep: (standard input): binary file matches
E   CLEAN: tree clean, just precommit passed
```

## Mutation proof

```
D=/tmp/claude/build-fixes/mutant-s4
mkdir -p $D && cp plugin/skills/build/scripts/verify-step.sh plugin/skills/build/scripts/exempt-paths.sh $D/
# python: asserted count==1, replaced
#   "git -c core.quotePath=true status --porcelain"  ->  "git status --porcelain"
diff plugin/skills/build/scripts/verify-step.sh $D/verify-step.sh
# 40c40: only the git status line differs (-c core.quotePath=true dropped)
grep -n "quotePath=true status" $D/verify-step.sh   # exit 1: no hit in mutant
PYTHONPATH=$D PATH=/Users/david/code/edify/.venv/bin:$PATH \
  pytest -p rebind_s4 tests/test_verify_step_exemption.py -v
```

`$D/rebind_s4.py` is a throwaway plugin: in `pytest_collection_modifyitems` it
takes `sys.modules["tests.verify_step_helpers"]` (where `_run_script` reads
`SCRIPT`), asserts the module exists and `SCRIPT != MUTANT` (not a no-op), then
rebinds `SCRIPT` to `$D/verify-step.sh`. The mutant's `exempt-paths.sh` copy
sits beside it, so its relative `source` resolves. Result: the named test reds
on `returncode == 1` with grep's "binary file matches" and a `CLEAN:` verdict
(the dirt hidden); the other six pass. Same test on the real script:
`1/1 passed`. The tracked script was never edited, so nothing to restore:
`git diff --quiet plugin/skills/build/scripts/` exits 0.

## Fixtures tried and rejected

- Using `_status(repo)` to pre-assert the porcelain: rejected. With
  `quotePath false` it emits the raw 0xFF byte, and `text=True` decoding fails
  on it; the test asserts the script's own listing instead.
- A `str` path with a literal escape: rejected, since the invalid byte must
  reach the filesystem; `os.makedirs`/`open` on bytes passed the filesystem but
  trips ruff PTH103/PTH123, so the surrogateescape `Path` form is used.
- Global `core.quotePath false` via `GIT_CONFIG_GLOBAL`: rejected; the tests
  null the global config, so only repo-local config reaches the script.

## Lint

`ruff check`, `ruff format --check` and `docformatter -c` pass on all three
touched test files.
