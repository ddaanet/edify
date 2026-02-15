# Pushback Runbook Outline

**Status:** Promoted to runbook.md (outline sufficiency criteria met: all items specify targets/actions/verification, no unresolved decisions)
**Created:** 2026-02-13

---

## Requirements Mapping

| Requirement | Implementation Phase | Notes |
|-------------|---------------------|-------|
| FR-1: Structural pushback in design discussions | Phase 1 (fragment), Phase 2 (hook d: enhancement) | Fragment provides behavioral rules, hook injects counterfactual structure |
| FR-2: Detect agreement momentum | Phase 1 (fragment self-monitoring rule) | Self-monitoring via fragment, no external state tracking |
| FR-3: Model selection evaluation | Phase 1 (fragment model tier rule) | Fragment Model Selection section with cognitive requirement evaluation |
| NFR-1: Not sycophancy inversion | Phase 1 (evaluator framing, "articulate WHY") | Evaluator framing (not devil's advocate), "articulate WHY" forces evaluation depth |
| NFR-2: Lightweight mechanism | Phase 1 (zero-cost fragment), Phase 2 (string-only hook modification) | Fragment is zero per-turn cost via CLAUDE.md @-reference, hook enhancement is string modification only |

---

## Phase Structure

### Phase 1: Fragment Creation (type: general)

**Scope:** Create `agent-core/fragments/pushback.md` with behavioral rules.

**Complexity:** Low — Direct content creation following existing fragment conventions.

**Model:** Sonnet

**Items:**
- Step 1.1: Create pushback fragment with sections: Motivation (WHY sycophancy is harmful), Design Discussion Evaluation (counterfactual structure, confidence calibration), Agreement Momentum (self-monitoring rule), Model Selection (cognitive requirement evaluation)
- Step 1.2: Vet fragment against deslop compliance, research grounding application (evaluator framing, counterfactual structure, confidence calibration), and fragment structural conventions

---

### Phase 2: Hook Enhancement (type: tdd)

**Scope:** Enhance `agent-core/hooks/userpromptsubmit-shortcuts.py` with long-form directive aliases, any-line matching, fenced block exclusion, and enhanced `d:` injection.

**Complexity:** Medium — Four testable features with clear behavioral contracts.

**Model:** Haiku (implementation), Sonnet (review)

**Test file:** `tests/test_userpromptsubmit_shortcuts.py` (new — in project `tests/` directory, not `agent-core/`; `pyproject.toml` `testpaths = ["tests"]` and `exclude = ["agent-core"]`)

**Import mechanism:** Hook filename contains hyphen — requires `importlib.util.spec_from_file_location` to import. Cycle 2.1 RED phase must establish this import pattern.

**Items:**
- Cycle 2.1: Long-form directive aliases (`discuss` → same as `d`, `pending` → same as `p`). **Depends on:** None
- Cycle 2.2: Enhanced d: directive injection with counterfactual structure (assumptions, failure conditions, alternatives, confidence). **Depends on:** None (modifies DIRECTIVES dict value, independent of matching mechanism). Enhanced content goes to `additionalContext` only; `systemMessage` stays concise (e.g., "[DIRECTIVE: DISCUSS] Discussion mode — evaluate critically, do not execute.")
- Cycle 2.3: Fenced block exclusion in directive scanning (skip lines inside 3+ backtick/tilde fences). **Depends on:** None (foundation for 2.4)
- Cycle 2.4: Any-line directive matching (scan all non-fenced lines, return first match; replaces inline `re.match` at hook line 653). **Depends on:** Cycle 2.3 (uses fenced block detection)
- Cycle 2.5: Integration test — E2E via JSON stdin→stdout (pipe `{"user_prompt": "..."}`, assert JSON output) verifying: long-form alias + any-line matching + fenced exclusion work together, Tier 1 exact-match unchanged. **Depends on:** All prior cycles

---

### Phase 3: Wiring (type: general)

**Scope:** Wire fragment into CLAUDE.md, sync symlinks, verify hook activation.

**Complexity:** Low — Straightforward configuration updates.

**Model:** Haiku

**Items:**
- Step 3.1: Add pushback fragment reference to CLAUDE.md (insertion point: after `@agent-core/fragments/execute-rule.md` in Core Behavioral Rules section)
- Step 3.2: Sync symlinks to parent via `just sync-to-parent` (requires `dangerouslyDisableSandbox: true`)
- Step 3.3: Checkpoint — verify Phase 2 unit tests pass, precommit clean, commit all changes before manual validation
- Step 3.4: Manual validation with 4 scenarios: (1) Good idea evaluation — verify agent articulates specifically WHY, (2) Flawed idea pushback — verify agent identifies assumptions/failure conditions/alternatives, (3) Agreement momentum — 3+ consecutive agreements trigger self-flag, (4) Model selection — pending task with opus-level reasoning gets model tier evaluation

**Note:** Restart required after Step 3.2 (hook changes take effect only after restart). Perform Step 3.4 in fresh session.

---

## Key Decisions Reference

**From design.md:**

| Decision | Section |
|----------|---------|
| D-1: Fragment over skill | Two-Layer Mechanism (ambient 100% vs invoked 79%) |
| D-2: Enhance existing hook | Layer 2: Hook Enhancement (zero infrastructure cost) |
| D-3: Self-monitoring over external state | Fragment: Agreement Momentum section |
| D-4: Model selection in fragment | Fragment: Model Selection section |
| D-5: Long-form directive aliases | Enhanced `d:` Directive (self-documenting) |
| D-6: Any-line directive matching | Any-Line Directive Matching (multi-line user messages) |
| D-7: Fenced block exclusion | Any-Line Directive Matching (reuse preprocessor code) |

---

## Complexity per Phase

| Phase | Files | Lines | Complexity | Model |
|-------|-------|-------|------------|-------|
| Phase 1 | 1 (new) | ~50 | Low | Sonnet |
| Phase 2 | 2 (1 modify, 1 new test) | ~150 additions | Medium (testable features) | Haiku |
| Phase 3 | 1 (modify CLAUDE.md) | ~5 | Low | Haiku |

**Model tier note:** Design recommends "Sonnet for all phases" (line 242). Haiku for Phase 2/3 is a deliberate deviation — TDD cycles have clear behavioral contracts (haiku-appropriate), Phase 3 is mechanical wiring. Sonnet reserved for Phase 1 (behavioral content requiring judgment) and Phase 2 review checkpoints.

**Total:** ~200 lines across 3-4 files, sequential phases.

---

## Expansion Guidance

**Phase 1 (Fragment):**
- Follow deslop.md prose rules (no hedging, direct statements)
- Structure: Motivation → Rules → Examples (per research grounding)
- Apply evaluator framing, counterfactual structure (per research)

**Phase 2 (Hook Enhancement):**
- RED/GREEN cycle format for each feature
- RED cycle stop conditions: test file created, test fails with expected error (import error, assertion failure, function not found)
- GREEN cycle behavioral descriptions: describe behavior and approach hint, not prescriptive code
- Cycle 2.1 RED phase establishes test infrastructure: `importlib.util.spec_from_file_location` import pattern for hyphenated hook filename
- Reuse existing fence tracking code from `src/claudeutils/markdown_parsing.py` (_extract_fence_info, _track_fence_depth) OR implement simpler standalone version (hook needs are simpler than full parser)
- Unit tests (Cycles 2.1-2.4) import and test extracted functions; integration test (Cycle 2.5) tests E2E via JSON stdin→stdout piping (matches hook execution model)
- Integration test (Cycle 2.5) ensures all features work together: long-form alias on non-first line inside fenced block should be excluded
- Each cycle: testable behavioral contract, not structural scaffolding
- Dependency order: 2.1 (aliases, independent), 2.2 (enhanced d:, independent), 2.3 (fences, independent), 2.4 (any-line, depends on 2.3), 2.5 (integration, depends on all)

**Phase 3 (Wiring):**
- Insertion point in CLAUDE.md: After `@agent-core/fragments/execute-rule.md` in Core Behavioral Rules section
- Use `just sync-to-parent` for symlink sync (requires dangerouslyDisableSandbox)
- Manual validation: 4 scenarios from Testing Strategy section in design

---

## Design Document Reference

**Source:** `plans/pushback/design.md`

**Key sections:**
- Research Grounding (lines 26-47) — Prompt techniques validated by research
- Architecture (lines 49-156) — Two-layer mechanism details
- Layer 1: Fragment (lines 74-117) — Content structure and design principles
- Layer 2: Hook Enhancement (lines 119-156) — Enhanced d:, aliases, any-line matching
- Implementation Notes (lines 178-211) — Affected files, testing strategy, dependencies
- Documentation Perimeter (lines 212-220) — Required reading for planner

**Testing strategy (lines 190-201):**
- Manual validation: 4 scenarios (good idea evaluation, flawed idea pushback, agreement momentum, model selection)
- Hook unit tests: long-form aliases, any-line matching, fenced block exclusion, Tier 1 unchanged

---

## Expansion Guidance for Runbook Creation

The following recommendations should be incorporated during full runbook expansion:

**Phase 1 Fragment Content:**
- Motivation section must explain WHY sycophancy is harmful (research: Claude generalizes better with context/motivation)
- Use evaluator framing language ("evaluate critically") not devil's advocate framing (research: DA is performative)
- Counterfactual structure: "what assumptions does this make", "what would need to be true for this to fail", "name unconsidered alternatives"
- Confidence calibration: "state confidence level", "what evidence would change assessment"
- Self-monitoring rule: track agreement patterns, flag 3+ consecutive agreements explicitly ("I notice I've agreed with several proposals in a row — let me re-evaluate...")
- Model Selection section: evaluate cognitive requirements (opus for design/architecture/synthesis, sonnet for balanced work, haiku for mechanical execution), do not default to sonnet

**Phase 2 TDD Cycle Expansion:**
- Cycle 2.1 (long-form aliases): Establish importlib import pattern for hyphenated hook filename. Test `discuss: <text>` produces same additionalContext as `d: <text>`, same for `pending`/`p`
- Cycle 2.2 (enhanced d: injection): Verify additionalContext includes all counterfactual structure elements (assumptions, failure conditions, alternatives, confidence), preserves existing "do not execute" behavior. Enhanced content to `additionalContext` only; `systemMessage` stays concise (short mode indicator, not full evaluation framework)
- Cycle 2.3 (fenced block detection): Test lines between opening fence (3+ backticks or tildes) and closing fence (same char, at least same count) are marked as fenced
- Cycle 2.4 (any-line matching): Test directive on line 2, line 3, etc. are found (not just line 1). Test directive inside fenced block returns None (excluded). GREEN phase must replace inline `re.match` at hook line 653 with call to new any-line scanner function
- Cycle 2.5 (integration): E2E test via JSON stdin→stdout piping. Test `discuss: <text>` on line 3 inside a fenced code block is excluded, but `discuss: <text>` on line 5 after closing fence is matched

**Phase 2 Implementation Choice:**
- Consider simpler standalone fence tracking for the hook (only needs to skip fenced regions, not parse them) versus reusing markdown_parsing.py code (more complex, handles nesting)
- Hook isolation advantage: simpler standalone reduces dependencies
- Code reuse advantage: proven logic for fence detection edge cases

**Phase 3 Manual Validation Execution Order:**
- Execute in sequence: (1) good idea first (baseline), (2) flawed idea second (tests pushback), (3) agreement momentum third (tests multi-turn self-monitoring), (4) model selection fourth (different context)
- Good idea test: propose a genuinely good design idea in `d:` mode, verify agent articulates specifically WHY (not "this is a good idea" but "this addresses X cost, avoids Y complexity")
- Flawed idea test: propose idea with hidden assumptions, verify agent identifies assumptions ("this assumes Z is true"), failure conditions ("this would fail if W"), alternatives ("alternatively, consider V")
- Agreement momentum test: make 3+ consecutive proposals agent agrees with, verify agent flags pattern explicitly after 3rd agreement
- Model selection test: create pending task requiring opus-level reasoning (e.g., nuanced behavioral design), verify agent evaluates model tier and doesn't default to sonnet

**Checkpoint Guidance:**
- Step 3.3 checkpoint validates Phase 2 completion before manual validation
- Verify all 5 cycles pass unit tests
- Run precommit validation (no dirty state)
- Commit all Phase 2 changes before proceeding to Step 3.4
- Step 3.4 must occur in fresh session after restart (hook changes only take effect after restart)

**References to Include:**
- Design lines 81-109 for fragment content structure (Motivation → Design Discussion Evaluation → Agreement Momentum → Model Selection)
- Design lines 122-129 for enhanced `d:` directive injection specification (counterfactual structure elements)
- Design lines 140-156 for any-line directive matching and fenced block exclusion behavioral specification
- Research Grounding table (design lines 30-38) for validation of prompt techniques applied in fragment
