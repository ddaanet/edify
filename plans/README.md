# Plans Directory

This directory contains implementation plans, design documents, and execution artifacts for project work.

## Directory Structure

```
plans/
├── markdown/              # Markdown processing reference
├── oneshot-workflow/      # Oneshot workflow design (reference)
├── prompt-composer/       # Prompt composer framework (ACTIVE)
└── unification/           # Agent-core unification project (ACTIVE)
```

---

## Active Projects

### unification/ - Agent-Core Unification

**Status:** ACTIVE - Phase 4 ready to execute
**Branch:** unification
**Start Date:** 2025-12
**Current Phase:** 3 complete, 4 ready

**Purpose:** Unify rules and patterns across repositories via plugin submodule.

**Progress:**
- ✅ Phase 1: Foundation and basic unification (10 steps, completed)
- ✅ Phase 2: Formalization (3 steps, completed)
- ✅ Phase 3: Design for compose-api (5 steps, completed)
- ⏳ Phase 4: Implementation of composition module and CLI (ready)
- ⏳ Phase 5+: To be planned

**Key Deliverables:**
- Main design: `unification/design.md`
- Phase documents: `unification/phases/phase*.md`
- **Phase 3 output:** `unification/consolidation/design/compose-api.md` (34K, ready for implementation)
- Execution reports: `unification/reports/phase*-*.md`

**Next Steps:** Execute Phase 4 implementation (core module, CLI, YAML validation)

**Owner:** Sonnet orchestrator

---

### prompt-composer/ - Prompt Composer Framework

**Status:** ACTIVE - Foundation ready, blocked by unification completion
**Branch:** TBD (awaiting unification merge)
**Start Date:** 2025-12

**Purpose:** Composable agent role architecture with semantic sources, tier markers, and variant generation.

**Progress:**
- ✅ Design complete: `prompt-composer/design.md`
- ✅ 14 semantic sources extracted
- ✅ Token counter command implemented
- ⏳ Phase 1 implementation plan ready: `prompt-composer/plan-phase1.md`
- ⏳ Blocked: Awaiting unification project completion

**Key Documents:**
- **Index:** `prompt-composer/README.md` (comprehensive guide)
- **Design:** `prompt-composer/design.md` (master specification)
- **Design review:** `prompt-composer/opus-review-tiering.md`
- **Phase 1 plan:** `prompt-composer/plan-phase1.md` (ready for execution)

**Dependencies:**
- Requires unification project completion
- plugin submodule must be stable

**Owner:** Sonnet orchestrator

---

## Reference Materials

### oneshot-workflow/ - Workflow Design Reference

**Status:** Design complete, formalized in agents/workflow.md
**Purpose:** Document oneshot workflow pattern for ad-hoc tasks.

**Key Documents:**
- **Design:** `oneshot-workflow/design.md` (complete workflow specification)
- **Phase 1 reports:** `oneshot-workflow/reports/phase1-*.md` (4 steps executed)

**Formalized in:**
- `agents/workflow.md` - Complete oneshot workflow guide
- `CLAUDE.md` - Workflow selection and entry points
- Skills: `/oneshot`, `/design`, `/plan-adhoc`, `/orchestrate`, `/vet`

**Status Note:** Design is complete and implemented. Directory preserved as reference for workflow evolution.

---

### markdown/ - Markdown Processing Reference

**Status:** Reference material
**Purpose:** Test corpus for markdown formatter evaluation.

**Contents:**
- `markdown/test-corpus.md` - Comprehensive markdown edge cases (150+ lines, 12 test sections)

**Use Cases:**
- Markdown formatter testing
- Edge case validation
- Regression testing for markdown processing

**Decision:** Formatter comparison completed (remark-cli selected). Decision recorded in `agents/decisions/`.

---

## Archived Plans

The following plans have been completed and removed from this directory:

- **test-refactor/** - Test file refactoring (committed cb3824f, merged)
- **markdown/archive/** - Historical markdown bug analysis
- **plan-token-check-command.md** - Token counter implementation (complete)
- **plan-orchestration-update.md** - Orchestration patterns (formalized in agents/workflow.md)
- **agent-context-v2.md** - Agent context architecture migration (completed)
- **formatter-comparison.md** - Markdown formatter evaluation (decision in agents/decisions/)
- **tidy-brewing-adleman.md** - Incomplete cost optimization analysis
- **markdown-fence-aware-processing.md** - Historical problem definition
- **plan-claude-wrapper.md** - Superseded sketch

**Rationale:** Completed plans archived to reduce clutter. Key decisions and patterns extracted to:
- `agents/decisions/` - Architectural decisions
- `agents/workflow.md` - Workflow patterns
- Git history - Full context preservation

---

## Plan Lifecycle

### 1. Creation
- Start with `/oneshot` skill (auto-detects workflow)
- OR create design doc manually in `plans/<project-name>/`

### 2. Active Development
- Update design documents as work progresses
- Generate execution artifacts via `prepare-runbook.py`:
  - `.claude/agents/<name>-task.md` (plan-specific agent)
  - `plans/<name>/steps/step-*.md` (individual steps)
  - `plans/<name>/orchestrator-plan.md` (orchestrator instructions)
- Track progress in `agents/session.md`

### 3. Execution
- Use `/orchestrate` skill for runbook execution
- Write reports to `plans/<name>/reports/`
- Update session.md with progress

### 4. Completion
- Extract valuable decisions to `agents/decisions/`
- Delete plan-specific agent (`.claude/agents/*-task.md`)
- Archive or delete plan directory (per project convention)

### 5. Archival
- Remove completed plan directories
- Git history preserves full context
- Key learnings in permanent agent documentation

---

## Conventions

### Directory Naming
- `kebab-case` for plan directories
- Descriptive names (project focus, not generic)

### File Structure
```
plans/<project-name>/
├── design.md              # Main design document
├── runbook.md             # Implementation steps (if using orchestrate)
├── orchestrator-plan.md   # Generated by prepare-runbook.py
├── phases/                # Phase documents (for complex projects)
│   ├── phase1.md
│   └── phase2.md
├── steps/                 # Generated step files
│   ├── step-1.md
│   └── step-2.md
└── reports/               # Execution reports
    ├── step-1.md
    └── step-2.md
```

### Report Files
- **Location:** `plans/<project-name>/reports/`
- **Naming:**
  - Phase reviews: `phase*-plan-review.md`
  - Step execution: `phase*-step*-execution.md`
  - Step reviews: `phase*-step*-review.md`
- **Purpose:** Track execution progress, decisions, issues

### Metadata (Runbook Frontmatter)
```yaml
---
name: project-name
model: sonnet  # default model for steps
---
```

---

## Related Documentation

- **CLAUDE.md** - Agent instructions, workflow selection
- **agents/workflow.md** - Complete oneshot workflow guide
- **agents/decisions/** - Architectural decisions
- **agents/session.md** - Current session handoff context
- **plugin/bin/prepare-runbook.py** - Runbook artifact generator

---

## Maintenance

### When to Archive
- Plan execution complete
- All valuable decisions extracted to agents/
- No pending tasks in session.md

### What to Preserve
- Architectural decisions → `agents/decisions/`
- Workflow patterns → `agents/workflow.md`
- Test data → Keep in place or move to `tests/fixtures/`
- Everything else → Git history

### Regular Cleanup
- After each major project completion
- When plans/ exceeds 50 files
- Before starting new major work

---

**Last Updated:** 2026-01-23
**Maintainer:** Sonnet orchestrator
