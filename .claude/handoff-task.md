## Current task

Proving the verify-loop thesis (living design L5/L6): the design doc and a first
`formalize` dogfood are done and committed; the open thread is which proof path
to take next.

## Open decisions

- Proof path — pick one: (a) one more qualitative `formalize` run aimed at a
  target that should *fail* (closes the only untested half of the loop — the
  dogfood verified, never caught a bug; cheap, in-session); (b) scope + build
  the eval harness (D8 — the only thing that yields a catch-rate against the
  paper's ~35–39% one-shot baseline and actually closes L5; needs its own
  spec/plan and Agent-SDK/`claude -p` plan credits); (c) stop — state is clean,
  committed, precommit green, living-doc resume pointer current.
