# Deliverable Review: provenance-reach-and-sweep

**Date:** 2026-09-18
**Methodology:** `docs/design.md` §6.8 "Deliverable review"
**Design artifact:** `plans/provenance-reach-and-sweep/outline.md` (no `design.md`)
**Range:** `926e372d02a0366202b2bb6a684551128d1f2a66..HEAD`, read from the
outline's §Provenance. Verified against the superseded artifact: the `Base:` in
`plans/design-routing-and-provenance/outline.md` is the same sha, so the
inheritance rule held on its first real exercise and the range spans both
passes.
**Layer 1:** skipped — 313 added / 99 removed lines, under the 500-line gate.
Layer 2 was a full review, per-file axes and cross-cutting.

## Inventory

| Type | File | +/- | In scope |
|---|---|---|---|
| Agentic prose | `plugin/skills/design/references/route-to-execution.md` (new) | +60 | yes |
| Agentic prose | `plugin/skills/design/references/write-outline.md` | +3/-27 | yes |
| Agentic prose | `plugin/skills/design/references/write-design.md` | +5/-24 | yes |
| Agentic prose | `plugin/skills/design/references/design-content-rules.md` | +21/-2 | yes |
| Agentic prose | `plugin/skills/design/references/research-protocol.md` | +8 | yes |
| Agentic prose | `plugin/skills/design/SKILL.md` | +5/-5 | yes |
| Agentic prose | `plugin/skills/deliverable-review/SKILL.md` | +4/-4 | yes |
| Agentic prose | `plugin/agents/outline-corrector.md` | +9/-1 | yes |
| Agentic prose | `plugin/agents/design-corrector.md` | +18/-14 | partly — see Excess |
| Agentic prose | `plugin/skills/build/SKILL.md` | +8/-5 | partly — see Excess |
| Agentic prose | `plugin/skills/build/references/phase-boundary.md` | +2 | no — unrelated |
| Human docs | `docs/design.md` | +43/-17 | yes |
| Human docs | `docs/changelog.md` | +36 | yes |
| Human docs | `inbox/brief-review-feeds-back-into-design.md` | +81 | no — arrival |
| Human docs | `inbox/recall-skill.md` | +10 | no — arrival |

No code, tests or configuration in the range. Agentic prose and human docs
throughout, as both passes' outlines promised.

**Conformance:** every IN-scope item of both passes produced. No missing
deliverables. Nothing under either OUT list was touched —
`runbook-corrector.md:112`, `design/SKILL.md` Phase 0 branches,
`build/SKILL.md` §4.1 and both correctors' pre-existing criteria are unedited,
and `docs/changelog.md` gained no second entry.

## Critical Findings

None.

## Major Findings

### M-1 — The corrector repair directive destroys a correct `Derived from:`

`plugin/agents/outline-corrector.md:117`, `plugin/agents/design-corrector.md:175`

Both correctors carry, identically:

> **Never fill in `Base:` yourself.** Repair a missing or unverifiable base
> with a `TODO` placeholder in **both fields**, and name in the report what the
> author must supply.

Both agents apply fixes directly rather than reporting them. When the section
is entirely missing, TODO in both fields is right. When `Derived from:`
resolves and only `Base:` is unverifiable, the directive overwrites the one
field that was correct — the field the bullet two lines above calls "a later
pass's only route to `Base:`". The author is then left with strictly less
information than the corrector found.

**Impact:** silent information loss, applied automatically, on the second-pass
path the whole contract exists for. **Fix:** scope the placeholder to `Base:`
and leave `Derived from:` untouched.

### M-2 — The blanket ban blocks the one repair that is not a recomputation

`plugin/agents/outline-corrector.md:117`, `plugin/agents/design-corrector.md:175`,
`docs/design.md:556-558`

The bullet immediately above tells the corrector to Read the artifact named in
`Derived from:` and check `Base:` matches it verbatim. Having read the correct
value, the corrector is barred from writing it, on the rationale that "a base
you compute is the recomputation the Critical bullet names". A verbatim copy
from the named prior artifact is not a computation — it is exactly what
`design-content-rules.md:110` prescribes to the author.

D-80 carries the same over-broad justification: "a base they supplied would be
the same recomputation, so they leave a `TODO` for the author instead."

**Impact:** the Critical case — a second-pass artifact with a recomputed base —
comes back to the author as a TODO plus a report, costing a round-trip while
the corrector held the correct value and had already verified it. **Fix:** allow
the verbatim copy where `Derived from:` resolves and the prior artifact carries
a usable `Base:`; keep the ban on any base the corrector derives.

### M-3 — The preconditions bind the `/runbook` branch on a criterion scoped to the no-runbook case

`plugin/skills/design/references/route-to-execution.md:14-22`

The scope sentence and the bullet's own rationale disagree:

> Both bind every branch this node routes, prose included.
>
> - Edit targets are named, section-level or line-level. **With no runbook the
>   artifact is the item list**, so `/build` walks what the artifact names.

The rationale holds only for the branches that skip `/runbook`. As written, a
Production + behavioral-code job whose design names no section- or line-level
edit targets fails a precondition and is sent back to A.5 or C.1 (`:53-54`) —
rather than to `/runbook`, whose job is to name those targets. The superseded
text applied these criteria only to the `/build` decision
(`write-outline.md`, removed: "Execution-readiness criteria (non-prose paths
only — prose path bypasses these)"), so the restructure widened their reach.

`docs/changelog.md:29-31` records the widening as deliberate
("preconditions, which bind every branch including prose"), so this may be
intended; if so, the rationale clause needs to stop justifying it by the
no-runbook case. This finding is not among the nine and was not raised by
either build review.

### M-4 — The consumer never checks the inheritance rule it depends on

`plugin/skills/deliverable-review/SKILL.md:31`

Phase 1 step 2 reads `<Base>` from §Provenance and ignores `Derived from:`. The
one failure D-80 exists to prevent — a second-pass artifact that recomputed its
base — passes every check the consumer makes: `git rev-parse` resolves, the
range is built, the diff is narrow, and the review reads clean. D-80's own
words for it: "a too-narrow diff reads as a clean review, so nothing surfaces
the error."

Enforcement is left entirely to the correctors, which run at write time only
and, per M-1 and M-2, cannot repair what they find. The consumer-side check is
one Read of the artifact named in `Derived from:` plus a string compare — this
review ran it by hand (see the Range line above) because the skill does not
ask for it.

### M-5 — The m-2 fix defers to a decision that does not exist

`plugin/skills/design/references/route-to-execution.md:58-60`,
`plugin/skills/design/references/write-outline.md:181-187`

The node closes with "the gate decides what a not-routable sub-problem does to
the outline". The Multi-Sub-Problem Sufficiency Gate carries no such branch:
its `**If sufficient**` block (`:181-185`) sends the agent to the node, and its
`**If insufficient**` branch (`:187`) is evaluated before `:185` is ever
reached. A sub-problem recorded not-routable therefore has nowhere to go.

Already tracked as observation A in `reports/review-skills.md` and deferred by
decision to a `/design` pass. Recorded here because the m-2 deliverable is
incomplete without it, not as new information.

### M-6 — The B/C fix is site-granular where the defect is target-granular

`plugin/skills/build/SKILL.md:122`, `plugin/skills/design/SKILL.md:133`

`reports/review-skills.md` observation E states that no "per"-form pointers
remain, scoped to the six files in Scope. A whole-tree grep over `plugin/`
classifies every hit and leaves five stale, two of them pointing at the same
target C just fixed:

| Site | Target | Verdict |
|---|---|---|
| `plugin/skills/build/references/tdd-slice.md:4` | `dispatch-composition.md` | **stale** — same target as C |
| `plugin/fragments/delegation.md:33` | `dispatch-composition.md` | **stale** — same target as C |
| `plugin/skills/runbook/SKILL.md:78` | `references/runbook-format.md` | **stale** — identical form to B |
| `plugin/skills/review/SKILL.md:207` | `plugin/fragments/review-requirement.md` | **stale** |
| `plugin/skills/build/references/review-dispatch-template.md:77` | `docs/design.md` §6.4 D-26 | **stale, lower cost** — a citation rather than a must-open node; target resolves, D-26 is in §6.4 |
| `plugin/agents/refactor.md:59` | "per the prompt" | **accurate** — not a file pointer, no edit |

All five sites are outside the review range and outside both outlines' scope,
so this is not a missing deliverable. It is the M-3 pattern of the first pass
repeating one level out: an exit condition scoped to the files under edit
reports clean while the defect form persists in the files it did not look at —
the failure `memory/ddaanet/reference-audit-after-a-move.md` describes, and
the site-granular-closure failure `inbox/brief-review-feeds-back-into-design.md`
names as its third.

## Minor Findings

**Clarity**

1. `plugin/skills/design/references/research-protocol.md:41` — "Write the
   Provenance heading and its two fields **as shown**" points at a block whose
   `Derived from:` value is `none`, the first-pass case. Read literally it
   tells a second-pass author to copy `none`. `:22` routes through the rule
   first, so the risk is bounded; scoping the clause to the heading and the
   field labels would close it.

2. `plugin/skills/design/SKILL.md:174` — "(B gate or C.5)" is singular where
   `:19` now says "both of `references/write-outline.md`'s sufficiency gates".
   Observation D of `reports/review-skills.md`; the same defect class as P-2 at
   a second site in the same file.

3. `plugin/skills/design/references/route-to-execution.md:30` — the final
   `ELSE` is annotated "(work type = Production AND behavioral code)" but is an
   unconditional catch-all. Work that is neither all-prose nor
   Investigation/Exploration nor behavioral code lands there, and the
   annotation misdescribes what routed it.

**Accuracy**

4. `docs/changelog.md:29-31` — "preconditions, which bind every branch
   including prose" is wider than what shipped. M-4 of the first pass narrowed
   it to the branches the node routes, and that correction landed on
   2026-09-17, the date the entry carries. The file's contract is a write-time
   record, so this is defensible; a reader meets the wider claim with nothing
   dated after it.

**Line counts**

5. `plugin/agents/outline-corrector.md` is 396 lines with 28 lines over 80
   columns; `design-corrector.md` is 398 with 48 over. Dividing each file's
   character count by 80 puts them at 435 and 456 lines respectively, so both
   read as under the 400 cap only because no hard-wrapping formatter is wired
   into the validation gate. This pass added 9 and 18 lines to them.
   `build/SKILL.md` is 222 against the ~200 hub guideline, unchanged by this
   pass.

## Gap Analysis

| Finding | Site | Status |
|---|---|---|
| M-1 (example form) | `research-protocol.md:29-33` | covered — `## Provenance` heading and two bold bullets, matching `design-content-rules.md:100-106`; see minor 1 |
| M-2 (imperative pointers) | `research-protocol.md:22`, `design/SKILL.md:133`, `:139` | covered — three imperative Reads; rule not inlined; hub still 175 lines |
| M-3 (sweep) | `build/SKILL.md:5`, `:35` | covered — whole-tree case-insensitive re-sweep run for this review leaves only `runbook-corrector.md:112` and `build/SKILL.md:110`, both classified accurate and both named OUT |
| M-4 (narrow the claim) | `route-to-execution.md:14-16` | covered — grep confirms exactly three readers, all Phase B/C; but see M-3 above on the `/runbook` branch |
| m-1 (`and` → `or`) | `deliverable-review/SKILL.md:31`, `docs/design.md:549` | covered — both sites |
| m-2 (scope the failure action) | `route-to-execution.md:56-60` | covered — but see M-5 |
| m-3 ("execution-ready") | subsumed into M-3 | covered |
| P-1 (`write-outline.md:185`) | `write-outline.md:185` | covered — "Read … and route by it, per sub-problem", matching `:204` and `write-design.md:70` |
| P-2 (caller count) | `design/SKILL.md:19` | covered — three callers, matching the grep and `docs/design.md:617-618`; see minor 2 |
| B (`design/SKILL.md:133`) | `design/SKILL.md:133` | covered — authorised extension, declared in `8828f63a`; see M-6 |
| C (`build/SKILL.md:122`) | `build/SKILL.md:122` | covered — authorised extension, declared in `8828f63a`; see M-6 |

**Cross-cutting checks.** Decision ids in `docs/design.md` run D-1..D-81 with
no duplicate; the first pass's D-79 collision is resolved and D-37's citation
repoints to D-81. Every `route-to-execution.md` inbound reference resolves, and
the three call sites match the two enumerations that count them
(`design/SKILL.md:19`, `docs/design.md:617-618`). The `C.5` label survives the
heading rename, so `write-design.md:53`, `design/SKILL.md:19`, `:174`,
`docs/design.md:618` and `docs/changelog.md:17` all still resolve. No `§
Continuation` reference remains anywhere in `plugin/` or `docs/`. Every new
pointer target exists on disk. The four Provenance-writing routes — Phase 0
Simple/Moderate-prose, Moderate non-prose, Complex outline, Complex design —
each reach a Provenance instruction; the Defect route produces no design
artifact.

**Excess (unspecified, all justified and traceable):**

- `plugin/skills/build/SKILL.md` +3, `references/phase-boundary.md` +2
  (`a533a842`) — the unsandboxed `verify-step.sh` note. Unrelated to either
  job, landed inside the range. The residual D-80 predicts and accepts.
- `docs/design.md` "Verified against: `f50ed025`" deleted, `design-corrector.md`
  §4.5 criteria table dropped, its `color` and `description` fixed
  (`34fafe63`) — settlements of the first pass's agent-review findings,
  recorded in the commit body.
- `plugin/skills/build/SKILL.md:122`, `plugin/skills/design/SKILL.md:133`
  (`8828f63a`) — observations B and C, applied past the outline's Scope on my
  human partner's instruction. The commit body declares them as an authorised
  extension and names the defect class; not undeclared deliverables.
- `inbox/*.md` (+91) — arrivals from other repos, not either job's output.

## Summary

**0 critical, 6 major, 5 minor.**

The nine findings the outline set out to work all land at their named sites,
and B and C land as declared. The sweep this pass was partly about now holds:
a fresh whole-tree case-insensitive re-sweep for the retired name leaves two
hits, both classified accurate and both already named OUT.

The majors cluster in two places. Three of them (M-1, M-2, M-4) are on the
Provenance contract's enforcement rather than its specification: the correctors
destroy a good field while repairing a bad one, are barred from the one repair
that is safe, and the consumer never checks the inheritance rule at all — so
the silent failure mode the contract was built to close is still open on every
side except the author's own discipline. None was reachable from either
outline's finding list; they surface only by reading the contract's three
surfaces against each other.

M-6 is the first pass's M-3 one level out. Both build reviews and this pass's
outline scoped the "per X" sweep to the six files under edit, and five
same-class pointers survive in files nobody looked at, two of them aimed at the
same target C just fixed. That is now the third consecutive pass where a sweep
scoped to the diff reported clean while the defect form persisted outside it —
after P-1 and P-2, which the deliverable review missed, and B and C, which the
skill review found only by grepping for the form. It is the strongest evidence
yet for the sweep mechanism M-3 descoped.

M-3 and M-5 are gaps left by the two fixes that changed routing text: one
precondition binds a branch its own rationale does not cover, and one deferral
points at a decision that has not been written.

On dogfooding, the contract's consumer side worked: the range came out of the
artifact with no user round-trip, the inherited base matched the superseded
artifact verbatim, and `plans/` exclusion kept both outlines' own commits out
of the diff.
