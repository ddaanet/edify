# 2026-08-13 — Per-plan generated agents retired

Execution now delegates by reference: the orchestrator dispatches a standing
agent with the path to a step file (D-24). The bespoke `<plan>-task`,
`<plan>-corrector`, `<plan>-tester` and `<plan>-implementer` definitions that
`prepare-runbook.py` used to generate into `.claude/agents/` are gone — they
fought the platform, since generated agents are not discoverable as
`subagent_type` values until session restart.

The forced planning/execution session restart stopped being a discoverability
requirement as a result. It was kept on model-tier and context-budget grounds
(D-25), and auto-chaining `/runbook` into `/orchestrate` was deliberately not
taken.
