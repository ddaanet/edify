### Phase 5: Version coordination and precommit (type: general, model: sonnet)

Wire version consistency and release coordination. Runs early — creates `.edify.yaml` before Phase 2's setup hook needs it.

---

## Step 5.1: Create .edify.yaml schema and initial file

**Objective**: Create `.edify.yaml` in project root with version from `pyproject.toml` and default sync policy.

**Prerequisite**: Read `pyproject.toml:1-5` — confirm current version string (e.g. `0.0.2`)

**Implementation**:
1. Create `.edify.yaml` in project root:
   ```yaml
   # Edify plugin version marker
   # Written by /edify:init, updated by sessionstart-health.sh on session start
   version: "0.0.2"
   sync_policy: nag  # nag | auto-with-report (future)
   ```
2. Version must match `pyproject.toml` version exactly
3. `sync_policy: nag` is the default — setup hook compares versions and nags if stale

**Expected Outcome**:
- `.edify.yaml` exists in project root with valid YAML
- `version` field matches `pyproject.toml`
- `sync_policy` is `nag`

**Error Conditions**:
- If `.edify.yaml` already exists → read and verify, do not overwrite without checking

**Validation**:
- `python3 -c "import yaml, tomllib; d=yaml.safe_load(open('.edify.yaml')); v=tomllib.load(open('pyproject.toml','rb'))['project']['version']; assert d['version']==v, f'version mismatch: {d[\"version\"]} != {v}'; assert d['sync_policy']=='nag'; print('OK')"`

---

## Step 5.2: Add version consistency precommit check

**Objective**: Add a check that `plugin.json` version == `pyproject.toml` version, integrated into `just precommit` and `just release`.

**Prerequisites**:
- **Prerequisite**: Read `justfile:386-513` — understand the existing `release` recipe: it uses `uv version --bump "$BUMP"` (not explicit version arg), commits `pyproject.toml uv.lock` together, tags, and publishes. The `plugin.json` bump must be inserted after `uv version --bump "$BUMP"` (line ~478) and before `git add pyproject.toml uv.lock` (line ~480).
- **Prerequisite**: Read `justfile:18-30` — understand current `precommit` recipe: calls `run-checks` then `run-pytest` then `run-line-limits`. Insert version check after `run-checks` call.
- **Prerequisite**: Read `agent-core/.claude-plugin/plugin.json` — confirm `version` field name and JSON structure (created in Step 1.1)

**Implementation**:
1. Create version consistency check script at `agent-core/bin/check-version-consistency.py`:
   - Read `pyproject.toml` version
   - Read `agent-core/.claude-plugin/plugin.json` version
   - Compare — exit 0 if match, exit 1 with message if mismatch
2. Add to `just precommit` recipe (after lint, before test):
   - `python3 agent-core/bin/check-version-consistency.py`
3. Update the existing `just release` recipe to bump `plugin.json` alongside `pyproject.toml`:
   - After `visible uv version --bump "$BUMP"` (which bumps `pyproject.toml`), insert: `python3 -c "import json, sys; p='agent-core/.claude-plugin/plugin.json'; d=json.load(open(p)); d['version']='$(uv version)'; json.dump(d,open(p,'w'),indent=2)"`
   - Extend the existing `git add pyproject.toml uv.lock` line to: `git add pyproject.toml uv.lock agent-core/.claude-plugin/plugin.json`
   - Run consistency check after: `python3 agent-core/bin/check-version-consistency.py`
   - No changes to the recipe's flags, argument handling, or publish logic

**Expected Outcome**:
- `agent-core/bin/check-version-consistency.py` exists (invoked as `python3 agent-core/bin/check-version-consistency.py`, not as a direct executable)
- `just precommit` includes version consistency check
- Mismatched versions cause precommit failure

**Error Conditions**:
- If `plugin.json` path changes → update script and release recipe accordingly

**Validation**:
1. Run `just precommit` — should pass (versions match)
2. Temporarily change `plugin.json` version → `just precommit` should fail
3. Restore `plugin.json` version
