# plugin-dev:skill-reviewer on plugin/skills/design (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — remainder requested; report was
cut mid-sentence inside M1.**

Scope: `skills/design/SKILL.md` and everything it routes through —
`references/write-outline.md`, `write-design.md`, `design-content-rules.md`,
`research-protocol.md`, `write-inline-plan.md`, and
`fragments/continuation-passing.md`. Cross-checked against `docs/design.md`
§6.4/§6.5, `plugin/bin/triage-feedback.sh`, `skills/proof/`, `skills/inline/SKILL.md`.

## Measurements (measured, `wc -w`)

| File | Lines | Words |
|---|---|---|
| `skills/design/SKILL.md` | 186 | 1623 |
| `references/write-outline.md` | 232 | 1755 |
| `references/design-content-rules.md` | 151 | 978 |
| `references/write-design.md` | 96 | 610 |
| `references/research-protocol.md` | 35 | 265 |
| `references/write-inline-plan.md` | 32 | 229 |
| `fragments/continuation-passing.md` | 167 | 1172 |

Frontmatter description: 31 words, 270 characters. Peer skills range 7 words
(`review`) to 61 (`formalize`), median 32.

## Critical

**C1. The Defect route has no destination.** SKILL.md:72 and :153 send
Defect-classified work to a "structured-bugfix workflow". No such skill, agent,
command or reference exists; a repo-wide grep finds the string only in those two
lines and in `plans/reports/` documents proposing it as future work. Defect is one
of four values in the mandatory classification block (SKILL.md:121), so any task
reaching it stops at a name that resolves to nothing. Add the workflow, or fold
Defect back into Simple/Moderate/Complex with the investigation steps inline.

**C2. The skill claims `/proof` dispatches correctors. It does not.** Four sites
assert it: SKILL.md:150 ("outline-corrector dispatched by /proof on revise/kill"),
`write-outline.md:159` and `write-design.md:60` (both "on terminal action 'apply'"),
and `write-inline-plan.md:31` (a "/proof Corrector Dispatch table"). Neither
`skills/proof/SKILL.md` nor `references/item-review.md` contains a corrector
dispatch or such a table; the batch-apply step (`item-review.md:48-58`) applies the
user's recorded verdicts only. Two of the four also disagree on the trigger
(revise/kill vs apply). Consequence: on the Complex path the outline-corrector
still runs because `write-outline.md:132` dispatches it directly at A.6, but on the
Moderate non-prose path SKILL.md:150 is the only mention, so the T6 gate defined at
`docs/design.md:452` never fires. Same for design-corrector via `write-design.md:60`,
though C.3 at `write-design.md:27` covers it earlier.

**C3. `Edit` is absent from `allowed-tools` but the procedure requires it.**
SKILL.md:8 declares `Agent, Read, Write, Bash, WebSearch, WebFetch, Skill`. The
A.2.5 gate anchor at `write-outline.md:86` says to append recall-selected paths to
the recall artifact via Edit. Siblings that edit artifacts all declare it (inline,
orchestrate, runbook, proof). Add `Edit`, or rewrite that step as a full-file Write.

## Major

**M1. The description misstates the skill's own routing.** SKILL.md:7 ends "routes
moderate to /runbook", but the agentic-prose Moderate path routes to `/inline`
(SKILL.md:145, continuation rule at :185), and the Defect path is omitted. The
trigger clauses are sound; only the summary clause is wrong. Suggested: "routes each
to inline execution, runbook planning, or full design."

**M2. A resumed complex job always goes to `/runbook`, bypassing the C.5 gate.** The
artifact check (SKILL.md:44) reads `design.md exists → route to /runbook` with no
condition, while C.5 (`write-design.md:64-89`) exists to decide the opposite for
prose, investigation and exploration work, and `docs/design.md:539` (D-34) puts the
route decision at C.5. A design written in a prior session loses work-type-aware
routing that D-35 calls an independent decision. Send `design.md exists` to C.5.

**M3. The Author-Corrector Coupling table contradicts the table it points at.**
SKILL.md:162 says to identify the corrector from T1-T6 in `docs/design.md` §6.4,
then SKILL.md:170-174 gives three rows covering only T6, T2 and requirements. It
omits T1 (`design.md` → design-corrector), T3 (runbook-simplifier) and T5 (inline
execution → corrector plus `triage-feedback.sh`), all at `docs/design.md:447-452`.
Since SKILL.md:176 makes the coupling statement mandatory output, a designer editing
the design skill's own format finds no row and reports "update needed: no".

**M4. The execution-routing decision is duplicated and has drifted.**
`write-outline.md:206-224` and `write-design.md:70-86` carry near-identical
pseudocode. They differ: outcome labels ("INLINE"/"inline" vs "direct execution");
third criterion ("No runtime ordering dependencies between files" vs "No cross-file
coordination requiring sequencing"); the prose-path rationale and explicit prose
bypass exist only in `write-outline.md:215-218`. Extract to one reference both
phases read. `plugin/fragments/execution-routing.md` is not that file — it covers
delegation-vs-direct and is referenced only by documents recording its deletion.

**M5. A.5 is specified twice, and the conditional route into `research-protocol.md`
is defeated.** `write-outline.md:89-93` makes reading it conditional on external
research, but A.5 at :103 reads it unconditionally, so the conditional buys nothing.
Both files specify the A.5 output (`write-outline.md:105`, `research-protocol.md:19-25`),
with the escape-hatch paragraph verbatim in both (:107, :35). Split by concern.

**M6. The classification contract with `triage-feedback.sh` silently succeeds for
half its values.** SKILL.md:129 requires the classification block at
`plans/<job>/classification.md`. The script's comparison (`triage-feedback.sh:47-61`)
branches on `Simple` and `Complex` only; `Moderate` and `Defect` fall through to
`verdict="match"` at :61 regardless of evidence. Script defect, but the skill is the
producer side and should not describe the comparison as unconditional.

## Minor

**m1. Ungrounded-threshold marking is inconsistent.** SKILL.md:157 (">5 tasks"),
`write-outline.md:120` ("3 or fewer decisions") and `design-content-rules.md:26`
(">8 items", "<20 LOC") carry the marker; `design-content-rules.md:28` (100-300
items per phase) and :33 ("The 5-repetition threshold balances…") assert as fact.

**m2. A maintainer-facing aside sits inside an executed instruction** (SKILL.md:152,
the verb-oriented-name parenthetical). It costs context on every load.

**m3. `write-inline-plan.md:32` names a status vocabulary that exists nowhere else**
(`inline-planned` parallel to `planned`); neither token appears elsewhere in
`plugin/` or `docs/`, and `docs/design.md:28-35` is a different legend.

**m4. Step numbering shows accretion**: A.0, A.1, A.2, A.2.5, A.3-4, A.5, an
unnumbered re-check, A.6; C.1-C.5 with C.4.5 inserted; SKILL.md:26 opens at "0.
Complexity Triage" and never reaches step 1. Cross-references like SKILL.md:47
("resume from A.5 or A.6") get harder to follow.

**m5. "Verbatim" is ambiguous at SKILL.md:129** — the template above it
(:121-127) is bracketed placeholders, and the parser (`triage-feedback.sh:44`)
would parse a persisted placeholder string and fall through to `match`. Say
"write the filled-in block".

**m6. The recall-diff paragraph is triplicated**: `write-outline.md:97`,
`research-protocol.md:15`, `write-design.md:7`.

**m7. `write-outline.md:39` routes to a glob, not a file** ("Read
`plugin/fragments/*.md` directly when referenced"), unlike every other routing line.

## What is sound

Imperative discipline is clean: a grep across SKILL.md and all five references for
second-person forms and hedges ("you", "your", "should", "can be used", "it is
important") returned no matches. The progressive-disclosure spine is correct —
SKILL.md holds triage and routing, Phase A/B behind `write-outline.md`, Phase C
behind `write-design.md`, content rules behind `design-content-rules.md`; nothing
loads Phase C material for a Simple task. The continuation section (SKILL.md:178-186)
states only its own step-2 prepend rule, as `continuation-passing.md:36-38` asks; the
frontmatter block matches the schema at :25-29 and the default exit matches the
registry row at :98. The D+B anchor pattern is applied at the four places a decision
could be skipped silently (SKILL.md:28, :50, :120, :176), each with its rationale.

## Suggested order of work

C1, C2 and C3 first — the three places the documented procedure cannot execute as
written. Then M2 and M4 together, since both concern the execution-readiness gate.
M1, M3, M5 and M6 are independent. Minors ride along with whichever file they sit in.
