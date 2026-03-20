# Step 5.1

**Plan**: `plans/plugin-migration/runbook-phase-5.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Phase Context

Wire version consistency and release coordination. Runs early — creates `.edify.yaml` before Phase 2's setup hook needs it.

---

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
