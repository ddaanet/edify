---
name: recall
description: >-
  Select and Read relevant memory-index entries for the current task or a
  given topic, for the edify pipeline. Triggers on /recall, "recall", "check
  memory", or when a pipeline skill or agent reaches its recall checkpoint.
  Not needed for facts already in this context.
allowed-tools: Read, Bash
user-invocable: true
---

# Recall — Select and Read Memory

One procedure for the edify pipeline's recall checkpoints: select entries from
the memory index, Read their bodies. Owns select-then-Read only — callers that
plan across turns (e.g. `plans/<job>/recall-artifact.md`) own that artifact
themselves; this skill writes nothing.

## Procedure

**1. Establish the topic.** The invocation argument is the topic —
`Skill(skill: "edify:recall", args: "<topic>")`. Absent argument: select
against what the conversation is actually doing right now — the task and how
it's being approached, not a literal string.

**2. Treat the index as already in context.** The memory index is injected at
session start and is never Read. Its one-line hooks are a routing table:
match the topic against those hooks, thematically — no deterministic search
does this matching. Degrade only where the index is structurally absent (the
auto-memory feature is off, or no store is configured for this session): run
`rg --files memory/` at the project root and select on filenames instead.

**3. Resolve the corpus.** The corpus is the memory store this session's own
context says it lives in — named in the auto-memory system-prompt section,
not a fixed path. In an edify checkout that resolves to `memory/`; elsewhere it
resolves wherever that session's store lives. Tier subdirectories included.
Nothing outside that store.

**4. Select under discipline.** At most 5 entries. Include only entries you
are certain will help — unsure means exclude. An empty selection is
legitimate; say so rather than force a match. Match on what the task is
about, not surface keyword overlap. Do not re-select a body already pulled
this conversation.

**5. Batch-Read.** Issue every selected Read in a single message.

**6. Report.** State what was selected and why, or that nothing matched. This
skill writes no file — a caller that needs the selection to survive past this
turn (a recall artifact) records it itself.

A subagent that lacks the index should not invoke this skill — recall assumes
a caller that has the index in context; a caller that doesn't is not this
skill's problem to solve.
