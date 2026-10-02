# Item 1.1 / Slice 2 — RED

Test added: `tests/test_verify_step.py::test_nested_path_under_exempt_dir_is_dirty`.

The SUT (`plugin/skills/build/scripts/verify-step.sh`) already implements the
behaviour this test pins — the exempt pattern's single-level globs already
exclude a nested path — so per the item text the red comes from a mutant copy,
never from editing or reverting the tracked script.

## Fixture

The test builds, in one tree seeded by `_init_repo`, two untracked files one
level deeper than the exempt globs reach:

- `inbox/sub/x.md` — under `inbox/` but past a second `/`.
- `.claude/handoff-dir/x.md` — under `.claude/handoff-` but past a second `/`.

Before running the script, the test asserts
`git status --porcelain --untracked-files=all` (via the new `_status(repo)`
helper, see Scope discipline) equals exactly:

```
?? .claude/handoff-dir/x.md
?? inbox/sub/x.md
```

so the test cannot pass on a fixture that drifted (e.g. `--untracked-files=all`
collapsing the directories, which would read `?? .claude/handoff-dir/` and
`?? inbox/sub/` instead). `_stub_just` is used so a false CLEAN verdict cannot
be masked by `just precommit` actually running.

## Per-test output

### Against the real script (expected PASS — behaviour already present)

```
PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_verify_step.py::test_nested_path_under_exempt_dir_is_dirty -v
```

Result: `1/1 passed`.

Full-file regression check, same script:

```
PATH=/Users/david/code/edify/.venv/bin:$PATH pytest tests/test_verify_step.py -v
```

Result: `8/8 passed` (the seven pre-existing tests, post `_status` refactor,
plus the new one).

## Mutation proof

Per this dispatch's override, mutants live only under
`/tmp/claude/build-fixes/`, never at the tracked path, and `SCRIPT` is rebound
by a throwaway pytest plugin rather than by editing the test module. Three
mutants prove the test reds on its own assertion and prove each glob
load-bearing independently (one mutation per behaviour):

- **Before** (tracked, unchanged):
  `exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'`
- **s2 (both `[^/]+` widened to `.+`)**:
  `exempt='^[^RC][^RC] "?(memory|\.claude/handoff-.+\.md|inbox/.+\.md)"?$'`
- **s2-inbox-only (only the `inbox/` glob widened)**:
  `exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/.+\.md)"?$'`
- **s2-handoff-only (only the `handoff-` glob widened)**:
  `exempt='^[^RC][^RC] "?(memory|\.claude/handoff-.+\.md|inbox/[^/]+\.md)"?$'`

Landing proof:

```
cp /Users/david/code/edify/plugin/skills/build/scripts/verify-step.sh /tmp/claude/build-fixes/verify-step-mutant-s2.sh
cp /Users/david/code/edify/plugin/skills/build/scripts/verify-step.sh /tmp/claude/build-fixes/verify-step-mutant-s2-inbox-only.sh
cp /Users/david/code/edify/plugin/skills/build/scripts/verify-step.sh /tmp/claude/build-fixes/verify-step-mutant-s2-handoff-only.sh
# Edit tool: swap the exempt= line in each, as above
chmod 755 /tmp/claude/build-fixes/verify-step-mutant-s2*.sh

grep -n "exempt=" /tmp/claude/build-fixes/verify-step-mutant-s2.sh
# -> 19:exempt='^[^RC][^RC] "?(memory|\.claude/handoff-.+\.md|inbox/.+\.md)"?$'
grep -n "exempt=" /tmp/claude/build-fixes/verify-step-mutant-s2-inbox-only.sh
# -> 19:exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/.+\.md)"?$'
grep -n "exempt=" /tmp/claude/build-fixes/verify-step-mutant-s2-handoff-only.sh
# -> 19:exempt='^[^RC][^RC] "?(memory|\.claude/handoff-.+\.md|inbox/[^/]+\.md)"?$'
grep -n "exempt=" /Users/david/code/edify/plugin/skills/build/scripts/verify-step.sh
# -> 19:exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'

diff /Users/david/code/edify/plugin/skills/build/scripts/verify-step.sh /tmp/claude/build-fixes/verify-step-mutant-s2.sh
# -> only line 19 differs, confirming the tracked file carries the original
#    and each scratch copy carries its own mutant
```

Rebinding `SCRIPT` without editing the test file: three throwaway pytest
plugins under `/tmp/claude/build-fixes/` — `rebind_script_plugin_s2.py`,
`rebind_script_plugin_s2_inbox.py`, `rebind_script_plugin_s2_handoff.py` —
each copying slice 1's `pytest_collection_modifyitems` shape, overwriting
`sys.modules["tests.test_verify_step"].SCRIPT` with its own mutant path once
collection has imported the module (asserting the module was found and that
`SCRIPT` was not already the mutant).

**s2 (both widened) — FAILS on its own assertion, not an error:**

```
PYTHONPATH=/tmp/claude/build-fixes PATH=/Users/david/code/edify/.venv/bin:$PATH \
  pytest -p rebind_script_plugin_s2 tests/test_verify_step.py::test_nested_path_under_exempt_dir_is_dirty -v
```

Result: `0/1 passed, 1 failed`, on `assert result.returncode == 1`:

```
AssertionError: CLEAN: tree clean, just precommit passed
assert 0 == 1
 +  where 0 = CompletedProcess(args=['/tmp/claude/build-fixes/verify-step-mutant-s2.sh'], returncode=0, ...).returncode
```

Both widened globs now swallow both nested paths, so the tree reads CLEAN —
the test reds on the returncode assertion.

**s2-inbox-only — FAILS on its own assertion, not an error (proves the
`inbox/` glob load-bearing on its own):**

```
PYTHONPATH=/tmp/claude/build-fixes PATH=/Users/david/code/edify/.venv/bin:$PATH \
  pytest -p rebind_script_plugin_s2_inbox tests/test_verify_step.py::test_nested_path_under_exempt_dir_is_dirty -v
```

Result: `0/1 passed, 1 failed`, on the `stdout.splitlines()` assertion:

```
AssertionError: DIRTY: uncommitted changes
  ?? .claude/handoff-dir/x.md

assert ['DIRTY: unco...off-dir/x.md'] == ['DIRTY: unco...box/sub/x.md']
  Right contains one more item: '?? inbox/sub/x.md'
```

The widened `inbox/` glob alone exempts `inbox/sub/x.md`, leaving only the
`.claude/handoff-dir/x.md` line dirty — one line short of the named three, so
the test reds distinctly from the full-mutant run (a failed-assertion red, not
a returncode red).

**s2-handoff-only — FAILS on its own assertion, not an error (proves the
`handoff-` glob load-bearing on its own):**

```
PYTHONPATH=/tmp/claude/build-fixes PATH=/Users/david/code/edify/.venv/bin:$PATH \
  pytest -p rebind_script_plugin_s2_handoff tests/test_verify_step.py::test_nested_path_under_exempt_dir_is_dirty -v
```

Result: `0/1 passed, 1 failed`, on the `stdout.splitlines()` assertion:

```
AssertionError: DIRTY: uncommitted changes
  ?? inbox/sub/x.md

assert ['DIRTY: unco...box/sub/x.md'] == ['DIRTY: unco...box/sub/x.md']
At index 1 diff: '?? inbox/sub/x.md' != '?? .claude/handoff-dir/x.md'
Right contains one more item: '?? inbox/sub/x.md'
```

The widened `handoff-` glob alone exempts `.claude/handoff-dir/x.md`, leaving
only the `inbox/sub/x.md` line dirty.

Real-script run (same command, no mutant, reported above under "Per-test
output") — PASSES, confirming each mutant, not the fixture or the harness, is
what produced its red.

No restore step: the tracked `verify-step.sh` was never touched. Confirmed:

```
git diff --quiet plugin/skills/build/scripts/verify-step.sh && echo "verify-step.sh untouched"
# -> verify-step.sh untouched
```

## Fixtures tried and rejected

- **Untracked directories left collapsed (no `--untracked-files=all` check
  before running the script).** Rejected: the pre-script porcelain assertion
  exists precisely to catch this — without it, a drifted fixture reporting
  `?? inbox/sub/` (a collapsed directory line) would still red under the s2
  mutant's returncode check (collapsed `?? inbox/sub/` still fails to match
  `inbox/.+\.md`, since the pattern requires a trailing `\.md`), making this a
  red this item's own mutation would also have produced rather than the
  mutation it is meant to catch — recording it here because the full-porcelain
  assertion is what rules the drift out, not a difference in the mutation red
  itself.
- **A single nested path instead of one under each exempt directory.**
  Rejected: the slice names both `inbox/sub/x.md` and
  `.claude/handoff-dir/x.md`, and using only one would leave the other glob's
  widening unpinned — exactly what the two single-glob mutants
  (`s2-inbox-only`, `s2-handoff-only`) above exist to rule out. A one-path
  fixture would have gone red under the full mutant but silently passed
  against a mutant that widened only the untested glob, which the dispatch's
  "one mutation per behaviour" requirement is there to surface.
- **Checking `result.returncode == 1` alone, without asserting the full
  `DIRTY:` listing.** Rejected: against `s2-inbox-only` and
  `s2-handoff-only`, the script still exits 1 (one nested path remains dirty
  even after the other is swallowed), so a bare returncode check would stay
  green under either single-glob mutant and only the full `s2` mutant would be
  caught — the asserted `stdout.splitlines()` is what makes each glob
  independently load-bearing.
- **`None`** — no fixture considered and rejected beyond the three above.

## Scope discipline

No implementation code touched; `verify-step.sh` carries no diff (`git diff
--quiet` above). `tests/test_verify_step.py` grew from 373 to 399 lines (under
the 400-line hard cap), which required the seam slice 1's test review named:
extracted `_status(repo)` — wrapping the repeated
`_run_git(repo, "status", "--porcelain", "--untracked-files=all")` — and used
it at all seven call sites in the module, the six pre-existing plus the new
one. The whole module was re-run green after the refactor (`7/7 passed`
before adding the new test, `8/8 passed` after) to confirm the refactor
changed no behaviour. `just format` was run after both the refactor and the
new test; it reformatted call sites onto one line where they now fit and
converted the new test's docstring to a raw string, with no line-count change
either time. No other test in the file was edited or weakened beyond this
mechanical `_status(repo)` substitution; the new test is purely additive.
