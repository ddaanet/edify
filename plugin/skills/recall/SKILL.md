---
name: recall
description: >-
  Resolve a plan's recall artifact and select and Read relevant memory-index
  entries for the current task or a given topic — the whole recall checkpoint
  for the edify pipeline. Triggers on /recall, "recall", "check memory", or
  when a pipeline skill or agent reaches its recall checkpoint. Not needed for
  facts already in this context.
allowed-tools: Read, Bash
user-invocable: true
---

# Recall — Select and Read Memory

The one procedure for every recall checkpoint in the edify pipeline: resolve
the plan's recall artifact, select further entries from the memory index, Read
their bodies, report. Callers do not restate any of this — they invoke this
skill with a plan directory and a topic, and add only their own delta.

This skill reads; it never writes. A caller that needs its selection to
survive past the turn (`plans/<job>/recall-artifact.md`) writes that artifact
itself.

## Invocation

`Skill(skill: "edify:recall", args: "<plan-dir> — <topic>")`. Both parts are
optional. A caller whose recall recurs — per item, per loop iteration —
invokes this skill once; every later recurrence runs the loaded procedure
inline, since a further `Skill` call only reprints a body already in context.

- **`<plan-dir>`** — a `plans/<job>` path. Present: step 1 runs. Absent:
  step 1 is skipped and selection starts at the index.
- **`<topic>`** — what to select against. Absent: select against what the
  conversation is actually doing right now — the task and how it's being
  approached, not a literal string.

## Procedure

**1. Resolve the recall artifact.** When a plan directory was named and
`<plan-dir>/recall-artifact.md` exists, Read it, then Read every file it
lists. Those files carry the upstream planner's curation — decision content,
failure modes, quality anti-patterns — and cover corpora the index does not
reach. Entries the caller already supplied in a delegation prompt take
precedence: do not re-resolve them.

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

**4. Select under discipline.** At most 5 entries, covering whatever step 1
did not already supply. Include only entries you are certain will help —
unsure means exclude. An empty selection is legitimate; say so rather than
force a match. Match on what the task is about, not surface keyword overlap.
Do not re-select a body already pulled this conversation.

**5. Batch-Read.** Issue every selected Read in a single message.

**6. Report.** State what was selected and why. When nothing matched and the
artifact was absent or added nothing, say that explicitly — the checkpoint was
reached and yielded nothing. Silence is indistinguishable from a skipped gate,
which is why callers treat this invocation as their structural anchor. A
caller may override this step to stay silent on a null result; `/proof`'s
per-item recall does.

A subagent that lacks the index should not invoke this skill — recall assumes
a caller that has the index in context; a caller that doesn't is not this
skill's problem to solve.
