# Review: skill definitions — provenance-reach-and-sweep

Reviewer: `plugin-dev:skill-reviewer` (fable), report-only. Findings returned
in three parts and written here by the dispatching session, which applied the
fixes. Baseline `a2a93ffd7bc66ba3d838dad8f1254524b8154b38`.

Group: the six `plugin/` files. `docs/design.md` reviewed separately
(`review-docs.md`).

## Verdict

All nine findings carry their settled fix at the named site; no fix deviates
from what the outline settled; no edit beyond scope. No critical, no major, no
blocker. Two minor issues on the added text, four out-of-scope observations.

## Per-finding check

| # | Site | Verdict |
|---|---|---|
| M-1 | `research-protocol.md:29-33` | PASS — example opens with `## Provenance` and the two bulleted bold fields, matching `design-content-rules.md:101-106` and what both correctors match on (`outline-corrector.md:113`, `design-corrector.md:171`); the rest stays compressed; no consumer named |
| M-2 | `research-protocol.md:22`, `design/SKILL.md:133`, `:139` | PASS — three imperative Reads of `design-content-rules.md` §Provenance Section; rule not inlined; both hub lines stay single lines, hub still 175 |
| M-3 / m-3 | `build/SKILL.md:5`, `:35` | PASS — "execution-ready" dropped at both, nothing replaces it, §1 item 2 still states the condition operationally. Whole-tree case-insensitive grep over `plugin/` and `docs/design.md` leaves only `runbook-corrector.md:112` (classified accurate, OUT) |
| M-4 | `route-to-execution.md:14-16` | PASS — claim narrowed to the branches the node routes, gap named. The node's readers are `write-outline.md:185`, `:204`, `write-design.md:70`, all Phase B/C, so the narrowed claim is true |
| m-1 | `deliverable-review/SKILL.md:31` | PASS — `or`, matching `docs/design.md:549` |
| m-2 | `route-to-execution.md:56-60` | PASS — per-sub-problem outcome records the route or the failed precondition as not-routable, names no command, resumes neither A.5 nor C.1 |
| P-1 | `write-outline.md:185` | PASS — "Read … and route by it, per sub-problem", matching `:204` and `write-design.md:70`; the residual "per sub-problem" is distributive, not a pointer |
| P-2 | `design/SKILL.md:19` | PASS — three callers, matching the three actual call sites and the wording at `docs/design.md:617-618` |

**Scope completeness.** Every Region 1-6 has its edit; the diff touches exactly
the six files and only the named sites. Nothing under OUT was touched —
`runbook-corrector.md:112`, Phase 0 branches, `build/SKILL.md` §4.1 and both
correctors are unedited.

**Cross-skill consistency.** `design/SKILL.md:19` and `:130` agree with
`build/SKILL.md` §1 items 1-2 on what `/build` takes. The caller enumeration at
`:19` matches `grep -rn route-to-execution plugin/`.

**Description shape** (`build/SKILL.md:3-7`): still opens with what the skill
does, then triggers. No trigger term lost — `/build`, "execute the runbook",
"execute this plan", `/design`, `/runbook`, `design`, `outline`, `runbook` all
survive. Folded scalar, so the shortened line changes nothing in the injected
string.

**Directive quality of added text.** No added sentence names a consuming system
or states rationale. The M-4 sentence states reach, not mechanism. The m-2
closing sentence carries one reassurance clause, within the rule. Only minor 1
applied.

## Minor issues — both resolved

1. **`research-protocol.md:41-42`** — the clause marking Provenance as the
   exception opened with a meta-description of the constraint
   (`craft:directive-writing`'s third cut) and carried the act only in its
   second half. **Fixed:** now "Write the Provenance heading and its two fields
   as shown; adapt the rest." The exception survives by contrast with the
   "adapt to task" caption at `:28`, without being named.
2. **`route-to-execution.md:58-60`** — "the gate decides what a not-routable
   sub-problem does to the outline" points at a decision with no text. The
   reviewer's judgement, accepted: the clause is the one reassurance
   directive-writing permits, it prevents an invented resume-to-A.5 recovery,
   and the node is correct as settled. **No change** — the gap is in the gate,
   carried as observation A.

## Line counts

`build/SKILL.md` 222, over the ~200 hub guideline — pre-existing, the baseline
was also 222 and this pass added no lines. `design/SKILL.md` 175,
`deliverable-review/SKILL.md` 143. References: `research-protocol.md` 43,
`route-to-execution.md` 60, `write-outline.md` 208, all under 400.

## Out-of-scope observations

Held back on first pass — the outline's Scope is the contract, and an edit it
does not name reads as an undeclared deliverable to the next
deliverable-review. **B and C were then applied on my human partner's
instruction**, in a follow-up commit that names them as an authorised scope
extension. A and D remain open.

- **A. `write-outline.md:170-187`'s multi-sub-problem gate has no not-routable
  branch.** The m-2 fix defers to "the gate above", and that gate carries no
  such decision — its "If insufficient" branch at `:187` is evaluated before
  the node is read. `:185` also still says the readiness "names its route",
  which after m-2 can be not-routable instead. This is the design question m-2
  deferred; it needs my human partner's call, not a wording fix.
- **B. `design/SKILL.md:133`** — "**Generate** … per `references/write-outline.md`",
  the surviving "per X" pointer on the very line M-2 fixed. The agent must open
  that node for the outline format; Phase 0 `:42-44` and Complex `:142` all say
  "Read". Same defect class as M-2, different target. **Applied:** the step now
  reads "Read `references/write-outline.md` for the outline format", line-neutral.
- **C. `build/SKILL.md:122`** — "One dispatch composed per
  `references/dispatch-composition.md`", a pointer that must be opened to
  compose any dispatch, in "per" form. No site says "Read"; `:214` only indexes
  it. **Applied:** "One dispatch: Read `references/dispatch-composition.md` and
  compose by it", line-neutral.
- **D. `design/SKILL.md:174`** — "(B gate or C.5)", singular where `:19` now
  says both of `write-outline.md`'s gates. Readable as the Phase B gate
  collectively, and the outline judged `:174` needs no edit for M-4 — it did not
  consider it for P-2.

B, C and D are what a form-grep finds where a name-grep cannot reach, which is
the pairing `memory/ddaanet/reference-audit-after-a-move.md` prescribes and the
outline's Risks section names as the evidence for the descoped sweep mechanism.

**E.** No other "per"-form pointers remain in the six files: a
`grep -n -E "\bper (\`|references|§|the |\*\*)"` sweep hits only B and C, the
rest being distributive uses ("per sub-problem", "per-file").

## Recall applied

`reference-audit-after-a-move.md` — whole-tree grep for the M-3 symbol run,
every hit classified, exit condition met. `instruction-names-absent-data.md` —
every new pointer's target verified to exist (`design-content-rules.md:98`
§Provenance Section, `route-to-execution.md`, `write-outline.md`,
`write-design.md:70`). `feedback-decision-docs-are-living.md` — bears on
`docs/design.md`, reviewed separately.

## Blockers

None.
