# Step 2.3

**Plan**: `plans/plugin-migration/runbook-phase-2.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Migrate all hooks to plugin, create consolidated setup hook, audit scripts for env var usage.
Phase 5 must complete first (`.edify.yaml` exists for setup hook to read/update).

**Step numbering note:** Step 2.2 (originally "Apply hook script fixes from audit") was absorbed into Step 2.1 during /proof. Step 2.4 (originally "Wire setup hook into hooks.json") was absorbed into Step 2.3 during /proof. The gaps in step numbering are intentional — outline requirements traceability uses original step IDs.

---

---

## Step 2.3: Integrate setup into sessionstart-health.sh (checkpoint)

**Objective**: Update `sessionstart-health.sh` to include setup responsibilities — env var export, CLI install, version write, and staleness nag. Replaces the originally-planned separate `edify-setup.sh`. All setup failures reported via `systemMessage`, not as crashes.

**Script Evaluation**: Moderate (additions to existing script)
**Execution Model**: Sonnet

**Prerequisites**:
- Read `agent-core/hooks/sessionstart-health.sh` (current state — understand existing structure)
- Read outline.md Component 2 "Consolidated setup hook" section
- Read outline.md §Key Decisions D-7 (python deps mechanism)
- Step 5.1 complete (`.edify.yaml` exists)
- Recall: "when using session start hooks" — SessionStart output discarded for new interactive sessions (#10373). UPS fallback already handled by existing session flag (`$TMPDIR/health-${session_id}`).

**Implementation**:
1. Edit `agent-core/hooks/sessionstart-health.sh`, inserting setup sections before existing health checks:
   a. **Export `EDIFY_PLUGIN_ROOT`** via `$CLAUDE_ENV_FILE`:
      ```bash
      if [ -n "${CLAUDE_ENV_FILE:-}" ] && [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
          echo "EDIFY_PLUGIN_ROOT=$CLAUDE_PLUGIN_ROOT" >> "$CLAUDE_ENV_FILE"
      fi
      ```
   b. **Install edify CLI** into plugin-local venv (failure → append warning to message):
      - Check for `uv` availability: `command -v uv`
      - If available: create plugin-local venv (`uv venv "$CLAUDE_PLUGIN_ROOT/.venv"` if not present), install (`uv pip install --python "$CLAUDE_PLUGIN_ROOT/.venv/bin/python" claudeutils==X.Y.Z`)
      - If not: fall back to `pip install --target "$CLAUDE_PLUGIN_ROOT/.venv/lib"` or append `⚠️ CLI install failed: uv not found` to message
      - Package name is `claudeutils` (current PyPI name; rename to `edify` is separate work)
      - Version pinned in script, updated with each plugin release
   c. **Write version provenance** to `.edify.yaml` (FR-10):
      - Read plugin version from `$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json`
      - Update `version` field in `.edify.yaml`
      - On failure: append `⚠️ Version write failed` to message
   d. **Compare versions and nag if stale** (FR-5):
      - Compare `.edify.yaml` `version` with plugin version
      - If mismatch: append `⚠️ Fragments may be stale. Run /edify:update` to message
2. UPS fallback: existing session flag (`touch "$TMPDIR/health-${session_id}"`) already provides idempotency — no additional marker needed
3. Guard all setup operations: `if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then ... fi` — skip silently if not in plugin context
4. All setup failures are non-fatal — append to `message` variable, script continues to health checks and outputs `systemMessage`

**Expected Outcome**:
- `sessionstart-health.sh` includes setup sections before health checks
- Setup failures reported in `systemMessage` output alongside health status
- No separate `edify-setup.sh` file created
- After run: `.edify.yaml` version matches `plugin.json` version

**Error Conditions**:
- If `$CLAUDE_ENV_FILE` is not set → skip env var export silently
- If `$CLAUDE_PLUGIN_ROOT` is not set → skip all setup operations silently
- If `uv` and `pip` both unavailable → append warning to message, continue
- If `.edify.yaml` doesn't exist → create it (first run scenario)

**Validation**:
- Script runs without error from project root: `bash agent-core/hooks/sessionstart-health.sh`
- After run: `.edify.yaml` version matches `plugin.json` version
- Script is idempotent: running twice produces same result
- **STOP and report Phase 2 results to orchestrator before proceeding to Phase 3**
