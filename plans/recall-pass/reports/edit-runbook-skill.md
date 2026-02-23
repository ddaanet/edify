# Edit Report: Runbook Skill — Recall Pass

**File:** `agent-core/skills/runbook/SKILL.md`
**Status:** Both edits already present — no changes needed.

## Edit A: Phase 0.5 — Recall Artifact Augmentation

**Location:** Lines 227-234 (new step 2, between "Discover relevant prior knowledge" and "Verify actual file locations")

**Content verified:**
- Reads existing `plans/<job>/recall-artifact.md` if present
- If present: augments with implementation/testing learnings from `agents/decisions/implementation-notes.md` and `agents/decisions/testing.md`
- Scopes to planning-relevant entries only (model selection failures, phase typing decisions, checkpoint placement patterns, precommit gotchas) — excludes execution-level entries
- If absent: generates initial artifact (memory-index + decision files, implementation focus)
- Writes augmented artifact back
- Multi-session staleness note included
- Step numbering correct: old step 2 (verify file locations) renumbered to step 3

## Edit B: Common Context Template — Recall Section

**Location:** Lines 952-962 (between "Key Constraints" and "Project Paths" fields)

**Content verified:**
- `**Recall (from artifact):**` field with source reference to `plans/<job>/recall-artifact.md`
- Token budget: <=1.5K tokens with ungrounded calibration note (D-3)
- Phase-neutral entries only in Common Context; phase-specific to preambles (D-1)
- Format per consumer tier: constraint (haiku/sonnet) vs rationale (opus) (D-9)
- Content baked at planning time — orchestrator does not filter (D-2)
- Planner resolves conflicts and evicts least-specific entries when budget exceeded (D-6)
- Early-mid positioning via Common Context -> agent system prompt (D-8, implicit via existing prepare-runbook.py injection)
- Conflicting signals warning for haiku-tier ambient context
- DO NOT rule placement alongside content guidance

## Design Decisions Embedded

| Decision | Where | How |
|----------|-------|-----|
| D-1 | Edit B, line 956 | Phase-neutral here, phase-specific in preambles |
| D-2 | Edit B, line 960 | "Content baked at planning time" |
| D-3 | Edit B, line 954 | Token budget with ungrounded note |
| D-6 | Edit B, line 960 | "Planner resolves conflicting entries" |
| D-8 | Edit B (implicit) | Common Context injected to agent system prompt by prepare-runbook.py |
| D-9 | Edit B, lines 957-959 | Format per consumer model tier |

## Memory-Index Knowledge Embedded

- **Conflicting signals:** Line 961 — "at haiku capability, persistent ambient signal wins"
- **Ambient context:** Line 953 — recall entries curated for task agents (ambient via Common Context)
- **DO NOT rule placement:** Line 962 — rules alongside content guidance, not separate cleanup step
