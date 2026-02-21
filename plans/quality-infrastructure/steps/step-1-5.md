# Step 1.5

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: opus
**Phase**: 1

---

## Step 1.5: Update references across codebase

**Objective**: Update all files outside agent-core/agents/ that reference old agent/skill/fragment names. Apply terminology propagation.

**Execution Model**: Opus

**Prerequisite**: Read terminology table from Common Context. Agent internal references were handled in Step 1.2. This step covers everything else.

**Implementation**:

Apply terminology table substitutions across these categories. For each file: read, apply all applicable substitutions, write.

**1. Skills (7+ files):**
- agent-core/skills/commit/SKILL.md — vet-requirement → review-requirement
- agent-core/skills/runbook/SKILL.md — quiet-task→artisan, tdd-task→test-driver, vet-fix-agent→corrector, plan-reviewer→runbook-corrector, runbook-simplification-agent→runbook-simplifier, quiet-explore→scout, test-hooks→hooks-tester, outline-review-agent→outline-corrector, runbook-outline-review-agent→runbook-outline-corrector
- agent-core/skills/design/SKILL.md — design-vet-agent→design-corrector
- agent-core/skills/deliverable-review/SKILL.md — vet-fix-agent→corrector
- agent-core/skills/orchestrate/SKILL.md — vet-fix-agent→corrector, quiet-task→artisan, tdd-task→test-driver, plan-reviewer→runbook-corrector, runbook-simplification-agent→runbook-simplifier, quiet-explore→scout
- agent-core/skills/doc-writing/SKILL.md — vet references → review
- agent-core/skills/plugin-dev-validation/SKILL.md — vet references → review
- agent-core/skills/review-plan/SKILL.md — plan-reviewer→runbook-corrector (if referenced)
- agent-core/skills/memory-index/SKILL.md — vet references → review

**2. Decision files (6 files):**
- agents/decisions/pipeline-contracts.md — vet-fix-agent→corrector, plan-reviewer→runbook-corrector, vet-requirement→review-requirement
- agents/decisions/operational-practices.md — vet delegation→review delegation
- agents/decisions/workflow-optimization.md — quiet-task→artisan, vet references→review
- agents/decisions/workflow-advanced.md — vet delegation references
- agents/decisions/project-config.md — agent configuration names
- agents/decisions/orchestration-execution.md — vet-fix-agent→corrector, vet-requirement→review-requirement

**3. Docs (2 files):**
- agent-core/docs/tdd-workflow.md — vet references→review
- agent-core/docs/general-workflow.md — remove vet-agent recommendation (deprecated per D-1), vet-fix-agent→corrector, plan-reviewer→runbook-corrector

**4. Other agent-core (2 files):**
- agent-core/README.md — agent inventory: update all renamed agent names, remove vet-agent, remove vet-taxonomy
- agent-core/bin/focus-session.py — vet reference→review

**5. Memory index:**
- agents/memory-index.md — update /when triggers referencing old names

**6. Session files:**
- agents/session.md — update task descriptions referencing old names
- agents/learnings.md — update vet references in learnings entries

**7. Rules:**
- .claude/rules/plugin-dev-validation.md — vet reference→review

**8. CLAUDE.md:**
- No changes needed for FR-3 — vet-requirement.md is NOT in CLAUDE.md @-references
- deslop.md removal happens in Phase 2e (not this step)

**9. Terminology propagation in ALL files touched above:**
- "vet report" → "review report"
- "vet-fix report" → "correction"
- "vetting" → "review/correction"
- "vet delegation" → "review delegation"

**Scope note**: Files in plans/ are historical records — do NOT update references in plans/ reports, requirements, or outlines. Only update production files (agent-core/, agents/, .claude/, CLAUDE.md).

**Expected Outcome**: All production files updated. No stale references to old names outside plans/.

**Error Conditions**:
- Old name in unexpected context → Distinguish: reference to agent/skill (update) vs descriptive historical prose (leave)
- File modified by concurrent worktree → STOP, report conflict

**Validation**: `grep -rl "vet-fix-agent\|design-vet-agent\|outline-review-agent\|runbook-outline-review-agent\|plan-reviewer\|review-tdd-process\|quiet-task\|quiet-explore\|tdd-task\|runbook-simplification-agent\|test-hooks\|vet-agent\|vet-taxonomy\|vet-requirement" --include="*.md" --include="*.py" agent-core/ agents/decisions/ agents/memory-index.md agents/session.md agents/learnings.md .claude/rules/ CLAUDE.md` returns zero files.

---
