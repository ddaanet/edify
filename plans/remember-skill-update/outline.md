# Remember Skill Update — Outline

## Problem

Learning titles in `agents/learnings.md` are structurally constrained (≤5 words, H2 format) but semantically unconstrained. During consolidation, `/remember` must rephrase titles into symptom-oriented memory-index triggers — unreliable, adds drift risk, depends on agent judgment.

Separately, consolidated knowledge is indexed but rarely recalled. Agents don't invoke `/when` proactively (2.9% baseline recall), and rule files meant to bridge this gap are ignored.

## Approach

**Workstream 1: Title-Trigger Alignment** — Make learning titles trigger-compatible at creation time so consolidation derives triggers without rephrasing.

**Workstream 2: Frozen-Domain Recall Analysis** — Evaluate alternatives to rule files. Output: recommendation with analysis, not implementation.

## Workstream 1: Title-Trigger Alignment

**Three enforcement layers:**

1. **Structural validation (learnings.py)** — Precommit enforcement of trigger-compatible format:
   - When/How prefix required (`## When ...` or `## How to ...`)
   - Min 2 words (prevents single-word titles)
   - Current checks preserved: max 5 words, uniqueness, H2 format
   - Precommit integration: Runs in existing validation suite, blocks commits on violation
   - Test requirements: When/How prefix (pass/fail), min 2 words (pass/fail), existing checks preserved (regression)

2. **Semantic guidance (skill + handoff documentation)** — Agent-facing instructions:
   - Learning titles should be usable as triggers without modification
   - Describes situation agent encounters, not root cause/jargon
   - Anti-pattern/correct-pattern examples:
     - ❌ "transformation table" → ✅ "choosing review gate"
     - ❌ "prose gates" → ✅ "prevent skill steps from being skipped"
   - Updated in: remember skill SKILL.md, handoff skill
   - Handoff skill implementation: Add guidance in "Learnings Quality" section after line 47, enforce trigger framing when creating learning titles during session handoff, reject jargon/root-cause titles with suggested rephrase

3. **Pipeline alignment (consolidation protocol)** — Trigger derivation from title:
   - Remember skill Step 4a: trigger = operator prefix + learning title (no rephrase)
   - Remove "rephrase for discovery" logic from consolidation protocol
   - compress-key.py validates against title text directly

**Phase types:** TDD for validation code (learnings.py), general for skill/agent documentation updates.

## Workstream 2: Frozen-Domain Recall Analysis

**Options:**

| Option | Mechanism | Reliability | Token Cost | Maintenance |
|--------|-----------|-------------|------------|-------------|
| Status quo | Agent invokes `/when` | 2.9% baseline | Zero | None |
| PreToolUse hook | Edit/Write hook maps file paths → entries, injects via additionalContext | High (code, not suggestion) | Per-edit overhead | Path mapping table |
| Inline code comments | `# See: /when X` in source code | Medium (visible when reading code) | Zero | Comment rot risk |
| UserPromptSubmit topic detection | Keyword scan → inject relevant entries | Medium (fires on every prompt) | Per-prompt overhead | Keyword mapping |

**Evaluation criteria:** Agent-independence (works without cooperation), token cost, false positive rate, maintenance burden.

**Output:** Analysis table with recommendation in dedicated design.md section "Frozen-Domain Recall Analysis". If hook-based, implementation as separate task.

## Key Decisions

1. ~~**Hyphen handling:**~~ **Resolved — allow hyphens.** Memory-index already uses hyphens in 30+ triggers. SKILL.md line 65 "no hyphens" is unenforced and contradicted by practice. No format incompatibility exists.
2. ~~**Existing title migration:**~~ **Resolved — already done.** All 54 current titles use `When` prefix format. No migration needed.
3. **Agent duplication:** remember-task.md manually mirrors SKILL.md steps. **Resolved by FR-8:** remember-task agent deleted, consolidation executes inline. Duplication eliminated.
4. **Frozen-domain priority:** Invest in hook infrastructure or accept 2.9% baseline? Resolution: Defer to Workstream 2 analysis output. If hook recommended, becomes separate task with own design/runbook.

## Implementation Phasing

**Phase 1: TDD Validation (type: tdd)**
- Implement structural validation in `src/claudeutils/validation/learnings.py`
- Tests in `tests/test_validation_learnings.py` (7 existing tests)
- Test requirements: When/How prefix (pass/fail), min 2 words (pass/fail), existing checks preserved (regression)
- Precommit integration via `src/claudeutils/validation/cli.py` (imports `validate_learnings`)

**Phase 2: Semantic Guidance + Pipeline Simplification (type: general)**
- Update `agent-core/skills/remember/SKILL.md`: title guidance, trigger derivation (Step 4a), inline execution in clean session (FR-8), inline file splitting with 400-line threshold and H2/H3 split boundaries (FR-9), run `validate-memory-index.py --fix` after splits, fix line 65 "no hyphens" (contradicts KD-1 resolution)
- Delete `agent-core/agents/remember-task.md` (FR-8)
- Delete `agent-core/agents/memory-refactor.md` (FR-9)
- Update `agent-core/skills/handoff/references/consolidation-flow.md`: remove delegation, invoke `/remember` inline in clean session
- Update handoff skill Step 4 with trigger framing enforcement
- Update `agent-core/skills/remember/references/consolidation-patterns.md` derivation protocol
- Remove `@agents/memory-index.md` from CLAUDE.md (~5000 tokens, 2.9% recall — not earning its context cost)

**Phase 3: Agent Routing for Learnings (type: general)**
- Add agent templates as consolidation targets in SKILL.md Step 2
- 13 eligible agents: artisan, brainstorm-name, corrector, design-corrector, hooks-tester, outline-corrector, refactor, runbook-corrector, runbook-outline-corrector, runbook-simplifier, scout, tdd-auditor, test-driver
- Excluded: plan-specific agents (generated per-runbook by prepare-runbook.py)
- Consolidation identifies agent-relevant learnings (execution patterns, tool usage, error handling)
- Relevant entries propagated to matching agent files

**Phase 4: Recall CLI Fix (type: tdd)**
- Replace two-argument convention (`when-resolve.py when <query>`) with one-argument-by-recall syntax (`when-resolve.py "when <query>"`)
- Operator parsed from query string prefix (when/how)
- Add batched recall: `when-resolve.py "when X" "how Y" "when Z"`
- Update `/when` and `/how` skill docs with new invocation syntax
- Update `agent-core/skills/memory-index/SKILL.md` — sub-agent recall skill, uses two-arg convention in examples
- Update `agents/decisions/project-config.md` — references `when-resolve.py` invocation
- Tests: `tests/test_when_cli.py` (5 existing tests, all use two-arg convention — must be rewritten)
- Code: `src/claudeutils/when/cli.py` (Click command), `agent-core/bin/when-resolve.py` (entry point), `src/claudeutils/when/resolver.py` (resolve function — check if signature needs changes for batch)

**Phase 5: Skill Rename to `/codify` (type: general)**
- Rename `/remember` skill directory to `codify`
- Update all references across codebase (~30 files): SKILL.md, handoff skill + references, consolidation-flow, session.md, memory-index triggers, `agent-core/README.md`, `agent-core/docs/shortcuts.md`, `agent-core/docs/migration-guide.md`, `agent-core/docs/general-workflow.md`, `agent-core/skills/review/SKILL.md`, `agent-core/skills/reflect/SKILL.md`, `agent-core/skills/memory-index/SKILL.md`, plan files referencing `/remember`
- Grep verification: `grep -r "remember" agent-core/ agents/ .claude/ --include="*.md"` for completeness
- `just sync-to-parent`, verify symlinks
- Requires restart

**Phase 6: Frozen-Domain Analysis (type: general)**
- Evaluate four options against criteria (agent-independence, token cost, false positive rate, maintenance)
- Write analysis section in design.md with recommendation
- If hook recommended: create separate task for implementation

**Dependencies:**
- Phase 2 depends on Phase 1 (documentation references validation constraints)
- Phase 3 depends on Phase 2 (routing targets defined after pipeline simplification)
- Phase 4 is independent (CLI fix, no dependency on other phases)
- Phase 5 depends on Phase 2-3 (rename after content changes, not before)
- Phase 6 is independent, can run in parallel with Phase 1-5

## Scope

**IN:**
- `src/claudeutils/validation/learnings.py` + `tests/test_validation_learnings.py` — When/How prefix, min 2 words
- `src/claudeutils/validation/cli.py` — precommit integration (imports validate_learnings)
- `agent-core/skills/remember/SKILL.md` — title guidance, trigger derivation, inline execution (FR-8), inline splitting (FR-9), fix "no hyphens" (line 65)
- `agent-core/agents/remember-task.md` — **delete** (FR-8)
- `agent-core/agents/memory-refactor.md` — **delete** (FR-9)
- `agent-core/skills/remember/references/consolidation-patterns.md` — derivation protocol
- `agent-core/skills/handoff/references/consolidation-flow.md` — remove delegation
- Handoff skill — title creation guidance, trigger framing
- CLAUDE.md — remove `@agents/memory-index.md` reference
- 13 agent templates (all except plan-specific) — learnings routing targets (FR-11)
- `src/claudeutils/when/cli.py` + `src/claudeutils/when/resolver.py` + `agent-core/bin/when-resolve.py` — one-arg syntax, batched recall
- `tests/test_when_cli.py` — rewrite for new invocation convention
- `agent-core/skills/when/SKILL.md` + `agent-core/skills/how/SKILL.md` + `agent-core/skills/memory-index/SKILL.md` — updated invocation docs
- `agents/decisions/project-config.md` — update when-resolve.py reference
- Skill directory rename to `codify` + all references (~30 files) (FR-10)
- Frozen-domain analysis section in design.md

**OUT:**
- Memory index validation pipeline changes
- Hook implementation for frozen-domain (separate task if recommended)
- `agent-core/bin/compress-key.py` — unchanged

## Context References

**Decision files (design rationale):**
- `agents/decisions/workflow-advanced.md` — trigger naming convention, seeding indexes, adding entries without documentation
- `agents/decisions/project-config.md` — memory index growth policy (append-only, no pruning), rule file injection, sub-agent memory recall via Bash transport, agent context augmentation (always-inject vs on-demand)
- `agents/decisions/implementation-notes.md` — DO NOT rules in skills, skill editing constraints
- `agents/decisions/prompt-structure-research.md` — fragment ordering and position bias (informs removing memory-index from CLAUDE.md)

**Empirical evidence (learnings):**
- "When evaluating recall system effectiveness" — 2.9% baseline, 801-session study, `/when` invoked in 4.1% of sessions
- "When assessing fragment demotion from always-loaded context" — ~5000 tokens, passive content not earning context cost
- "When designing CLI tools for LLM callers" — structured format over CLI conventions for LLM-sole-caller tools
- "When editing skill files" — must load `/plugin-dev:skill-development` before edits

**Existing research:**
- `plans/remember-skill-update/reports/explore-remember-skill.md`
- `plans/remember-skill-update/reports/outline-review.md`

**Skill internals (current implementation):**
- `agent-core/skills/remember/examples/remember-patterns.md` — usage patterns
- `agent-core/skills/handoff/references/learnings.md` — handoff-specific patterns
- `agent-core/skills/handoff/references/consolidation-flow.md` — current delegation flow

**Platform guides (editing constraints):**
- `/plugin-dev:skill-development` — skill description format ("This skill should be used when..."), structure rules
- `/plugin-dev:agent-development` — agent frontmatter, triggering conditions
