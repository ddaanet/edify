## Current task

L7 hardening shipped end-to-end (FR12: `edify check` reports the per-condition
budget and warns on stderr + JSON `vacuity_warning` when a `verified` used
CrossHair's default budget) — committed, tree clean, precommit green; next is to
pick the following verify-loop proof lever.

## Open decisions

- Next proof lever for the thesis: build the **D8 eval harness** (the only path
  to an L5 catch-rate number vs the paper's ~35–39% one-shot baseline; needs its
  own spec/plan and Agent-SDK / `claude -p` plan credits, API-key variant is
  ToS-disallowed) vs **stop** (state is clean, L7 done).
- Optional, gated: enrich the `crosshair-verified-falsification-probe` memory to
  cross-reference FR12 as the shipped CLI-level surfacing of the budget-vacuity
  lesson (currently it only describes the manual probe) — awaiting user approval.
