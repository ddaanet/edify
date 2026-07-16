## Current task

The plugin-packaging design is fully specified but its runtime bootstrap is unbuilt — the SessionStart stdlib-venv hook, publishing `edify-cli` to PyPI, and the marketplace `git-subdir` entry all remain to implement.

## Open decisions

- Publish ordering: `edify-cli` must reach PyPI before the plugin version that pins it (the bootstrap installs `edify-cli==<version>`) — decide whether to publish first or develop the hook against a local index.
- Two empirical checks still gate design choices: whether `${CLAUDE_PLUGIN_DATA}` substitutes in skill content, and whether a write into `${CLAUDE_PLUGIN_ROOT}` persists across a session (the latter would permit the simpler ROOT venv location).
