---
name: remember-skill-update
model: sonnet
---

# Remember Skill Update

**Context**: Align learning titles with memory-index triggers at creation time; simplify consolidation pipeline; add recall CLI improvements; rename skill.
**Design**: `plans/remember-skill-update/outline.md`
**Requirements**: `plans/remember-skill-update/requirements.md`
**Status**: Ready
**Created**: 2026-02-23

---

## Weak Orchestrator Metadata

**Total Steps**: 16 (6 TDD cycles + 6 general steps + 2 inline phases)

**Execution Model**:
- Phase 1 (Cycles 1.1-1.3): Sonnet (TDD — behavioral code in validation module)
- Phase 2 (Steps 2.1-2.5): Opus (architectural artifacts — skills, agents, fragments)
- Phase 3 (Step 3.1): Opus (architectural artifacts — skill routing)
- Phase 4 (Cycles 4.1-4.3): Sonnet (TDD — behavioral code in CLI module)
- Phase 5: Inline (orchestrator-direct — mechanical substitution in 4 files)
- Phase 6 (Steps 6.1-6.2): Sonnet (mechanical rename propagation)
- Phase 7: Inline (orchestrator-direct — analysis writing)

**Step Dependencies**:
- Phase 1 → Phase 2 → Phase 3 → Phase 6
- Phase 4 → Phase 5 → Phase 6
- Phase 7: independent (parallel with any phase)

**Error Escalation**:
- Sonnet → User: Test regression, unexpected validation behavior
- Opus → User: Skill wording ambiguity, conflicting instructions across files

**Report Locations**: `plans/remember-skill-update/reports/`

**Success Criteria**:
- All 20 tests pass (12 baseline + 8 new) after Phases 1 and 4
- `just precommit` passes at each phase checkpoint
- Grep verification clean after Phase 6 rename
- Frozen-domain analysis report written (Phase 7)

**Prerequisites**:
- All source files exist (✓ verified via Phase 0.5 discovery)
- 12/12 baseline tests pass (✓ verified)
- `/plugin-dev:skill-development` loaded before skill edits (Phase 2, 3, 5)
- `/plugin-dev:agent-development` loaded before agent edits (Phase 2 Step 2.5)

---

## Common Context

**Requirements (from design):**
- FR-1: Titles use When/How prefix
- FR-2: Min 2 content words after prefix ("When X Y" = 2 content, pass; "When X" = 1, fail)
- FR-3: Structural validation at precommit
- FR-4: Consolidation pipeline is mechanical (trigger = title, no rephrasing)
- FR-5: Semantic guidance in skill and handoff docs
- FR-8: Inline execution in clean session — delete remember-task agent
- FR-9: Inline file splitting — delete memory-refactor agent
- FR-10: Rename skill to /codify
- FR-11: Agent routing for learnings (13 eligible agents)
- FR-12: Recall CLI one-arg syntax + batched recall
- FR-13: Remove @agents/memory-index.md from CLAUDE.md

**Requirements Mapping:**

| Requirement | Phase | Items |
|-------------|-------|-------|
| FR-1 | 1 | Cycle 1.1 |
| FR-2 | 1 | Cycle 1.2 |
| FR-3 | 1 | Cycles 1.1-1.3 (validate() changes propagate via cli.py) |
| FR-4 | 2 | Step 2.1 (trigger derivation), Step 2.3 (consolidation-patterns) |
| FR-5 | 2 | Steps 2.1, 2.4 |
| FR-8 | 2 | Steps 2.1, 2.2, 2.5 |
| FR-9 | 2 | Steps 2.1, 2.5 |
| FR-10 | 6 | Steps 6.1-6.2 |
| FR-11 | 3 | Step 3.1 |
| FR-12 | 4, 5 | Cycles 4.1-4.3 (code), Phase 5 (docs) |
| FR-6 | 7 | Phase 7 inline |
| FR-13 | 2 | Step 2.5 |

**Key Decisions:**
- KD-1: Hyphens allowed (30+ existing triggers use hyphens)
- KD-2: Migration already done (all 54 titles use When prefix)
- KD-3: Agent duplication eliminated by FR-8
- KD-4: Frozen-domain deferred to Phase 7 analysis
- Content words: "min 2 words" = 2 content words after stripping When/How to prefix

**Scope boundaries:**
- IN: validation code, skill docs, agent definitions, CLI code, CLI docs, rename propagation, analysis
- OUT: memory index validation pipeline, hook implementation, compress-key.py

**Project Paths:**
- Validation: `src/claudeutils/validation/learnings.py`, `tests/test_validation_learnings.py`
- CLI: `src/claudeutils/when/cli.py`, `tests/test_when_cli.py`, `agent-core/bin/when-resolve.py`
- Resolver: `src/claudeutils/when/resolver.py` (signature unchanged)
- Remember skill: `agent-core/skills/remember/SKILL.md`
- Consolidation patterns: `agent-core/skills/remember/references/consolidation-patterns.md`
- Consolidation flow: `agent-core/skills/handoff/references/consolidation-flow.md`
- Handoff skill: `agent-core/skills/handoff/SKILL.md`
- When/How skills: `agent-core/skills/when/SKILL.md`, `agent-core/skills/how/SKILL.md`
- Memory-index skill: `agent-core/skills/memory-index/SKILL.md`
- Agents to delete: `agent-core/agents/remember-task.md`, `agent-core/agents/memory-refactor.md`
- TDD test plan: `plans/remember-skill-update/tdd-test-plan.md`

**Platform constraints:**
- Load `/plugin-dev:skill-development` before editing skill files
- Load `/plugin-dev:agent-development` before editing agent files
- Skill descriptions require "This skill should be used when..." format

---

### Phase 1: TDD Validation (type: tdd, model: sonnet)

Structural validation in `src/claudeutils/validation/learnings.py`. Three new checks added to existing `validate()` function.

**Files:** `src/claudeutils/validation/learnings.py`, `tests/test_validation_learnings.py`
**Baseline:** 7 existing tests, all passing. Precommit integration already wired in `src/claudeutils/validation/cli.py`.

## Cycle 1.1: When/How prefix required

**RED:**
- New test: `test_title_without_prefix_returns_error`
- Fixture: learnings file with `## Bad Title` after preamble
- Assert: `validate()` returns error containing prefix requirement + line number
- Expected failure: No prefix check in validate(), returns `[]`

**Verify RED:** `just test tests/test_validation_learnings.py::test_title_without_prefix_returns_error -v`

**GREEN:**
- Add prefix check in `validate()`: title must start with `When ` or `How to `
- Update 5 existing test fixtures to use prefixed titles while preserving their error conditions:
  - "Learning One" → "When learning one"
  - "Learning Two" → "When learning two"
  - "First Learning Title" → "When first learning"
  - "First Valid Title" → "When valid title"
  - Long title → `## When this title has way too many words for the validator`
  - Multiple errors fixture: update all titles to use prefixes while preserving word count and duplicate error conditions

**Verify GREEN:** `just test tests/test_validation_learnings.py -v`
**Verify no regression:** `just test -v`

---

## Cycle 1.2: Min 2 content words after prefix

**RED:**
- New test: `test_insufficient_content_words_returns_error`
- Fixture: learnings file with `## When testing` (1 content word after prefix)
- Assert: `validate()` returns error mentioning content words + line number
- Expected failure: No content word count check, returns `[]`

**Verify RED:** `just test tests/test_validation_learnings.py::test_insufficient_content_words_returns_error -v`

**GREEN:**
- Strip prefix, count remaining words, require ≥2
- Implementation: if title starts with `How to `, content = words[2:]; if `When `, content = words[1:]. Check `len(content) < 2`.

**Verify GREEN:** `just test tests/test_validation_learnings.py -v`
**Verify no regression:** `just test -v`

---

## Cycle 1.3: Edge cases and combined validation

**RED:** Three new tests:
- `test_how_to_prefix_accepted` — `## How to encode paths` (2 content words) → passes (no errors)
- `test_how_without_to_rejected` — `## How encode` → prefix error (not `How to`)
- `test_combined_errors_reported` — file with `## When testing` (prefix OK, 1 content word → content error) and `## Bad` (prefix error) → both errors reported

**Verify RED:** `just test tests/test_validation_learnings.py -k "how_to or how_without or combined" -v`

**GREEN:**
- No implementation change required. Cycles 1.1-1.2 implement complete logic: prefix check rejects anything not starting with `When ` or `How to ` (covers `How encode`), content-word check covers all prefix-passing titles. Verify all 12 tests pass with no code changes.

**Verify GREEN:** `just test tests/test_validation_learnings.py -v`
**Verify no regression:** `just test -v`

**Phase 1 Checkpoint:** `just precommit` — validates new checks propagate through CLI.

---

### Phase 2: Semantic Guidance + Pipeline Simplification (type: general, model: opus)

Prose edits to skills, agents, and CLAUDE.md. All decisions pre-resolved.

**Note:** SKILL.md also edited in Phase 3 (agent routing). Phase 3 depends on Phase 2 completion.

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.

## Step 2.1: Update remember SKILL.md

**Objective**: Align skill documentation with new validation rules and inline execution model.

**Target:** `agent-core/skills/remember/SKILL.md`

**Implementation:**
- **Title guidance (FR-5):** Add section after "Learnings Quality Criteria" (line 76): titles must start with "When"/"How to", min 2 content words after prefix, anti-pattern/correct-pattern examples
- **Trigger derivation (FR-4):** Update Step 4a (line 59): trigger = operator prefix + learning title (mechanical, no rephrasing). Remove "Optimize for discovery" guidance (line 67) — title IS the trigger
- **Inline execution (FR-8):** Add prerequisite note: skill executes in calling session, requires clean session (fresh start). Remove any delegation references
- **Inline splitting (FR-9):** Add to Step 4: after Write/Edit to decision file, check line count; if >400, split by H2/H3 boundaries into 100-300 line sections; run `validate-memory-index.py --fix` after split
- **Fix "no hyphens" (KD-1):** Remove "no hyphens or special characters" from line 65 — contradicts practice (30+ triggers use hyphens)

**Validation:** Read updated file, verify all 5 changes applied, no conflicting instructions.

---

## Step 2.2: Update consolidation-flow.md

**Objective**: Remove delegation flow, replace with inline invocation.

**Target:** `agent-core/skills/handoff/references/consolidation-flow.md`

**Implementation:**
- Replace delegation flow (lines 7-10: filter → batch check → delegate to remember-task → read report) with inline flow: invoke `/remember` skill in clean session
- Replace refactor flow (lines 16-19: delegate to memory-refactor) with inline instructions matching FR-9 (check line count, split by H2/H3, run validate-memory-index.py)
- Preserve error handling section (lines 24-27)

**Validation:** Read updated file, verify no references to remember-task or memory-refactor agents remain.

---

## Step 2.3: Update consolidation-patterns.md derivation protocol

**Objective**: Make trigger derivation mechanical — title IS the trigger.

**Target:** `agent-core/skills/remember/references/consolidation-patterns.md`

**Implementation:**
- Update Memory Index Maintenance section (line 64): trigger derived mechanically from title — `## When X Y` → `/when x y` (lowercase, no rephrasing)
- Remove "Trigger naming" optimization guidance that implies agent judgment

**Validation:** Read updated section, verify no language suggesting rephrasing or "optimize for discovery".

---

## Step 2.4: Update handoff skill Step 4 with trigger framing

**Objective**: Enforce trigger-compatible title format at creation time.

**Target:** `agent-core/skills/handoff/SKILL.md` (lines 101-107)

**Implementation:**
- Strengthen line 105: titles must start with "When" or "How to", min 2 content words after prefix
- Add: reject jargon/root-cause titles, suggest rephrasing to situation description
- Add examples: ❌ "transformation table" → ✅ "choosing review gate"; ❌ "prose gates" → ✅ "prevent skill steps from being skipped"

**Validation:** Read Step 4, verify format rules present and examples clear.

---

## Step 2.5: Remove deprecated artifacts (FR-8, FR-9, FR-13)

**Objective**: Delete superseded agents and demote memory-index from always-loaded context.

**Implementation:**
- Delete `agent-core/agents/remember-task.md` (FR-8)
- Delete `agent-core/agents/memory-refactor.md` (FR-9)
- Remove `@agents/memory-index.md` reference from `CLAUDE.md` line 49 (~5000 tokens, 2.9% recall — FR-13)
- File `agents/memory-index.md` remains (used by when-resolve.py)
- Verify no other files reference deleted agents: `grep -r "remember-task\|memory-refactor" agent-core/ agents/ .claude/ --include="*.md"`

**Validation:** Grep returns no references (excluding plan files and git history).

**Phase 2 Checkpoint:** `just precommit` passes. Grep verification clean.

---

### Phase 3: Agent Routing for Learnings (type: general, model: opus)

Add agent templates as consolidation targets.

**Eligible agents (13):** artisan, brainstorm-name, corrector, design-corrector, hooks-tester, outline-corrector, refactor, runbook-corrector, runbook-outline-corrector, runbook-simplifier, scout, tdd-auditor, test-driver

**Excluded:** plan-specific agents (generated per-runbook by prepare-runbook.py), remember-task (deleted), memory-refactor (deleted)

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.

## Step 3.1: Add agent routing to remember skill (SKILL.md + consolidation-patterns.md)

**Objective**: Enable consolidation pipeline to route agent-relevant learnings to agent definitions.

**Target 1:** `agent-core/skills/remember/SKILL.md` Step 2 "File Selection" (line 26)
- Add agent templates as consolidation target category: `**Agent templates** → agent-core/agents/*.md: Execution patterns, tool usage, error handling, domain-specific guidance`
- Add selection criteria: learning is actionable for a specific agent role (execution pattern, stop condition, tool preference, error handling heuristic)
- List eligible agents (13) and exclusion rule (plan-specific)

**Target 2:** `agent-core/skills/remember/references/consolidation-patterns.md`
- Add "Agent-Specific" subsection under "Target Selection by Domain" (after line 30)
- Pattern: learnings about agent execution behavior → append to matching agent definition
- Example routing: "haiku rationalizes test failures" → test-driver.md; "step agents leave uncommitted files" → artisan.md

**Validation:** Read both files, verify agent routing section present with examples.

**Phase 3 Checkpoint:** `just precommit` passes.

---

### Phase 4: Recall CLI Code (type: tdd, model: sonnet)

Rewrite Click command for one-arg syntax with batched recall.

**Files:** `src/claudeutils/when/cli.py`, `tests/test_when_cli.py`, `agent-core/bin/when-resolve.py`
**Baseline:** 5 existing tests, all passing. Resolver (`src/claudeutils/when/resolver.py`) signature unchanged — CLI parses operator, calls `resolve(operator, query, ...)` as before.

## Cycle 4.1: One-arg syntax replaces two-arg

**RED:**
- New test: `test_single_arg_query_parsed`
- Invoke: `["when", "when writing mock tests"]` (single arg with operator prefix)
- Assert: resolve() called with operator="when", query="writing mock tests"
- Expected failure: CLI expects separate operator arg, "when writing mock tests" is invalid Choice value

**Verify RED:** `just test tests/test_when_cli.py::test_single_arg_query_parsed -v`

**GREEN:**
- Rewrite Click command: remove `operator` argument, change `query` to variadic args each containing operator prefix, parse prefix from each query string
- Call resolve() with parsed operator and remaining query
- Update all 5 existing tests to new invocation syntax (same behavioral contract, new API surface)
- Update docstring comment in `agent-core/bin/when-resolve.py` to reflect new invocation: `Usage: when-resolve.py "when <query>" ["how <query>" ...]`. No code change needed — entry point delegates to Click, which handles all arg parsing.

**Verify GREEN:** `just test tests/test_when_cli.py -v`
**Verify no regression:** `just test -v`

---

## Cycle 4.2: Batched recall

**RED:**
- New test: `test_batched_recall_multiple_queries`
- Invoke: `["when", "when writing mock tests", "how encode paths"]`
- Assert: resolve() called twice (once per query), output contains both results separated by `\n---\n`
- Expected failure: After 4.1, CLI processes first query only, ignores rest

**Verify RED:** `just test tests/test_when_cli.py::test_batched_recall_multiple_queries -v`

**GREEN:**
- Implement batch loop: iterate queries, collect results, join with separator
- Single query = no separator (backward compatible output)

**Verify GREEN:** `just test tests/test_when_cli.py -v`
**Verify no regression:** `just test -v`

---

## Cycle 4.3: Invalid prefix rejection

**RED:**
- New test: `test_invalid_prefix_rejected`
- Invoke: `["when", "no prefix query"]`
- Assert: exit code != 0, error message mentions "when" or "how" prefix required
- Expected failure: No prefix validation on query strings (old CLI had Click.Choice)

**Verify RED:** `just test tests/test_when_cli.py::test_invalid_prefix_rejected -v`

**GREEN:**
- Add prefix validation: query must start with `when ` or `how ` (case-insensitive)
- Error: state what IS wrong, no recovery suggestions

**Verify GREEN:** `just test tests/test_when_cli.py -v`
**Verify no regression:** `just test -v`

**Phase 4 Checkpoint:** `just precommit` passes. Verify dot-prefix modes still work (covered by existing test migration in 4.1).

---

### Phase 5: Recall CLI Docs Update (type: inline, model: opus)

Update invocation examples in 4 skill/decision files from two-arg to one-arg syntax.

Load `/plugin-dev:skill-development` before editing skill files.

- Update `agent-core/skills/when/SKILL.md`: change all examples from `when-resolve.py when <query>` to `when-resolve.py "when <query>"`
- Update `agent-core/skills/how/SKILL.md`: same pattern — `when-resolve.py how <query>` to `when-resolve.py "how <query>"`
- Update `agent-core/skills/memory-index/SKILL.md`: update sub-agent invocation examples to one-arg syntax, add batched recall example
- Update `agents/decisions/project-config.md`: update `when-resolve.py` reference to new invocation convention

---

### Phase 6: Skill Rename to /codify (type: general, model: sonnet)

Mechanical rename — grep-and-replace across codebase. Sonnet sufficient (no architectural judgment, purely mechanical substitution despite touching skill files). Advisory: artifact-type override rule recommends opus for skill file edits, but this phase is pure text substitution with no semantic content changes — sonnet assignment is appropriate exception.

## Step 6.1: Rename directory and update all references

**Objective**: Rename /remember to /codify across the codebase.

**Implementation:**
- `mv agent-core/skills/remember agent-core/skills/codify`
- Grep-and-replace across ~30 files: `grep -r "remember" agent-core/ agents/ .claude/ plans/ --include="*.md" -l`
- Key files: SKILL.md name/description, handoff skill + references, session.md, memory-index SKILL.md, agent-core docs (README.md, migration-guide.md, general-workflow.md, shortcuts.md), review skill, reflect skill, plan files
- Update skill name in SKILL.md frontmatter: `name: codify`
- Update description: "This skill should be used when..." with `/codify` trigger

**Validation:** Grep for `/remember` returns only plan files and historical references.

---

## Step 6.2: Sync symlinks and verify completeness

**Objective**: Ensure skill discovery works after rename.

**Implementation:**
- Run `just sync-to-parent`
- Verify symlinks: `.claude/skills/codify` exists, `.claude/skills/remember` removed
- Grep verification: `grep -r "/remember" agent-core/ agents/ .claude/ --include="*.md"` — only historical references remain
- Note: requires session restart (skill directory change)

**Validation:** Symlinks correct, grep clean.

**Phase 6 Checkpoint:** `just precommit` passes. Grep clean.

---

### Phase 7: Frozen-Domain Analysis (type: inline, model: opus)

Independent of all other phases. Can run at any time.

- Evaluate four recall options against criteria (agent-independence, token cost, false positive rate, maintenance burden):
  - Status quo (agent invokes `/when`, 2.9% baseline)
  - PreToolUse hook (file path → entry mapping, inject via additionalContext)
  - Inline code comments (`# See: /when X`)
  - UserPromptSubmit topic detection (keyword scan → inject)
- Write analysis report to `plans/remember-skill-update/reports/frozen-domain-analysis.md`
- If hook recommended: note as separate task in session.md
