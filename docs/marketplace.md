# Marketplace

Plugin distribution via Claude Code marketplace system. Reference: https://code.claude.com/docs/en/plugin-marketplaces

## Ecosystem

| Repo | Role | Location |
|------|------|----------|
| `ddaanet/claude-plugins` | Marketplace manifest | `/Users/david/code/claude-plugins` |
| `ddaanet/skills` | `ddaa` plugin — bilingual skills | `/Users/david/code/skills` |
| `ddaanet/edify` | `edify` plugin (in `plugin/`) + the `edify-cli` package | `/Users/david/code/edify` |

Marketplace name `ddaanet` — install commands: `/plugin install ddaa@ddaanet`, `/plugin install edify@ddaanet`

`ddaanet/edify-plugin` was archived on 2026-07-16: the plugin lives in this
repo's `plugin/` subdirectory and is sourced via `git-subdir` (see
`docs/design.md` §5.1 "One tree, two products"). The marketplace entry is not yet
added — it waits on the first `edify-cli` PyPI publish, since the plugin's
SessionStart hook installs `edify-cli==<plugin version>` from the index.

## Distribution model

- `claude-plugins` is metadata-only — `.claude-plugin/marketplace.json` pointing to external repos, no runtime code
- `README.md` and `marketplace.json` must stay in sync
- Third-party marketplaces do not auto-update by default — users run `/plugin marketplace update`
- Version detection uses `plugin.json` version field. Same version string = update skipped. Must bump version for users to see updates.
- Pinning available via `ref` (branch/tag) and `sha` (exact commit) — currently unused, tracking default branch head
- `strict: true` (default) means plugin's own `plugin.json` is authoritative; marketplace entries supplement
- Users can opt in to per-marketplace auto-update via `/plugin` settings
- Reserved marketplace names exist (cannot use `anthropic-marketplace`, `claude-code-plugins`, etc.)
