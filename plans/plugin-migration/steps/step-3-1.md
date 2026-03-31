# Step 3.1

**Plan**: `plans/plugin-migration/runbook-phase-3.md`
**Execution Model**: opus
**Phase**: 3

---

## Phase Context

Create `/edify:init` and `/edify:update` skills — agentic prose artifacts requiring opus.

---

---

## Step 3.1: Create /edify:init skill and CLAUDE.md template

**Objective**: Create the `/edify:init` skill that helps new consumer projects set up edify framework, plus the CLAUDE.md template it references.

**Script Evaluation**: Prose (agentic skill definition)
**Execution Model**: Opus (architectural artifact — agentic prose determining downstream agent behavior)

**Prerequisites**:
- Read outline.md Component 4 "Migration Command" section (behavioral specification)
- Read 2-3 existing skills for format reference: `plugin/skills/commit/SKILL.md`, `plugin/skills/handoff/SKILL.md`
- Read `plugin/fragments/` directory listing (know what fragments exist for distribution)
- Read current CLAUDE.md (understand `@`-reference structure for template design)

**Implementation**:
1. Create `plugin/skills/init/SKILL.md`:
   - **Concrete actions, not open-ended conversation.** The outline specifies the operations: copy fragments, rewrite refs, scaffold structure, write `.edify.yaml`. The skill must execute these, not ask the user to decide them.
   - Skill behavior (per outline FR-3 and Component 4):
     - Copy fragments from `plugin/fragments/` to `agents/rules/`
     - CLAUDE.md handling (conditional):
     - If CLAUDE.md exists in project root: rewrite `@plugin/fragments/` refs to `@agents/rules/`
     - If CLAUDE.md does not exist: generate from `plugin/templates/CLAUDE.template.md`
     - Scaffold `agents/` structure: `session.md`, `learnings.md`, `jobs.md`
     - Write `.edify.yaml` with current plugin version and sync policy (`nag` default)
   - Reference points the skill needs to be aware of:
     - Fragment inventory (`plugin/fragments/*.md`)
     - `agents/` directory structure conventions
     - CLAUDE.md template at `plugin/templates/CLAUDE.template.md`
     - `.edify.yaml` format (version, sync_policy)
   - Idempotent: check before acting, never destroy existing content
   - No submodule detection — the edify project itself does not run `/edify:init`
   - Consumer mode only — marketplace install context
   - Frontmatter: `name: init`, appropriate description for triggering

2. Update `plugin/templates/CLAUDE.template.md` (file exists — needs ref rewrites):
   - Currently uses `@plugin/fragments/` paths — must be updated to `@agents/rules/` references (local copies for consumer projects)
   - Includes standard sections: workflows, communication rules, operational rules
   - Placeholders for project-specific content
   - Must be a starting point, not a complete CLAUDE.md — consumer fills in project-specific details

**Expected Outcome**:
- `plugin/skills/init/SKILL.md` exists with valid skill frontmatter and concrete action-oriented behavior (CLAUDE.md conditional, fragment copy, scaffold, `.edify.yaml` write)
- `plugin/templates/CLAUDE.template.md` exists with template structure
- Skill references template path correctly

**Error Conditions**:
- If `plugin/skills/init/` directory doesn't exist → create it
- If template references fragments that don't exist → verify fragment inventory

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer for skill quality review
3. Verify skill appears in plugin discovery: `claude --plugin-dir ./plugin` → `/help` lists `/edify:init`

---
