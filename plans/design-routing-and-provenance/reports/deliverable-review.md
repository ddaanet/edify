# Deliverable Review: design-routing-and-provenance

**Date:** 2026-09-17
**Methodology:** `docs/design.md` §6.8 "Deliverable review"
**Design artifact:** `plans/design-routing-and-provenance/outline.md` (no `design.md`)
**Range:** `926e372d02a0366202b2bb6a684551128d1f2a66..HEAD`, read from the outline's §Provenance — the first artifact written under the contract this job introduces
**Layer 1:** skipped — 297 added / 94 removed lines, under the 500-line gate. Layer 2 was a full review, per-file axes and cross-cutting.

## Inventory

| Type | File | +/- | In scope |
|---|---|---|---|
| Agentic prose | `plugin/skills/design/references/route-to-execution.md` (new) | +55 | yes |
| Agentic prose | `plugin/skills/design/references/write-outline.md` | +3/-27 | yes |
| Agentic prose | `plugin/skills/design/references/write-design.md` | +5/-24 | yes |
| Agentic prose | `plugin/skills/design/references/design-content-rules.md` | +21/-2 | yes |
| Agentic prose | `plugin/skills/design/references/research-protocol.md` | +2 | yes |
| Agentic prose | `plugin/skills/design/SKILL.md` | +5/-5 | yes |
| Agentic prose | `plugin/skills/deliverable-review/SKILL.md` | +4/-4 | yes |
| Agentic prose | `plugin/agents/outline-corrector.md` | +9/-1 | yes |
| Agentic prose | `plugin/agents/design-corrector.md` | +18/-14 | partly — see Excess |
| Human docs | `docs/design.md` | +43/-17 | partly — see Excess |
| Human docs | `docs/changelog.md` | +36 | yes |
| Agentic prose | `plugin/skills/build/SKILL.md` | +3 | no — unrelated |
| Agentic prose | `plugin/skills/build/references/phase-boundary.md` | +2 | no — unrelated |
| Human docs | `inbox/brief-review-feeds-back-into-design.md` | +81 | no — arrival |
| Human docs | `inbox/recall-skill.md` | +10 | no — arrival |

No code, tests or configuration in the range. Agentic prose throughout, as the outline promised.

**Conformance:** every IN-scope item produced. No missing deliverables.

## Critical Findings

None.

## Major Findings

### M-1 — The one worked example of a Provenance section is in a form both correctors reject

`plugin/skills/design/references/research-protocol.md:30`

The §A.5 example outline renders provenance as a flat inline line:

```
Provenance: Derived from: none. Base: <full sha from git rev-parse HEAD>.
```

The contract (`design-content-rules.md:100-107`) specifies a `## Provenance` heading with two bold-labelled bullets, and both correctors match on that heading: "A `## Provenance` section is present" (`outline-corrector.md:113`), "Every `/design` artifact carries a `## Provenance` section" (`design-corrector.md:171`). An outline written to the example has no such heading and is flagged **Major** by the corrector that reviews it — on a path where the example is the only concrete rendering the agent sees.

The rest of that example is flat by design (`Approach:`, `Key decisions:`), so the style is consistent within the block; provenance is the one field with a downstream consumer and a heading-matched check. Either the example carries the block form, or it says explicitly that provenance is the exception to the block's compression.

**Impact:** the first-pass failure mode is loud (corrector flags it), so this costs a revise cycle rather than a wrong review range. It is the shape of the outline's own stated risk — "Provenance goes unwritten … correctors as the only enforcement, which catches it after the artifact is written".

### M-2 — The inheritance rule is behind a non-imperative pointer on every outline-producing path

`plugin/skills/design/SKILL.md:133`, `:144`; `plugin/skills/design/references/research-protocol.md:22`

The rule the outline calls "the whole point" — *a second-pass artifact copies `Base:` verbatim and never recomputes it* — exists in exactly one place a producer can read: `design-content-rules.md:110`. The `design.md` path reaches it imperatively (`write-design.md:13`: "**Content rules:** Read `references/design-content-rules.md` …"). All three outline-producing paths reach it only as "**per** `references/design-content-rules.md` §Provenance Section":

- `SKILL.md:133` — Simple / Moderate agentic-prose: "including a Provenance section per …"
- `SKILL.md:144` — Moderate non-prose: "(provenance per …, scope, per-file changes, …)"
- `research-protocol.md:22` — Complex Phase A.5: "- Provenance -- two fields, per …"

"Two fields, per X" is answerable without opening X, and an agent that answers it without opening X has `git rev-parse HEAD` as the only base it knows how to produce. That is the recomputation, on a second pass, with the failure mode the design doc itself names: "a fresh `HEAD` would start the range after the first pass's work and the second review would see the fixes instead of the deliverable". Silent — a too-narrow diff reads as a clean review.

`write-design.md:13`'s "Read …" is the form that works; the three outline sites should match it.

**Impact:** highest on the Simple / Moderate-agentic-prose route, which is where second passes land — a deliverable-review finding routes back to `/design` and that route produces only an outline.

### M-3 — Item A's exit condition is unmet, and the report asserts it is met

`plans/design-routing-and-provenance/reports/review-skills.md:105-107`

The outline's exit condition: "a whole-tree grep with **every** hit classified accurate or stale and the classification stated per hit." `review-skills.md` claims the sweep "leaves only hits the outline classifies accurate." Three live case-insensitive `execution.read` hits are classified nowhere — not in the outline, not in any of the four reports:

- `plugin/skills/build/SKILL.md:5` — frontmatter description, "or an execution-ready design or outline that has no runbook"
- `plugin/skills/build/SKILL.md:35` — §1, "execution-ready work with no runbook"
- `plugin/agents/runbook-corrector.md:112` — "**Execution Readiness:**"

The last is named in the outline's own list of the five hits the case-insensitive form finds, as evidence for using `-i` — and then never classified. `review-docs.md`'s sweep was scoped to `docs/` and says so; `review-skills.md`'s claims whole-tree coverage and does not have it.

On the merits: `runbook-corrector.md:112` is **accurate** (runbook item executability, unrelated to `/design` routing). `build/SKILL.md:5`/`:35` are **stale** — they name a verdict `/design` no longer computes under that name. The cost is low (trigger text and a fallback label, no broken routing), but the audit was the one mechanism standing between this job and a repeat of the residue it exists to remove, and it reported clean while under-covering.

### M-4 — "Both preconditions bind every branch" is false on the two highest-volume prose routes

`plugin/skills/design/SKILL.md:130-136`, `:137-143` vs `plugin/skills/design/references/route-to-execution.md:11-19`

`route-to-execution.md` states its preconditions as binding "every branch, prose included", and the outline's D — *Preconditions bind the prose path too* — argues named edit targets are what the prose path needs most: "with no runbook the artifact **is** the item list, and a prose job that names no targets gives `/build` nothing to walk."

The node is read from three sites, all inside Phase B/C (`write-outline.md:185`, `:204`, `write-design.md:70`). The Phase 0 fast routes never reach it: Simple and Moderate-agentic-prose go outline → proof → commit → `/build` with no runbook and no precondition check (`SKILL.md:130-136`). So the route that produces the most runbook-less prose jobs is the one where "edit targets are named" is unchecked.

This is consistent with D-35 as reworded ("Phase 0 … fixes the route for Simple and Moderate work"), so it is not a regression — the Phase 0 routes never checked. But the node now asserts universality it does not have, and the argument for the precondition is strongest exactly where it is absent. Either the node's claim narrows to its callers, or the two Phase 0 prose routes gain the precondition check.

## Minor Findings

**Clarity**

1. `plugin/skills/deliverable-review/SKILL.md:31` and `docs/design.md:548-549` — "Ask the user for the range when the artifact carries no Provenance section, **and** when `git rev-parse <Base>^{commit}` does not resolve." Two independent triggers joined by "and"; read as a conjunction, neither fires alone. "or" in both sites.

2. `plugin/skills/design/references/route-to-execution.md:52-53` — "A precondition failed — name it, then resume from A.5 … or from C.1. Do not route." The node is also read per sub-problem from the multi-sub-problem gate (`write-outline.md:185`), where the gate above it already owns the insufficiency branch and one sub-problem cannot send the whole outline back to A.5. The node's last line scopes the *route* case to that caller; the precondition-failure case is left unscoped.

**Terminology**

3. `plugin/skills/build/SKILL.md:5`, `:35` — "execution-ready" (see M-3). `/build` §1 already describes the condition operationally ("design or outline that has no runbook"); the adjective adds nothing and points at a retired `/design` verdict.

## Gap Analysis

| Outline IN-scope item | Status |
|---|---|
| `write-outline.md` routing block `:206-228` → pointer | covered — `:204` |
| `write-outline.md:185` §Continuation dangling ref | covered |
| `write-design.md` §C.5 `:70-89` → pointer | covered — heading also reworded off "readiness" (deviation, flagged by `review-skills.md` item 10) |
| `route-to-execution.md` new shared node | covered — 55 lines |
| `design-content-rules.md` §Provenance + §References rewording | covered — `:97-113` |
| `research-protocol.md` §A.5 content list | covered — but see M-1 |
| `design/SKILL.md:19`, `:174-175` | covered |
| `design/SKILL.md:42-43` resume branches | **not changed — correct.** Both gate headings survive unrenamed at `write-outline.md:165`, `:191`, so the references still resolve |
| `design/SKILL.md:133`, `:144` Provenance in step lists | covered — but see M-2 |
| `outline-corrector.md`, `design-corrector.md` criteria | covered — made unconditional rather than conditional, deviation recorded and justified (`review-agents.md` F5) |
| `deliverable-review/SKILL.md:23`, `:31` | covered — `:31` also closed `review-agents.md` F4 |
| `docs/design.md` D-35, L-2, D-55, new D-80 | covered; `D-79` renumbered to `D-81` with both inbound references updated |
| `docs/changelog.md` dated entry | covered |

**Excess (unspecified, all justified and traceable):**

- `plugin/skills/build/SKILL.md` +3, `references/phase-boundary.md` +2 (`a533a842`) — the unsandboxed `verify-step.sh` note. Unrelated to this job; landed inside the range. Exactly the residual the outline predicted and accepted.
- `docs/design.md` "Verified against: `f50ed025`" deleted, `design-corrector.md` §4.5 criteria table dropped, its `color` and `description` fixed (`34fafe63`) — settlements of `review-agents.md` F1/F2/F3 and `review-docs.md`'s reported-not-fixed item. Recorded in the commit body.
- `inbox/*.md` (+91) — arrivals from other repos, not this job's output.

## Summary

**0 critical, 4 major, 3 minor.**

The two mechanisms land. `route-to-execution.md` states the routing decision once, resolves all three drifts the outline identified, drops the false single-session criterion, and every inbound reference resolves. The Provenance contract is specified, consumed and enforced, with the correctors correctly barred from supplying a base — a hazard the delegated review caught and closed.

The majors cluster on one seam: the contract is well specified at its definition site and thinly reached from the outline-producing paths (M-1, M-2), which is where second passes — the case the whole mechanism exists for — actually land. M-3 is about the audit rather than the artifacts: the exit condition Item A set for itself was reported met and was not. M-4 is a claim wider than its enforcement.

This run was also the contract's first dogfooding, and on that the evidence is positive: the range came out of the artifact with no user round-trip, and `plans/` exclusion kept the outline's own commit out of the diff as designed.
