## Current task

The `edify:recall` spec is committed at `docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md` and awaits the user's review; the implementation plan comes after that, then the skill and the eight-call-site rewire it specifies. Separately, a gitlore index-composition bug found this session is briefed at `../gitlore/brief-index-compose-drops-unterminated-final-line.md` for an agent working in that repo.

## Open decisions

- Whether `memory/cc-subagent-context-capabilities.md` or `agents/decisions/operational-tooling.md` owns the Claude Code capability facts. The recall spec routes `agents/decisions/` into the living design doc, which forces the question rather than leaving the two duplicating each other.