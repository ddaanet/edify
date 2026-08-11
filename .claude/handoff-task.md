## Current task

The revived pipeline's dispatch surface (`Agent` spawn, name-based `SendMessage` resume, `rg`-via-Bash search) has never been exercised end to end. Separately, the local corpus's memory half is now on gitlore: the `ddaanet` tier is mounted and edify's local memory triaged against it. Folding the corpus into a living design document is still unstarted.

## Open decisions

- Whether to build `plugin/skills/recall/` at all. The tier-mount precondition is now met — `ddaanet` is mounted and active — so its remaining job would be "select from the in-context index, then Read," which is `gitlore:recall` minus the hook. It earns its place only as the portable path for installs without gitlore; the living-design-doc half of the corpus integration is still open.
- Where the Claude Code capability facts should live. `cc-subagent-context-capabilities` was judged repo-specific this session and stayed in edify's local memory rather than the tier, so both it and `agents/decisions/operational-tooling.md` are edify-local and still duplicate each other. One should become the owner when the corpus integration lands.