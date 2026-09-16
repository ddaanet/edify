# plugin-dev:skill-reviewer on plugin/skills/recall (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — parts 2 and 3 pending.**

Scope: `SKILL.md` alone — no `references/`, no fragment links, so no routed files to
check for drift. Consistency was checked against in-repo callers instead:
`skills/requirements/`, `skills/design/`, `skills/runbook/`, `skills/inline/`,
`skills/orchestrate/`, `skills/proof/`, `agents/*-corrector.md`,
`fragments/delegation.md`, `docs/design.md`.

Measured: 76 lines, 3810 bytes whole file; 537 words and 3381 bytes of body after
frontmatter; `description:` 355 bytes.

## Critical

**C1. The skill removes the mechanism its own anchor claim rests on.** SKILL.md:46-48
says the memory index "is injected at session start and is never Read".
`docs/design.md:665-674` (D-48) records the opposite as the canonical gate anchor:
"the recall pass: a Read of `memory/MEMORY.md` followed by Reads of the files it
names. The index Read is unskippable and the per-file Reads require knowing which
entries matter, so the pair proves selection happened." The skill then reuses D-48's
conclusion at :69-71 ("Silence is indistinguishable from a skipped gate, which is why
callers treat this invocation as their structural anchor") without the index Read
that produced it. With :62 ("An empty selection is legitimate"), a null recall emits
zero tool calls — the unfalsifiable gate D-48 was written against. One document is
stale. `docs/design.md:859-861` sides with the skill ("Never instruct an agent to
Read the index — it already has it"), so the design doc contradicts itself and the
reconciliation has to happen there too.

**C2. Step 5 omits the path-prefixing rule, so every Read in the batch fails.**
SKILL.md:65 says only "Batch-Read. Issue every selected Read in a single message."
Index entries in `memory/MEMORY.md` are store-relative links, e.g.
`[Bash tool: set -e is inert](ddaanet/bash-tool-set-e-inert.md)`, while the file is at
`memory/ddaanet/bash-tool-set-e-inert.md`. Nothing tells the agent to prefix the
store path. The sibling gitlore skill states the rule in its own step 3.
SKILL.md:56 ("Tier subdirectories included") gestures at the layout but never gives
the prefix.

## Major

**M1. Near-total duplication with the enabled `gitlore:recall`, plus a trigger
collision.** Both descriptions name "recall" and "check memory" and close with the
byte-identical "Not needed for facts already in this context"; neither excludes the
other. The bodies overlap clause for clause: the five-entry ceiling, "unsure means
exclude", "do not re-select a body already pulled", "an empty selection is
legitimate", the single-message batch Read (SKILL.md:59-65 vs gitlore steps 2-3).
Genuinely edify's own: step 1 (the plan recall artifact) and step 6 (the report
contract). Recommend narrowing to those two, routing selection discipline to
`gitlore:recall`, and adding an exclusion clause. Both descriptions load every
session in every repo where the plugins are enabled.

**M2. Step 2 consumes the corpus that step 3 resolves.** SKILL.md:50-51 ends step 2
with a degrade path hardcoding `rg --files memory/` at the project root; :53-57 then
opens step 3 with "The corpus is the memory store this session's own context says it
lives in — named in the auto-memory system-prompt section, not a fixed path". The
hardcoded path is wrong in any non-edify checkout, which is exactly when the degrade
path matters. Move corpus resolution ahead of it.

**M3. "Callers do not restate any of this" is falsified by three in-repo callers**
(SKILL.md:17-18). Step 1 is restated at `orchestrate/references/dispatch-composition.md:16`,
`inline/references/review-dispatch-template.md:26`, and `fragments/delegation.md:75`.
Those restatements are correct, because a dispatched subagent may have no `Skill`
tool, so the blanket claim is what needs fixing.

**M4. The absolute "never Read" drops the compaction exception** (SKILL.md:46-48).
The gitlore skill keeps one: Read the index once if a compaction has happened since
it loaded or it was edited this session. As written, the skill has the agent select
against something it may no longer hold.

**M5. Step 1's precedence clause contradicts the delegation fragment.** SKILL.md:43-44
says entries the caller supplied in a delegation prompt take precedence, "do not
re-resolve them", while `fragments/delegation.md:87-89` forbids inlining resolved
recall content in delegation prompts. If "supplied" means inlined content it
describes a prohibited case; if it means paths, "do not re-resolve" is wrong because
a path still has to be Read.

## Minor

**m1. Unattributed ceiling**: SKILL.md:60 "At most 5 entries" with no grounding. The
gitlore skill grounds the same number in Claude Code's own recall returning at most
five files. Name the source or drop the number.

**m2. A prohibition that cannot fire in time**: SKILL.md:74-76 says "A subagent that
lacks the index should not invoke this skill", but a subagent reads that only after
the body has loaded, so the cost is already paid. Rewrite as an instruction to the
agent now holding the body.

**m3. Overstated scope**: SKILL.md:15 calls this "The one procedure for every recall
checkpoint", then the same file carves out two exceptions (:70-72, :74-76).

**m4. Imperative form is fine, with one qualification.** All six steps lead verb-first
and there is no second-person instruction subject, so no true violation. The framing
paragraphs (:15-22, :74-76) are third-person descriptions of caller behaviour, which
is what lets the false claim in M3 sit unchecked.

**m5. Two step verbs name states rather than acts**: step 2 "Treat the index as
already in context" (:46) and step 3 "Resolve the corpus" (:53) produce no observable
action. Folding them into step 4 would leave four steps that each do something.

## What holds up

Description shape follows the house rule and at 355 bytes sits in the same band as
siblings. `allowed-tools: Read, Bash` is adequate, since the field grants rather than
restricts. Progressive disclosure is right for 537 words. The write boundary is
stated once (:20-22) and matches the callers that do the writing
(`requirements/SKILL.md:48`, `design/references/write-outline.md:55`). The `/proof`
override (:70-72) matches `proof/SKILL.md:100` exactly, including the silent-null
behaviour. The recurrence rule (:27-29) matches how `proof/SKILL.md:100` and
`runbook/SKILL.md:72` use it. Every caller checked carries `Skill` in its frontmatter
or agent tool list, and the two dispatch templates for agents that lack it supply the
artifact fallback.

**Checks that found nothing:** no broken file references, no stale volatile git
state, no model guidance in the body, and the argument separator at :26 matches every
call site found.

## Suggested order of work

Settle C1 first, because whether the index Read stays decides what steps 2, 4 and 6
say. C2 is a one-line addition and can land immediately. M1 is the largest structural
change and should follow the C1 decision, since the answer determines how much of
gitlore's body edify still needs to carry.
