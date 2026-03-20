# Step 1.1

**Plan**: `plans/plugin-migration/runbook-phase-1.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Create the plugin structure inside existing `agent-core/` directory. Checkpoint at end gates all downstream phases.

---

---

## Step 1.1: Create plugin manifest

**Objective**: Create `agent-core/.claude-plugin/plugin.json` with plugin name and version matching `pyproject.toml`.

**Prerequisites**:
- Read `pyproject.toml` (extract current version — currently `0.0.2`)

**Implementation**:
1. Create directory `agent-core/.claude-plugin/`
2. Create `agent-core/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "edify",
     "version": "0.0.2",
     "description": "Opinionated agent framework for Claude Code"
   }
   ```
3. Version must match `pyproject.toml` `version` field exactly

**Expected Outcome**:
- `agent-core/.claude-plugin/plugin.json` exists with valid JSON
- `name` is `edify`, `version` matches `pyproject.toml`

**Error Conditions**:
- If `.claude-plugin/` directory already exists → check contents, do not overwrite without verifying
- If `pyproject.toml` version format is unexpected → escalate

**Validation**:
- `cat agent-core/.claude-plugin/plugin.json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['name']=='edify'; print('OK:', d['version'])"`

---
