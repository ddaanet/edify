## Current task

The plugin's SessionStart uv-venv bootstrap is implemented and unit-tested (uv
stubbed on PATH) but not yet verified end-to-end against a real edify-cli wheel,
nor wired into distribution.

## Open decisions

- How to verify the bootstrap end-to-end: build a local edify-cli wheel and run
  the hook on a uv host with `UV_FIND_LINKS` pointed at it (offline dogfood),
  versus deferring until the first real PyPI publish.
- Distribution remainder: publish edify-cli to PyPI and add the marketplace
  `git-subdir` entry pointing at `plugin/` — publish ordering requires the
  package to reach the index before the plugin version that pins it.
