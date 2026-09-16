# plugin-dev:skill-reviewer on plugin/skills/requirements (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — parts 2 and 3 pending.**

Scope: `SKILL.md` and `references/empirical-grounding.md` (the only file under
`references/`). No fragment is referenced; the sole outbound link is at line 296.

## Critical

**C1. Step 5 and step 6 contradict each other on when the artifact is written.**
SKILL.md:155 invokes `/proof plans/<job>/requirements.md`, while step 6 (:160-162)
says "After user validation: Write to plans/<job>/requirements.md (create directory
if needed)". `/proof` takes an existing artifact path (`proof/SKILL.md:21`), and
SKILL.md:157 compounds it ("On terminal action 'apply', accumulated decisions are
applied to the artifact"), presupposing the file exists during step 5. SKILL.md:267-268
puts the STOP conditions "abort before an artifact is written" after validation too.
As written the skill validates a file that does not exist, or writes it twice.
Siblings resolve it the other way (`design/references/write-design.md:60` proofs a
`design.md` the phase already wrote). Fix: step 5 writes the draft and step 6 applies
the proof outcome, or fold the write into step 4 and retitle step 6.

**C2. The skill mandates `AskUserQuestion`, which the always-loaded conventions
forbid.** SKILL.md:4 declares it; :134-151 gives a worked block for gap-fill; :172
mandates it per critical section in elicit mode. `memory/ddaanet/shared-claude.md:22`
forbids it, and that file is imported at `CLAUDE.md:7`, so it loads every session in
this repo. The conflict is unavoidable at runtime. Requirements is the heaviest user,
but it is repo-wide: `proof/SKILL.md:8`, `formalize/SKILL.md:15` and
`review/SKILL.md:20` also declare or instruct it. Either the shared convention needs
a stated exception for user-facing pipeline skills, or these skills need rewriting to
numbered prose questions with stated defaults. The gap-fill block at :134-151
converts cleanly, since its options already carry labels and descriptions.

## Major

**M1. No continuation frontmatter, though the skill documents its own exits.**
SKILL.md:1-6 declares only name, description, allowed-tools, user-invocable, while
:242-261 documents a Default Exit with routing criteria and a workflow-positioning
block naming `/design` and `/handoff:handoff`. Every other pipeline skill declares the
protocol (`design/SKILL.md:10-12`, `runbook/SKILL.md:14-16`, `inline/SKILL.md:9-11`,
`orchestrate/SKILL.md:6-8`), each with `cooperative: true` and a `default-exit`. Per
`fragments/continuation-passing.md:28-37`, a skill without `cooperative: true` does
not implement the consumption protocol, so a continuation passed to `/requirements`
is silently dropped at the pipeline's entry point. The prose Default Exit is a
hand-rolled substitute that never links the fragment.

**M2. STOP conditions sit after the procedure they are meant to prevent**
(SKILL.md:263-289, after Default Exit). D-53 (`docs/design.md:706-709`): negative
constraints sit beside the positive guidance they qualify. Natural homes: "No job
name given" (:271) and "Extract mode with no substantive conversation" (:272-274) at
Mode Detection (:24-30); "existing requirements.md overwritten with a narrower scope"
(:275-277) at step 6 (:160).

**M3. Three procedure steps open with no tool call, against the skill's own anchoring
convention.** D-52 (`docs/design.md:697-703`) requires every step to open with a
concrete tool call; the skill applies it deliberately at :40 and :107. Step 1 Scan
Conversation (:74-84), step 3 Structure Requirements (:112-117) and step 4 Gap
Detection (:119-133) are prose-only. Step 4 matters most: a judgement gate on section
emptiness, exactly the shape D-52 says gets skipped, and it could anchor on a Read of
the draft.

**M4. `allowed-tools` omits `Edit` while the body instructs an append.** SKILL.md:4
lists Read, Write, Bash, AskUserQuestion, Skill; :233 says "If indicators found,
append to artifact" with the block at :235-238. With Write only, appending means
rewriting the whole file from memory, risking loss of what the `/proof` loop just
settled. `proof/SKILL.md:8` and `runbook/SKILL.md:7` both carry `Edit`.

**M5. Step numbering breaks in both modes.** SKILL.md:103 inserts an unnumbered
"Post-Explore Recall Gate" between step 2 (:86) and step 3 (:112) at the same heading
level. :174-176 then says "follow Extract mode steps 2-6 (Codebase Discovery,
Structure, Gap Detection, Present Draft, Write Artifact)" — the count is right, but
"Present Draft" does not match the actual step 5 heading, "User Validation" (:153),
and the recap omits the unnumbered recall gate.

**M6. Progressive disclosure is inverted: the reference is linked from the last
line.** `references/empirical-grounding.md` is routed only from SKILL.md:296, the
final bullet under Key Principles, while its content justifies three rules appearing
far earlier: the do-not-infer rule (:84, grounded at `empirical-grounding.md:40-48`),
the question budget (:130-132, at :47), the semi-structured elicit design (:170-172,
at :34-38).

## Minor

**m1. `rg --files` used as an existence test** (SKILL.md:26). The reviewer ran both
cases: on an existing file it prints the path and exits 0; on a missing file it
prints an IO error to stderr and exits 2. Under the no-silent-errors rule that reads
as a failure rather than a negative answer, and invites suppression. `test -f` is the
existence primitive. SKILL.md:96 also constrains Bash to rg forms, so the fix touches
that line.

**m2. The recall args omit the plan-dir half** (SKILL.md:38 passes a topic only,
against the contract at `recall/SKILL.md:24-33`). Correct here, since requirements
creates the artifact, but the skill does not say so, and `runbook/SKILL.md:57` passes
the plan-dir form.

**m3. A second `Skill(edify:recall)` call** (SKILL.md:105) against
`recall/SKILL.md:25-28`, which says a caller invokes it once and runs the loaded
procedure inline afterwards. `runbook/SKILL.md:71-72` has the identical pattern, so
this is a pipeline-wide divergence rather than unique to this skill.

**m4. "D+B" is never expanded** (SKILL.md:107). It appears at 14 sites across six
skills and at `docs/design.md:699`, which describes "the D+B fix" without defining it.

**m5. Descriptive where imperative is the house style**: SKILL.md:22 ("Skill
automatically detects appropriate mode…"), :157 ("/proof handles the iterative
validation loop"), and a full explanatory paragraph mid-procedure at :50.

**m6. The question budget is stated three times** (SKILL.md:130-132, :172, :294). The
values agree, so this is an edit-site count, not a contradiction.

**m7. "Target Model — Opus required" is unenforceable** (SKILL.md:12-14): skill
frontmatter carries no model field. Contrast `ground/SKILL.md:39-43`, which sets
model per delegated agent, where it binds.

**m8. The References example cannot be produced by this skill** (SKILL.md:210 offers
`plans/<job-name>/reports/explore-<topic>.md`, while :97-98 forbids agent delegation
and scout, which are what produce it). It can only cite one inherited from prior work.

**m9. "Standalone" is presented as an exit route** (SKILL.md:251, :281) alongside
`/design plans/<job>/`, but no skill or command by that name exists. It means "stop
here", which the parenthetical at :260 says plainly.

**m10. The description is a plain scalar** while sibling pipeline skills use the
block form. Cosmetic.

## What is sound

Description triggering is strong: four trigger phrases, the artifact produced, the
downstream consumers. One gap — SKILL.md:19 makes `<job-name>` required and :271
aborts without it, but the description never mentions it. The recall artifact
contract (:46-68) matches every consumer checked (`recall/SKILL.md:38-44`,
`runbook/SKILL.md:61-62`, `dispatch-composition.md:16`, `delegation.md:75`), and the
null-entry rule at :64 is a genuine design fix. Skill Dependency Scanning (:222-240)
has a real consumer at `write-outline.md:11` and `:25`. The `/proof <path>` form
matches the house convention.

## Measurements (`wc`)

`SKILL.md` 296 lines / 1727 words; `references/empirical-grounding.md` 63 / 348;
description 259 characters / 32 words.
