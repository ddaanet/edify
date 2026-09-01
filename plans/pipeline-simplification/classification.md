# Classification — pipeline-simplification

- **Classification:** Complex
- **Implementation certainty:** Moderate — target shape known (superpowers' writing-plans / executing-plans / subagent-driven-development, C-1/C-2); agent surface open (Q-1 GREEN role, Q-2 refactor placement); deletion spans ~5,000 lines across 4 scripts, 10 references, 3 agents, 2 docs and `docs/design.md`.
- **Requirement stability:** High — 7 FRs mechanism-specified, /proof-validated 2026-08-29, two open questions explicitly scoped.
- **Behavioral code check:** Yes — deletes Python scripts and their tests; rewrites agent/skill behaviour.
- **Work type:** Production
- **Artifact destination:** agentic-prose (primary: `plugin/skills/`, `plugin/agents/`), with production deletions (`plugin/bin/`, `tests/`) and investigation edits (`docs/design.md`).
- **Evidence:** two open questions on the agent surface = certainty not High; C-1 reopens a "do not re-litigate" tier decision = architectural; `cc-subagent-context-capabilities` constrains the orchestrator mechanism (FR-4); `remove-cleanly-no-vestigial` + `spec-enumerations-need-rederiving` constrain the deletion (FR-2/C-4). Multi-item check: one coherent job, no implicit or explicit bundling — "inline task sequence on a branch" is a routing constraint (C-5), not extra work.
- **Routing:** Complex → outline (Phase A/B) → design → execution as inline task sequence on a branch (C-5, D-39), not `/runbook`.
