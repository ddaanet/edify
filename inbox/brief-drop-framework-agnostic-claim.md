## Brief: drop the "framework-agnostic" claim from the plugin's descriptions

2026-09-20

Found while rewriting the `ddaanet/claude-plugins` marketplace README from
each plugin's own README. The user challenged "framework-agnostic" in the
edify section ("vraiment ?"), and the plugin's own content does not back it.
The marketplace README has been reworded; the claim's sources are here.

### Decisions

- **Remove "framework-agnostic" as the plugin's headline descriptor.** What
  the plugin actually assumes:
  - `/formalize` is Python-only — icontract contracts checked with CrossHair
    through `edify check`.
  - `/recall` reads `memory/MEMORY.md` and the memory files it indexes, i.e.
    the gitlore memory layout.
  - Per `plugin/README.md`, `/commit` and `/handoff` defer to the
    `commit-commands` and `handoff` plugins, and the session task frame is
    `.claude/handoff-task.md`.
  - The SessionStart bootstrap (`plugin/bin/bootstrap-venv.sh`) requires `uv`
    and a Python >= 3.14 environment for `edify-cli`.
- **Describe the plugin by what it is.** The marketplace README now says:
  "skills and agents built around a requirements → design → runbook →
  execution planning pipeline. Recall reads the project's `memory/MEMORY.md`,
  and the session task frame is the `handoff` plugin's." `/formalize` is
  listed there as "Python only: icontract contracts checked with CrossHair".

### Known occurrences

- `plugin/.claude-plugin/plugin.json` `description`: "A lean bundle of
  framework-agnostic Claude Code skills".
- `plugin/README.md` line 3: "bundle of framework-agnostic skills and
  agents".
- `README.md` line 5 ("ships a handful of framework-agnostic skills") and
  line 37 ("ships framework-agnostic skills invoked as slash commands").

### Constraints

- A `plugin.json` description change only reaches users after a **version
  bump** (currently 0.2.0): same version = update skipped.
- The marketplace (`../claude-plugins/.claude-plugin/marketplace.json`)
  copies the description and still says "framework-agnostic". It was left
  alone so it would not diverge from `plugin.json` here. After releasing,
  update the description and version there.
- If "framework-agnostic" was meant in a narrower sense — no dependency on a
  particular test runner, web framework or agent framework such as
  superpowers — say that precisely instead. As a bare adjective it reads as
  "no assumptions about your project", which the list above contradicts.

### Additional context

- The marketplace README documents the **published** pipeline
  (`origin/main`, 0.2.0): `/requirements` → `/design` → `/runbook` →
  `/orchestrate`, or `/inline` without a runbook. The local tree, ahead of
  `origin/main`, has replaced `/orchestrate` and `/inline` with `/build`.
  When that ships, the edify section of `../claude-plugins/README.md` needs
  the same update.
- The marketplace README states that `edify-cli` is provisioned
  transparently by the SessionStart hook and that `uv` on `PATH` is the only
  prerequisite. That was read from the local `plugin/hooks/hooks.json`; it
  was not checked against the published 0.2.0.
