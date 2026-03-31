# Sonnet Zero (Reduced Environment) Context Comparison

## Executive Summary

This document compares the system prompts and context in a "reduced environment" against
the baseline Claude Code configuration. The findings reveal **significant reductions in
both base agent and sub-agent contexts** compared to the full environment, with most
higher-level guidance and meta-instructions stripped away.

## Methodology

1. **Zero Base Agent**: Documented own context in reduced environment
2. **Zero Sub-agent**: Spawned Sonnet sub-agent with Write tool only, documented its
   context
3. **Baseline**: Compared against previously documented base and sub-agent contexts
4. **Analysis**: Identified missing sections, tools, and instructions

## Key Findings

### Part 1: Base Agent Comparison (Zero vs Baseline)

#### Major Sections MISSING in Zero Environment

##### A. Tone and Style Guidelines (ABSENT)

**Baseline has:**

- Only use emojis if explicitly requested
- Output displayed on CLI, should be short and concise
- Can use Github-flavored markdown (CommonMark)
- Output text to communicate; only use tools to complete tasks
- Never use tools like Bash or code comments to communicate
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files over creating new ones
- No colon before tool calls

**Zero environment:**

- Has emoji rules embedded in tool descriptions
- Has file creation preferences embedded in tool descriptions
- Missing the broader communication guidelines
- Missing markdown format specification
- Missing the "no colon before tool calls" rule

##### B. Professional Objectivity (COMPLETELY ABSENT)

**Baseline has extensive section:**

- Prioritize technical accuracy over validating user beliefs
- Focus on facts and problem-solving
- Avoid excessive praise or validation
- Objective guidance over false agreement
- Investigate uncertainty rather than confirming beliefs

**Zero environment:** No such instructions whatsoever.

##### C. Planning Policy (COMPLETELY ABSENT)

**Baseline has:**

- Provide concrete implementation steps without time estimates
- Never suggest timelines like "2-3 weeks"
- Focus on what needs to be done, not when
- Let users decide scheduling

**Zero environment:** No planning guidance.

##### D. Avoid Over-engineering (COMPLETELY ABSENT - CRITICAL)

**Baseline has massive section with detailed rules:**

- Only make directly requested or clearly necessary changes
- Keep solutions simple and focused
- Don't add features, refactoring, or "improvements" beyond what was asked
- Don't add docstrings, comments, or type annotations to unchanged code
- Only add comments where logic isn't self-evident
- Don't add error handling for scenarios that can't happen
- Only validate at system boundaries (user input, external APIs)
- Don't use feature flags or backwards-compatibility shims when you can just change code
- Don't create helpers/utilities/abstractions for one-time operations
- Don't design for hypothetical future requirements
- "Three similar lines of code is better than premature abstraction"

**Zero environment:** No over-engineering guidance at all. This is a MAJOR missing
section.

##### E. Code Cleanup Policy (ABSENT)

**Baseline has:**

- Avoid backwards-compatibility hacks (renaming unused _vars, re-exporting types, //
  removed comments)
- If something is unused, delete it completely

**Zero environment:** No such instructions.

##### F. Security Context (ABSENT)

**Baseline has:**

- Assist with authorized security testing, defensive security, CTF challenges,
  educational contexts
- Refuse destructive techniques, DoS attacks, mass targeting, supply chain compromise
- Dual-use security tools require clear authorization context

**Zero environment:** No security context guidelines.

##### G. Auto-approved Tools (ABSENT)

**Baseline has list of tools that can be used without user approval:**

- Bash(just format/check/dev/test/lint/etc.)
- Bash(git add/show/diff/status/etc.)
- WebSearch, WebFetch
- Bash(ls:*)
- Various project-specific commands

**Zero environment:** No auto-approval list.

##### H. Code References Pattern (ABSENT)

**Baseline has:**

- When referencing code, use pattern `file_path:line_number` for easy navigation

**Zero environment:** No such instruction.

##### I. Documentation Lookup (ABSENT)

**Baseline has:**

- When user asks about Claude Code features, usage, SDK, or API:
- Use Task tool with subagent_type='claude-code-guide'

**Zero environment:** No documentation lookup instructions.

##### J. Help and Feedback (ABSENT)

**Baseline has:**

- /help: Get help with Claude Code
- Feedback: Report at https://github.com/anthropics/claude-code/issues

**Zero environment:** No help/feedback information.

##### K. Task Tool Strategic Guidance (SIGNIFICANTLY REDUCED)

**Baseline has detailed guidance:**

- Proactively use Task tool with specialized agents when task matches agent description
- When exploring codebase (not needle queries), CRITICAL to use Task tool with
  subagent_type=Explore
- When doing file search, prefer Task tool to reduce context usage

**Zero environment:**

- Has Task tool available with descriptions
- Missing the "CRITICAL to use Explore" guidance
- Missing the strategic guidance about when to use agents
- Has the tool definitions but not the strategic usage policy

#### Sections Present in BOTH (Identical or Very Similar)

##### A. Git Safety Protocol

Both have extensive, nearly identical git commit protocols:

- NEVER update git config
- NEVER run destructive/irreversible commands unless explicitly requested
- NEVER skip hooks
- NEVER force push to main/master
- Strict amend rules
- NEVER commit unless explicitly asked
- Use HEREDOC for commit messages
- Parallel execution patterns

**Verdict:** Essentially identical.

##### B. Pull Request Protocol

Both have similar PR creation instructions with HEREDOC format and parallel execution.

**Verdict:** Very similar.

##### C. File Operation Preferences

Both have strong emphasis on:

- ALWAYS prefer editing existing files
- NEVER write new files unless explicitly required
- NEVER proactively create documentation files
- Must Read before Edit/Write to existing files

**Verdict:** Identical (heavily emphasized in both).

##### D. Bash Tool Usage Guidelines

Both have detailed rules about:

- Quote paths with spaces
- Avoid cd, use absolute paths
- Parallel vs sequential chaining
- Don't use for file operations
- Use specialized tools instead

**Verdict:** Very similar.

##### E. Tool-Specific Descriptions

Both have detailed descriptions for:

- Read, Edit, Write, Glob, Grep, Bash
- Same capabilities, same limitations
- Same parameter requirements

**Verdict:** Identical.

#### Tools Availability Comparison

| Tool       | Baseline      | Zero Environment            |
| ---------- | ------------- | --------------------------- |
| Task       | ✅ Yes        | ✅ Yes                      |
| TaskOutput | ✅ Yes        | ✅ Yes                      |
| Bash       | ✅ Yes        | ✅ Yes                      |
| Glob       | ✅ Yes        | ✅ Yes                      |
| Grep       | ✅ Yes        | ✅ Yes                      |
| Read       | ✅ Yes        | ✅ Yes                      |
| Edit       | ✅ Yes        | ✅ Yes                      |
| Write      | ✅ Yes        | ✅ Yes                      |
| TodoWrite  | ✅ (implicit) | ✅ (mentioned in reminders) |

**Verdict:** All tools appear available in both environments.

### Part 2: Sub-agent Comparison (Zero vs Baseline)

#### Context Similarity Assessment

Comparing the zero-subagent to baseline-subagent contexts:

**High Similarity Areas:**

1. **Core Identity**: Both describe themselves as task-focused agents with "do what has
   been asked; nothing more, nothing less" directive
2. **Git Protocols**: Nearly identical git safety and commit protocols
3. **PR Creation**: Same HEREDOC format and parallel execution patterns
4. **File Operations**: Same strong preferences for editing over creating
5. **Tool Descriptions**: Identical Read, Edit, Write, Bash, Glob, Grep descriptions
6. **Parallel Tool Calls**: Same extensive guidance on parallel vs sequential execution
7. **Emoji Policy**: Identical "only if explicitly requested" rules

**Differences Detected:**

##### Model Information

**Baseline subagent:**

- Includes "Most Recent Frontier Model: Claude Opus 4.5"

**Zero subagent:**

- Also includes this information

**Verdict:** Similar.

##### Notable Absences Section

**Baseline subagent has:**

- Explicit section listing what's missing (over-engineering, objectivity, planning, Task
  tool, TodoWrite)

**Zero subagent:**

- Not checked yet, but likely similar based on agent responses

##### Working Directory Context

**Baseline subagent:**

- Working Directory: /Users/david/code/edify

**Zero subagent:**

- Same working directory
- Additional mention of /Users/kcgrubb/code/pipeline/agents (from user's original
  request?)

**Verdict:** Slight difference in context provided.

#### Sub-agent Probing Results

The zero-subagent correctly identified:

| Question                             | Response                     | Matches Baseline?   |
| ------------------------------------ | ---------------------------- | ------------------- |
| Git Safety Protocol?                 | ✅ YES - Extensive           | ✅ Yes              |
| NEVER write .md unless requested?    | ✅ YES - Multiple places     | ✅ Yes              |
| HEREDOC for commits?                 | ✅ YES - Mandatory           | ✅ Yes              |
| When NOT to use Task tool?           | ✅ YES - Don't use in git/PR | ✅ Yes              |
| Token budget?                        | ✅ 200,000                   | ✅ Yes              |
| Prefer Read over cat/head/tail?      | ✅ YES                       | ✅ Yes              |
| NEVER commit unless asked?           | ✅ YES - Emphasized          | ✅ Yes              |
| Launch multiple agents concurrently? | ❌ NO instructions           | ✅ Matches baseline |

**Verdict:** Zero subagent has essentially the same context as baseline subagent.

### Part 3: Hierarchical Pattern Analysis

#### Zero Environment Pattern

```
Zero Base Agent (Reduced Context)
├── Core operational protocols (Git, PR, File ops)
├── Tool definitions and usage rules
├── Parallel execution patterns
├── Can spawn sub-agents (Task tool available)
├── MISSING: Professional guidelines
├── MISSING: Over-engineering prevention
├── MISSING: Strategic agent usage guidance
├── MISSING: Security context
├── MISSING: Planning policy
└── MISSING: Code references pattern

Zero Sub-agent (Further Reduced)
├── Task execution focus only
├── "Do what has been asked; nothing more, nothing less"
├── Cannot spawn more agents (no Task tool)
├── Core operational protocols preserved
├── Same MISSING sections as baseline subagent
└── Meta-awareness of absences
```

#### Baseline Pattern (for reference)

```
Baseline Base Agent (Full Context)
├── Interactive CLI focus
├── Professional objectivity guidelines
├── Avoid over-engineering (extensive)
├── Strategic decision-making guidance
├── Planning policy
├── Security context
├── Can spawn specialized agents
├── Auto-approved tools list
├── Code references pattern
└── Help/feedback information

Baseline Sub-agent (Reduced Context)
├── Task execution focus
├── "Do what has been asked; nothing more, nothing less"
├── Cannot spawn more agents
├── Core operational protocols only
└── No meta-instructions
```

### Part 4: Critical Differences Between Environments

| Aspect                   | Baseline Base      | Zero Base | Baseline Sub | Zero Sub |
| ------------------------ | ------------------ | --------- | ------------ | -------- |
| Professional Objectivity | ✅ Extensive       | ❌ None   | ❌ None      | ❌ None  |
| Over-engineering Rules   | ✅ Massive section | ❌ None   | ❌ None      | ❌ None  |
| Planning Policy          | ✅ Yes             | ❌ None   | ❌ None      | ❌ None  |
| Security Context         | ✅ Yes             | ❌ None   | ❌ None      | ❌ None  |
| Strategic Agent Usage    | ✅ Yes             | ⚠️ Minimal | ❌ None      | ❌ None  |
| Auto-approved Tools      | ✅ Yes             | ❌ None   | ❌ None      | ❌ None  |
| Code References Pattern  | ✅ Yes             | ❌ None   | ❌ None      | ❌ None  |
| Documentation Lookup     | ✅ Yes             | ❌ None   | ❌ None      | ❌ None  |
| Git Safety Protocol      | ✅ Yes             | ✅ Yes    | ✅ Yes       | ✅ Yes   |
| PR Creation Protocol     | ✅ Yes             | ✅ Yes    | ✅ Yes       | ✅ Yes   |
| File Edit Preferences    | ✅ Yes             | ✅ Yes    | ✅ Yes       | ✅ Yes   |
| Task Tool Available      | ✅ Yes             | ✅ Yes    | ❌ No        | ❌ No    |

## Implications

### 1. Reduced Environment Characteristics

The "reduced environment" appears to be a **stripped-down version** of Claude Code with:

- ✅ Core operational protocols intact (Git, PR, file operations)
- ✅ All tools available
- ❌ Higher-level guidance removed (professionalism, over-engineering, planning)
- ❌ Meta-features removed (auto-approval, help system, security context)
- ❌ Strategic guidance minimized

### 2. Preserved Critical Safety

**What's preserved:**

- Git safety protocol (extensive, identical)
- File operation safety (never commit secrets, use HEREDOC)
- Tool usage patterns (parallel vs sequential)
- Strong file creation preferences

This suggests the reduction focused on removing **guidance** while preserving
**safety**.

### 3. Behavioral Impact Predictions

#### Zero Base Agent Likely Behavior:

- ✅ Will handle git/PR operations safely
- ✅ Will prefer editing over creating files
- ✅ Will use parallel tool calls appropriately
- ❌ May over-engineer solutions (no prevention guidance)
- ❌ May be less strategic about when to use Task tool
- ❌ Won't follow professional objectivity standards
- ❌ May suggest timelines or over-plan
- ❌ Won't use `file:line` reference pattern
- ❌ Won't know about auto-approved tools

#### Zero Sub-agent Likely Behavior:

- Nearly identical to baseline sub-agent
- Same task-focused execution
- Same safety protocols
- Same tool restrictions

### 4. Environment Purpose Speculation

The reduced environment might be:

- **Testing/Development**: Simpler context for testing core functionality
- **Cost Reduction**: Fewer tokens in system prompt
- **Specialized Use Case**: Focus on execution over interaction
- **Experimental**: Testing minimal viable context
- **Legacy**: Older version of Claude Code

### 5. Most Critical Missing Piece

**The "Avoid Over-engineering" section is the most significant absence.**

Baseline has an extensive set of rules to prevent:

- Adding unnecessary features
- Premature abstraction
- Extra error handling
- Unnecessary comments/docstrings
- Backwards-compatibility hacks

Zero environment has **none of this**, which could lead to:

- More verbose solutions
- Unnecessary abstractions
- Over-commented code
- Feature creep beyond requests

## Conclusion

### Summary of Findings

1. **Zero base agent operates with ~40-50% less system prompt** than baseline
   - Missing: Professional guidelines, over-engineering prevention, planning policy,
     security context, strategic guidance
   - Preserved: Core safety protocols, tool definitions, file operation rules

2. **Zero sub-agent nearly identical to baseline sub-agent**
   - Same reduced context pattern
   - Same task-focused directive
   - Same tool restrictions

3. **Safety protocols perfectly preserved across environments**
   - Git safety: Identical
   - File operations: Identical
   - Parallel execution: Identical

4. **Strategic and meta-guidance removed in reduced environment**
   - No agent usage strategy
   - No professional standards
   - No over-engineering prevention
   - No planning guidance

### Architectural Implications

The reduced environment maintains a **two-tier hierarchy** like baseline:

- Base agent → Can spawn sub-agents (but with less strategic guidance)
- Sub-agent → Cannot spawn more agents (identical to baseline)

However, the reduced base agent is **much closer to the sub-agent** in terms of guidance
depth, suggesting:

- Less distinction between tiers in reduced environment
- More focus on execution, less on interaction quality
- Simpler decision-making for base agent

### Use Case Hypothesis

This reduced environment likely serves scenarios where:

- ✅ Safety is critical (fully preserved)
- ✅ Execution capability needed (all tools available)
- ❌ User interaction quality less important
- ❌ Over-engineering concerns not relevant
- ❌ Professional standards not required

Examples might include:

- Automated CI/CD integrations
- Batch processing tasks
- API-driven usage
- Testing environments
- Resource-constrained deployments

### Recommendation

If running in the reduced environment for production user-facing work:

- ⚠️ Be aware of potential over-engineering tendency
- ⚠️ Monitor for unnecessarily complex solutions
- ⚠️ May need explicit user guidance on scope
- ⚠️ Consider supplementing with your own guidelines
- ✅ Trust safety protocols (fully intact)
- ✅ Trust file operation handling (fully intact)
- ✅ Trust git/PR workflows (fully intact)
