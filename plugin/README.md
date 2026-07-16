# edify plugin

A lean [Claude Code][claude-code] bundle of framework-agnostic skills. It
carries no workflow engine — the earlier `design → runbook → orchestrate`
pipeline, its session/worktree task model, and the homegrown recall system were
torn down in 2026-05 when the ecosystem (superpowers, native memory) caught up.
What remains is the part that was worth keeping.

A plain subdirectory of the `edify` repo (previously a git submodule). Skills
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
