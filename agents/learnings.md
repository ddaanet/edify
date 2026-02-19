# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## When design ceremony continues after uncertainty resolves
- Anti-pattern: One-shot complexity triage at `/design` entry, no re-assessment when outline resolves architectural uncertainty. Process continues at "complex" even when outline reveals 2-file prose edits.
- Correct pattern: Two gates. Entry gate reads plan directory artifacts (existing outline can skip ceremony). Mid-stream gate re-checks complexity after outline production. Both internal to `/design` — preserves single entry point.
- Evidence: Outline-review-agent + design.md + design-vet-agent cost ~112K tokens for work that could have been done inline. Findings would have surfaced during editing.
## When deleting agent artifacts
- Anti-pattern: Treating all ceremony artifacts as equally disposable. Outline review found real issues (FR-2a gap, FR-3c contradiction); design.md restated the reviewed outline.
- Correct pattern: Distinguish audit trails with real findings from redundant restates. Review reports that improved artifacts have value; documents that reformat existing artifacts don't.
## When recovering agent outputs
- Anti-pattern: Manually reading agent session log and retyping content.
- Correct pattern: Script extraction from task output files. Agent Write calls are JSON-structured in `tmp/claude/.../tasks/<agent-id>.output`. Parse with jq or Python, recover deterministically.
- Prototype: `plans/prototypes/recover-agent-writes.py`
## When design resolves to simple execution
- Anti-pattern: Always routing from `/design` to `/runbook` after sufficiency gate, regardless of execution complexity. Complex design classification persists through the pipeline even when design resolves the uncertainty.
- Correct pattern: Execution readiness gate inline at sufficiency gate. When design output is ≤3 files, prose/additive, insertion points identified, no cross-file coordination → direct execution with vet, skip `/runbook`.
- Rationale: Design can resolve complexity. A job correctly classified as Complex for design may produce Simple execution. The gate is subtractive (creates exit ramp), not additive (more ceremony).
## When selecting reviewer for artifact vet
- Anti-pattern: Defaulting to vet-fix-agent for all artifacts because the vet-requirement fragment names it as the universal reviewer. Fragments are LLM-consumed behavioral instructions, not human documentation — doc-writing skill is wrong reviewer for them.
- Correct pattern: Check artifact-type routing table in vet-requirement.md before selecting reviewer. Skills → skill-reviewer, agents → agent-creator, design → design-vet-agent, fragments → vet-fix-agent (default, not doc-writing). The routing table is always-loaded; the process step is the enforcement gate.
- Evidence: Selected vet-fix-agent for skill edits. User corrected to skill-reviewer. Root cause: generic rule without routing lookup.
## When assuming interactive context
- Anti-pattern: Assuming orchestration is interactive (user watching, can ctrl+c hung agents). Designing timeout as low-priority because "human-in-the-loop provides timeout for free."
- Correct pattern: Orchestration is unattended — user focuses on design/workflow work elsewhere. Timeout is a real operational requirement, not a nice-to-have. Calibrate from historical data.
- Rationale: The operational model determines which error handling mechanisms are needed. Wrong assumption about attended vs unattended cascades into under-specifying timeout, recovery, and notification.
## When classifying errors by tier
- Anti-pattern: Moving ALL error classification to orchestrator because haiku can't classify. Sweeping change that ignores capable agents.
- Correct pattern: Tier-aware classification — sonnet/opus execution agents self-classify and report classified error; haiku agents report raw errors for orchestrator to classify. Preserves context locality for capable agents.
- Rationale: Execution agent has full error context (stack trace, file state). Transmitting to orchestrator for classification loses fidelity or costs tokens. Orchestrator already knows agent model tier.
## When measuring agent durations
- Anti-pattern: Computing duration as timestamp delta between tool_use and tool_result — includes laptop sleep time, producing 10-hour "outliers" that are artifacts
- Correct pattern: Use `duration_ms` from Task result metadata when available (post-W06 2026, ~42% coverage). For all entries with both duration and tool_uses, validate via seconds-per-tool-use rate (normal p50=6.6s/tool). Flag entries >30s/tool as sleep-inflated.
- Rationale: `duration_ms` is wall-clock computed by CLI process — suspended process = inflated time. Cross-referencing with tool_uses exposes the inflation. 13/951 entries flagged, all confirmed artifacts.
## When designing timeout mechanisms
- Anti-pattern: Treating "dual signal" (time OR tool count) as reducing false positives. OR-logic is the union of both kill zones — it increases false positives vs either threshold alone.
- Correct pattern: Time and tool count address independent failure modes. Spinning (high activity, no convergence) → `max_turns`. Hanging (no activity, high wall-clock) → duration timeout. Independent guards, not a combined signal.
- Evidence: OR(600s, 90 turns) would false-positive on the 855s/75-tool legitimate agent AND the 495s/129-tool agent. AND logic misses fast spinners.
## When all work is prose edits with pre-resolved decisions
- Anti-pattern: Routing through full runbook pipeline (outline → runbook expansion → plan-reviewer → prepare-runbook.py → step files → orchestrate → per-step agents) when all phases are additive prose with no feedback loop.
- Correct pattern: Recognize prose edits have no implementation loop — outcome determined by instruction + target file state. Execute inline from design outline. The delegation ceremony (agent startup, file re-reads, report write/read) costs more tokens than the edits.
- Evidence: Error-handling runbook used 11 opus agents for ~250 lines of prose. Plan-reviewer caught a regression *introduced* by the runbook generation process (Step 4.2 dropped 2 of 4 skills the outline correctly listed).
## When proposing thresholds without data
- Anti-pattern: Deriving thresholds from reasoning (">2 inline phases → batch") or replacing one confabulated metric with a cleaner confabulated metric ("coordination complexity" replacing "≤3 files"). Cleaner confabulation is still confabulation.
- Correct pattern: Ground thresholds in empirical data. If data doesn't exist, state the decision as ungrounded and defer until measurement. The No Estimates rule applies to operational thresholds, not just time/cost predictions.
- Evidence: Proposed >2 threshold for inline batching, then replaced with "all-inline vs mixed" property check — both ungrounded. User corrected: measure Task delegation token overhead before committing to a threshold.
## When execution readiness gate uses file count
- Anti-pattern: Using ≤3 files as the discriminator for "design resolves to simple execution." File count is a proxy — 7 files with independent additive changes can be simpler than 2 files with interleaving structural changes.
- Correct pattern: The underlying property is coordination complexity: all decisions pre-resolved + changes additive + cross-file deps phase-ordered + no implementation loops. File count correlates but doesn't determine.
- Rationale: Supersedes the ≤3 files heuristic in the existing "When design resolves to simple execution" learning. The inline-phase-type design formalizes this as D-5.
