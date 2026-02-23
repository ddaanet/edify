# Implementation Notes

Detailed implementation decisions for claudeutils codebase. Consult this document when implementing similar features or patterns.

## When Using At-sign References

**Context:** CLAUDE.md supports `@file.md` references for progressive disclosure.

**Limitation:** @ references only work in `CLAUDE.md`. Not supported in:
- Skill `SKILL.md` files
- Agent `.md` system prompts
- Task tool prompts

**Workaround:** Place supporting files in skill directory and reference with relative path.

**Example:** `skills/gitmoji/gitmoji-table.md` referenced from SKILL.md using relative path.

**Impact:** Skill documentation must use inline content or relative paths for supporting files.

## When Placing DO NOT Rules In Skills

**Context:** Multi-phase skill procedures with content generation and cleanup.

**Anti-pattern:** Placing "don't write X" rules in cleanup/trim phases instead of writing phases.

**Problem:** Agent follows phases sequentially; by the time it reaches cleanup, the violation is already written.

**Correct pattern:** Place negative constraints alongside positive content guidance, where decisions are made.

**Example:** "No commit tasks" rule moved from Phase 6 (Trim) to Phase 3 (Context Preservation).

**Generalization:** Any rule about what NOT to produce should be co-located with instructions for WHAT to produce.

**Impact:** Prevents violations rather than detecting them after the fact.

## .Claude Code Hooks and Sessions

### When Using Session Start Hooks

**Context:** SessionStart hook output is discarded for new interactive sessions.

**Issue:** [#10373](https://github.com/anthropics/claude-code/issues/10373) — `qz("startup")` never called for new interactive sessions.

**Works:** After `/clear`, `/compact`, or `--resume`.

**Workaround:** Use `@agents/session.md` in CLAUDE.md for task context (already loaded).

**Impact:** Don't build features depending on SessionStart until fixed upstream.

### How to Filter User Prompt Submit Hooks

**Decision:** UserPromptSubmit hooks fire on every prompt; no `matcher` field support.

**Pattern:** All filtering logic must be script-internal, not in settings.json configuration.

**Rationale:** Different hook events have different API capabilities; script-level filtering is more flexible.

**Example:** PreToolUse/PostToolUse support `matcher`, UserPromptSubmit does not.

### When Using Hooks In Subagents

**Anti-pattern:** Using PostToolUse hooks to capture Explore/claude-code-guide results.

**Problem:** Hooks don't fire in sub-agents spawned via Task tool. Task matcher fires on ALL Tasks (noisy).

**Correct pattern:** Session-log based capture (future work) or quiet agents that write their own reports.

**Impact:** Sub-agents can have tools (Bash, Write) but hook interceptors won't execute.

### When Needing Mcp Tools In Subagents

**Anti-pattern:** Assuming quiet-task or other sub-agents can call MCP tools (Context7, etc.).

**Correct pattern:** MCP tools only available in main session. Call directly from designer/planner, write results to report file for reuse.

**Confirmed:** Empirical test — quiet-task haiku has no access to `mcp__plugin_context7_context7__*` tools.

**Impact:** Context7 queries cost opus tokens when designer calls them, but results persist for planner reuse.

### When Skill Is Already Loaded

**Anti-pattern:** After `/clear`, treating loaded skill content as informational rather than actionable.

**Correct pattern:** If skill content is present in context (via command injection), execute it immediately.

**Rationale:** `/clear` resets conversation history but skill invocation injects actionable instructions. The skill IS the task — "fresh session" is not a reason to pause.

### When Hook Fragment Alignment Needed

**Decision:** Hook output must reinforce fragment instructions, never contradict.

**Anti-pattern:** Hook says "write now", fragment says "write on handoff" — agent follows hook (recency position).

**Rationale:** Hook content sits in recency zone, fragment in primacy zone. Contradictions resolve to recency — agent follows stronger signal.

### When Prompt Caching Differs From File Caching

**Decision:** Each Read appends new content block to conversation. "Caching" = prompt prefix matching at API level (92% reuse, 10% cost).

**Anti-pattern:** Assuming Claude Code deduplicates file reads or maintains a file cache.

**Rationale:** No application-level dedup. @-references (system prompt) are more cache-efficient than Read (messages) for always-needed content.

### When Sub-Agent Rules Not Injected

**Decision:** Rules files (`.claude/rules/`) fire in main session only; sub-agents don't receive injection.

**Anti-pattern:** Assuming sub-agents via Task tool receive rules file context.

**Consequence:** Domain context must be carried explicitly — planner writes it into runbook, orchestrator passes through task prompt.

## .Version Control Patterns

### When Treating Commits As Sync Points

**Principle:** Every version control commit synchronizes files, submodules, and context (session.md).

**Trigger:** When adding new kind of state to versioned content, design extension point in /commit skill to check for that state.

**Current sync checks:**
- Submodule commits (step 1b)
- Session.md freshness (step 0)

**Future examples:** Large file tracking, external dependency manifests, generated artifacts.

**Impact:** Commit skill serves as synchronization checkpoint for all versioned state.

### When Deciding To Commit Interactively

**Anti-pattern:** Committing after completing work because it "feels like a natural breakpoint".

**Anti-pattern:** Running raw `git commit` to bypass skill protocol (no STATUS display, no clipboard).

**Correct pattern:** Only commit when user explicitly requests (`/commit`, `ci`, `xc`, `hc`).

**Correct pattern:** ALL commits follow commit skill protocol — STATUS display is mandatory, not optional.

**Rationale:** With `xc` (execute+commit) shortcuts, auto-commit provides no value — user controls commit timing explicitly.

**Reinforcement:** "Fix X and do Y" means fix X, do Y, then STOP. Commit is never implicit in task completion.

### When Git Branch Rename Writes Config

**Decision:** `git branch -m` requires `dangerouslyDisableSandbox: true` — writes `[branch "X"]` tracking section to `.git/config`.

**Failure mode:** Ref renamed successfully but config write fails. Retry sees "branch not found."

**Scope:** Most git commands only read `.git/config`; `branch -m` is an exception.

## .Tokenization and Formatting

### When Choosing Naming Convention Format

**Decision:** Use title-words (e.g., `Tool batching unsolved`) instead of kebab-case identifiers (e.g., `tool-batching-unsolved`).

**Measured:** Kebab-case +31% drift penalty vs title-words +17% when agents get verbose.

**Rationale:** Hyphens often tokenize as separate tokens; spaces between words don't add overhead.

**Impact:** More efficient token usage for identifiers and headers.

### .When Formatting Index Entry Lines

**Decision:** Use bare lines without markers for flat keyword lists.

**Anti-pattern:** Using `- ` list markers for keyword index entries.

**Measured:** 49 tokens (bare) vs 57 tokens (list markers) = 14% savings.

**Rationale:** List markers add no semantic value for flat keyword lists.

**Impact:** 14% token reduction for index structures.

### .When Classifying Section Headers

**Decision:** Default semantic, `.` prefix marks structural (`## .Title`).

**Syntax:** Dot is part of the title text, after the markdown header marker.
- ✅ Correct: `## .Title` (dot after `## `)
- ❌ Wrong: `.## Title` (dot before `##`)

**Rationale:** "Prefix" is ambiguous — explicit examples prevent misinterpretation.

**Anti-pattern:** Mark semantic headers with special syntax, leave structural unmarked.

**Rationale:** Failure mode — orphan semantic header → ERROR (caught) vs silent loss (dangerous).

**Cost:** +1 token per structural header (minority case).

**Impact:** Safe by default with minimal overhead.

## .Design and Requirements

### When Reading Design Classification Tables

**Decision:** Read design classification tables LITERALLY. Apply judgment only where design says "use judgment".

**Anti-pattern:** Inventing classification heuristics when design provides explicit rules (e.g., "subsections = structural" when design table shows all ##+ as semantic).

**Rationale:** Design decisions are intentional. Overriding them based on assumptions contradicts designer's intent.

**Process fix:** Skill fixes outlined for `/design` and `/plan-adhoc`.

**Impact:** Implementation matches design intent without interpretation drift.

### .When Writing Memory Index Entry Keys

**Anti-pattern:** Adding header titles to memory-index.md and claiming "entries exist".

**Correct pattern:** Index entries are `Title — keyword description` where description captures semantic content for discovery.

**Rationale:** Validation checks structural requirements (entry exists); design defines content requirements (entry is keyword-rich). Both must be met.

**Impact:** Don't dismiss critical vet feedback by reframing it as a less-severe related finding.

### How to Format Runbook Phase Headers

**Decision Date:** 2026-02-05

**Decision:** Use `### Phase N` (H3) for visual grouping and `## Step N.M:` (H2) for steps.

**Anti-pattern:** Using `## Phase N` (H2) and `### Step N.M:` (H3) — prepare-runbook.py can't find steps.

**Rationale:** prepare-runbook.py regex matches `^## Step` — steps must be H2 for extraction.

**Implementation:** prepare-runbook.py outputs correct format; manual runbooks need header level awareness.

**Impact:** Runbook processing tools work correctly with phase-grouped structure.

## How to Prevent Skill Steps From Being Skipped

**Decision Date:** 2026-02-06

**Problem:** Skill steps with only prose judgment (no tool call) get skipped during execution. Manifested in 3 cases: commit skill session freshness (Step 0), commit skill vet checkpoint (Step 0b), orchestrate skill phase boundary (3.4).

**Root cause:** Execution-mode cognition optimizes for "next tool call." Steps without tool calls register as contextual commentary, not actionable work.

**Fix (D+B Hybrid):** Combines Option D (Read/Bash anchor) with Option B (restructure into adjacent step):
1. Eliminate standalone prose gates — merge each gate into its adjacent action step
2. Anchor with tool call — each gate's first instruction is a Read or Bash call providing data for evaluation
3. Explicit control flow — gate evaluation uses if/then with explicit branch targets

**Convention:** Every skill step must open with a concrete tool call (Read/Bash/Glob). Prose-only judgment steps are a structural anti-pattern.

**Design:** `plans/reflect-rca-prose-gates/outline.md`

**Impact:** Prevents prose gates from being skipped; establishes convention for future skill design.

## .Validation Patterns

### When Choosing Hard Or Soft Limits

**Decision Date:** 2026-02-11

**Decision:** Either fail build (hard error) or don't check (no validation). Never warnings only.

**Anti-pattern:** Validators that print warnings but don't fail build.

**Rationale:** "Normalize deviance" principle — warnings create false sense of compliance without forcing resolution.

**Example:** memory-index word count changed from warning to hard error, exposed 62 violations immediately.

**Trade-off:** Hard limits force immediate resolution but may need tuning (word count 8-12 may be too strict).

**Impact:** Clear pass/fail states, no ambiguity about compliance.

### .When Marking Organizational Sections

**Decision Date:** 2026-02-11

**Decision:** Mark organizational sections structural (`.` prefix), autofix removes corresponding index entries.

**Anti-pattern:** Index entries pointing to organizational sections (H2 with only H3 subsections).

**Correct pattern:** Judgment at source (decision file marks section structural), index cleanup automatic.

**Recursive rule:** Applies at all heading levels (H2, H3, H4) — any heading with no direct content before sub-headings.

**Impact:** Cleaner indexes pointing only to actual content sections.

### .When Shortening Index Entry Keys

**Decision Date:** 2026-02-11

**Decision:** Shorten description (after em-dash), preserve key exactly as header title.

**Anti-pattern:** Shortening index entry by changing key (part before em-dash).

**Rationale:** Validator matches index keys to decision file headers — changed key = orphan entry error.

**Example:** "Never auto-commit in interactive sessions — ..." → keep full key, shorten description only.

**Impact:** Validator enforcement of index-to-header correspondence.

### When Hitting File Line Limits

**Decision Date:** 2026-02-18

**Anti-pattern:** Compressing user-facing output strings or splitting to new files to pass line-count checks. Both responses degrade quality (output clarity, module cohesion) without addressing the underlying problem.

**Correct pattern:** Look for code quality improvements first — redundant calls, dead code, extraction candidates, helper functions that encode repeated kwargs. Black expansion of 5+ line call sites signals too many parameters for inline use — extract a helper.

**Evidence:** worktree/cli.py 401→400 via output compression (reverted). Actual fix: dedup redundant `rev-parse --show-toplevel` call (401→399).

### When Lint Rule Requires Code Change

**Decision Date:** 2026-02-18

**Anti-pattern:** Circumventing lint with mechanical transformations that satisfy the checker without improving the code. Example: `msg = "..."; raise ValueError(msg)` to dodge "no hardcoded exception messages" — the real problem is using `ValueError` for domain errors.

**Correct pattern:** Fix the underlying design problem the lint rule is pointing at. "No hardcoded exception messages" → create a custom exception class. "Function too long" → extract helpers, not compress strings.

**Rationale:** Lint rules surface design problems. Mechanical circumvention preserves the design problem while removing the signal.

## .Script Optimization

### How to Format Batch Edits Efficiently

**Decision Date:** 2026-02-11

**Decision:** Marker format (`<<<` `>>>` `===`) saves 13% tokens vs JSON for batch edit operations.

**Benefits:**
- No quotes, braces, colons, or escaping needed
- Multi-line content handled naturally without escaping
- Simpler parsing and generation

**Script location:** `agent-core/bin/batch-edit.py`

**Impact:** Token efficiency for automated edit operations.

## .Workflow Integrity

### When Precommit Fails

**Decision Date:** 2026-02-18

**Anti-pattern:** Rationalizing past precommit failure ("lint issues are pre-existing", "my changes are clean"). Deeper: `just precommit` was broken for 9 days (~845 commits) due to non-existent `claudeutils validate` command. No agent noticed because failure was rationalized or bypassed each time.

**Correct pattern:** Precommit is a gate. If it fails, fix before committing. A broken gate is worse than no gate — creates false confidence across all subsequent commits.

**Systemic:** No health check verifies gates themselves are functional. Pipeline assumes `just precommit` works.

### When Editing Runbook Step Or Agent Files

**Decision Date:** 2026-02-18

**Anti-pattern:** Editing `.claude/agents/<plan>-task.md` directly — it's a generated file assembled by prepare-runbook.py from tdd-task.md baseline + Common Context from phase-1 + phase content.

**Correct pattern:** Edit the source (phase files in `plans/<job>/`), then re-run `prepare-runbook.py` to regenerate the agent file and step files. Common Context is extracted from phase preambles (text between `### Phase N:` header and first `## Step`/`## Cycle`) and injected into all step/cycle files via `## Phase Context` section.

**Evidence:** Edit rejected 3 times because target was the generated output, not the source.

### When Removing Stale Learnings On Commit

**Decision Date:** 2026-02-11

**Decision:** When a change invalidates a learning, remove/update that learning atomically in the same commit.

**Anti-pattern:** Adding enforcement without removing the "not enforced" learning in same commit.

**Trigger:** Changes to enforcement (validators, scripts) or behavioral rules (fragments, skills).

**Constraint added:** handoff skill step 4b, commit-delegation.md step 3.

**Impact:** Maintains consistency between code and documentation.
