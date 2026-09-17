# Inventory: `/inline` + `/orchestrate` → `/build` merge

Verified 2026-09-16. Every line cite below was read directly (grep -n or full
Read) at that path; none is inferred. `.git/` and `plans/skill-reviews/`
excluded per instructions. `__pycache__/` excluded: it is gitignored and
contains stale `.pyc` for dozens of tests with no tracked `.py` source (a
leftover from another checkout) — irrelevant to this merge.

## 0. Corrections from the 2026-09-17 proof pass

The proof of the merge plan re-read every claim below against source. Six
were wrong; all are corrected **in place** above rather than appended, so
this document stays usable as the grounding record. Listed here so a reader
knows which way the errors ran.

- **`write-outline.md` had seven sites, not four.** Missing were 209 (the
  prose hard gate, `→ INLINE`), 217 (the `**Inline criteria**` heading) and
  224 (`Inline execution bypasses /runbook`). The hard gate is the first
  routing branch in the file.
- **`delegation.md` line numbers drifted** — 28→33, 75→80. The count (one
  framing sentence, three hardcoded `dispatch-composition.md` paths) was
  right.
- **`runbook-format.md` drifted in text, not only in line number** — 35→38,
  and the line-25 quote (`` `Model:` — optional ``) is text that no longer
  exists; the file now says an item does not carry a model. The drift is
  from this session's own D-42 edits, so a cite verified on 2026-09-16 could
  already be stale by the time the plan was written.
- **`runbook-format.md` does specify the general item format.** §Structure's
  base item shape *is* it, and `### tdd items: Slices` adds `Slices:` on
  top. The plan asserted the opposite and attributed it to "inventory C1" —
  **there is no C1 in this document** (sections are 1–9 plus 2b) and no
  section of it makes that claim. The real gap is signposting: no phase is
  headed `(type: general)`, and the tdd-only sections are unlabelled.
- **`plans/skill-reviews/` was excluded per instructions**, as stated above —
  not an oversight. But the merge plan's frozen-plans list inherited the
  omission and also missed `plans/dispatch-model-precedence/` and
  `plans/prototypes/`. Measured 2026-09-17: **380 stale-name hits across 9
  directories under `plans/`**, all out of scope as frozen records.
- **A report claim cited during the proof was itself stale.**
  `plans/skill-reviews/review-skills.md:73` records
  `runbook/SKILL.md:30` accepting `inline-plan.md` as a runbook
  prerequisite; read against source, the line names only `outline.md` or
  `design.md`. Fixed some time before this pass.

## 1. Skill-body content

### `plugin/skills/inline/` (174-line SKILL.md + 82-line reference)

- `SKILL.md` frontmatter (1-11): name, description, `allowed-tools: Agent,
  Read, Write, Edit, Bash, Skill`, `continuation.default-exit`.
- Entry Points table + cold-start-vs-`execute` token apparatus (20-31) —
  **abolished per task decisions** (single entry point once `/design` no
  longer implements inline itself).
- Phase 1 Entry Gate (33-58): dirty-tree STOP, `just precommit` STOP,
  baseline capture to `tmp/inline-baseline` — **must move into `/build`**
  (currently the only entry gate between the two skills).
- Phase 2 Pre-Work (60-76): brief check, recall, reference loading — cold-start
  only, skipped when chained from `/design`.
- Phase 3 Execute (78-98): direct vs delegated execution; delegated path cites
  `plugin/skills/orchestrate/references/dispatch-composition.md` (88) — i.e.
  inline already depends on orchestrate's dispatch-composition reference.
- Phase 4 Post-Work (100-168): 4a Review Gate (full routing-table dispatch,
  Path A/B), 4b Triage Feedback (`triage-feedback.sh`), 4c Deliverable-Review
  Handoff — **must move into `/build`** (orchestrate has no review/triage
  phase of its own; see §Overlap).
- Continuation (170-174) — near-identical to orchestrate's, see §Overlap.

- `references/review-dispatch-template.md` (82 lines) — reviewer-dispatch
  prompt template + field rules + worked example. Entirely inline-specific;
  no orchestrate equivalent. References `/inline` by name (3, 42) and
  `tmp/inline-baseline` (42) — both need rewriting for `/build`.

### `plugin/skills/orchestrate/` (202-line SKILL.md + 79-line reference + 32-line script)

- `SKILL.md` frontmatter (1-9): name, description ("Triggers on /orchestrate
  or when /runbook hands off"), `allowed-tools: Agent, Read, Write, Edit,
  Bash, Skill, SendMessage, TaskOutput, TaskStop` — **wider tool set than
  inline's** (adds `SendMessage`, `TaskOutput`, `TaskStop` for resume/escalate).
- §1 Load the Runbook (21-32): `Read plans/<job>/runbook.md` with no
  preflight — **must relax** per task decision (fall back to design.md/
  outline.md, else ad-hoc task). STRICT SEQUENTIAL execution-mode rule (31-32).
- §2 Execute Items (34-108): 2.1 Inline Items (38-49, **the live phase-type
  `inline` consumer** — see §3 below), 2.2 General Items (50-54), 2.3 TDD
  Items (56-108, four-dispatch slice protocol: RED/test-review/GREEN/code-review,
  refactor dispatch, list revision).
- §3 Post-Item Verification (110-129): `verify-step.sh`, exit-code taxonomy
  (0/1/2), remediation/escalation.
- §4 Phase Boundary (131-148): checkpoint corrector, IN/OUT non-empty gate,
  final-checkpoint stateful-object audit.
- §5 Escalation Rules (150-171): 2-level model, five named triggers.
- §6 Completion (173-188): final review, TDD audit, run summary.
- Continuation (190-195) — near-identical to inline's.
- §References (197-203): points at `dispatch-composition.md`,
  `verify-step.sh`, `delegation.md`, `continuation-passing.md`.

- `references/dispatch-composition.md` (79 lines) — single source for
  composing any dispatch prompt (prompt contents, model assignment,
  naming/resumption, agent-behaviour contract). Already shared infra: inline
  Phase 3 (88) points at it rather than restating it. Line 4 explicitly names
  `/inline`'s delegated path as a second caller: `"from an ad-hoc task in
  `/inline`'s delegated path"`. Lines 53/55 state the `Model:`-line-wins
  precedence that `inbox/brief-dispatch-model-precedence.md` (still open, see
  §7) says must change to be outranked by two new rules.
- `scripts/verify-step.sh` (32 lines) — clean-tree + precommit gate, no
  phase-type or skill-name string inside it (confirmed by grep, zero hits).
  Referenced by hardcoded path from four other files (§7).

## 2. Inbound references (real hits — literal `/inline`, `/orchestrate`,
`edify:inline`, `edify:orchestrate`, `skills/inline`, `skills/orchestrate`, or
routing prose to either; false positives from generic English "inline"/
"orchestrator" are listed separately in §2b)

| File | Line | Text |
|---|---|---|
| `plugin/README.md` | 4 | `built around a \`requirements → design → runbook → orchestrate\` planning and` |
| `plugin/README.md` | 27 | `\| \`/design\` \| Triage complexity, then design the approach; routes simple work straight to \`/inline\` \|` |
| `plugin/README.md` | 28 | `\| \`/runbook\` \| Decompose a design into a runbook of typed items (tdd slices, general, inline) \|` |
| `plugin/README.md` | 29 | `\| \`/orchestrate\` \| Execute a runbook by composing dispatch prompts per item, with verification gates \|` |
| `plugin/README.md` | 30 | `\| \`/inline\` \| Sequence inline execution — pre-work, execute, post-work — for work without a runbook \|` |
| `plugin/README.md` | 72-73 | `Plus \`skills/orchestrate/scripts/verify-step.sh\`, the clean-tree and precommit` / `gate \`/orchestrate\` runs after each committing dispatch — GREEN, code review` |
| `plugin/agents/corrector.md` | 313 | `` `/orchestrate` dispatches this agent twice per TDD slice. The prompt names `` |
| `plugin/fragments/continuation-passing.md` | 13,15,16,57,62,66,70,82,100,101,131,132,133,145,146,148 | 16 literal `/inline`/`/orchestrate` citations forming the continuation-chain examples and the default-exit table rows (e.g. line 100: `` \| `/inline` \| `["/handoff:handoff", "/commit-commands:commit"]` \| Inline execution lifecycle (no runbook) \| ``; line 101 the `/orchestrate` row). Full file is continuation-protocol reference material for both skills — needs a single merged row/example set. |
| `plugin/fragments/delegation.md` | 3 | `` When executing runbooks via `/orchestrate`, the orchestrator coordinates but does not implement: `` |
| `plugin/fragments/delegation.md` | 11 | `` `plugin/skills/orchestrate/references/dispatch-composition.md` §Model assignment `` |
| `plugin/fragments/delegation.md` | 33 | `The dispatcher composes each prompt per \`plugin/skills/orchestrate/references/dispatch-composition.md\`: item text inline, design and recall artifact by path...` |
| `plugin/fragments/delegation.md` | 80 | `` ...`plugin/skills/orchestrate/references/dispatch-composition.md` §Prompt contents is the authoritative rule. `` |
| `plugin/fragments/workflows-terminology.md` | 22 | `` \| **Runbook** \| Phased implementation plan `/orchestrate` dispatches from (previously called "plan") \| `` |
| `plugin/fragments/workflows-terminology.md` | 23 | `` \| **Phase type** \| `tdd`, `general` or `inline` — determines item format, review criteria and dispatch for that phase \| `` (also §3 phase-type) |
| `plugin/skills/design/SKILL.md` | 21 | `` - **Planning:** `/runbook` — phases typed tdd / general / inline. Note which phases are behavioural (tdd), infrastructure (general), or prose/config the orchestrator applies itself (inline) to guide per-phase typing. `` |
| `plugin/skills/design/SKILL.md` | 22 | `` - **Execution:** `/inline` when work is execution-ready (Phase B sufficiency gate, Phase C.5 execution readiness). Handles execution lifecycle: corrector, triage feedback, deliverable-review chain. `` |
| `plugin/skills/design/SKILL.md` | 133,137,143-145,185 | Simple-route steps: `chain to \`/inline\``, `Read \`references/write-inline-plan.md\`. **Generate** \`plans/<job>/inline-plan.md\``, `Invoke \`/proof plans/<job>/inline-plan.md\``, `prepend \`/inline plans/<job> execute\`` (x2) |
| `plugin/skills/design/references/write-design.md` | 88 | `` - **If execution-ready:** Follow §Continuation (prepends `/inline plans/<job> execute`). `` |
| `plugin/skills/design/references/write-inline-plan.md` | 3,25,31,32 | Whole file is the `inline-plan.md` format reference for the Simple/Moderate agentic-prose route: `` Reference for `plans/<job>/inline-plan.md` — execution plan for direct inline implementation... ``; `/proof` corrector-dispatch table row `inline-plan.md → -- (no corrector)`; status transition `` `inline-planned` → `/inline plans/{plan}` (parallel to `planned` → `/orchestrate`) ``. |
| `plugin/skills/design/references/write-outline.md` | 209,210,211,217,222,224,226 | Execution-routing block and its criteria: `` IF all prose edits, no implementation loops → INLINE (hard gate — file count irrelevant) `` (the prose hard gate — the first routing branch, and the one §Prose path rationale exists to defend); `` ELSE IF work type = Investigation → inline (criteria below) ``; `` ELSE IF work type = Exploration AND design resolved all questions → inline (criteria below) ``; `` **Inline criteria (non-prose paths only — prose path bypasses these):** ``; `Scope fits inline capacity (single session, single model)`; `` Inline execution bypasses `/runbook` — this gate assesses coordination complexity and capacity. ``; `` follow §Continuation (prepends `/inline plans/<job> execute`). `` |
| `plugin/skills/requirements/SKILL.md` | 266 | `` - Very clear scope + simple → `/design plans/<job>/` (its triage routes small work to `/inline`) `` |
| `plugin/skills/review/SKILL.md` | 200 | `` 3. `/orchestrate` — Executes runbook `` |
| `plugin/skills/runbook/SKILL.md` | 5,26,37,40-41,45,149,151 | `` (tdd / general / inline) that /orchestrate composes dispatch prompts from. ``; `` `runbook-corrector` → `runbook-simplifier` → `/proof` → `/orchestrate` in a ``; `` `type: inline`. Type determines: ``; `` concrete action against a named target; inline → same, executed by the / orchestrator itself. ``; `` code review); general → one dispatch; inline → no dispatch. ``; `` Propagation. No prepend: orchestration runs in a fresh session via ``; `` budget, and the orchestrator needs its own. `` |
| `plugin/skills/runbook/references/runbook-format.md` | 5,14,25,38 | `` `/proof` validates it, and `/orchestrate` reads it and composes each dispatch ``; `` ## Phase N: <title> (type: tdd|general|inline) `` (the phase-type header format itself); line 25 is now `` the dispatch itself (`dispatch-composition.md` §Model assignment) `` — a bare filename that does not resolve from `runbook/references/`, replacing the `` `Model:` — optional `` text this inventory quoted; `` id `/orchestrate` uses in dispatch names and slice commit subjects. `` |
| `docs/design.md` | 16,24,26,59,61,62,138-139,144,149-150,157,160,163-164,177,183,398,400,412,414,417,430,440,447,451-452,465,473-474,491,493,497-498,502,509,541,544,546-547,549-553,569,583,591,605,629,963,965-966,968,973,988,1053 | See §3 — D-30, D-34, D-37 own the phase-type/route decisions; FR-8/FR-10/FR-11 map requirements to `skills/design/`, `skills/orchestrate/`, `skills/inline/` paths (59,61,62). Full list of 58 grep hits verified; most are the generic-role word "orchestrator" describing the dispatching skill (see §2b), but the FR table and D-30/D-34/D-37 decision text are literal and load-bearing. |
| `docs/changelog.md` | 33-36,44,60,84,93,153,155 | Historical changelog entries describing the 2026-09-01 one-stage-runbook landing and the weak-orchestrator retirement — literal `/orchestrate` at 44 (`` gate it, `/proof` validates it, and `/orchestrate` composes every dispatch ``), rest is "orchestrator"/"orchestration" as role word describing that same landed change. Dated entries — see §8 on whether changelog entries get edited retroactively. |
| `CLAUDE.md` (project root) | 183 | `` - **Workflow pipeline:** `requirements` → `design` → `runbook` → `orchestrate`, or `design` → `inline` for work that needs no runbook, with `review` as the in-progress quality gate. `` |
| `CLAUDE.md` (project root) | 192-193 | `` Execution delegates **by reference**: the orchestrator composes each dispatch / prompt from the runbook item (`plugin/skills/orchestrate/references/dispatch-composition.md`) `` |
| `README.md` (project root) | 41-42 | `` - **Pipeline** — `/requirements` → `/design` → `/runbook` → `/orchestrate` / (or `/design` → `/inline` for work that needs no runbook), with `/review` `` |
| `.claude/handoff-todo.md` | 4 | `` Fix /inline's report-only reviewer flow: `plugin-dev:skill-reviewer` has Read/Grep/Glob only, yet `review-dispatch-template.md` tells it to fix issues and write the report... `` — **live open defect against the exact files this merge touches.** |
| `inbox/brief-dispatch-model-precedence.md` | 5,27,59,60-61 | Live, uncommitted brief. Names `plugin/skills/orchestrate/references/dispatch-composition.md` (27,59) and `` `plugin/skills/inline/SKILL.md` references model assignment too; check whether it restates the ordering or defers. `` (60-61) — an **open task that presupposes the current file paths**; must be reconciled with the merge (either land first, or the merge updates its target paths). |
| `agents/learnings.md` | 21,22,49,70-72,76,103,130,144,146,153-156 | Historical learnings log entries naming `/inline`, `/orchestrate`, "inline skill", "orchestrator" — see §8 (judgment call on whether a learnings log is edited retroactively). |
| `plans/README.md` | 23,27,52-53 | `` `plans/<name>/orchestrator-plan.md` (orchestrator instructions) ``; `Use \`/orchestrate\` skill for runbook execution`; `` `orchestrator-plan.md   # Generated by prepare-runbook.py` `` — **note:** `prepare-runbook.py` has no tracked source under `plugin/bin/` (only a stale `__pycache__` entry), so this reference was already stale before this merge; out of scope but flagged. |
| `memory/ddaanet/cc-bash-background-no-duration-cap.md` | 26 | `test-driver dispatches in one orchestrate run each launched the gate in the` — generic role word, not a literal skill-name dependency. |
| `memory/strategic-pivot.md` | 21,31 | `` The `design→runbook→orchestrate` pipeline... `` (x2) — historical memory fact describing pipeline lineage; see §8. |
| `docs/superpowers/design/plugin-transition-evaluation.md` | 260,273,277,343,393 | Pre-existing historical design doc (last touched 2026-08-14, predates current file shapes); line 260 literally: `` It still cites the torn-down pipeline: "/inline or /orchestrate `` — this doc already describes an **earlier, torn-down** pipeline, not the current one. Out of scope (§8). |
| `docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md` | 11,56,80,114 | Historical spec; line 11 lists `orchestrate` among then-current skill names. Out of scope (§8). |
| `docs/superpowers/specs/2026-06-08-invariant-guided-verify-loop-design.md` | 136 | `intent, orchestrates the loop...` — generic verb, unrelated to the skill. |
| `docs/superpowers/plans/2026-06-08-edify-check-verify-loop.md` | 14 | `orchestrates the loop and asks the user when intent is ambiguous.` — generic verb, unrelated. |

## 2b. False positives (grep matched, not a real skill-name reference)

Generic English usage of "inline" (= "embedded in the prompt/text", "in the
current context") or "orchestrator"/"orchestrate" (= the general dispatching
role, applicable to whichever skill currently plays it) that do **not** name
`/inline` or `/orchestrate` literally:

- `plugin/agents/artisan.md:19`, `plugin/agents/test-driver.md:18` — "task
  text inline" / "slice text inline" (prompt-composition idiom).
- `plugin/agents/design-corrector.md:249`, `outline-corrector.md:36,338,353`
  — "requirements … inline" (embedded vs. separate file).
- `plugin/agents/corrector.md:181,368,573`, `refactor.md` (10 lines),
  `runbook-simplifier.md:165`, `tdd-auditor.md` (5 lines) — "the
  orchestrator" as generic role word for whichever skill dispatched the agent.
- `plugin/fragments/error-classification.md:47,93,103,107`,
  `escalation-acceptance.md:29,53`, `execution-routing.md:9,11`,
  `prerequisite-validation.md:6,24,260`, `review-requirement.md:95,134,166`
  — same generic "orchestrator"/"orchestration" role usage.
- `plugin/skills/formalize/SKILL.md:33`, `proof/SKILL.md:24,100,156`,
  `recall/SKILL.md:29`, `requirements/SKILL.md:57,134,177`,
  `review/SKILL.md:31,190`, `design/references/design-content-rules.md:78`,
  `write-design.md:84`, `write-outline.md:15,53,62`,
  `runbook/SKILL.md:129` — "ask inline", "runs inline", "rely on inline
  summaries" — all the generic sense.
- `src/edify/markdown_inline_fixes.py`, `markdown_block_fixes.py`,
  `markdown_list_fixes.py`, and every `tests/test_markdown_*.py` hit —
  "inline code span" (CommonMark backtick spans). Confirmed by direct read of
  matched lines; zero relation to the `/inline` skill.

## 3. Phase-type `inline`

Definition and every consumer, verified by direct read:

- **Definition:** `plugin/skills/runbook/references/runbook-format.md:14` —
  `` ## Phase N: <title> (type: tdd|general|inline) `` — the phase-type header
  format itself.
- **Consumer (the only live executable branch):** `plugin/skills/orchestrate/SKILL.md:38-49`
  §2.1 "Inline Items" — `` The orchestrator executes the item itself — Read
  targets, apply edits, `just precommit`, commit. No dispatch. `` Per the
  task's decision, phase types become `tdd`/`general` only, and the
  direct-vs-delegated choice becomes a live dispatch-time decision — this
  section is the one place that decision currently lives in prose.
- **Documentation:** `plugin/skills/runbook/SKILL.md:37,40-41,45`;
  `plugin/fragments/workflows-terminology.md:23`;
  `plugin/skills/design/SKILL.md:21`.
- **Design record:** `docs/design.md` D-30 (line 491: `` **D-30 — Phases
  declare a type: `tdd`, `general` (default), or `inline`.** ``, through 509),
  D-34 (541-553, the `/inline`-vs-`/orchestrate` route split, explicitly
  notes the inline-item type "survives inside `/inline`" wording that predates
  this merge), D-37 (569, "Simple classification still routes through
  `/inline`").
- **Script/test parsing:** none found. `verify-step.sh` has zero
  inline/orchestrate/phase-type string matches (confirmed by grep). No
  `tests/*.py` parses a `type:` token — grep of `tests/` for phase-type
  syntax returns nothing (the test suite covers `edify-cli`, not the
  markdown-based skill/runbook format at all — there is no runbook-format
  parser in this repo's tracked source; `test_validate_runbook*.py` and
  `test_prepare_runbook_*.py` exist only as stale `__pycache__` with no
  tracked `.py`, per the note at the top of this file).

## 4. Baseline/state files (`tmp/inline-baseline`)

Repo-wide search for `inline-baseline` (zero hits outside these two files):

| File | Line | Text |
|---|---|---|
| `plugin/skills/inline/SKILL.md` | 52 | `` mkdir -p tmp && git rev-parse HEAD > tmp/inline-baseline `` |
| `plugin/skills/inline/SKILL.md` | 56-58 | `` A file, not a shell variable... Phases 4a and 4b read it back with / `$(cat tmp/inline-baseline)`. `` |
| `plugin/skills/inline/SKILL.md` | 111 | `` 1. List changed files: `git diff --name-only "$(cat tmp/inline-baseline)"` `` |
| `plugin/skills/inline/SKILL.md` | 157 | `` plugin/bin/triage-feedback.sh <job> "$(cat tmp/inline-baseline)" `` |
| `plugin/skills/inline/references/review-dispatch-template.md` | 42 | `` **Baseline:** substitute the hash itself, read back from `tmp/inline-baseline` (written at /inline Phase 1 by `git rev-parse HEAD` before edits)... `` |

`plugin/bin/triage-feedback.sh` itself (read in full) takes a generic
`<job-dir> <baseline-commit>` positional pair — it contains no `inline`
string and needs no change; only its five callers above do.
`tmp/` is gitignored (confirmed in `plugin/skills/inline/SKILL.md:56`), so no
tracked fixture or `.gitignore` entry references the literal filename.

## 5. Manifest/registration

**None found.** Checked and read in full:

- `plugin/.claude-plugin/plugin.json` — name/version/description/author/repo/
  license only; no skill enumeration (skills are auto-discovered from
  `plugin/skills/*/SKILL.md`, so no manifest edit is needed to register
  `/build` or remove `/inline`/`/orchestrate`).
- `plugin/hooks/hooks.json` — one `SessionStart` hook (venv bootstrap); no
  skill name.
- `plugin/.claude/settings.json`, `.claude/settings.json`,
  `.claude/settings.local.json` — permissions/sandbox config; grepped, zero
  `inline`/`orchestrat` hits.
- Root `justfile`, `plugin/justfile`, `plugin/portable.just` — grepped, zero
  hits.
- Every tracked `*.json` under the repo root and `plugin/` was enumerated;
  the only ones with any content are the four above. (`package.json`,
  `.remarkrc.json`, `.dprint.json`, and everything under `node_modules/`,
  `.mypy_cache/`, `scratch/` are unrelated tooling/dependency manifests, out
  of scope, zero hits confirmed by directory content, not individually grepped.)

## 6. Tests

**None found.** `tests/` contains only `edify-cli` tests (session scraping,
token counting, markdown postprocessing, contract checking — the four tools
`CLAUDE.md` documents); nothing in the tracked `tests/*.py` set touches
`plugin/skills/`, skill names, or runbook phase-type parsing.
`grep -l 'plugin/skills' tests/*.py` returns nothing.
`tests/test_agent_files.py` (the one file whose name suggested agent/skill
coupling) has zero `inline`/`orchestrat` hits. `scripts/check_line_limits.sh`
enforces a 400-line cap only on `src/**/*.py`, `tests/**/*.py`, and
`agents/decisions/*.md` — it does not scan `plugin/skills/` at all, so no
script currently enforces the SKILL.md line caps discussed in §8.

## 7. Overlap analysis (both SKILL.md files read in full)

**Near-duplicate sections** (candidates for a single merged section):
- **Continuation.** `inline/SKILL.md:170-174` and `orchestrate/SKILL.md:190-195`
  are near-verbatim: both "Read `plugin/fragments/continuation-passing.md`
  and follow its §Consumption Protocol as the final action... no
  routing-dependent prepend — step 2 applies unmodified."
- **Deliverable-review handoff.** inline 4c (166-168) and orchestrate §6.3
  (183-188) both close with the identical follow-up line:
  `/deliverable-review plans/<job>` (opus, fresh session), routed through the
  same default-exit continuation.
- **Dispatch composition.** inline's Delegated Execution (88) already
  defers to `orchestrate/references/dispatch-composition.md` rather than
  restating it — this is shared infra today, not duplicated text; the merge
  just needs to keep one copy at the new path.

**Unique to inline** (no orchestrate equivalent):
- Entry Points table / cold-start-vs-`execute` token (20-31) — abolished per
  task decision, so this disappears rather than merges.
- Phase 1 Entry Gate: dirty-tree STOP, `just precommit` STOP, baseline
  capture (33-58) — orchestrate has **no entry gate at all**; its first
  action is `Read plans/<job>/runbook.md` with no git-state check.
- Phase 2 Pre-Work: brief check, recall, reference loading (60-76) —
  orchestrate assumes this already happened upstream (via `/runbook`).
- Phase 4a's full review-routing-table dispatch (multiple reviewer types,
  fix-capable vs report-only pattern, Path B skip hatch) (100-152).
- Phase 4b Triage Feedback (154-164) — orchestrate never calls
  `triage-feedback.sh`.
- `references/review-dispatch-template.md` in its entirety.

**Unique to orchestrate** (no inline equivalent):
- §1 Load the Runbook, STRICT SEQUENTIAL rule (21-32).
- §2.2/2.3 General/TDD item dispatch machinery — the four-dispatch TDD slice
  protocol, refactor dispatch, list revision (50-108). inline has no concept
  of "items" or "slices" at all.
- §3 Post-Item Verification via `verify-step.sh` with a 0/1/2 exit-code
  taxonomy (110-129) — inline's nearest analog is a looser
  `git status --porcelain && just lint` after each dispatch (Phase 3, 90-96),
  with no dedicated script or exit-code contract.
- §4 Phase Boundary checkpoint, IN/OUT non-empty gate, final stateful-object
  audit (131-148).
- §5 Escalation Rules — 2-level model, five named triggers (150-171) — inline
  has no equivalent structure; its only escalation vocabulary is the single
  "STOP" in Phase 1 and Phase 4a.
- §6 Completion — final review / TDD audit / run summary (173-188) —
  inline's 4c is a single line by comparison.
- `references/dispatch-composition.md`'s Model-assignment, naming/resumption,
  and agent-behaviour-contract sections — inline defers to this file rather
  than duplicating it (see above), so it is shared infra already.

**Conflicts** (the two skills say different things about the same step):
- **Dirty-tree / entry-gate handling.** inline STOPs the entire skill at
  entry if `git status --porcelain` is non-empty (Phase 1, 41). Orchestrate
  never checks git state at entry — dirtiness is only ever discovered
  post-dispatch (`verify-step.sh`) or at a phase boundary (`just precommit`,
  131-138). A merged skill needs one entry-gate policy, not two.
- **Review routing scope.** inline routes any changed-file group through
  `plugin/fragments/review-requirement.md`'s full routing table — potentially
  `design-corrector`, `outline-corrector`, `runbook-corrector`, or the
  report-only `skill-reviewer`, in addition to `corrector` (106-119).
  Orchestrate's own SKILL.md body only ever dispatches `edify:corrector`
  (opus) — for TDD test/code review (67-87) and phase-boundary/final
  checkpoints (140-145, 175-177) — with no report-only pattern and no
  mention of the other three reviewer agents anywhere in its text (they
  appear only in the shared `docs/design.md` D-26 table, not in
  `orchestrate/SKILL.md` itself). Which routing scope the merged skill's
  non-tdd/general items use is an open question this inventory surfaces but
  does not answer.
- **Commit ownership after review.** orchestrate is explicit: "the corrector
  never commits... the orchestrator commits it" (91-92, "After the slice").
  inline's Phase 4a never states who commits a fix-capable reviewer's
  changes — its text says only "Agent applies fixes directly" (117), with no
  statement of commit ownership. This is a gap to reconcile, not a stated
  contradiction, but the two skills are silent/explicit on the same question
  in different directions.
- **Halt vocabulary.** Both agree "UNFIXABLE → STOP" as the terminal review
  outcome, but orchestrate names five distinct escalation triggers with a
  2-level (execution vs. design) routing model (§5), while inline has a
  single ad hoc STOP clause in Phase 4a and nothing else. A merged skill
  needs to decide whether inline-sourced work inherits orchestrate's richer
  escalation taxonomy.

## 8. Line budget

| File | Lines |
|---|---|
| `plugin/skills/inline/SKILL.md` | 174 |
| `plugin/skills/orchestrate/SKILL.md` | 202 |
| **SKILL.md combined** | **376** |
| `plugin/skills/inline/references/review-dispatch-template.md` | 82 |
| `plugin/skills/orchestrate/references/dispatch-composition.md` | 79 |
| `plugin/skills/orchestrate/scripts/verify-step.sh` | 32 (script, not prose — the 400-line artifact cap is about documents; noted for completeness, not asserted to apply) |

Project convention (`CLAUDE.md`): "~200 a `SKILL.md` hub" (soft cap, paid on
every invocation) and "400 lines caps any artifact" (source files,
`references/` nodes, plans, design docs, PRs). The two SKILL.md bodies alone
already sum to 376 lines — over 3x the ~200-line hub target and just under
the 400-line hard artifact cap — before any merged content is added. No
script enforces either cap against `plugin/skills/` (§6), so nothing will
flag an oversized merged `SKILL.md` automatically.

## 9. Anything that would silently break

- `verify-step.sh` is referenced by a **hardcoded path**
  (`plugin/skills/orchestrate/scripts/verify-step.sh`) from three other
  locations: `orchestrate/SKILL.md:117,200` and `plugin/README.md:72`. If the
  script moves under `plugin/skills/build/` without updating all three, the
  path in prose goes stale silently — nothing checks it (no test, no lint).
- `dispatch-composition.md` is referenced by hardcoded path from **five**
  files beyond its own owning skill: `plugin/fragments/delegation.md:11,28,75`,
  `plugin/skills/inline/SKILL.md:88`, and
  `inbox/brief-dispatch-model-precedence.md:27,59` (a live, uncommitted brief
  that quotes exact line ranges in this file and in `delegation.md` — those
  line numbers will drift the moment either file is edited, merge or not).
- `tmp/inline-baseline` is a bare literal filename embedded in five lines
  across two files (§4). A rename requires all five to change together, or
  Phase 4a/4b reads a baseline file that was never written.
- `docs/design.md`'s FR-8/FR-10/FR-11 table (59,61,62) maps requirements
  directly to `skills/design/`, `skills/orchestrate/`, `skills/inline/`
  paths. Nothing tests documentation-to-code path correctness, so this table
  goes silently wrong the moment the merge lands without a `docs/design.md`
  pass.
- `plugin/skills/design/SKILL.md` and its `references/write-design.md`,
  `references/write-outline.md` write the literal string
  `` /inline plans/<job> execute `` into their own §Continuation prepend logic
  (four occurrences, §2 table). If `/inline` disappears without updating
  these, `/design`'s cooperative continuation silently calls a skill that no
  longer exists — this is the mechanism, not just documentation, since
  `continuation-passing.md`'s protocol executes whatever string is prepended.
- `agents/learnings.md:71-72` points a future reader at "the inline skill's
  template" and "Fix the template in inline/SKILL.md" — a path that will not
  exist. Harmless (historical note) but misleading if followed.
- `.claude/handoff-todo.md:4` names a **currently open, unfixed defect**
  against `plugin/skills/inline/references/review-dispatch-template.md` and
  `plugin/skills/inline/SKILL.md` (the report-only reviewer flow: the
  `skill-reviewer` agent has Read/Grep/Glob only, but the template tells it
  to fix and write; and a structural-proof Read blocks the gate). This
  defect must be carried into whatever the merged skill does with review
  dispatch, not silently dropped by the rewrite.

## Judgment calls flagged, not resolved

- **Historical plan artifacts** (`plans/pipeline-simplification/**`,
  `plans/pilfer-superpowers/**`, `plans/edify-recall-skill/**`,
  `plans/blog-series/**`, `plans/reports/**`) contain dozens of additional
  `/inline`/`/orchestrate` hits — these are dated, completed plan records
  (the `pipeline-simplification` plan is in fact what built the current
  `verify-step.sh` and `orchestrate/SKILL.md`). Per project convention
  (plans are frozen, date-stamped, not retroactively edited), listed here at
  file level only, not line level, and treated as out of scope for this
  merge. File count: `plans/pipeline-simplification/` alone has ~25 files
  with hits; full list available via the grep commands in the working notes
  if needed.
- **`agents/learnings.md`** (§2, 11 lines) is a live-accumulating learnings
  log, not a frozen plan — whether its historical entries get rewritten to
  say `/build` instead of `/inline`/`/orchestrate`, or are left as accurate
  history of past defects, is a call for the merge design, not this
  inventory.
- **`docs/changelog.md`** (§2, 8 lines) — same question: dated changelog
  entries describing the 2026-09-01 landing are historically accurate as
  written; only a new entry for this merge is unambiguously required.
- **`memory/strategic-pivot.md`, `memory/ddaanet/cc-bash-background-no-duration-cap.md`**
  — memory facts describing pipeline lineage; per shared-claude.md's "no
  volatile git state" convention these describe history and likely don't
  need edits, but are listed for completeness.
- **`docs/superpowers/**`** — three files under this tree predate the
  current `/inline`/`/orchestrate` shape entirely (one explicitly describes
  "the torn-down pipeline"); out of scope, listed for completeness only.
