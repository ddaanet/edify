## Current task

Execute the verify-loop implementation plan (`edify check` CrossHair CLI +
`formalize` skill) — plan written and self-reviewed, not yet started, awaiting
the execution-mode choice.

## Open decisions

- Execution mode: subagent-driven (recommended, fresh agent per task) vs inline
  with checkpoints.
- Task 1 is a gate: confirm `crosshair-tool` installs and runs under Python
  3.14 *before* building further; if it doesn't, stop and pick a fallback
  (pin a compatible interpreter for a check-only path, or defer) rather than
  working around silently.
