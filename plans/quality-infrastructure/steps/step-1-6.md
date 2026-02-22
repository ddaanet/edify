# Step 1.6

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: opus
**Phase**: 1

---

## Step 1.6: Propagate name changes across codebase

**Objective**: Apply full substitution table across ~30 files — all agent name and terminology references.
**Script Evaluation**: Prose
**Execution Model**: Opus
**Depends on**: Steps 1.1, 1.2, 1.4, 1.5

**Implementation**:
For each file: Read, apply all applicable substitutions (agent names + terminology), Edit.

**Skills** (11 files):
- agent-core/skills/commit/SKILL.md — vet-requirement to review-requirement
- agent-core/skills/design/SKILL.md — design-vet-agent to design-corrector
- agent-core/skills/deliverable-review/SKILL.md — vet-fix-agent to corrector
- agent-core/skills/orchestrate/SKILL.md — vet terminology, agent names
- agent-core/skills/doc-writing/SKILL.md — vet references
- agent-core/skills/plugin-dev-validation/SKILL.md — vet references
- agent-core/skills/runbook/SKILL.md — runbook-outline-review-agent, plan-reviewer, runbook-simplification-agent, vet-fix-agent
- agent-core/skills/runbook/references/examples.md — vet delegation examples
- agent-core/skills/runbook/references/general-patterns.md — vet patterns
- agent-core/skills/remember/SKILL.md — /vet reference
- agent-core/skills/memory-index/SKILL.md — vet-fix-agent reference

**Decision files** (9 files):
- agents/decisions/pipeline-contracts.md — vet-fix-agent routing, reviewer table
- agents/decisions/operational-practices.md — vet delegation learnings
- agents/decisions/workflow-optimization.md — design-vet-agent, vet context reuse
- agents/decisions/project-config.md — agent composition references
- agents/decisions/orchestration-execution.md — vet delegation patterns
- agents/decisions/workflow-planning.md — vet-fix-agent, vet-agent, design-vet-agent references
- agents/decisions/workflow-core.md — /vet skill reference, vetting terminology
- agents/decisions/deliverable-review.md — vet-fix-agent routing reference
- agents/decisions/prompt-structure-research.md — vet-requirement reference

**Docs** (2 files):
- agent-core/docs/tdd-workflow.md
- agent-core/docs/general-workflow.md

**Other agent-core** (2 files):
- agent-core/README.md — agent inventory
- agent-core/bin/focus-session.py — agent references

**Project root** (5 files):
- CLAUDE.md — @vet-requirement to @review-requirement if present, any vet-fix-agent references
- agents/memory-index.md — vet-related /when triggers and agent name references
- agents/session.md — task descriptions referencing old names
- agents/learnings.md — vet-related learning descriptions
- .claude/rules/plugin-dev-validation.md — vet to review references

Commit all changes atomically.

**Scope note**: Files in plans/ are historical records — do NOT update. Only update production files.

**Expected Outcome**: All ~30 files updated. Zero old-name references remaining.
**Error Conditions**: Substitution ambiguity (old name in unrelated context) -> STOP, describe. File missing -> STOP, report.
**Validation**: grep all updated files for all old names -> zero hits

---
