# Phase 8: Skill Wrappers

**Type:** General
**Model:** haiku
**Dependencies:** Phase 5 (bin script must exist)
**Files:**
- `agent-core/skills/when/SKILL.md`
- `agent-core/skills/how/SKILL.md`

**Design reference:** Skill Wrappers section
**Skill guidance:** plugin-dev:skill-development (loaded in session)

---

## Step 8.1: Create `/when` skill SKILL.md

**Objective:** Create the `/when` skill wrapper that invokes the resolver.

**Implementation:**
- Create `agent-core/skills/when/SKILL.md` with YAML frontmatter:
  - `name: when`
  - `description:` Third-person format with specific trigger phrases per skill-development guidance. Include: "This skill should be used when the agent needs to recall behavioral knowledge", "when facing a decision", "when encountering a pattern seen before", "retrieve decision content". Include operator prefix examples.
  - `allowed-tools: Bash(agent-core/bin/when-resolve.py:*)`
  - `user-invocable: true`
- Body: Invocation instructions using `agent-core/bin/when-resolve.py when <trigger>`
- Include three resolution modes (trigger, .section, ..file) with examples
- Keep lean (~200-300 words) per skill-development guidance

**Expected Outcome:** Skill file exists, frontmatter validates, triggers match usage patterns.

**Error Conditions:**
- Missing frontmatter fields → skill won't load
- Vague description → poor triggering

**Validation:** Verify SKILL.md has valid YAML frontmatter with name and description fields.

---

## Step 8.2: Create `/how` skill SKILL.md

**Objective:** Create the `/how` skill wrapper, parallel to `/when`.

**Implementation:**
- Create `agent-core/skills/how/SKILL.md` with YAML frontmatter:
  - `name: how`
  - `description:` "This skill should be used when the agent needs to recall procedural knowledge", "how to do something", "technique for", "step-by-step procedure". Distinct trigger phrases from `/when`.
  - `allowed-tools: Bash(agent-core/bin/when-resolve.py:*)`
  - `user-invocable: true`
- Body: Same invocation pattern but with `how` operator: `agent-core/bin/when-resolve.py how <trigger>`
- Same three resolution modes documented

**Expected Outcome:** Skill file exists, triggers distinct from `/when` skill.

**Error Conditions:** Same as Step 8.1.

**Validation:** Verify SKILL.md has valid YAML frontmatter. Verify description trigger phrases don't overlap with `/when`.

---

## Step 8.3: Sync skills to .claude directory

**Objective:** Make skills discoverable by running `just sync-to-parent`.

**Implementation:**
- Run `just sync-to-parent` in `agent-core/` directory (requires `dangerouslyDisableSandbox: true`)
- Verify symlinks created in `.claude/skills/when/` and `.claude/skills/how/`

**Expected Outcome:** Skills appear in `.claude/skills/` directory as symlinks to `agent-core/skills/`.

**Error Conditions:**
- Sandbox restriction → use dangerouslyDisableSandbox
- Recipe failure → fix obstruction, retry recipe (per project-tooling rule)

**Validation:** `ls -la .claude/skills/when/SKILL.md` and `.claude/skills/how/SKILL.md` show symlinks

---

## Step 8.4: Test skill triggering

**Objective:** Verify `/when` and `/how` skills are discoverable and invoke correctly (requires restart after Step 8.3).

**Implementation:**
- Restart Claude Code session (skills load on startup)
- Test `/when` skill invocation with a known trigger
- Test `/how` skill invocation with a known trigger
- Verify both resolve correctly via `agent-core/bin/when-resolve.py`

**Expected Outcome:** Skills appear in skill list, invoke resolver script, return formatted output.

**Error Conditions:**
- Skill not discoverable → check symlinks exist, verify SKILL.md frontmatter
- Resolver error → check bin script permissions, verify claudeutils package installed

**Validation:** Manual verification - `/when` and `/how` commands work as expected
