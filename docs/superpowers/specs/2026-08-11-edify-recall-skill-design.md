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
entries are selected against it. Without one, selection runs against what the
conversation is actually doing — the task and how it's being approached. A
string in a tool result or a flag in a file just opened can prompt the check,
but the match itself is thematic, per FR6, not literal keyword search: no
deterministic tool, however much context it's given, does that matching.

**FR3** — The index is treated as already in context and is never Read.

**FR4** — Where no index is in context, the skill has no stated path to go on
and degrades to a conventional guess: `rg --files memory/` at the project
root, selecting on filenames.

**FR5** — The corpus is the memory store itself, wherever this session's
context says it actually lives — named in the auto-memory system-prompt
section, not assumed to be a fixed path. In this project that resolves to
`memory/`; a different project, or a different store such as a non-default
`~/.claude/` location or a plugin-provided mount like gitlore's, resolves
elsewhere. Tier subdirectories included, wherever the store places them.
Nothing else.

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

The body follows FR2–FR7 in order: establish the topic, treat the index as
already in context per FR3 — degrading per FR4 only where it's structurally
absent (feature off, no store configured) — select under FR6, batch-Read
under FR7, act. A subagent regime that lacks the index is not this case: per
D2, recall assumes the caller is one that gets it, and a caller that isn't
simply shouldn't invoke recall — that's not FR4's problem to solve.

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
| `proof/SKILL.md` | per-item recall directive → `edify:recall` invocation (D4) |
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

**D4 — `proof` keeps per-item recall, rewired to invoke the skill.** The
original plan to delete it argued from the mature sibling
(`../skills/dist/proof-en.skill`) carrying no per-item recall — but that
sibling was produced by stripping memory-related content out of a copy of this
same `proof` skill, so its absence is circular evidence, not independent
justification. `proof` becomes a ninth invocation site: the inline `**Per-item
recall (FR-3):**` procedure is replaced with `Skill(skill: "edify:recall",
args: "<topic>")`, same call shape as the eight FR9 sites.

**D5 — The ceiling of 5 is borrowed, not invented.** Claude Code's own recall
classifier caps selection at five and states the same certainty bar
(`claude-code-system-prompts/system-prompts/agent-prompt-determine-which-memory-files-to-attach.md`,
CC 2.1.210). FR6 adopts that number and that discipline with attribution.

**D6 — `agents/decisions/` leaves the corpus.** Those files are being folded
into the living design doc, so recall must not encode a dependency on them.

**D7 — Compaction neither drops the index nor refreshes it, so FR3 needs no
exception clause.** Live-tested in this session, not reasoned: a marker line
was inserted into `memory/MEMORY.md`, then the session compacted twice — once
automatically, once via an explicit `/compact`. After the first, the
resumption message carried a memory-index block showing pre-edit content, no
marker — which rules out a fresh disk read at compaction (the marker was
already on disk by then; a fresh read would have shown it). After the second,
no memory-index block was re-injected into context at all. Conclusion: the
index is never dropped — some copy is always present — but it is also never
refreshed by compaction; what's in context is a frozen copy from session
start. That leaves nothing for a conditional Read to key off. An edit the
agent just made is already visible from the edit's own diff, independent of
the frozen block. An edit it has no memory of making leaves no signal to
detect, so a conditional Read has no condition to test. FR3 drops the
exception clause rather than replace it.

## 6. Rejected alternatives

**Depend on `gitlore:recall`.** Rejected: it makes gitlore a hard dependency of
the edify pipeline, which is the premise this design denies.

**Skill without the rewire.** Rejected: the duplication is the motivation, and a
skill no call site invokes goes unexercised.

**A numeric ceiling derived from pipeline reasoning.** Rejected before D5
surfaced the upstream source — a threshold reasoned into existence is
confabulation. The number stands only because CC publishes it.

**A configurable corpus root.** Rejected: FR5 already resolves the root from
session context; a config knob would duplicate that for no benefit.

## 7. Verification

`just precommit`, then manual invocation of the skill and of one rewired call
site. This build does not route through the revived pipeline; exercising that
pipeline is separate work and would confound both results.
