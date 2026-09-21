# Verification of `plans/skill-reviews/design.md` — 2026-09-21

Checked against the working tree: `plugin/skills/design/SKILL.md` (285 lines,
modified today), `references/write-outline.md` (309, modified today),
`write-design.md` (101), `design-content-rules.md` (225), `research-protocol.md`
(64), `route-to-execution.md` (66, new since the review).
`references/write-inline-plan.md` and `plugin/fragments/continuation-passing.md`
no longer exist.

**Line budget:** `plugin/skills/design/SKILL.md` is allowlisted at ceiling
**285** and measures exactly 285 lines — edits to it must be net-zero or
shrinking. The references are not allowlisted (cap 400).

Review tally: 3 critical, 6 major, 7 minor = 16 findings. My table carries 16.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | open-design | Both sites survive: SKILL.md:104-105 "Route to structured-bugfix regardless of apparent complexity" and :239-241 "**Defect →** Route to structured-bugfix workflow: reproduce → root-cause → fix → verify." A repo-wide grep for `structured-bugfix` outside `plans/` returns only those two lines; the rest are `plans/reports/` documents proposing it as future work. `Defect` is still one of four values in the mandatory classification block (:177). Fork: build the workflow, or fold Defect into Simple/Moderate/Complex with the investigation steps inline. Not inside any named pending job. |
| C2 | Critical | open-design | Same defect as proof C1. Three caller sites remain: SKILL.md:214-215 and :232-233 ("outline-corrector dispatched by /proof on revise/kill"), `write-outline.md:224-226` and `write-design.md:76-78` (both "On terminal action "apply""). `proof/SKILL.md:170-176` still dispatches nothing. The fourth site (`write-inline-plan.md`) is gone with the file. Trigger disagreement unchanged. |
| C3 | Critical | fixed | SKILL.md:8 is now `allowed-tools: Agent, Read, Write, Edit, Bash, WebSearch, WebFetch, Skill` — `Edit` present, and `write-outline.md:129-133` still needs it ("append the paths recall selected to the recall artifact via Edit"). |
| M1 | Major | fixed | The description (:3-7) now reads "classify simple/moderate/complex, produce design documents for complex jobs, and **route by whether the work needs a runbook**" — the false "routes moderate to /runbook" summary clause is gone, and routing is no longer enumerated in a way that can drift. |
| M2 | Major | fixed | The artifact check now sends a pre-existing design to the gate: SKILL.md:59-60 "`design.md` exists → Read `references/write-design.md`, skip to C.5, which routes by `references/route-to-execution.md`". |
| M3 | Major | open-mechanical | SKILL.md:256-257 points at "the transformation table (T1–T6 in `docs/references/pipeline-contracts.md`)", then :263-267 gives three rows covering the outline format, the runbook format and requirements. `pipeline-contracts.md:59-64` carries six rows; T1 (`design.md` → `design-corrector`), T4 (per-slice correctors) and T5 (`corrector` + `triage-feedback.sh`) have no row. :269 still makes the coupling statement mandatory output. Fix by deletion (see edits) — completing the table would add lines this file has none of. |
| M4 | Major | fixed | The duplicated routing pseudocode is gone. Both phases now read one node: `write-outline.md:263-265` and `:302` route through `references/route-to-execution.md`, `write-design.md:92` likewise, and that node holds the single `IF/ELSE IF/ELSE` block (`route-to-execution.md:31-35`) plus the discriminators (:37-50). Extracted exactly as the reviewer proposed. |
| M5 | Major | open-design | Unchanged. `write-outline.md:136-142` makes the read of `research-protocol.md` conditional on external research, then A.5 at :160 reads it unconditionally ("Read `references/research-protocol.md` for outline content/format guidance"). Both files still specify the A.5 output (`write-outline.md:162-163` vs `research-protocol.md:20-42`) and the escape-hatch paragraph is still verbatim in both (`write-outline.md:165-167`, `research-protocol.md:62-64`). Fork: which file owns A.5's output spec — splitting by concern is an authoring structure call. |
| M6 | Major | open-design | `plugin/bin/triage-feedback.sh` still branches on `Simple` and `Complex` only, with a bare `else verdict="match"` for everything else, so `Moderate` and `Defect` are recorded as matching regardless of evidence. SKILL.md:189-191 is the producer side and describes the file as "consumed by `triage-feedback.sh` for post-execution comparison". Fork: give the script Moderate and Defect branches (what evidence discriminates them is undecided), or have the skill state that only Simple and Complex are checked. Not inside any named pending job. |
| m1 | Minor | open-mechanical | Marked: SKILL.md:246-247, `write-outline.md:181-182`, `design-content-rules.md:31-33`. Unmarked and still asserted as fact: `design-content-rules.md:36-38` ("items-per-phase x avg-LOC-per-item should fall in the 100-300 range") and :47-48 ("The 5-repetition threshold balances extraction overhead against repetition cost"). |
| m2 | Minor | open-mechanical | SKILL.md:238 still carries the aside: `*(Verb-oriented name: action the agent takes, not the artifact produced.)*`. Deleting it frees one line. |
| m3 | Minor | moot | `references/write-inline-plan.md` no longer exists, and a repo-wide grep for `inline-planned` returns hits only under `plans/`. The defect did **not** migrate: `docs/references/execution-routing.md:49` records "`inline-plan.md` is **removed as a kind, not renamed**", and `build/` uses no status vocabulary. |
| m4 | Minor | open-design | Unchanged and slightly worse: SKILL.md:32 still opens "### 0. Complexity Triage" and the file never reaches a step 1; `write-outline.md` still runs A.0, A.1, A.2, A.2.5, A.3-4, A.5, an unnumbered Post-Outline re-check (:169), A.6; `write-design.md` still C.1-C.5 with C.4.5 inserted (:74). Renumbering breaks every inbound cross-reference (`route-to-execution.md:57-59` names "from A.5 … from C.1"), so it is a structural choice. |
| m5 | Minor | open-mechanical | SKILL.md:189 still "Write the classification block verbatim to `plans/<job>/classification.md`", with the bracketed-placeholder template at :177-187 immediately above. `triage-feedback.sh` parses the `Classification:` line and falls through to `match` on an unrecognised value. |
| m6 | Minor | open-mechanical | The recall-diff paragraph is still in three places: `write-outline.md:149-153`, `research-protocol.md:22-31`, `write-design.md:7-16`. |
| m7 | Minor | open-mechanical | `write-outline.md:50` still routes to a glob inside the A.1 table: "Read `plugin/fragments/*.md` directly when referenced." |

## Cross-file links

- C2 ↔ proof C1: one fix, two reports.
- M5 and m6 are the same wound — three files each carrying a copy of
  A.5-adjacent content — and should be repaired together.
- m1 is the same class as deliverable-review M2, runbook M5, review m16 and
  formalize 7: a threshold asserted where a sibling marks the same number
  ungrounded.

## Exact edits for `open-mechanical`

### `plugin/skills/design/SKILL.md` — net-zero or shrinking

**M3** — replace the drifted table with the pointer that already exists.

- delete :261-267 (the `**Dependency mapping:**` heading, its blank lines, and
  the four table lines) and amend :256-257:
  - old: `1. Identify the corrector from the transformation table (T1–T6 in`
    `   `docs/references/pipeline-contracts.md`)`
  - new: `1. Identify the corrector from the transformation table (T1–T6 in`
    `   `docs/references/pipeline-contracts.md` §D-26) — Read it; do not work from`
    `   memory of it`
  Net −5 lines. The alternative — adding T1, T4 and T5 rows — costs +3 and the
  file has no budget for it.

**m2** — delete :238 (`     *(Verb-oriented name: action the agent takes, not the
artifact produced.)*`). Net −1.

**m5** — :189:

- old: `**Classification persistence (C-2):** Write the classification block verbatim to`
- new: `**Classification persistence (C-2):** Write the filled-in classification block to`

### `plugin/skills/design/references/design-content-rules.md`

**m1**, two sites:

- :36-38 old: `- **Heuristic:** items-per-phase x avg-LOC-per-item should fall in the 100-300`
  `  range. Below 100 suggests items are trivially small; above 300 suggests items`
  `  are overloaded.`
  new: same three lines with `*(ungrounded — needs calibration)*` appended to the
  third.
- :47-48 old: `repetitions increases with count). The 5-repetition threshold balances`
  `extraction overhead against repetition cost.`
  new: `repetitions increases with count). Five is an arbitrary trigger point, not`
  `calibrated against measured extraction or repetition cost.`

### `plugin/skills/design/references/write-outline.md`

**m6** — delete the recall-diff paragraph at :149-153, replacing it with:

- new: `**Recall diff:** per `references/research-protocol.md` §A.5 — re-invoke recall`
  `on what just changed and reconcile the artifact.`
  Then do the same at `write-design.md:7-16`, leaving `research-protocol.md:22-31`
  as the single definition.

**m7** — :50, inside the A.1 table's Level 1 cell:

- old: `` Read `plugin/fragments/*.md` directly when referenced. `` 
- new: `` Read the named fragment under `plugin/fragments/` when a step references one. ``
