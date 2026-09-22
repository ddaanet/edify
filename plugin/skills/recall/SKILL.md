---
name: recall
description: >-
  Resolve a plan's recall artifact — its memory files and the skills it lists —
  and select and Read further memory-index entries for the current task or a
  given topic; the whole recall checkpoint for the edify pipeline. Triggers on
  /recall, "recall", "check memory", or when a pipeline skill or agent reaches
  its recall checkpoint. Not needed for facts already in this context.
allowed-tools: Read, Bash, Skill
user-invocable: true
---

# Recall — Select and Read Memory

The one procedure for every recall checkpoint in the edify pipeline: resolve the
plan's recall artifact, select further entries from the memory index, Read their
bodies, report. A caller invokes this skill with a plan directory and a topic
and adds only its own delta — except a dispatch prompt for a sub-agent that may
hold no `Skill` tool, which restates step 1 inline
(`../../fragments/delegation.md` §Recall Artifacts For Sub-Agents).

This skill reads; it never writes. A caller that needs its selection to survive
past the turn (`plans/<job>/recall-artifact.md`) writes that artifact itself.

## Invocation

`Skill(skill: "edify:recall", args: "<plan-dir> — <topic>")`. Both parts are
optional. A caller whose recall recurs — per item, per loop iteration — invokes
this skill once; every later recurrence runs the loaded procedure inline, since
a further `Skill` call only reprints a body already in context.

- **`<plan-dir>`** — a `plans/<job>` path. Present: step 1 runs. Absent: step 1
  is skipped and selection starts at the index.
- **`<topic>`** — what to select against. Absent: select against what the
  conversation is actually doing right now — the task and how it's being
  approached, not a literal string.

## Procedure

**1. Resolve the recall artifact.** When a plan directory was named and
`<plan-dir>/recall-artifact.md` exists, Read it, then Read every file it lists.
Those files carry the upstream planner's curation — decision content, failure
modes, quality anti-patterns — and cover corpora the index does not reach. A
delegation prompt supplies entries as **paths**, never as inlined content
(`../../fragments/delegation.md` §Recall Content In Delegation Prompts): Read
those paths and do not re-select against the index for them.

Load the artifact's `## Skills to load before executing` list in the same step,
where it has one: `Skill(skill: "<plugin>:<name>")` per entry. A sub-agent
without the `Skill` tool Reads the body instead, at
`~/.claude/plugins/cache/<owner>/<plugin>/<version>/skills/<name>/SKILL.md`;
several versions are usually installed, so take the newest —

```bash
ls -dt ~/.claude/plugins/cache/*/<plugin>/*/skills/<name>/SKILL.md | head -1
```

— the glob covering both segments that vary, since a version directory may be a
content hash rather than a semver. No match means the skill is not installed
here: report the name and continue. Never reconstruct a body from a description.

**2. Match the topic against the index.** The index's one-line hooks are a
routing table: match the topic against them thematically — no deterministic
search does this matching. The index is normally injected at session start.
Confirm its lines are in this context before matching against them; where they
are not, Read `MEMORY.md` under the corpus root step 3 resolves and match
against that. Its absence is ordinary, not impossible: one prior session found
it missing at every recall checkpoint. Where the file is absent too, run
`rg --files` over the corpus root and select on filenames instead.

**3. Resolve the corpus.** The corpus is the memory store this session's own
context says it lives in — named in the auto-memory system-prompt section, not a
fixed path. In an edify checkout that resolves to `memory/`; elsewhere it
resolves wherever that session's store lives. Tier subdirectories included.
Nothing outside that store.

**4. Select under discipline.** At most 5 entries — an arbitrary ceiling, not
calibrated — covering whatever step 1 did not already supply. Include only
entries you are certain will help — unsure means exclude. An empty selection is
legitimate; say so rather than force a match. Match on what the task is about,
not surface keyword overlap. Do not re-select a body already pulled this
conversation.

**5. Batch-Read.** Issue every selected Read in a single message. Index links
are store-relative, so join each to the corpus root resolved in step 3 — a link
reading `ddaanet/foo.md` is `<root>/ddaanet/foo.md`. Never hardcode the root:
the same index resolves against whatever path this session's context names, and
a Read of the bare link fails.

**6. Report.** State what was selected and why. When nothing matched and the
artifact was absent or added nothing, say that explicitly — the checkpoint was
reached and yielded nothing. Silence is indistinguishable from a skipped gate,
which is why callers treat this invocation as their structural anchor. A caller
may override this step to stay silent on a null result; `/proof`'s per-item
recall does.

A caller that reaches this checkpoint without the index is step 2's conditional
Read. It runs the same procedure.
