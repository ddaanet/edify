# Orchestrate Evolution — Runbook Outline

**Design:** `plans/orchestrate-evolution/design.md`
**Recall:** `plans/orchestrate-evolution/recall-artifact.md`

## Requirements Mapping

| Requirement | Phase | Item |
|-------------|-------|------|
| FR-2 (post-step remediation) | 3 | Step 3.1 (SKILL.md remediation protocol) |
| FR-3 (RCA task generation) | 3 | Step 3.1 (SKILL.md RCA after remediation) |
| FR-4 (delegation prompt dedup) | 1 | Cycles 1.1-1.3 (agent caching eliminates inline content) |
| FR-5 (commit instruction) | 1 | Cycle 1.1 (clean tree footer in agent definition) |
| FR-6 (scope constraint) | 1 | Cycle 1.1 (scope enforcement footer + structural absence) |
| FR-7 (precommit verification) | 2 | Cycle 2.4 (verify-step.sh) + Phase 3 (SKILL.md invocation) |
| FR-8 (ping-pong TDD) | 4, 5 | Phase 4 (agents + scripts) + Phase 5 (SKILL.md loop) |
| FR-8a (RED gate) | 4 | Cycle 4.4 (verify-red.sh) |
| FR-8b (GREEN gate) | 2, 5 | Cycle 2.4 (verify-step.sh: clean tree), Step 5.1 (composed GREEN = `just test` + verify-step.sh) |
| FR-8c (role-specific correctors) | 4 | Cycle 4.1 (test-corrector + impl-corrector) |
| FR-8d (agent resume) | 5 | Step 5.1 (SKILL.md TDD loop resume strategy) |
| NFR-1 (context bloat) | 1, 2 | Agent caching + structured plan format |
| NFR-2 (backward compat) | All | Q-4 clean break — no migration needed |
| NFR-3 (orchestrator model) | 3 | Step 3.1 (SKILL.md sonnet default) |

## Key Decisions Reference

- **D-1 (sonnet default):** design.md "D-1: Abandon weak orchestration"
- **D-2 (agent caching):** design.md "Agent Caching Model (D-2)"
- **D-3 (remediation):** design.md "Post-Step Remediation Protocol (D-3)"
- **D-4 (escalation):** design.md "D-4: Simplified error escalation"
- **D-5 (ping-pong TDD):** design.md "Ping-Pong TDD Orchestration (D-5)"
- **D-6 (inline phases):** design.md "D-6: Inline phase handling"

## Expansion Guidance

- **Existing test suite:** 6 test files for prepare-runbook.py (`tests/test_prepare_runbook_*.py`). New TDD cycles extend these or create new test modules.
- **Agent baselines:** `artisan.md` (general), `test-driver.md` (TDD), `corrector.md` (review). Design references "quiet-task" and "tdd-task" — these map to artisan.md and test-driver.md respectively.
- **Current naming:** Agents use `crew-<name>[-p<N>]` prefix. Design changes to `<plan>-task`, `<plan>-corrector`. Clean break (Q-4).
- **prepare-runbook.py size:** ~1500 lines. Monitor line count; extract helpers for repeated kwargs patterns before splitting.
- **Shell script testing:** Use pytest with real git repos in `tmp_path` fixtures (E2E pattern from `agents/decisions/testing.md`).
- **Architectural artifacts:** SKILL.md, refactor.md, delegation.md require opus per Model Assignment rules.
- **Test file growth risk:** `test_prepare_runbook_agents.py` is 353 lines. Phase 1 (4 cycles) and Phase 4 Cycle 4.1 both extend it. Project split threshold is 400 lines. Planner should route Phase 4 TDD agent tests to a new `tests/test_prepare_runbook_tdd_agents.py` file, or split Phase 1 tests into `test_prepare_runbook_agent_caching.py` before Phase 4 begins. See learnings: "When TDD cycles grow a shared test file past line limits."

---

### Phase 1: Agent caching model (type: tdd)

**Scope:** Restructure prepare-runbook.py agent generation from per-phase to per-role model. Single task agent with embedded design+outline replaces N per-phase agents.

**Files:** `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_agents.py` (extend)

- Cycle 1.1: Single task agent with new naming and footers
  - Replace per-phase agent generation with single `<plan>-task.md`
  - Baseline selection: artisan.md for general/mixed, test-driver.md for pure TDD
  - Include scope enforcement and clean tree requirement footers
  - Verify: single agent file generated (not per-phase), correct naming `{name}-task`

- Cycle 1.2: Design.md embedding in task agent
  - Read `plans/<plan>/design.md` and embed full text under `# Plan Context / ## Design`
  - Fallback: empty section with note when design.md absent
  - Verify: agent body contains design.md content between Plan Context markers

- Cycle 1.3: Outline embedding in task agent
  - Source priority: runbook `## Outline` section → `plans/<plan>/outline.md` → empty fallback
  - Embed under `# Plan Context / ## Runbook Outline`
  - Verify: agent body contains outline content; verify fallback chain

- Cycle 1.4: Corrector agent generation for multi-phase plans
  - Generate `<plan>-corrector.md` using corrector.md baseline + same embedded content
  - Only for plans with >1 non-inline phase; skip for single-phase
  - Corrector-specific scope enforcement footer
  - Verify: corrector generated for multi-phase, absent for single-phase

**Complexity:** Medium — restructuring existing generation logic with new content sources

### Phase 2: Orchestrator plan and verification (type: tdd)

**Scope:** New structured orchestrator plan format. verify-step.sh creation.

**Files:** `agent-core/bin/prepare-runbook.py`, `agent-core/skills/orchestrate/scripts/verify-step.sh` (create), `tests/test_prepare_runbook_orchestrator.py` (extend), `tests/test_verify_step.py` (create)

- Cycle 2.1: Structured step list format
  - Replace prose orchestrator plan with structured metadata
  - Format: `- filename | Phase N | model | max_turns [| PHASE_BOUNDARY]`
  - Header fields: `**Agent:**`, `**Corrector Agent:**`, `**Type:**`
  - Verify: orchestrator plan has `## Steps` section with pipe-delimited entries

- Cycle 2.2: PHASE_BOUNDARY markers and phase summaries
  - PHASE_BOUNDARY on last step of each phase
  - `## Phase Summaries` section with IN/OUT scope per phase
  - INLINE marker for inline phases (no step file)
  - Verify: boundary markers present; summaries match phase count

- Cycle 2.3: max_turns extraction from step metadata
  - Add `**Max Turns**` extraction to `extract_step_metadata`
  - Default: 30 when not specified (design example values range 20-30)
  - Propagate to orchestrator plan step list
  - Verify: max_turns in metadata; default applied; appears in plan

- Cycle 2.4: verify-step.sh creation and testing
  - Create `agent-core/skills/orchestrate/scripts/verify-step.sh`
  - Contract: exit 0 (clean) or exit 1 (dirty) + details on stdout
  - Checks: `git status --porcelain`, submodule pointer consistency, `just precommit`
  - Test with real git repos in tmp_path: clean state → 0, uncommitted changes → 1, submodule drift → 1, precommit failure → 1

**Complexity:** Medium — new format generation + shell script with E2E tests

### Phase 3: Skill and prose updates (type: general, model: opus)

**Scope:** Rewrite orchestrate SKILL.md, update refactor agent and delegation fragment.

**Files:** `agent-core/skills/orchestrate/SKILL.md` (rewrite), `agent-core/agents/refactor.md` (modify), `agent-core/fragments/delegation.md` (modify)

**Depends on:** Phase 1 (agent caching model), Phase 2 (verify-step.sh, orchestrator plan format)

- Step 3.1: SKILL.md rewrite
  - Rewrite from ~517 lines to ~200 lines
  - Sonnet orchestrator (D-1), remove `allowed-tools` constraint
  - New execution loop: verify artifacts → read plan → dispatch with file reference → verify-step.sh → remediate (D-3) → phase boundary corrector → inline handling (D-6)
  - Post-step remediation protocol: resume agent → recovery delegation → RCA task (FR-2, FR-3)
  - Completion review: plan-specific corrector (multi-phase) or generic corrector (single-phase)
  - Cleanup: delete `.claude/agents/<plan>-*.md` files
  - Continuation protocol preserved
  - Keep: deliverable review assessment, progress tracking, error escalation

- Step 3.2: Refactor agent and delegation fragment updates
  - **refactor.md:** Add deslop directives before Step 3 (Refactoring Protocol), factorization-before-splitting rule to Evaluation section, resume pattern to return protocol (~30 lines of additions to existing 244-line agent)
  - **delegation.md:** Sonnet default (remove haiku default), remove "Never use opus for straightforward execution" (covered by skill), add file reference pattern and agent caching note, update quiet execution pattern references

**Complexity:** High (Step 3.1), Low (Step 3.2)

### Phase 4: TDD agent generation (type: tdd)

**Scope:** Extend prepare-runbook.py for ping-pong TDD: 4 agent types, step file splitting, orchestrator plan TDD markers.

**Files:** `agent-core/bin/prepare-runbook.py`, `agent-core/skills/orchestrate/scripts/verify-red.sh` (create), `tests/test_prepare_runbook_agents.py` (extend), `tests/test_verify_red.py` (create)

**Depends on:** Phase 1 (agent caching model used as foundation for TDD agents), Phase 2 (orchestrator plan format extended with TDD role markers)

- Cycle 4.1: TDD agent type generation (4 agents)
  - `<plan>-tester.md`: test-driver.md baseline + design + outline + test quality rules
  - `<plan>-implementer.md`: test-driver.md baseline + design + outline + coding rules
  - `<plan>-test-corrector.md`: corrector.md baseline + design + outline + test quality rules
  - `<plan>-impl-corrector.md`: corrector.md baseline + design + outline + coding rules
  - Generated only for TDD-typed runbooks (pure TDD or TDD phases in mixed)
  - Verify: all 4 agents generated for TDD runbook; none for general runbook; correct baselines and cached rules

- Cycle 4.2: Step file splitting (test/impl per TDD cycle)
  - Split each TDD cycle into `step-N-test.md` (test spec) and `step-N-impl.md` (implementation hints)
  - Test file: RED phase content. Impl file: GREEN phase content.
  - Verify: two files per cycle; correct content separation; metadata headers on both

- Cycle 4.3: Orchestrator plan TDD role markers
  - TDD step entries include role: `step-1-1-test.md | Phase 1 | sonnet | 25 | TEST`
  - IMPLEMENT role on impl steps
  - Orchestrator dispatches TEST → tester agent, IMPLEMENT → implementer agent
  - Verify: role markers present; TEST/IMPLEMENT alternating per cycle

- Cycle 4.4: verify-red.sh creation and testing
  - Create `agent-core/skills/orchestrate/scripts/verify-red.sh`
  - Contract: input = test file path; exit 0 if test fails (RED confirmed); exit 1 if test passes
  - Mechanism: `pytest <test_file> --no-header -q`, invert exit code
  - Test with tmp_path: failing test → exit 0, passing test → exit 1, missing test → exit 1

**Complexity:** Medium — extends Phase 1 patterns to TDD-specific generation

### Phase 5: TDD orchestration skill (type: general, model: opus)

**Scope:** Extend SKILL.md with TDD orchestration loop.

**Files:** `agent-core/skills/orchestrate/SKILL.md` (extend)

**Depends on:** Phase 3 (SKILL.md rewrite provides base to extend), Phase 4 (TDD agents, verify-red.sh, step splitting)

- Step 5.1: SKILL.md TDD loop extension (extends ~200-line rewrite from Phase 3)
  - Add TDD orchestration loop section (D-5):
    - Dispatch tester with test spec → RED gate (verify-red.sh) → test-corrector → dispatch implementer → GREEN gate (just test + verify-step.sh) → impl-corrector → next cycle
  - Agent resume strategy: resume tester/implementer across cycles; fresh if >15 messages; correctors never resumed
  - Error handling: RED gate failure → resume tester or escalate; GREEN gate failure → resume implementer or remediate (D-3 pattern)
  - Reference the 4 TDD agent types and their dispatch conditions

**Complexity:** Medium — single opus step extending existing skill with fully-specified loop

---

## Checkpoint Plan

- **Phase 1 → 2 boundary:** Light checkpoint (fix + functional). Verify: single task agent generated, design+outline embedded, corrector for multi-phase.
- **Phase 2 → 3 boundary:** Light checkpoint. Verify: structured plan format, verify-step.sh functional.
- **Phase 3 → 4 boundary:** Full checkpoint (fix + review + functional). SKILL.md rewrite is high-impact architectural artifact.
- **Phase 4 → 5 boundary:** Light checkpoint. Verify: TDD agents generated, step splitting works, verify-red.sh functional.
- **Phase 5 (final):** Full checkpoint. Complete review of all changes.

## Expansion Guidance (Review)

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- Phase 5 (1 step, Medium complexity) is a valid standalone phase — opus model differs from Phase 4's sonnet, and SKILL.md extension logically follows TDD infrastructure. Preserve as separate phase.
- Step 3.2 (refactor agent + delegation fragment) is Low complexity but grouped correctly with Step 3.1 (all prose/architectural artifacts requiring opus).

**Cycle expansion:**
- Cycle 4.1 tests should target a new test file (`tests/test_prepare_runbook_tdd_agents.py`) to avoid pushing `test_prepare_runbook_agents.py` past 400 lines. Phase 1 cycles own the existing test file; Phase 4 creates a new one.
- Cycle 2.4 and Cycle 4.4 (shell script creation + testing) should each specify E2E test pattern: real git repos in `tmp_path` fixtures, not mocked subprocess (per recall artifact: "When Preferring E2E Over Mocked Subprocess").

**Checkpoint guidance:**
- Phase 3 → 4 full checkpoint is critical: validate SKILL.md rewrite covers all design sections (D-1 through D-6, inline handling, remediation protocol, cleanup step).
- Phase 5 final checkpoint should validate TDD loop integration end-to-end against the composed GREEN gate (`just test` + `verify-step.sh`).

**References to include:**
- Recall artifact entries on positional authority (agent definitions: constraints in primacy, plan context middle, scope enforcement recency).
- Recall artifact entry on GREEN phase lint inclusion (`just check && just test` not just `just test`).
- Design section "Post-Step Remediation Protocol (D-3)" for Step 3.1 remediation detail — reference, do not reproduce.
