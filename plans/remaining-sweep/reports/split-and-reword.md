# Split test_review_range.py + drop "framework-agnostic"

## Task A — split tests/test_review_range.py

**Files created:**

- `tests/review_range_helpers.py` (132 lines) — shared fixtures, moved
  verbatim from the original file with no renaming: `REPO_ROOT`, `BIN_DIR`,
  `_run_git`, `_init_repo`, `_write_artifact`, `_second_pass_derived_from`,
  `_write_artifact_no_provenance_section`, `_run_review_range`.
- `tests/test_review_range_range.py` (125 lines) — the `RANGE:` verdict: 5
  tests.
- `tests/test_review_range_no_provenance.py` (74 lines) — the
  `NO-PROVENANCE:` verdict: 2 tests (one parametrized ×3).
- `tests/test_review_range_conflict.py` (42 lines) — the `CONFLICT:` verdict:
  1 test.
- `tests/test_review_range_unresolved.py` (30 lines) — the `UNRESOLVED:`
  verdict: 1 test.
- `tests/test_review_range_no_prior.py` (65 lines) — the `NO-PRIOR:` verdict:
  2 tests (one parametrized ×2).

No fifth "non-verdict" module was needed — every test in the original file
exercises one of the five verdicts; there were no argument/usage-error tests.

**Files deleted:** `tests/test_review_range.py` (396 lines), via `git rm`.

Each split file imports the shared helpers directly by their original
underscore-prefixed names (`from .review_range_helpers import _init_repo,
...`) — no aliasing, no renaming. Test function bodies, docstrings and
assertions are byte-identical to the original file; only the import lines and
each file's own module docstring changed.

**Before/after test-ID comparison** (`pytest --collect-only -q ... -p
no:markdown_report`, since the repo's default `pytest-markdown-report` plugin
suppresses the collect-only listing — ran with plain `pytest`, not `uv run
pytest`, because `uv`'s cache directory is read-only in this sandbox):

- Before: 14 tests collected from `tests/test_review_range.py`.
- After: 14 tests collected across the 5 new files.
- `diff` of both listings with the module-path prefix stripped: **no
  differences** — every test name and parametrize ID (`[no-section]`,
  `[only-derived-from]`, `[only-base]`, `[base-absent]`, `[base-short]`)
  matches exactly.
- All 14 pass when run together: `pytest -q tests/test_review_range_*.py -p
  no:markdown_report` → `14 passed`.

**Live references updated:** grepped the whole tree for
`test_review_range.py`. The only live (non-frozen-report) hit was
`.claude/handoff-todo.md:12` ("Split `tests/test_review_range.py` before
anything else touches it...") — removed that line since the split is done.
Every other hit is under `plans/provenance-enforcement-and-routing/reports/`
(frozen TDD-slice reports) and was left untouched as instructed.

## Task B — drop the "framework-agnostic" claim

Whole-tree `grep -rn -i "framework-agnostic"` (excluding `.git`,
`plans/*/reports`, `inbox/`, `memory/`) found exactly the 4 sites the brief
named, no surprises:

1. `plugin/.claude-plugin/plugin.json` `description`:
   - Old: `"A lean bundle of framework-agnostic Claude Code skills"`
   - New: `"A lean bundle of Claude Code skills and agents built around a
     requirements → design → runbook → build planning pipeline"`
   - Version left at `0.2.0` (unchanged); JSON validated with `python3 -c
     "import json; json.load(open(...))"`.

2. `plugin/README.md` line 3:
   - Old: "A [Claude Code][claude-code] bundle of framework-agnostic skills
     and agents, built around a `requirements → design → runbook → build`
     planning and execution pipeline."
   - New: "A [Claude Code][claude-code] bundle of skills and agents built
     around a `requirements → design → runbook → build` planning and
     execution pipeline."
   - `/formalize`'s row in this file's skill table already says "Verify a
     Python function against intent via an icontract contract checked with
     `edify check` (CrossHair)" — already Python-only, no change needed there.

3. `README.md` line 5:
   - Old: "...plus a Claude Code plugin (`plugin/`) that ships a handful of
     framework-agnostic skills."
   - New: "...plus a Claude Code plugin (`plugin/`) that ships skills and
     agents built around a requirements → design → runbook → build planning
     pipeline."

4. `README.md` line 37 (now ~36-37, plus the `/formalize` bullet):
   - Old: "It ships framework-agnostic skills invoked as slash commands, in
     two groups: ... **Standalone** — `/proof`, `/deliverable-review`,
     `/ground`, `/formalize`, `/recall`."
   - New: "It ships skills and agents invoked as slash commands, in two
     groups: ... **Standalone** — `/proof`, `/deliverable-review`, `/ground`,
     `/formalize` (Python only: icontract contracts checked with CrossHair),
     `/recall`."

Verified against `plugin/skills/` (`ls`): `build`, `deliverable-review`,
`design`, `formalize`, `ground`, `proof`, `recall`, `requirements`, `review`,
`runbook` — confirms the local tree uses `/build`, not `/orchestrate` or
`/inline`, matching what both READMEs already said.

**Occurrences found and deliberately left:**

- `inbox/brief-drop-framework-agnostic-claim.md` — the brief itself, excluded
  per instructions.
- `memory/strategic-pivot.md:17,26` — two mentions of "framework-agnostic"
  describing a skill's review core and a batch of prose skills; excluded per
  instructions (memory/ out of scope) and semantically unrelated to the
  plugin's headline descriptor this brief targets.
- The brief's own "Constraints" section names a fifth site outside this repo
  — `../claude-plugins/.claude-plugin/marketplace.json` — explicitly left
  alone there too (outside `/Users/david/code/edify`, and the brief says not
  to touch it until after release).

## Precommit

`cd "/Users/david/code/edify" && just precommit` — full output:

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

Exit code 0. The 9 `oversized-file` lines are pre-existing, allowlisted
(non-blocking) warnings — none of the files in the list are ones this job
touched, and `.claude/handoff-todo.md` already tracked them as "unowned on
the line-limit allowlist" before this session started. A prior run in this
session (before `just format` was applied) also surfaced a ruff `I001`
import-sort error on the 5 new split-test files and an `rumdl` reflow request
on the new `README.md` wording — both fixed by running the project's own
`just format` recipe, then confirmed clean by the `just precommit` run above.

## Anything left undone

Nothing from either task. Both are complete and verified.
