# Verification of `plans/skill-reviews/requirements.md` — 2026-09-21

Checked against the working tree: `plugin/skills/requirements/SKILL.md` (357
lines, unmodified today) and `references/empirical-grounding.md` (71).
`plugin/fragments/continuation-passing.md` no longer exists.

**Line budget:** `requirements/SKILL.md` is allowlisted at ceiling **357** and
measures exactly 357 lines. Every additive fix below is paired with a deletion
so the net is zero or negative; `references/empirical-grounding.md` is not
allowlisted.

Review tally: 2 critical, 6 major, 10 minor = 18 findings. My table carries 18.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | open-mechanical | Unchanged. Step 5 (:194) invokes `/proof plans/<job>/requirements.md` and :199-200 says "On terminal action 'apply', accumulated decisions are applied to the artifact"; step 6 (:202-205) "After user validation: Write to `plans/<job>/requirements.md` (create directory if needed)". §STOP Conditions (:326-329) still says the conditions "abort before an artifact is written". `proof/SKILL.md:27` takes an existing `<artifact-path>` and :85 Reads it. The skill still validates a file that does not exist, or writes it twice. |
| C2 | Critical | fixed | `allowed-tools` (:4) is `Read, Write, Bash, Skill` — no `AskUserQuestion` — and :185-190 forbids it explicitly: "Never reach for `AskUserQuestion`. A picker hides the exchange from the transcript…". The gap-fill block at :173-183 is now numbered prose with proposed answers, and elicit mode (:213-225) the same. Closes with formalize 3, review C1, proof M7. |
| M1 | Major | moot | The protocol the finding measures against is gone: `plugin/fragments/continuation-passing.md` no longer exists, and no sibling declares `cooperative:` or `default-exit:` any more — `design/SKILL.md:1-10`, `runbook/SKILL.md:1-14` and `build/SKILL.md:1-10` all carry plain frontmatter. Nothing is silently dropped because nothing is passed. The prose Default Exit (:303-322) is now the house form, not a hand-rolled substitute. |
| M2 | Major | open-mechanical | §STOP Conditions (:324-350) still sits after §Default Exit (:303). D-53 survives at `docs/references/quality-gates.md:83`. The three relocatable conditions are still "No job name given" (:332), "Extract mode with no substantive conversation" (:333-335) and the overwrite guard (:336-338). |
| M3 | Major | open-mechanical | Step 1 Scan Conversation (:100-112), step 3 Structure Requirements (:145-151) and step 4 Gap Detection (:153-166) still open with prose, no tool call. D-52 at `quality-gates.md:76`; the skill applies it deliberately at :46-47 and :136-137. Net-zero fixes available on each step's first body line. |
| M4 | Major | open-mechanical | `allowed-tools` (:4) still omits `Edit` while :292 instructs "If indicators found, append to artifact" with the block at :294-297. `proof/SKILL.md:8` and `runbook/SKILL.md:7` both carry `Edit`. |
| M5 | Major | open-mechanical | Both halves survive. "### Post-Explore Recall Gate" (:133) is still unnumbered between step 2 (:114) and step 3 (:145) at the same heading level, and :229-230 still recaps "Extract mode steps 2-6 (Codebase Discovery, Structure, Gap Detection, **Present Draft**, Write Artifact)" while the actual step 5 heading (:192) is "User Validation". |
| M6 | Major | open-mechanical | `references/empirical-grounding.md` is still routed only from :357, the last bullet of §Key Principles, while its content grounds :110-112 (do-not-infer — `empirical-grounding.md:47-55`), :164-166 (question budget — :54) and :213-221 (semi-structured elicit — :37-44). Net-zero fix: spend the last bullet on one inline route. |
| m1 | Minor | open-mechanical | :29 still "**Primary signal:** `rg --files plans/<job>/requirements.md` — if file exists". On a missing file `rg --files` prints an IO error to stderr and exits non-zero, which under the no-silent-errors rule reads as a failure rather than a negative answer. :125 still constrains Bash to "(`rg`, `rg --files`)", so the fix touches that line too. |
| m2 | Minor | open-mechanical | :46-47 still passes a topic only. That is *correct* per `recall/SKILL.md:30-31` ("Absent: step 1 is skipped and selection starts at the index"), since requirements is the artifact's author — but the skill still does not say so, and `runbook/SKILL.md:56` passes the plan-dir form, so a reader sees an inconsistency with no stated reason. |
| m3 | Minor | open-mechanical | :136-137 still issues a second `Skill(skill: "edify:recall")`, against `recall/SKILL.md:26-28`: "A caller whose recall recurs … invokes this skill once; every later recurrence runs the loaded procedure inline, since a further `Skill` call only reprints a body already in context." `runbook/SKILL.md:70-71` has the identical pattern — pipeline-wide, not unique here. |
| m4 | Minor | open-design | "D+B" is still unexpanded at :139 and nothing routes to D-52. Repo-wide: same finding as runbook m13. One decision covers every site. |
| m5 | Minor | open-mechanical | :25 still "Skill automatically detects appropriate mode based on conversation history."; :198 still "/proof handles the iterative validation loop"; :49-53 is still an explanatory paragraph mid-procedure. |
| m6 | Minor | open-mechanical | The question budget is still stated three times, in agreement: :164-166, :220-221, :355. |
| m7 | Minor | open-mechanical | :14-17 §Target Model still "**Opus required.** Extract mode requires synthesizing nuanced conversation context; sonnet misses implicit requirements." Skill frontmatter carries no model field. Deleting the section frees four lines — the budget for M3, M4 and M6. |
| m8 | Minor | open-mechanical | :264 still offers `plans/<job-name>/reports/explore-<topic>.md` in the References template, while :126-127 forbids "No agent delegation / No Context7, no web research, no scout" — the two producers of such a report. |
| m9 | Minor | open-mechanical | "Standalone" is still an exit route at :312 and :342, though no skill or command by that name exists; :321 already says what it means plainly. |
| m10 | Minor | open-mechanical | :3 is still a plain scalar `description: Capture and document requirements…` on one long line, where siblings use `>-` block form. |

## Cross-file links

- C2 closes with formalize 3, review C1, proof M7 — one rewrite pattern, four
  skills, all landed.
- m3 = runbook's identical re-invocation; both measure against
  `recall/SKILL.md:26-28`.
- m4 = runbook m13 (D+B expansion).
- m2 pairs with proof M4, which is the *wrong* side of the same contract: proof
  drops the plan dir where it has one, requirements omits it correctly.

## Exact edits for `open-mechanical`

All in `plugin/skills/requirements/SKILL.md` unless noted. Budget: m7 frees 4
lines, m6 frees 2, m9 frees 0 (in-place), m10 costs 1 — net available +5.

**m7 (do this first, it funds the rest)** — delete :14-17:

```
## Target Model

**Opus required.** Extract mode requires synthesizing nuanced conversation
context; sonnet misses implicit requirements.
```

**C1** — step 5 writes, step 6 finalises.

- :192-196 old: `### 5. User Validation`
  ``
  `` Invoke `/proof plans/<job>/requirements.md` — structured reword-accumulate-sync ``
  `loop on the requirements draft. Present artifact path, summarize sections`
  `populated, note Open Questions.`
- new: `### 5. Write the Draft and Validate`
  ``
  `` Write the draft to `plans/<job>/requirements.md` (create the directory if ``
  `` needed), then invoke `/edify:proof plans/<job>/requirements.md` — a structured ``
  `reword-accumulate-sync loop on it. Present the artifact path, summarize the`
  `sections populated, note Open Questions.`
- :202-205 old: `### 6. Write Artifact`
  ``
  `After user validation:`
  `- Write to `plans/<job>/requirements.md` (create directory if needed)`
- new: `### 6. Finalise`
  ``
  `After /proof applies the accumulated decisions:`
  `- Confirm the artifact on disk matches the validated state`

(The `/edify:proof` qualification is proof M1's fix, listed there too.)

**M2** — move three STOP conditions to where they bind:

- move :332 ("**No job name given.** …") and :333-335 ("**Extract mode with no
  substantive conversation…**") into §Mode Detection, after :31
- move :336-338 (the overwrite guard) into step 6, after the new :205
- leave :339-342 (the open-questions condition) where it is, since it qualifies
  §Default Exit

**M3**, three sites, all net-zero:

- :102 old: `Extract from conversation history:`
  new: `Read `plans/<job>/requirements.md` if it exists, then extract from history:`
- :147 old: `Format into standard artifact (see Standard Format section below):`
  new: `Read §Standard Format below, then format the extracted items by it:`
- :155 old: `Check for empty critical sections:`
  new: `Read the structured draft, then check for empty critical sections:`

**M4** — :4:

- old: `allowed-tools: Read, Write, Bash, Skill`
- new: `allowed-tools: Read, Write, Edit, Bash, Skill`

**M5**, two sites:

- :133 old: `### Post-Explore Recall Gate`
  new: `### 2.5 Post-Explore Recall Gate`
- :229-230 old: `After elicitation, follow Extract mode steps 2-6 (Codebase Discovery, Structure,`
  `Gap Detection, Present Draft, Write Artifact).`
  new: `After elicitation, follow Extract mode steps 2, 2.5 and 3-6 (Codebase`
  `Discovery, Post-Explore Recall, Structure, Gap Detection, Write and Validate,`
  `Finalise).`
  (+1 line, paid from m7's budget)

**M6** — delete :357 (`- See `references/empirical-grounding.md` for research
basis`) and route inline at the highest-value point, :110-112:

- old: `**Critical rule:** Extract from what was said, do NOT infer unstated`
  `requirements. Hallucination risk — if not discussed, flag as Open Question`
  `rather than inventing.`
- new: `**Critical rule:** Extract from what was said, do NOT infer unstated`
  `requirements. Hallucination risk — if not discussed, flag as Open Question`
  `rather than inventing. Basis: `references/empirical-grounding.md``
  `§Hallucination Risk and §AI Weaknesses.`
  (+1 line, −1 from the deletion)

**m1**, two sites:

- :29 old: `**Primary signal:** `rg --files plans/<job>/requirements.md` — if file exists,`
  new: `**Primary signal:** `test -f plans/<job>/requirements.md` — if it exists,`
- :125 old: `- Direct tool use only (Read, Write, Bash (`rg`, `rg --files`))`
  new: `- Direct tool use only (Read, Write, Bash (`rg`, `rg --files`, `test -f`))`

**m2** — :46-47, add the reason on the existing gate-anchor line at :49:

- :49 old: `**Gate anchor:** The recall artifact **write** is the structural anchor — a tool`
  new: `**Gate anchor:** No plan-dir argument: this skill *creates* the artifact, so`
  `there is none to resolve. The artifact **write** is the structural anchor — a tool`
  (+1 line, paid from m7)

**m3** — :136-137:

- old: `during the initial recall pass. Invoke `Skill(skill: "edify:recall")` (no`
  `topic).`
- new: `during the initial recall pass. Run the recall procedure already loaded at`
  `:46 inline, with no topic — do not issue a second `Skill` call.`

**m5**, three sites:

- :25 old: `Skill automatically detects appropriate mode based on conversation history.`
  new: `Detect the mode from conversation history (see §Mode Detection).`
- :198 old: `/proof handles the iterative validation loop. No corrector dispatch for`
  new: `/proof runs the iterative validation loop. No corrector dispatch for`
- :50-53: compress the explanatory paragraph to its instruction — keep "write
  the artifact with an explicit null entry when nothing relevant is found", drop
  the downstream-rationale sentence.

**m6** — delete :220-221 ("Total budget: 4-6 questions." is duplicated by :166)
and :355 (`- Gap-fill, not interrogation: max 3 questions (extract) or 4-6
(elicit)`), keeping :164-166 as the single statement.

**m8** — :264:

- old: `- `plans/<job-name>/reports/explore-<topic>.md` — codebase exploration findings`
- new: `- `plans/<job-name>/reports/explore-<topic>.md` — inherited from prior work;`
  `  this skill does not produce one`
  (+1 line, paid from m7 / m6's deletions)

**m9**, two sites:

- :312 old: `- 3+ open questions or empty critical sections → Standalone (revisit when clearer)`
  new: `- 3+ open questions or empty critical sections → stop here; revisit when clearer`
- :342 old: `  exists, mark the artifact incomplete in its header, and route to Standalone`
  new: `  exists, mark the artifact incomplete in its header, and stop here`

**m10** — :3, convert to block form:

- old: `description: Capture and document requirements for implementation. Triggers on "capture requirements", "document requirements", "what do I want to build", or feature discussions without clear documentation. Produces requirements.md artifact for design and planning phases.`
- new: `description: >-`
  `  Capture and document requirements for implementation. Triggers on "capture`
  `  requirements", "document requirements", "what do I want to build", or feature`
  `  discussions without clear documentation. Produces requirements.md artifact`
  `  for design and planning phases.`
  (+4 lines — this is the one edit the budget may not cover; apply it only after
  re-counting, or leave m10 unfixed as the cosmetic it is)
