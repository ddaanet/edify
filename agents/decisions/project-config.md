# Project Configuration

Project-level configuration decisions for Claude Code, models, skills, and development environment.

## .Memory Index Pruning

### .How to Manage Memory Index Growth

**Memory index append-only:**

**Decision Date:** 2026-02-01

**Decision:** No active pruning. Soft limit (100 entries) triggers consolidation of related entries into domain summaries, not deletion.

**Options considered:**
- A) No pruning, just growth — simple but index could become noisy
- B) Redundancy-based (remove when fragment is @-imported) — circular: index catalogs ALL knowledge
- C) Staleness-based (remove after N cycles without relevance) — requires metadata tracking, learnings aren't ephemeral
- D) Coverage-based (replace granular entries with domain summaries) — natural consolidation pattern

**Chosen:** A — append-only, no pruning, no consolidation, no limit.

**Rationale:**
- Each entry provides keyword-rich discovery surface for on-demand knowledge — removal loses ambient awareness
- Consolidation into domain summaries kills keyword matching (e.g., "Sandbox patterns" won't trigger when agent works on `prepare-runbook.py`)
- Soft limits cause the same failure as learnings.md: agents treat them as hard caps and aggressively prune
- Token cost is modest: 200 entries × ~25 tokens ≈ 5000 tokens (acceptable for always-loaded context)
- Growth is naturally bounded by consolidation rate (~5-10 entries/session)

**Impact:** memory-index.md header updated (append-only), consolidation-patterns.md updated, no changes to /codify skill logic.

## .Claude Code Rule Files

### How to Inject Context With Rule Files

**Rule files pattern:**

**Decision Date:** 2026-01-27

**Decision:** Use `.claude/rules/` with `paths` frontmatter for automatic context injection when editing domain-specific files.

**Rationale:**
- Documentation-only enforcement (CLAUDE.md tables) relies on model memory/attention - unreliable
- Hooks cannot detect skill loading state (only see tool inputs, not conversation context)
- Rule files with path prefixes provide automatic, hierarchical context injection

**Implementation:**
- `.claude/rules/skill-development.md` → `.claude/skills/**/*`
- `.claude/rules/hook-development.md` → `.claude/hooks/**/*`
- `.claude/rules/agent-development.md` → `.claude/agents/**/*`
- `.claude/rules/command-development.md` → `.claude/commands/**/*`

**Limitations:**
- Rule files provide passive reminders, not enforcement
- Models can still ignore rule context (requires compliance)
- Trade-off accepted: Better discoverability than CLAUDE.md bloat, but not foolproof

**Impact:**
- Improved discoverability of pre-edit requirements
- Automatic context loading when editing domain files
- Removed 13 lines of Pre-Edit Checks table from CLAUDE.md

## .Model Terminology

### When Naming Model Capability Tiers

**Premium standard efficient:**

**Decision Date:** 2026-01-27

**Decision:** Use "premium/standard/efficient" terminology for model tiers instead of "T1/T2/T3".

**Rationale:**
- T3 terminology ambiguous: Could mean "tier 3" (lowest) or "T-3" (third from top)
- Premium/standard/efficient clearly communicates capability hierarchy
- Aligns with cost and performance expectations

**Mapping:**
- Premium = Opus (architecture, complex design)
- Standard = Sonnet (general work, planning)
- Efficient = Haiku (execution, simple edits)

**Impact:**
- Clear model selection guidance in delegation
- No ambiguity in documentation and skill instructions
- Easier for users to understand model choices

## .Skill Discovery

### How to Make Skills Discoverable

**Skill discovery layers:**

**Decision Date:** 2026-02-01

**Decision:** Skills require multiple discovery layers, not just good internal documentation.

**Anti-pattern:** Build well-documented skill and assume agents will find it ("build it and they will come")

**Correct pattern:** Surface skills via 4 discovery layers:
1. CLAUDE.md fragment or always-loaded context
2. Path-triggered `.claude/rules/` entry
3. In-workflow reminders in related skills
4. Directive skill description

**Rationale:** Agents only see skill listing descriptions and always-loaded context. Internal skill docs are invisible until invoked.

**Example:** opus-design-question skill had 248-line docs but zero external visibility — agents asked user instead of consulting it. Fixed with 4-layer approach.

**Impact:** Ensures skills are discoverable and used appropriately.

## .Agent Development

### When Writing Agent Yaml Frontmatter

**Agent frontmatter multiline:**

**Decision Date:** 2026-02-01

**Decision:** Agent frontmatter YAML must use multi-line syntax (`|`) for descriptions containing examples.

**Anti-pattern:**
```yaml
description: Short description
<example>...</example>
```

**Correct pattern:**
```yaml
description: |
  Short description with examples
  <example>...</example>
```

**Rationale:** YAML parsers treat unindented content after `description:` as new fields. Invalid YAML prevents agent registration. Multi-line string syntax (`|`) makes examples part of description value.

**Impact:** Prevents agent registration failures due to invalid YAML.

## .Symlink Management

### When Verifying Symlinks After Operations

**Symlinks after formatters:**

**Decision Date:** 2026-02-01

**Decision:** Verify symlinks after operations that reformat files.

**Anti-pattern:** Assume symlinks in `.claude/hooks/` persist across tool operations

**Correct pattern:** Verify symlinks after `just dev`, `ruff format`, or similar formatters

**Rationale:** Formatters follow symlinks and may replace them with reformatted copies. `just dev` did this to both hook .py files.

**Impact:** Use `just sync-to-parent` to restore symlinks after formatting operations.

## .Shell Environment

### When Using Heredocs In Sandbox

**Heredocs in sandbox:**

**Decision Date:** 2026-02-01 (SOLVED)

**Problem:** Heredocs broken in sandbox mode — zsh uses `TMPPREFIX` (not `TMPDIR`) for heredoc temp files. Default `/tmp/zsh` is outside sandbox allowlist.

**Solution:** `export TMPPREFIX="${TMPDIR:-/tmp}/zsh"` in `agent-core/configs/claude-env.sh` (sourced by `.envrc`)

**Rationale:** Claude Code sandbox sets TMPDIR but not TMPPREFIX for zsh.

**Status:** Resolved in agent-core configuration.

**Impact:** Heredocs work correctly in sandbox mode.

## .Command-Line Parsing

### When Parsing Cli Flags As Tokens

**Flags are exact tokens:**

**Decision Date:** 2026-02-04

**Decision:** Flags are exact tokens (`--commit`), not prose containing flag-like words.

**Anti-pattern:** Parsing `/handoff describe commit` as having `--commit` flag (substring match).

**Correct pattern:** User prose after command is guidance for the skill, not flags. When ambiguous, assume no flag.

**Rationale:** Flags are CLI syntax; prose is user guidance. Substring matching leads to false positives.

**Impact:** Clear separation between flags and prose arguments.

## .File Size Limit

### .400-Line Module Limit

**File size limit rationale:**

**Decision Date:** 2026-02-13

**Decision:** 400-line hard limit per source module. Enforced by precommit.

**Rationale (research-backed):**
- Code review effectiveness drops faster-than-linear past ~400 LOC ([Baldawa 2024](https://rishi.baldawa.com/posts/pr-throughput/cognitive-load-cliff/)). Reviews under 300 lines get architectural feedback; past 600, only style comments.
- AI-assisted development sweet spot: 150-500 lines ([Faherty 2025](https://medium.com/@eamonn.faherty_58176/right-sizing-your-python-files-the-150-500-line-sweet-spot-for-ai-code-editors-340d550dcea4))
- PyLint default max-module-lines: 1000 (too permissive for agent context)
- Provides backpressure against slop accumulation
- Approximates what a human can read without significant effort

**Remedy when exceeded:** Split module by functional responsibility. Refactor agent (sonnet) has authority to split without opus escalation — module extraction is mechanical, not architectural.

**Anti-pattern:** Reactive per-cycle refactoring to squeeze lines within limit. Proactive split before a phase that targets a near-limit file.

**Impact:** Runbook planning must project file growth and insert split points.

## .Project Structure

### When Finding Project Root In Scripts

**Root marker for scripts:**

**Decision Date:** 2026-02-04

**Decision:** Use `CLAUDE.md` as project root marker in `find_project_root()`.

**Anti-pattern:** Using `agents/` as project root marker.

**Rationale:** Subdirectories may contain their own `agents/` folders (e.g., `agent-core/agents/`), causing scripts to stop at wrong level.

**Impact:** Scripts correctly identify project root regardless of subdirectory structure.

## .Agent Architecture

### How To Compose Agents Via Skills

**Decision Date:** 2026-02-15

**Decision:** Use `skills:` YAML frontmatter in agent definitions to inject skill content as prompt.

**Pattern:** Wrap fragments as lightweight skills, reference via `skills:` — no build step, stays current automatically.

**Usage:** corrector, design-corrector, outline-corrector, runbook-corrector, refactor, runbook-outline-corrector.

### How To Recall Sub-Agent Memory

**Decision Date:** 2026-02-15

**Decision:** Inject memory index via `skills:` (discovery), recall via Bash transport (`claudeutils _recall resolve "when <trigger>"`).

**Anti-pattern:** Expecting sub-agents to use Skill tool for `/when` or `/how`.

**Rationale:** Sub-agents lack Skill tool. Bash transport provides same recall capability with different invocation.

### How To Augment Agent Context

**Decision Date:** 2026-02-15

**Decision:** Two-tier context augmentation:
- Always-inject (skills prolog): universal conventions, ~400 tokens, cached in system prompt
- Index-and-recall (on-demand): domain-specific, recalled via bash transport

**Key insight:** Discovery burden stays with capable agents (design/planning). Haiku gets pre-assembled context in runbook steps and agent system prompts.

**Sub-agent gap:** CC sub-agent system prompt provides only identity and file search guidance — no prose quality, token economy, or error handling rules. Skills injection via `skills:` frontmatter is high value.

### When Agent-Creator Reviews Agents

**Decision Date:** 2026-02-15

**Decision:** plugin-dev agent-creator has Write+Read tools — can review and fix agent definitions, not just create.

**Pattern:** "Review and fix this agent definition at [path]" works for validation + autofix.

**Note:** No dedicated agent-reviewer exists in plugin-dev (only skill-reviewer, plugin-validator, agent-creator).

### When Custom Agents Need Session Restart For Discoverability

**Decision Date:** 2026-02-24

**Anti-pattern:** Using plan-specific agents as `subagent_type` values in the same session they were created. They aren't indexed until restart.

**Correct pattern:** Plan-specific agents in `.claude/agents/` are discoverable as Task `subagent_type` values only after session restart. The prepare-runbook.py → restart → orchestrate workflow naturally includes this boundary. Built-in types with prompt injection work as fallback when restart isn't feasible.

**Evidence:** `hb-p1` through `hb-p5` not discoverable in creating session. Confirmed discoverable in subsequent sessions.
