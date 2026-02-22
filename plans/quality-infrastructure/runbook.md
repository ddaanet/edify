---
name: quality-infrastructure
model: sonnet
---

# Quality Infrastructure Reform

**Context**: Rename 11 agent files, embed taxonomy, delete deprecated agents, propagate name changes across ~43 files, restructure deslop content, add code density decisions.
**Design**: plans/quality-infrastructure/outline.md
**Requirements**: plans/quality-infrastructure/requirements.md
**Status**: Ready
**Created**: 2026-02-22

---

## Weak Orchestrator Metadata

**Total Steps**: 7

**Execution Model**:
- Steps 1.1, 1.3, 1.7: Haiku (mechanical file operations)
- Steps 1.2, 1.4: Sonnet (content insertion, substitution)
- Steps 1.5, 1.6: Opus (architectural artifact prose)

**Step Dependencies**: Sequential (1.1 -> 1.2 -> 1.3 -> 1.4 -> 1.5 -> 1.6 -> 1.7 -> checkpoint -> Phase 2 inline -> Phase 3 inline -> final checkpoint)

**Error Escalation**:
- Haiku -> Sonnet: git operation fails, unexpected file state
- Sonnet -> User: substitution ambiguity, content conflict
- Opus -> User: architectural wording decisions

**Report Locations**: plans/quality-infrastructure/reports/

**Success Criteria**: Zero grep hits for all old names from substitution table in production files. `just precommit` passes. `just sync-to-parent` succeeds. Deslop.md deleted. 5 code density entries in cli.md. 5 /when triggers in memory-index.md.

**Prerequisites**:
- All 11 agent source files exist in agent-core/agents/ (verified Phase 0.5)
- All referenced skill, fragment, decision files exist (verified Phase 0.5)
- Git tree clean before each step

---

## Common Context

**Requirements:**
- FR-1: Deslop restructuring — prose rules to communication.md (ambient), code rules stay in project-conventions skill
- FR-2: Code density decisions — 5 grounded principles to cli.md + memory-index triggers
- FR-3: Agent rename — 11 renames + 1 embed + 1 deprecation deletion + 8 plan-specific deletions + cross-codebase propagation

**Scope boundaries:**
- IN: All items above, symlink regeneration, cross-reference verification
- OUT: Context optimization (demotion), project-conventions restructuring beyond code deslop, new agent definitions, codebase sweep (FR-4), prepare-runbook.py crew- prefix changes

**Key Decisions:**
- D-1: vet-agent deprecated, delete (zero call sites)
- D-2: vet-taxonomy embedded in corrector (63 lines)
- D-3: Code deslop via project-conventions skill (add to artisan + test-driver)
- D-4: Prose deslop merged into communication.md (5 rules, strip examples)
- D-5: Phase ordering FR-3 then FR-1 then FR-2
- D-6: vet-requirement.md renamed to review-requirement.md
- D-7: /vet skill renamed to /review skill (directory rename)

**Substitution Table — Agent Names:**

| Old | New |
|-----|-----|
| vet-fix-agent | corrector |
| design-vet-agent | design-corrector |
| outline-review-agent | outline-corrector |
| runbook-outline-review-agent | runbook-outline-corrector |
| plan-reviewer | runbook-corrector |
| review-tdd-process | tdd-auditor |
| quiet-task | artisan |
| quiet-explore | scout |
| tdd-task | test-driver |
| runbook-simplification-agent | runbook-simplifier |
| test-hooks | hooks-tester |

**Substitution Table — Terminology:**

| Old | New |
|-----|-----|
| vet report | review report |
| vet-fix report | correction |
| vetting | review/correction |
| vet-requirement | review-requirement |
| /vet | /review |
| vet/ (skill directory) | review/ |

**Deprecated — delete references:**

| Old | Action |
|-----|--------|
| vet-agent | Delete file + references (zero call sites per D-1) |
| vet-taxonomy | Delete file after embed in corrector (D-2) |

**Project Paths:**
- Agent definitions: agent-core/agents/
- Skills: agent-core/skills/
- Fragments: agent-core/fragments/
- Decisions: agents/decisions/
- Symlinks: .claude/agents/, .claude/skills/

---

### Phase 1: Agent Rename (type: general)

**Checkpoint:** full

## Step 1.1: Batch rename agent definition files

**Objective**: Rename 11 agent files via git mv to new names per substitution table.
**Script Evaluation**: Direct
**Execution Model**: Haiku

**Implementation**:
Git mv 11 files in agent-core/agents/:
- vet-fix-agent.md to corrector.md
- design-vet-agent.md to design-corrector.md
- outline-review-agent.md to outline-corrector.md
- runbook-outline-review-agent.md to runbook-outline-corrector.md
- plan-reviewer.md to runbook-corrector.md
- review-tdd-process.md to tdd-auditor.md
- quiet-task.md to artisan.md
- quiet-explore.md to scout.md
- tdd-task.md to test-driver.md
- runbook-simplification-agent.md to runbook-simplifier.md
- test-hooks.md to hooks-tester.md

Requires `dangerouslyDisableSandbox: true` (git mv writes .git tracking).
Commit all renames atomically.

**Expected Outcome**: All 11 files at new paths. Old paths removed. Single commit.
**Error Conditions**: git mv fails -> STOP, report file state
**Validation**: `ls agent-core/agents/corrector.md artisan.md scout.md test-driver.md` succeeds; `git status` clean after commit

---

## Step 1.2: Embed vet-taxonomy and delete deprecated agents

**Objective**: Embed vet-taxonomy.md content into corrector.md, delete vet-taxonomy.md and vet-agent.md.
**Script Evaluation**: Small
**Execution Model**: Sonnet
**Depends on**: Step 1.1

**Implementation**:
- Read agent-core/agents/vet-taxonomy.md (62 lines: status table, subcategory codes, investigation format, deferred items template)
- Read agent-core/agents/corrector.md
- Insert full taxonomy content into corrector.md after the role description section, before any existing status taxonomy reference. Preserve all tables and examples.
- Delete agent-core/agents/vet-taxonomy.md
- Delete agent-core/agents/vet-agent.md (deprecated per D-1: zero active call sites)
- Commit changes

**Expected Outcome**: corrector.md contains embedded taxonomy. vet-taxonomy.md and vet-agent.md deleted.
**Error Conditions**: Insertion point ambiguous -> STOP, describe section boundaries found
**Validation**: grep for taxonomy table headers in corrector.md succeeds; verify deleted files absent

---

## Step 1.3: Delete plan-specific agent detritus

**Objective**: Delete 8 standalone agent files from .claude/agents/ left over from past plan executions.
**Script Evaluation**: Direct
**Execution Model**: Haiku

**Implementation**:
Delete 8 files in .claude/agents/:
- error-handling-task.md
- pushback-task.md
- runbook-quality-gates-task.md
- when-recall-task.md
- workflow-rca-fixes-task.md
- worktree-merge-data-loss-task.md
- worktree-merge-resilience-task.md
- workwoods-task.md

Do NOT delete: hb-p*.md, quality-infrastructure-task.md, runbook-generation-fixes-task.md (active plans).

**Expected Outcome**: 8 files deleted. Active plan agents untouched.
**Error Conditions**: File not found -> warn and continue (may already be deleted)
**Validation**: `ls .claude/agents/*-task.md` shows only active plan agents

---

## Step 1.4: Update renamed agent internals

**Objective**: Update YAML frontmatter and cross-references in all 11 renamed agents.
**Script Evaluation**: Small
**Execution Model**: Sonnet
**Depends on**: Step 1.1

**Implementation**:
- Update `name:` YAML frontmatter in all 11 renamed agents to match new filename (without .md)
- Update cross-references between agents per substitution table:
  - tdd-auditor.md: vet-fix-agent to corrector
  - runbook-corrector.md: vet-fix-agent to corrector
  - runbook-outline-corrector.md: vet-fix-agent to corrector
  - outline-corrector.md: vet-fix-agent to corrector
- Update `skills:` frontmatter lists if any reference old agent names
- Grep each renamed file for any remaining old names from substitution table
- Commit changes

**Expected Outcome**: All 11 agents have correct `name:` frontmatter and internal cross-references.
**Error Conditions**: Old names found in grep -> fix before committing
**Validation**: grep all 11 files for all old names from substitution table -> zero hits

---

## Step 1.5: Rename skill directory and fragment file

**Objective**: Rename vet/ to review/ skill directory and vet-requirement.md to review-requirement.md fragment, update content.
**Script Evaluation**: Small
**Execution Model**: Opus
**Depends on**: Step 1.1

**Implementation**:
- git mv agent-core/skills/vet/ agent-core/skills/review/
- git mv agent-core/fragments/vet-requirement.md agent-core/fragments/review-requirement.md
- Update review/SKILL.md: all vet to review terminology, agent name references per substitution table. Update trigger phrase, description, all internal references.
- Update review-requirement.md: agent name references per substitution table (vet-fix-agent to corrector, design-vet-agent to design-corrector, etc.), vet to review terminology
- Requires `dangerouslyDisableSandbox: true`
- Commit changes

**Expected Outcome**: Skill directory at review/, fragment at review-requirement.md. Content updated with new terminology.
**Error Conditions**: git mv fails -> STOP, report. Content ambiguity -> STOP, describe alternatives.
**Validation**: `ls agent-core/skills/review/SKILL.md` succeeds; grep both files for old names -> zero hits

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

## Step 1.7: Symlink sync, stale removal, and verification

**Objective**: Clean up dangling symlinks, regenerate correct ones, verify no stragglers across entire codebase.
**Script Evaluation**: Direct
**Execution Model**: Haiku
**Depends on**: Steps 1.1-1.6

**Implementation**:
- Find and remove dangling symlinks in .claude/agents/ and .claude/skills/ (old-name targets gone after git mv)
- Run `just sync-to-parent` to regenerate correct symlinks
- Grep entire codebase for ALL old names: vet-fix-agent, quiet-task, tdd-task, plan-reviewer, design-vet-agent, outline-review-agent, runbook-outline-review-agent, review-tdd-process, quiet-explore, runbook-simplification-agent, test-hooks, vet-agent, vet-taxonomy, vet-requirement, /vet
- Fix any stragglers found
- Commit if changes made

**Expected Outcome**: All symlinks valid. Zero grep hits for old names across codebase.
**Error Conditions**: `just sync-to-parent` fails -> STOP, report. Stragglers found -> fix if mechanical, STOP if ambiguous.
**Validation**: `just precommit` passes; grep for old names -> zero hits; no dangling symlinks

---

### Phase 2: Deslop Restructuring (type: inline)

- Merge 5 prose deslop rules into agent-core/fragments/communication.md as new subsection after existing rules. Rules only, strip examples. Discard principle line.
- Update agent-core/skills/project-conventions/SKILL.md: remove "Prose" subsection under Deslop section (now ambient). Add missing code rule: "Expose fields directly until access control needed." Restructure heading to "Code Quality."
- Add `skills: ["project-conventions"]` to YAML frontmatter of agent-core/agents/artisan.md and agent-core/agents/test-driver.md.
- Remove "Code Quality" section (8 bullets) from agent-core/agents/artisan.md — redundant with project-conventions skill injection.
- Remove `@agent-core/fragments/deslop.md` line from CLAUDE.md. Delete agent-core/fragments/deslop.md. Update remaining "deslop" references:
  - agent-core/README.md — update inventory description
  - agent-core/skills/memory-index/SKILL.md — update if references deslop fragment
  - agents/memory-index.md — update deslop-related /when triggers
  - agents/decisions/operational-practices.md — update term to "code quality"/"prose quality"
  - agents/session.md — update task descriptions

---

### Phase 3: Code Density Decisions (type: inline)

- Add 5 entries to agents/decisions/cli.md. Each states general principle first, project instance second. Source content from plans/reports/code-density-grounding.md:
  1. Expected state checks return booleans — normal states checked with boolean returns, not exceptions. Project: `_git_ok(*args) -> bool`
  2. Consolidate display and exit — error termination as single call. Project: `_fail(msg, code=1) -> Never`
  3. Formatter expansion signals abstraction need — 5+ lines after formatting = extract helper. Project: default kwargs pattern
  4. Exceptions for exceptional events only — custom exception classes, not ValueError. Project: lint satisfaction via proper design
  5. Error handling layers don't overlap — context at failure site, display at top level. Project: never both
- Add 5 /when triggers to agents/memory-index.md under `## agents/decisions/cli.md` section.
