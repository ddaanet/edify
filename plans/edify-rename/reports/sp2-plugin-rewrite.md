# SP-2 Plugin Runtime References Rewrite

**Scope:** Submodule runtime references to `claudeutils` → `edify` (deferred from SP-1)

## Files Updated

1. **plugin/bin/compress-key.py** — 1 occurrence
   - `from claudeutils.when.compress` → `from edify.when.compress`

2. **plugin/bin/when-resolve.py** — 1 occurrence
   - `from claudeutils.when.cli` → `from edify.when.cli`

3. **plugin/bin/prepare-runbook.py** — 2 occurrences
   - subprocess call: `["claudeutils", "_recall",` → `["edify", "_recall",`
   - error message: `"claudeutils not found"` → `"edify not found"`

4. **plugin/hooks/userpromptsubmit-shortcuts.py** — 2 occurrences
   - help text: `claudeutils _recall resolve` → `edify _recall resolve`
   - import: `from claudeutils.planstate.inference` → `from edify.planstate.inference`

5. **plugin/hooks/pretooluse-recipe-redirect.py** — 4 occurrences
   - Three error messages: `claudeutils _worktree` → `edify _worktree` (both suggest text and code)
   - One error message: `claudeutils _worktree merge` → `edify _worktree merge`

6. **plugin/hooks/sessionstart-health.sh** — 2 occurrences
   - pip install: `"claudeutils==$EDIFY_VERSION"` → `"edify==$EDIFY_VERSION"` (2x, uv and pip branches)

7. **plugin/portable.just** — 10 occurrences
   - precommit recipe: 5x `claudeutils validate` → `edify validate` (memory-index, learnings, tasks, planstate, session-structure)
   - precommit-base recipe: 5x `claudeutils validate` → `edify validate` (same 5)

## Total: 22 occurrences across 7 files, all replaced.

**Status:** Complete. No submodule commits created (caller handles submodule commit).
