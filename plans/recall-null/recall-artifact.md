# Recall Artifact: recall-null

Resolve entries via `agent-core/bin/when-resolve.py` — do not use inline summaries.

## Entry Keys (planning + cross-cutting)

when anchoring gates with tool calls — D+B gate pattern, canonical anchor
when selecting gate anchor tools — null mode rationale, equal-cost negative path
how prevent skill steps from being skipped — D+B hybrid, prose gates must anchor with tool call
when implementation modifies pipeline skills — self-modification concern, inline task sequence
when writing recall artifacts — keys only, no excerpts, downstream resolve
when selecting model for prose artifact edits — opus for skills/fragments/agents
when corrector agents lack recall mechanism — self-contained vs caller-passed vs skill-level
when recall-artifact is absent during review — lightweight recall fallback
when delegating TDD cycles to test-driver — piecemeal dispatch, resume context
when delegating well-specified prose edits — opus delegation ceremony cost, pre-resolved decisions
when adding a new variant to an enumerated system — grep downstream enumeration sites

## Per-Consumer Artifacts

- `tdd-recall-artifact.md` — test-driver (5 entries: CLI testing, assertions, lint gate)
- `review-recall-artifact.md` — corrector (7 entries: D+B pattern, model selection, holistic fixes)
- `skill-review-recall-artifact.md` — skill-reviewer (6 entries: skill editing, D+B propagation)
