# Outline Review: remember-skill-update (Round 2)

**Artifact**: plans/remember-skill-update/outline.md
**Requirements**: plans/remember-skill-update/requirements.md
**TDD Test Plan**: plans/remember-skill-update/tdd-test-plan.md
**Date**: 2026-02-23
**Mode**: review + fix-all

## Summary

Outline covers all 12 active FRs (FR-1 through FR-13, excluding struck FR-7) across 6 phases. Phase types are correctly assigned (tdd for Phases 1 and 4, general for 2, 3, 5, 6). Dependencies are valid with no circular or forward dependencies. Two issues required fixes: an incorrect file reference for the handoff skill edit location, and a non-existent output path for the frozen-domain analysis. A requirements mapping table was added.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Items | Coverage | Notes |
|-------------|-------|-------|----------|-------|
| FR-1 | 1, 2 | P1: prefix check; P2: SKILL.md guidance | Complete | Structural + semantic enforcement |
| FR-2 | 1 | Min 2 content words, prefix, regression | Complete | All validation in learnings.py |
| FR-3 | 1 | Precommit via cli.py | Complete | Existing import, new checks propagate |
| FR-4 | 2 | SKILL.md Step 4a, consolidation-patterns | Complete | Trigger = title, no rephrase |
| FR-5 | 2 | SKILL.md guidance, handoff Step 4 | Complete | Anti-pattern examples |
| FR-6 | 6 | Analysis report | Complete | Output: reports/frozen-domain-analysis.md |
| ~~FR-7~~ | -- | -- | N/A | Struck: migration already done |
| FR-8 | 2 | Delete remember-task, SKILL.md inline exec | Complete | Consolidation inline |
| FR-9 | 2 | Delete memory-refactor, SKILL.md inline split | Complete | 400-line threshold |
| FR-10 | 5 | Directory rename + ~30 references | Complete | Grep verification + restart |
| FR-11 | 3 | SKILL.md Step 2, 13 agents | Complete | Agent-relevant learnings |
| FR-12 | 4 | cli.py rewrite, tests, docs | Complete | One-arg + batch |
| FR-13 | 2 | Remove @agents/memory-index.md from CLAUDE.md | Complete | ~5000 tokens freed |

**Coverage Assessment**: All 12 active requirements mapped to specific phases and items.

## Phase Structure Analysis

### Phase Balance

| Phase | Items | Type | Key Files | Assessment |
|-------|-------|------|-----------|------------|
| 1 | 3 TDD cycles + precommit verify | tdd | learnings.py, test_validation_learnings.py | Balanced |
| 2 | 7 items (1 heavy SKILL.md edit, 2 deletes, 4 updates) | general | SKILL.md, agents, consolidation-flow, handoff, CLAUDE.md | Heaviest phase; defensible grouping |
| 3 | 4 items | general | SKILL.md (additive), 13 agent files | Balanced |
| 4 | 3 TDD cycles + 3 doc updates | tdd | cli.py, when-resolve.py, test_when_cli.py, skill docs | Balanced |
| 5 | 4 items (rename + refs + grep + sync) | general | ~30 files | Balanced |
| 6 | 3 items | general | Analysis report | Light; appropriate for research output |

**Balance Assessment**: Phase 2 is the densest but items are thematically cohesive (pipeline simplification + semantic guidance). No phase exceeds 8 items.

### Phase Types

- Phase 1: tdd -- correct (behavioral code in learnings.py)
- Phase 2: general -- correct (prose/config edits, deletions)
- Phase 3: general -- correct (prose additions to agent files)
- Phase 4: tdd -- correct (behavioral code in cli.py)
- Phase 5: general -- correct (mechanical rename propagation)
- Phase 6: general -- correct (research/analysis output)

### Dependencies

```
Phase 1 (foundation)
  |
  v
Phase 2 (references validation constraints)
  |
  v
Phase 3 (routing targets from Phase 2)
  |
  v
Phase 5 (rename after content settles)

Phase 4 (independent, parallel with 1-3)
Phase 6 (independent, parallel with 1-5)
```

No circular dependencies. No forward dependencies within phases. Foundation-first ordering verified.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Incorrect handoff skill insertion point reference**
   - Location: Workstream 1, Step 2 (line 33)
   - Problem: Referenced "Learnings Quality" section after line 47 in handoff SKILL.md. No such section exists. Handoff SKILL.md has Step 4 "Write Learnings" at line 101.
   - Fix: Updated to reference Step 4 "Write Learnings" (line 101) with specific guidance on what to add
   - **Status**: FIXED

2. **Non-existent output path for frozen-domain analysis**
   - Location: Workstream 2 output (line 55) and Phase 6 (line 107)
   - Problem: Referenced "design.md section" but no design.md exists in the plan directory. Output location was undefined.
   - Fix: Changed to `plans/remember-skill-update/reports/frozen-domain-analysis.md`. Updated Workstream 2 output description, Phase 6 item, and Scope IN section.
   - **Status**: FIXED

3. **Missing requirements mapping table**
   - Location: Between Dependencies and Scope sections
   - Problem: No formal FR-to-phase mapping existed. Coverage was implicit from phase descriptions but not traceable.
   - Fix: Added Requirements Mapping section with table covering all 12 active FRs
   - **Status**: FIXED

### Minor Issues

1. **Phase 4 mixes TDD cycles with general doc updates**
   - Location: Phase 4 items (lines 92-96)
   - Problem: Phase type is "tdd" but includes 3 doc update items (when/how SKILL.md, memory-index SKILL.md, project-config.md) that are general work.
   - Assessment: Acceptable. Doc updates reflect the new API and naturally follow TDD cycles. Splitting into a separate phase would create an unnecessary 1-phase gap.
   - Fix: Added expansion guidance noting TDD cycles precede doc updates within the phase
   - **Status**: FIXED (via expansion guidance)

2. **Phase 2 SKILL.md edit is dense (6 changes to one file)**
   - Location: Phase 2, first item (line 73)
   - Problem: Single SKILL.md edit bundles title guidance, trigger derivation, inline execution, inline splitting, validate-memory-index, and no-hyphens fix. Large scope for one item.
   - Fix: Added expansion guidance recommending split into 2 steps: (a) guidance/derivation/hyphens, (b) inline execution/splitting/validation
   - **Status**: FIXED (via expansion guidance)

3. **Missing expansion guidance section**
   - Location: End of outline
   - Problem: No guidance for runbook expansion agents on ordering, checkpoints, or known structural decisions.
   - Fix: Added comprehensive Expansion Guidance section covering Phase 2 ordering, handoff edit location, Phase 4 structure, Phase 3 SKILL.md exception, Phase 5 scope, checkpoints, and TDD test plan references
   - **Status**: FIXED

## Fixes Applied

- Line 33: Corrected handoff skill reference from "Learnings Quality section after line 47" to "Step 4 Write Learnings (line 101)"
- Line 55: Changed frozen-domain output from "design.md section" to `reports/frozen-domain-analysis.md`
- Line 107: Updated Phase 6 output path to match
- Line 135: Updated Scope IN to reference correct analysis report path
- After line 116: Added Requirements Mapping table (FR-1 through FR-13)
- After line 167: Added Expansion Guidance section (phase ordering, handoff edit, Phase 4 structure, SKILL.md exception, rename scope, checkpoints, TDD references)

## Verification Checks

**Unresolved decisions:** Grep for "choose between", "decide", "determine", "evaluate which" -- none found. All key decisions are resolved (KD-1 through KD-4).

**File references verified against codebase:**
- `src/claudeutils/validation/learnings.py` (80 lines) -- exists
- `tests/test_validation_learnings.py` (144 lines) -- exists
- `src/claudeutils/validation/cli.py` (32 lines) -- exists
- `agent-core/skills/remember/SKILL.md` (145 lines) -- exists
- `agent-core/agents/remember-task.md` -- exists (to be deleted)
- `agent-core/agents/memory-refactor.md` -- exists (to be deleted)
- `agent-core/skills/handoff/references/consolidation-flow.md` -- exists
- `agent-core/skills/handoff/SKILL.md` -- exists (Step 4 at line 101)
- `agent-core/skills/remember/references/consolidation-patterns.md` -- exists
- `src/claudeutils/when/cli.py` (32 lines) -- exists
- `src/claudeutils/when/resolver.py` -- exists
- `agent-core/bin/when-resolve.py` -- exists
- `tests/test_when_cli.py` (220 lines) -- exists
- `agent-core/skills/when/SKILL.md` -- exists
- `agent-core/skills/how/SKILL.md` -- exists
- `agent-core/skills/memory-index/SKILL.md` -- exists
- `agents/decisions/project-config.md` -- exists
- All 13 eligible agents verified on filesystem (15 total minus remember-task, memory-refactor)

**Agent list verified:** artisan, brainstorm-name, corrector, design-corrector, hooks-tester, outline-corrector, refactor, runbook-corrector, runbook-outline-corrector, runbook-simplifier, scout, tdd-auditor, test-driver -- all present in `agent-core/agents/`.

**Vacuity:** No vacuous items. Every phase produces a functional outcome (passing tests, file edits, deletions, analysis report).

**Forward dependencies:** None. Foundation-first ordering confirmed.

**Prose atomicity:** SKILL.md edited in Phases 2 and 3 -- acknowledged exception due to dependency (Phase 3 routing targets require Phase 2 pipeline simplification first). All other artifacts edited in exactly one phase.

**Self-modification ordering:** No pipeline tools are modified before they're used in the runbook. `when-resolve.py` (Phase 4) is an end-user tool, not used during execution.

## Positive Observations

- All 12 active FRs have explicit phase assignments with no gaps
- TDD test plan exists separately with detailed cycle definitions for both TDD phases
- Phase types correctly match content (behavioral code = tdd, prose/config = general)
- Independent phases (4, 6) enable parallel execution
- Context References section provides thorough discovery pointers for expansion agents
- Key decisions are all resolved with clear rationale

---

**Ready for full expansion**: Yes
