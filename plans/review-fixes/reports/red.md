# RED — review-fixes (F-1, F-2, F-3)

Scope: `plans/provenance-enforcement-and-routing/reports/deliverable-review.md`
findings F-1, F-2, F-3 plus their probe detail in the sub-report
`deliverable-review-code-tests.md`. Edited only `tests/`.

## Tests added

- `tests/test_line_limits.py:326` `test_line_limits_fails_python_over_400_under_src`
  — pins that a 401-line `.py` under `src/` reports exactly
  `oversized-file: src/pkg/big.py: 401 lines > 400` and exits 1 (F-3, the
  `src/` half of KD-7's "the Python loop adopts the same line").
- `tests/test_line_limits.py:345` `test_line_limits_fails_python_over_400_under_tests`
  — same contract for a `.py` under `tests/` (F-3, the `tests/` half).
- `tests/test_line_limits.py:358` `test_line_limits_reports_allowlisted_python_without_failing`
  — pins that the Python branch calls into the same allowlist-ceiling
  mechanism the markdown branch uses: reported, exit 0, at the ceiling
  (F-3).
- `tests/test_line_limits_wc_padding.py:24`
  `test_line_limits_reports_unpadded_count_under_bsd_style_wc` — pins the
  exact unpadded `oversized-file:` line against a `wc` shim that
  left-pads its count the way BSD/macOS `wc` does (F-1). **Left red** —
  this is the deliverable; see below.

Helper changes (`tests/line_limits_helpers.py`):

- `_run_check_line_limits` (line 31) now always passes `--allowlist`
  explicitly: when the caller gives none, it writes an empty allowlist
  file under `root.parent` (outside the scanned `ROOT`, so the file
  itself is never walked or counted) and passes that. Explicit-allowlist
  callers are unchanged — same flag, same value. This is the F-2 fix.
  Added a `path_prepend: Path | None` parameter that, when given, prefixes
  `PATH` in the subprocess env — needed by the F-1 test to install the
  `wc` shim.
- `_write_padded_wc_shim` (line 95, new) — writes a `wc` wrapper under a
  given `bin_dir` that execs the real `wc` (located once via
  `shutil.which`, baked in as an absolute path so it can't recurse into
  itself) and reformats only the `wc -l` reading-stdin, no-filename shape
  `check_line_limits.sh:124` uses, left-padding the count into an 8-char
  field. Every other invocation passes straight through.

No test needed an opt-in back to the script's own default-sidecar
fallback — grepped the two modules; nothing exercises that path today.

## F-2 — before/after probe

Probe: append `plugin/skills/x/SKILL.md\t999\tprobe` to the production
`scripts/check_line_limits.allow` (exact match against the fixture path
`test_line_limits_fails_skill_hub_over_200` writes at 201 lines), via Edit,
then invert the same Edit to remove it. Never touched the other 3 lines
already dirty in that file from a concurrent agent (`allowlist-ownership`) —
confirmed identical before and after.

**Before the fix** (`tests/test_line_limits.py::test_line_limits_fails_skill_hub_over_200`
run against the helper as inherited, ceiling 999 in the production
allowlist):

```
tests/test_line_limits.py:60: in test_line_limits_fails_skill_hub_over_200
    assert skill_result.returncode == 1, skill_result.stdout + skill_result.stderr
E   AssertionError: oversized-file: plugin/skills/x/SKILL.md: 201 lines > 200
E
E   assert 0 == 1
E    +  where 0 = CompletedProcess(args=['/Users/david/code/edify/scripts/check_line_limits.sh',
       '/tmp/.../skill_root'], returncode=0,
       stdout='oversized-file: plugin/skills/x/SKILL.md: 201 lines > 200\n',
       stderr='').returncode
```

The test flipped from green to red on its `returncode == 1` assertion —
the production allowlist's ceiling of 999 silently suppressed the fixture's
failure, with no `--allowlist` argument in sight in the test.

Fixed the helper (see above), reapplied the same probe line, reran the
**whole module**:

```
# Test Report

**Summary:** 14/14 passed
✓ Tests OK
```

14/14 green with the probe entry still present in the production
allowlist — the fix is confirmed: none of the eight previously-affected
tests reads it anymore. Removed the probe line (inverted the same Edit).
`git diff --stat -- scripts/` at that point: `scripts/check_line_limits.allow
| 4 ----` — identical to the diff already present from the concurrent
agent before I touched the file, confirming clean restoration.

Also reran `tests/test_line_limits_exit_codes.py` (the other two tests
Finding F-2 names) after the fix, unprobed: `2/2 passed`.

## F-3 — mutation proof

Mutation: in `scripts/check_line_limits.sh:167`, changed
`check_cap "$file" 400` to `check_cap "$file" 999999` inside the `for dir in
src tests` loop only (the Python branch's call site, not the shared
`check_cap` function body, so the markdown branch's behaviour is untouched).

Ran `tests/test_line_limits.py` + `tests/test_line_limits_exit_codes.py`
(19 tests) against the mutant:

```
**Summary:** 16/19 passed, 3 failed

### tests/test_line_limits.py::test_line_limits_fails_python_over_400_under_src FAILED
    assert result.returncode == 1, result.stdout + result.stderr
E   AssertionError:
E   assert 0 == 1
E    +  where 0 = CompletedProcess(..., returncode=0, stdout='', stderr='').returncode

### tests/test_line_limits.py::test_line_limits_fails_python_over_400_under_tests FAILED
    (same shape)

### tests/test_line_limits.py::test_line_limits_reports_allowlisted_python_without_failing FAILED
    assert result.stdout.splitlines() == [...]
E   AssertionError:
E   assert [] == ['oversized-f... lines > 400']
```

Exactly the three new F-3 tests went red; all 16 markdown and exit-code
siblings (which never touch `src/`/`tests/` fixtures) stayed green — the
red is confined to the mutated branch. Restored
`scripts/check_line_limits.sh` by inverting the edit.
`git diff --stat -- scripts/`: `scripts/check_line_limits.allow | 4 ----`
only — `check_line_limits.sh` shows no diff, confirming restoration.

## F-1 — failing assertion (left red)

`tests/test_line_limits_wc_padding.py::test_line_limits_reports_unpadded_count_under_bsd_style_wc`
run against unchanged `scripts/check_line_limits.sh`, with the `wc` shim on
`PATH`:

```
tests/test_line_limits_wc_padding.py:36: in test_line_limits_reports_unpadded_count_under_bsd_style_wc
    assert result.stdout.splitlines() == [
E   AssertionError: oversized-file: docs/notes.md:      401 lines > 400
E
E   assert ['oversized-f... lines > 400'] == ['oversized-f... lines > 400']
E
E     At index 0 diff: 'oversized-file: docs/notes.md:      401 lines > 400' != 'oversized-file: docs/notes.md: 401 lines > 400'
E     Use -v to get more diff
```

`result.returncode == 1` passed (the `-gt` comparison tolerates the
left-padded value, so the gate still decides correctly) — the failure is
purely on the stdout-content assertion, i.e. the malformed line, which is
F-1's whole point. Not a shim, import, or fixture error: the shim produced
the padded count as designed and the script printed it verbatim into
`oversized-file:`. This is the deliverable and is left failing for the
GREEN half.

## Final test run — the three (four, with the new module) line-limit modules

```
$ just test tests/test_line_limits.py tests/test_line_limits_exit_codes.py tests/test_line_limits_wc_padding.py

# Test Report

**Summary:** 19/20 passed, 1 failed

## Failures

### tests/test_line_limits_wc_padding.py::test_line_limits_reports_unpadded_count_under_bsd_style_wc FAILED

    tests/test_line_limits_wc_padding.py:36: in test_line_limits_reports_unpadded_count_under_bsd_style_wc
        assert result.stdout.splitlines() == [
    E   AssertionError: oversized-file: docs/notes.md:      401 lines > 400
    E
    E   assert ['oversized-f... lines > 400'] == ['oversized-f... lines > 400']
    E
    E     At index 0 diff: 'oversized-file: docs/notes.md:      401 lines > 400' != 'oversized-file: docs/notes.md: 401 lines > 400'
    E     Use -v to get more diff
```

19 green, 1 red on assertion (F-1), as expected end state.

## Non-test checks

`just check` (format + style checks, no pytest — the non-test equivalent
of `just lint`, chosen because `just lint` also runs the full suite and
would report the deliberately red F-1 test as a failure):

```
✓ Checks OK
```

## Line caps

`tests/test_line_limits.py`: 377 lines (cap 400) — stayed under, so the
three F-3 tests went into it directly rather than a new module.
`tests/test_line_limits_wc_padding.py` (new, 39 lines) — its docstring
states why it's a separate module: it carries the one deliberately-red
test, isolated for review clarity.
`tests/line_limits_helpers.py`: 123 lines (cap 400).

## Anything unsure

- `scripts/check_line_limits.allow` carries an unrelated, pre-existing
  4-line diff from a concurrent agent (`allowlist-ownership`) throughout
  this session. I never touched anything but my own temporary probe line
  and confirmed the diff was byte-identical before and after each of my
  edits (`git diff --stat -- scripts/`). Not mine to resolve.
- F-1's fix (the actual `tr -d ' '` guard in `scripts/check_line_limits.sh`)
  is production code and out of RED's scope — left for GREEN.
- The `_write_padded_wc_shim` shim only reformats the exact `wc -l`
  no-filename shape the script uses at `:124`; I did not generalize it to
  arbitrary `wc` invocations, since the script has only that one call site
  (verified by reading the whole script).

## Review follow-up

Closed both findings from `plans/review-fixes/reports/test-review.md`
§Findings. Edited only `tests/`.

### Tests added

- `tests/test_line_limits_default_invocation.py` (new module, 106 lines) —
  docstring states why it's separate: these tests need a relocated copy of
  the script (so `SCRIPT_DIR` resolves somewhere the test controls) and a
  plain `cwd=root` invocation with no `ROOT` argument, neither of which any
  other module needs.
  - `:40` `test_line_limits_default_sidecar_applies_its_ceiling` — a
    relocated copy plus a sidecar `check_line_limits.allow` beside it
    (ceiling 401 for a 401-line fixture file), run with no `--allowlist` at
    all: still reported at the cap, exit 0. Pins
    `scripts/check_line_limits.sh:63-65`'s `SCRIPT_DIR`-relative default
    resolution and the ceiling mechanism together, against the real
    invocation form production uses.
  - `:66` `test_line_limits_default_sidecar_missing_is_empty_allowlist` — a
    relocated copy with no sidecar beside it: exit 1 on the same fixture.
    Pins "a missing default allowlist file means an empty allowlist"
    (`scripts/check_line_limits.sh:21-22`, the `-f` guard at `:74`).
  - `:89` `test_line_limits_root_defaults_to_cwd_when_omitted` — runs with
    `omit_root=True` (no `ROOT` positional, `cwd=root`), explicit empty
    `--allowlist` unaffected: exit 1 on an over-cap fixture. Pins
    `ROOT="."` (`scripts/check_line_limits.sh:35`) in isolation from the
    allowlist question.

Helper changes (`tests/line_limits_helpers.py`, now 157 lines):

- `_run_check_line_limits` gained `script: Path | None = None` (invoke a
  relocated copy in place of the canonical `SCRIPT`) and widened
  `allowlist` to `Path | None | Literal["default"]` — `"default"` emits no
  `--allowlist` flag at all, letting the script fall to its own
  `SCRIPT_DIR`-relative sidecar. Also gained a keyword-only
  `omit_root: bool = False` (drops the `ROOT` positional, runs with
  `cwd=root` instead of `root.parent`) — made keyword-only because `ruff`'s
  `FBT001`/`FBT002` flag a positional boolean parameter; `just check`
  caught this and it's fixed.
- Corrected the docstring sentence the review flagged
  (previously `:47-48`, now `:44-56`): it used to say a test wanting the
  default-sidecar fallback "must say so by passing that path explicitly" —
  wrong, since an explicit `Path` sets `ALLOWLIST_EXPLICIT=1` and skips
  that branch entirely. Replaced with the correct mechanism: relocate the
  script via `script=` and pass `allowlist="default"`.

### Major — mutation proofs

**Mutation 1** — `scripts/check_line_limits.sh:64`,
`ALLOWLIST="$SCRIPT_DIR/check_line_limits.allow"` →
`ALLOWLIST="$PWD/check_line_limits.allow"`:

```
**Summary:** 21/23 passed, 2 failed
  test_line_limits_wc_padding.py::...unpadded...        FAILED (pre-existing F-1 red)
  test_line_limits_default_invocation.py::test_line_limits_default_sidecar_applies_its_ceiling FAILED
      assert 1 == 0  (oversized-file line present, but exit 1 — the ceiling
      never applied because $PWD/check_line_limits.allow doesn't exist at
      that cwd, so the sidecar silently resolved empty)
```

Exactly the first coverage test went red, as the review predicted — the
second (no-sidecar) test asserts exit 1 with an empty allowlist regardless,
so this mutation is invisible to it; the ROOT-omission test doesn't touch
the sidecar path at all. Restored by inverting the edit; `git diff --
scripts/check_line_limits.sh` empty.

**Mutation 2** — `scripts/check_line_limits.sh:74`,
`if [ -f "$ALLOWLIST" ]; then` → `if true; then`:

```
**Summary:** 21/23 passed, 2 failed
  test_line_limits_wc_padding.py::...unpadded...        FAILED (pre-existing F-1 red)
  test_line_limits_default_invocation.py::test_line_limits_default_sidecar_missing_is_empty_allowlist FAILED
      assert [] == ['oversized-file: docs/notes.md: 401 lines > 400']
```

The second test went red, as the review flagged as possible — but not by
reaching the empty-allowlist branch and reporting the overage; the review
asked to report what actually happens, so: dropping the `-f` guard makes
the script attempt `done <"$ALLOWLIST"` against a file that does not exist,
which is a bash redirection error under `set -e` — the script aborts
immediately, before any `check_cap` call. Reproduced directly:

```
returncode: 1
stdout: ''
stderr: '.../bin/check_line_limits.sh: line 97: .../bin/check_line_limits.allow: No such file or directory\n'
```

`returncode == 1` is true by coincidence (bash's own redirection-failure
exit status, not `$EXIT_CODE`), so the test's `returncode` assertion alone
would have missed this mutation; it is caught only because the test also
pins the exact stdout line, which comes back empty. The first
(has-sidecar) test is unaffected, since its sidecar file exists and the
mutated `if true` branch reads it exactly as before. Restored by inverting
the edit; `git diff -- scripts/check_line_limits.sh` empty.

**Mutation 3** — `scripts/check_line_limits.sh:35`, `ROOT="."` →
`ROOT="/tmp/certainly-does-not-exist-review-mutation"`:

```
**Summary:** 21/23 passed, 2 failed
  test_line_limits_wc_padding.py::...unpadded...        FAILED (pre-existing F-1 red)
  test_line_limits_default_invocation.py::test_line_limits_root_defaults_to_cwd_when_omitted FAILED
      assert 2 == 1
      check_line_limits.sh: line 100: cd: /tmp/certainly-does-not-exist-review-mutation: No such file or directory
```

Only the ROOT-omission test went red (exit 2, `cd` failure, instead of the
expected exit 1) — the two default-sidecar tests both supply `ROOT`
explicitly via the positional argument, which overwrites the mutated
default, so they're unaffected. Restored by inverting the edit; `git diff
-- scripts/check_line_limits.sh` empty.

All three mutations restored one at a time, each confirmed clean before the
next was applied. Final confirmation after all three:
`git diff -- scripts/check_line_limits.sh` → empty.

### Minor — wc-padding docstring

`_write_padded_wc_shim`'s docstring (`tests/line_limits_helpers.py:97-116`)
now states plainly that BSD's left-padding is the claim F-1 rests on and is
unverified on macOS (this box is Linux), and that the shim pins robustness
against *any* padding `wc` might emit rather than reproducing a measured
BSD output — aligned with the module docstring in
`tests/test_line_limits_wc_padding.py:9-10`, which already said this
correctly.

### `just check` fixup

First `just check` run flagged `FBT001`/`FBT002` on the new positional
`omit_root: bool` parameter. Fixed by making it keyword-only (`*,` before
it in the signature); the one call site already used the keyword form, so
no test call needed to change.

### Final run

```
$ just format
Reformatted files:
  - tests/test_line_limits_default_invocation.py

$ just test tests/test_line_limits.py tests/test_line_limits_exit_codes.py \
      tests/test_line_limits_wc_padding.py tests/test_line_limits_default_invocation.py

# Test Report

**Summary:** 22/23 passed, 1 failed

## Failures

### tests/test_line_limits_wc_padding.py::test_line_limits_reports_unpadded_count_under_bsd_style_wc FAILED

    tests/test_line_limits_wc_padding.py:36: in test_line_limits_reports_unpadded_count_under_bsd_style_wc
        assert result.stdout.splitlines() == [
    E   AssertionError: oversized-file: docs/notes.md:      401 lines > 400
    E
    E   assert ['oversized-f... lines > 400'] == ['oversized-f... lines > 400']
    E
    E     At index 0 diff: 'oversized-file: docs/notes.md:      401 lines > 400' != 'oversized-file: docs/notes.md: 401 lines > 400'
    E     Use -v to get more diff

$ just check
✓ Checks OK
```

22/23 green, 1 red on assertion (the standing F-1 red), matching the
expected end state.

### Tree state

`git status --porcelain -- tests/ scripts/` at close:

```
 M scripts/check_line_limits.allow
 M tests/line_limits_helpers.py
 M tests/test_line_limits.py
?? tests/test_line_limits_default_invocation.py
?? tests/test_line_limits_wc_padding.py
```

`scripts/check_line_limits.allow`'s diff is the same pre-existing 4-line
deletion from the concurrent `allowlist-ownership` work noted earlier in
this report — untouched by this follow-up.
`scripts/check_line_limits.sh` shows no diff.
