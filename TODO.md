## Remaining

- Verify the background commit security review's unchecked finding: a hook in
  `.claude/settings.json` executing a workspace-writable script (sandbox
  escape). Read the `hooks` entries and check whether each script path is
  writable from the sandbox.
- Settle the two "unverified on macOS" comments in
  `scripts/check_line_limits.sh` and `tests/line_limits_helpers.py` against the
  passing macOS `just precommit` run, then verify or delete them.
- `.dprint.json` is orphaned: the gate formats markdown with rumdl. Delete the
  config.
- `memory/MEMORY.md` is over the loader budget (116% of 25600 bytes), so tail
  entries may not load — run `/gitlore:index-audit`.
- **justfile consolidation**: move `plugin/portable.just` into the root
  `justfile`, then clean up or split to meet the line limit; remove
  `plugin/justfile`. Sweep inbound references: the root `justfile`'s
  `portable.just` comments, `tests/test_line_limits_default_invocation.py`,
  `memory/worktree-submodule-setup.md`.
- `memory/ddaanet/cc-plugin-dir-edits-sensitive.md` still names "a `just claude`
  recipe" as a `--plugin-dir` launcher; the recipe is gone — the launcher is
  `.bin/claude` loading `dist/plugin/`, promoted by `just dogfood`.
