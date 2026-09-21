# Format recipe fix + verify-step.sh sign-off — report

## Task 1 — `format` recipe

### Per-pipeline diagnosis (1a)

Both `ruff`-sourced pipelines in `plugin/portable.just`'s `format` recipe were
broken, but by **two separate defects**, and both defects are exercised
identically by the lint-autofix pipeline and the format pipeline — the
"possible contradiction" in the brief does not hold; both pipelines are
broken the same way.

**Defect 1 — missing `-p0`.** Both `ruff format --diff` and
`ruff check --fix-only --diff` emit unified-diff headers with no `a/`/`b/`
prefix (`--- src/edify/check.py` / `+++ src/edify/check.py`). Verified with a
throwaway file (`tests/_zz_format_probe.py`, unsorted imports, removed after
the probe): `ruff check -q --fix-only --diff` on it produced the identical
bare-path header style as `ruff format --diff`. Bare `patch` (no `-p`) cannot
auto-detect the strip level for either header and, receiving the diff via a
pipe (not a tty), silently answers "Skip this patch?" → the file is
untouched, exit 1. `patch -p0` applies both cleanly. Confirmed against the 13
files `ruff format --check` currently flags across `src`/`tests` and against
the probe file for the lint-autofix side.

**Defect 2 — `patch-and-print`'s filename-extraction regex never matches.**
Independent of defect 1, and the reason `just format` still printed no
"Reformatted files:" banner even after adding `-p0`. The helper assumed GNU
patch prints `patching file 'PATH'` (quoted). This GNU patch (2.8) prints
`patching file PATH` unquoted — verified directly, in both forward and
reverse (`-R`) mode — so the `sed -Ene "/^patching file '/..."` pattern never
matched and the accumulated file list was always empty, regardless of the
strip-level bug. This also silently affected the `docformatter | patch-and-print
-Rp1` call, but that call was never exercised (see next paragraph), so this
defect was previously undetectable in practice for any of the three
pipelines.

**On "an earlier agent reported `just format` DID fix I001 on new test
files"**: grepped the whole tree for any other `ruff --fix` invocation —
`plugin/portable.just:133` is the only one. Reproduced the exact pipeline
(`ruff check -q --fix-only --diff | patch` with no `-p`) against a fresh
unsorted-import probe file: it left the file untouched, exit 1. There is no
code path by which the unfixed recipe could have applied an I001 fix; the
earlier report does not hold against current behavior. (Not chasing further —
no other mechanism exists in-repo that could explain it.)

**`docformatter` line — not touched, verified why.** `docformatter --help`:
`-d, --diff ... when used with --check or --in-place, also what changes would
be made`. The recipe's line (`docformatter --diff src tests`, no `-c`/`-i`)
is a documented no-op: confirmed live, `docformatter --diff src tests` exits
0 with empty output even though `docformatter -c --diff src tests` (which
does take effect) also currently finds nothing to flag — there are no
pending docformatter diffs in the tree right now either way. Because the
current invocation never produces a diff, there is no "diffs exist" case to
verify the ruff fix's reasoning against — `apply-ruff-diff`'s tolerate-1/fail-
on-else split is not applied here. This is a separate, pre-existing defect
(missing `-c`/`-i`) independent of items in scope; left as found and flagged
below, not fixed.

### Changes made (1b, 1c, 1d, 1f)

**`plugin/portable.just`** — `format` recipe:
- `patch-and-print`'s `sed` pattern: quoted-filename assumption →
  `s/^patching file //p` (strips the unquoted prefix this patch actually
  emits).
- Replaced the two bare `ruff ... --diff | patch-and-print >> "$tmpfile" ||
  true` lines with a new `apply-ruff-diff()` helper, called as
  `apply-ruff-diff "ruff check --fix-only --diff" ruff check -q --fix-only
  --diff` and `apply-ruff-diff "ruff format --diff" ruff format -q --diff`.
  The helper: runs `"$@" | patch-and-print -p0 >> "$tmpfile"` under `set +e`
  (to survive `pipefail` without aborting under `set -e`), captures both
  ends via `local status=("${PIPESTATUS[@]}")` in one combined
  declare+assign statement (a two-statement `local x; x=(...)` was tried
  first and silently lost `PIPESTATUS[1]` — the `local` builtin itself
  resets `PIPESTATUS` when it runs as a separate command; the combined form
  does not), then `fail`s loudly if ruff's own exit is `>1` (a real tool
  error — verified live as exit `2` for a bad path and a bad `--config`
  value; `--help` for both subcommands documents `--diff` as "exit with a
  non-zero status" on diffs found, with no explicit exit-code table, so the
  `2`-for-error behavior was confirmed by provoking it rather than assumed)
  or if `patch`'s own exit is non-zero.
- `docformatter` line left untouched (see diagnosis above).

**`plugin/portable.just` and `justfile`** — `run-checks()` (1f): added
`report "ruff format --check" ruff format --check -q` beside `report "ruff
check" ruff check -q`, in the existing `report "label" cmd` style. **Both**
files needed the edit, not just one: `run-checks` (used by `precommit`, not
`run-lint-checks`, used by `check`/`lint`/`green`/`red-lint`) is duplicated —
root's `justfile:135-146` carries its own full copy of `run-checks` and the
rest of the shared shell functions, not just `bash_prolog` as items 4/5 in
`small-defects.md` anticipated. Per the existing documented override
semantics (`small-defects.md` item 4): `just` variable overrides apply
globally once the importer redefines a variable the imported module also
defines, so **root's** `bash_prolog` — and therefore root's `run-checks` —
is what actually runs for `just precommit` in this repo, not
`portable.just`'s copy. Editing only `portable.just` would have left
`precommit` unfixed; edited both so the fix is live here and vendoring
consumers of `portable.just` standalone also get it.

`run-lint-checks` (used by `check`/`lint`/`green`/`red-lint`, all of which
depend on `format` first except `check`) was **not** touched — out of the
task's asked scope (which named the recipe `precommit` uses), and `lint`/
`green`/`red-lint`/`dev` already run `format` before their checks so the gap
matters less there; `check` on its own has no format verification at all.
Flagging as an observation, not fixing: a call for whoever owns the `check`
recipe's scope.

No `bash 3.2` concern: confirmed the file already uses `[[ ! -v `, so bash
4+ was already assumed; the new code uses arrays and `PIPESTATUS`, also
bash 4+ only.

### Proof runs (1e, 1f)

**1e** — `just format`, full repo: applied all 13 pending `ruff format`
diffs (`src/edify/check.py`, `src/edify/discovery.py`,
`src/edify/markdown_inline_fixes.py`, plus 10 already-dirty test files —
`git status` shows those 13 were `M` before this batch too, from earlier
agents' work; `just format` only reformatted their *content*, it did not
change what was already staged/unstaged) and printed the "Reformatted
files:" list correctly for the first time. Confirmed the PEP 758 exception
line the brief called out
(`src/edify/discovery.py`: `except json.JSONDecodeError, OSError:`,
parenthesis-free) is present post-format and left alone — valid Python
3.14, and `pyproject.toml`'s `requires-python = ">=3.14"` makes ruff
target it correctly.

`ruff format --check src tests` afterward: `69 files already formatted`,
exit 0.

**1f** — added `ruff format --check` to `run-checks`, then:
1. Edited `src/edify/__init__.py`: `version("edify-cli")` →
   `version(  "edify-cli")` (extra internal whitespace — format-dirty,
   lint-clean; confirmed `ruff check -q src/edify/__init__.py` exit 0
   on it).
2. `just precommit` → failed, with `# ruff format --check` /
   `Would reformat: src/edify/__init__.py` as the only new failing check;
   everything else in the run stayed green up to that point. Exit 1.
3. Reverted with the exact inverse edit (`version(  "edify-cli")` →
   `version("edify-cli")`); `git diff -- src/edify/__init__.py` empty,
   confirming an exact revert.
4. `just precommit` → green again (`✓ Precommit OK`).

A stray `.orig` file (`src/edify/__init__.py.orig`) was left behind by an
earlier manual `patch -R` probe during diagnosis, not by the recipe itself —
removed before the proof run above; confirmed via `git status` it left no
trace.

### Test coverage (1g)

Grepped `plugin/`, `tests/`, `docs/`, `scripts/` for `justfile`,
`portable.just`, and `just `-prefixed invocations inside `tests/`. The only
hits are prose mentions of `just precommit` / `just test` in test docstrings
(`tests/test_bootstrap_hook.py:5`, `tests/test_line_limits.py:34`) — no test
spawns `just` as a subprocess or exercises a recipe. No fitting harness
exists; per instruction, not inventing one. **The `format` recipe has no
automated coverage** — this fix (and any future regression in it) is
verified by hand only.

## Task 2 — `verify-step.sh` sign-off

### Consumers found

Grepped `plugin/`, `tests/`, `docs/`, `scripts/` for `CLEAN`:
- `plugin/skills/build/SKILL.md:52` and `:141`: `- Exit 0 (CLEAN) → proceed.`
  — both match on **exit code**, not the literal stdout string, and describe
  the success case parenthetically. The new output still starts with
  `CLEAN`, so these remain accurate; not edited.
- No test files reference `CLEAN` or `verify-step.sh` at all (`grep -rln
  verify-step tests/` = no hits).

Also grepped `verify-step` alone across the same four directories, beyond
`SKILL.md`'s two hits: `plugin/README.md:71`, `plugin/skills/build/references/
phase-boundary.md:8,12`, `plugin/skills/build/references/
review-dispatch-template.md:121` — all reference the script by path or
describe exit-code semantics, none quote its stdout. No edits needed in any
of these.

### Change made

`plugin/skills/build/scripts/verify-step.sh`: replaced the bare `echo
"CLEAN"` with an accumulated `checks` variable, appended as each check
passes:
- After the dirty-tree check passes: `checks="tree clean"`.
- After `just precommit` passes: `checks="$checks, just precommit passed"`.
- Final line: `echo "CLEAN: $checks"` (was `echo "CLEAN"`).

Exit codes unchanged (0/1/1/2 paths all untouched otherwise).

Verified all three paths in isolation (throwaway git repos under `$TMPDIR`
with a fake `just` shim on `PATH`, cleaned up after):
- Dirty tree → `DIRTY: uncommitted changes` + `git status --porcelain`
  listing, exit 1 (unchanged, also exercised directly against this repo's
  real — legitimately dirty — tree).
- `just precommit` fails → `PRECOMMIT: validation failed`, exit 1
  (unchanged).
- Clean tree, `just precommit` passes → `CLEAN: tree clean, just precommit
  passed`, exit 0 (new sign-off, confirmed).

### docs/ updates needed (not made — read-only for this task)

- `docs/references/quality-gates.md:53-57` (D-49) and `docs/design.md:160-171`
  both describe `verify-step.sh` prose-only ("clean tree, precommit —
  blocking"), with no literal `CLEAN` string quoted — no change needed for
  Task 2.
- `docs/references/quality-gates.md` (or wherever `just precommit`'s check
  list is documented) should now note `ruff format --check` is part of
  `run-checks` / gated by `precommit` (this was previously flagged in
  `small-defects.md` item 5 as *not* gated; that gap is now closed).

## Final verification

`UV_CACHE_DIR="$TMPDIR/uv-cache" just precommit`, full output:

```
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 231 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 357 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 285 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: plugin/skills/proof/SKILL.md: 203 lines > 200
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
✓ Precommit OK
```

All nine `oversized-file:` lines are the same pre-existing allowlisted
entries reported in `small-defects.md`'s own final run — unchanged by this
batch. `ruff check`, the new `ruff format --check`, `docformatter -c`,
`mypy`, the full test suite (336 passed, 1 xfail — sentinel-cached against
this batch's own already-verified run earlier in the session, content
hash unchanged since), `rumdl`, and line limits all green.

## Files changed this batch

- `plugin/portable.just` — `format` recipe (`patch-and-print` sed fix,
  `apply-ruff-diff` restructuring, both `ruff`-sourced calls); `run-checks`
  (added `ruff format --check`)
- `justfile` — `run-checks` (added `ruff format --check`, matching its
  duplicate of `run-checks`)
- `plugin/skills/build/scripts/verify-step.sh` — accumulated `CLEAN:` sign-off
- `src/edify/check.py`, `src/edify/discovery.py`,
  `src/edify/markdown_inline_fixes.py` — reformatted by the now-working
  `just format` (content only; all three were already `M` before this batch)
- `tests/*.py` (already-dirty tracked files from earlier agents) — reformatted
  by the same `just format` run; diffs are whitespace/line-length only,
  spot-checked `tests/test_review_range_range.py`'s diff (the largest, since
  it also carries `small-defects.md` item 3's new test) to confirm no content
  loss.

Nothing else in the working tree was touched; the pre-existing uncommitted
work from earlier agents (per the dispatch instructions) was left alone
except for the formatting pass itself, which is exactly the fix under test.
