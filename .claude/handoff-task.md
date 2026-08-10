## Current task

The revived pipeline's dispatch surface has been rewritten off retired platform APIs — spawning is the `Agent` tool, resumption is `SendMessage` to a name set at spawn, search is `rg` via Bash — and that combination has never been exercised end to end.

## Open decisions

- Whether to build `plugin/skills/recall/` at all. Once the local corpus is integrated into a living design document and gitlore-managed memory with a shared tier, its remaining job is only "select from the in-context index, then Read" — which is `gitlore:recall` minus the hook. It earns its place only as the portable path for installs without gitlore.
- Where the Claude Code capability facts should live. They are stated both in `agents/decisions/operational-tooling.md` and in the `cc-subagent-context-capabilities` memory. Memory guidance says a memory duplicating what another artifact owns loses; but the memory is marked a global candidate and the decision doc is edify-local. One of the two should become the owner when the corpus integration lands.