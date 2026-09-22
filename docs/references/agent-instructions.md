# Agent instructions and model choice

Decisions governing the prose an agent reads and the model that reads it: how a
model is assigned to a dispatch, and how instructions are ordered, formatted and
sized for the model class. Read this before writing a skill, a fragment, an
agent definition or a dispatch prompt.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`.

## Model selection

**D-41 — Assign model by the correctness property being verified, not by
authorship or task label.** State-machine routing, architectural wiring and
design-invariant compliance need opus; behavioral changes within a function need
sonnet; mechanical substitutions need sonnet at most, because test pass/fail is
sufficient signal. Matching the reviewer to the author's model ("haiku wrote it
→ sonnet reviews it") and blanket-opus inheritance from the orchestrator are
both wrong. Haiku writes state-machine code that looks plausible and has subtle
wiring errors; opus reviewing grep-and-replace is waste.

**D-79 — Two dispatches are fixed, and a runbook item carries no model.** A
`test-driver` dispatch runs sonnet in RED and in GREEN; a dispatch whose
deliverable is prose runs opus. Nothing overrides either — they sit above the
artifact-type override and the type default alike.

The `Model:` line on a runbook item is removed rather than demoted. It is
written at planning time by a skill that knows neither which agent type the
dispatcher will pick nor what the work turns out to involve, so it cannot be
right by construction; the observed failure was a blanket `Model: opus` copied
from `runbook-format.md`'s own worked example onto three tdd items, sending
every test-driver dispatch to opus while the type default said sonnet. A field
whose main effect is teaching a habit through its example is a field to delete.

What replaces it is escalation on demand — the agent returns
`escalated: <reason>` and the dispatcher re-dispatches at the higher model, the
mechanism D-30 already specifies for `edify:refactor`. Predicting an item's
difficulty before anyone has read the code is an estimate, and this project does
not take estimates. The cost is one failed dispatch on a genuinely hard item;
the benefit is that no planner guesses.

**D-42 — Prose artifacts consumed by LLMs are opus work.** Skills, fragments,
agent definitions and design documents are instructions whose wording determines
downstream agent behavior. The rule is stated by **artifact kind, not by path**
— a path list enumerating edify's own directories does not reach a consumer
repository's prose, which is how a changelog entry under a consumer's `docs/`
came to be dispatched at sonnet. Assigning by "edit complexity" rather than
artifact type is the anti-pattern. The rule targets cases where design decisions
happen *during* editing — when an outline pre-resolves every decision and
specifies exact insertion points, execution is mechanical and delegation
ceremony exceeds the edit cost.

**D-43 — Discovery and audit over skills, agents and fragments need sonnet
minimum.** Haiku grades generously, misses dominant failure patterns and
produces false positives that require opus validation — double work.
*Grounding:* haiku graded 0 skills at C where sonnet found 3, missed the
dominant description anti-pattern (18/30), and produced 15 gate findings against
sonnet's 12.

**D-44 — Model tier is a configurable knob, not an architectural constraint.**
Stabilize at sonnet, optimize downward once patterns are proven and failure
modes understood. Defaulting to haiku for cost before validation is the
anti-pattern.

**D-45 — Tier-aware error classification.** Sonnet and opus execution agents
self-classify errors and report the classification; haiku agents report raw
errors for the orchestrator to classify. Moving all classification to the
orchestrator because haiku cannot do it ignores the capable agents and loses
fidelity, since the execution agent holds the full error context.

**Model tier naming.** Premium (opus) / standard (sonnet) / efficient (haiku),
not T1/T2/T3 — "T3" reads ambiguously as either the lowest tier or the third
from the top.

**No model-tier introspection exists.** An agent consistently misidentifies
itself as sonnet while running as opus. Do not guess: ask, stay silent, or rely
on an external signal.

## Prompt and instruction structure

**D-61 — Order by position bias.** LLMs show strong primacy bias, secondary
recency bias, and weakest attention in the middle. Critical rules go at the
start, guidance at the end, important-but-not-critical in the middle where the
bulk of content sits. *Sources:*
[Serial Position Effects of LLMs](https://arxiv.org/html/2406.15981v1),
[Exploiting Primacy Effect](https://arxiv.org/html/2507.13949),
[Positional Bias in Financial Decision-Making](https://arxiv.org/html/2508.18427).
The 20/60/20 split sometimes quoted alongside this comes from organizational
change management and is *not* validated for LLMs — treat it as a starting point
(L-3).

**D-62 — Format by content type.** Discrete rules as bullets (higher adherence);
connected concepts as prose (cohesion); critical rules with visually salient
markers; examples in code blocks. *Source:*
[Effect of Selection Format on LLM Performance](https://arxiv.org/html/2503.06926).

**D-63 — Instruction density varies by model class.** Opus takes concise prose
and infers; sonnet takes clear bullets with context; haiku needs explicit steps,
salient markers and DO-NOT examples. Expansion ranges: 3-5 rules per module for
opus, 8-12 for sonnet, 12-18 for haiku.

**D-64 — Rule adherence degrades past roughly 200 rules.** The system prompt
consumes about 50, leaving ~150. Counting is marker-based so the generator
defines what a rule is, rather than a parser heuristic guessing (L-3 — the 200
figure is an empirical observation, not a calibrated threshold).

**D-65 — Contradictions resolve by position, so hook output must reinforce
standing rules.** A hook message sits in the recency zone and a standing rule in
primacy; when they disagree, the agent follows the hook. A hook that blocks a
dangerous action must give guidance aligned with the rule it enforces — "retry
your git command, do not delete lock files" rather than a bare "retry", which
sends the agent to retry the wrong command.

**D-66 — Contents are only present if explicitly loaded.** There is no implicit
file loading. Each Read appends a new content block; "caching" is prompt-prefix
matching at the API level, not application-level deduplication.

**D-78 — Skills ask inline in numbered prose, never through `AskUserQuestion`.**
The picker is shiny and costs nothing to reach for, which is the problem: it
hides a user turn. The exchange does not read back as prompting in the
transcript, so the record of how a decision was settled is lost to the next
session and to the user rereading the thread — and for `requirements` and
`formalize`, that record is the justification for the artifact they produce. The
option list also silently bounds what the user can say, which defeats
elicitation.

The replacement form: numbered plain prose, one turn, each question carrying a
**proposed answer** inferred from context, with silence taken as agreement. The
user corrects a draft instead of filling a blank, and the thread proceeds
without a round-trip. Rewritten at four call sites (`review`, `requirements`,
`formalize`; `proof` declared the tool without calling it). Enforced
structurally by omission from `allowed-tools` per D-50 — `review` had already
dropped the declaration while still instructing the call, so the instruction was
unsatisfiable. Delegated reviewers are a separate case already covered: they
have no user at all (`plugin/agents/corrector.md`), and a reviewer reaching for
a question has hit a dispatch-prompt defect.

The bounded option list is the defect, not the tool that renders it. `proof`
ended every item with `Verdict? (a)pprove (r)evise (k)ill (s)kip` — an inline
menu, so the `allowed-tools` omission never reached it — and it invited a single
character where the gate wants a judgement. It now proposes the verdict it
thinks the item deserves, with its reason and, for a revision, the amended item
text, and reads the disposition from the free-form reply; an unsettled reply
costs one clarifying question rather than a guessed verdict. That is the same
proposed-answer form, applied to a disposition instead of a question.

The norm behind both cases is plain conversation (user ruling, 2026-09-21): the
picker makes a non-binary answer hard to give and obscures its own output in the
transcript, so plain-text interaction is the default for every skill, whatever
renders the alternative. The conclusion stays worded against `AskUserQuestion`
because that is the mechanism that exists; it takes no position on interaction
mechanisms that do not exist yet.

## Rejected alternatives

**Inlining a "top N" subset of a reference file to avoid a Read** — the agent
picks from the visible subset unaware that better matches exist, creating a
knowledge ceiling. Keep the full Read or move selection into a tool; partial
inlining is worse than both.
