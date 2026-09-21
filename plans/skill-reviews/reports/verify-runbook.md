# Verification of `plans/skill-reviews/runbook.md` — 2026-09-21

Checked against the working tree: `plugin/skills/runbook/SKILL.md` (149 lines,
modified today) and `references/runbook-format.md` (138). Consumers checked:
`plugin/agents/runbook-corrector.md`, `plugin/skills/build/` (successor to
`skills/orchestrate/`), `plugin/skills/design/`,
`docs/references/pipeline-contracts.md`.
`plugin/fragments/continuation-passing.md` no longer exists.

Neither runbook file is on `scripts/check_line_limits.allow`; SKILL.md is 149
against a 200 cap, so additive fixes are affordable.

Review tally: 2 critical, 7 major, 8 minor = 17 findings. My table carries 17.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | fixed | `runbook-format.md:70-78` now specifies the general item shape with a worked example: "A general phase uses the base item shape with no `Slices:`" followed by a Phase 3 Documentation example. §Item-level rules (:118-138) now tags which rules bind on which type, including one `*(general)*` rule. The `inline` half of the finding is moot with the type. |
| C2 | Critical | moot | `type: inline` is abolished. `runbook/SKILL.md:32` declares "`type: tdd` or `type: general` (default)"; `runbook-format.md:14` shows `(type: tdd\|general)`; `docs/references/pipeline-contracts.md:116-121` records "the third type, `inline`, meant "the executor does this one itself" and was abolished with the `/build` merge (D-34)". The defect did **not** migrate: no token exists for `build/` to fail to read. This settles the README's decision 4 — inline phases are not real. |
| M3 | Major | open-mechanical | SKILL.md:26-28 still "**Prerequisites check (D+B anchor):** Check the plan directory for a design-stage artifact: `outline.md` or `design.md`. Absent → STOP" with no call named, while :55 and :70 both carry "tool call required" and name `Skill(edify:recall)`. `allowed-tools` (:7) is still `Bash(rg:*, git:*)` — no directory listing. |
| M4 | Major | open-design | The duplication and the drift both survive. SKILL.md:81-117 restates rules `runbook-format.md` owns (:92-93 vs format:41-47; :94-96 vs format:32-40; :113 vs format:131-133), and two still use different names for the same rule: SKILL.md:110 "**No vacuous items**" vs format:123 "**No setup-only items.**"; SKILL.md:113 "**Prose atomicity**" vs format:131 "**No split prose edits.**" The self-check still omits the assertion-quality table (format:87-96), integration-first (:100-103), wire-then-isolate (:104-106) and conformance validation (:110-116). Fork: make the self-check a pointer plus the rules the format file does not carry, or make the format file the only checklist. Structural, and m16 rides on the same decision. |
| M5 | Major | open-mechanical | SKILL.md:105-106 still "a phase over 8 items is a split signal" unmarked, and `runbook-corrector.md:82` still "A phase with >8 items is a phase-split signal" unmarked — while the corrector marks its neighbouring threshold at :85-86 (`>40% of total items` — *(ungrounded — needs calibration)*) and `design-content-rules.md:31-33` marks the identical `>8 items` figure ungrounded. |
| M6 | Major | open-mechanical | Still no assignment criterion. SKILL.md:30-44 lists only consequences (item format, review criteria, dispatch structure) plus what type does *not* decide. `pipeline-contracts.md:108-115` (D-30) likewise gives only consequences. The `inline` third of the original finding is moot; the tdd-vs-general criterion is stated only obliquely, at `design/SKILL.md:19-21` ("which phases are behavioural (tdd) and which are infrastructure or prose (general)"). |
| M7 | Major | open-mechanical | **The blocking half of this finding is wrong.** `allowed-tools` grants rather than restricts — that is the reviewer's own mechanism note in review C2, cited to an external doc and not verifiable from this repo, so treat it as unconfirmed either way. What *is* verifiable: SKILL.md:119-122 §4 Commit names no precommit run at all ("Commit `runbook.md` before review — review agents operate on filesystem state"), against the shared convention that the repo's precommit gate runs before every commit, and §Routing out (:146) names `/handoff:handoff` rather than a commit path. |
| M8 | Major | open-mechanical | SKILL.md:18 still "**Usage:** `/runbook plans/<job-name>/design.md`", while :26 speaks of "the plan directory", :27 accepts `outline.md` too, and every later step composes `plans/<job>/…`. The callers no longer name a form at all — `design/SKILL.md:284-285` and `route-to-execution.md:56` say only "commit the artifact and stop" — so the file-path usage line is the sole surviving claim and the outlier. |
| M9 | Major | open-mechanical | SKILL.md:141 still "Invoke `/proof plans/<job>/runbook.md`". `edify:proof`, `ddaa:proof` and `plugin:proof` all answer to the bare name. Same defect as proof M1; SKILL.md:56 already uses the unambiguous `Skill(skill: "edify:recall", …)` form. |
| m10 | Minor | open-mechanical | SKILL.md:3 still `description: \|` — a literal block scalar carrying embedded newlines. Every other skill uses `>-` or a plain scalar. |
| m11 | Minor | open-mechanical | The description (:4-6) still covers only "/runbook" and "a design needs step-by-step planning" — no "implementation plan", "break the design into steps", "plan the work", and no boundary clause, though `route-to-execution.md:31-35` now defines the adjacent case precisely (work with no runbook → `/build`). |
| m12 | Minor | open-mechanical | `requires:` and `outputs:` (SKILL.md:8-12) still appear on no other skill; both restate what :18-24 says in prose. |
| m13 | Minor | open-design | "D+B" is still unexpanded at SKILL.md:26, :55, :70, and no reference routes to its definition (`docs/references/quality-gates.md:76`, D-52). Repo-wide jargon — requirements m4 counts 14 sites across six skills — so expanding it in one skill is a partial fix. Fork: expand at every site, or route once from a shared fragment. |
| m14 | Minor | open-mechanical | Both schemes survive: `### 1.` through `### 7.` at :48-139, with substeps inside stage 1 numbered 0, 1, 2, 3, 4 (:50, :55, :60, :66, :70). "1." still denotes both the stage and a substep within it, and the substep list still opens at 0. |
| m15 | Minor | open-mechanical | SKILL.md:16 "# Write the Runbook" and :75 "### 2. Write the Runbook" — still identical. |
| m16 | Minor | open-design | §3 Self-Check (:81-117) is still twelve bullets of prose judgement with no opening tool call, the shape D-52 rules out and the rule this file invokes by name three times. Rides with M4's restructuring decision. |
| m17 | Minor | open-mechanical | The contradiction survives with different fields: `runbook-format.md:13-18` puts `Requirements:` on the item line and `Depends on: Item N.K` on its own, while the worked example at :66-67 inlines both ("Requirements: FR-3. Depends on: Item 2.1"). The `Model:` field named in the original finding is gone (:25-30 now forbids it). `runbook-corrector.md` still validates against this file. |

## Cross-file links

- M9 = proof M1 = the `/proof` call sites disposed in `verify-design.md`.
- M5 is the same class as design m1, deliverable-review M2, review m16.
- m13 = requirements m4 (the "D+B" expansion) — one decision covers both.
- M4/m16 are one restructuring; C1's fix already moved the general item format
  into the reference, which is the half that makes the restructure cheaper.

## Exact edits for `open-mechanical`

### `plugin/skills/runbook/SKILL.md`

**M3** — :26-28:

- old: `**Prerequisites check (D+B anchor):** Check the plan directory for a`
  `design-stage artifact: `outline.md` or `design.md`. Absent → STOP. `/runbook``
  `without prior `/design` gating is an error — scope was not user-validated.`
- new: `**Prerequisites check (D+B anchor — tool call required):**`
  `` `rg --files plans/<job>` `` `and branch on it: a design-stage artifact —`
  `` `outline.md` or `design.md` — must be listed. Absent → STOP. `/runbook` ``
  `without prior `/design` gating is an error — scope was not user-validated.`

**M5** — :105-106:

- old: `- **Phase size** — a phase over 8 items is a split signal: prefer splitting the`
  `  phase at a clean boundary. Not a count gate.`
- new: `- **Phase size** — a phase over 8 items is a split signal *(ungrounded — needs`
  `  calibration)*: prefer splitting at a clean boundary. Not a count gate.`

**M6** — insert after :32 (`Each phase declares … Type determines:`), before the
`- **Item format:**` bullet:

- new: `Assign the type by what the phase produces: a phase building or changing`
  `behaviour is `tdd`; infrastructure, configuration and prose work is `general`.`

**M7** — :119-122:

- old: `### 4. Commit`
  ``
  `` Commit `runbook.md` before review — review agents operate on filesystem state, ``
  `and a committed checkpoint keeps their fixes diffable.`
- new: `### 4. Commit`
  ``
  `` Run `just precommit`, then commit `runbook.md` before review — review agents ``
  `operate on filesystem state, and a committed checkpoint keeps their fixes`
  `diffable. Route the commit through `/commit-commands:commit`.`

**M8** — :18:

- old: `**Usage:** `/runbook plans/<job-name>/design.md``
- new: `**Usage:** `/runbook plans/<job-name>``

**M9** — :141 (also listed in `verify-proof.md`):

- old: `` Invoke `/proof plans/<job>/runbook.md` — the user validates the runbook item by ``
- new: `` Invoke `/edify:proof plans/<job>/runbook.md` — the user validates the runbook ``

**m10** — :3:

- old: `description: |`
- new: `description: >-`

**m11** — :4-6, replacing the description body:

- old: `  Decompose a design into an executable runbook — phases of typed items`
  `  (tdd / general) that /build composes dispatch prompts from.`
  `  Triggers on /runbook or when a design needs step-by-step planning.`
- new: `  Decompose a design into an executable runbook — phases of typed items`
  `  (tdd / general) that /build composes dispatch prompts from. Triggers on`
  `  /runbook, "implementation plan", "break the design into steps", "plan the`
  `  work", or when a design needs step-by-step decomposition. Not for work that`
  `  needs no runbook — that goes straight to /build.`

**m12** — delete :8-12 (`requires:` and `outputs:` and their list items).

**m14** — renumber the substeps of stage 1 (:50, :55, :60, :66, :70) from
`0.`-`4.` to `a.`-`e.`, and update the two inbound references
(`design/references/...` carries none; SKILL.md:58 "Upstream triage recall" and
:70 "step 1 did not anticipate" both survive unchanged).

**m15** — :16:

- old: `# Write the Runbook`
- new: `# Decompose a Design into a Runbook`

### `plugin/agents/runbook-corrector.md` — not allowlisted

**M5**, second site, :82:

- old: `- A phase with >8 items is a phase-split signal: propose the split point, apply`
- new: `- A phase with >8 items is a phase-split signal *(ungrounded — needs`
  `  calibration)*: propose the split point, apply`

### `plugin/skills/runbook/references/runbook-format.md`

**m17** — :66-67, make the example match the spec:

- old: `- Item 2.2: src/edify/cli.py — wire parse_entries() into `edify extract`.`
  `  Requirements: FR-3. Depends on: Item 2.1`
- new: `- Item 2.2: src/edify/cli.py — wire parse_entries() into `edify extract`.`
  `  Requirements: FR-3.`
  `  Depends on: Item 2.1`
  (Or amend :17-18 to permit inlining. Pick one; the corrector validates against
  this file, so the two must agree.)
