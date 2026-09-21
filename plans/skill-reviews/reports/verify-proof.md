# Verification of `plans/skill-reviews/proof.md` — 2026-09-21

Checked against the working tree: `plugin/skills/proof/SKILL.md` (203 lines) and
`references/item-review.md` (100 lines); neither is modified today. Caller sites
checked in the working-tree copies of `design/SKILL.md`,
`design/references/write-outline.md`, `write-design.md`, `runbook/SKILL.md`,
`requirements/SKILL.md`.

**Line budget:** `plugin/skills/proof/SKILL.md` is on
`scripts/check_line_limits.allow` at ceiling **203** and measures exactly 203
lines. Any edit to it must be net-zero or shrinking, or the gate goes red.

Review tally: 2 critical, 9 major, 6 minor = 17 findings. My table carries 17.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | open-design | Terminal "apply" (SKILL.md:170-176) is still four steps with no corrector dispatch, and `Agent` is still in `allowed-tools` (:8) with no dispatch anywhere in the body. Three callers still assert it: `design/SKILL.md:214-215` and `:232-233` ("outline-corrector dispatched by /proof on revise/kill"), `write-outline.md:224-226` ("On terminal action "apply", /proof dispatches outline-corrector automatically"), `write-design.md:76-78` ("On terminal action "apply", /proof dispatches design-corrector automatically"). The fourth caller (`write-inline-plan.md`) no longer exists. Trigger disagreement (revise/kill vs apply) is also unchanged. Fork: implement the apply-time dispatch, or strip the claim from the three callers — the choice decides whether the T6 and T1 gates (`docs/references/pipeline-contracts.md:59,:64`) fire on the Moderate non-prose and resumed-design paths. |
| C2 | Critical | open-mechanical | SKILL.md:57 and :66 still advertise `feedback, proceed, learn, suspend, sync`. A grep of the file finds `feedback` only at :141 (as a noun in "Restate user feedback") and `suspend` nowhere; `proceed` exists only as the orientation checkpoint's "proceed as-is" (:102). Real and unadvertised: `apply`, `discard`, `revisit`, `pending`, `brief`. Fix is net-zero (see edits). Pending job (3) may rewrite the whole line; this edit does not conflict with it. |
| M1 | Major | open-mechanical | Every call site still uses the bare form: `design/SKILL.md:214`, `:232`; `write-outline.md:223`; `write-design.md:76`; `requirements/SKILL.md:194`; `runbook/SKILL.md:141`. `edify:proof`, `ddaa:proof` and `plugin:proof` all answer to "proof" in this environment's skill list. |
| M2 | Major | open-mechanical | SKILL.md:4 still opens "This skill should be used when an artifact needs structured user validation." Every other edify skill opens with what it does. |
| M3 | Major | open-mechanical | SKILL.md:85-87 still "If the artifact path contains a glob pattern (e.g., `section-*.md`), expand via `rg --files` (Bash)". Bare `rg --files` takes a path; the pattern form needs `-g`. |
| M4 | Major | open-mechanical | SKILL.md:120 still `Skill(skill: "edify:recall", args: "<that item's topic>")`, against the contract at `recall/SKILL.md:25` (`"<plan-dir> — <topic>"`) whose step 1 (:38-44) resolves the plan artifact. |
| M5 | Major | open-mechanical | Half applied: the guard at SKILL.md:153-154 now reads "Refuse execution-oriented requests (file edits, skill chains to other skills or external plugins)" — the "execution-oriented" framing the reviewer asked for is there, but the parenthetical still forbids exactly what :157-160 permits (`learn`, `pending` → handoff plugin, `brief` → `ddaa:brief`). |
| M6 | Major | open-mechanical | SKILL.md:187 still heads Loop Actions "Available during and after item iteration"; :203 still "Revisit is post-completion only"; `item-review.md:92` still "After completing iteration through all items". |
| M7 | Major | fixed | `allowed-tools` (SKILL.md:8) is `Read, Write, Edit, Bash, Agent, Skill` — `AskUserQuestion` is gone, and the file names it nowhere. |
| M8 | Major | open-design | `p:` is still cited twice and defined nowhere: a grep across `plugin/` and `docs/` returns only `SKILL.md:159` and `item-review.md:84`. I could not establish what mechanism `p:` names, so proposing a definition would be confabulation. Fork: establish the handoff plugin's actual capture syntax and cite it, or drop the token and say "capture task for handoff". |
| M9 | Major | open-design | `agents/learnings.md` is still the write target at SKILL.md:158 and `item-review.md:83`, with no absence handling. It exists in this checkout (195 lines) and nothing guarantees it in a consuming repo. Fork: where a consumer's learnings land — the same question `ground` finding 13 raises about citing that file at all. |
| m1 | Minor | open-mechanical | SKILL.md:118 still "**Per-item recall (FR-3):**". No `plans/proof*` directory holds a requirements document defining FR-3. |
| m2 | Minor | open-mechanical | The emission table (:55-61) still has no row for a recorded per-item verdict — the most frequent transition. "After accumulate" (:58) is the discussion-round case. A net-zero reword of that row covers it. |
| m3 | Minor | open-mechanical | Entry (:83-87) and Orientation (:95-102) still never mention the state line; only :38 does, generically. Net-zero fix available on the Checkpoint bullet. |
| m4 | Minor | open-mechanical | SKILL.md:162-166 still repeats the emission table's post-sync row inside the loop-actions block. Deleting it frees five lines, which is what pays for any additive fix elsewhere in this file. |
| m5 | Minor | open-mechanical | `item-review.md:62` still "**Kill sub-actions (planning artifacts only):** Per verdict semantics in SKILL.md", while :64-73 re-lists all five verdict cases under Batch-Apply Execution. SKILL.md:124-130 is the definition. |
| m6 | Minor | open-mechanical | Revisit is still documented twice at similar depth: SKILL.md:189-191 and `item-review.md:90-100`, with identifier flexibility and the post-iteration return in both. |

Uncounted in the tally: the reviewer's closing "**Fragments:**" paragraph (no
proof file reads anything under `plugin/fragments/`). Still true — a grep for
`fragments/` in both files returns nothing. Treat as an observation, not a
finding; `token-economy.md`'s do-not-repeat rule is what m4/m5/m6 violate.

## Cross-file links

- C1 is the same defect as design C2 and is disposed there too; one fix closes
  both. `verify-design.md` carries the caller-side detail.
- M1 is the same defect as runbook M9 and design's bare-`/proof` sites.
- M4 is the caller half of recall's §Invocation contract; see `verify-recall.md`.
- M7 closes with formalize 3, requirements C2 and review C1.
- M9 pairs with ground finding 13 (`agents/learnings.md` staleness).

## Exact edits for `open-mechanical`

### `plugin/skills/proof/SKILL.md` — net-zero required

**C2**, two sites, same replacement text:

- :57 old: `| Entry (after summary) | `reviewing` | Full: `feedback, proceed, learn, suspend, sync` |`
  new: `| Entry (after summary) | `reviewing` | Full: `proceed, sync, learn, pending, brief` |`
- :66 old: `[proof: reviewing outline.md | decisions: 0 | actions: feedback, proceed, learn, suspend, sync]`
  new: `[proof: reviewing outline.md | decisions: 0 | actions: proceed, sync, learn, pending, brief]`

**M1** — SKILL.md itself needs no change; the six caller sites do:

- `design/SKILL.md:214` `  4. **Proof:** Invoke `/proof plans/<job>/outline.md` (outline-corrector`
  → `  4. **Proof:** Invoke `/edify:proof plans/<job>/outline.md` (outline-corrector`
- `design/SKILL.md:232` same substitution
- `write-outline.md:223` `**Protocol:** Invoke `/proof plans/<job>/outline.md` — structured`
  → `**Protocol:** Invoke `/edify:proof plans/<job>/outline.md` — structured`
- `write-design.md:76` `Invoke `/proof plans/<job-name>/design.md` — structured validation loop on the`
  → `Invoke `/edify:proof plans/<job-name>/design.md` — structured validation loop`
- `requirements/SKILL.md:194` `Invoke `/proof plans/<job>/requirements.md` — structured reword-accumulate-sync`
  → `Invoke `/edify:proof plans/<job>/requirements.md` — structured`
- `runbook/SKILL.md:141` `Invoke `/proof plans/<job>/runbook.md` — the user validates the runbook item by`
  → `Invoke `/edify:proof plans/<job>/runbook.md` — the user validates the runbook`

`design/SKILL.md` (285 = ceiling) and `requirements/SKILL.md` (357 = ceiling)
are both at their ceilings, so each substitution must be re-wrapped in place;
run the 80-column reflow and re-count before committing, since a wrap that
spills adds a line and turns the gate red.

**M2** — :4-5:

- old: `  This skill should be used when an artifact needs structured user`
  `  validation. Triggers on "proof", "validate artifact", "review loop", or`
- new: `  Validate an artifact item by item with the user, forcing a verdict per`
  `  item. Triggers on "proof", "validate artifact", "review loop", or`

**M3** — :86:

- old: `(e.g., `section-*.md`), expand via `rg --files` (Bash) and read all matching`
- new: `(e.g., `section-*.md`), expand via `rg --files -g '<pattern>' <dir>` (Bash) and read`

**M4** — :120:

- old: `` `Skill(skill: "edify:recall", args: "<that item's topic>")`; every later item ``
- new: `` `Skill(skill: "edify:recall", args: "<plan-dir> — <item topic>")`; later items ``

**M5** — :153-154:

- old: `**No direct edits during iteration.** Refuse execution-oriented requests (file`
  `edits, skill chains to other skills or external plugins). This gate prevents`
- new: `**No direct edits during iteration.** Refuse execution-oriented requests (file`
  `edits, execution or planning skill chains) — `learn`, `pending` and `brief``
  `below are the named exceptions. This gate prevents`
  (net +1; pay for it by deleting one of m4's five lines)

**M6** — :187:

- old: `Available during and after item iteration (non-terminal — resume review after):`
- new: `Available after item iteration completes (non-terminal — resume review after):`

**m1** — :118:

- old: `**Per-item recall (FR-3):** Before presenting each item, run recall for that`
- new: `**Per-item recall:** Before presenting each item, run recall for that`

**m2** — :58:

- old: `| After accumulate | `reviewing` | Compact: omit actions (user has seen them) |`
- new: `| After a verdict or accumulate | `reviewing` | Compact: omit actions |`

**m3** — :101:

- old: `- **Checkpoint:** Wait for user response before first item. User may: reorder`
- new: `- **Checkpoint:** Emit the entry state line, then wait for a response. May: reorder`

**m4** — delete :162-166 entirely (the `**Emit state line** after showing
decisions:` line, its blank lines and the three-line fenced block). Frees five
lines, which funds M5's +1 and leaves four in hand.

### `plugin/skills/proof/references/item-review.md` — not allowlisted

**m5** — delete the duplicated verdict list at :64-73 and replace the section
body with a pointer:

- old (§Batch-Apply Execution body, :66-73): the six-bullet verdict list
- new: `On terminal action "apply" after user confirms the verdict summary, apply`
  `each accumulated verdict per §Verdicts in SKILL.md — approve and skip need no`
  `edit, revise applies the stated fix, kill deletes or absorbs.`

**m6** — delete the §Revisit section (:90-100) and leave SKILL.md:189-191 as the
single definition; or, if the detail belongs in the reference, cut
SKILL.md:189-191 to a one-line pointer instead. Either direction is net-negative
overall; pick the reference as the home for detail, matching the file's own
framing at :3-5.
