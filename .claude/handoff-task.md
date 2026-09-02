## Current task

edify 0.2.0 shipped, and the reason its skills were invisible to every other repo is fixed: the marketplace entry used a `github` source, which resolves the repo root, while edify's manifest lives at `plugin/.claude-plugin/plugin.json`. The entry in `ddaanet/claude-plugins` is now `git-subdir` / `url: ddaanet/edify` / `path: plugin`, and `scripts/release.sh` derives that subdirectory from the manifest path — emitting the right source type when it creates an entry, and refusing the release when an existing entry has drifted off it.

The fix is not yet proven end to end. The install cache is keyed by version, so `edify@ddaanet` at 0.2.0 still holds the old wrong-shaped extraction until it is uninstalled and reinstalled, and plugin roots freeze at session start, so verification needs a fresh session in some other repo.
