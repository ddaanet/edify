# Deliverable Review: quality-infrastructure

**Date:** 2026-02-23
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

**Scope:** Changes since merge-base `22434a5b` (main), excluding plan artifacts, session artifacts, `.claude/agents/` symlinks, `.claude/skills/` symlinks.

### Agent-core submodule (43 files, -971/+674 net)

| Type | File | Lines |
|------|------|-------|
| Agent def | agents/corrector.md (new, was vet-fix-agent) | 513 |
| Agent def | agents/artisan.md (was quiet-task) | 119 |
| Agent def | agents/test-driver.md (was tdd-task) | ~120 |
| Agent def | agents/design-corrector.md (was design-vet-agent) | ~90 |
| Agent def | agents/tdd-auditor.md (was review-tdd-process) | ~80 |
| Agent def | agents/runbook-corrector.md (was plan-reviewer) | ~60 |
| Agent def | agents/scout.md (was quiet-explore) | ~40 |
| Agent def | agents/outline-corrector.md | ~40 |
| Agent def | agents/runbook-outline-corrector.md | ~40 |
| Agent def | agents/runbook-simplifier.md | ~40 |
| Agent def | agents/hooks-tester.md | ~30 |
| Agent def (deleted) | agents/vet-agent.md | -371 |
| Agent def (deleted) | agents/vet-taxonomy.md | -62 |
| Fragment | fragments/communication.md | +8 |
| Fragment (deleted) | fragments/deslop.md | -49 |
| Fragment (renamed) | fragments/review-requirement.md (was vet-requirement) | 172 |
| Fragment | fragments/error-classification.md | 2 chg |
| Fragment | fragments/execution-routing.md | 1 chg |
| Skill (renamed) | skills/review/SKILL.md (was vet/) | 384 |
| Skill | skills/project-conventions/SKILL.md | 13 chg |
| Skill | skills/design/SKILL.md | 30 chg |
| Skill | skills/orchestrate/SKILL.md | 26 chg |
| Skill | skills/runbook/SKILL.md | 26 chg |
| Skill | skills/plugin-dev-validation/SKILL.md | 38 chg |
| Skill | skills/doc-writing/SKILL.md | 4 chg |
| Skill | skills/commit/SKILL.md | 2 chg |
| Skill | skills/deliverable-review/SKILL.md | 2 chg |
| Skill | skills/review-plan/SKILL.md | 10 chg |
| Skill refs | skills/runbook/references/*.md | 16 chg |
| Skill | skills/memory-index/SKILL.md | 0 chg (stale) |
| Script | bin/prepare-runbook.py | 557 chg |
| Script | bin/focus-session.py | 76 chg |
| Docs | docs/general-workflow.md, tdd-workflow.md, shortcuts.md | 69 chg |
| Docs | README.md | 33 chg |

### Parent repo (18 files, -101/+152 net)

| Type | File | Lines |
|------|------|-------|
| Human docs | agents/decisions/cli.md | +32 |
| Human docs | agents/decisions/pipeline-contracts.md | 36 chg |
| Human docs | agents/decisions/workflow-optimization.md | 38 chg |
| Human docs | agents/decisions/workflow-core.md | 16 chg |
| Human docs | agents/decisions/workflow-planning.md | 16 chg |
| Human docs | agents/decisions/orchestration-execution.md | 14 chg |
| Human docs | agents/decisions/implementation-notes.md | 6 chg |
| Human docs | agents/decisions/operational-practices.md | 6 chg |
| Human docs | agents/decisions/defense-in-depth.md | 2 chg |
| Human docs | agents/decisions/deliverable-review.md | 2 chg |
| Human docs | agents/decisions/project-config.md | 2 chg |
| Human docs | agents/decisions/prompt-structure-research.md | 2 chg |
| Agentic prose | agents/memory-index.md | +17 chg |
| Human docs | agents/learnings.md | 38 chg |
| Human docs | agents/plan-archive.md | 14 chg |
| Config | CLAUDE.md | -2 |
| Config | README.md | 2 chg |
| Config | .claude/rules/plugin-dev-validation.md | 8 chg |

### Deleted plan-specific detritus (8 files)

error-handling-task, pushback-task, runbook-quality-gates-task, when-recall-task, workflow-rca-fixes-task, worktree-merge-data-loss-task, worktree-merge-resilience-task, workwoods-task — all confirmed deleted from `.claude/agents/`.

## Critical Findings

### C1. Test regression: test_prepare_runbook_inline.py fixture uses old agent names

**File:** `tests/test_prepare_runbook_inline.py:304-308`
**Design requirement:** FR-3 rename propagation across codebase
**Impact:** Two tests fail (`test_no_step_files_generated`, `test_orchestrator_plan_all_inline`). `_setup_baseline_agents()` creates `quiet-task.md` and `tdd-task.md` but `prepare-runbook.py` now reads `artisan.md` and `test-driver.md` (lines 593-595). `SystemExit: 1` on missing baseline agent.

**Verified:** `just test tests/test_prepare_runbook_inline.py` produces 2 failures.

## Major Findings

### M1. Corrector agent retains "Vet" in description, H1, and report template

**File:** `agent-core/agents/corrector.md:3,10,291`
**Axis:** Naming convention uniformity (cross-cutting)
**Impact:** Agent's own `description:` frontmatter says "Vet review agent", H1 says "# Vet Review + Fix Agent", report template header says "# Vet Review:". These are the primary identity strings — agents presenting themselves use old terminology.

### M2. Design-corrector H1 retains "Design Vet Agent"

**File:** `agent-core/agents/design-corrector.md:11`
**Axis:** Naming convention uniformity
**Impact:** H1 heading says "# Design Vet Agent" instead of "# Design Corrector".

### M3. Skill-embedded memory-index has 5 stale "vet" triggers

**File:** `agent-core/skills/memory-index/SKILL.md:114,166-168,278`
**Axis:** Path consistency across documents
**Impact:** Parent `agents/memory-index.md` was updated (e.g., "vet escalation calibration" → "review escalation calibration") but the skill-embedded copy was not touched. 5 triggers still use "vet" terminology where the parent uses "review"/"corrector".

Stale triggers:
- `/when requiring per-artifact vet coverage`
- `/when vet escalation calibration`
- `/when vet flags out-of-scope items`
- `/when vet receives execution context`
- `/when vet catches structural issues`

### M4. Incomplete terminology propagation in agent-core skills (13+ references)

**Files and counts:**
- `skills/doc-writing/SKILL.md` — 4 refs: description (line 3), intro (line 10), step flow (line 117), delegation context (line 123). "vet review" and "vet delegation" should be "review" or "correction".
- `skills/design/SKILL.md` — 2 refs: step C.2 objective (line 382), C.2 why (line 386). "vet review" and "vet review cycle" in step headers.
- `skills/runbook/SKILL.md` — 4 refs: line 150 "vet review", line 483 "vet checkpoint steps", line 791 "Vet" in checkpoint pattern, line 795 "Vet:" checkpoint step.
- `skills/orchestrate/SKILL.md` — 1 ref: line 176, report path `checkpoint-N-vet.md`.
- `skills/plugin-dev-validation/SKILL.md` — 2 refs: line 167 `name: vet`, line 515 "vet checkpoint steps".

**Axis:** Naming convention uniformity
**Impact:** Agent name references (vet-fix-agent→corrector) were propagated but generic "vet" terminology in skill step descriptions, section headers, and report naming conventions was not.

### M5. Parent memory-index.md has 4 partially-propagated "vet" triggers

**File:** `agents/memory-index.md`
**Impact:** Some triggers were renamed (e.g., "vet-fix-agent rejects" → "corrector rejects") but 4 others still use "vet":
- `/when requiring per-artifact vet coverage`
- `/when vet flags unused code`
- `/when routing artifact review | ... vet-fix orchestrator`
- `/when scoping vet for cross-cutting invariants`

## Minor Findings

### Style/clarity

- `agent-core/fragments/execution-routing.md:19` — "vet, design review" should be "review, design review" or "correction, design review"
- `agent-core/skills/reflect/references/patterns.md:158` — "vet agent" should be "corrector"
- `agent-core/skills/prioritize/references/scoring-tables.md:17` — "vet delegation" should be "review delegation"
- `test_prepare_runbook_inline.py:83` — test fixture content says "Update plan-reviewer.md" (cosmetic — in a test runbook string, not a real reference)
- Decision files retain ~25 "vet" references in historical narrative (e.g., "Phase 5 opus vet audited"). Borderline — these describe past events using names that existed at the time, but inconsistent with updated terminology in the same files.

## Gap Analysis

| Design Requirement | Status | Reference |
|--------------------|--------|-----------|
| FR-1: Prose rules → communication.md | Covered | +8 lines, 5 rules |
| FR-1: Code rules stay in project-conventions | Covered | Section renamed, "Expose fields" added |
| FR-1: Deslop.md removed from CLAUDE.md | Covered | -2 lines in CLAUDE.md |
| FR-1: Deslop.md deleted | Covered | File gone |
| FR-1: project-conventions added to artisan + test-driver | Covered | `skills: ["project-conventions"]` in frontmatter |
| FR-1: Inline code quality removed from artisan | Covered | 8-bullet "Code Quality" section removed |
| FR-2: 5 code density entries in cli.md | Covered | 5 H3 entries under ".Code Density" section |
| FR-2: 5 /when triggers in memory-index | Covered | 5 triggers under cli.md section |
| FR-2: General principle first, project instance second | Covered | All 5 entries follow pattern |
| FR-3: 11 agent renames (git mv) | Covered | All 11 renamed |
| FR-3: vet-agent deleted (D-1) | Covered | File deleted |
| FR-3: vet-taxonomy embedded in corrector (D-2) | Covered | Status taxonomy section in corrector.md |
| FR-3: 8 plan-specific agent deletions | Covered | All 8 confirmed deleted |
| FR-3: vet/ → review/ skill rename | Covered | Symlink + content updated |
| FR-3: vet-requirement → review-requirement | Covered | Renamed, internal refs updated |
| FR-3: Agent name propagation (~37 files) | Partially covered | Agent name refs updated; generic "vet" terminology not (M1-M5) |
| FR-3: Symlink sync | Covered | No stale symlinks, all new names resolve |
| FR-3: Cross-reference verification | Failed for test | C1 test regression; M3-M5 terminology gaps |

## Summary

- **Critical:** 1 (test regression — 2 failing tests from stale fixture names)
- **Major:** 5 (agent self-identity "Vet" retention, skill-embedded memory-index drift, incomplete terminology propagation in skills + parent memory-index)
- **Minor:** 5 (scattered cosmetic "vet" references in fragments, skills, decision narratives)

The structural deliverables are complete — all renames, deletions, deslop restructuring, and code density entries landed correctly. The gap is in terminology propagation depth: agent name references (vet-fix-agent→corrector) were systematically updated, but generic "vet" terminology in step descriptions, section headers, report naming, and skill-embedded copies was not.
