# Item 1.10, slices 1-2 — GREEN

## Approach

Rewrote `scripts/check_line_limits.sh`:

- Accepts optional `--allowlist FILE` (parsed and discarded — not
  implemented yet, KD-7 defers `--allowlist` and per-entry ceilings to
  slices 4-5) and optional `ROOT` (default `.`); `cd`s into `ROOT` so all
  reported paths are root-relative.
- Factored the per-file check into one function, `check_cap FILE CAP`, so
  the allowlist can hook in later without a rewrite.
- Kept the existing Python gate (`src`, `tests`, `*.py`, cap 400) but
  switched its message to `oversized-file: <path>: <n> lines > <cap>`.
- Added a markdown gate: `plugin/` and `docs/` walked recursively for
  `*.md`, plus root-level `*.md` via `find . -maxdepth 1` (leading `./`
  stripped so the reported path matches the recursive-scan form). Cap is
  200 when the basename is `SKILL.md`, 400 otherwise. `docs/superpowers/plans/`
  and `docs/superpowers/specs/` are skipped by a `case` match on the
  found path.
- `src`/`tests`/`plugin`/`docs` are each tested for existence (`[ -d "$dir" ]
  || continue`) before `find` runs, so a fixture tree missing some of them
  does not error — no `find ... 2>/dev/null` anywhere.
- Deleted the dead `agents/decisions` loop and its `2>/dev/null` (this was
  also Item 1.11's listed deletion; done here since the loop was being
  rewritten anyway).

## Test results

`pytest tests/test_line_limits.py -v`: 2/2 passed
(`test_line_limits_passes_clean_tree`, `test_line_limits_fails_markdown_over_400`).

`pytest -q` (full suite): 306/322 passed, 16 skipped — same skip count as
before this change, no new failures.

`shellcheck scripts/check_line_limits.sh`: no output, clean.

`ruff check tests/test_line_limits.py`: all checks passed.
`mypy tests/test_line_limits.py`: no errors.
`docformatter --diff tests/test_line_limits.py`: no diff.

## Precommit over the real tree (expected RED — designed state until slice 4)

`PATH=.../.venv/bin:$PATH just precommit` exits 1. Full `oversized-file:`
list it printed:

```
oversized-file: plugin/agents/corrector.md: 605 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 412 lines > 400
oversized-file: plugin/agents/design-corrector.md: 413 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 213 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 310 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 221 lines > 200
oversized-file: docs/design.md: 1213 lines > 400
```

This is the designed state per the dispatch: real files are over cap and
the allowlist does not exist yet (slice 4). Item 1.11 needs these measured
counts.

## Commit step

Precommit is red by design (the gate this very slice built now enforces
caps the repo doesn't yet meet), so the normal "precommit green" commit
gate cannot pass. Checked whether the repo's actual pre-commit *hook*
(distinct from `just precommit`) runs this script — it does not; the
parent repo's git hook is gitlore's memory gate, unrelated to line limits.
So the hook does not block, and the commit proceeded normally (hooks ran,
none skipped, no `--no-verify`).
