# Phase-Scoped Agent Context — Outline

## Problem

prepare-runbook.py generates one agent per runbook. All phases share the same agent definition and the same "Runbook-Specific Context" section. Phase-specific context is injected per-step file (as `## Phase Context`), meaning each step agent re-reads it fresh — no caching benefit.

For mixed-type runbooks (TDD + general phases), a single baseline is chosen (artisan for mixed), losing TDD protocol for TDD phases.

The orchestrator plan has a Phase-Agent Mapping table but it's structurally unpopulated — all steps map to a single `<plan>-task` agent.

## Approach

Generate one agent per phase instead of one per runbook. Each phase agent:
- Uses the baseline appropriate to its phase type (test-driver for TDD, artisan for general)
- Carries plan-level shared context (runbook common context)
- Carries phase-specific context (phase preamble from runbook)
- Has a unique name following the `crew-<plan>-p<N>` convention (crew- prefix from agent-naming brainstorm)

The orchestrator plan's Phase-Agent Mapping table is populated with generated per-phase agents. Each step entry in the plan already has an `Agent:` field — the orchestrate skill needs a minor update to read this field as the `subagent_type` instead of hardcoding `<runbook-name>-task`. This also implements the `crew-` prefix convention that quality-infrastructure marked as out-of-scope future work. This is a targeted edit (one line in SKILL.md Section 3.1), not a rewrite.

Inline phases generate no agent (orchestrator executes directly — unchanged).

## Key Decisions

1. **Naming:** `crew-<plan>-p<N>` for multi-phase, `crew-<plan>` for single-phase. The `crew-` prefix is the plan-specific executor convention from the agent-naming brainstorm (`plans/quality-infrastructure/reports/agent-naming-brainstorm.md`). Replaces the old `<plan>-task` convention.

2. **Baseline per phase type:** Each phase gets its own baseline. TDD phase → test-driver. General phase → artisan. No more "mixed → artisan for everything." The base type (test-driver or artisan) is reused across phases of the same type — the differentiator is injected context (plan context + phase context), not protocol.

3. **Context layering in agent file:**
   ```
   frontmatter (name, model, tools)
   + baseline body (from phase type)
   + plan context (common context from runbook, shared across phases)
   + phase context (preamble extracted from runbook phase header)
   + footers (scope enforcement, clean-tree requirement)
   ```

4. **Common context placement:** Runbook-wide `## Common Context` is embedded in every phase agent (plan-level shared context). This duplicates across agents but enables API prompt caching — each agent's system prompt is self-contained.

5. **Phase context source:** Phase preamble (text between `## Phase N: Title` and first step/cycle header) is the phase context. Already extracted by `extract_phase_preambles()`.

6. **Orchestrator plan format change:** Phase-Agent Mapping table populated with `crew-<plan>-p<N>` names. Each step entry references its phase, orchestrator resolves phase→agent from the table. The `Agent: <plan>-task` header line is removed (no single agent).

7. **Backward compatibility:** The `<plan>-task` naming convention is replaced by `crew-<plan>[-p<N>]`. Existing orchestrator plans need re-preparation (`prepare-runbook.py` re-run). Acceptable — orchestrator plans are generated artifacts, not authored.

8. **Orchestrate-evolution compatibility:** That design's D-2 (`<plan>-task` with embedded design+outline) is superseded by per-phase agents. The dispatch side reads Phase-Agent Mapping — same mechanism regardless of whether agents are per-plan or per-phase. D-5 (ping-pong TDD) composes naturally: role-specific agents (tester, implementer) would become phase-AND-role-scoped.

## Scope

**IN:**
- prepare-runbook.py: per-phase agent generation, orchestrator plan format
- Existing tests: update to verify per-phase output
- Orchestrator plan format: populated Phase-Agent Mapping
- Orchestrate skill: update Section 3.1 `subagent_type` to read per-step `Agent:` field from plan (one-line change)

**OUT:**
- Orchestrate skill rewrite (orchestrate-evolution owns this)
- Vet agent generation (orchestrate-evolution D-2)
- Ping-pong TDD agents (orchestrate-evolution D-5)
- Post-step remediation (orchestrate-evolution D-3)
- Design/outline embedding in agents (orchestrate-evolution D-2 — additive, can layer on top later)

## Affected Files

- `agent-core/bin/prepare-runbook.py` — behavioral: agent generation, orchestrator plan generation
- `tests/test_prepare_runbook*.py` — test updates for new output format
- `agent-core/skills/orchestrate/SKILL.md` — Section 3.1: read `Agent:` field per step instead of hardcoding `<runbook-name>-task`
- Generated artifacts (`.claude/agents/crew-<plan>[-p<N>].md`, `plans/<plan>/orchestrator-plan.md`) — format change

## Requirements Traceability

- **FR-1** (per-phase agents with phase-scoped context) → Approach, Key Decisions 1-5, Affected Files
- **FR-2** (same base type, differentiator is injected context) → Key Decision 2 (baseline per phase type, context is the differentiator)
- **FR-3** (orchestrate-evolution dispatch compatibility) → Key Decision 8 (D-2 superseded, Phase-Agent Mapping mechanism unchanged)

## Open Questions

None — approach is concrete, precedented by manual hb-p1..p5 pattern.
