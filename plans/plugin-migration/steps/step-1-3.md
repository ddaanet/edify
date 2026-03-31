# Step 1.3

**Plan**: `plans/plugin-migration/runbook-phase-1.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Create the plugin structure inside existing `plugin/` directory. Checkpoint at end gates all downstream phases.

---

---

## Step 1.3: Validate plugin loading (checkpoint)

**Objective**: Verify plugin auto-discovery works with `claude --plugin-dir ./plugin`. Gates all downstream phases.

**Prerequisites**:
- Steps 1.1, 1.2 complete

**Implementation**:

**Automated checks (agent executes directly via `claude -p` headless mode):**

1. **FR-1 Skills**: Verify plugin skills discoverable from a clean directory (no `.claude/`):
   ```bash
   mkdir -p tmp/plugin-verify && cd tmp/plugin-verify && \
     claude -p "list your available slash commands" --plugin-dir ../../plugin 2>&1 | tee ../../tmp/plugin-verify-skills.txt && \
     cd ../..
   ```
   - Output must contain plugin skills (`/design`, `/commit`, `/orchestrate`, `/handoff`)
   - If skills missing → check `plugin.json` format, directory structure
2. **FR-1 Agents**: Verify plugin agents discoverable:
   ```bash
   cd tmp/plugin-verify && \
     claude -p "list your available agents" --plugin-dir ../../plugin 2>&1 | tee ../../tmp/plugin-verify-agents.txt && \
     cd ../..
   ```
   - Output must list agents from `plugin/agents/`
3. **FR-8 Coexistence**: Verify plan-specific agents coexist with plugin agents:
   ```bash
   claude -p "list your available agents" --plugin-dir ./plugin 2>&1 | tee tmp/plugin-verify-coexist.txt
   ```
   - Run from project root (has `.claude/agents/handoff-cli-tool-*.md`)
   - Output must contain both plugin agents AND plan-specific agents — no conflicts
4. **FR-1 Hooks**: Verify hooks fire from plugin:
   ```bash
   cd tmp/plugin-verify && \
     claude -p "write the word test to /tmp/hook-test.txt" --plugin-dir ../../plugin 2>&1 | tee ../../tmp/plugin-verify-hooks.txt && \
     cd ../..
   ```
   - `pretooluse-block-tmp.sh` should block the `/tmp` write — look for hook output in response

**Manual check (STOP — human performs):**

5. **NFR-1 Dev mode reload**: Edit one skill file (add a comment), then re-run check 1. Confirm the edit is reflected (skill content changed). This validates the edit-restart cycle is no slower than symlinks.

**Expected Outcome**:
- Plugin skills, agents, and hooks all discoverable via `--plugin-dir`
- No conflicts between plugin agents and plan-specific agents
- Dev mode reload works: edit-restart-verify cycle confirms change visible on next start

**Error Conditions**:
- If plugin not discovered → check `plugin.json` format, directory structure
- If hooks not loading → check wrapper format matches Claude Code expectations
- If agent conflicts → check namespace prefixing

**Validation**:
- Checks 1-4 must pass (automated, agent verifies output)
- Check 5: STOP and report NFR-1 result to orchestrator
- All downstream phases depend on this checkpoint passing
