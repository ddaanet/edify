## Current task

Proving the verify-loop thesis: both qualitative halves are now dogfooded
(D9 verify path, D10 catch-a-bug path + the L7 default-budget-vacuity finding),
so the only remaining lever for L5 (catch-rate vs the paper's ~35–39% one-shot
baseline) is the D8 eval harness.

## Open decisions

- Proof path — pick one: (a) **L7 hardening first** (cheap, in-session): give the
  CLI a minimum-budget floor or a vacuity guard so a default-budget `verified`
  can't be hollow, since D10 showed a contract-violating bug passes at the
  default CrossHair budget; (b) **scope + build the D8 eval harness** — the only
  thing that yields a catch-rate number; needs its own spec/plan and
  Agent-SDK/`claude -p` plan credits (the API-key variant is ToS-disallowed);
  (c) **stop** — state is clean, committed, precommit green, living-doc resume
  pointer current.
