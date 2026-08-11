# `edify:recall` — Design

**Date:** 2026-08-11
**Status:** Approved design, pre-implementation

## 1. Context

Eight files in the plugin carry their own copy of the same paragraph: *the
memory index is already in your context, do not Read it, pick the relevant
entries, Read those files.* Four skills (`requirements`, `design`,
`orchestrate`, `review-plan`) and four agents (`corrector`, `design-corrector`,
`outline-corrector`, `runbook-outline-corrector`). The copies have drifted in
wording, in what they say about subagents, and in which corpora they name.

`gitlore:recall` covers the same ground, but edify and gitlore are separate
value propositions: an edify install must not require gitlore to have a working
recall checkpoint. The cost of shipping a twin is picker ambiguity when both are
installed, addressed by the description (D3).

## 2. Requirements

**FR1** — One skill, `plugin/skills/recall/`, owns the recall procedure: select
entries from the memory index, Read their bodies.

**FR2** — Selection accepts an optional topic from the caller. With a topic,
entries are selected against it. Without one, entries are selected against
triggers the conversation has actually surfaced — a string in a tool result, a
flag in a file just opened.

**FR3** — The index is treated as already in context and is not Read. The single
exception: a compaction dropped it, or it was edited this session.

**FR4** — Where no index is in context, the skill degrades to `rg --files
memory/` and selects on filenames.

**FR5** — The corpus is `memory/`, tier subdirectories included. Nothing else.

**FR6** — Selection discipline: at most 5 entries; include only entries you are
certain will help; unsure means exclude; an empty selection is a legitimate
answer; match on what the task is about, not surface keyword overlap; do not
re-select a body already pulled this conversation.

**FR7** — Every Read issues in a single message.

**FR8** — The skill writes nothing. `plans/<job>/recall-artifact.md` stays with
its callers.

**FR9** — The eight call sites invoke the skill in place of their inlined
paragraph, each supplying its own topic.

## 3. Procedure

The body follows FR2–FR7 in order: establish the topic, confirm the index is in
context (FR3) or degrade (FR4), select under FR6, batch-Read under FR7, act.

The topic arrives as the skill's invocation argument — `Skill(skill:
"edify:recall", args: "<topic>")`. Absent argument means FR2's trigger-based
branch.

Frontmatter: `allowed-tools: Read, Bash` — `Bash` serves the FR4 degrade path
only — and `user-invocable: true`.

## 4. Scope of change

| File | Change |
|------|--------|
| `plugin/skills/recall/SKILL.md` | new |
| `requirements`, `design`, `orchestrate`, `review-plan` SKILL.md | fallback paragraph → invocation; drop `agents/decisions/*.md` |
| `corrector`, `design-corrector`, `outline-corrector`, `runbook-outline-corrector` | same |
| `requirements/SKILL.md` artifact format | drop the `agents/decisions/<name>.md` example entry |
| `proof/SKILL.md` | delete the per-item recall directive (D4) |
| `plugin/bin/prepare-runbook.py` | `resolve_recall_entries` docstring — memory files, not "memory and decision files" |
| `CLAUDE.md`, `plugin/README.md` | list the skill |

`resolve_recall_entries` resolves whatever repo-relative paths the artifact
names, so dropping a corpus needs no code change.

## 5. Decisions

**D1 — The skill owns select-then-Read; callers own the artifact.** Pipeline
callers and a human invoker diverge in three places: pipeline callers Read
`plans/<job>/recall-artifact.md` first and fall back to index selection;
`requirements` must *write* that artifact, null marker included, as a gate
anchor; and pipeline selection is topic-based where mid-task selection is
trigger-based. The first two are plan plumbing and stay with the callers. The
third becomes the FR2 topic argument, so one body serves both without modes.

**D2 — Subagents invoke the skill directly.** A subagent receives the index and
the `Skill` tool, and never receives auto-fetched bodies
(`memory/cc-subagent-context-capabilities.md`). The four corrector agents
therefore need the same procedure as the skills, from the same source.

**D3 — The description names the edify pipeline.** With gitlore installed, two
skills named `recall` are offered at once. Purpose-first wording that names the
pipeline routes the picker.

**D4 — `proof` loses per-item recall.** The mature sibling
(`../skills/dist/proof-en.skill`) carries no per-item recall at all. Reviving it
with a real procedure would re-add a mechanism its own lineage discarded.

**D5 — The ceiling of 5 is borrowed, not invented.** Claude Code's own recall
classifier caps selection at five and states the same certainty bar
(`claude-code-system-prompts/system-prompts/agent-prompt-determine-which-memory-files-to-attach.md`,
CC 2.1.210). FR6 adopts that number and that discipline with attribution.

**D6 — `agents/decisions/` leaves the corpus.** Those files are being folded
into the living design doc, so recall must not encode a dependency on them.

## 6. Rejected alternatives

**Depend on `gitlore:recall`.** Rejected: it makes gitlore a hard dependency of
the edify pipeline, which is the premise this design denies.

**Skill without the rewire.** Rejected: the duplication is the motivation, and a
skill no call site invokes goes unexercised.

**A numeric ceiling derived from pipeline reasoning.** Rejected before D5
surfaced the upstream source — a threshold reasoned into existence is
confabulation. The number stands only because CC publishes it.

**A configurable corpus root.** Rejected: machinery for a portability problem
FR4 already covers.

## 7. Verification

`just precommit`, then manual invocation of the skill and of one rewired call
site. This build does not route through the revived pipeline; exercising that
pipeline is separate work and would confound both results.
