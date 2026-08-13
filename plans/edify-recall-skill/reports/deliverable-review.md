# Deliverable Review: edify-recall-skill

**Date:** 2026-08-13
**Methodology:** agents/decisions/deliverable-review.md
**Design reference:** docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md (FR1-FR9, D1-D7)
**Reviewed commit:** 6108f610 (already on `main`)

## Inventory

`plugin/bin/deliverable-inventory.py` returned an empty table: it diffs
`merge-base HEAD main`, and the work is committed on `main`, so the merge base
is the commit itself. Inventory below reconstructed from `6108f610^..6108f610`,
excluding `plans/`, `.claude/`, and the `memory` submodule pointer.

| Type | File | + | - |
|------|------|---|---|
| Agentic prose | plugin/skills/recall/SKILL.md (new) | +52 | -0 |
| Agentic prose | plugin/skills/requirements/SKILL.md | +4 | -7 |
| Agentic prose | plugin/skills/design/SKILL.md | +1 | -5 |
| Agentic prose | plugin/skills/orchestrate/SKILL.md | +1 | -1 |
| Agentic prose | plugin/skills/review-plan/SKILL.md | +1 | -1 |
| Agentic prose | plugin/skills/proof/SKILL.md | +2 | -2 |
| Agentic prose | plugin/agents/corrector.md | +1 | -1 |
| Agentic prose | plugin/agents/design-corrector.md | +1 | -1 |
| Agentic prose | plugin/agents/outline-corrector.md | +1 | -1 |
| Agentic prose | plugin/agents/runbook-outline-corrector.md | +1 | -1 |
| Code | plugin/bin/prepare-runbook.py | +1 | -1 |
| Human docs | CLAUDE.md | +1 | -1 |
| Human docs | plugin/README.md | +1 | -0 |

**Total:** 13 files, +68 / -22. Under the 500-line Layer 1 gate — Layer 1
skipped, Layer 2 covers per-file axes and cross-cutting checks.

**Design conformance:** every file in the design's §4 Scope-of-change table was
produced, and no file outside it was touched. No missing deliverables, no
unspecified deliverables, no excess.

**Gate:** `just precommit` — version consistent 0.0.3, tests cached (inputs
unchanged), ✓ Precommit OK.

## Critical Findings

### C1 — The four corrector agents invoke `Skill` without declaring it

- `plugin/agents/corrector.md:188` — `tools: ["Read", "Write", "Edit", "Bash"]`
- `plugin/agents/design-corrector.md:95` — same, no `Skill`
- `plugin/agents/outline-corrector.md:58` — same, no `Skill`
- `plugin/agents/runbook-outline-corrector.md:71` — same, no `Skill`

**Design requirement:** D2 — "Subagents invoke the skill directly. The four
corrector agents therefore need the same procedure as the skills, from the same
source."

**Impact:** Each agent's inlined fallback procedure was deleted and replaced by
a call to a tool its own frontmatter does not request. Per
`memory/cc-subagent-context-capabilities.md`, a declared `tools:` list is a
request rather than a contract — undeclared tools sometimes arrive — so this may
work by accident, but that memory's own rule is to verify before relying on any
tool in an agent. If `Skill` does not arrive, the failure is silent: no fallback
text remains, so the corrector proceeds with no recall at all and review quality
degrades invisibly.

This is the same gap class the commit fixed for `requirements` and `proof`
(`allowed-tools: … , Skill`); the agent side was missed. `plugin/agents/artisan.md`
already declares `"Skill"`, so the convention exists in-repo.

**Fix:** add `"Skill"` to the `tools:` array in all four agent definitions.

## Major Findings

### M1 — Five further call sites still carry the inlined paragraph and the `agents/decisions/` dependency

The design's §1 states "Eight files in the plugin carry their own copy of the
same paragraph." Against the actual corpus that is an undercount. Still
un-rewired, each still naming `agents/decisions/*.md` as recall corpus:

- `plugin/skills/runbook/SKILL.md:120-123` — Implementation recall (D+B anchor)
- `plugin/skills/inline/SKILL.md:70-73` — §2.3 Recall (D+B anchor)
- `plugin/skills/runbook/references/tier3-planning-process.md:22-25` and `:47-50`
- `plugin/skills/inline/references/review-dispatch-template.md:25-28`
- `plugin/skills/design/references/write-outline.md:39` (A.1 Level 1) and `:87`
  (A.2.5 post-explore gate)

**Design requirement:** D6 — "`agents/decisions/` leaves the corpus. Those files
are being folded into the living design doc, so recall must not encode a
dependency on them."

**Impact:** Conformance to the written spec is intact — the delivered work does
exactly what §4 lists. Functional completeness against D6's stated intent is
not: the pipeline still instructs six recall sites to read a corpus that is being
dissolved, and the duplication the design exists to remove survives at those
sites. `tier3-planning-process.md:31` goes further and names two specific files
(`agents/decisions/implementation-notes.md`, `testing.md`) as mandatory reads.

### M2 — The recall-artifact format is duplicated and the two copies now disagree

- `plugin/skills/requirements/SKILL.md:59` — `agents/decisions/<name>.md` example
  line removed (per §4)
- `plugin/skills/design/references/write-outline.md:67` — the same format block,
  still listing `agents/decisions/<name>.md`

**Impact:** `/requirements` and `/design` write the same artifact from two
divergent format specs. `resolve_recall_entries`' docstring now says "the memory
files named in the recall artifact" while `write-outline.md` still tells the
designer to name decisions files in it. Consumers are unaffected mechanically
(the resolver resolves whatever paths it is given), but the format is no longer
single-sourced or self-consistent.

### M3 — `requirements` Post-Explore gate tells the caller to re-Read what the skill already Read

`plugin/skills/requirements/SKILL.md:105-108`:

```
Discovery via `rg --files`/`rg` (Bash) … Invoke `Skill(skill: "edify:recall")` (no topic).

**Gate anchor (D+B — tool call required):**
- **New entries found:** Read the matching `memory/*.md` files, then add their paths…
```

**Design requirement:** D1 — the skill owns select-then-Read; callers own the
artifact. FR7 — every Read issues in a single message, inside the skill.

**Impact:** The bullet survives from the pre-rewire text, where the caller did
the Read. Now the skill has already Read the bodies, so the instruction either
duplicates every Read or leaves the agent reconciling two conflicting owners of
the same step. The bullet should carry only the artifact write — "add the paths
of the entries recall selected".

## Minor Findings

**Topic placeholders lost their derivation guidance.** Four sites pass a bare
`<topic>` with nothing to resolve it from, where the other five give derivation
guidance (`"<topic derived from phase scope>"`, `"<topic covering quality
patterns, failure modes>"`):

- `plugin/agents/outline-corrector.md:58` and
  `plugin/agents/runbook-outline-corrector.md:71` — the inline plan's items 8-9
  specified "same edit as corrector.md", which supplies a topic
- `plugin/skills/design/SKILL.md:57` — the dropped lead sentence was where
  "triage-relevant" came from
- `plugin/skills/proof/SKILL.md:100` — the prior text said "for that item's
  topic"; the rewrite dropped the antecedent

FR9 requires each call site to supply its own topic; a literal `<topic>` supplies
none.

**Section purpose dropped with the procedure.** `plugin/skills/design/SKILL.md:49-57`
— "Triage Recall (D+B anchor)" now runs heading → code block, having lost "surface
codified decisions that constrain classification before it happens." Conformant
(inline plan item 3 specified the removal), but the section no longer says why the
gate exists, which is what keeps a D+B anchor from being rationalized away.

**Project-specific example inside a distributed skill.**
`plugin/skills/recall/SKILL.md:35` — "In this project that resolves to `memory/`"
ships to every install of the plugin. It matches FR5's wording and is framed as an
example, so it is conformant, but it reads as a statement about the reader's
project rather than about edify's.

## Gap Analysis

| Requirement | Status | Reference |
|-------------|--------|-----------|
| FR1 — one skill owns select-then-Read | Covered | recall/SKILL.md:12-18 |
| FR2 — optional topic, else trigger-based | Covered | recall/SKILL.md:21-24 |
| FR3 — index never Read | Covered | recall/SKILL.md:26-27 |
| FR4 — degrade to `rg --files memory/` | Covered | recall/SKILL.md:29-31 |
| FR5 — corpus resolved from session context | Covered | recall/SKILL.md:33-36 |
| FR6 — ≤5, certainty-gated, thematic, no re-select | Covered | recall/SKILL.md:38-42 |
| FR7 — batch-Read in one message | Covered | recall/SKILL.md:44 |
| FR8 — writes nothing | Covered | recall/SKILL.md:46-48; no `Write` in allowed-tools |
| FR9 — call sites invoke with own topic | Partial | 9 sites rewired; 4 pass bare `<topic>` (Minor); 5 further sites un-enumerated (M1) |
| D1 — skill owns procedure, caller owns artifact | Partial | M3 |
| D2 — subagents invoke directly | **Blocked** | C1 — `Skill` undeclared in all four agents |
| D3 — description names the edify pipeline | Covered | recall/SKILL.md:3-7 |
| D4 — `proof` rewired, not deleted | Covered | proof/SKILL.md:100 |
| D5 — ceiling of 5 | Covered | recall/SKILL.md:38 |
| D6 — `agents/decisions/` leaves the corpus | Partial | M1, M2 |
| D7 — no compaction exception clause | Covered | no exception clause in recall/SKILL.md |

## Resolution

All seven findings fixed in the working tree after this review. `just precommit`
green afterwards (version consistent 0.0.3, tests cached, ✓ OK).

| Finding | Fix |
|---------|-----|
| C1 | `"Skill"` added to `tools:` in all four corrector agents (`runbook-corrector` already declared it) |
| M1 | Six sites rewired to invoke `edify:recall`: `runbook/SKILL.md`, `inline/SKILL.md`, `tier3-planning-process.md` (recall step, artifact augmentation, post-explore gate), `review-dispatch-template.md`, `write-outline.md` A.1 Level 1 |
| M2 | `agents/decisions/<name>.md` dropped from `write-outline.md`'s artifact-format block, matching `requirements/SKILL.md` |
| M3 | Post-explore gate bullets in `requirements/SKILL.md`, `write-outline.md`, and `tier3-planning-process.md` now record paths only — "recall has already Read the bodies" |
| Minor 1 | Derivation guidance restored in all four bare-`<topic>` sites |
| Minor 2 | Purpose sentence restored to `design/SKILL.md` Triage Recall |
| Minor 3 | `recall/SKILL.md:35` reworded — "In an edify checkout that resolves to `memory/`; elsewhere it resolves wherever that session's store lives" |

Post-fix verification: no inlined index-selection procedure remains anywhere in
`plugin/` outside `skills/recall/`, and no `agents/decisions/*.md` reference
remains in any recall path. The `agents/decisions` references that survive are
non-recall (deliverable-review methodology, pipeline contracts, design content
rules), which D6 does not touch.

Fifteen call sites now invoke `edify:recall` — the design's nine plus the six
from M1.

## Summary

**1 critical, 3 major, 3 minor — all fixed.**

Design conformance is exact: every §4 file changed, nothing outside it touched,
no missing or excess deliverables, and `just precommit` is green. The findings are
completeness gaps rather than scope violations.

C1 is the one that breaks a delivered path — the correctors' recall now depends on
a tool they do not declare, and the fallback that would have covered it was
removed in the same edit. M1/M2 record that the design's eight-site enumeration
undercounted the corpus, so the duplication and the `agents/decisions/` dependency
both survive at six locations the spec never listed.
