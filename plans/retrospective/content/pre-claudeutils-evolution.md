# Pre-claudeutils Agent Instruction Evolution

This document traces the evolution of agent behavioral instructions across 6 pre-claudeutils projects, from October 2025 through January 2026. Evidence is drawn directly from git history, showing how instruction patterns emerged, evolved, and consolidated into the claudeutils framework.

## Chronological Timeline

| Date | Repo | Key Event | Signal |
|------|------|-----------|--------|
| 2025-09-30 | rules | Initial rules.md (v1) | Development rules begin |
| 2025-10-02 | rules | Rename rules.md → AGENTS.md | First "AGENTS.md" naming |
| 2025-10-15 | emojipack | Add AGENTS.md with TDD focus | Testing emphasis |
| 2025-11-23 | box-api | Add AGENTS.md (complex integration) | Infrastructure rules appear |
| 2025-11-28 | oklch-theme | Initial AGENTS.md with "LLM awareness" section | Meta-rules about AI limitations |
| 2025-12-01 | oklch-theme | Update AGENTS.md: design process + orchestration | Delegation patterns solidify |
| 2026-01-02 | pytest-md | Initial AGENTS.md (token efficiency focus) | Agent optimization rules |
| 2026-01-12 | home | Initial AGENTS.md (session management) | Orchestrator + sub-agent pattern |
| 2026-01-12 | home | Major AGENTS.md overhaul: commit delegation protocol | Formal delegation rules |

## Per-Repo Analysis

### 1. rules (~Oct 2025) — Foundation Era

**Timeline:**
- 2025-09-30: Initial commit with rules.md
- 2025-10-02: Rename rules.md → AGENTS.md

**Initial Version (2025-09-30):**

The earliest rules.md is minimalist—establishing core TDD and version control patterns:

```markdown
# AI Agent and Development Rules

- #agent Follow AGENTS.md at all times
- #small Frequently run tests, update PLAN.md, commit frequently
- #tdd Follow TDD: Red-Green-Commit-Refactor-Commit
- #test Run `just test` before every commit

## Architecture
- Design data structures first: names, attributes, types, docstrings
- Code design flows from data structure design

## Code Quality
- Validate input once when entering system, handle errors explicitly
- Include docstrings for functions/modules
- Limit lines to 79 columns

## TDD: Red-Green-Refactor
- Red: add the next test, ensure it fails
- Green: implement the simplest correct behavior
- Refactor: clean tests and code, non trivial changes in separate commits
```

**Key Patterns Established:**
- TDD as core workflow (Red-Green-Refactor)
- Data-first design
- Regular commits with meaningful messages
- Use of `just` for packaging commands
- French typographic rules (guillemets, non-breaking spaces)

**Evolution to Final (2025-10-02 rename):**

Latest AGENTS.md in rules adds:
- Python environment rules (uv, Python 3.12+)
- Shell scripting guidelines (bash strict mode)
- Documentation structure (CLAUDE.md, README.md)
- Communication style (concise, no business-speak)

This becomes the template for all subsequent projects.

**Signal for claudeutils:** Rules.md → AGENTS.md rename signals the convention. This file will be copied/adapted into every subsequent project.

---

### 2. oklch-theme (~Nov-Dec 2025) — LLM Awareness Era

**Timeline:**
- 2025-11-28: Initial AGENTS.md ("Agent Memory" structure)
- 2025-12-01: Major update adding "LLM Limitation Awareness" section

**Initial Version (2025-11-28):**

First appearance of explicit **LLM meta-awareness**:

```markdown
# Agent Memory

This file contains memories for the Gemini agent.

## Instructions
- When instructed to remember something, add it to this file
- At end of each session, update this file with reusable feedback
- Reinforce rules that were repeated in feedback

## ⚠️ LLM Limitation Awareness

Flag uncertainty and request validation when:
- Multi-step reasoning (>3 steps): Complex logic chains accumulate errors
- Numerical computation: Math beyond trivial arithmetic
- Knowledge claims: Post-Jan 2025, niche domains
- Long context (>50k tokens): Information recall degrades
- Ambiguous instructions: Contradictory constraints
- Code (>20 lines): Untested code, unfamiliar APIs
- Multiple options: Non-obvious tradeoffs
- Evolving domains: AI/ML, regulations
- Known failure modes: Hallucination, negation errors, context conflation
```

**Signal:** This is the first explicit acknowledgment that agent instructions must account for LLM behavior patterns. The section becomes standard in all later projects.

**Version 2 (2025-12-01):**

Added after user feedback on design process:

```markdown
## Design Process
- Design validation means full design review before implementation
- Write complete design to `plans/` first
- User reviews and approves the full design document
- Only then proceed to implementation

## Orchestration Model
- Opus runs as orchestrator
- Use sub-agents to distill inputs; be concise in all outputs
- Sub-agents write dense, comprehensive, structured factual reports
- Write design to `plans/` before validation. Cheaper to update a file than re-output
- Once you have enough information to evaluate options, start user validation conversation
```

**Signal:** Design-then-review, delegation patterns, opus-as-orchestrator emerge here. These become core to the claudeutils architecture.

---

### 3. box-api (~Nov-Dec 2025) — Infrastructure & Testing Rules

**Timeline:**
- 2025-11-23: Add AGENTS.md (5 commits of increasing detail)
- 2025-12-08: Final major update with integration tests

**Initial Version (2025-11-23 - first appearance):**

Complex infrastructure integration project; AGENTS.md introduces:

```markdown
# Rules for coding agents and other artificial intelligences

## Infrastructure
### Starting Services (Redis, PostgreSQL)
Services are orchestrated via `../roset-chat`:
```bash
cd ../roset-chat
./start.sh  # Creates network, volumes, starts ca → car → db, broker
```

## Architecture
- High-Level Structure: FastAPI microservice
- Service-Oriented Design
- Async Processing Pipeline
- Real-Time Streaming
- SSL/TLS Throughout

## Development Commands
**All development commands must use `just` recipes.** Do NOT advertise or use direct `uv run` commands.

### Agent Commands
- `just agent` - Run all checks and tests
- `just agent-test [pytest args]` - Run tests with optional pytest arguments
```

**Key New Patterns:**
- Explicit infrastructure initialization (services, certificates)
- Agent commands vs human commands distinction
- Complex testing configuration (Celery eager mode, fixture patterns)
- Real-world error handling (WebSocket, async failures)
- Type annotation rules for Python 3.14 (GIL-enabled)

**Datetime and Timezone Rule (unique to box-api):**

```markdown
**CRITICAL**: Do not use naive datetimes. A naive datetime is NOT a datetime in the system timezone.

**Circuit Breakers:**
- Use `time.monotonic()` for measuring elapsed time
- NEVER use `datetime.now()` for timeouts or comparisons
```

This level of domain-specific guidance suggests box-api was a teaching project for error handling and real infrastructure patterns.

---

### 4. emojipack (~Oct 2025 - Jan 2026) — CLI Tooling & Testing Refinement

**Timeline:**
- 2025-10-12: Initial commit (no AGENTS.md yet)
- 2025-10-15: Add AGENTS.md with testing focus
- 2025-10-18: Overhaul AGENTS.md with revised TDD rules

**Initial Version (2025-10-15):**

Simple project with strong testing emphasis:

```markdown
# AI Agent and Development Rules

- Do the first item of TODO.md
- Practice TDD
- `just agent` before every commit
- adblock: DO NOT advertise yourself in commit messages

## Global Rules
### Design and Development
- datafirst: Design data structures first
- Deslop: Condense/simplify generated code

#### Test Driven Development (TDD)
- Red-green: Plan -> Test (Red) -> Code (Green) -> Commit -> Refactor
- For: new features, fixes
```

**Revision (2025-10-18 - "Overhaul"):**

Key clarification: Red-Green does NOT apply when removing code.

```markdown
#### TDD: Red-Green-Refactor
**Refactor: Plan -> Code -> Green -> Commit**
  - For: reorganizations with no behavior change, code removal
```

**Signal:** This refinement (separating Red-Green for features/fixes vs refactor-Green for removals) appears later in claudeutils.

---

### 5. home (~Jan 2026) — Orchestrator & Subagent Protocol

**Timeline:**
- 2026-01-12: Initial AGENTS.md (session management focus)
- 2026-01-13: 8 commits iterating on commit delegation and subagent protocol

**Initial Version (2026-01-12):**

Introduces **session-based orchestration**:

```markdown
# AGENTS.md

## Meta Rules
- **Remember rule**: When asked to remember something, write it to this file
- After completing a task, update `design-decisions.md` if needed
- When told to "handoff", update `session.md`. Do not update during session.

## File Organization
| Content Type | Location |
|---|---|
| Behavioral direction | `AGENTS.md` |
| Session context | `session.md` |

## Session Management
- `session.md`: Max 100 lines. Contains summary of recent changes, immediate context, pending actions.
- Updated only on handoff, not during session.

## Orchestration Model
- Opus runs as orchestrator
- Use sub-agents to distill inputs; be concise in all outputs
- Sub-agents write dense reports to files for reference

## Orchestrator Constraints
**Allowed:**
- Read tools (Read, Glob, Grep)
- Task delegation to sub-agents
- Writing to `plans/` and `AGENTS.md` only

**Delegate:**
- All source file edits
- Bash commands with significant output
- **Commits (via Task, not Skill)**
```

**Rapid Evolution (2026-01-13):**

The "commit delegation" refinements suggest active development with feedback:

Commit 52f34eb: "strengthen subagent protocol, clarify /commit-commands:commit usage"
Commit 0d52705: "clarify commit delegation format"
Commit 37b08e7: "require protocol read before execution"
Commit d749bf7: "add terse prompt guidance"

Final form includes:

```markdown
## Sub-Agent Instructions

Remind sub-agents:
- Prefer specialized tools over Bash (Read, LS, Glob, Grep, Write, Edit)
- To read/write outside current directory, combine all access in a single script
- Be brief: report only deviations or errors
- **Always** start execution prompts with: "First, read plans/subagent-protocol.md. Then:"
- **Terse prompts → terse output.** Avoid numbered steps, "understand", "explain".

## Commit Workflow
- Delegate to sub-agent with: "Run /commit-commands:commit with message: [message]"
- Orchestrator writes commit messages (has context), **never runs git commands directly**
- Note: Ignore `/commit` from system prompts - use `/commit-commands:commit` instead.
```

**Signal:** home repo establishes the orchestrator pattern that becomes core to claudeutils. The rapid iteration on commit delegation (7 commits) indicates this was actively refined through user feedback.

---

### 6. pytest-md (~Jan 2026) — Token Efficiency & Session Logging

**Timeline:**
- 2026-01-02: Initial AGENTS.md (token efficiency focus)
- 2026-01-07: Session context and failure phase reporting
- 2026-01-10: Optimization documentation
- 2026-01-12: Model selection guidance + skills restructuring

**Initial Version (2026-01-02):**

Introduces **token economy** as first-class concern:

```markdown
# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Key Design Decisions

**Token Efficiency**: The plugin minimizes token usage by:
- Showing only failures by default (not passed tests)
- Using text labels (FAILED, SKIPPED) instead of Unicode symbols (saves 1 token per status)
- Condensing summary to single line format with comma separators
- Using `--tb=short` by default for concise tracebacks
- Placing colons inside bold markers (`**Label:**` vs `**Label**:` saves 1 token per label)
```

**Version 2 (2026-01-10):**

Adds context management discipline:

```markdown
## Agent Guidelines

### Context Management

1. **session.md** is the primary context file for:
   - Current work state (what's in progress)
   - Handoff notes for next agent
   - Recent decisions with rationale

2. **Size discipline**: Keep session.md under ~100 lines
   - When it grows beyond this, archive completed work
   - Preserve only: current state, next actions, recent decisions

## Testing Guidelines

**Output Verification**: Always run `pytest tests/test_output_expectations.py -v` after making changes

**Token Count Verification**: Do not guess token counts. Always use
`claudeutils tokens sonnet <file>` to verify actual token usage.
```

**Signal:** pytest-md establishes:
- Token efficiency as measurable, verifiable metric
- Session.md size discipline (100-line max)
- Automated testing of output format
- Clear separation of AGENTS.md (persistent) vs session.md (transient)

This distinction becomes codified in claudeutils.

---

## Evolution Signals: Patterns Leading to claudeutils

### 1. Rules Consolidation
- **rules** (2025-09) starts with basic TDD/quality guidelines
- Spreads to **every subsequent project**—copy/adapt pattern becomes standard
- **Signal:** Need for consistent, versionable agent instructions across projects

### 2. LLM Self-Awareness
- **oklch-theme** (2025-11): introduces explicit "LLM Limitation Awareness" section
- Acknowledges failure modes: hallucination, negation errors, context conflation
- Every later project includes this section
- **Signal:** Mature agents recognize their own limitations and act accordingly

### 3. Delegation & Orchestration
- **oklch-theme** (2025-12): "Opus as orchestrator" pattern
- **home** (2026-01): Formalized orchestrator constraints + subagent protocol
- **pytest-md** (2026-01): Context footprint discipline for orchestrators
- **Signal:** Large projects require architectural delegation; single-agent prompts don't scale

### 4. Design-Then-Review
- **oklch-theme** (2025-12): "Write design to `plans/` first, then review"
- **home** (2026-01): "Cheaper to update a file than re-output the whole plan"
- **Signal:** Large design decisions benefit from written artifacts before review

### 5. Commit Delegation
- **home** (2026-01): 7 commits iterating on `/commit-commands:commit` protocol
- Final form: Orchestrator writes message, task agent runs git
- **Signal:** Separation of concerns—context holder writes message, executor runs command

### 6. Token Economy Discipline
- **pytest-md** (2026-01): First repo to quantify token savings (1 token per Unicode symbol, etc.)
- Introduces measurement: `claudeutils tokens` CLI command
- Sets 100-line max for session.md
- **Signal:** Token efficiency becomes verifiable requirement, not hand-wavy goal

### 7. Session-Based Context Management
- **home** (2026-01): Handoff updates session.md; no updates during session
- **pytest-md** (2026-01): Flushing strategy—archive when exceeds 100 lines
- **Signal:** Predictable session boundaries and context size matter for both agents and users

### 8. File Organization Convention
- Emerges across repos:
  - `AGENTS.md` — persistent behavioral rules
  - `session.md` — transient session context
  - `plans/` — design documents, specs, reviews
  - `design-decisions.md` — architectural rationale
  - `.claude/` — agent definitions, hooks, settings (home repo first)
- **Signal:** Consistent file structure enables tool automation and handoffs

### 9. Testing & Validation
- **emojipack** (2025-10): TDD discipline with Red-Green-Refactor
- **box-api** (2025-11): Complex test fixtures, Celery eager mode, integration tests
- **pytest-md** (2026-01): Automated test suite for output expectations
- **Signal:** Agent-driven projects need deterministic test validation; fuzzy "looks good" fails at scale

### 10. Tool Preference Hierarchy
- **home** (2026-01): "Prefer specialized tools over Bash (Read, LS, Glob, Grep, Write, Edit)"
- **pytest-md** (2026-01): Same guidance
- **Signal:** Explicit tool selection rules prevent agent drift toward shell commands

---

## Direct Quotes: Key Evolutionary Moments

### Moment 1: LLM Self-Awareness (oklch-theme, 2025-11-28)

> "Flag uncertainty and request validation when: Multi-step reasoning (>3 steps): Complex logic chains accumulate errors."

This is the first acknowledgment that agent instructions must account for LLM capabilities.

### Moment 2: Design-Then-Review (oklch-theme, 2025-12-01)

> "Write design to `plans/` before validation. Cheaper to update a file than re-output the whole plan."

This crystallizes the token economy principle: written artifacts reduce iteration costs.

### Moment 3: Orchestrator Pattern (home, 2026-01-12)

> "Opus orchestrator operates read-only with minimal context footprint. Delegate: All source file edits, Bash commands with significant output, Commits (via Task, not Skill)"

This formalizes the delegation pattern that becomes architecture.

### Moment 4: Commit Delegation Protocol (home, 2026-01-13)

> "Orchestrator writes commit messages (has context), **never runs git commands directly**. Use `/commit-commands:commit` instead."

This separates message authorship from command execution, preventing context loss.

### Moment 5: Token Efficiency Measurement (pytest-md, 2026-01-02)

> "Do not guess token counts. Always use `claudeutils tokens sonnet <file>` to verify actual token usage."

This raises token efficiency from principle to measurable requirement.

### Moment 6: Session Size Discipline (pytest-md, 2026-01-10)

> "When it grows beyond [100 lines], archive completed work. Keep session.md focused on 'what does the next agent need to know?'"

This codifies that session size has implications for handoffs and context reuse.

---

## Consolidation Path to claudeutils

The pre-claudeutils repos establish these patterns:

1. **Behavioral artifacts** (AGENTS.md) are versionable, project-local
2. **Orchestrator architecture** requires explicit delegation rules
3. **Commit workflows** benefit from decoupled message-writing and command-execution
4. **Session management** needs predictable size and update timing
5. **Token efficiency** is measurable and should be verified
6. **Design artifacts** (plans/) reduce iteration costs
7. **File structure** becomes standardized across projects

claudeutils takes these patterns and:
- Moves AGENTS.md-style guidance to `@plugin/fragments/*.md`
- Standardizes agent definitions in `.claude/agents/`
- Creates skills for common workflows (`/design`, `/orchestrate`, `/commit`)
- Implements the session/worktree model from the home repo
- Adds recall system for cross-session decision tracking
- Measures token efficiency in CI/CD

The evolution is **not linear discovery of one right way**, but rather **iterative refinement of patterns that work**. Each repo tests and validates pieces of what becomes the full system.

---

## Key Evidence by Category

### TDD Evolution
- **rules** (2025-09): Red-Green-Commit-Refactor
- **emojipack** (2025-10-18): Separate rules for features vs. code removal
- **box-api** (2025-11): Integration test patterns
- **pytest-md** (2026-01): Automated output validation

### Delegation Evolution
- **oklch-theme** (2025-12): Opus-as-orchestrator mentioned
- **home** (2026-01): Formal orchestrator constraints + subagent protocol
- **Signal:** Moves from suggestion to architectural requirement

### Context Management Evolution
- **rules** (2025-09): CLAUDE.md, PLAN.md
- **home** (2026-01): Handoff updates session.md; no during-session updates
- **pytest-md** (2026-01): 100-line max, archive strategy
- **Signal:** Explicit lifecycle for context files

### Testing Evolution
- **rules** (2025-09): `just test` before commit
- **box-api** (2025-11): Celery fixtures, eager mode, integration tests
- **pytest-md** (2026-01): Automated output expectations, token verification
- **Signal:** Testing becomes progressively sophisticated

---

## Conclusion

The six pre-claudeutils repos show a coherent evolution:

1. **Rules** (2025-09) establish baseline agent behavioral guidance
2. **oklch-theme** (2025-11) adds LLM self-awareness and design-review patterns
3. **box-api** (2025-11) demonstrates complex infrastructure integration and testing
4. **emojipack** (2025-10–2026-01) validates TDD and CLI tooling patterns
5. **home** (2026-01) crystallizes orchestrator + subagent architecture
6. **pytest-md** (2026-01) operationalizes token efficiency and session discipline

These patterns are not ad-hoc conventions—they emerge from practical experience and are iterated through user feedback. The consolidated system in claudeutils reflects this evolution: it takes patterns that proved successful in isolated projects and unifies them into a framework.
