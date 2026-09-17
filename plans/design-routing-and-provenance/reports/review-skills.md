# Skill Definition Review: design-routing-and-provenance

**Reviewer:** `plugin-dev:skill-reviewer` (opus, report-only — no Write/Edit/Bash)
**Baseline:** `a533a842573459032e7816271b3b55849fe37890`
**Date:** 2026-09-17
**Mode:** report-only; findings transcribed and fixes applied by the calling `/build` session

## Group

- `plugin/skills/design/SKILL.md`
- `plugin/skills/design/references/route-to-execution.md` (new)
- `plugin/skills/design/references/write-outline.md`
- `plugin/skills/design/references/write-design.md`
- `plugin/skills/design/references/design-content-rules.md`
- `plugin/skills/design/references/research-protocol.md`
- `plugin/skills/deliverable-review/SKILL.md`

## Item A verdict

Implemented as designed. All three documented drifts resolved correctly:
`write-design.md`'s "Cross-file coordination requiring sequencing" wording won
(`route-to-execution.md:44`); the "hard gate — file count irrelevant" qualifier
survived (`:32`); the substantive disagreement is settled in `write-design.md`'s
favour with the reasoning stated ("Both bind every branch, prose included",
`:14`). The false single-session-capacity criterion and the Exploration branch's
`AND design resolved all questions` conjunct are gone. Both call sites
(`write-outline.md:204`, `write-design.md:70`) are one-line pointers; the
sufficiency criteria, `**If insufficient**` branch and `**When to apply:**` all
stayed. `write-outline.md:185`'s dangling `§Continuation` reference is
repointed.

## Major findings

1. **`design-content-rules.md` §Structure Guidance omits Provenance** —
   `:60-69` is the section list a `design.md` author works from. `## Provenance
   Section` was added at `:97` but never entered the list, so the `design.md`
   path has a spec with no instruction to emit it. Fix: add
   `- Provenance (see below)` as the list's first item, mirroring the
   `References (see below)` pattern.

2. **The Simple / Moderate-agentic-prose route never names Provenance** —
   `design/SKILL.md:133` still reads "**Generate** `plans/<job>/outline.md` per
   `references/write-outline.md`". §Scope named both `:133` and `:139` as Item B
   deliverables; only the non-prose one was edited. The reachable chain
   (`write-outline.md` → `:103` → `research-protocol.md` §A.5) is two hops
   through Complex-job ceremony this route does not run, and
   `write-outline.md:105`'s own content list contradicts it. This is the route
   R1's second clause and `deliverable-review`'s `else outline.md` fallback
   exist to serve. Fix: extend `:133` the way `:139` was extended.

3. **Two outline content lists still enumerate the pre-Provenance set** —
   `write-outline.md:105` ("approach, key decisions, open questions, scope
   boundaries") is the line a Phase A reader acts on; `research-protocol.md`
   §A.5 is only a pointer two lines above. And `research-protocol.md:28-34`'s
   "Example outline" block contradicts the Content list directly above it — an
   agent copying the example emits no Provenance. Fix: add Provenance to both.

4. **The `Base:` rule is stated descriptively, not as an act** —
   `design-content-rules.md:109` says what artifacts *do* ("takes", "copies"),
   leaving the reader to infer two commands. Fix: state them as acts.

5. **Precondition failure has no act** — `route-to-execution.md:14-15` says a
   failure "sends the work back to design", but §Terminal action (`:47-51`)
   enumerates only `/build` and `/runbook`. A reader whose artifact fails a
   precondition has nothing to do. Fix: add a precondition-failure terminal
   bullet naming where to resume.

## Minor findings

6. **§Terminal action does not cover its third caller** —
   `write-outline.md:185` (multi-sub-problem gate) reads the node per
   sub-problem while keeping dispatch with the caller, but the node's terminal
   actions unconditionally say "commit the artefact, then name `/build
   plans/<job>` … and stop".

7. **`write-design.md:13` under-reports its own node** — the inbound pointer
   enumerates `design-content-rules.md`'s contents and omits Provenance. It is
   the only inbound reference to that file.

8. **`artefact` / `artifact` split inside changed text** —
   `route-to-execution.md` (six) and `design-content-rules.md:3` (one) are the
   only "artefact" users in `plugin/`; `design-content-rules.md:99,104,108`
   uses "artifact" three lines below its own "artefact".

9. **`deliverable-review/SKILL.md:48` still says "design In-scope items"** —
   inconsistent with `:23` and `:30`, both widened to "design artifact".

## Observation

10. **Scope deviation in `write-design.md`, already flagged by the
    implementer** — §Scope said the C.5 heading and `:66`/`:68` "stay"; the
    implementation renamed the heading and reworded both lines off
    "execution-readiness". Coherent with Item A §3's stale-name finding, `C.5`
    retained so `write-design.md:53` still resolves. No change recommended;
    needs my human partner's confirmation.

## Cross-reference integrity: clean

Every named path resolves: `references/route-to-execution.md` from
`design/SKILL.md:19`, `:174`, `write-outline.md:185`, `:204`,
`write-design.md:70`; `references/design-content-rules.md` §Provenance Section
from `design/SKILL.md:139` and `research-protocol.md:22`, target heading at
`design-content-rules.md:97`. The two headings named from `design/SKILL.md:42-43`
exist unchanged at `write-outline.md:165` and `:191`. `/build` §1 does take
whichever artifact exists with no path back to `/runbook`, so
`route-to-execution.md:8-10`'s justification holds. No `§Continuation` reference
remains anywhere. The case-insensitive sweep for
`execution.read|direct.execution|C\.5|§ *Continuation` over `plugin/`, `docs/`
and `.claude/` leaves only hits the outline classifies accurate.

## Skill quality

`design/SKILL.md` 175 lines (~200 hub guideline); `route-to-execution.md` 51;
`design-content-rules.md` 169. Progressive disclosure improved — a block
duplicated across two reference files became one opt-in node. Descriptions
untouched and still name their triggers.

## Summary

5 major, 4 minor, 1 observation. No UNFIXABLE blockers.
