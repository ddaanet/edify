### Phase 2: Hook migration and setup hook (type: general, model: sonnet)

Migrate all hooks to plugin, create consolidated setup hook, audit scripts for env var usage.
Phase 5 must complete first (`.edify.yaml` exists for setup hook to read/update).

**Step numbering note:** Step 2.2 (originally "Apply hook script fixes from audit") was absorbed into Step 2.1 during /proof. Step 2.4 (originally "Wire setup hook into hooks.json") was absorbed into Step 2.3 during /proof. The gaps in step numbering are intentional — outline requirements traceability uses original step IDs.

---

## Step 2.1: Audit hook scripts for env var usage

**Objective**: Audit 4 hook scripts for `$CLAUDE_PROJECT_DIR` usage and hardcoded paths that may not resolve correctly under plugin context.

**Prerequisites**:
- Read outline.md Component 2 hook script changes table (authoritative list of which scripts need audit)
- Read each of the 4 scripts:
  - `plugin/hooks/pretooluse-recipe-redirect.py`
  - `plugin/hooks/pretooluse-recall-check.py`
  - `plugin/hooks/sessionstart-health.sh`
  - `plugin/hooks/stop-health-fallback.sh`

**Implementation**:
1. For each script, check:
   - Uses of `$CLAUDE_PROJECT_DIR` — these are correct (available in all hook types, resolves to project root)
   - Hardcoded `plugin/` paths — these need `$CLAUDE_PLUGIN_ROOT` substitution (or `$EDIFY_PLUGIN_ROOT` after setup hook runs)
   - Relative path references — must use absolute paths via env vars
2. Record findings per script in a report at `plans/plugin-migration/reports/hook-audit.md`:
   - Script name
   - Finding: no-change-needed OR specific edits required (with line numbers)
   - Rationale
3. Apply fixes per audit findings:
   - Replace hardcoded `plugin/` paths with `$CLAUDE_PLUGIN_ROOT` or `$EDIFY_PLUGIN_ROOT`
   - Fix any relative path references to use absolute resolution
4. Delete `plugin/hooks/pretooluse-symlink-redirect.sh` — purpose eliminated by plugin migration
5. Verify no remaining bare references: `grep -r 'plugin/' plugin/hooks/*.py plugin/hooks/*.sh` returns no matches (except comments)

**Expected Outcome**:
- `plans/plugin-migration/reports/hook-audit.md` exists with per-script findings
- Each script classified as no-change or with specific edits listed
- Audit fixes applied to all scripts requiring changes
- `pretooluse-symlink-redirect.sh` deleted
- No remaining bare `plugin/` references in hook scripts

**Error Conditions**:
- If a script uses env vars not available in plugin context → escalate (design assumption violated)
- If a script has complex path resolution logic → document and escalate for careful review
- If audit found no changes needed → skip fix step, proceed to deletion
- If grep finds unexpected references → investigate and fix or escalate

**Validation**:
- Audit report exists with entries for all 4 scripts
- No scripts left unaudited
- `grep -r 'plugin/' plugin/hooks/*.py plugin/hooks/*.sh` returns no matches (except comments)
- `ls plugin/hooks/pretooluse-symlink-redirect.sh` returns "No such file"

---

## Step 2.3: Integrate setup into sessionstart-health.sh (checkpoint)

**Objective**: Update `sessionstart-health.sh` to include setup responsibilities — env var export, CLI install, version write, and staleness nag. Replaces the originally-planned separate `edify-setup.sh`. All setup failures reported via `systemMessage`, not as crashes.

**Script Evaluation**: Moderate (additions to existing script)
**Execution Model**: Sonnet

**Prerequisites**:
- Read `plugin/hooks/sessionstart-health.sh` (current state — understand existing structure)
- Read outline.md Component 2 "Consolidated setup hook" section
- Read outline.md §Key Decisions D-7 (python deps mechanism)
- Step 5.1 complete (`.edify.yaml` exists)
- Recall: "when using session start hooks" — SessionStart output discarded for new interactive sessions (#10373). UPS fallback already handled by existing session flag (`$TMPDIR/health-${session_id}`).

**Implementation**:
1. Edit `plugin/hooks/sessionstart-health.sh`, inserting setup sections before existing health checks:
   a. **Export `EDIFY_PLUGIN_ROOT`** via `$CLAUDE_ENV_FILE`:
      ```bash
      if [ -n "${CLAUDE_ENV_FILE:-}" ] && [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
          echo "EDIFY_PLUGIN_ROOT=$CLAUDE_PLUGIN_ROOT" >> "$CLAUDE_ENV_FILE"
      fi
      ```
   b. **Install edify CLI** into plugin-local venv (failure → append warning to message):
      - Check for `uv` availability: `command -v uv`
      - If available: create plugin-local venv (`uv venv "$CLAUDE_PLUGIN_ROOT/.venv"` if not present), install (`uv pip install --python "$CLAUDE_PLUGIN_ROOT/.venv/bin/python" edify==X.Y.Z`)
      - If not: fall back to `pip install --target "$CLAUDE_PLUGIN_ROOT/.venv/lib"` or append `⚠️ CLI install failed: uv not found` to message
      - Package name is `edify` (current PyPI name; rename to `edify` is separate work)
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
- Script runs without error from project root: `bash plugin/hooks/sessionstart-health.sh`
- After run: `.edify.yaml` version matches `plugin.json` version
- Script is idempotent: running twice produces same result
- **STOP and report Phase 2 results to orchestrator before proceeding to Phase 3**

