# Current Implementation: Agent Generation and Orchestration Dispatch

## Summary

The current implementation uses a single one-agent-per-runbook model where `prepare-runbook.py` generates a plan-specific agent that carries all runbook context (common context + frontmatter). The orchestrator dispatches to this single agent for each step, and the agent receives fresh context for each execution. This explores how the system currently works and identifies where phase-scoped agent generation would fit.

---

## 1. prepare-runbook.py: Agent Generation

**File:** `/Users/david/code/claudeutils-wt/phase-scoped-agents/agent-core/bin/prepare-runbook.py`

### Current Workflow

The script transforms runbook markdown into three artifacts:

1. **Plan-specific agent** (`.claude/agents/<runbook-name>-task.md`)
   - Frontmatter with agent metadata
   - Baseline template (artisan or test-driver)
   - Common context section (appended after baseline)
   - Clean-tree requirement statement

2. **Step files** (`plans/<runbook-name>/steps/step-*.md`)
   - H1 header with step identifier
   - Metadata header: Plan, Execution Model, Phase, optional Report Path
   - Optional phase context section (injected preamble)
   - Step body content (from runbook)

3. **Orchestrator plan** (`plans/<runbook-name>/orchestrator-plan.md`)
   - Sequential step listing with phase boundaries
   - Phase model mappings
   - Execution mode (steps or inline)
   - Phase boundary markers

### Agent Creation: One Agent Per Runbook

**Key function:** `generate_agent_frontmatter()` (lines 794-797)

```python
def generate_agent_frontmatter(runbook_name, model=None) -> str:
    """Generate frontmatter for plan-specific agent."""
    model_line = f"model: {model}\n" if model is not None else ""
    return f'---\nname: {runbook_name}-task\ndescription: Execute {runbook_name} steps from the plan with plan-specific context.\n{model_line}color: cyan\ntools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]\n---\n'
```

**Baseline selection:** `read_baseline_agent()` (lines 771-791)

- TDD runbooks → `agent-core/agents/test-driver.md`
- General runbooks → `agent-core/agents/artisan.md`
- Mixed runbooks → `agent-core/agents/artisan.md` (baseline)

**Agent composition:** `validate_and_create()` (lines 1090-1283)

```
frontmatter (generated)
+ baseline_body (from test-driver or artisan)
+ common_context (appended as "# Runbook-Specific Context")
+ clean-tree requirement statement
```

### Context Injection Structure

**Common Context** (extracted at lines 459-595 via `extract_sections()`)

- Appears in runbook as `## Common Context` section
- Applied as `---\n# Runbook-Specific Context\n\n{common_context}`
- Single context shared by all steps of this runbook

**Phase-specific content** NOT currently generated as per-phase context:

- Phase preambles extracted (lines 610-647) but only injected into individual step files
- Each step file gets `## Phase Context` section with preamble text
- No per-phase agent created

### Phase Type Handling

**Frontmatter field:** `type` (tdd/general/mixed/inline)

**TDD runbooks** (type: tdd):
- Extracted via `extract_cycles()` (lines 104-166)
- Baseline: `test-driver.md`
- Default common context injected if absent (lines 740-744)

**General runbooks** (type: general):
- Extracted via `extract_sections()` (lines 459-595)
- Baseline: `artisan.md`
- No automatic common context

**Mixed runbooks** (type: mixed):
- Auto-detected when both cycles and steps exist (lines 1358-1365)
- Baseline: `artisan.md`

**Inline-only runbooks** (type: inline):
- Only inline phases, no step files created
- Orchestrator handles these directly

### Agent Frontmatter Structure

**Generated frontmatter example** (from `generate_agent_frontmatter()`):

```yaml
---
name: hook-batch-task
description: Execute hook-batch steps from the plan with plan-specific context.
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---
```

**No skills field** in generated agents. Skills injected via baseline template or not at all.

---

## 2. Orchestrate Skill: Dispatch Mechanism

**File:** `/Users/david/code/claudeutils-wt/phase-scoped-agents/agent-core/skills/orchestrate/SKILL.md`

### Agent Selection for Steps

**Section 3.1 (lines 93-103):**

```
Use Task tool with:
- subagent_type: "<runbook-name>-task"
- prompt: "Execute step from: plans/<runbook-name>/steps/step-N.md"
- model: [from step file header "Execution Model" field]
```

**Current behavior:**
- Single subagent type per runbook: `<runbook-name>-task`
- Model override per-step from `**Execution Model**` in step header
- Same agent used for all steps (no phase-scoping)

### Model Selection Per-Step

**Critical constraint (lines 105):**

> The orchestrator itself may run on haiku, but step agents use the model specified in each step file's **header metadata**. The `**Execution Model**` field appears in the step file header (lines before the `---` separator), placed there by `prepare-runbook.py`. Read the header section of each step file to extract the model — do NOT search the full body. Do NOT default all steps to haiku.

**Implementation:** `extract_step_metadata()` (lines 800-832)

```python
def extract_step_metadata(content, default_model=None):
    """Extract execution metadata from step/cycle content."""
    # Looks for bold-label fields like **Execution Model**: Sonnet
    model_match = re.search(r"\*\*Execution Model\*\*:\s*(\w+)", content, re.IGNORECASE)
```

### Inline Phase Handling

**Section 3.0 (lines 78-91):**

Inline phases are executed by the orchestrator directly:

1. Orchestrator reads phase content from runbook
2. Orchestrator executes edits (Read/Edit/Write)
3. Orchestrator runs `just precommit` validation
4. Orchestrator applies review-requirement proportionality
5. Orchestrator commits changes

**No agent dispatch for inline phases** — orchestrator is a "weak orchestrator" that delegates steps but executes inline phases directly.

### Step File Structure

**Generated by `generate_step_file()` (lines 915-950) and `generate_cycle_file()` (lines 953-984)**

```markdown
# Step N.M

**Plan**: `plans/runbook-name/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Phase Context

[Optional preamble text from phase header]

---

[Step body content]
```

**Metadata in step header (not frontmatter):**

- Lines before first `---` separator
- Human-readable format (`**Field**: value`)
- Orchestrator reads these lines to extract model, phase, report path

---

## 3. Existing Agent Definitions

### Baseline Agents

**test-driver.md** (lines 1-327)
- Purpose: TDD cycle execution
- Model: haiku
- Skills: project-conventions
- Role: Execute RED-GREEN-REFACTOR with strict protocol
- Context handling: Baseline + common context combined at generation time
- Each cycle gets fresh context (no accumulation)

**artisan.md** (lines 1-119)
- Purpose: General task execution
- Model: haiku
- Skills: project-conventions
- Role: Execute assigned tasks following plans
- Output format: Filepath (success) or `error: [description]`

### Plan-Specific Agents (Generated)

**Examples:** `.claude/agents/hb-p*.md` (hook-batch phases 1-5)

These are NOT phase-scoped in the sense of the task — they're still one-per-runbook but have different names by coincidence of file organization.

**hb-p1.md example:**

```yaml
---
name: hb-p1
description: Hook-batch Phase 1 TDD execution agent (UserPromptSubmit improvements).
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

## First Action

Read `plans/hook-batch/context/phase-1.md` — contains prerequisites, key decisions, checkpoint gate, and completion criteria.

## TDD Protocol

[embedded protocol]

## Stop Conditions

[embedded stop conditions]
```

**Key observation:** This agent reads a phase-specific context file (`phase-1.md`) as its first action. This is the EXISTING pattern for phase-scoped context, though not via the generator.

### corrector.md (Review Agent)

**File:** `/Users/david/code/claudeutils-wt/phase-scoped-agents/agent-core/agents/corrector.md`

- Model: sonnet
- Skills: project-conventions, error-handling, memory-index
- Role: Review + apply all fixes
- Status taxonomy: FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE
- Does NOT review runbooks (rejects them)

---

## 4. Orchestrator Plan Format

**File:** `/Users/david/code/claudeutils-wt/phase-scoped-agents/plans/hook-batch/orchestrator-plan.md`

### Structure (Generated by `generate_default_orchestrator()`, lines 987-1087)

```markdown
# Orchestrator Plan: runbook-name

## Phase-Agent Mapping

| Phase | Agent | Model | Type |
|-------|-------|-------|------|
| 1 (steps 1-1 to 1-5) | hb-p1 | sonnet | TDD |
| 2 (steps 2-1 to 2-2) | hb-p2 | sonnet | TDD |
| 3 (steps 3-1 to 3-2) | hb-p3 | haiku | General |
| 4 (steps 4-1 to 4-3) | hb-p4 | haiku | General |
| 5 (steps 5-1 to 5-4) | hb-p5 | haiku | General |

Exception: step-5-3 uses sonnet (override via Task model parameter).

## Step Execution Order

## step-N-M (Cycle/Step N.M)
Agent: agent-name
Execution: steps/step-N-M.md

## step-N-M (Cycle/Step N.M) — PHASE_BOUNDARY
Agent: agent-name
Execution: steps/step-N-M.md
[Last item of phase N. Insert functional review checkpoint before Phase N+1.]
```

### Agent Assignment

**Current:** Fixed mapping at generation time (lines 1019-1052)

- Single agent name for all steps in a phase
- Phase boundaries marked with `— PHASE_BOUNDARY`
- No dynamic assignment

**Note:** The plan format reserves space for per-phase agents but doesn't use them generatively. It's a structural placeholder for manual orchestration of phase-scoped agents.

---

## 5. Key Paths and Data Models

### Artifact Locations

| Artifact | Path | Creator | Consumer |
|----------|------|---------|----------|
| Runbook | `plans/<name>/runbook.md` | User | prepare-runbook.py |
| Agent | `.claude/agents/<name>-task.md` | prepare-runbook.py | orchestrator (Task subagent_type) |
| Step files | `plans/<name>/steps/step-N.md` | prepare-runbook.py | orchestrator (reads header, passes path to agent) |
| Orchestrator plan | `plans/<name>/orchestrator-plan.md` | prepare-runbook.py | orchestrator (reads order + phase boundaries) |
| Phase context (optional) | `plans/<name>/context/phase-N.md` | User (manual) | agent (reads via hardcoded path in First Action) |

### Code Flow: Generation

```
runbook.md (user input)
    ↓
parse_frontmatter() → metadata (type, model, name)
    ↓
extract_sections() → common_context, steps, inline_phases
extract_cycles() → cycles (if TDD)
    ↓
validate_and_create()
    ↓
    ├─→ generate_agent_frontmatter() + read_baseline_agent()
    │   ├─→ append common_context
    │   └─→ append clean-tree requirement
    │   → .claude/agents/<name>-task.md
    │
    ├─→ for each step/cycle: generate_step_file() / generate_cycle_file()
    │   ├─→ extract metadata (model, phase)
    │   ├─→ inject phase preamble as Phase Context
    │   → plans/<name>/steps/step-N.md
    │
    └─→ generate_default_orchestrator()
        → plans/<name>/orchestrator-plan.md
```

### Code Flow: Execution (Orchestrator)

```
orchestrator skill (/orchestrate <runbook-name>)
    ↓
read orchestrator-plan.md → step list + phase boundaries
    ↓
for each step:
    ├─→ read step-N.md header
    ├─→ extract model from **Execution Model**: field
    ├─→ Task(subagent_type="<runbook-name>-task", model=extracted_model, prompt="Execute step from: plans/<name>/steps/step-N.md")
    │   ↓ (agent receives step file path, loads it)
    │   ├─→ read plans/<name>/steps/step-N.md
    │   ├─→ (optional) read Phase Context section
    │   ├─→ execute step body
    │   └─→ report success or error
    │
    ├─→ check git status (must be clean)
    ├─→ on phase boundary: delegate to corrector (checkpoint review)
    └─→ continue to next step
```

---

## 6. Gaps and Opportunities for Phase-Scoped Agents

### Current Limitations (Why Phase-Scoped Agents Are Needed)

1. **Single agent carries all context**
   - Agent receives entire runbook's common context, even for phase-specific work
   - No natural boundary between phase concerns
   - All phases share same agent definition

2. **Step files carry phase preamble only**
   - Phase context is optional and embedded in step file
   - No dedicated phase context file at generation time
   - Agents must read step file to access phase context

3. **Orchestrator plan doesn't encode agent-per-phase**
   - Current format shows `Agent: hb-p1` as a manual mapping
   - But these agents aren't generated by prepare-runbook.py
   - Missing: structured generation of per-phase agents with per-phase context

4. **Phase context retrieval is hardcoded**
   - Example: `hb-p1.md` reads `plans/hook-batch/context/phase-1.md` via hardcoded path
   - Not generated by prepare-runbook.py
   - Not surfaced in orchestrator plan

### Required Changes for Phase-Scoped Implementation

**Generation (prepare-runbook.py):**
- Generate one agent per phase (not per runbook)
- Each phase agent receives only its phase's context
- Orchestrator plan maps phases to generated agent names
- Phase context extracted and injected per-agent

**Dispatch (orchestrate skill):**
- Read orchestrator plan to get phase-specific agent name
- Extract agent name from `Agent:` field per-step
- Dispatch to `<runbook-name>-phase-<N>-task` instead of `<runbook-name>-task`
- Same step file and model override mechanism

**Agent Definition:**
- Per-phase agent carries baseline + phase-specific context only
- Frontmatter: `name: <runbook-name>-phase-<N>-task`
- Phase context injected as "# Phase Context" section (not "Runbook-Specific Context")
- No common context (or minimal cross-phase common context)

---

## 7. Reference Files and Line Numbers

### prepare-runbook.py Key Functions

| Function | Lines | Purpose |
|----------|-------|---------|
| parse_frontmatter | 61-101 | Extract metadata |
| extract_cycles | 104-166 | Parse TDD cycles |
| extract_sections | 459-595 | Parse steps, common context, phases |
| extract_phase_preambles | 610-647 | Extract phase headers' preamble text |
| generate_agent_frontmatter | 794-797 | Create agent YAML header |
| read_baseline_agent | 771-791 | Load test-driver or artisan |
| generate_step_file | 915-950 | Create step-N.md with Phase Context |
| generate_cycle_file | 953-984 | Create cycle-N.M.md with Phase Context |
| generate_default_orchestrator | 987-1087 | Create orchestrator-plan.md |
| validate_and_create | 1090-1283 | Main orchestration (lines 1188-1205 show agent composition) |

### Orchestrate Skill Key Sections

| Section | Lines | Purpose |
|---------|-------|---------|
| 3.1: Agent dispatch | 93-103 | Describe Task tool usage |
| Model selection | 105 | Critical constraint on per-step models |
| Phase boundary | 137-154 | Checkpoint delegation template |

### Agent Files

| File | Role | Notes |
|------|------|-------|
| agent-core/agents/test-driver.md | TDD baseline | ~327 lines, strict protocol |
| agent-core/agents/artisan.md | General baseline | ~119 lines, quiet execution |
| .claude/agents/hb-p1.md (etc) | Plan-specific | Generated, reads phase context manually |
| agent-core/agents/corrector.md | Review agent | Status taxonomy, fix-all protocol |

---

## 8. Key Insights

### Existing Phase-Scoped Patterns

The codebase already has phase-scoped concepts:

1. **Phase context files** (manual)
   - `plans/hook-batch/context/phase-1.md` read by `hb-p1.md` agent
   - Not generated; author must create these
   - Pattern: agent's "First Action" reads phase context

2. **Phase preambles** (generated)
   - Extracted by `extract_phase_preambles()` and injected into step files
   - Each step carries its phase preamble as optional "## Phase Context" section
   - Agents read this when present

3. **Orchestrator plan metadata**
   - Already has `Phase-Agent Mapping` table showing agent-per-phase intent
   - Format prepared for per-phase agents but not generated

### What Would Change for Full Phase-Scoping

**In prepare-runbook.py:**
- `generate_agent_frontmatter()` → per-phase name
- `validate_and_create()` → loop over phases, create one agent per phase
- Orchestrator plan generation → assign per-phase agent to steps

**In orchestrate skill:**
- Read orchestrator plan's `Agent:` field per-step
- Dispatch to phase-specific agent name (already supports this via subagent_type parameter)

**In runbooks:**
- No change to markdown structure
- prepare-runbook.py handles agent generation automatically

**Benefits:**
- Each agent starts with only its phase's context (smaller context per-agent)
- Natural phase boundaries in agent lifecycle
- Enables phase-specific customization if needed later
- Orchestrator plan becomes the agent assignment record

---

## 9. Files and Paths (Absolute)

**Code:**
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/agent-core/bin/prepare-runbook.py`
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/agent-core/skills/orchestrate/SKILL.md`
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/agent-core/agents/test-driver.md`
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/agent-core/agents/artisan.md`
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/agent-core/agents/corrector.md`

**Example Artifacts:**
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/plans/hook-batch/orchestrator-plan.md`
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/plans/hook-batch/steps/step-1-1.md`
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/.claude/agents/hb-p1.md`

**Session Context:**
- `/Users/david/code/claudeutils-wt/phase-scoped-agents/agents/session.md`
