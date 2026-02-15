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
   - Min 2 words (prevents single-word titles)
   - No special characters beyond alphanumeric + spaces (trigger format compatibility)
   - Current checks preserved: max 5 words, uniqueness, H2 format
   - Precommit integration: Runs in existing validation suite, blocks commits on violation
   - Test requirements: Min 2 words (pass/fail), special char detection (pass/fail), existing checks preserved (regression)

2. **Semantic guidance (skill + handoff documentation)** — Agent-facing instructions:
   - Learning titles should be usable as triggers without modification
   - Describes situation agent encounters, not root cause/jargon
   - Anti-pattern/correct-pattern examples from session's 24 key renames:
     - ❌ "transformation table" → ✅ "choosing review gate"
     - ❌ "prose gates" → ✅ "prevent skill steps from being skipped"
   - Updated in: remember skill SKILL.md, remember-task agent (consolidation protocol Step 4a, reporting format discovery updates section), handoff skill
   - Handoff skill implementation: Add guidance in "Learnings Quality" section after line 47, enforce trigger framing when creating learning titles during session handoff, reject jargon/root-cause titles with suggested rephrase

3. **Pipeline alignment (consolidation protocol)** — Trigger derivation from title:
   - Remember skill Step 4a: trigger = operator prefix + learning title (no rephrase)
   - Remove "rephrase for discovery" logic from consolidation protocol
   - compress-key.py validates against title text directly
   - remember-task agent mirrors the change

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

1. **Hyphen handling:** Current titles use hyphens (e.g., "zero-ambiguity"). Enforce no-hyphens (breaking) or allow (weaker alignment)? Impact: existing learnings.md has hyphenated titles, memory-index trigger format excludes hyphens — this is data migration issue. Resolution: Decide during Phase 1 (TDD validation) implementation — recommend allowing hyphens in learning titles (current usage), enforcing no-hyphens only in memory-index triggers (already required).
2. **Existing title migration:** Migrate current learnings to new format or grandfather? Resolution: Grandfather existing titles (no migration), new titles must conform. Enforcement starts at commit after validation implementation.
3. **Agent duplication:** remember-task.md manually mirrors SKILL.md steps. Fix duplication or maintain? Resolution: User decision required — fixing duplication adds complexity, maintaining risks drift. Recommend: maintain for now, document as tech debt.
4. **Frozen-domain priority:** Invest in hook infrastructure or accept 2.9% baseline? Resolution: Defer to Workstream 2 analysis output. If hook recommended, becomes separate task with own design/runbook.

## Implementation Phasing

**Phase 1: TDD Validation (type: tdd)**
- Implement structural validation in `src/claudeutils/validation/learnings.py`
- Test requirements: min 2 words, special char detection, existing checks preserved
- Resolve Key Decision #1 (hyphen handling) during implementation
- Precommit integration verification

**Phase 2: Semantic Guidance (type: general)**
- Update `agent-core/skills/remember/SKILL.md` Step 4a with trigger derivation protocol
- Update `agent-core/agents/remember-task.md` consolidation protocol Step 4a and reporting format
- Update handoff skill "Learnings Quality" section with trigger framing enforcement
- Update `agent-core/skills/remember/references/consolidation-patterns.md` derivation protocol

**Phase 3: Frozen-Domain Analysis (type: general)**
- Evaluate four options against criteria (agent-independence, token cost, false positive rate, maintenance)
- Write analysis section in design.md with recommendation
- If hook recommended: create separate task for implementation

**Dependencies:**
- Phase 2 should reference Phase 1 validation constraints (validation must exist before documentation references it)
- Phase 3 is independent, can run in parallel with Phase 1-2

## Scope

**IN:**
- `src/claudeutils/validation/learnings.py` + tests — new structural checks
- `agent-core/skills/remember/SKILL.md` — title guidance, trigger derivation
- `agent-core/agents/remember-task.md` — matching updates
- `agent-core/skills/remember/references/consolidation-patterns.md` — derivation protocol
- Handoff skill — title creation guidance
- Frozen-domain analysis section in design.md

**OUT:**
- `/when` runtime resolution changes
- Memory index validation pipeline changes
- Hook implementation for frozen-domain (separate task if recommended)
- Learning content migration (existing titles grandfathered unless decided otherwise)
- `agent-core/bin/compress-key.py` — validation logic unchanged, usage context shifts to title-based validation instead of post-consolidation trigger compression
