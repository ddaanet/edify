# General Workflow Guide

**Purpose:** Execute one-off, ad-hoc tasks that don't repeat.

## What is a "General Workflow" Task?

**General workflow tasks** are one-time operations that don't require ongoing maintenance:
- **Migrations** - Database migrations, data transformations, format conversions
- **Refactoring** - Code cleanup, architecture improvements, technical debt
- **Prototypes** - Experimental implementations, proof-of-concepts
- **Infrastructure** - One-time config changes, deployment updates, tooling setup
- **Fixes** - Legacy code updates, one-time bug fixes, cleanup tasks

**NOT general workflow** (use feature development workflow instead):
- **Repeatable features** - User-facing functionality with ongoing maintenance
- **Production features** - Require comprehensive tests and documentation
- **Business logic** - Features that will be used repeatedly and modified over time

**Key distinction:** If it needs ongoing maintenance, comprehensive tests, and user-facing documentation → **feature development**. If it's a one-time change → **general workflow**.

## Entry Point: `/design` Skill

The recommended way to start a task:
```
/design "migrate database from SQLite to PostgreSQL"
```

The `/design` skill will:
1. Verify this is a one-off task (not feature development)
2. Assess complexity (simple/moderate/complex)
3. Set up workflow stages in `.claude/handoff-task.md` as pending tasks
4. Begin executing the first stage

**User reads no docs** - the workflow guides itself through `.claude/handoff-task.md`.

---

## Terminology

| Term | Definition |
|------|------------|
| **Job** | What you want to accomplish (user goal) |
| **Design** | Architectural specification from Opus design session |
| **Phase** | Design-level segmentation for complex work |
| **Runbook** | Step-by-step implementation instructions |
| **Step** | Individual unit of work within a runbook |
| **Runbook prep** | 4-point process: Evaluate, Metadata, Review, Split |

---

## Workflow Overview

The general workflow has 6 stages:

```
Discussion → [Design] → Planning → Execution → Review → Completion
              optional
```

### Decision Flow

1. **Simple job** → Execute directly (no workflow needed)
2. **Moderate complexity** → Skip to Planning (Stage 3)
3. **Complex/uncertain** → Start with Design (Stage 2)

**Complexity heuristics:**
- **Moderate**: Clear requirements, straightforward implementation
- **Complex**: Architectural decisions needed OR unclear requirements

---

## Stage 1: Initial Discussion

**Model:** Sonnet (orchestrator)

**Purpose:** Define job scope and choose workflow path.

**Activities:**
- Discuss requirements with user
- Clarify scope and constraints
- Determine complexity level
- Route to appropriate next stage

**Decision tree:**
- Simple → Execute directly using CLAUDE.md patterns
- Moderate → Continue to Planning (Stage 3)
- Complex → Handoff to Design (Stage 2)

---

## Stage 2: Design Session (Optional)

**Model:** Opus
**Skill:** `/design`

**Purpose:** Resolve architectural ambiguity and capture complex requirements.

**When to use:**
- Architectural decisions required
- User uncertain about requirements
- Multiple valid approaches exist
- Complex technical constraints

**Activities:**
- Examine existing artifacts
- Explore codebase (delegated to specialized agents)
- Search web if needed
- Get user validation on design outline
- Create dense design document

**Design document contains:**
- Motivation and scope
- Key architectural choices with rationale
- Design decisions with trade-offs
- Implementation phases (if complex)
- **NO detailed steps** (sonnet does this in Planning)

**Output:** Compact design doc targeting sonnet (not user).

---

## Stage 3: Planning Session

**Model:** Sonnet
**Skill:** `/runbook`

**Purpose:** Create executable runbook from requirements or design.

**Inputs:**
- User requirements (from Discussion), OR
- Design document (from Design Session)

**Activities:**

### 1. Evaluate
Determine implementation approach:
- **≤25 lines**: Direct script execution (no agent needed)
- **25-100 lines**: Consider script vs prose delegation
- **>100 lines**: Separate planning required

### 2. Metadata
Add orchestrator coordination info:
- Default model per step (haiku/sonnet)
- Error handling rules
- Reporting locations
- Sequencing constraints

### 3. Review
Delegate to `edify:runbook-corrector` for validation:
- Completeness check
- Executability verification
- Context sufficiency
- LLM failure mode detection
- Apply review fixes

### 4. Split
Run `prepare-runbook.py` to create:
- Step files (`plans/<name>/steps/step-*.md`)
- Orchestrator plan (`plans/<name>/orchestrator-plan.md`)

**Special case:** If job is simple enough for single step, offer immediate execution.

**Output:** Prepared runbook ready for execution.

---

## Stage 4: Execution

**Model:** Sonnet (orchestrator)
**Skill:** `/orchestrate`

**Purpose:** Execute runbook steps reliably and efficiently.

**Inputs:**
- Orchestrator plan (from Planning)
- Step files (one per step)

**Orchestrator responsibilities:**
- Dispatch a standing agent per step, passing the step file path
- Track progress
- Handle errors per runbook rules:
  - **Simple error** → Delegate to sonnet for fix
  - **Complex error** → Abort, request opus plan update
- Write reports to specified locations

**Pattern: Quiet Execution**
- Agents write detailed output to files
- Orchestrator receives only:
  - Success: filename
  - Failure: error + diagnostic info
- Keeps orchestrator context lean

---

## Stage 5: Review

**Model:** Sonnet
**Agent:** corrector (all tiers)

**Purpose:** Review completed work before finalization.

**Scope:** Uncommitted changes, recent commits, or partial branch.

**Agent selection:**
- **After orchestration (Tier 3):** Use `corrector` — orchestrator has no context, agent applies critical/major fixes directly
- **After direct/lightweight work (Tier 1/2):** Use `corrector` — caller has context to evaluate and apply fixes from report

**Fix classification (after review report):**
- **Few/simple fixes** → Apply directly (Tier 1/2) or already applied (Tier 3)
- **UNFIXABLE issues** → Escalate to user or create fixes runbook
- **Complex fixes** → Create fixes runbook (back to Planning)

**Note:** review/correction agents are distinct from built-in `/review` (PR-focused).

---

## Stage 6: Completion

**Purpose:** Finalize work and update project documentation.

**Activities:**
- Update project documentation for changes
- Record architectural choices in `agents/decisions/`
- Move relevant decisions OUT of `plans/` to permanent docs
- Archive or delete plan directory per project convention

---

## Skills Reference

### `/design`
**Stage:** Entry point (any), and Stage 2 for complex jobs
**Model:** Opus (for complex) or Sonnet (delegates to Opus when needed)
**Use when:** Starting a new task; also the design session itself for complex jobs, uncertain requirements, or architectural decisions

**What it does:**
- Assesses complexity and routes by tier
- Auto-detects methodology (general vs TDD) from project context
- For complex jobs, runs the Opus design session with delegated exploration and produces a dense design document capturing fuzzy requirements and technical constraints

**Why use it:** Single command to start any workflow. Handles complexity triage automatically.

---

### `/runbook`
**Stage:** 3 (Planning)
**Model:** Sonnet
**Use when:** Ready to create implementation steps

**What it does:**
- Starts with tier assessment (evaluates complexity)
- **Tier 1** (Direct): Implements directly, vets, commits
- **Tier 2** (Lightweight): Delegates to artisan agents, reviews, commits
- **Tier 3** (Full Runbook): Executes 4-point runbook prep process, delegates review to `edify:runbook-corrector`, invokes `prepare-runbook.py` to create execution artifacts, primes `.claude/handoff-task.md` for orchestrator handoff

**Note:** Unified skill supporting both TDD and general workflows via per-phase typing.

---

### `/orchestrate`
**Stage:** 4 (Execution)
**Model:** Sonnet
**Use when:** Executing prepared runbooks only

**What it does:**
- Dispatches a standing agent per step, passing the step file path
- Handles error escalation
- Tracks progress
- Reports to specified locations

**Prerequisites:** Must have prepared runbook from `/runbook`.

---

### corrector
**Stage:** 5 (Review)
**Model:** Sonnet
**Use when:** Reviewing in-progress or completed changes

**What it does:**
- Analyzes changes following review protocol
- Writes detailed review to file with issues by priority
- Applies all fixes (critical, major, minor) directly via Edit tool
- Marks each issue FIXED or UNFIXABLE
- Returns filepath or error (quiet execution pattern)

**Distinction:** NOT for PRs (use built-in `/review` for that).

---

### `/claude-md-management:revise-claude-md`
**Stage:** Any
**Model:** Sonnet
**Use when:** Documenting workflow learnings or updating rules

**What it does:**
- Updates CLAUDE.md with new rules/constraints
- Updates `.claude/handoff-task.md` with pattern learnings
- Documents workflow improvements
- Adds constraints after discovering issues

**Principles:**
- Precision over brevity
- Examples over abstractions
- Constraints over guidelines
- Atomic changes

---

## Multi-Session Workflow

The general workflow is designed for natural multi-session execution with model switching.

### How It Works

1. **Start with `/design`** - Creates design document and assesses complexity
2. **Work continues** - Agent executes stages, updates `.claude/handoff-task.md`
3. **Session break** - Agent calls `/handoff:handoff`, advises on model switch if needed
4. **User starts new session** - Types `#load` or just describes next step
5. **Agent continues** - Reads `.claude/handoff-task.md`, resumes from pending tasks
6. **Repeat** - Until all workflow stages complete

### Example Multi-Session Flow

**Session 1 (Opus or Sonnet):**
```
User: /design "refactor auth system to support OAuth providers"
Agent: Assesses as complex task requiring design
Agent: Sets up workflow in `.claude/handoff-task.md`:
       - [ ] Design - Explore architecture (/design - Opus)
       - [ ] Planning - Create runbook (/runbook)
       - [ ] Execution - Run steps (/orchestrate - Sonnet)
       - [ ] Review - Check changes (corrector)
       - [ ] Completion - Finalize docs
Agent: "Design stage requires Opus. Switch to Opus model and type #load to continue."
```

**Session 2 (User switches to Opus):**
```
User: #load
Agent: Reads `.claude/handoff-task.md`, sees Design stage pending
Agent: Invokes /design skill
Agent: Explores codebase, makes architectural decisions
Agent: Completes design document
Agent: Updates `.claude/handoff-task.md` (Design complete, Planning next)
Agent: Calls /handoff:handoff: "Switch to Sonnet for Planning stage"
```

**Session 3 (User switches to Sonnet):**
```
User: #load
Agent: Reads `.claude/handoff-task.md`, sees Planning stage pending
Agent: Invokes /runbook
Agent: Creates runbook with implementation steps
Agent: Runs prepare-runbook.py to generate artifacts
Agent: Updates `.claude/handoff-task.md` (Planning complete, Execution next)
Agent: Calls /handoff:handoff: "Execution stage next"
```

**Session 4 (Execution):**
```
User: #load
Agent: Reads `.claude/handoff-task.md`, sees Execution stage pending
Agent: Invokes /orchestrate
Agent: Executes runbook steps
Agent: Updates `.claude/handoff-task.md` (Execution complete, Review next)
Agent: Calls /handoff:handoff: "Switch to Sonnet for Review stage"
```

**Session 5 (User switches to Sonnet):**
```
User: #load
Agent: Reads `.claude/handoff-task.md`, sees Review and Completion pending
Agent: Delegates to corrector to review changes
Agent: Makes any fixes needed based on review report
Agent: Updates documentation
Agent: Updates `.claude/handoff-task.md` (all tasks complete)
Agent: Calls /handoff:handoff: "All workflow tasks complete. Start fresh session for new work."
```

### Key Benefits

- **Zero context overhead** - Each session starts fresh, reads state from `.claude/handoff-task.md`
- **Right model for right task** - Design uses Opus, orchestration and review use Sonnet, individual steps may use Haiku
- **Natural breaks** - Work can pause/resume at any stage
- **Transparent state** - User sees workflow in `.claude/handoff-task.md` at any time
- **Cost efficient** - Only use expensive models when needed

---

## Example Flows

### Example 1: Simple Job (No Workflow)

**Job:** "Fix typo in README"

**Flow:**
1. Discussion: Sonnet determines this is trivial
2. Execute directly (no workflow stages needed)

---

### Example 2: Moderate Complexity

**Job:** "Add logging to API endpoints"

**Flow:**
1. **Discussion** (Stage 1): Requirements clear, approach straightforward
2. **Planning** (Stage 3): Create runbook with `/runbook`
3. **Execution** (Stage 4): Run steps with `/orchestrate`
4. **Review** (Stage 5): Delegate to corrector
5. **Completion** (Stage 6): Update docs, finalize

---

### Example 3: Complex Job

**Job:** "Implement real-time data sync across services"

**Flow:**
1. **Discussion** (Stage 1): Complex, multiple approaches possible
2. **Design** (Stage 2): Use `/design` to explore options (WebSockets vs SSE vs polling)
3. **Planning** (Stage 3): Create runbook from design with `/runbook`
4. **Execution** (Stage 4): Run Phase 1 steps with `/orchestrate`
5. **Planning** (Stage 3): Plan Phase 2 after Phase 1 validation
6. **Execution** (Stage 4): Run Phase 2 steps
7. **Review** (Stage 5): Delegate to corrector
8. **Completion** (Stage 6): Update architecture docs with `/claude-md-management:revise-claude-md`, finalize

---

## Tips and Best Practices

### When to Use Design Stage

**Use `/design` when:**
- You're not sure what approach to take
- Multiple valid solutions exist
- Architectural impact is significant
- Requirements are fuzzy or incomplete

**Skip `/design` when:**
- Implementation is obvious
- Requirements are crystal clear
- Changes are localized and low-risk

### Model Selection

- **Sonnet**: Orchestration (Stage 4), planning, review, most work (Stages 1, 3, 5, 6)
- **Opus**: Design and complex architecture only (Stage 2)
- **Haiku**: individual step agents where a runbook assigns it; not the orchestrator

### Runbook Changes Mid-Execution

If execution reveals issues with the runbook:

1. Update the runbook markdown file
2. Re-run `prepare-runbook.py` (idempotent, overwrites artifacts)
3. Resume execution from failed step

Git tracks all changes to runbook and artifacts.

### Documentation Flow

**During execution:**
- Record decisions in `plans/<name>/decisions.md`

**After completion:**
- Move important decisions to `agents/decisions/`
- Archive plan directory (or delete per project convention)

---

## Related Documentation

- **CLAUDE.md**: Agent instructions, communication rules, patterns
- **`.claude/handoff-task.md`**: Current task frame — in-progress task and open decisions
- **agents/decisions/**: Architectural decisions and rationale

---

## Plan Lifecycle

### 1. Creation
- Start with `/design` skill (auto-detects workflow and complexity)
- OR create design doc manually in `plans/<project-name>/`

### 2. Active Development
- Update design documents as work progresses
- Generate execution artifacts via `prepare-runbook.py`
- Track progress in `.claude/handoff-task.md`

### 3. Execution
- Use `/orchestrate` skill for runbook execution
- Write reports to `plans/<name>/reports/`
- Update `.claude/handoff-task.md` with progress

### 4. Completion
- Extract valuable decisions to `agents/decisions/`
- Archive or delete plan directory (per project convention)

---

## Script: `prepare-runbook.py`

**Location:** `plugin/bin/prepare-runbook.py`

**Purpose:** Transform runbook document into execution artifacts.

**Usage:**
```bash
prepare-runbook.py plans/foo/runbook.md
```

**Creates:**
- `plans/foo/steps/step-*.md` (individual steps)
- `plans/foo/orchestrator-plan.md` (orchestrator instructions)

**Runbook format:**
```markdown
---
name: <runbook-name>
model: sonnet  # default model for steps
---

## Common Context
[Shared knowledge for all steps]

## Step 1: [Title]
[Step instructions]

## Step 2: [Title]
[Step instructions]

## Orchestrator Instructions
[Sequencing, error handling, reporting]
```

**Validation:**
- Fails on: missing baseline, missing steps, duplicate numbers
- Warns on: existing artifacts, missing optional sections

---

## Change Log

**2026-01-19**: Initial workflow documentation (general workflow pattern formalized)
**2026-01-31**: Renamed from "oneshot workflow" to "general workflow" (oneshot skill superseded by `/design`)
**2026-08-13**: Merged the duplicated `/design` skill entry; orchestrator model tier stated as Sonnet, matching `/orchestrate`
