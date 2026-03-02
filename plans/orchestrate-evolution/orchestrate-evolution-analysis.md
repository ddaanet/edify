# Orchestrate Evolution Analysis

## Summary

The current orchestrate skill (`/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md`) implements a strictly sequential weak orchestrator. Session learnings from the worktree-skill planning orchestration identified seven concrete gaps. The requirements document (`/Users/david/code/claudeutils/plans/orchestrate-evolution/requirements.md`) is skeletal -- three open questions and no concrete requirements. This report maps session learnings to specific skill/infrastructure changes needed.

## 1. Current Orchestration Model

### Orchestrate Skill (`/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md`)

The skill is a 474-line document implementing the weak orchestrator pattern:

- **Execution:** Strictly sequential -- steps execute one at a time (Section 3: "Execute Steps Sequentially")
- **Delegation:** Each step dispatched to plan-specific agent via Task tool
- **Model selection:** Read from step file header `**Execution Model**` field
- **Post-step:** Git status check (3.3) -- dirty tree = immediate stop
- **Phase boundaries:** Detected by comparing `Phase:` field between consecutive step files. Triggers vet-fix-agent checkpoint delegation
- **Error escalation:** Haiku -> Sonnet -> User (three levels)
- **Completion:** TDD runbooks get vet + review-tdd-process; general runbooks get vet suggestion
- **Continuation:** Cooperative with continuation passing system (default-exit: `/handoff`, `/commit`)

Key constraint in Section "Critical Constraints":
> Always sequential unless orchestrator plan explicitly allows parallel

### Plan-TDD Skill (`/Users/david/code/claudeutils/agent-core/skills/plan-tdd/SKILL.md`)

1035 lines. Five-phase process: Tier Assessment -> Intake -> Outline -> Expansion -> Assembly. Planning IS orchestratable as a DAG -- the worktree-skill session proved phase expansions are fully parallel (8 concurrent sonnet agents). But this parallelism was done ad-hoc by the opus orchestrator, not by the orchestrate skill.

### Plan-Adhoc Skill (`/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md`)

1104 lines. Four-point process: Discover -> Outline -> Expand -> Assemble. Similar DAG structure to plan-tdd.

### Delegation Fragment (`/Users/david/code/claudeutils/agent-core/fragments/delegation.md`)

44 lines. Orchestration-only scope. Covers model selection, quiet execution pattern, tool usage reminders. No parallel dispatch guidance.

### Execution Routing Fragment (`/Users/david/code/claudeutils/agent-core/fragments/execution-routing.md`)

26 lines. Interactive routing: do directly > use recipe > delegate. Clearly separated from delegation (orchestration).

## 2. Worktree-Skill Orchestration Experience

### Session Learnings (from `/Users/david/code/claudeutils/agents/learnings.md`)

The following learnings directly relate to orchestration evolution:

**Planning as orchestratable DAG:**
- /plan-tdd phases decompose into independent delegations
- Phase expansions are fully parallel (all read same inputs, write different files)
- 8 concurrent sonnet agents produced correct output
- Per-phase review needs full outline context (scope alignment)
- Holistic review runs once after all phases complete

**Post-step verify-remediate-RCA pattern:**
- After each agent: git status + precommit -> remediate if dirty -> add pending RCA task
- General orchestration pattern, not session-specific

**Delegation requires commit instruction:**
- Agents write artifact, return filepath, leave tree dirty
- Must include explicit "commit your output before returning" in every delegation

**Consolidation gate catches phase overengineering:**
- Outline review should flag trivial phases for merge

**Delegation prompt deduplication:**
- Repeating boilerplate in N parallel prompts bloats orchestrator context
- Write shared content to file, reference by path

**Orchestration context bloat mitigation:**
- Handoff is NOT delegatable (requires current agent's session context)
- Plan for restart boundary: planning -> restart -> execution

**Agent scope creep in orchestration:**
- Prompt must include "Execute ONLY this step. Do NOT read or execute other step files."
- Orchestrator must verify agent return describes only assigned step

**Per-artifact vet coverage required:**
- Each production artifact requires vet-fix-agent review
- Gate B is boolean (any report?), not coverage ratio (artifacts:reports 1:1)

**Sequential Task launch breaks parallelism:**
- Anti-pattern: Launch Task agents one at a time when all inputs ready
- Batch all independent Task calls in single message

**Phase boundaries require checkpoint delegation:**
- Phase boundary = hard stop requiring explicit checkpoint delegation per 3.3

### Orchestration Reports

12 reports exist at `/Users/david/code/claudeutils/plans/worktree-skill/reports/`:
- `intake-assessment.md`, `outline-review.md`, `runbook-outline-review.md`
- `phase-0-review.md` through `phase-5-review.md` (6 per-phase reviews)
- `runbook-final-review.md` (holistic cross-phase review)
- `design-review.md`, `explore-integration.md`

The holistic review confirmed 42 cycles across 6 phases, all requirements covered, no issues.

## 3. Gap Analysis

### Gap 1: DAG Execution (Parallel Phases)

**Current:** Orchestrate skill section 3 is "Execute Steps Sequentially." The only escape hatch: "Always sequential unless orchestrator plan explicitly allows parallel."

**Needed:** First-class parallel dispatch. The orchestrator plan should declare which steps/phases can run in parallel. The orchestrate skill should batch independent Task calls in a single message.

**Evidence:** 8 parallel phase expansions worked correctly during worktree-skill planning. The pattern: all read same inputs, write different files, git handled concurrent commits to different files.

**Concrete change:** Add a parallel execution section to the orchestrate skill. The orchestrator plan (generated by prepare-runbook.py) should emit dependency/parallelism metadata per step. The orchestrate skill reads this and batches independent steps.

### Gap 2: Post-Step Verify-Remediate-RCA Pattern

**Current:** Post-step check is binary: clean tree (proceed) or dirty tree (stop and escalate to user). No remediation delegation, no RCA task generation.

**Needed:** After each agent returns success:
1. `git status --porcelain` (existing)
2. If dirty: delegate remediation to sonnet (commit or fix), not immediate escalation to user
3. After remediation: add pending RCA task to session.md for fixing the causing skill/prompt
4. Also: run `just precommit` as second verification layer

**Evidence:** Learning "Post-step verify-remediate-RCA pattern" -- dirty tree doesn't need user intervention if it's just uncommitted files.

**Concrete change:** Modify skill section 3.3 to add remediation delegation before user escalation. Add RCA task appending.

### Gap 3: Delegation Prompt Deduplication

**Current:** Each Task call includes full prompt text. For N parallel expansions, this means N copies of identical boilerplate.

**Needed:** Write shared content (boilerplate, common context, conventions) to a file. Reference by path in delegation prompts: "Read shared context from `plans/<name>/shared-context.md`."

**Evidence:** Learning "Delegation prompt deduplication" -- bloats orchestrator context N-fold.

**Concrete change:** Add convention to orchestrate skill: when dispatching 3+ parallel tasks, write shared prompt content to a temp file, reference in prompts. prepare-runbook.py could pre-generate this shared context file.

### Gap 4: Context Bloat Mitigation

**Current:** No explicit context management. Long orchestrations accumulate messages.

**Needed:**
- Handoff is NOT delegatable (requires current session context) -- must stay inline
- Plan for restart boundary between planning and execution sessions
- Quiet execution pattern (agents write to files, return only filepath) already exists but could be more aggressively applied

**Evidence:** Learning "Orchestration context bloat mitigation" -- complex reasoning at end of 50+ message sessions.

**Concrete change:** Add guidance to orchestrate skill about restart boundaries. For very long runbooks (>20 steps), recommend splitting into sub-orchestrations with restart between them.

### Gap 5: Phase Boundary Checkpoint Delegation

**Current:** Phase boundary detection exists (skill section 3.3), with vet-fix-agent checkpoint delegation template.

**Gap is partially filled.** The checkpoint delegation is documented. The remaining gap: the prose gate D+B hybrid pattern -- phase boundary check must open with a tool call (Read next step file) to avoid being skipped in execution mode.

**Evidence:** Learning "Phase boundaries require checkpoint delegation" -- "hard stop requiring explicit checkpoint delegation per orchestrate skill 3.3." Also "Prose gate D+B hybrid fix."

**Status:** Mostly addressed. The merged 3.3/3.4 step already opens with `git status --porcelain` (tool call). Minor refinement possible.

### Gap 6: Consolidation Gates

**Current:** Consolidation gates exist in plan-tdd (Phase 1.6) and plan-adhoc (Point 0.85), NOT in the orchestrate skill. This is correct -- consolidation is a planning concern, not an execution concern.

**Gap is architectural, not in orchestrate.** The orchestrate skill doesn't need consolidation gates. Planning skills already have them. The learning "Consolidation gate catches phase overengineering" targets plan-tdd and plan-adhoc.

**Status:** Already addressed in planning skills. No orchestrate skill change needed.

### Gap 7: Commit Instruction in Delegation Prompts

**Current:** prepare-runbook.py appends this to every generated agent:
```
**Clean tree requirement:** Commit all changes before reporting success.
The orchestrator will reject dirty trees -- there are no exceptions.
```

The orchestrate skill section 3.1 prompt template does NOT include a commit instruction.

**Needed:** Every delegation prompt must include explicit "commit your output before returning."

**Evidence:** Learning "Delegation requires commit instruction" -- agents optimize for stated task, cleanup is not implied.

**Concrete change:** Add commit instruction to the step delegation prompt template in skill section 3.1. Also verify prepare-runbook.py's agent content includes it (it does, via the "Clean tree requirement" footer).

### Additional Gap: Scope Creep Prevention

**Current:** No explicit scope constraint in delegation prompts.

**Needed:** "Execute ONLY this step. Do NOT read or execute other step files."

**Evidence:** Learning "Agent scope creep in orchestration" -- agent reads ahead and executes step N+1.

**Concrete change:** Add scope constraint to delegation prompt template.

## 4. Requirements Document Enrichment

The current requirements document at `/Users/david/code/claudeutils/plans/orchestrate-evolution/requirements.md` contains:

```
Absorb planning into orchestrate, finalize phase pattern.
```

Based on this analysis, the requirements should be expanded to:

### Functional Requirements

- **FR-1: Parallel step dispatch** -- Orchestrate skill batches independent steps in single Task message
- **FR-2: Post-step remediation** -- Dirty tree triggers sonnet remediation before user escalation
- **FR-3: RCA task generation** -- Remediated dirty trees generate pending RCA tasks
- **FR-4: Delegation prompt deduplication** -- Shared context written to file, referenced by path
- **FR-5: Commit instruction in prompts** -- Every delegation includes "commit before returning"
- **FR-6: Scope constraint in prompts** -- Every delegation includes "execute ONLY this step"
- **FR-7: Precommit verification** -- Post-step runs `just precommit` as second verification layer

### Non-Functional Requirements

- **NFR-1: Context bloat mitigation** -- Restart boundary guidance for long orchestrations
- **NFR-2: Backward compatibility** -- Existing orchestrator plans continue to work (sequential by default)
- **NFR-3: Weak orchestrator preservation** -- New features are mechanical (grep, file existence), not judgment

### Infrastructure Changes

- **prepare-runbook.py:** Emit parallelism metadata in orchestrator plan (step dependencies, parallel groups)
- **orchestrator-plan.md format:** Add step dependency graph section
- **delegation.md fragment:** Add parallel dispatch guidance, prompt deduplication convention

### Open Questions (Resolved by This Analysis)

- "How does orchestrate absorb planning responsibilities?" -- It doesn't absorb planning itself. Rather, the orchestrate skill gains the patterns discovered during planning orchestration (parallel dispatch, deduplication, remediation). Planning remains in plan-tdd and plan-adhoc.
- "What is the finalized phase pattern?" -- Post-step verify-remediate-RCA. Phase boundaries trigger checkpoint delegation (already partially implemented).
- "Integration with continuation passing system?" -- Already implemented in current orchestrate skill (cooperative mode with default-exit chain).

## 5. Cycle 4.2 Parser Issue Analysis

### The Problem

`/Users/david/code/claudeutils/plans/worktree-skill/runbook-phase-4.md` cycle 4.2 (lines 52-109) contains a fenced code block in its GREEN section (lines 79-95):

```markdown
` ` `markdown
# Session: Worktree — <task name>

**Status:** Focused worktree for parallel execution.

## Pending Tasks         <-- H2 header inside code block

- [ ] **<task name>** — <full metadata from original>

## Blockers / Gotchas    <-- H2 header inside code block

<only blockers relevant to this task>

## Reference Files       <-- H2 header inside code block

<only references relevant to this task>
` ` `
```

### Parser Behavior (Line-by-Line)

In `extract_cycles()` at `/Users/david/code/claudeutils/agent-core/bin/prepare-runbook.py:85-142`:

1. Line 52: `## Cycle 4.2:` -- parser starts cycle 4.2, `current_cycle` set
2. Lines 53-83: Content accumulated normally (including the opening ` ``` ` at line 79)
3. **Line 84: `## Pending Tasks`** -- matches `line.startswith('## ')` at parser line 126
   - Parser does NOT track fenced code block state
   - Cycle 4.2 is terminated prematurely: content saved (lines 52-83), appended to cycles list
   - `current_cycle` set to None
4. Lines 85-94: These lines are inside the code block but the parser has no current_cycle -- they are silently dropped
5. **Line 88: `## Blockers / Gotchas`** -- another H2, but current_cycle is None so no effect (just skipped)
6. **Line 92: `## Reference Files`** -- same, skipped
7. Line 95: Closing ` ``` ` -- skipped (no current_cycle)
8. Lines 97-107: These lines contain the `**Error Conditions**` and `**Success Criteria**` for cycle 4.2 -- silently dropped
9. **Line 111: `## Cycle 4.3:`** -- new cycle starts normally

### Consequence

- **Cycle 4.2 content is truncated** at `## Pending Tasks` (line 84). Everything from line 84 to line 109 is lost.
- **Error Conditions section (line 104) is lost**, causing `validate_cycle_structure()` to report: `ERROR: Cycle 4.2 missing required section: Stop/Error Conditions`
- **Cycle 4.3 is NOT lost** -- it starts at line 111 with a proper `## Cycle 4.3:` header. The grep confirms all 42 cycle headers are present.

### Cycle Count Verification

From the grep output, all 42 cycles are detected as headers:
- Phase 0: 0.1-0.9 (9 cycles)
- Phase 1: 1.1-1.7 (7 cycles)
- Phase 2: 2.1-2.4 (4 cycles)
- Phase 3: 3.1-3.13 (13 cycles)
- Phase 4: 4.1-4.5 (5 cycles)
- Phase 5: 5.1-5.4 (4 cycles)
- **Total: 42 cycles** -- matches holistic review

The issue is content truncation of cycle 4.2, not missing cycles.

### Fix Options

**Option A: Fix the content (recommended, simplest)**

Replace the fenced code block in cycle 4.2 GREEN section with indented block (4 spaces), which the parser won't interpret as H2 headers:

```markdown
Describe focused session.md format with indented template:

    # Session: Worktree — <task name>

    **Status:** Focused worktree for parallel execution.

    ## Pending Tasks

    - [ ] **<task name>** — <full metadata from original>

    ## Blockers / Gotchas

    <only blockers relevant to this task>

    ## Reference Files

    <only references relevant to this task>
```

**Option B: Escape H2 markers in code block**

Replace `## Pending Tasks` with `\## Pending Tasks` (or use HTML entity `&#35;&#35;`). This is brittle and reduces readability.

**Option C: Fix the parser**

Add fenced code block tracking to `extract_cycles()`:

```python
in_code_block = False
for i, line in enumerate(lines):
    if line.startswith('```'):
        in_code_block = not in_code_block
        if current_cycle is not None:
            current_content.append(line)
        continue
    if in_code_block:
        if current_cycle is not None:
            current_content.append(line)
        continue
    # ... existing H2/cycle detection logic
```

This is a proper fix but adds complexity to the parser. Given this is the only instance, Option A is simpler.

**Recommendation:** Option A (indented block). It's a content fix that requires no code changes, takes 30 seconds, and the indented format is still readable for the executing agent.

## Patterns

- The orchestrate skill's sequential-only design was adequate for early runbooks but became a bottleneck during complex planning orchestration
- The "weak orchestrator" pattern works -- the gaps are in the mechanical checks around delegation, not in adding intelligence
- All seven gaps can be addressed without violating the weak orchestrator principle (all fixes are mechanical: grep, file write, prompt template changes)
- prepare-runbook.py is the natural place to encode parallelism metadata since it already parses the runbook structure and generates the orchestrator plan

## Gaps in This Analysis

- No concrete examples of orchestrator plan format with parallelism metadata (needs design work)
- The "absorb planning" language in requirements is misleading -- planning orchestration was ad-hoc by opus, not by the orchestrate skill. Whether to formalize planning orchestration inside the orchestrate skill or keep it separate is an open design question
- No assessment of how context bloat mitigation interacts with continuation passing (restart boundary vs continuation chain)
- The cycle 4.2 fix was not tested (only analyzed via code reading)
