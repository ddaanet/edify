# Step 3.2

**Plan**: `plans/plugin-migration/runbook-phase-3.md`
**Execution Model**: opus
**Phase**: 3

---

## Phase Context

Create `/edify:init` and `/edify:update` skills — agentic prose artifacts requiring opus.

---

---

## Step 3.2: Create /edify:update skill

**Objective**: Create the `/edify:update` skill that syncs fragments and portable justfile when plugin version changes.

**Script Evaluation**: Prose (agentic skill definition)
**Execution Model**: Opus (architectural artifact — agentic prose)

**⚠️ Design dependency:** The outline does not specify a conflict policy for fragment updates. Before implementing, the outline must define: (a) conflict definition (consumer file content differs from plugin's version), (b) update policy (warn-and-skip, never silent overwrite), (c) `--force` mechanism for intentional overwrite. Do not implement conflict detection without this policy.

**Prerequisites**:
- Read outline.md Component 4 `/edify:update` section (verify conflict policy has been added)
- Read `agent-core/skills/init/SKILL.md` (created in Step 3.1 — understand separation of concerns)
- Read 1-2 existing skills for format reference

**Implementation**:
1. Create `agent-core/skills/update/SKILL.md`:
   - Behavior: sync fragments + portable justfile module(s), update `.edify.yaml` version
   - Separate from init — update is sync-only, not scaffolding
   - Should handle:
     - Compare current fragments in `agents/rules/` with plugin's fragments at `agent-core/fragments/`
     - Copy updated fragments, preserving any local customizations (warn on conflicts)
     - Sync portable justfile module(s) to project
     - Update `.edify.yaml` version to match current plugin version
   - Idempotent: safe to run when already up-to-date
   - Frontmatter: `name: update`, appropriate description

**Expected Outcome**:
- `agent-core/skills/update/SKILL.md` exists with valid skill frontmatter
- Skill clearly separated from `/edify:init` (sync vs scaffold)
- Handles conflict detection for modified fragments

**Error Conditions**:
- If fragments directory doesn't exist in consumer project → suggest running `/edify:init` first

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer for skill quality review
3. Verify skill appears in plugin discovery
