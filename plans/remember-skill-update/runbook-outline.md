# Remember Skill Update — Runbook Outline

## Requirements Mapping

| Requirement | Phase | Items |
|-------------|-------|-------|
| FR-1: When/How prefix | 1 | Cycle 1.1 |
| FR-2: Min 2 content words | 1 | Cycle 1.2 |
| FR-3: Precommit enforcement | 1 | Cycles 1.1-1.3 (validate() changes propagate via cli.py) |
| FR-4: Mechanical consolidation | 2 | Step 2.1 (trigger derivation), Step 2.3 (consolidation-patterns) |
| FR-5: Semantic guidance | 2 | Steps 2.1, 2.4 |
| FR-8: Inline execution, remove delegation | 2 | Steps 2.1, 2.2, 2.5 |
| FR-9: Inline splitting, remove delegation | 2 | Steps 2.1, 2.5 |
| FR-10: Rename to /codify | 6 | Steps 6.1-6.2 |
| FR-11: Agent routing | 3 | Step 3.1 |
| FR-12: Recall CLI simplification | 4, 5 | Cycles 4.1-4.3 (code), Phase 5 (docs) |
| FR-13: Remove memory-index from CLAUDE.md | 2 | Step 2.5 |

## Key Decisions Reference

- KD-1: Hyphens allowed (resolved — 30+ existing triggers use hyphens)
- KD-2: Migration already done (all 54 titles use When prefix)
- KD-3: Agent duplication eliminated by FR-8 (delete remember-task)
- KD-4: Frozen-domain deferred to Phase 7 analysis
- Content words: "min 2 words" means 2 content words after stripping prefix

## Dependencies

```
Phase 1 → Phase 2 → Phase 3 → Phase 6
Phase 4 → Phase 5 → Phase 6
Phase 7 (independent)
```

Phase 4 and Phase 7 can start in parallel with Phase 1.
Phase 6 waits on Phases 3 and 5 (all content changes settled before rename).

---

### Phase 1: TDD Validation (type: tdd, model: sonnet)

Structural validation in `src/claudeutils/validation/learnings.py`. Three new checks added to existing `validate()` function.

**Files:** `src/claudeutils/validation/learnings.py`, `tests/test_validation_learnings.py`
**Baseline:** 7 existing tests, all passing. Precommit integration already wired in `src/claudeutils/validation/cli.py`.

- Cycle 1.1: When/How prefix required
  - RED: `test_title_without_prefix_returns_error` — title `## Bad Title` → error mentioning prefix requirement + line number
  - GREEN: Add prefix check in `validate()`. Title must start with `When ` or `How to `. Update 5 existing test fixtures to use prefixed titles while preserving their error conditions.
  - Regression: all 8 tests pass

- Cycle 1.2: Min 2 content words after prefix
  - RED: `test_insufficient_content_words_returns_error` — title `## When testing` (1 content word) → error mentioning content words + line number
  - GREEN: Strip prefix, count remaining words, require ≥2. Implementation: if title starts with `How to `, content = words[2:]; if `When `, content = words[1:]. Check `len(content) < 2`.
  - Regression: all 9 tests pass

- Cycle 1.3: Edge cases and combined validation
  - RED: Three new tests:
    - `test_how_to_prefix_accepted` — `## How to encode paths` (2 content words) → passes
    - `test_how_without_to_rejected` — `## How encode` → prefix error (not `How to`)
    - `test_combined_errors_reported` — file with `## When testing` (prefix OK, 1 content word → content error) and `## Bad` (prefix error) → both errors reported
  - GREEN: Verify implementation handles all cases. `How ` without `to` fails prefix check.
  - Regression: all 12 tests pass

**Checkpoint:** `just precommit` — validates new checks propagate through CLI.

---

### Phase 2: Semantic Guidance + Pipeline Simplification (type: general, model: opus)

Prose edits to skills, agents, and CLAUDE.md. All decisions pre-resolved.

**Note:** SKILL.md also edited in Phase 3 (agent routing). Phase 3 depends on Phase 2 completion.

- Step 2.1: Update remember SKILL.md
  - Target: `agent-core/skills/remember/SKILL.md`
  - Prerequisite: Read current SKILL.md (already done in discovery)
  - Changes:
    - **Title guidance (FR-5):** Add section after "Learnings Quality Criteria" (line 76): titles must start with "When"/"How to", min 2 content words after prefix, anti-pattern/correct-pattern examples per FR-5
    - **Trigger derivation (FR-4):** Update Step 4a (line 59): trigger = operator prefix + learning title (mechanical, no rephrasing). Remove "Optimize for discovery" guidance (line 67) — title IS the trigger
    - **Inline execution (FR-8):** Add prerequisite note: skill executes in calling session, requires clean session (fresh start). Remove any delegation references
    - **Inline splitting (FR-9):** Add to Step 4: after Write/Edit to decision file, check line count; if >400, split by H2/H3 boundaries into 100-300 line sections; run `validate-memory-index.py --fix` after split
    - **Fix "no hyphens" (KD-1):** Remove "no hyphens or special characters" from line 65 — contradicts practice (30+ triggers use hyphens)

- Step 2.2: Update consolidation-flow.md
  - Target: `agent-core/skills/handoff/references/consolidation-flow.md`
  - Replace delegation flow (lines 7-10: filter → batch check → delegate to remember-task → read report) with inline flow: invoke `/remember` skill in clean session
  - Replace refactor flow (lines 16-19: delegate to memory-refactor) with inline instructions matching FR-9
  - Preserve error handling section (lines 24-27)

- Step 2.3: Update consolidation-patterns.md derivation protocol
  - Target: `agent-core/skills/remember/references/consolidation-patterns.md`
  - Update Memory Index Maintenance section (line 64): trigger derived mechanically from title — `## When X Y` → `/when x y` (lowercase, no rephrasing)
  - Remove "Trigger naming" optimization guidance that implies agent judgment

- Step 2.4: Update handoff skill Step 4 with trigger framing
  - Target: `agent-core/skills/handoff/SKILL.md` (lines 101-107)
  - Strengthen line 105: titles must start with "When" or "How to", min 2 content words after prefix
  - Add: reject jargon/root-cause titles, suggest rephrasing to situation description
  - Add examples: ❌ "transformation table" → ✅ "choosing review gate"; ❌ "prose gates" → ✅ "prevent skill steps from being skipped"

- Step 2.5: Remove deprecated artifacts (FR-8, FR-9, FR-13)
  - Delete `agent-core/agents/remember-task.md` (FR-8)
  - Delete `agent-core/agents/memory-refactor.md` (FR-9)
  - Remove `@agents/memory-index.md` reference from `CLAUDE.md` line 49 (~5000 tokens, 2.9% recall — FR-13)
  - File `agents/memory-index.md` remains (used by when-resolve.py)
  - Verify no other files reference deleted agents (grep `remember-task` and `memory-refactor`)

**Checkpoint:** `just precommit` passes. Verify deleted agents not referenced elsewhere.

---

### Phase 3: Agent Routing for Learnings (type: general, model: opus)

Add agent templates as consolidation targets.

**Eligible agents (13):** artisan, brainstorm-name, corrector, design-corrector, hooks-tester, outline-corrector, refactor, runbook-corrector, runbook-outline-corrector, runbook-simplifier, scout, tdd-auditor, test-driver

**Excluded:** plan-specific agents (generated per-runbook by prepare-runbook.py), remember-task (deleted), memory-refactor (deleted)

- Step 3.1: Add agent routing to remember skill (SKILL.md + consolidation-patterns.md)
  - Target 1: `agent-core/skills/remember/SKILL.md` Step 2 "File Selection" (line 26)
    - Add agent templates as consolidation target category: `**Agent templates** → agent-core/agents/*.md: Execution patterns, tool usage, error handling, domain-specific guidance`
    - Add selection criteria: learning is actionable for a specific agent role (execution pattern, stop condition, tool preference, error handling heuristic)
    - List eligible agents (13) and exclusion rule (plan-specific)
  - Target 2: `agent-core/skills/remember/references/consolidation-patterns.md`
    - Add "Agent-Specific" subsection under "Target Selection by Domain" (after line 30)
    - Pattern: learnings about agent execution behavior → append to matching agent definition
    - Example routing: "haiku rationalizes test failures" → test-driver.md; "step agents leave uncommitted files" → artisan.md

**Checkpoint:** `just precommit` passes.

---

### Phase 4: Recall CLI Code (type: tdd, model: sonnet)

Rewrite Click command for one-arg syntax with batched recall.

**Files:** `src/claudeutils/when/cli.py`, `tests/test_when_cli.py`, `agent-core/bin/when-resolve.py`
**Baseline:** 5 existing tests, all passing. Resolver (`src/claudeutils/when/resolver.py`) signature unchanged — CLI parses operator, calls `resolve(operator, query, ...)` as before.

- Cycle 4.1: One-arg syntax replaces two-arg
  - RED: `test_single_arg_query_parsed` — invoke `["when", "when writing mock tests"]` (single arg with operator prefix) → resolve() called with operator="when", query="writing mock tests"
  - GREEN: Rewrite Click command: remove `operator` argument, change `query` to variadic args each containing operator prefix, parse prefix from each query string. Update all 5 existing tests to new invocation syntax (same behavioral contract, new API surface). Update `agent-core/bin/when-resolve.py` if entry point args change.
  - Regression: all 6 tests pass

- Cycle 4.2: Batched recall
  - RED: `test_batched_recall_multiple_queries` — invoke `["when", "when writing mock tests", "how encode paths"]` → resolve() called twice, output contains both results separated by `\n---\n`
  - GREEN: Implement batch loop: iterate queries, collect results, join with separator. Single query = no separator (backward compatible output).
  - Regression: all 7 tests pass

- Cycle 4.3: Invalid prefix rejection
  - RED: `test_invalid_prefix_rejected` — invoke `["when", "no prefix query"]` → exit code != 0, error message mentions "when" or "how" prefix required
  - GREEN: Add prefix validation: query must start with `when ` or `how ` (case-insensitive). Error: state what IS wrong, no recovery suggestions.
  - Regression: all 8 tests pass

**Checkpoint:** `just precommit` passes. Verify dot-prefix modes still work (covered by existing test migration in 4.1).

---

### Phase 5: Recall CLI Docs Update (type: inline, model: opus)

Update invocation examples in 4 skill/decision files from two-arg to one-arg syntax.

- Update `agent-core/skills/when/SKILL.md`: change all examples from `when-resolve.py when <query>` to `when-resolve.py "when <query>"`
- Update `agent-core/skills/how/SKILL.md`: same pattern — `when-resolve.py how <query>` to `when-resolve.py "how <query>"`
- Update `agent-core/skills/memory-index/SKILL.md`: update sub-agent invocation examples to one-arg syntax, add batched recall example
- Update `agents/decisions/project-config.md`: update `when-resolve.py` reference to new invocation convention

---

### Phase 6: Skill Rename to /codify (type: general, model: sonnet)

Mechanical rename — grep-and-replace across codebase. Sonnet sufficient (no architectural judgment, purely mechanical substitution despite touching skill files).

- Step 6.1: Rename directory and update all references
  - `mv agent-core/skills/remember agent-core/skills/codify`
  - Grep-and-replace across ~30 files: `grep -r "remember" agent-core/ agents/ .claude/ plans/ --include="*.md" -l`
  - Key files: SKILL.md name/description, handoff skill + references, session.md, memory-index SKILL.md, agent-core docs (README.md, migration-guide.md, general-workflow.md, shortcuts.md), review skill, reflect skill, plan files
  - Update skill name in SKILL.md frontmatter: `name: codify`
  - Update description: "This skill should be used when..." with `/codify` trigger

- Step 6.2: Sync symlinks and verify completeness
  - Run `just sync-to-parent`
  - Verify symlinks: `.claude/skills/codify` exists, `.claude/skills/remember` removed
  - Grep verification: `grep -r "/remember" agent-core/ agents/ .claude/ --include="*.md"` should return only historical references (plan files, git history mentions)
  - Note: requires session restart (skill directory change)

**Checkpoint:** `just precommit` passes. Grep clean.

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

---

## Expansion Guidance

**Phase 1:** Test plan already prepared in `plans/remember-skill-update/tdd-test-plan.md`. Cycle descriptions reference it. Key: Cycle 1.1 GREEN must update 5 existing test fixtures simultaneously.

**Phase 2:** Steps 2.1-2.5 are all prose edits. Step 2.1 is largest (5 changes to SKILL.md). Step 2.5 batches three trivial removals (2 agent deletions + CLAUDE.md reference removal).

**Phase 3:** Single step updating two files in the same skill module. Small phase, kept separate from Phase 2 due to dependency (Phase 3 needs Phase 2's pipeline simplification complete before defining routing targets).

**Phase 4:** Test plan prepared. Key risk: Cycle 4.1 GREEN rewrites Click command AND migrates all 5 existing tests.

**Phase 5:** 4 files, mechanical substitution of invocation examples. Pattern: `when-resolve.py {when|how} <query>` → `when-resolve.py "{when|how} <query>"`.

**Phase 6:** Pattern: `grep -rl` to find files, `sed` for mechanical replacement. Verify: `grep -r` for residual references.

**Phase 7:** Analysis writing. Outline's options table (from design) provides the framework.

## Context References

**Design documents:**
- `plans/remember-skill-update/outline.md` — source outline with all FRs
- `plans/remember-skill-update/requirements.md` — acceptance criteria
- `plans/remember-skill-update/tdd-test-plan.md` — Phase 1 and 4 test plans

**Decision files (rationale):**
- `agents/decisions/workflow-advanced.md` — trigger naming
- `agents/decisions/project-config.md` — memory index growth, rule injection, sub-agent recall
- `agents/decisions/implementation-notes.md` — skill editing constraints
- `agents/decisions/prompt-structure-research.md` — position bias (informs FR-13)

**Platform guides (editing constraints):**
- `/plugin-dev:skill-development` — must load before editing skill files
- `/plugin-dev:agent-development` — agent frontmatter rules

**Existing exploration:**
- `plans/remember-skill-update/reports/explore-remember-skill.md`
