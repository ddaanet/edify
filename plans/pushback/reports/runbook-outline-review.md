# Runbook Outline Review: Pushback

**Artifact**: plans/pushback/runbook-outline.md
**Design**: plans/pushback/design.md
**Requirements**: plans/pushback/requirements.md
**Date**: 2026-02-13T19:45:00Z
**Mode**: review + fix-all

## Summary

The runbook outline provides a solid three-phase structure for implementing the pushback mechanism (fragment creation, hook enhancement, wiring). All requirements are traced to specific phases with clear implementation notes. The outline correctly identifies Phase 2 as TDD-suitable with 5 testable cycles. Found 11 issues across critical/major/minor severity — all fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 1, 2 | 1.1, 2.4 | Complete | Fragment rules + hook counterfactual injection |
| FR-2 | 1 | 1.1 | Complete | Fragment self-monitoring rule for agreement momentum |
| FR-3 | 1 | 1.1 | Complete | Fragment Model Selection section |
| NFR-1 | 1 | 1.1 | Complete | Evaluator framing, "articulate WHY" rules |
| NFR-2 | 1, 2 | 1.1, 2.1-2.4 | Complete | Zero-cost fragment, string-only hook modification |

**Coverage Assessment**: All requirements covered with explicit phase and step mappings. Requirements mapping table enhanced with notes column explaining how each requirement is addressed.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps/Cycles | Complexity | Percentage | Assessment |
|-------|--------------|------------|------------|------------|
| 1 | 2 | Low | 22% | Balanced |
| 2 | 5 | Medium | 56% | Appropriate for TDD phase |
| 3 | 4 | Low | 22% | Balanced |

**Balance Assessment**: Well-balanced. Phase 2 is the largest at 56% but appropriate given TDD cycle structure (5 independent testable features). Phases 1 and 3 are low-complexity configuration work.

### Complexity Distribution

- **Low complexity phases**: 2 (Phase 1, Phase 3)
- **Medium complexity phases**: 1 (Phase 2)
- **High complexity phases**: 0

**Distribution Assessment**: Appropriate. No high-complexity phases — all design decisions resolved during design session. Phase 2 is Medium due to testable feature count, not conceptual difficulty.

## Review Findings

### Critical Issues

1. **Insufficient Step 1.1 Specification**
   - Location: Phase 1, Step 1.1
   - Problem: "Create pushback fragment" lacks enumeration of required content sections (Motivation, Design Discussion Evaluation, Agreement Momentum, Model Selection)
   - Fix: Expanded step to enumerate all four sections with brief descriptors from design
   - **Status**: FIXED

2. **Inverted Cycle Dependency Order**
   - Location: Phase 2, Cycles 2.2 and 2.3
   - Problem: Cycle 2.2 (any-line matching) listed before Cycle 2.3 (fenced block exclusion), but any-line matching depends on fenced block detection
   - Fix: Reordered cycles — 2.2 is now fenced block exclusion (foundation), 2.3 is any-line matching (depends on 2.2)
   - **Status**: FIXED

3. **Missing Test File Specification**
   - Location: Phase 2
   - Problem: 5 TDD cycles but no test file location/naming specified
   - Fix: Added test file specification: `agent-core/hooks/tests/test_userpromptsubmit_shortcuts.py` (new)
   - **Status**: FIXED

### Major Issues

4. **Step 1.2 Lacks Vet Execution Context**
   - Location: Phase 1, Step 1.2
   - Problem: "Vet fragment" without specifying what to check (deslop compliance, research grounding, fragment conventions)
   - Fix: Expanded to enumerate vet criteria: deslop compliance, research grounding application (evaluator framing, counterfactual structure, confidence calibration), fragment structural conventions
   - **Status**: FIXED

5. **Step 3.3 Behavioral Specification Missing**
   - Location: Phase 3, Step 3.3
   - Problem: "Manual validation" without listing the 4 scenarios from design Testing Strategy
   - Fix: Renumbered to Step 3.4, added all 4 scenarios with expected outcomes (good idea evaluation, flawed idea pushback, agreement momentum, model selection)
   - **Status**: FIXED

6. **Missing Checkpoint Between Phases**
   - Location: Phase 3 boundary
   - Problem: No explicit checkpoint before manual validation ensuring Phase 2 work is complete and committed
   - Fix: Added Step 3.3 checkpoint — verify Phase 2 tests pass, precommit clean, commit all changes before proceeding to manual validation
   - **Status**: FIXED

7. **Cycle 2.5 Ambiguous Scope**
   - Location: Phase 2, Cycle 2.5
   - Problem: "Integration test (all features together)" doesn't specify what combinations to test
   - Fix: Specified integration test scope: long-form alias + any-line matching + fenced exclusion work together, Tier 1 exact-match unchanged
   - **Status**: FIXED

### Minor Issues

8. **Requirements Mapping Lacks Notes Column**
   - Location: Requirements Mapping table
   - Problem: No explanatory notes showing how each requirement is addressed
   - Fix: Added Notes column with explanations for each requirement (fragment provides X, hook injects Y)
   - **Status**: FIXED

9. **Phase 3 File Count Discrepancy**
   - Location: Complexity per Phase table
   - Problem: Listed "2 (modify)" but Step 3.2 uses `just sync-to-parent` (not direct file modification) and Step 3.3/3.4 are validation steps
   - Fix: Updated to "1 (modify CLAUDE.md)" — symlink sync is a recipe invocation, not file count
   - **Status**: FIXED

10. **Missing Dependency Declarations**
   - Location: Phase 2 Items
   - Problem: Cycles 2.2, 2.3, 2.4 have dependencies but not explicitly declared
   - Fix: Added "Depends on:" annotations for cycles 2.3 (depends on 2.2) and 2.4 (depends on 2.3)
   - **Status**: FIXED

11. **Expansion Guidance Lacks TDD-Specific Details**
   - Location: Expansion Guidance, Phase 2 section
   - Problem: No mention of RED cycle stop conditions or GREEN cycle behavioral descriptions (TDD workflow requirements)
   - Fix: Added RED cycle stop conditions (test file created, test fails with expected error) and GREEN cycle behavioral descriptions (describe behavior and approach hint, not prescriptive code)
   - **Status**: FIXED

## Fixes Applied

- Requirements Mapping — Added Notes column with implementation explanations for all requirements
- Phase 1 Step 1.1 — Enumerated all four fragment sections (Motivation, Design Discussion Evaluation, Agreement Momentum, Model Selection)
- Phase 1 Step 1.2 — Specified vet criteria (deslop, research grounding, fragment conventions)
- Phase 2 — Added test file specification (`agent-core/hooks/tests/test_userpromptsubmit_shortcuts.py`)
- Phase 2 Cycles — Reordered 2.2 and 2.3 to fix dependency inversion (fenced block detection now before any-line matching)
- Phase 2 Cycles — Added explicit "Depends on:" annotations for cycles 2.3 and 2.4
- Phase 2 Cycle 2.5 — Specified integration test scope (long-form alias + any-line + fenced exclusion together)
- Phase 3 — Added Step 3.3 checkpoint (verify tests pass, precommit clean, commit before manual validation)
- Phase 3 — Renumbered Step 3.3 to 3.4, expanded with all 4 manual validation scenarios and expected outcomes
- Phase 3 — Added restart note to Step 3.4 (perform in fresh session after restart)
- Complexity per Phase table — Corrected Phase 2 file count to "2 (1 modify, 1 new test)" and Phase 3 to "1 (modify CLAUDE.md)"
- Expansion Guidance Phase 2 — Added RED cycle stop conditions and GREEN cycle behavioral descriptions
- Expansion Guidance Phase 2 — Added dependency order note (2.1/2.2 independent, 2.3 depends on 2.2, 2.4 depends on 2.3)

## Design Alignment

**Architecture**: Outline correctly reflects two-layer mechanism (Layer 1 fragment in Phase 1, Layer 2 hook enhancement in Phase 2, wiring in Phase 3).

**Module structure**: Matches design — fragment in `agent-core/fragments/`, hook modification in `agent-core/hooks/`, CLAUDE.md reference for activation.

**Key decisions**: All 7 design decisions (D-1 through D-7) referenced in Key Decisions Reference table with correct section mappings.

**Dependencies**: Design identifies existing fence tracking code in `src/claudeutils/markdown_parsing.py` — Expansion Guidance Phase 2 notes reuse option OR simpler standalone implementation (hook needs are simpler than full parser).

## Positive Observations

- **Clear phase typing**: Phase 1 and 3 correctly marked as general, Phase 2 correctly identified as TDD with testable behavioral contracts
- **Model tier assessment**: Sonnet for Phase 1 (content creation with research grounding), Haiku for Phase 2 (TDD implementation), Haiku for Phase 3 (configuration) — appropriate to cognitive requirements
- **Comprehensive design references**: Key Decisions Reference table and Design Document Reference section provide strong traceability to design rationale
- **Foundation-first ordering**: Phase 1 creates fragment before Phase 2 enhances hook (no circular dependency), Phase 3 wires only after implementation complete
- **Restart boundary awareness**: Correctly notes restart required after hook changes, specifies manual validation must occur in fresh session

## Recommendations

**For full runbook expansion:**

1. **Phase 1 Step 1.1**: Follow deslop.md rules strictly — no hedging ("worth noting", "it's important"), direct statements only. Research grounding provides motivational WHY, rules provide behavioral WHAT.

2. **Phase 2 Cycles**: Consider whether to reuse existing `_extract_fence_info` and `_track_fence_depth` from markdown_parsing.py OR implement simpler standalone fence tracking (hook only needs to skip fenced regions, not parse them). Simpler standalone may be preferable for hook isolation.

3. **Phase 2 Cycle 2.4**: Enhanced `d:` directive injection must preserve existing "do not execute" behavior while adding counterfactual structure. Verify Tier 2 flow remains identical (lookup in DIRECTIVES, output formatting unchanged).

4. **Phase 3 Step 3.4**: Manual validation scenarios should be executed in sequence — good idea first (establishes baseline), flawed idea second (tests pushback), agreement momentum third (tests self-monitoring over multiple turns), model selection fourth (tests different context from discussion mode).

5. **Checkpoint spacing**: All checkpoints are appropriately placed. Step 3.3 is the only formal checkpoint (after Phase 2 TDD completion, before manual validation).

---

**Ready for full expansion**: Yes
