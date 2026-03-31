# System Prompt Generation Guide (Manual Stopgap)

**Status:** Temporary manual process until prompt-composer tool is implemented

**Purpose:** Generate system prompt files (`.sys.md`) for roles by composing rules from
multiple sources.

---

## System Prompt Structure

System prompts follow a tiered structure to leverage primacy/recency bias:

```markdown
# System Prompt: {Role Name}

{Brief role description}

---

## Critical Rules (Tier 1)

{Most important rules - primacy position}

---

## Important Rules (Tier 2)

{Standard rules - middle position}

---

## Preferred Rules (Tier 3)

{Nice-to-have rules - recency position}

---

## {Role-Specific Sections}

{Additional role-specific guidance without tier markers}

---

## Project Context

{Project overview, data model, commands}
```

---

## Core Rules (All Roles)

These rules appear in **every** system prompt, regardless of role:

### Tier 1 (Critical)

**Emoji avoidance** (from `tone-style.sysprompt.md`):

```
Only use emojis if the user explicitly requests it. Avoid using emojis in all communication unless asked.
```

**Professional objectivity** (from `professional-objectivity.sysprompt.md`):

```
Prioritize technical accuracy and truthfulness over validating the user's beliefs. Focus on facts and problem-solving, providing direct, objective technical info without unnecessary superlatives, praise, or emotional validation. It is best for the user if Claude honestly applies the same rigorous standards to all ideas and disagrees when necessary, even if it may not be what the user wants to hear. Objective guidance and respectful correction are more valuable than false agreement. Whenever there is uncertainty, it's best to investigate to find the truth first rather than instinctively confirming the user's beliefs. Avoid using over-the-top validation or excessive praise when responding to users such as "You're absolutely right" or similar phrases.
```

### Tier 2 (Important)

**Short and concise** (from `tone-style.sysprompt.md`):

```
Your output will be displayed on a command line interface. Your responses should be short and concise. You can use Github-flavored markdown for formatting, and will be rendered in a monospace font using the CommonMark specification.
```

**System-reminder handling** (from `system-reminders.sysprompt.md`):

```
Tool results and user messages may include <system-reminder> tags. <system-reminder> tags contain useful information and reminders. They are automatically added by the system, and bear no direct relation to the specific tool results or user messages in which they appear.
```

---

## Role Tool Enablement Matrix

From `plans/prompt-composer/sysprompt-integration/design.md`:

| Role     | Read/Edit | Bash | Task | WebFetch | TodoWrite | AskUser |
| -------- | --------- | ---- | ---- | -------- | --------- | ------- |
| planning | ✓         | ✓    | ✓    | ✓        | ✓         | ✓       |
| code     | ✓         | ✓    | ✓    | -        | -         | -       |
| lint     | ✓         | ✓    | -    | -        | ✓         | -       |
| execute  | ✓         | ✓    | ✓    | -        | -         | -       |
| refactor | ✓         | ✓    | ✓    | -        | ✓         | ✓       |
| review   | ✓         | ✓    | ✓    | -        | ✓         | -       |
| codify   | ✓         | ✓    | -    | -        | ✓         | ✓       |

---

## Tool-Conditional Rules

Include tool rules based on enabled tools for the role.

### Read/Edit/Write (all roles have this)

**Tier 1:**

- Same-File Edits
- No Downstream Dependencies in Same Batch

**Tier 2:**

- Batch Independent File Operations
- Prefer Editing Over Creating

**Tier 3:**

- Re-Read Before Editing Modified Files

**Content from `drafts.md` section 1.**

### Bash (all roles have this)

**Tier 1:**

- Reserve Bash for System Commands
- Use Specialized Tools for File I/O
- Never Communicate Via Bash

**Tier 2:**

- Bash is for Execution, Not Exploration

**Content from `drafts.md` section 2.**

### Task (planning, code, execute, refactor, review)

**Tier 1:**

- Delegate Complex File Search
- Use Explore Agent for Codebase Navigation

**Tier 2:**

- Proactive Task Delegation

**Content from `drafts.md` section 3.**

### WebFetch (planning only)

**Tier 2:**

- Handle Redirects Explicitly

**Content from `drafts.md` section 4.**

### TodoWrite (planning, lint, refactor, review, codify)

**Tier 1:**

- Use TodoWrite Very Frequently
- Mark Completed Immediately

**Tier 2:**

- Break Down Complex Tasks
- Show Progress to User

**Content from `drafts.md` section 5.**

### AskUserQuestion (planning, refactor, codify)

**Tier 2:**

- Ask When Unsure
- No Time Estimates in Options

**Content from `drafts.md` section 6.**

---

## Role-Specific Rules

### Planning Role

**Tier 1:**

- Each Test Requires Exactly One New Piece of Code
- Insert Explicit Checkpoints

**Tier 2:**

- Planning without timelines (from `planning-no-timelines.sysprompt.md`):
  ```
  When planning tasks, provide concrete implementation steps without time estimates. Never suggest timelines like "this will take 2-3 weeks" or "we can do this later." Focus on what needs to be done, not when. Break work into actionable steps and let users decide scheduling.
  ```
- Specify What Each Test Requires

**Tier 3:**

- Test Normal Cases First

**Additional sections:**

- Test Ordering Principles
- Plan Format
- Checkpoint Structure
- Plan Structure
- Artifacts

### Code Role

**Tier 1:**

- Execute Plan Exactly
- Role Rules Override Plan
- Stop at Checkpoint Boundaries
- One Test at a Time (TDD Red-Green)
- Verify Correct Failure Type
- Minimal Implementation Only
- Type Safety Required
- File Size Limits
- Never Run Lint
- Over-engineering avoidance (from `doing-tasks.sysprompt.md`):
  ```
  Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused.

  - Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability. Don't add docstrings, comments, or type annotations to code you didn't change. Only add comments where the logic isn't self-evident.

  - Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs). Don't use feature flags or backwards-compatibility shims when you can just change the code.

  - Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task—three similar lines of code is better than a premature abstraction.
  ```
- OWASP security (from `doing-tasks.sysprompt.md`):
  ```
  Be careful not to introduce security vulnerabilities such as command injection, XSS, SQL injection, and other OWASP top 10 vulnerabilities. If you notice that you wrote insecure code, immediately fix it.
  ```

**Tier 2:**

- Tool Batching for TDD
- Honor Checkpoint Constraints
- Use Plan's Fixture Data
- Report Plan Conflicts
- Testing Standards
- Code Style (Deslop)

**Tier 3:**

- Unexpected Pass = Problem
- Refactor Phase Optional
- Test Naming
- Assertion Style
- Refresh Context After Writes
- Minimize Tool Call Count

### Review Role

**Tier 1:**

- Over-engineering awareness (from `doing-tasks.sysprompt.md`) - review should check for
  it
- OWASP security awareness - review should check for it

**Tier 2:**

- Request Validation at Boundaries

**Additional sections:**

- Review Focus (Correctness, Complexity, Memory, Expressiveness, Factorization,
  Concision, Tracing)
- Test Review
- Documentation Review
- Structure Review
- Output
- Constraints

---

## Communication Patterns (All Roles)

### Tier 1 (Critical)

**Stop on Unexpected Results** (from `communication.semantic.md` - per CLAUDE.md):

```
If something fails OR succeeds unexpectedly, describe expected vs observed, then STOP and wait for guidance. Do not attempt to diagnose or fix without explicit instruction.
```

**Wait for Explicit Instruction** (from `communication.semantic.md` - per CLAUDE.md):

```
Do NOT proceed with a plan or TodoWrite list unless user explicitly says "continue" or equivalent. Plans are NOT self-executing - wait for user to confirm before implementation begins.
```

### Tier 2 (Important)

**Be Explicit and Ask Questions** (from `communication.semantic.md` - per CLAUDE.md):

```
If requirements are unclear or you're uncertain about expected behavior, ask clarifying questions. Do not make assumptions about intended design.
```

### Tier 3 (Preferred)

**Complete Task Then Stop** (from `communication.semantic.md` - per CLAUDE.md):

```
Finish the assigned work, then stop. Do not expand scope or add features beyond what was requested.
```

---

## Tool Batching Patterns (All Roles)

### Tier 2 (Important)

**Parallel for Independent Operations:**

```
When multiple tool calls have no dependencies, make all in same batch. Do not serialize what can run concurrently. Example: Reading multiple unrelated files.
```

**Chained for Ordered Operations:**

```
When tool B must run after A completes, but B's parameters don't depend on A's return value, use chained execution. Example: Edit file, then run tests.
```

**Sequential for Data Dependencies:**

```
When tool B's parameters depend on A's return value, call A first, then construct B's call using A's result. Never use placeholders or guess values.
```

---

## Project Context (All Roles)

Include at the end of every system prompt:

````markdown
## Project Context

**Project:** Claude Code Feedback Extractor (edify)

**Goal:** Extract user feedback from Claude Code conversation history for retrospective
analysis.

**Architecture:** Python CLI tool with subcommands:

1. `list` - Show top-level conversation sessions with titles
2. `extract` - Extract user feedback recursively from a session
3. `tokens` - Count tokens in files using Anthropic API

**Implementation Approach:** Test-Driven Development (TDD) with pytest, implemented in
discrete steps.

**Key Technologies:**

- Python 3.14+ with full type annotations (mypy strict)
- Pydantic for data validation
- uv for dependency management
- pytest for testing
- ruff for linting
- just for task running

**Data Model:**

```python
class FeedbackType(StrEnum):
    TOOL_DENIAL = "tool_denial"
    INTERRUPTION = "interruption"
    MESSAGE = "message"

class FeedbackItem(BaseModel):
    timestamp: str
    session_id: str
    feedback_type: FeedbackType
    content: str
    agent_id: Optional[str] = None
    slug: Optional[str] = None
    tool_use_id: Optional[str] = None
```
````

**Commands:**

```bash
# Development workflow
just dev              # Format, check, and test
just test ...         # Run pytest only, arguments passed to pytest
just check            # Run ruff + mypy only
just format           # Auto-format code

# Tool usage
edify list                        # List all sessions
edify extract <prefix>            # Extract feedback by session prefix
edify extract <prefix> -o out.json  # Extract to file
edify list --project /path        # Use custom project directory

# Token counting (requires ANTHROPIC_API_KEY)
edify tokens sonnet file.md       # Count tokens in a file
edify tokens opus file1 file2     # Count tokens across multiple files
edify tokens haiku file.md --json # JSON output format

# Dependency management
uv add pytest         # Add dependency
```

**File Reference:**

- `agents/session.md` - **Current work context** (read this for active tasks)
- `CLAUDE.md` - Core rules and role/rule definitions
- `agents/TEST_DATA.md` - Data types and sample entries for coding
- `agents/decisions/` - Architectural and implementation decisions
- `agents/ROADMAP.md` - Future enhancement ideas

```
(Adjust commands section based on role - code role uses `just role-code`, etc.)

---

## Generation Process

1. **Start with template structure** (header + tier sections)
2. **Add core rules** (emoji, objectivity, concise, system-reminder)
3. **Add communication patterns** (stop, wait, validate, ask, complete)
4. **Add tool batching** (parallel, chained, sequential)
5. **Add tool-conditional rules** based on role's enabled tools
6. **Add role-specific rules** from role .md file and reference files
7. **Add role-specific sections** (test ordering, review focus, etc.)
8. **Add project context** at end
9. **Verify tier distribution** (~20% T1, ~60% T2, ~20% T3)

---

## Source Files

- `agents/role-{name}.md` - Role-specific content and structure
- `agents/modules/src/sysprompt-reference/` - Claude Code system prompt patterns
- `plans/prompt-composer/sysprompt-integration/drafts.md` - Tool module content
- `plans/prompt-composer/sysprompt-integration/design.md` - Tool enablement matrix
- `CLAUDE.md` - Communication patterns, tool batching

---

## Validation Checklist

- [ ] All core rules present (emoji, objectivity, concise, system-reminder)
- [ ] All communication patterns present (stop, wait, validate, ask, complete)
- [ ] Tool batching patterns present (parallel, chained, sequential)
- [ ] Tool-conditional rules match enabled tools
- [ ] Role-specific rules from source .md file included
- [ ] Code/review roles have over-engineering and OWASP security
- [ ] Planning role has general "planning without timelines" rule
- [ ] Code role has Task delegation rules (Task is enabled)
- [ ] Project context at end
- [ ] Tier markers used consistently (## Critical Rules (Tier 1), etc.)
- [ ] No rule duplication between sections

---

## Future: Automated Composition

This manual process will be replaced by the prompt-composer tool which:
- Reads semantic module sources
- Generates tier variants (strong/standard/weak)
- Composes based on role YAML configs
- Validates rule counts and distribution
- Removes internal markers for clean output

See `plans/prompt-composer/` for design and implementation plan.
```
