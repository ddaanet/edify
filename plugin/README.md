# edify plugin

A [Claude Code][claude-code] plugin of working-discipline skills for an
orchestrating agent, plus two small standard-library scripts.

Install through the ddaanet marketplace:

```text
/plugin marketplace add ddaanet/marketplace
/plugin install edify@ddaanet
```

## Skills

Each lives in `skills/<name>/SKILL.md`.

| Skill | Purpose |
|-------|---------|
| `/edify:release` | Release `dev` onto `main`: simplify, parallel release reviews, triaged fixes, a medium loop, then push, preflight and `just release` |
| `/edify:review` | Per-commit review loop: a medium code review of each commit, triage, fix commits reviewed the same way |
| `/edify:dispatch` | Rules for dispatching subagents: boundaries, reuse, model tiering, self-contained prompts, collecting replies |
| `/edify:markdown` | Fix structural defects in agent-written markdown with `bin/edify-markdown` |
| `/edify:token-counting` | Count file tokens with `bin/edify-count-tokens` |
| `/edify:ground` | Ground a methodology in external research before asserting it |

## Agents

| Agent | Role |
|-------|------|
| `brainstorm-name` | Generates and scores candidate names in a clean context |

## Scripts

In `bin/`, standard library only:

- `edify-markdown` reads markdown paths on stdin and rewrites each file in
  place, fixing keyword lists lacking bullets, inline triple backticks, spaced
  backtick spans and similar defects. Fenced code and YAML prologs are left
  alone.
- `edify-count-tokens [--model haiku|sonnet|opus|ID] [--json] FILE...` counts
  input tokens with the Anthropic `count_tokens` endpoint. The key comes from
  `ANTHROPIC_API_KEY` or `[anthropic] api_key` in `~/.config/edify/config.toml`.

[claude-code]: https://docs.claude.com/en/docs/claude-code/overview
