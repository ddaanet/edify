# GREEN — `scripts/check_design_links.sh`

No commit — orchestrator commits.

## Order tests went green

Implemented the full contract in one pass (all six invariants plus the
sign-off line), not incrementally per test, since the checks share the same
two parsed tables (node definitions, index entries) and splitting them across
separate implementation passes would have meant re-parsing or stubbing parts
of a table the earlier tests didn't need. First full run against the suite
came back `4/12 passed, 8 failed` — the four purely-structural exit2 tests
passed, the six content-detection tests and the two exit-0 sign-off tests
failed.

Root cause (one bug, explaining all 8 failures): `count_def()` / `count_idx()`
used an un-`local` loop variable `i` for their internal scan
(`for ((i = 0; ...))`), which is the *same* variable the callers were
iterating with in their own `for ((i = 0; i < DEF_COUNT; i++))` loops — a
plain `for ((...))` loop variable is an ordinary global in bash, not scoped.
Calling `count_def`/`count_idx` from inside the caller's loop body clobbered
the caller's `i` mid-iteration: the `[ "$FIRST_INDEX" -ne "$i" ] && continue`
first-occurrence guard then compared `FIRST_INDEX` against the *post-scan*
`i` (equal to `DEF_COUNT`/`IDX_COUNT`) instead of the caller's real index, so
it spuriously `continue`d on every iteration and no per-id check ever ran —
manifesting as silently-missing violations in six tests, and as an
`unbound variable` abort (`DEF_CONCLUSION[$i]` with `i` now out of bounds) in
the two sign-off tests and `test_design_links_real_repo_root`, since that
loop's `i` was clobbered too. Fixed by giving both functions their own
`local ... j` and scanning with `j` instead of `i` (`scripts/check_design_links.sh:176-198`).
After the fix, all 12 pass together on the first re-run — no test-by-test
sequence beyond that, since the fix was structural, not per-test.

```
$ UV_CACHE_DIR="$TMPDIR/uv-cache" uv run pytest tests/test_design_links.py -p no:markdown_report -q
............                                                             [100%]
12 passed in 0.83s
```

## Real-shape verification done before writing the script

Cross-checked the design in `plans/remaining-sweep/reports/crosslink-red.md`
against the live tree before coding, not just trusted the report:

- Grepped `docs/references/*.md` and `docs/decisions.md` for `D-` counts: 85
  definitions, 85 index lines, 8 groups, 8 `docs/references/*.md` files — the
  real repo is fully cross-linked already (confirmed independently, not
  assumed from the red report).
- Confirmed `L-` ids exist only in `docs/design.md` (the hub), never in
  `docs/references/*.md` or `docs/decisions.md` — out of this checker's scope
  by construction (it only reads decisions.md + references/*.md), so no `L-`
  handling was needed despite the red report's "85 D-/L- ids" phrasing (that
  count spans the whole tree including the hub; the subset this script reads
  is D- only).
- Verified with a small Python probe that no node's bolded conclusion
  contains a literal `*` anywhere in the real tree — this is what makes the
  `[^*]*` non-backtracking-into-ambiguity extraction safe; recorded as the
  script's own residual bound rather than assumed silently.
- Hand-traced the D-31 (superseded) prefix case and the D-67/D-68 case
  (conclusion text containing internal periods inside backtick-quoted
  paths, e.g. `.claude/rules/`) through both regexes to confirm greedy
  matching with `$`-anchoring lands on the *trailing* sentence period, not an
  internal one — this is exactly the case the red report flagged as
  load-bearing.

No test looked wrong or unsatisfiable against the real docs; no blocker of
that kind.

## Script's final contract header

```
#!/usr/bin/env bash
# Check the crosslink invariants of the split living design: hub
# docs/design.md, decision index docs/decisions.md, argument nodes
# docs/references/*.md.
#
# Usage: check_design_links.sh [ROOT]
#
# ROOT defaults to `.`. Reads ROOT/docs/decisions.md and
# ROOT/docs/references/*.md.
#
# A node's decision definition is a bolded paragraph lead,
# `**D-<n> — <conclusion>.**`, possibly wrapped across physical lines by
# `just format`'s 80-column reflow. A decisions.md index line is
# `- **D-<n>** — <conclusion>.`, also possibly wrapped, continuation
# indented. A group is `## <Group Name>` then `Argued in
# \`docs/references/<file>.md\`.`. Paragraphs are joined (wrap lines rejoined
# with a single space) before matching, so a wrap never misreports as a
# violation.
#
# Checked, one violation line per finding (`<kind>: <ID or path>: <detail>`):
#   unindexed-decision   — a node's D-<n> has no index line
#   orphan-index-line    — an index D-<n> has no node definition
#   duplicate-definition — a D-<n> defined in more than one node
#   duplicate-index-line — a D-<n> indexed more than once
#   conclusion-mismatch  — the index conclusion does not have the node's
#                          conclusion (trailing period stripped) as a
#                          prefix — not equality: a superseded decision's
#                          index line appends a parenthetical the node's own
#                          lead does not carry
#   missing-node         — a group's `Argued in` path does not resolve to a
#                          real file
#
# A clean run prints one sign-off line naming the counts, never a bare "OK":
#   design-links: N decisions indexed, defined once, conclusions match, M
#   nodes present
#
# Exit codes: 0 clean, 1 on any violation, 2 on a failure to run the check
# (missing docs/decisions.md or docs/references/, or a find/read failure) —
# 2 outranks 1: a run failure is reported instead of whatever violations a
# partial scan could see.
#
# Residual bound: `[^*]*` assumes a node's bolded conclusion never itself
# contains a literal `*`; true of every conclusion in the real tree at the
# time this was written (verified across all D-<n> ids). Portable to macOS
# bash 3.2: no associative arrays, indexed arrays walked by C-style `((i++))`
# loops rather than `"${arr[@]}"` expansion, since expanding an empty array
# under `set -u` aborts pre-4.4 bash.
```

Full file: `scripts/check_design_links.sh` (executable, 269 lines).

Run against the real tree:

```
$ UV_CACHE_DIR="$TMPDIR/uv-cache" just design-links
# design links
design-links: 85 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Design links OK
```

## Wiring choice and proof

**Choice: root `justfile` only, not `plugin/portable.just`.** `precommit` and
`dev` are themselves *defined* in `plugin/portable.just` (imported by the root
justfile), which is the module distributed to other projects via
`just update-plugin-dev`. Those projects have no `docs/decisions.md` or
`docs/references/`, so a design-links call baked into portable.just's
`precommit` would break every consumer's gate. The root justfile already
establishes the override mechanism this repo needs: it re-declares its own
`bash_prolog` (`justfile:71-189`) which — per `set allow-duplicate-variables`
and just's file-order-wins rule for duplicate variables — completely replaces
portable.just's `bash_prolog` for *every* recipe in the merged justfile,
including recipes textually defined inside portable.just (`precommit`,
`dev`, `test`, `format`). That's why the root file's `bash_prolog` re-declares
`run-checks`, `run-pytest`, `run-line-limits`, `report-end-safe`, etc. instead
of only defining recipes unique to the root file — those functions must exist
in whichever `bash_prolog` wins, and root's wins unconditionally.

The same mechanism (`set allow-duplicate-recipes`, already set at
`justfile:8`) lets the root file *override a recipe by name*, not just the
shared prolog variable. I added:

- `run-design-links()` to the root `bash_prolog`, beside `run-line-limits()`
  (`justfile:182-184`): `report "design links" ./scripts/check_design_links.sh`.
- A standalone `design-links` recipe (`justfile:56-62`), mirroring the
  existing `line-limits` recipe shape exactly.
- A root-local override of `precommit` (`justfile:64-89`) — a full copy of
  portable.just's `precommit` body with one line added, `run-design-links`,
  placed after `run-line-limits`, so its output lands under its own
  `# design links` header exactly like `# line limits`. `dev: format precommit`
  (defined in portable.just, unchanged) picks up the override automatically:
  `just` resolves a recipe *dependency* by name against the final merged
  recipe set, not against the file that named it, so `dev`'s call to
  `precommit` reaches the root override without `dev` itself being touched.

portable.just is otherwise untouched — no design-links reference anywhere in
it, so `just update-plugin-dev` and any other project importing it are
unaffected.

**Proof**, run against the live (already-dirty) `docs/decisions.md`:

```
$ cp docs/decisions.md "$TMPDIR/decisions.md.orig"
$ cmp docs/decisions.md "$TMPDIR/decisions.md.orig"
backup ok
```

Deleted the `D-1` index line (`docs/decisions.md:15`) with an exact edit
(removed the one line, nothing else touched):

```
$ UV_CACHE_DIR="$TMPDIR/uv-cache" just precommit
...
# design links
unindexed-decision: D-1: defined in docs/references/cli-and-package.md but has no index line in docs/decisions.md
✗ Precommit failed
```

Restored the line with the exact inverse edit, then confirmed byte-identical
to the pre-edit backup (`git diff --quiet` alone doesn't prove this, since
`docs/decisions.md` already carries unrelated uncommitted changes from
earlier in the sweep — same file, same dirty state before and after either
way):

```
$ cmp docs/decisions.md "$TMPDIR/decisions.md.orig"
restored exactly — identical to pre-edit backup
```

Re-ran `just precommit`: the design-links section is now clean.

```
$ UV_CACHE_DIR="$TMPDIR/uv-cache" just precommit
...
# design links
design-links: 85 decisions indexed, defined once, conclusions match, 8 nodes present
✗ Precommit failed
```

`just precommit`'s overall exit code is still 1 here — see "Blocker" below;
the design-links gate itself is proven wired and green.

## Gates — full untruncated output

### `just test`

```
$ UV_CACHE_DIR="$TMPDIR/uv-cache" just test
# Test Report

**Summary:** 348/349 passed, 1 xfail
✓ Tests OK
```

### `just lint`

```
$ UV_CACHE_DIR="$TMPDIR/uv-cache" just lint
**Reformatted files:**
  - tests/test_design_links.py
# ruff check
tests/test_design_links.py:31:89: E501 Line too long (89 > 88)
# docformatter -c
tests/test_design_links.py
Tests cached (inputs unchanged)
✗ Lint failed
```

**Blocker — not mine to fix:** `tests/test_design_links.py:31` (module
docstring prose) is 89 columns, and `tests/test_design_links.py:74` and
`:165` (two test docstrings) trip `docformatter`'s D205 (blank line required
between summary and description) once `ruff format` reflows them. All three
are pre-existing in the RED-authored file — present already in the very first
`Read` of `tests/test_design_links.py` before I changed anything — not
something my script or the `just lint` reformat introduced. My mandate
explicitly excludes editing `tests/test_design_links.py` or
`tests/design_links_helpers.py`; fixing this requires editing the former.
Flagging per "stop and report `blocked: ... — <why>` rather than bending the
script or the test" — this isn't one of the 12 tests, so it doesn't block the
GREEN slice itself, but it does block `just lint` and `just precommit` from
going fully green until someone with write access to that file wraps those
three lines. `run-design-links`/`run-checks` themselves are not implicated —
`ruff check`/`docformatter` ran the same on this file whether or not
design-links exists.

Note: `just lint` also ran `ruff format` (non-`--check`, so it auto-fixes) as
part of its own recipe, which reformatted `tests/test_design_links.py` in
place before reporting the residual E501/D205 findings — that's the project's
own gate doing its job, not a manual edit by me; the file's test content and
assertions are unchanged, confirmed by `just test` staying at 348/349 passed
+ 1 xfail both before and after.

### `just precommit`

```
$ UV_CACHE_DIR="$TMPDIR/uv-cache" just precommit
# ruff check
tests/test_design_links.py:31:89: E501 Line too long (89 > 88)
tests/test_design_links.py:74:5: D205 1 blank line required between summary line and description
tests/test_design_links.py:165:5: D205 1 blank line required between summary line and description
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
# design links
design-links: 85 decisions indexed, defined once, conclusions match, 8 nodes present
✗ Precommit failed
```

Two failure sources, neither introduced by this slice and neither in
`scripts/check_design_links.sh` or the `justfile` wiring:

1. The `ruff check` block above (same `tests/test_design_links.py` blocker as
   under `just lint`).
2. The `line limits` block: nine pre-existing oversized files, all under
   `plugin/agents/`, `plugin/skills/*/SKILL.md`, and
   `docs/superpowers/design/`. These match files the session's git status
   shows as concurrently modified by other in-flight agents in this sweep
   (design-split, skill-doc-pass, split-review, and others touching
   `plugin/agents/`, `plugin/skills/`, `docs/superpowers/`) — outside this
   slice's scope (`scripts/check_design_links.sh` + the design-links
   wiring), and the tree is explicitly "leave it alone" for everything else.

The `# design links` section itself is clean, matching the standalone
`just design-links` run above.

## Docs updates needed (not made — out of scope for this slice)

- `docs/references/quality-gates.md`: **D-46**'s enumeration of the automated
  layer ("`ruff format --check`, a non-fixing markdown reflow check, line
  limits, lint, tests") should add design-links once this lands, alongside
  line limits.
- `docs/changelog.md`: a dated entry recording the new
  `scripts/check_design_links.sh` gate and its `just precommit` wiring, in
  the same style as the existing "review gate — record the markdown gate in
  the living design" entry.

Neither edited — the dispatch said not to touch `docs/` beyond what's needed
to prove the wiring (the temporary `docs/decisions.md` edit, restored
exactly).
