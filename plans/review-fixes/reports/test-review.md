# RED review — review-fixes (F-1, F-2, F-3)

**Verdict: proceed to GREEN.**

Findings: 1 major, 1 minor, 1 nit. None blocks GREEN — GREEN's scope is the
`tr -d ' '` guard at `scripts/check_line_limits.sh:124`, and the major finding
names a coverage gap in allowlist *resolution*, which that guard does not
touch. The major should be closed inside this job, not deferred.

Reviewed against `craft:test-discipline`, `docs/references/testing.md` and
`scripts/check_line_limits.sh`. Every claim in
`plans/review-fixes/reports/red.md` that I could check, I re-ran; all of them
held.

---

## Findings

### Major — F-2's fix leaves the only invocation form production uses with zero coverage

Production runs the script with **no arguments at all**:

- `justfile:219` — `report "line limits" ./scripts/check_line_limits.sh`
- `plugin/portable.just:86` — identical

So in production `ROOT` defaults to `.` and `ALLOWLIST_EXPLICIT` stays `0`,
taking the default-sidecar branch at `scripts/check_line_limits.sh:63-65`.

After this change all 20 tests pass `--allowlist` explicitly
(`tests/line_limits_helpers.py:58`), so that branch has no cover at all.
Before the change eight tests reached it — wrongly, via the real file, which
is exactly what F-2 was raised about. The fix removed the dependency on the
production file's *contents* and removed the coverage with it. What is now
unpinned:

- `scripts/check_line_limits.sh:13-14` — the default is "resolved from this
  script's own location (never ROOT or CWD)".
- `scripts/check_line_limits.sh:21-22` — "A missing default allowlist file
  means an empty allowlist" (the `-f` guard at `:74`).
- `ROOT` defaulting to `.` when no positional argument is given (`:35`).

A refactor resolving the default from `$ROOT` or `$PWD`, or dropping the `-f`
guard, passes the entire suite today. This is `coverage-shape.md`'s
"invoked as production invokes it" contract: the test harness now uses a form
production never uses, and the form production always uses is untested.

Compounding it, the helper's own docstring prescribes an opt-in that cannot
work — `tests/line_limits_helpers.py:47-48`:

> A test that means to exercise the script's own default-sidecar fallback must
> say so by passing that path explicitly.

Passing the path explicitly sets `ALLOWLIST_EXPLICIT=1` and skips the branch
entirely, while reintroducing the dependency on the production file's contents
that F-2 exists to remove. The sentence reads as though the gap is covered by
an available opt-in; it is not.

**Fix.** Add a test that copies `scripts/check_line_limits.sh` into
`tmp_path/bin/`, writes `tmp_path/bin/check_line_limits.allow` holding a
fixture entry, and runs the copy with **no** `--allowlist` against a fixture
`ROOT` — asserting the sidecar's ceiling applies (exit 0, still reported at the
cap). `SCRIPT_DIR` is derived from `BASH_SOURCE` (`:34`), so the copy resolves
its own sidecar; relocating the script is legitimate here because `SCRIPT_DIR`
resolution *is* the subject under test, not a mutation workaround. A second
case with no sidecar beside the copy asserts exit 1 on the same fixture
(missing default = empty allowlist). Give `_run_check_line_limits` a
`script: Path | None = None` parameter and an explicit
`allowlist: Path | None | Literal["default"]` opt-in rather than another
boolean flag, and correct the `:47-48` docstring sentence to say that the
fallback can only be exercised against a relocated copy.

### Minor — the helper docstring states unverified BSD behaviour as established fact

`tests/line_limits_helpers.py:100-101`:

> BSD/macOS ``wc`` left-pads that same call into a fixed-width field.

and the shim commits to an 8-character field (`:117`). The source finding
records the opposite status —
`plans/provenance-enforcement-and-routing/reports/deliverable-review.md:72-73`:

> **Verification status:** the padding claim is **not executed on macOS** —
> this box is Linux (bash 5.2.37), where `wc -l < f` printed unpadded.

Under CLAUDE.md's No Confabulation rule the docstring should carry that status.
This does not weaken the test: its assertion discriminates on the *presence* of
padding, not its width (proved below — a 5-space residue fails the same way a
6-space one does), so the exact field width is immaterial. Saying so is worth a
line, because a reader who takes "8" as measured fact may go looking to verify
it.

**Fix.** One sentence in `_write_padded_wc_shim`'s docstring: name the padding
as the unverified-on-macOS claim F-1 rests on, and say the shim pins robustness
against *any* padding `wc` rather than reproducing a measured BSD output. The
module docstring at `tests/test_line_limits_wc_padding.py:9-10` already gets
this right ("pins the exact unpadded line KD-7 requires regardless of which
`wc` ran") — align the helper to it.

### Nit — line count off by one in the RED report

`plans/review-fixes/reports/red.md:194` says the new module is 39 lines;
`wc -l tests/test_line_limits_wc_padding.py` reports 38. No consequence.

---

## What I verified

### 1. F-1 — red for the right reason, and it discriminates

**Red on the stdout assertion, not a shim/fixture/import error.**

```
$ just test tests/test_line_limits.py tests/test_line_limits_exit_codes.py \
      tests/test_line_limits_wc_padding.py
**Summary:** 19/20 passed, 1 failed

### tests/test_line_limits_wc_padding.py::test_line_limits_reports_unpadded_count_under_bsd_style_wc FAILED
    tests/test_line_limits_wc_padding.py:36: in ...
        assert result.stdout.splitlines() == [
    E   AssertionError: oversized-file: docs/notes.md:      401 lines > 400
    E     At index 0 diff: 'oversized-file: docs/notes.md:      401 lines > 400'
                        != 'oversized-file: docs/notes.md: 401 lines > 400'
EXIT=1
```

The failure message carries the padded count, which is positive evidence the
shim ran, the script resolved it, and the padded value reached
`echo` at `:129` verbatim. Line 35's `assert result.returncode == 1` passed.

**The shim models the call site faithfully.** The script has exactly one `wc`
invocation:

```
$ grep -n "wc " scripts/check_line_limits.sh
124:    if ! line_count=$(wc -l <"$file"); then
```

That is `$# == 1`, `$1 == "-l"`, stdin redirected, no filename — precisely the
shim's guard (`tests/line_limits_helpers.py:115`). Everything else `exec`s
through to the real `wc` at an absolute path baked in via `shutil.which`, so it
cannot recurse. The report's claim that `:124` is the only call site is
confirmed.

**The obvious fix turns it green.** Applied `| tr -d ' '` at `:124`:

```
$ just test tests/test_line_limits.py tests/test_line_limits_exit_codes.py \
      tests/test_line_limits_wc_padding.py
**Summary:** 20/20 passed
EXIT=0
```

Note for GREEN: that pipeline form preserves the exit-2 unreadable-file
contract **only because `:32` sets `pipefail`** — `test_unreadable_file_outranks_a_later_overage`
stayed green above. A GREEN that writes the fix as a pipeline must not also
touch `set -euo pipefail`.

**A partially-correct fix is caught.** Replaced the strip with a
single-leading-space trim, `line_count="${line_count# }"`, before the `-gt`
comparison:

```
$ just test tests/test_line_limits_wc_padding.py
**Summary:** 0/1 passed, 1 failed
E   AssertionError: oversized-file: docs/notes.md:     401 lines > 400
```

Five spaces instead of six — still red. The assertion pins the complete line,
so any residue fails it. Mutation inverted; `git diff -- scripts/check_line_limits.sh`
empty and `grep` for the mutation text returns nothing.

**Whitespace safety and PATH containment.** Every expansion in the generated
shim is quoted (`"$#"`, `"$1"`, `"$count"`, `"$@"`, and `real_wc` interpolated
inside double quotes). The PATH prepend uses `os.pathsep`
(`tests/line_limits_helpers.py:62`). No leak into other tests:
`env = os.environ.copy()` copies rather than mutates the parent environment,
`env` stays `None` unless `path_prepend` is given (so the other 19 tests are
unaffected), and `bin_dir` is a per-test `tmp_path / "bin"`.

The shim's unconditional `exit 0` looked like a latent hazard — it would
swallow a real `wc` failure — but it cannot reach the script's exit-2 path,
because an unreadable file fails at the *redirect* in `check_cap`'s own
subshell before `wc` runs. Reproduced by hand with the shim on `PATH` against a
chmod-000 fixture: `check_line_limits: cannot read docs/locked.md`, `EXIT=2`.
Not a finding.

### 2. F-2 — no test reaches the production allowlist

**Every caller goes through the helper.** `grep -rn "check_line_limits"` over
`tests/` finds 22 call sites, all `_run_check_line_limits`, across
`test_line_limits.py`, `test_line_limits_exit_codes.py` and
`test_line_limits_wc_padding.py`. `grep -rn "subprocess" tests/` finds no
direct invocation of the script bypassing the helper. The helper now always
emits `--allowlist` (`:58`), defaulting to an empty file at
`root.parent / "_empty_allowlist_for_test.txt"` — outside the scanned `ROOT`
in every test, since every test builds `root = tmp_path / "<name>"` and the
script `cd`s into `root`.

**Probe re-run, independently.** Added two entries to the production
`scripts/check_line_limits.allow`, matching fixture paths used by the suite:

```
plugin/skills/x/SKILL.md	999	REVIEW PROBE
src/pkg/big.py	999	REVIEW PROBE
```

First, proved the probe is live — a hand-built fixture tree with a 201-line
`plugin/skills/x/SKILL.md` and a 401-line `src/pkg/big.py`:

```
--- run WITHOUT --allowlist (default sidecar, probe live) ---
oversized-file: src/pkg/big.py: 401 lines > 400
oversized-file: plugin/skills/x/SKILL.md: 201 lines > 200
EXIT=0
--- run WITH empty --allowlist (what the helper now does) ---
oversized-file: src/pkg/big.py: 401 lines > 400
oversized-file: plugin/skills/x/SKILL.md: 201 lines > 200
EXIT=1
```

Exit 0 vs 1 is the discrimination: the probe entries do suppress the failure
when the default sidecar is read. Then, with the probes still in place:

```
$ just test tests/test_line_limits.py tests/test_line_limits_exit_codes.py \
      tests/test_line_limits_wc_padding.py
**Summary:** 19/20 passed, 1 failed
  (only test_line_limits_reports_unpadded_count_under_bsd_style_wc)
```

Byte-identical to the unprobed run. No test reads the production allowlist.
F-2 confirmed fixed.

Probe removed by inverting the same edit; `grep "REVIEW PROBE"` returns
nothing and `git diff -- scripts/check_line_limits.allow` shows only the four
pre-existing deleted entries belonging to the concurrent `allowlist-ownership`
work (`docs/superpowers/design/plugin-transition-evaluation.md`,
`plugin/skills/build/SKILL.md`, `plugin/skills/design/SKILL.md`,
`plugin/skills/requirements/SKILL.md`).

**Default-sidecar fallback coverage:** gone — see the major finding above.

### 3. F-3 — exact line and exit code pinned, mutation confined

All three tests pin the complete stdout line (`splitlines() == [...]`, not a
substring) and the exit code:

- `tests/test_line_limits.py:339-342` — `src/pkg/big.py`, exit 1
- `tests/test_line_limits.py:352-355` — `tests/big.py`, exit 1
- `tests/test_line_limits.py:374-377` — allowlisted `src/pkg/big.py` at
  ceiling 401, exit 0, still reported at the cap

**Mutation A**, repeating the implementer's — `check_cap "$file" 400` →
`check_cap "$file" 999999` in the `for dir in src tests` loop only (string
verified unique, `grep -c` → 1):

```
**Summary:** 16/20 passed, 4 failed
  test_line_limits_fails_python_over_400_under_src        FAILED (assert 0 == 1)
  test_line_limits_fails_python_over_400_under_tests      FAILED (assert 0 == 1)
  test_line_limits_reports_allowlisted_python_without_failing FAILED
      (assert [] == ['oversized-file: src/pkg/big.py: 401 lines > 400'])
  test_line_limits_reports_unpadded_count_under_bsd_style_wc FAILED (pre-existing F-1 red)
```

Exactly the three new tests, plus the expected standing F-1 red. All 16
markdown and exit-code siblings green — the red is confined to the mutated
branch, and each mutation-caused red is the test named for it.

**Mutation B**, mine, sharper — `for dir in src tests` → `for dir in src`:

```
**Summary:** 18/19 passed, 1 failed
  test_line_limits_fails_python_over_400_under_tests FAILED (assert 0 == 1)
```

One red, caught by its own test. The `src/` and `tests/` halves are
independently pinned; neither carries the other.

Both mutations inverted. `git diff -- scripts/check_line_limits.sh` is empty
and a residue grep for `WRONGFIXPROBE`, `tr -d ' '` and `line_count# ` returns
nothing.

### 4. General

**Invoked as production invokes it — partly.** `git ls-files -s scripts/check_line_limits.sh`
→ `100755`, and the tests run `subprocess.run([str(SCRIPT), ...])` with no
shell, so the executable bit and the shebang are load-bearing in the test path
exactly as they are in production's `./scripts/check_line_limits.sh`. Exit code
and both streams are asserted, never internals. The one divergence is the
argument vector, which is the major finding.

**Caps and formatting.**

```
$ wc -l tests/test_line_limits.py tests/test_line_limits_wc_padding.py \
       tests/line_limits_helpers.py tests/test_line_limits_exit_codes.py
  377 tests/test_line_limits.py
   38 tests/test_line_limits_wc_padding.py
  123 tests/line_limits_helpers.py
   77 tests/test_line_limits_exit_codes.py

$ just check
✓ Checks OK
```

`just check` runs `ruff format --check`, `ruff check`, `docformatter -c` and
the line-limit gate, so `just format` is a no-op on these files and every
module is under the 400-line cap. I did not run `just format` (it mutates) or
`just lint`/`just precommit` (they run the suite, which is red by design in
RED).

**Vacuity sweep.** No test in the change passes vacuously.

- The three F-3 tests each went red under a mutation of the behaviour they
  name, and only under it.
- The F-1 test's discriminating assertion is `:36` (the exact line); `:35`
  `returncode == 1` is already true pre-fix and stays true post-fix, so it can
  never be the red. That is correct as a guard — it would catch a fix that
  broke the `-gt` comparison by emptying `line_count` — but the GREEN reviewer
  should not mistake it for the contract under test.
- All three F-3 fixtures use 401 lines, which is the "parallel values all
  equal" smell, but the fixtures live in separate `tmp_path` trees with
  distinct paths, so there is nothing for a swapped predicate to exchange. Not
  a defect.

---

## Commands run

All from `/Users/david/code/edify`.

1. `git diff -- tests/`, `git status --porcelain -- tests/ scripts/`
2. `grep -rn "check_line_limits" --include=*.py tests/`;
   `grep -rn "subprocess" --include=*.py tests/`
3. `just test tests/test_line_limits.py tests/test_line_limits_exit_codes.py tests/test_line_limits_wc_padding.py`
   — baseline, 19/20
4. Edit `:124` → `| tr -d ' '`; same `just test` → 20/20; inverted
5. Edit — `line_count="${line_count# }"` before the `-gt`;
   `just test tests/test_line_limits_wc_padding.py` → 0/1; inverted
6. `git diff -- scripts/check_line_limits.sh` → empty
7. Edit `scripts/check_line_limits.allow` — two `REVIEW PROBE` entries; hand
   fixture run with and without `--allowlist` (exit 0 / exit 1); full
   `just test` → 19/20 identical to baseline; inverted; residue grep clean
8. `grep -c 'check_cap "$file" 400'` → 1; `grep -c 'for dir in src tests'` → 1
9. Mutation A (`999999`) → 16/20; inverted. Mutation B (`for dir in src`) →
   18/19; inverted
10. `git ls-files -s scripts/check_line_limits.sh` → `100755`;
    `grep -n "wc " scripts/check_line_limits.sh` → one hit at `:124`
11. Shim-plus-unreadable-file probe → `EXIT=2`
12. `wc -l` on the four modules; `just check` → `✓ Checks OK`
13. `git diff -- scripts/check_line_limits.sh` empty;
    `git diff -- scripts/check_line_limits.allow` → only the four pre-existing
    deletions

## Tree state

I edited only this report. `scripts/check_line_limits.sh` is byte-identical to
`HEAD` (empty diff). `scripts/check_line_limits.allow` carries only the four
deleted entries that predate this review, from the concurrent
`allowlist-ownership` work — not mine to resolve. `git status --porcelain --
tests/ scripts/` at close:

```
 M scripts/check_line_limits.allow
 M tests/line_limits_helpers.py
 M tests/test_line_limits.py
?? tests/test_line_limits_wc_padding.py
```

One background probe of mine hung on a `/dev/full` read (my error — it reads
infinite zeros) and was killed; it touched nothing in the repo, only
`$TMPDIR`.
