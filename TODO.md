## Remaining

- Verify the background commit security review's unchecked finding: a hook in
  `.claude/settings.json` executing a workspace-writable script (sandbox
  escape). Read the `hooks` entries and check whether each script path is
  writable from the sandbox.
- `memory/MEMORY.md` is over the loader budget (116% of 25600 bytes), so tail
  entries may not load — run `/gitlore:index-audit`.
- Memory facts name the removed package and old layout (`src/edify`,
  `edify-cli`, `plugin/portable.just`, `scripts/dogfood.sh`, `.bin/claude`,
  `check_line_limits`, `bin/last-output`): `memory/MEMORY.md`,
  `distribution-published.md`, `macos-gate-target.md`, `style-edit-briefs.md`,
  `strategic-pivot.md`, `python-standards.md`, `worktree-submodule-setup.md`,
  and in the `ddaanet` tier `MEMORY.md`, `cc-plugin-dir-edits-sensitive.md`,
  `cc-project-dir-encoding.md`. Update or retire each through the memory gate.
- `memory/ddaanet/cc-plugin-dir-edits-sensitive.md` still names "a `just claude`
  recipe" as a `--plugin-dir` launcher; the recipe is gone — the launcher is the
  vendored toolkit's dogfood shim loading `dist/plugin/`, promoted by
  `just dogfood`.
- Drop a brief in `../claude-plugins/inbox/` rewriting that README's edify
  section (it still advertises the removed pipeline, `/proof`, `edify-cli` and
  the uv venv hook) for the six skills, `brainstorm-name` and the two scripts,
  with no uv or venv (another repo — brief only).
- The markdown fixer mangles valid markdown: `~~~` fences, fences inside
  blockquotes, inline code spans wrapped across lines (xfailed in
  `tests/test_markdown_fixtures.py`), `+` bullets, and repeated-prefix lines
  such as `$ cmd` or headings without a blank line between them. Fix in
  `lib/edify_markdown/` with regression fixtures.
