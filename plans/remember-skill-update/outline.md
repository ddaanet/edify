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
   - Min 2 content words after prefix (prevents vague triggers like "When testing")
   - Current checks preserved: max 5 words, uniqueness, H2 format
   - Precommit integration: Runs in existing validation suite, blocks commits on violation
   - Test requirements: When/How prefix (pass/fail), min 2 content words (pass/fail), existing checks preserved (regression)

2. **Semantic guidance (skill + handoff documentation)** — Agent-facing instructions:
   - Learning titles should be usable as triggers without modification
   - Describes situation agent encounters, not root cause/jargon
   - Anti-pattern/correct-pattern examples:
     - ❌ "transformation table" → ✅ "choosing review gate"
     - ❌ "prose gates" → ✅ "prevent skill steps from being skipped"
   - Updated in: remember skill SKILL.md, handoff skill
   - Handoff skill implementation: Strengthen Step 4 "Write Learnings" (line 101) with trigger framing rules — titles must start with When/How to, describe the situation not the root cause. Add anti-pattern/correct-pattern examples. Enforce rejection of jargon/root-cause titles with suggested rephrase

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

**Output:** Analysis report at `plans/remember-skill-update/reports/frozen-domain-analysis.md` with recommendation. If hook-based, implementation as separate task.

## Key Decisions

1. ~~**Hyphen handling:**~~ **Resolved — allow hyphens.** Memory-index already uses hyphens in 30+ triggers. SKILL.md line 65 "no hyphens" is unenforced and contradicted by practice. No format incompatibility exists.
2. ~~**Existing title migration:**~~ **Resolved — already done.** All 54 current titles use `When` prefix format. No migration needed.
3. **Agent duplication:** remember-task.md manually mirrors SKILL.md steps. **Resolved by FR-8:** remember-task agent deleted, consolidation executes inline. Duplication eliminated.
4. **Frozen-domain priority:** Invest in hook infrastructure or accept 2.9% baseline? Resolution: Defer to Workstream 2 analysis output. If hook recommended, becomes separate task with own design/runbook.

## Implementation Phasing

**Phase 1: TDD Validation (type: tdd)**
- Implement structural validation in `src/claudeutils/validation/learnings.py`
- Tests in `tests/test_validation_learnings.py` (7 existing tests)
- Test requirements: When/How prefix (pass/fail), min 2 content words (pass/fail), existing checks preserved (regression)
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
- Write analysis report at `plans/remember-skill-update/reports/frozen-domain-analysis.md` with recommendation
- If hook recommended: create separate task for implementation

**Dependencies:**
- Phase 2 depends on Phase 1 (documentation references validation constraints)
- Phase 3 depends on Phase 2 (routing targets defined after pipeline simplification)
- Phase 4 is independent (CLI fix, no dependency on other phases)
- Phase 5 depends on Phase 2-3 (rename after content changes, not before)
- Phase 6 is independent, can run in parallel with Phase 1-5

## Requirements Mapping

| Requirement | Phase | Items | Notes |
|-------------|-------|-------|-------|
| FR-1 | 1, 2 | P1: prefix check; P2: SKILL.md title guidance | Structural + semantic enforcement |
| FR-2 | 1 | Min 2 content words, prefix check, regression | All validation rules in learnings.py |
| FR-3 | 1 | Precommit integration via cli.py | Existing import path, new checks propagate |
| FR-4 | 2 | SKILL.md Step 4a, consolidation-patterns.md | Trigger = title, no rephrase |
| FR-5 | 2 | SKILL.md guidance, handoff Step 4 | Anti-pattern examples, rejection rules |
| FR-6 | 6 | Analysis report with recommendation | Output: reports/frozen-domain-analysis.md |
| ~~FR-7~~ | — | — | Struck: migration already done |
| FR-8 | 2 | Delete remember-task.md, SKILL.md inline exec | Consolidation executes inline |
| FR-9 | 2 | Delete memory-refactor.md, SKILL.md inline split | 400-line threshold, H2/H3 boundaries |
| FR-10 | 5 | Directory rename + ~30 file references | Grep verification, sync-to-parent, restart |
| FR-11 | 3 | SKILL.md Step 2, 13 agent templates | Agent-relevant learnings propagated |
| FR-12 | 4 | cli.py rewrite, when-resolve.py, tests | One-arg syntax + batched recall |
| FR-13 | 2 | Remove @agents/memory-index.md from CLAUDE.md | ~5000 tokens freed |

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
- `plans/remember-skill-update/reports/frozen-domain-analysis.md` — analysis report (FR-6)

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

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Phase 2 item ordering:**
- SKILL.md edits first (establishes the updated protocol), then deletions (remember-task.md, memory-refactor.md), then downstream references (consolidation-flow, handoff, consolidation-patterns), then CLAUDE.md cleanup last
- SKILL.md is the largest single edit in the outline (6 changes); consider splitting into 2 steps: (a) title guidance + trigger derivation + fix no-hyphens, (b) inline execution + inline splitting + validate-memory-index

**Phase 2 handoff skill edit:**
- Target is Step 4 "Write Learnings" at line 101 of `agent-core/skills/handoff/SKILL.md`
- No "Learnings Quality" section exists; guidance integrates into the existing Step 4 block
- Line 105 already says "Titles become `/when` triggers" — strengthen with format rules and examples, do not duplicate

**Phase 4 structure:**
- TDD cycles (4.1-4.3 per tdd-test-plan.md) precede doc updates
- Doc updates (when/how SKILL.md, memory-index SKILL.md, project-config.md) are post-TDD general steps within the same phase
- Phase type remains tdd; doc updates are non-code followup after all cycles green

**Phase 3 SKILL.md edit:**
- This is the known exception to single-artifact-per-item: SKILL.md is edited in both Phase 2 (protocol changes) and Phase 3 (routing targets)
- Phase 3 edit is additive (adding agent list to Step 2), not conflicting with Phase 2 edits (Steps 4a, inline exec, splitting)

**Phase 5 rename scope:**
- The ~30 file estimate needs verification at expansion time via `grep -r "/remember\b" agent-core/ agents/ .claude/ --include="*.md"`
- Include `agent-core/skills/remember/examples/remember-patterns.md` (internal reference file)
- Include `agent-core/skills/handoff/references/learnings.md` if it references `/remember`

**Checkpoint guidance:**
- Checkpoint after Phase 1 (TDD complete, precommit passes)
- Checkpoint after Phase 2 (all deletions + edits verified, no broken references)
- Phase 4 is independent; can checkpoint independently
- Phase 5 requires post-rename grep verification as final checkpoint

**TDD test plan:**
- Phases 1 and 4 have detailed cycle definitions in `plans/remember-skill-update/tdd-test-plan.md`
- Phase 1: 3 cycles (1.1 prefix, 1.2 min words, 1.3 edge cases), 5 new tests, 5 fixture updates
- Phase 4: 3 cycles (4.1 one-arg, 4.2 batch, 4.3 invalid prefix), 3 new tests, 5 rewrites
