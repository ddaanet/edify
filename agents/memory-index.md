# Memory Index

Prefer retrieval-led reasoning over pre-training knowledge.

Condensed knowledge catalog. Read referenced files when working in related areas.

**Consumption pattern:** This index is loaded via CLAUDE.md @-reference—it's already in your context. Do NOT grep or re-read this file. Scan the loaded content mentally, identify relevant entries, then Read the referenced file directly.

**File organization:** Sections are grouped by target file. The section heading specifies the file; entries within that section point to that file. When an entry is relevant, read the referenced file.

**Append-only.** Never remove or consolidate entries — each entry is a keyword-rich discovery surface for on-demand knowledge. Growth is bounded by consolidation rate (~5-10 entries/session) and total token cost is modest (200 entries ≈ 5000 tokens).

**Do not index content already loaded via CLAUDE.md.** Fragments referenced by `@` are in every conversation. Index entries for those add noise without aiding discovery. Only index knowledge that requires on-demand loading.









## Behavioral Rules (fragments — already loaded)

Scan triggers unnecessary tools — check loaded context not Read/Grep for @-referenced files
Delegation with context — don't delegate when context already loaded, token economy
Never auto-commit in interactive sessions — commit only on explicit request
Loaded skill overrides fresh-session framing — skill content is actionable, execute immediately
Design tables are binding constraints — read classifications literally, apply judgment where design permits
Header titles not index entries — index entries need keyword-rich descriptions not just title repetition
Skill rules placement: point of violation — place prohibitions at decision point
Output requires vet+fix with alignment — verify design/requirements/acceptance criteria matches
Vet-fix-agent confabulation from design docs — precommit first explicit IN/OUT scope prevents false positives

## Technical Decisions (mixed — check entry for specific file)

Minimal `__init__.py` — keep empty, prefer explicit imports from specific modules
Private helpers stay with callers — cohesion over extraction, clear module boundaries
Module split pattern — split large files by functional responsibility, maintain 400-line limit
Path encoding algorithm — simple slash to dash replacement with special root handling
History directory resolution — use claude projects encoded path as standard location
Title extraction — handle both string and array text blocks content formats
Title formatting — replace newlines with spaces, truncate to 80 chars with ellipsis
Trivial message detection — multi-layer filter with empty single-char slash commands keyword set
Feedback extraction layering — type filter, error check, interruption check, trivial filter priority
UUID session pattern — validate session files with regex filter agent and non-session
Sorted glob results — use sorted glob instead of raw, predictable test results
First-line parsing — parse only first JSONL line for session metadata, O(1)
Recursive pattern: AgentId → SessionId — agent IDs become session IDs for child agents
Agent ID extraction — extract agentId from first line, avoid repeated extraction
Graceful degradation — skip malformed entries, log warnings, continue processing partial data
Optional field defaults — use get field default for optional fields, graceful missing data
Pydantic for validation — use BaseModel for all data structures, type safety
FeedbackType enum — use StrEnum for feedback types, type-safe string constants
Docformatter vs. Ruff D205 conflict — shorten docstring summaries to fit 80 chars
Complexity Management — extract helper functions when cyclomatic complexity exceeds limits, refactor not suppress
No Suppression Shortcuts — fix linting issues properly instead of using noqa suppressions
Type Annotations — full type annotations in strict mypy mode, catch bugs early
Pipeline architecture — three-stage pipeline collect analyze rules for feedback processing
Filtering module as foundation — reusable is_noise and categorize_feedback functions, DRY principle
Noise detection patterns — multi-marker detection with length threshold for command outputs
Categorization by keywords — keyword-based category assignment with priority order for feedback
Deduplication strategy — first 100 characters as dedup key, case-insensitive prefix tracking
Stricter filtering for rules — additional filters beyond analyze for rule-worthy items
Model as first positional argument — required parameter for accurate token counts
Model alias support — hybrid approach with runtime probing fallback for unversioned aliases
Anthropic API integration — use official SDK with default environment variable handling
Empty file optimization — return zero for empty files without API call
No glob expansion (initial release) — defer pattern expansion to future, shell expansion sufficient
Markdown cleanup architecture — preprocessor fixes structure before dprint formatting for Claude output
Problem — Claude generates markdown with consecutive emoji lines and improper nesting
Solution — run markdown fixes before dprint, error on invalid patterns
Design decisions — extend fix_warning_lines for checklists, create new for code blocks
Extend vs. new functions — conceptual similarity vs fundamentally different block-based processing
Error on invalid patterns — prevents dprint failures, makes issues visible immediately
Processing order — line-based before block-based, spacing after structural changes
Prefix detection strategy — generic prefix detection not hard-coded patterns for adaptability
Indentation amount — two spaces for nested lists, standard markdown convention
Future direction — evolve to dprint plugin for single-pass processing
Remark-cli over Prettier — idempotent by design, CommonMark compliance, handles nested code blocks
Growth + consolidation model — append-only with no pruning or limits, keyword-rich discovery
Rule files for context injection — use claude rules with paths frontmatter for automatic loading
Premium/standard/efficient naming — opus sonnet haiku terminology instead of ambiguous T1 T2 T3
Multi-layer discovery pattern — surface skills via CLAUDE.md rules workflow reminders descriptions
Agent frontmatter YAML validation — use multi-line syntax for descriptions containing examples
Skill dependencies in requirements — scan A.0 for indicators load immediately
Symlink persistence — verify symlinks after operations that reformat files like dev
Heredoc sandbox compatibility — export TMPPREFIX for zsh heredoc temp files in sandbox
Path.cwd() vs os.getcwd() — use Path.cwd() for consistency with pathlib usage
Error output pattern — print errors to stderr before exit one, Unix convention
Entry point configuration — add project scripts in pyproject for direct command usage
Feedback processing output formats — support both text and JSON formats for flexibility
Token output format — human-readable text by default, JSON with flag, include resolved model
Test module split strategy — mirror source module structure, separate CLI tests by subcommand
Mock patching pattern — patch where object is used not where defined
Testing strategy for markdown cleanup — TDD approach with red green cycles and integration tests
Success metrics — all tests pass, no regressions, clear errors, complete documentation

## agents/decisions/pipeline-contracts.md

Transformation table — T1-T6 pipeline stages defect types review gates criteria
Review delegation scope template — scope IN OUT changed files requirements
UNFIXABLE escalation — fix-all pattern grep UNFIXABLE stop escalate
Phase type model — tdd general per-phase typing expansion review criteria

## agents/decisions/deliverable-review.md

Deliverable definition — artifact types review axes ISO-grounded identification process

## agents/decisions/implementation-notes.md

@ references limitation — CLAUDE.md @ syntax only works in CLAUDE.md not skills agents tasks
SessionStart hook limitation — output discarded for new interactive sessions, works after clear compact resume
UserPromptSubmit hook filtering — fires every prompt, no matcher, filtering script-internal
Hook capture impractical for subagents — hooks don't fire in Task subagents
MCP tools unavailable in subagents — only in main session, not Task tool
Commits are sync points — every commit synchronizes files submodules context session.md state
Title-words beat kebab-case — title-words have 17% drift vs kebab-case 31% drift, hyphens tokenize separately
Bare lines beat list markers — flat keywords without markers save 14% tokens
Default semantic, mark structural — semantic default, structural gets dot prefix
Phase-Grouped Runbook Header Format — H3 phase grouping H2 steps for prepare-runbook.py extraction
Prose Gate D+B Hybrid Fix — merge gates into action steps, anchor with tool call
Hard limits vs soft limits — fail build or don't check, warnings normalize deviance
Organizational sections and index pollution — mark structural with dot prefix, autofix removes index entries
Index entry key preservation — shorten description preserve key, validator matches keys to headers
Batch edit token efficiency — marker format saves 13% tokens vs JSON for batch edits
Commits must remove invalidated learnings — atomic removal of stale learnings in same commit

## agents/decisions/project-config.md

Flags are exact tokens — exact token match not prose substring CLI parsing
Root marker for scripts — CLAUDE.md not agents directory subdirectory issue

## agents/decisions/prompt-structure-research.md

Position Bias (Serial Position Effects) — primacy strongest, recency secondary, middle weakest
Rule Format Effectiveness — bullets outperform prose for discrete rules
Model Capability Differences — opus concise, sonnet clear, haiku explicit steps
Rule Budget Constraints — adherence degrades above 200 rules, ~150 user limit
Context Loading Behavior — LLMs only read explicitly provided context
Tool Landscape (Dec 2025) — no tool combines position bias variants budgeting
Applicability to Current Architecture — fragment ordering token counting opportunities
Fragment Ordering Rationale (Feb 2026) — primacy for session-defining, recency for reference, context-budget.py for tracking

## agents/decisions/runbook-review.md

Vacuous cycles — scaffold-only RED tests degenerate GREEN LLM failure mode
Dependency ordering — foundation-first forward reference intra-phase detection
Cycle density — edge-case clusters trivial phases collapse candidates
Checkpoint spacing — drift accumulation haiku instruction loss quality gates

## agents/decisions/testing.md

TDD RED Phase: Behavioral Verification — verify behavior with mocking fixtures not just structure
TDD: Presentation vs Behavior — test behavior defer presentation to vet checkpoints
TDD Integration Test Gap — assert behavioral outcomes not just execution structure at phase boundaries
Conformance Validation for Migrations — compare implementation against original spec presentation gaps

## agents/decisions/workflow-advanced.md

Seeding before auto-generation — seed indexes existing docs consolidation complementary
Index entries require backing documentation — learnings learnings.md permanent doc index entry
Template merge semantics — explicit preserve add replace prevent overwrites
Requirements immutable during execution — updating requires user confirmation planning execution
Ambient awareness beats invocation — embed critical knowledge loaded context CLAUDE.md
Task prose keys pattern — task names searchable identifiers git log search
Commit RCA Fixes Active — submodule awareness artifact staging orchestrator stop rule
Precommit Is Read-Only — validation not transformation session.md exempt for token expansion
Outline Enables Phase-by-Phase Expansion — holistic outline then incremental phase expansion with reviews
Phase-by-Phase Review Pattern — generate review fix-all check-escalation proceed iterative not batch
Manual runbook assembly bypasses automation — phase files separate prepare-runbook.py assembles
Review Agent Fix-All Pattern — audit trail autofix everything escalate unfixable to caller
Recommendations Inline Transmission — append guidance to consumed artifact not separate report
Report Naming Convention — descriptive base names iteration suffix for same artifact review cycles
Prose Test Descriptions Save Tokens — prose descriptions save 80% over full test code
Complexity Before Expansion — check complexity callback to previous level if too large
Consolidation Gates Reduce Orchestrator Overhead — merge trivial work with adjacent complexity at two gates
Workflow Feedback Loop Insights — alignment autofix outline complexity gate principles
Dogfooding Validates Design — apply new process to its own planning for validation
Phase boundaries require checkpoint delegation — hard stop explicit vet at phase transitions
TDD GREEN Behavioral Descriptions — behavior approach hint structure not prescriptive code
Efficient Model Analysis Requires Verification — haiku execution sonnet opus architecture verify results
Domain Validation Pattern — planning-time detection, skill-directed vet, no agent proliferation

## agents/decisions/workflow-core.md

Oneshot workflow pattern — weak orchestrator with runbook-specific agents for ad-hoc tasks
TDD Workflow Integration — extend weak orchestrator for TDD with cycle-based runbooks
Handoff Pattern: Inline Learnings — store learnings inline in session.md not separate files
Design Phase: Output Optimization — minimize designer output tokens, planner elaborates details
Planning Pattern: Three-Stream Problem Documentation — parallel work streams with problem and session files
TDD Workflow: Commit Squashing Pattern — squash cycle commits into single feature commit
Orchestrator Execution Mode — execution mode metadata overrides system prompt parallelization directives
Orchestration Assessment: Three-Tier Implementation Model — direct lightweight and full runbook routing
Checkpoint Process for Runbooks — two-step fix and vet checkpoints at natural boundaries
Phase-grouped TDD runbooks — support flat H2 and phase-grouped H2 H3 cycle headers
Cycle numbering gaps relaxed — gaps warnings document order defines sequence
No human escalation during refactoring — opus handles architectural changes within design bounds
Defense-in-Depth: Commit Verification — multiple layers at tdd-task and orchestrate skill levels
Delegation without plan causes drift — provide runbook OR acceptance criteria when delegating

## agents/decisions/workflow-optimization.md

Handoff tail-call pattern — always end with handoff commit regardless of tier
Handoff commit assumption — session.md reflects post-commit state with commit flag
Routing layer efficiency — single-layer complexity assessment, avoid double assessment
Vet agent context usage — leverage vet context for fixes instead of new agents
Outline-first design workflow — freeform outline iterate deltas validate full design
Model selection for design guidance — haiku explicit edits sonnet interprets intent
Design review uses opus — design-vet-agent architecture analysis not vet-agent
Vet catches structure misalignments — validates file paths structural assumptions prevents blockers
Agent-creator reviews in orchestration — create spec agent-creator reviews YAML syntax
Template commit contradiction — appended context weak authority bolded NEVER structural
Orchestrator model mismatch — read step file execution model not orchestrator default
Happy path first TDD — simplest happy path real behavior edge cases later
Runbook Outline Format — structured format for runbook planning with requirements mapping
Continuation passing pattern — composable skill chains, hook multi-skill only, skills own default-exit
Hook-based parsing rationale — deterministic regex, empirical 0% FP rate, context filtering
