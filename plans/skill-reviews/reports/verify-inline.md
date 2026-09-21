# Verification of `plans/skill-reviews/inline.md` — 2026-09-21

`plugin/skills/inline/` no longer exists. Its successor is
`plugin/skills/build/` — `SKILL.md` (218 lines) plus `references/`
{`dispatch-composition.md` 97, `finishing.md` 74, `phase-boundary.md` 22,
`resuming.md` 13, `review-dispatch-template.md` 137, `tdd-slice.md` 79} and
`scripts/verify-step.sh`. `inline/references/review-dispatch-template.md` became
`build/references/review-dispatch-template.md`, so "the template" below means
that file. Every finding is checked for migration into the successor.

**Line budget:** `build/SKILL.md` is allowlisted at ceiling **218** and measures
exactly 218 — edits to it must be net-zero or shrinking. The references are not
allowlisted.

The review's IDs are its criticals 1-3 and its unnumbered Major and Minor
bullets, numbered here in file order as M1-M7 and m1-m16. **The Minor list holds
16 bullets, not the 17 the README tallies** — see §Count discrepancy.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | fixed | The commit/baseline ownership question (README decision 5) is settled in `/design`'s favour, both ways the reviewer proposed. `design/SKILL.md:216-218`: "**Route (after /proof approval):** commit the outline, then name `/build plans/<job>` as the next command and stop." The Simple route no longer implements — steps 1-5 (:199-218) produce an `outline.md` and hand off. `build/SKILL.md:46-55` §2 entry gate STOPs on `DIRTY:`, and :65-74 captures the baseline *after* that gate, so the baseline cannot postdate the implementation. |
| C2 | Critical | fixed | `build/SKILL.md:24-41` §1 "Load the work" opens with `ls plans/<job>` and Reads the plan: "1. `plans/<job>/runbook.md` … 2. `plans/<job>/design.md` or `plans/<job>/outline.md` … 3. Neither — take the task from the invocation." :38 adds "Existence is tested, not discovered by a failing Read". `inline-plan.md` is gone as an artifact kind (`docs/references/execution-routing.md:49`). |
| C3 | Critical | fixed | The report-only reviewer flow exists. `finishing.md:25-29`: "**Report-only reviewers** (`plugin-dev:skill-reviewer`): delegate, read the findings it returns, then write the report and apply the fixes in this session. That reviewer holds **Read, Grep and Glob only** … Use the template's §Report-only variant." `review-dispatch-template.md:45-69` supplies that variant, including the 4000-character chunking contract, and :66-69 states the calling session writes the file so the structural-proof Read at `finishing.md:40-43` finds it. |
| M1 | Major | migrated | `build/references/dispatch-composition.md:33-35` and `build/references/review-dispatch-template.md:89-90`. Two documents each claim to be the only rule and disagree: dispatch-composition says "**Report path** — `plans/<job>/reports/<dispatch name>.md`, the `name` from §Naming and nothing else. **This is the only rule for report paths**"; the template says "**Report path:** one rule — `plans/<job>/reports/review-<group>.md`". `finishing.md` §1 never assigns a `name` to its per-group dispatches, so nothing reconciles them. |
| M2 | Major | migrated | `build/references/review-dispatch-template.md:15-43`. The template still has no `**Constraints:**` block, which `plugin/fragments/review-requirement.md:179-181` requires and :184-188 makes a halt condition ("If a delegation prompt has empty IN, empty OUT, missing changed files, or missing Constraints section, the orchestrator must halt"). And the Changed files field (:20) is still the whole baseline diff (`git diff --name-only <baseline commit hash>`) while `finishing.md:31` scopes each dispatch to "the uncommitted changes for that artifact group". |
| M3 | Major | migrated | `plugin/bin/triage-feedback.sh` and `build/references/finishing.md:45-56`. The script's `reports_count` still counts every file in `plans/<job>/reports/` except `design-review*`, `outline-review*` and `recall-*`, so a review report counts; for `Simple` it still sets `verdict="underclassified"` when `reports_count -gt 0`. A separate `review_artifact` block was added since the review but does not change `reports_count`. The `WARNING: No corrector report` line still has no handling: `finishing.md:54-56` covers only "a divergence message" and "match or no-classification". |
| M4 | Major | fixed | All three halves. D-39 is no longer cited here — a grep of `plugin/skills/build/` finds it nowhere (it survives only at `runbook/SKILL.md:116`, for self-modification ordering). The TDD slice shape is specified: `build/SKILL.md:126-129` §4.3 routes to `references/tdd-slice.md`, whose :4-5 states "It reaches here from a runbook, or from an outline or design routed to `/build`". And `dispatch-composition.md:2-5` now opens "from a runbook item, **or from an ad-hoc task where the work has no runbook**". |
| M5 | Major | fixed | `build/SKILL.md:3-7`: "Execute planned work — a proofed runbook (plans/<job>/runbook.md), or a design or outline that has no runbook. Triggers on /build, "execute the runbook", "execute this plan", or when /design or /runbook hands work off for execution." No "run task"; `/orchestrate` no longer exists to collide with. |
| M6 | Major | fixed | `review-dispatch-template.md:79-81`: "**Design context:** Always `outline.md` or `design.md` — never `requirements.md`." Every `/design` route now produces an `outline.md` (`design/SKILL.md:205`, :226; `write-outline.md:162`), and `inline-plan.md` is removed as a kind, so the field's assumption holds on all routes. |
| M7 | Major | fixed | The two thresholds are now separated and each states its authority. Per-item self-review: `build/SKILL.md:114-117` — "Self-review via `git diff` only when every self-review condition in `plugin/fragments/review-requirement.md` §Proportionality holds … so the threshold is the fragment's." Whole-job review skip: :181-183 — "**Skip is not confidence-gated:** "scope is small" and "well-tested" are not justifications". Different gates, no conflict. |
| m1 | Minor | fixed | `build/SKILL.md:39-41` notes the recall artifact *path* for dispatch composition rather than asserting the file exists, and `recall/SKILL.md:38-39` conditions step 1 on existence ("When a plan directory was named and `<plan-dir>/recall-artifact.md` **exists**"). |
| m2 | Minor | migrated | `plugin/fragments/delegation.md:105-114`. `build/` itself is clean — `scripts/verify-step.sh:8-33` checks status, branches on it, then runs `just precommit` with distinct exit codes — but the fragment still prescribes the broken compound as the "**Correct pattern:** Single compound command (`git status --porcelain && just lint`). Compound commands can't be partially executed — both run or neither." A clean status prints nothing and exits 0, so `&&` does not guard dirtiness. |
| m3 | Minor | fixed | The "10+ delegated executions" threshold is gone: a grep for `10+` across `plugin/skills/build/` returns nothing. |
| m4 | Minor | fixed | `build/SKILL.md:87`: "In worktrees: `git show main:plans/<job>/brief.md`." — no `2>/dev/null`. |
| m5 | Minor | fixed | `finishing.md:34-38` resolves the ambiguity explicitly: "Planning artifacts do not route through this gate. They route by artifact, as `docs/references/pipeline-contracts.md` D-26 records: `design.md` → `edify:design-corrector`, `outline.md` → `edify:outline-corrector`, `runbook.md` → `edify:runbook-corrector`." |
| m6 | Minor | migrated | `build/references/finishing.md:34-38` and `build/references/review-dispatch-template.md:100-104`. The same paragraph, near-verbatim in both, down to "`runbook-corrector` rejects anything that is not `runbook.md`." |
| m7 | Minor | migrated | `build/SKILL.md:46` ("## 2. Entry gate (D+B anchor)") and :89 ("### 3.2 Recall (D+B anchor — tool call required)") still use the term with no expansion and no route to its definition (`docs/references/quality-gates.md:76`, D-52). Same defect as runbook m13 and requirements m4 — repo-wide. |
| m8 | Minor | fixed | No history note survives. `build/SKILL.md:18-22` is a design rationale that is actionable ("whether an item is delegated is decided per item at dispatch time … A run spanning several sessions loads only what its own session hits"). |
| m9 | Minor | migrated | `build/SKILL.md:93`: "Patterns for implementing this, not for classifying it." Still a sentence fragment, though it reads as an intelligible gloss on the recall topic above it. Cosmetic. |
| m10 | Minor | migrated | `build/references/finishing.md:31`: "Scope per dispatch is the uncommitted changes for that artifact group, implementation only". Under delegated execution every dispatch commits (`dispatch-composition.md:24-32`), so at §1 there are no uncommitted changes — the set is empty. Same wound as orchestrate C1; the correct referent is the baseline diff §1 step 1 already computes. |
| m11 | Minor | migrated | `build/references/finishing.md:40-43` still reduces the protocol to "UNFIXABLE in any report → STOP and surface it to the user with the path", skipping the validation at `plugin/fragments/review-requirement.md:221-229` (subcategory code, three-gate investigation summary, scope-OUT overlap check). No re-review after the calling session applies a report-only reviewer's fixes (`review-dispatch-template.md:66-69`). |
| m12 | Minor | migrated | `build/references/finishing.md`. §1 ends at the structural-proof Read and §2 runs `triage-feedback.sh`; nothing commits the corrector's fixes or runs `verify-step.sh` between them, though `finishing.md:22-24` says the fix-capable reviewers "appl[y] its fixes" and `dispatch-composition.md:31-32` says "a review dispatch commits nothing either — the orchestrator commits the fixes". `build/SKILL.md:131-135` §4.4 covers per-item verification only. |
| m13 | Minor | fixed | `finishing.md:71-74` §3.3 defines the run summary concretely — "per item its dispatches (`item-N-M`, `item-N-M-s<k>-red`, …), each report path, each remediation RCA, the list revisions, and the follow-up `/deliverable-review plans/<job>`". No "step 2 applies unmodified" wording survives. |
| m14 | Minor | fixed | `review-dispatch-template.md:106-137` §Example is now a real build-skill dispatch with FR-8/FR-10/FR-11, real paths, and the recall line present at :126. No C1-C4 placeholders and no "~1500 words" estimate. |
| m15 | Minor | migrated | First half survives: `review-dispatch-template.md:42` "Return filepath on success, or "UNFIXABLE: [description]" on failure." against `dispatch-composition.md:38-41` "Return contract: the report path on success, or `blocked: <reason>`". Second half fixed: :73-78 now explains the baseline correctly ("taken after the entry gate has confirmed a clean tree, so it excludes design-phase artifacts unconditionally"). |
| m16 | Minor | migrated (first half) / disputed (second) | `review-dispatch-template.md` still has no slot for the `plugin-dev:agent-development` criteria that `plugin/fragments/review-requirement.md:53` says are "named in the dispatch prompt" for an agent-definition review. The `argument-hint` half is **disputed**: no edify skill declares that key, so its absence is the house convention rather than a defect. |

## Count discrepancy

The Minor section of `plans/skill-reviews/inline.md` (:23-38) holds 16 bullets.
The README tallies 17 for inline. I found no seventeenth bullet — the reviewer's
own tally in the file is absent (unlike orchestrate's explicit "2 critical, 8
major, 9 minor"), so the README figure appears to be a transcription error.
Every other skill's counts reconcile. Repo total is therefore **188**, not 189:
24 critical / 74 major / **90** minor.

## Cross-file links

- M3, m10 and m12 are all the review gate's state derivation, and orchestrate C1
  is the same defect at the phase boundary — one repair for all four.
- m2 is `plugin/fragments/delegation.md` §Multi-Step Verification; `build/`
  supersedes it with `verify-step.sh` but the fragment is still live and read by
  dispatched agents.
- m7 = runbook m13 = requirements m4.
- M1 and m15 are both dispatch-contract divergence between the two build
  references; fix them together.

## Exact edits for `open-mechanical`

None. Every still-true finding here is either `migrated` — the fix belongs with
its successor file and several are the same repair — or `disputed`. The migrated
set below has the fixes written up in one place because they overlap; treat them
as a single change to `build/references/`.

### `plugin/skills/build/references/review-dispatch-template.md`

**M1 + m15** — make the report-path and return contracts one rule each:

- :89-90 old: `- **Report path:** one rule — `plans/<job>/reports/review-<group>.md`, `<group>``
  `  being the artifact group `finishing.md` §1 routed.`
  new: `- **Report path:** `plans/<job>/reports/<dispatch name>.md` per`
  `  `dispatch-composition.md` §Prompt contents — the `name` for a review-gate`
  `  dispatch is `review-<group>`, `<group>` being the artifact group`
  `  `finishing.md` §1 routed.`
- :42 old: `Return filepath on success, or "UNFIXABLE: [description]" on failure.`
  new: `Return the report path on success, or `blocked: <reason>`. Mark an issue you`
  `cannot fix "UNFIXABLE: [description]" inside the report.`
  (and the same substitution at :136 in the Example)

**M2** — add the Constraints block and scope Changed files to the group:

- :20 old: `**Changed files:** `git diff --name-only <baseline commit hash>``
  new: `**Changed files:** the files in this artifact group, from`
  `` `git diff --name-only <baseline commit hash>` filtered to the group ``
- insert before :40 (`Fix all issues …`):
  `**Constraints:**`
  `- Do NOT flag items outside the provided scope (Scope OUT above)`

**m16** — add a criteria slot after :38 (`- Integration: consistency …`):

- new: `<for an agent-definition group, the `plugin-dev:agent-development` criteria:`
  `frontmatter validity, trigger description quality, tool access minimality,`
  `system-prompt structure>`

**m6** — delete :100-104 (the `- **Constraint:** This template is for
implementation changes only. Planning artifacts route by artifact …` bullet) and
replace with a pointer:

- new: `- **Constraint:** implementation changes only. Planning-artifact routing is`
  `  `finishing.md` §1's, not this template's.`

### `plugin/skills/build/references/finishing.md`

**m10** — :31:

- old: `Scope per dispatch is the uncommitted changes for that artifact group,`
  `implementation only; the template's §Field Rules set every other field.`
- new: `Scope per dispatch is that artifact group's share of the baseline diff from`
  `step 1, implementation only; the template's §Field Rules set every other field.`

**m11** — :43:

- old: `gate's anchor. UNFIXABLE in any report → STOP and surface it to the user with`
  `the path. Do not proceed to §2 until every issue is resolved or accepted.`
- new: `gate's anchor. UNFIXABLE in any report → validate it by`
  `` `../../fragments/review-requirement.md` §UNFIXABLE Detection Protocol ``
  `(subcategory code, three-gate investigation summary, no scope-OUT overlap),`
  `then STOP and surface it with the path. Where a report-only reviewer's fixes`
  `were applied in this session, re-dispatch that group once to confirm. Do not`
  `proceed to §2 until every issue is resolved or accepted.`

**m12** — insert after the structural-proof paragraph, before §2:

- new: `Commit the fixes the correctors applied — they commit nothing themselves`
  `` (`dispatch-composition.md` §Prompt contents) — then run ``
  `` `plugin/skills/build/scripts/verify-step.sh` and require exit 0 before §2. ``

**M3**, second half — :54-56:

- old: `Read the script output. On a divergence message → surface it inline. On match or`
  `no-classification → proceed silently.`
- new: `Read the script output. On a divergence message, or on`
  `` `WARNING: No corrector report` → surface it inline; the warning means the ``
  `gate's artifact is missing, which contradicts §1 and needs investigating before`
  `§3. On match or no-classification with no warning → proceed silently.`

### `plugin/bin/triage-feedback.sh`

**M3**, first half — exclude review artifacts from the report count so a Simple
job is not logged `underclassified` for having been reviewed:

- old: `    reports_count=$(find "$reports_dir" -maxdepth 1 -type f ! -name "design-review*" ! -name "outline-review*" ! -name "recall-*" | wc -l | tr -d ' ')`
- new: `    reports_count=$(find "$reports_dir" -maxdepth 1 -type f ! -name "design-review*" ! -name "outline-review*" ! -name "recall-*" ! -name "review.md" ! -name "review-*.md" | wc -l | tr -d ' ')`
  The `review_artifact` block already reports review presence separately, so
  nothing is lost.

### `plugin/fragments/delegation.md`

**m2** — :112-114:

- old: `**Correct pattern:** Single compound command`
  `(`git status --porcelain && just lint`). Compound commands can't be partially`
  `executed — both run or neither.`
- new: `**Correct pattern:** one script that owns the whole verdict —`
  `` `plugin/skills/build/scripts/verify-step.sh`. A compound ``
  `` `git status --porcelain && just lint` does not work: a clean status prints ``
  `nothing and exits 0, so the `&&` guards nothing.`

### `plugin/skills/build/SKILL.md` — net-zero required

**m9** — :93:

- old: `Patterns for implementing this, not for classifying it.`
- new: `Select patterns for implementing this task, not for classifying it.`
