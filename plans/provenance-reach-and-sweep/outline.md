# Outline: provenance reach, and the sweep the sweep missed

Second pass on `design-routing-and-provenance`, working its deliverable
review's 4 major and 3 minor findings. Agentic prose throughout — no
behavioral code.

## Provenance

- **Derived from:**
  `plans/design-routing-and-provenance/reports/deliverable-review.md`,
  superseding `plans/design-routing-and-provenance/outline.md`
- **Base:** `926e372d02a0366202b2bb6a684551128d1f2a66` — copied verbatim from
  the superseded outline, **not** recomputed.

*(First real exercise of D-80's inheritance rule. A recomputed base would have
started this job's review after the first pass's work, so the second review
would have seen these fixes instead of the deliverable they repair.)*

## Requirements

The review report is the requirement. Each finding names its file, its line and
the defect; five of seven named their own fix, and M-1 and M-4 each offered
two.

| # | Finding | Settled as |
|---|---|---|
| M-1 | `research-protocol.md:30`'s example renders Provenance in a form both correctors reject | fix the example |
| M-2 | The inheritance rule sits behind a non-imperative "per" pointer on all three outline-producing paths | make the three pointers imperative |
| M-3 | Item A's whole-tree exit condition was unmet and reported met; three hits unclassified | classify all three, fix the two stale ones |
| M-4 | `route-to-execution.md` claims its preconditions bind "every branch" but is unreachable from the Phase 0 prose routes | **narrow the claim** |
| m-1 | Two independent fallback triggers joined by `and` in two places | `or` |
| m-2 | The precondition-failure action is unscoped for the multi-sub-problem caller | scope it |
| m-3 | "execution-ready" survives in `/build`'s description and §1 | subsumed into M-3 |

**Found during `/proof`, not in the report.** Its whole-tree verification of
the M-4 and M-3 claims turned up two further defects of the same class, both
in scope:

| # | Finding | Settled as |
|---|---|---|
| P-1 | `write-outline.md:185` points at `route-to-execution.md` with "per", the non-imperative form M-2 removes, on the very caller m-2 scopes | imperative Read, matching its two sibling sites |
| P-2 | `design/SKILL.md:19` enumerates the node's callers as two; there are three | name both `write-outline.md` gates |

So the next deliverable-review checks coverage against seven report findings
plus these two.

**Decisions taken before this outline** (my human partner, this session):

- **M-4 → narrow the claim, not extend the check.** Giving the Phase 0 Simple /
  Moderate-agentic-prose route a named-edit-targets precondition is a separate
  decision about Phase 0's weight, and Phase 0 has never carried one. What
  ships is an honest description of what the node actually governs.
- **M-3's process half is out.** The three hits get fixed and classified;
  nothing is built to stop a future sweep reporting clean while under-covering.
  The mechanism for that is not obvious and would be invented rather than
  grounded. Recorded under Risks with the recall entry that bears on it.
- **`inbox/brief-review-feeds-back-into-design.md` stays out.** It proposes
  three changes to the deliverable-review *report contract* — co-location
  grouping, per-reviewer counts, site lists on multi-site findings. That is a
  design question, not a fix to this pass's findings, and folding it in roughly
  doubles the scope. Its recommendation is that agent's input, not a decision.

## Scope

**IN** — six edit regions. Ordered by region rather than by severity: two of
the six carry findings from both tiers, and working the severity sort would
re-enter the same paragraph twice.

- `plugin/skills/design/references/research-protocol.md` — `:22` (M-2) and the
  example block at `:28-35` (M-1)
- `plugin/skills/design/SKILL.md` — `:133`, `:139` (M-2) and `:19` (P-2).
  Line-neutral rewordings; the hub is 175 lines against the ~200 guideline
- `plugin/skills/design/references/route-to-execution.md` — `:14` (M-4) and
  `:51-55` (m-2)
- `plugin/skills/build/SKILL.md` — `:5` frontmatter description and `:35`
  (M-3, m-3)
- `plugin/skills/deliverable-review/SKILL.md:31` and `docs/design.md:549`
  (m-1) — the same defect in the skill and in the decision that specifies it
- `plugin/skills/design/references/write-outline.md` — `:185` (P-1)

**OUT**

- `plugin/agents/runbook-corrector.md:112` — **classified accurate, no edit.**
  "**Execution Readiness:**" there is a runbook-item review dimension, asking
  whether an item is executable as written; it has nothing to do with
  `/design`'s routing. The outline that shipped it named this hit as evidence
  for the case-insensitive grep and then never stated its verdict. The verdict
  is here, which is what M-3 asked for.
- `plugin/skills/design/SKILL.md` §Routing Phase 0 branches — untouched, per
  the M-4 decision.
- `docs/changelog.md` — **no new entry.** The 2026-09-17 entry already narrates
  this change; a fix pass correcting the wording of a contract landed the same
  day does not get a second dated entry. D-80's `and`/`or` defect is corrected
  in place, which is what a living design doc is for.
- Both correctors — their criteria already hold the spec these fixes reach.
  Verified, not assumed: `outline-corrector.md:112-118`,
  `design-corrector.md:169-177`.
- `plugin/skills/build/SKILL.md` §4.1 "Direct execution" — still accurate,
  still means inline rather than delegated dispatch, still out of every sweep.

## The changes

### Region 1 — `research-protocol.md`

**M-1.** The §A.5 example currently opens with
`Provenance: Derived from: none. Base: <full sha from git rev-parse HEAD>.` —
a flat line with no `## Provenance` heading, which is what both correctors
match on. The rest of the example is deliberately compressed (`Approach:`,
`Key decisions:`), and that stays; provenance becomes the one block shown
verbatim, followed by one imperative clause marking it as the exception — copy
this block verbatim, adapt the rest. No consumer is named: per
`craft:directive-writing`'s five cuts, which system keys on the heading is
mechanism the producer does nothing with.

**M-2.** `:22` reads "- Provenance -- two fields, per
`references/design-content-rules.md` §Provenance Section". "Two fields, per X"
is answerable without opening X. It becomes an imperative Read of that section.
The inheritance rule is **not** inlined here — one home for it is the point;
duplicating it across three producer sites rebuilds the drift Item A just
removed.

### Region 2 — `design/SKILL.md`

**M-2**, same defect at two sites, same fix: `:133` ("including a Provenance
section per …") and `:139` ("(provenance per …, scope, per-file changes, …)")
become imperative Reads of `references/design-content-rules.md` §Provenance
Section. Both stay on one line; the hub gains no lines.

**P-2.** `:19` describes the routing node as "reached from the Phase B
sufficiency gate and from Phase C.5" — two callers, where there are three:
`write-outline.md` has two gates. `docs/design.md:617-618` already states it
correctly ("both of `write-outline.md`'s sufficiency gates and
`write-design.md`'s C.5"), so the hub is the one surface that is wrong, and
the correct form is there to copy.

`:174`'s routing line already distinguishes Simple / Moderate-agentic-prose
from work routed by the node, so it is consistent with M-4's narrowing and
needs no edit.

### Region 3 — `route-to-execution.md`

**M-4.** `:14` "Both bind every branch, prose included." asserts a reach the
node does not have — it is read only from `write-outline.md:185`, `:204` and
`write-design.md:70`, all inside Phase B/C. The line narrows to the branches
this node routes, and then names the gap rather than leaving a reader to infer
universality: the Phase 0 Simple and Moderate-agentic-prose routes reach
`/build` without reading this node, so neither precondition binds them.

**m-2.** `:51-52`'s "resume from A.5 … or from C.1. Do not route." is written
for a single-artifact caller. Under the multi-sub-problem gate the node is read
per sub-problem, and one sub-problem cannot send the whole outline back to A.5
— that gate already owns its own insufficiency branch. The closing paragraph,
which already scopes the *route* case to that caller, extends to cover
precondition failure: the sub-problem is recorded not-routable in its readiness
summary, and the gate above decides what that does to the outline.

### Region 4 — `build/SKILL.md`

**M-3 / m-3.** Two hits, both **stale**: `:5` (frontmatter description, "or an
execution-ready design or outline that has no runbook") and `:35` (§1, item 2,
"execution-ready work with no runbook"). They name a verdict `/design` stopped
computing under that name when `route-to-execution.md` replaced it. §1 already
states the condition operationally — *has no runbook* — so the adjective is
dropped at both sites and nothing replaces it.

The description edit removes a word and adds none; `design`, `outline`,
`runbook` and `/build` all survive as trigger terms.

### Region 5 — `deliverable-review/SKILL.md` and `docs/design.md`

**m-1.** Both sites join two independent fallback triggers with `and`, so
neither fires on its own:

- `deliverable-review/SKILL.md:31` — "Ask the user for the range when the
  artifact carries no Provenance section, **and** when `git rev-parse
  <Base>^{commit}` does not resolve"
- `docs/design.md:549` — "asks the user for the range when the section is
  absent **and** when `<Base>` does not resolve to a commit"

`or` in both. This matters for the `TODO` placeholder the correctors write
into an unrepairable Provenance block: that path reaches the second trigger
only.

### Region 6 — `write-outline.md`

**P-1.** `:185` reads "Each sub-problem's readiness names its route per
`references/route-to-execution.md`; dispatch remains the caller's
responsibility". An agent cannot name a route without opening the node, so
"per X" is exactly the form M-2 removes — here on the pointer belonging to the
multi-sub-problem caller that Region 3's m-2 fix is written to serve. It
becomes an imperative Read, matching the node's two other call sites
(`:204` and `write-design.md:70`), which already say "Read … and route by it".

Same defect class as M-2, a different rule: this pointer targets the routing
node, not the inheritance rule.

## Key decisions

- **D — The inheritance rule keeps one home.** M-2 makes three pointers
  imperative rather than inlining the rule at each producer. *Accepted
  tradeoff:* an agent still has to follow a pointer to reach the rule that
  matters most, and the imperative form is the only thing making it do so.
  The same imperative-form fix applies to `write-outline.md:185`'s pointer at
  `route-to-execution.md` (P-1) — found during proof, same defect class, a
  different rule.
- **D — Narrow the node's claim rather than widen its reach (M-4).** *Accepted
  tradeoff:* the argument the first pass made for the precondition — with no
  runbook the artifact **is** the item list — remains unenforced on the route
  that produces the most runbook-less prose jobs. The gap is now written down
  where a reader of the node will meet it, which is the difference between an
  accepted gap and an undiscovered one.
- **D — Provenance is the one verbatim block in a compressed example (M-1).**
  *Accepted tradeoff:* the example block becomes visually inconsistent with
  itself, and the inconsistency has to be marked with one imperative clause,
  which is a line the compressed form does not need.
- **D — D-80 is corrected in place, with no changelog entry.** Per
  `memory/feedback-decision-docs-are-living.md` the design doc is current
  truth; the `and`/`or` defect is a defect in the decision's text, not a new
  decision. *Accepted tradeoff:* the git history is the only record that D-80
  ever said `and`.

## Risks and open questions

**Open questions:** none. Both forks (M-1, M-4) were settled before this
outline was written.

**Risks:**

- **The sweep mechanism is untouched.** M-3's finding was that an exit
  condition requiring every hit classified was reported satisfied and was not.
  This job fixes the three hits and leaves the mechanism alone, by decision.
  `memory/ddaanet/reference-audit-after-a-move.md` closes with the lead a
  future pass would follow — *prefer a check phrased as "produce the right
  answer" over "judge this answer"* — and notes that the fixer caught all three
  misses where two reviewers did not, because writing a correction forces
  naming the symbol's real home. Recorded, not acted on. This pass's own
  `/proof` then found two further reach defects the deliverable-review missed
  — P-1 and P-2 — which is the same under-coverage one pass later, and the
  strongest evidence yet for the mechanism this decision descopes.
- **M-2's fix is a wording change against a habit.** "Read X" versus "per X" is
  a one-word difference in the artifact and a whole behaviour in the agent, and
  no linter distinguishes them. The rule itself is written down —
  `craft:directive-writing` requires imperative wording in directive channels —
  and `write-design.md:13` is the site the review found clean, so the gap is
  enforcement, not grounding.
- **This outline is its own second test of the contract.** If `Base:` here is
  wrong, the review that checks this job inherits the error silently — a
  too-narrow diff reads as a clean review. It is copied from
  `plans/design-routing-and-provenance/outline.md`, which a `git rev-parse
  926e372d02a0366202b2bb6a684551128d1f2a66^{commit}` confirms resolves.

## Next steps

Load `craft:directive-writing` (M-2's imperative-form rule) and
`plugin-craft:skill-authoring` (the `build/SKILL.md:5` description edit) before
executing. Six regions, no ordering dependency between them — prose edits
commute.

**Session restart required before `/build`.** The `/edify:design` body loaded
in this session is the pre-change version: it reads "execution-ready (B gate or
C.5)" at §Routing out and carries no Provenance clause at `:133`. The on-disk
file has the shipped text. Any skill body this job edits has the same exposure;
the reference files it edits do not, since those are Read at runtime. Load
`plugin-craft:verifying-plugin-changes` and confirm the loaded bodies match the
repo before trusting any verification of these edits.
