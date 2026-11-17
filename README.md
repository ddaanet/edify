# edify

A [Claude Code][claude-code] plugin of working-discipline skills for an
orchestrating agent: a release cascade, a per-commit review loop, rules for
dispatching subagents, a markdown fixer and a token counter.

## Install

Through the ddaanet marketplace:

```text
/plugin marketplace add ddaanet/marketplace
/plugin install edify@ddaanet
```

## Plugin

The plugin lives at the repository root. Skills are invoked as slash commands:

- `/edify:release` — release `dev` onto `main` through the review cascade.
- `/edify:review` — review each commit as it lands, triage, fix.
- `/edify:dispatch` — rules for dispatching subagents.
- `/edify:markdown` — fix structural defects in agent-written markdown.
- `/edify:token-counting` — count file tokens with the Anthropic API.
- `/edify:ground` — ground a methodology in external research.

Plus the `brainstorm-name` agent and two scripts, `bin/edify-markdown` and
`bin/edify-count-tokens`. See [`plugin/README.md`](plugin/README.md).

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
