# edify plugin

A lean [Claude Code][claude-code] bundle: a handful of framework-agnostic
skills plus behavioral instruction fragments. It carries no workflow engine —
the earlier `design → runbook → orchestrate` pipeline, its session/worktree
task model, and the homegrown recall system were torn down in 2026-05 when the
ecosystem (superpowers, native memory) caught up. What remains is the part that
was worth keeping.

Consumed as a git submodule of the `edify` repo. Fragments load into every
conversation via `@` references in the consuming project's `CLAUDE.md`; skills
are invoked as slash commands.

## Skills

Slash-command procedures that inject instructions into the current
conversation. Each lives in `skills/<name>/SKILL.md`.

| Skill | Purpose |
|-------|---------|
| `/requirements` | Capture and document requirements for design and planning |
| `/proof` | Item-by-item structured user validation of an artifact before it ships |
| `/deliverable-review` | Post-execution artifact review, severity-classified against ISO 25010 / IEEE 1012 |
| `/ground` | Ground a methodology in external research before asserting it (diverge–converge) |
| `/formalize` | Verify a Python function against intent via an icontract contract checked with `edify check` (CrossHair) |

## Fragments

Reusable instruction files loaded as ambient context via `@` references in
`CLAUDE.md`. They state behavioral rules the agent must hold every turn.

| Fragment | Rule |
|----------|------|
| `communication.md` | Report observable state; don't let output-style plugins override prose rules |
| `error-handling.md` | Errors never pass silently; don't escape to `sed` after Edit failures |
| `no-confabulation.md` | Never present invented heuristics or thresholds as established fact |
| `no-estimates.md` | No estimates or predictions unless explicitly requested |
| `code-removal.md` | Delete obsolete code — don't archive or comment it out |
| `source-not-generated.md` | Edit source files, never generated output |
| `tmp-directory.md` | Use the harness scratchpad or project-local `tmp/` for temp files |
| `project-tooling.md` | Prefer existing project recipes; check platform capabilities before building |

## Scripts

Utility scripts in `bin/` (Python 3):

| Script | Purpose |
|--------|---------|
| `bump-plugin-version.py` | Bump the plugin manifest version |
| `check-version-consistency.py` | Verify plugin and package versions agree |
| `deliverable-inventory.py` | Diff merge-base→HEAD, classify changed files, report counts |

## Recipes

`just precommit` runs the plugin's own checks. See `justfile` and
`portable.just`.

[claude-code]: https://docs.claude.com/en/docs/claude-code/overview
