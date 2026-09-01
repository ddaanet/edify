# edify

A lean [Claude Code][claude-code] toolkit in one tree: a Python CLI
(`edify-cli`) for working with session data, tokens, and markdown, plus a
Claude Code plugin (`plugin/`) that ships a handful of framework-agnostic
skills.

Direction: Lean-assisted (formal-proof-backed) requirements tracking.

## Install

```bash
uv tool install edify-cli
```

Requires Python 3.14+ and [uv]. To work from source instead, clone the repo
and run `uv tool install .` in it.

## CLI (`edify-cli`)

Source in `src/edify/`. Six commands in four groups:

- **Session scraping** — `edify list`, `edify extract <prefix>`, `edify
  collect`. Parse the JSONL under `~/.claude/projects/` to pull your own
  messages back out, per session or across all of them.
- **Token counting** — `edify tokens FILE...`. Count tokens via the Anthropic
  API (needs `ANTHROPIC_API_KEY`); the `haiku`/`sonnet`/`opus` aliases resolve
  to the latest model.
- **Markdown postprocessing** — `edify markdown`. Reads file paths from stdin
  and fixes structural issues formatters can't, in place. Pair with [dprint]
  for formatting.
- **Contract checking** — `edify check <target>`. Verify a Python function
  against its icontract contract with CrossHair.

## Plugin

The `plugin/` directory is a Claude Code plugin — a plain subdirectory of this
repo (previously a git submodule). It ships framework-agnostic skills invoked
as slash commands, in two groups:

- **Pipeline** — `/requirements` → `/design` → `/runbook` → `/orchestrate`
  (or `/design` → `/inline` for work that needs no runbook), with `/review`
  as the in-progress quality gate.
- **Standalone** — `/proof`, `/deliverable-review`, `/ground`, `/formalize`,
  `/recall`.

Plus the agents the pipeline dispatches. See
[`plugin/README.md`](plugin/README.md).

## Development

```bash
just dev        # format + check + test
just test       # tests only
just check      # lint + type check
just precommit  # all checks (CI equivalent)
```

Python 3.14+ with [mypy] strict types, [pytest] for tests, [ruff] for linting,
[uv] for dependencies, and [just] for tasks. Design is recorded in
`docs/design.md`.

## License

MIT

[claude-code]: https://github.com/anthropics/claude-code
[dprint]: https://dprint.dev
[mypy]: https://mypy.readthedocs.io
[pytest]: https://pytest.org
[ruff]: https://docs.astral.sh/ruff
[uv]: https://docs.astral.sh/uv
[just]: https://just.systems
