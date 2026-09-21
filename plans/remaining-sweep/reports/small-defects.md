# Small defects batch — report

Five independent items. Items 1–3 done and verified; item 4 stopped on a
documented reason plus a genuine drift needing a decision; item 5 stopped on
a root cause deeper than the anticipated trivial case. `just precommit` is
green at the end (full output at the bottom).

## Item 1 — `plugin/skills/design/SKILL.md` missing `Edit` in `allowed-tools`

Confirmed both facts: `allowed-tools` (line 8) lacked `Edit`, and
`plugin/skills/design/references/write-outline.md:123` says the outline is
written "via Edit". Confirmed the file sits on the line-limit allowlist
(`scripts/check_line_limits.allow`) at its exact line count, 285.

**Changed:** `plugin/skills/design/SKILL.md:8`
- Old: `allowed-tools: Agent, Read, Write, Bash, WebSearch, WebFetch, Skill`
- New: `allowed-tools: Agent, Read, Write, Edit, Bash, WebSearch, WebFetch, Skill`

`Edit` inserted after `Write` — the ordering `build/SKILL.md` already uses
(`Agent, Read, Write, Edit, Bash, ...`). Line count unchanged at 285
(verified with `wc -l` before and after).

## Item 2 — "exit 2 outranks exit 1" in `scripts/check_line_limits.sh`

Read the whole script. Every `exit 2` site was classified by whether it can
run after `check_cap` has already set `EXIT_CODE=1`:

- Cannot co-occur (fire during argument/allowlist parsing, strictly before
  the first `check_cap` call): `--allowlist` missing its argument, unknown
  option, malformed allowlist ceiling, CRLF in an allowlist entry, a failed
  `mktemp`, a missing explicit `--allowlist` file, a bad `ROOT`.
- Can co-occur: the unreadable-file branch inside `check_cap` (line ~126)
  and the `find`-failure branch inside `walk()` (line ~148) — both can run
  in a *later* walk stage after an *earlier* stage already found an
  over-cap file. The script's two walk loops (`for dir in src tests`, then
  `for dir in plugin docs`, then a root-level walk) run sequentially, so
  putting the exit-2 condition under `plugin` and an oversized file under
  `docs` gives a deterministic order regardless of `find`'s own
  (unspecified) per-directory entry order.

**Added:** `tests/test_line_limits_exit_codes.py` (new module, 79 lines) —
`test_unreadable_file_outranks_a_later_overage` and
`test_walk_failure_outranks_a_later_overage`, one per distinct co-occurrence
path. Moved the three shared fixture helpers (`_write_lines`,
`_run_check_line_limits`, `_write_allowlist`) out of
`tests/test_line_limits.py` into a new `tests/line_limits_helpers.py` (pure
move, no renames, following the `tests/review_range_helpers.py` pattern) —
`tests/test_line_limits.py` shrank from 380 to 323 lines, comfortably under
its 400 cap even before the new module's 79 lines are counted separately.

Both new tests pass against the unmutated script (pinning existing,
correct behavior).

**Mutation proof** (script backed up to `$TMPDIR`, mutated, tested red,
restored, verified with `cmp` — the pre-existing uncommitted CRLF-check
diff, `+4` lines, was preserved throughout and confirmed via `git diff
--stat` after each restore):

1. `check_cap`'s unreadable-file branch (line ~126): `exit 2` →
   `EXIT_CODE=2; return` (record and continue instead of exiting
   immediately).
   ```
   AssertionError: oversized-file: docs/over.md: 401 lines > 400
     .../check_line_limits.sh: line 124: plugin/locked.md: Permission denied
     check_line_limits: cannot read plugin/locked.md
   assert 1 == 2
   ```
   `test_unreadable_file_outranks_a_later_overage` went red exactly on the
   assertion (1 instead of 2) — the later `docs` overage overwrote the
   deferred `EXIT_CODE=2`.
2. `walk()`'s find-failure branch (line ~148): `exit 2` → `EXIT_CODE=2`
   (drop the `exit`, same idea).
   ```
   AssertionError: oversized-file: docs/over.md: 401 lines > 400
     find: 'plugin/locked': Permission denied
     check_line_limits: find failed under plugin
   assert 1 == 2
   ```
   `test_walk_failure_outranks_a_later_overage` went red the same way.

Both mutations restored; `cmp "$TMPDIR/check_line_limits.sh.orig"
scripts/check_line_limits.sh` reported identical each time, and `git diff
--stat -- scripts/check_line_limits.sh` showed only the pre-existing `+4`
CRLF-check diff throughout — no drift introduced.

Behavior is correctly pinned; no defect found (the existing `exit 2`
statements already short-circuit immediately, so `EXIT_CODE`'s value at
that point is irrelevant — this is exactly what makes "exit 2 outranks
exit 1" hold today).

## Item 3 — KD-2 "one hop only"

`plans/provenance-enforcement-and-routing/outline.md:106` — "No
substitution: a conflict means one of two artifacts is wrong, and the
script cannot know which. One hop only — each artifact in a chain was
compared against its predecessor at its own review." This constrains
`plugin/bin/edify-review-range.sh`: when it resolves a `Derived from:`
chain to a prior artifact, it must compare only its own `Base:` against
that immediate prior's `Base:`, and must never chase through the prior's
own `Derived from:` to an earlier ancestor (that comparison was already
settled at the prior's own review).

Read the whole script (`plugin/bin/edify-review-range.sh:142-149`):
confirmed it only ever reads the immediate prior's `Base:`
(`prior_base_line`/`prior_base`) and never reads or follows the prior's own
`Derived from:` field. This is genuine script behavior, not prose an agent
follows — a test is possible and was written.

**Added:** `tests/test_review_range_range.py::test_one_hop_only_ignores_grandprior_mismatch`
(fits the `RANGE:`-verdict module, since one-hop-only correct behavior here
resolves to `RANGE:`). Builds a three-artifact chain A→B→C: A's `Base:` is
the repo's first commit, B's `Base:` is the second commit (deliberately
different from A's — a fact already settled at B's own prior review), C's
`Base:` matches B's. One-hop-only must emit `RANGE:` (comparing only C
against B); a second-hop implementation that chased through B to A would
see C's base diverge from A's and wrongly report `CONFLICT:`.

Passes against the unmutated script (5/6 in the file passed before, now
6/6 — the new test included).

**Mutation proof** (script backed up to `$TMPDIR`; `git diff --stat` on
this file was already clean, no pre-existing diff to preserve): added a
second-hop chase after `prior_base` is computed — if the prior's own
`Derived from:` names a further `superseding` artifact, resolve *that*
artifact's `Base:` and use it in place of the immediate prior's own. Result:
```
AssertionError: CONFLICT: base aaf7f96...b643 != c7b1e52...0e8d1 inherited from plans/job-b/outline.md
assert 1 == 0
```
Test went red exactly as expected — the mutated script chased to
grandparent A and reported a spurious conflict. Restored;
`cmp` confirmed byte-identical to the pre-mutation copy, `git diff --stat`
showed no diff on `plugin/bin/edify-review-range.sh` afterward.

## Item 4 — `justfile` / `plugin/portable.just` duplication — STOPPED, real choice

The root `justfile` **already** does `import 'plugin/portable.just'`
(`justfile:6`) — all of `precommit`/`test`/`format`/`lint`/`green`/`check`/
`claude`/`claude0` live only in `portable.just` and reach `just --list` via
the import; there is no duplicate copy of those recipes. The actual
duplication is narrower than the brief assumed: **both files define their
own `bash_prolog` variable** (justfile:71-188, portable.just:6-87).

**Documented reason, found in place:** `plugin/portable.just:3` — "Import in
consuming projects: import 'portable.just'" — and `plugin/portable.just:5-`
"Self-contained bash prolog for portable module (cannot rely on root
justfile's bash_prolog)" together with `plugin/portable.just:3`, "Variables
merge across import boundaries; root justfile's bash_prolog overrides this
one." `docs/superpowers/design/plugin-transition-evaluation.md:40` confirms
the import's intended scope: "`portable.just` supplies `bash_prolog` +
`precommit`/`test`/`format`/`lint`/`check`/`claude`". This is `just`'s own
variable-merge semantics: when an importing file redefines a variable the
imported module also defines, the importer's definition wins globally,
including inside the imported module's own recipes. So `portable.just`
ships a self-contained `bash_prolog` so it works when vendored standalone
into *another* project with no override, while in `edify` itself every
recipe (including `portable.just`'s own `precommit`, `test`, etc.) actually
runs under **root's** `bash_prolog` (which adds `trace`, `wt-path`,
`add-sandbox-dir` that generic consumers don't need). This is intentional,
not an oversight — leaving it alone.

**Drift found, reported rather than fixed** (a real design choice, not a
mechanical fix): the two `bash_prolog` copies are otherwise byte-identical
except `fail()`:
- `justfile:84`: `fail () { echo "${ERROR}$*${NORMAL}"; exit 1; }` — stdout,
  no `FAIL:` prefix.
- `plugin/portable.just:18`: `fail () { echo "${RED}FAIL: $*${NORMAL}" >&2; exit 1; }`
  — stderr, `FAIL: ` prefix.

Because of the override semantics above, this drift is inert *inside
edify* — every recipe here always runs under root's `fail()`. It only bites
a project that vendors `portable.just` standalone (its own stated use
case): that project gets the stderr+prefixed version, which is arguably the
better one, and root's copy here would silently diverge from it further if
either is edited without the other. Left both files untouched; whether to
converge `fail()` (and if so, which behavior wins) is a call for whoever
owns the choice, not a mechanical fix — reporting it here per instruction.

## Item 5 — `ruff format --check` diffs `just precommit` doesn't catch — STOPPED, deeper cause

Reproduced with `UV_CACHE_DIR="$TMPDIR/uv-cache" uv run ruff format --check
src/edify` (the project's default `uv` cache directory was not writable in
this sandbox; this env var redirected it to a writable path — noted per
instruction, no other workaround needed). Confirmed 3 files pending:
`src/edify/check.py`, `src/edify/discovery.py`,
`src/edify/markdown_inline_fixes.py`.

Investigated why `just format` (`plugin/portable.just:126-146`) does not
clear them. The recipe pipes `ruff format -q --diff` and `ruff check -q
--fix-only --diff` output into a local `patch-and-print()` helper that runs
bare `patch "$@"` with **no `-p`/strip-level flag** — unlike the
`docformatter --diff ... | patch-and-print -Rp1` call three lines later,
which does pass one. `ruff format --diff`'s unified-diff header carries no
`a/`/`b/` prefix (`--- src/edify/check.py` / `+++ src/edify/check.py`), so
it needs `-p0`; bare `patch` cannot reliably auto-detect that and, run
non-interactively (stdin not a tty, as in this sandbox and presumably in
CI), silently answers "no" to its own "File to patch:"/"Reversed patch"
prompts and skips every hunk — in an interactive terminal it would instead
hang waiting for input. Verified directly:
```
$ patch < ruff-format.diff          # bare, from repo root
can't find file to patch at input line 3
...
Skip this patch? [y]
$ patch -p0 < ruff-format.diff      # explicit -p0
patching file src/edify/check.py
patching file src/edify/discovery.py
patching file src/edify/markdown_inline_fixes.py
```
`-p0` applies cleanly and reproduces exactly what `ruff format` (no
`--diff`) would do directly. Ran `just trace=true format` against the real
tree to confirm end-to-end: it printed no "Reformatted files" line and
`ruff format --check` still failed afterward on the same 3 files —
`just format` is not a no-op by luck, it is silently applying nothing for
both of the `ruff`-sourced diffs (format *and* lint autofixes share the
same broken `patch-and-print` call with no pending lint-autofix diffs to
demonstrate against right now, but the mechanism is identical and would
fail the same way).

One incidental finding while narrowing this down, not a defect: `ruff
format --diff` on `src/edify/discovery.py` proposes removing the
parentheses in `except (json.JSONDecodeError, OSError):` →
`except json.JSONDecodeError, OSError:`. That looks like Python-2 syntax
but is valid under PEP 758 (parenthesis-free multi-exception `except`),
landed in Python 3.14 — `pyproject.toml`'s `requires-python = ">=3.14"`
makes ruff correctly target it. Confirmed with `ast.parse` on the
reformatted file under this repo's Python 3.14.3: no syntax error.

**Per the task's own condition** ("Only if the cause is simply 'precommit
never runs the format check and `just format` does clear the diffs' apply
the fix. Otherwise change nothing.") — the cause here is *not* that simple
case: `just format` does **not** clear the diffs, due to the missing
`-p0` on both `ruff`-sourced `patch-and-print` calls in
`plugin/portable.just`. Changed nothing in `pyproject.toml`,
`plugin/portable.just`, or `src/edify/*` for this item. The `format` recipe
bug (add `-p0` to the two `ruff ... --diff | patch-and-print` calls) and
whether/how to add a `ruff format --check` gate to `precommit` are both
real fixes for whoever owns this decision — flagging both here rather than
choosing.

## docs/ updates needed (not made — docs/ is read-only for this task)

- `docs/references/quality-gates.md` (or wherever `just precommit`'s check
  list is documented) should note that `ruff format --check` is not
  currently gated by `precommit`, once item 5 is resolved either way.
- No design-doc update needed for items 1–4.

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

All nine `oversized-file:` lines are pre-existing `scripts/check_line_limits.allow`
entries reported at their exact allowlisted ceiling (disclosure, not
failure) — matches the allowlist verbatim, nothing new. `ruff check`,
`docformatter -c`, `mypy`, the full test suite (336 passed, 1 xfail —
pre-existing, unrelated to this batch), `rumdl`, and line limits all green.

Full `pytest` run for the files touched in this batch, standalone:
`tests/test_line_limits.py`, `tests/test_line_limits_exit_codes.py`,
`tests/test_review_range_*.py` — 31/31 passed.

## Files changed this batch

- `plugin/skills/design/SKILL.md` — `allowed-tools` line (item 1)
- `tests/line_limits_helpers.py` — new, shared fixtures moved from
  `tests/test_line_limits.py` (item 2)
- `tests/test_line_limits.py` — now imports the moved helpers (item 2)
- `tests/test_line_limits_exit_codes.py` — new, two co-occurrence tests
  (item 2)
- `tests/test_review_range_range.py` — added
  `test_one_hop_only_ignores_grandprior_mismatch` (item 3)

Nothing changed for items 4 and 5 — both left as found, pending a decision.
`scripts/check_line_limits.sh` and `plugin/bin/edify-review-range.sh` are
unchanged from before this batch (mutation-proof cycles fully restored and
verified).
