# Step 4.8

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Stdin parsing, session.md writes, committed detection, state caching, diagnostics. Precommit is a pre-handoff gate (skill responsibility), not an internal CLI step.

---

---

## Step 4.8: Update handoff skill — add pre-handoff precommit gate

**Objective:** Add `just precommit` as a gate in the handoff skill (`agent-core/skills/handoff/SKILL.md`). The handoff CLI no longer runs precommit (removed from pipeline); the skill must run it before STATUS display. Without this update, precommit validation drops out of the handoff flow entirely.

**Script Evaluation:** Small (~10 lines skill edit)

**Execution Model:** Opus (agentic prose — skill file, wording determines downstream agent behavior)

**Actions:**
1. Read `agent-core/skills/handoff/SKILL.md`
2. Add a precommit gate step after all writes (session.md, learnings, plan-archive, trim) and before Step 7 (Display STATUS):
   - Run `just precommit`
   - On failure: output precommit result, stop (agent fixes issues and retries)
   - On success: continue to STATUS display
3. Verify the step integrates coherently with the existing protocol flow — precommit validates all writes made during handoff (session.md, learnings.md, plan-archive.md)

**Changes:**
- File: `agent-core/skills/handoff/SKILL.md`
  Action: Add precommit gate step between current Step 6 (Trim Completed Tasks) and Step 7 (Display STATUS)

**Expected Outcome:** Handoff skill runs `just precommit` after all writes and before STATUS display. Failed precommit surfaces output and stops the flow so agent can fix issues. Passing precommit proceeds to STATUS display unchanged.

**Validation:** Read modified skill, verify precommit gate is positioned after all writes and before STATUS display.

---

**Phase 4 Checkpoint:** `just precommit` — handoff subcommand and skill precommit gate complete.
