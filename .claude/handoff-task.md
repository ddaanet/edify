## Current task

The revived pipeline's recall mechanism has been rewired off index Reads and
onto select-from-context-then-Read, with gate anchors moved to the recall
artifact; the `/recall` skill itself is still unbuilt.

## Open decisions

- Whether to build `plugin/skills/recall/` at all. Once the local corpus is
  integrated into a living design document and gitlore-managed memory (with
  shared tier), its remaining job is only "select from the in-context index,
  then Read" — which is `gitlore:recall` minus the hook. It earns its place
  only as the portable path for installs without gitlore.
- Whether subagents have the `Task` tool. The `Skill` half of the old
  "sub-agents lack Task and Skill tools" claim was probed false; `Task` was
  not probed. Four documents now rest on implementer-bias policy instead and
  mark the capability unverified. One probe closes it.
