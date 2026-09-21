# Verification of `plans/skill-reviews/recall.md` — 2026-09-21

Checked against the working tree copy of `plugin/skills/recall/SKILL.md` (94
lines, modified today — verified against the tree, not HEAD). Supporting files:
`docs/references/quality-gates.md` (D-48),
`docs/references/project-configuration.md` (D-72),
`plugin/fragments/delegation.md`.

Review tally: 2 critical, 5 major, 5 minor = 12 findings. My table carries 12.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | fixed | Both sides reconciled. SKILL.md §Procedure step 2 (:62-66): "The index is normally injected at session start. Confirm its lines are in this context before matching against them; where they are not, Read `MEMORY.md` under the corpus root step 3 resolves." quality-gates.md:37-49 (D-48) now states the anchor is "the Read of `<plan-dir>/recall-artifact.md` followed by Reads of the files selected from the index — *not* a Read of the index itself … the index Read is conditional on its lines not being in context (D-85) and never becomes the anchor." The absolute "never Read" is gone and the design no longer contradicts itself. |
| C2 | Critical | fixed | SKILL.md step 5 (:80-84): "Index links are store-relative, so join each to the corpus root resolved in step 3 — a link reading `ddaanet/foo.md` is `<root>/ddaanet/foo.md`. Never hardcode the root". |
| M1 | Major | open-design | Description (:3-8) still names "recall", "check memory" and closes "Not needed for facts already in this context", with no clause excluding `gitlore:recall`; steps 4 and 5 still carry the five-entry ceiling, "unsure means exclude", "do not re-select a body already pulled", "An empty selection is legitimate" and the single-message batch Read. The fork: narrow this skill to step 1 (plan artifact) + step 6 (report contract) and route selection discipline to `gitlore:recall`, or keep the duplication deliberately. Not inside any named pending job. |
| M2 | Major | fixed | The hardcoded degrade path is gone. Step 2 now ends "Where the file is absent too, run `rg --files` over the corpus root and select on filenames instead" (:66) — the root is step 3's, named as such, so nothing resolves against a fixed `memory/` path. The forward reference to step 3 remains but is explicit and resolvable. |
| M3 | Major | open-mechanical | SKILL.md:17-18 still "Callers do not restate any of this — they invoke this skill with a plan directory and a topic, and add only their own delta." Falsified by `build/references/dispatch-composition.md:16` ("`Read plans/<job>/recall-artifact.md, then Read each file it lists`"), `build/references/review-dispatch-template.md:58-59` ("Read `plans/<job>/recall-artifact.md` and Read each file it lists") and `fragments/delegation.md:92-96`. Those restatements are correct — a dispatched subagent may lack `Skill` — so the blanket claim is the defect. |
| M4 | Major | fixed | Step 2 (:63-66) carries the exception: "Its absence is ordinary, not impossible: one prior session found it missing at every recall checkpoint." |
| M5 | Major | open-mechanical | SKILL.md:42-43 still "Entries the caller already supplied in a delegation prompt take precedence: do not re-resolve them", against `fragments/delegation.md:118-119` "**Reference recall artifact file paths. Do not inline resolved recall content in delegation prompts.**" The ambiguity (inlined content vs paths) is unchanged. |
| m1 | Minor | open-mechanical | Step 4 (:74) still "At most 5 entries" with no source. |
| m2 | Minor | fixed | The closing paragraph is now an instruction to the holder: ":93-94 "A caller that reaches this checkpoint without the index is step 2's conditional Read. It runs the same procedure."" — no longer a prohibition that cannot fire in time. |
| m3 | Minor | disputed | :15 still says "The one procedure for every recall checkpoint", but the two things the reviewer counted as exceptions are now *inside* the procedure: step 6's caller override (:90-91) is a documented clause of step 6, and the no-index case (:93-94) explicitly "runs the same procedure". A procedure with a documented per-caller override is still one procedure. |
| m4 | Minor | open-mechanical | :15-22 and :93-94 are still third-person descriptions of caller behaviour — the framing that lets M3's false claim sit unchecked. Fix rides with M3. |
| m5 | Minor | fixed | Step 2's verb is now an act ("Match the topic against the index", :62); the old "Treat the index as already in context" is gone. Step 3 "Resolve the corpus" (:68) does resolve a value the later steps consume. |

## Cross-file links

- M3 is the same defect as ground finding 5 and deliverable-review M6 in class
  (fragment/skill boundary claims), but here the claim is false rather than
  missing.
- M5 pairs with `fragments/delegation.md` §Recall Content In Delegation Prompts;
  fixing one without the other reopens it.
- proof M4 (per-item recall dropping the plan-dir half) is disposed in
  `verify-proof.md` and depends on this skill's §Invocation contract (:25).

## Exact edits for `open-mechanical`

`plugin/skills/recall/SKILL.md` is not on the line-limit allowlist (94 lines,
cap 200), so these may add lines.

### M3 + m4 — :17-18

- old: `plan's recall artifact, select further entries from the memory index, Read their`
  `bodies, report. Callers do not restate any of this — they invoke this skill with`
  `a plan directory and a topic, and add only their own delta.`
- new: `plan's recall artifact, select further entries from the memory index, Read their`
  `bodies, report. A caller invokes this skill with a plan directory and a topic`
  `and adds only its own delta — except a dispatch prompt for a sub-agent that may`
  `hold no `Skill` tool, which restates step 1 inline`
  (`plugin/fragments/delegation.md` §Recall Artifacts For Sub-Agents).`

### M5 — :42-43

- old: `Entries the caller already supplied in a delegation prompt take precedence: do`
  `not re-resolve them.`
- new: `A delegation prompt supplies entries as **paths**, never as inlined content`
  (`plugin/fragments/delegation.md` §Recall Content In Delegation Prompts): Read`
  `those paths and do not re-select against the index for them.`

### m1 — :74

- old: `**4. Select under discipline.** At most 5 entries, covering whatever step 1 did`
- new: `**4. Select under discipline.** At most 5 entries — an arbitrary ceiling, not`
  `calibrated — covering whatever step 1 did`
