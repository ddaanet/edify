# Agent Instructions

Edify is a lean Claude Code skills bundle plus a small CLI toolkit. Direction: Lean-assisted (formal-proof-backed) requirements tracking.

@plugin/fragments/communication.md

## Core Behavioral Rules

@plugin/fragments/error-handling.md

@plugin/fragments/no-confabulation.md

@plugin/fragments/no-estimates.md

@plugin/fragments/source-not-generated.md

@plugin/fragments/code-removal.md

@plugin/fragments/tmp-directory.md

@plugin/fragments/project-tooling.md

## CLI (`edify-cli`)

Source in `src/edify/`. Four tools:
- **Session scraping** — `edify list | extract <prefix> | collect`
- **Token counting** — `edify tokens FILE...` (Anthropic API)
- **Markdown postprocessing** — `edify markdown` (reads paths from stdin)
- **Contract checking** — `edify check <target>` (CrossHair verification)

## Skills

In `plugin/skills/`, invoked via slash command: `proof`, `ground`, `requirements`, `deliverable-review`, `token-efficient-bash`, `formalize`.

## Recipes

- `just precommit` — run all checks
- `just test *ARGS` — run test suite
- `just dev` — format and run all checks
- `just format` / `just lint` / `just check`

## Design Decisions

See `agents/decisions/` — `cli`, `markdown-tooling`, `data-processing`, `testing`, `project-config`, `deliverable-review`.
