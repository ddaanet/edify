# Allowlist ownership — implementation report

**Date:** 2026-09-21
**Scope:** the four `scripts/check_line_limits.allow` entries noted "no job yet".
All four are under their path-picked cap and off the allowlist. `just precommit`
passes.

## Line counts

| File | Before | After | Cap | Headroom |
|---|---|---|---|---|
| `plugin/skills/build/SKILL.md` | 218 | **188** | 200 | 12 |
| `plugin/skills/design/SKILL.md` | 277 | **174** | 200 | 26 |
| `plugin/skills/requirements/SKILL.md` | 354 | **185** | 200 | 15 |
| `docs/superpowers/design/plugin-transition-evaluation.md` | 403 | **106** | 400 | 294 |
| `plugin/skills/build/references/escalation.md` | — | 50 (new) | 400 | |
| `plugin/skills/build/references/resuming.md` | 13 | deleted | | |
| `plugin/skills/design/references/triage.md` | — | 120 (new) | 400 | |
| `plugin/skills/requirements/references/formats-and-exit.md` | — | 174 (new) | 400 | |
| `plugin/skills/requirements/references/elicit-mode.md` | — | 27 (new) | 400 | |
| `plugin/skills/build/references/review-dispatch-template.md` | 137 | 137 | 400 | |
| `scripts/check_line_limits.allow` | 22 | 18 | | |
| `docs/changelog.md` | 174 | 176 | 400 | |
| `docs/changelog/2026-09-21-pipeline-hubs-split-along-branch-seams.md` | — | 44 (new) | 400 | |

Counts are post-`just format` (rumdl MD013 reflow at 80 columns). No line in any
touched file exceeds 80 columns except pre-existing table rows and code blocks
the formatter leaves alone.

## The splitting rule applied

One node per **branch**, never one node per topic. A branch not taken costs
nothing; a topic split makes one path open three files in sequence. Where a body
still did not fit after the conditional branches came out, the remainder went
into a *single* node read once at its earliest point of need, rather than
several read at each point. Every pointer states the condition under which its
node is read.

---

## `/build` — 218 → 188

### Paths

| Path | Before | After |
|---|---|---|
| Runbook run, general items only | `dispatch-composition` per delegated item, `phase-boundary` per phase end, `finishing` at §5 | unchanged |
| Runbook run with `Slices:` items | + `tdd-slice` | unchanged |
| Runbook-less run (design/outline) | `dispatch-composition`, `finishing` | unchanged |
| **A dispatch errors / verify-step non-zero** | 0 (rules were inline in §4.4 and §6) | **1** (`escalation.md`) |
| **Resuming after a ceiling or kill** | 1 (`resuming.md`) | 1 (`escalation.md`) |
| Errors *and* resumes | 1 | 1 |

The happy path was already at zero extra reads for its lifecycle rules and
stays there. The error branch is the seam: §4.4's exit-1/exit-2 remediation,
§6's escalation cases and `resuming.md` are one condition — "the run did not go
as planned" — and are now one Read instead of one Read plus two inline blocks
paid on every invocation.

### Content moved

| From | To |
|---|---|
| `build/SKILL.md` §4.4 exit-2 and exit-1 bullets (7 lines) | `references/escalation.md` §Post-item remediation |
| `build/SKILL.md` §6 bullet list — unexpected result, missing report, same error twice, agent never returns (13 lines) | `references/escalation.md` §Escalation |
| `references/resuming.md` (whole file, 13 lines) | `references/escalation.md` §Resuming after a context ceiling or a kill |

Verbatim except: `plugin/fragments/escalation-acceptance.md` became
`../../fragments/escalation-acceptance.md` in the moved text, because writing
the repo-relative form into a *new* file would have added a new instance of the
defect F-5 names (see §Findings). The form matches
`build/references/finishing.md:10`.

`build/SKILL.md` keeps in the body: the two-level model statement (a standing
rule, not a procedure), and the condition sentence routing to the node.

### Deleted, not moved

The trailing `## References` recap (13 lines). Every node it listed is already
named inline at its point of use with its trigger, and the section's own
preamble said so ("Each node names the condition that reaches it"). The one
entry not named inline was `plugin/fragments/delegation.md`; it is reached from
`references/dispatch-composition.md:102`, which every delegated dispatch reads,
so nothing lost a route. **This is the one deletion in the task that is not a
move — flagged as a judgement call.**

---

## `/design` — 277 → 174

### Paths

| Path | Before | After |
|---|---|---|
| Fresh Simple / Moderate-agentic-prose | `write-outline`, `design-content-rules`, [`runbook-format`] = 2–3 | **+1** = 3–4 (`triage`) |
| Fresh Moderate non-prose | `design-content-rules`, [`runbook-format`], `route-to-execution` = 2–3 | **+1** = 3–4 |
| Fresh Complex | `write-outline` (chains `research-protocol`, `design-content-rules`, `route-to-execution`) | **+1** |
| Fresh Defect | 0 | **+1** |
| **Resumed `design.md`** | `write-design` | unchanged |
| **Resumed `outline.md`** (all three sub-cases) | `write-outline` | unchanged |
| Author-corrector coupling check | 0 (inline) | 0 (inline — kept in the body) |

The artifact check already short-circuits resumed work past classification
("skip to C.5", "skip to the sufficiency gate"), so the three resumption paths
now genuinely load nothing they do not use — that content was hub weight they
paid for and skipped. A fresh job pays one Read for the whole triage apparatus
instead of four topic-sized ones.

Routing deliberately stayed in the body: moving the Simple and Moderate-non-prose
route procedures out would have cost those paths a Read each and bought only 40
lines, against 105 for triage.

### Content moved

All to `references/triage.md`, verbatim, in the same order:

| From `design/SKILL.md` | Section in the node |
|---|---|
| `#### Classification Criteria` (30 lines) | `## Classification Criteria` |
| `#### Work Type Assessment` + both tables (27) | `## Work Type Assessment` |
| `#### Multi-Item Decomposition` (27) | `## Multi-Item Decomposition` |
| `#### Classification Gate` + persistence (27) | `## Classification Gate` |

The body's replacement is `#### Classify`, 8 lines, stating the condition ("only
on the artifact check's 'otherwise' branch") and enumerating what the node
carries so the agent knows what it is fetching.

**Named `triage.md`, not `classification.md`:** `plans/<job>/classification.md`
is the artifact `plugin/bin/triage-feedback.sh:42` reads. A reference node with
the same basename is a live confusion hazard for an agent holding both paths.
`triage` is the skill's own word for the phase (`### 0. Complexity Triage`,
`#### Triage Recall`).

---

## `/requirements` — 354 → 185

### Paths

| Path | Before | After |
|---|---|---|
| **Extract mode** (the primary signal's path) | 0 required (`empirical-grounding.md` is cited as provenance, not an imperative Read) | **1** (`formats-and-exit`) |
| **Elicit mode** | 0 required | **2** (`formats-and-exit`, `elicit-mode`) |

This skill could not be brought under 200 by need-to-know alone. Its genuinely
conditional content is the elicit branch (19 lines) and four abort conditions;
everything else — the recall artifact, the `requirements.md` format, the
skill-dependency table, the exit routing — is on every path. So the rule that
applied was "limit the number of additional reads": **one** node carrying all of
it, read once at the Recall Pass, which is the earliest point any of it is
needed (the recall artifact is written there). Steps 3, 4 and 6 then cite
sections of a file already in context rather than opening more.

Splitting formats from exit routing would have been more cohesive and cost every
run a second Read. The cohesion was traded for the read.

### Content moved

To `references/formats-and-exit.md`, verbatim:

| From `requirements/SKILL.md` | Section in the node |
|---|---|
| `### Recall Artifact` — rationale, format block, null artifact, selection criteria, output (35 lines) | `## Recall Artifact` |
| `### 4. Gap Detection`'s question-form paragraph and example block (17) | `## Gap-Fill Questions` |
| `## Standard Format` + `**Section rules:**` (49) | `## Standard Format` |
| `## Skill Dependency Scanning` (21) | `## Skill Dependency Scanning` |
| `## Default Exit` + workflow positioning (20) | `## Default Exit` |
| `## STOP Conditions` (20) | `## STOP Conditions` |

To `references/elicit-mode.md`, verbatim:

| From | To |
|---|---|
| `## Elicit Mode Procedure` §1 and §2-6 (21 lines) | the whole node |

Two wording changes inside moved text, both forced by the move:

- `same form as the gap-fill block above` → `same form as §Gap-Fill Questions in
  references/formats-and-exit.md` (the block is no longer "above").
- `that is the hallucination risk the Key Principles below name` → `…the
  do-not-infer rule names` (§Key Principles was deleted, below).

### Deleted, not moved

`## Key Principles` (4 lines). Both bullets were verbatim duplicates: "Extract
from conversation, do not infer (hallucination risk)" restates the **Critical
rule** at step 1, and "Omit empty sections" restates a Section rule and step 3's
fourth bullet. Flagged as a judgement call alongside `/build`'s References recap.

---

## Skill-review findings

### Folded in

- **requirements m10** — `description:` converted from a 254-character single
  scalar to `>-` block form, matching every sibling. `verify-requirements.md:185`
  deferred it explicitly ("the one edit the budget may not cover; apply it only
  after re-counting"); the budget now exists, and a 254-character line is the
  cramming the cap exists to prevent.
- **requirements M2, partial** — the leftover `## STOP Conditions` heading is
  gone from the body. M2's three relocatable conditions were already moved to
  where they bind (§Mode Detection ×2, step 5's overwrite guard) by an earlier
  pass; the fourth, on open questions blocking every exit path, now sits beside
  §Default Exit in `formats-and-exit.md`, which is the guidance it qualifies
  (D-53).
- **The README cross-cutting item "progressive disclosure inverted"** is
  resolved for `requirements` (its M6 instance — `empirical-grounding.md` routed
  only from the last line — was already fixed; the general inversion, a hub
  carrying reference material, is what this restructuring undoes). `review M8`
  and `formalize 8` are the other two instances and are untouched.

### Left untouched (out of scope — all still open)

`design` C1 (`structured-bugfix` names a workflow that does not exist — the text
moved verbatim into `triage.md` and `SKILL.md`'s Defect route is unchanged), C2
(`/proof` dispatches no corrector), M3, M5, M6 (`triage-feedback.sh` has no
Moderate/Defect branch — its producer text moved into `triage.md` unchanged),
m1, m2, m4, m5, m6, m7. `requirements` C1, M3, M4, M5, M6, m1–m9 were already
applied in the tree before this job. Everything in `verify-summary.md`'s
open-design list is untouched.

## Deliverable-review findings landing in moved text

- **F-5** (new repo-relative `plugin/…` paths in skill bodies) — one site sat in
  text I moved: `escalation-acceptance.md`'s citation in `build/SKILL.md` §6. It
  is now `../../fragments/escalation-acceptance.md` in `escalation.md`, because
  re-writing the repo-relative form into a new file would create a new instance
  of the defect rather than carry an old one. **Not fixed, listed:**
  `build/references/dispatch-composition.md:102`
  (`plugin/fragments/delegation.md`), and F-5's four named sites in
  `recall/SKILL.md:20`, `:45`, `ground/SKILL.md:70`,
  `deliverable-review/SKILL.md:104`, `plugin/agents/tdd-auditor.md:209`.
- **F-4** (two "per `X.md`" must-open pointers reintroduced at
  `write-outline.md:149` and `write-design.md:7`) — not in text I moved, not
  fixed.
- F-1, F-2, F-3, F-6 and every Minor are outside this task; none touch the files
  I changed.

## Inbound references

### Updated

- `plugin/skills/design/SKILL.md:139-140` — "handled by §Multi-Item
  Decomposition in Phase 0" → "…in `references/triage.md`".
- `plugin/skills/build/references/review-dispatch-template.md:121` — the example
  Scope IN list named `references/resuming.md`; now `references/escalation.md`.
- `scripts/check_line_limits.allow` — four entries deleted, leaving the three
  corrector entries owned by pilfer defect 21.
- `docs/changelog.md` — new bullet at the top of the list.

### Checked and clean

A tree-wide `rg -U` for every moved heading (`Classification Criteria`, `Work
Type Assessment`, `Multi-Item Decomposition`, `Classification Gate`, `Standard
Format`, `Skill Dependency Scanning`, `Default Exit`, `Recall Artifact`, `Elicit
Mode`, `Key Principles`, `STOP Conditions`, `Escalation`, `Resuming`,
`resuming.md`, `Complexity Triage`) across `plugin/`, `docs/`, `tests/`,
`scripts/`, `CLAUDE.md` and `.claude/rules/` returns no other citation of a
moved section. `docs/references/execution-routing.md` and
`pipeline-contracts.md` cite `route-to-execution.md`, `phase-boundary.md`,
`tdd-slice.md`, `runbook-format.md` and `dispatch-composition.md` — none moved.
No test asserts on any `SKILL.md` body; `tests/test_line_limits.py` builds its
own fixture trees.

### Left deliberately

- **`.claude/handoff-todo.md:20`** — "Still unowned on the line-limit allowlist:
  `build/SKILL.md` (218), `design/SKILL.md` (277), `requirements/SKILL.md`
  (354), `docs/superpowers/design/plugin-transition-evaluation.md` (403)." Now
  stale. It is the session's live task frame, written by other agents in this
  session; I did not edit it. **Needs the lead to strike that line.**
- **Frozen plan artifacts** (historical, not edited):
  `plans/skill-reviews/reports/verify-summary.md:103-107` and
  `verify-design.md:10-12`, `verify-requirements.md:7-10` state the old ceilings
  as live constraints; `plans/provenance-enforcement-and-routing/reports/`
  and `plans/*/outline.md` reference the pre-split shapes.
- `docs/superpowers/specs/2026-08-11-edify-recall-skill-design.md:82` cites
  "`requirements/SKILL.md` artifact format" generically; it is a frozen spec and
  the format still exists, one file over.

### Stale memory references (not edited)

- **`memory/plugin-transition-eval.md`** — says "Full findings with file:line
  refs live at `docs/superpowers/design/plugin-transition-evaluation.md` — read
  that before acting". Four of the five sections it summarises are no longer in
  that file. The memory itself carries the executed outcomes, so it is now the
  fuller record; its pointer sentence over-promises.
- The same file records "the PyPI publish **shipped 2026-08-04** (0.0.3)" while
  **D-9** (`docs/references/cli-and-package.md:71-77`) records publication as
  postponed indefinitely as of 2026-07-17 and `docs/marketplace.md` says the
  marketplace entry "waits on the first `edify-cli` PyPI publish". One of the
  two is wrong; I did not resolve it and did not rely on either.
- **`memory/line-caps.md`** — accurate on mechanism; its "hard gate over `src`
  and `tests`" line predates the prose coverage D-69 now records. Not
  contradicted by this work.

## `plugin-transition-evaluation.md` — what was cut and where each fact survives

403 → 106 lines. The doc was a 2026-07-15 evaluation of five directives; four
were executed.

| Cut | Where the fact is recorded now |
|---|---|
| §1 Merge the submodule (67 lines) — both rationales dead, the justfile rewrite table, the `git add`-in-submodule blocker, the verdict | **D-10**, `docs/references/cli-and-package.md:78-86`, with the archive of `ddaanet/edify-plugin` and the rejection of merge-to-root. Dated in `docs/changelog/2026-07-16-plugin-de-submoduled.md`. The `git-subdir` route and parked marketplace entry in `docs/marketplace.md:17-21`. |
| §1's open question — does the version-consistency invariant survive? | Answered by the tree: `plugin/bin/check-version-consistency.py` exists and `just precommit` runs it (`Version consistent: 0.2.0`). Retained as one clause in the new preamble. |
| §3 Hooks (46 lines) — both hooks, the false settings.json claim in `tmp-directory.md`, the tmp-policy coupling, the dangling `plugin/.claude/agents` symlink | Executed: `plugin/hooks/` now registers only the venv bootstrap (**D-11**); the symlink is gone (`plugin/.claude/` holds `settings.json` and the `skills` symlink only); the tmp policy was *rewritten* and lives in `CLAUDE.md` §Temporary Files. Retained as one bullet. |
| §4 Fragments (76 lines) — the `memory/operational-rules.md` mirror table, what would be lost, the obsolete content list, the prior-art triage, the mechanism question | Executed: the rule set is inline in `CLAUDE.md` (§Error Handling, §No Confabulation, §No Estimates, §Source Not Generated, §Code Removal, §Temporary Files, §Project Tooling Priority — each carrying the specific content §4 flagged as "worth not losing", including "Reuse is not measurement", the operational-thresholds extension, the recipe-before-ad-hoc rule, Rule Suppression by Procedure and the ADR exception). `memory/operational-rules.md` is deleted. The enforcement-strength argument (deterministic include vs retrieval-based recall) is recorded in `memory/plugin-transition-eval.md:81-89`. Retained as one bullet. |
| §5 `token-efficient-bash` (55 lines) — the unsourced 40-60% claim, the `\|\| true` defect, the outlier argument, the two reword sites | Executed: the skill is gone, and the exception now names the condition rather than the skill in `CLAUDE.md` §Error Handling — "legitimate only where a non-zero exit *encodes a result* rather than a failure — `grep` finding no match, `diff` finding differences", which is exactly the reword §5 demanded. The two knowledge items (`((count++))` under `set -e`, `trap "cd …" EXIT`) are covered by the installed `shell-scripting:shell-gotchas` skill, whose own description names "set -e blind spots" and "GNU vs BSD/macOS divergence". Retained as one bullet. |
| §6 Incidental staleness — 10 of 13 bullets | Each verified dead this session: `docs/marketplace.md` now records the archive and the parked entry; `plugin/README.md` is rewritten; `plugin/bin/deliverable-inventory.py` is deleted; `agents/README.md` has no `compose` claim; `agents/learnings.md:5` no longer routes into `plugin/fragments/`; `plugin/README.md:35` has no fragments include; `skills/requirements` consumers `/design` and `/runbook` both exist; `memory/operational-rules.md` is deleted; `refs/remotes/origin/HEAD` → `refs/remotes/origin/main`; `dist/` holds no `claudeutils` artifact. |
| §Recommended sequence (23 lines) | All seven steps executed except the §2 decision, which the trimmed §2 still carries. |

**Kept, because nothing else records it:**

- **§2 Release mechanism** in full — the two `claude-plugin-dev` quotations
  excluding hybrid Python+plugin repos, the eight-row gap table, the root-path
  and marketplace-side-effect frictions, the vendoring mechanics and the
  `version-guard.sh` hook, and the four options. Verified: no `docs/` node
  mentions `claude-plugin-dev`; `docs/decisions.md` has no release decision.
  This page is the only record of why the bespoke `scripts/release.sh` stays.
- **The three live §6 items**: `bump-plugin-version.py:36-52` still rewrites the
  deleted `hooks/sessionstart-health.sh` behind an `.exists()` guard (verified
  in the file); `plugin/.claude/settings.json` sets `"plansDirectory": "plans/"`
  against the parent's `"plans/claude/"` (both verified); `agents/learnings.md:5`
  still routes through the deleted `/codify`.

**One correction, not a cut:** §2 ended "Not actionable without the owner's
call." `memory/plugin-transition-eval.md:47-52` records the call as taken on
2026-07-16 (keep the bespoke recipe now, migrate later). I verified that no
design node carries that decision, so the doc now says option 2 is what the repo
does, names the memory as the only record of the call, and states that recording
it as a decision or reopening it is the remaining work — rather than asserting
either that it is undecided or that it is settled.

## Questions for my human partner, with the default I took

1. **Deleting `/build`'s `## References` recap and `/requirements`'
   `## Key Principles`.** Both are pure restatements of content that remains
   inline, but both are deletions rather than moves, which the task's "move
   verbatim" framing does not cover. **Default taken: deleted**, because a hub
   recap is paid on every invocation and both duplicated live text. Reversible
   in one edit each.
2. **`/requirements` and a fresh `/design` job each pay one extra Read.** The
   200-line hub cap cannot be met for those two without it; every other path is
   unchanged or unchanged-but-lighter. **Default taken: pay the Read**, on the
   grounds that the cap is not negotiable and one Read beats three.
3. **`requirements` m10 (description → block scalar) folded in.** It was the one
   review finding deferred purely for line budget. **Default taken: applied.**
4. **The eval doc's §2 is now the only home for a decision nobody recorded.** It
   would be better as a `docs/decisions.md` line plus a `cli-and-package.md`
   paragraph, which would let this page shrink further. That is a design change
   and I did not take it. **Default taken: left in place, flagged in the doc.**
5. **`.claude/handoff-todo.md:20` is now stale** and I did not edit it (live task
   frame, other agents writing). **Default taken: reported, not edited.**

## `just precommit` — full output

```
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 348/349 passed, 1 xfail
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 86 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

The three remaining `oversized-file:` lines are the allowlisted correctors
(pilfer defect 21), reported and not failing — the gate behaving as KD-7
designed. Before this change the same run printed seven such lines. The
`1 xfail` is the pre-existing `pytest-markdown-report` expected failure.

`just format` ran first and reformatted
`docs/superpowers/design/plugin-transition-evaluation.md`,
`plugin/skills/design/SKILL.md`, `plugin/skills/requirements/SKILL.md` and
`plugin/skills/requirements/references/elicit-mode.md`; all counts above are
post-reflow.

## Tree state

I created, modified or deleted only: the three `SKILL.md` files, the four new
reference nodes, `plugin/skills/build/references/resuming.md` (deleted),
`review-dispatch-template.md`, `scripts/check_line_limits.allow`,
`docs/superpowers/design/plugin-transition-evaluation.md`, `docs/changelog.md`,
`docs/changelog/2026-09-21-pipeline-hubs-split-along-branch-seams.md` and this
report. Nothing is committed.

The working tree also carries other agents' uncommitted work, untouched:
`CLAUDE.md`, `docs/references/agent-instructions.md`,
`plugin/skills/proof/SKILL.md`, `plugin/skills/proof/references/item-review.md`
modified; `docs/changelog/`, `plans/changelog-split/`,
`plans/proof-verdict-prompt/`, two `plans/provenance-enforcement-and-routing/`
reports and six `.claude/` paths untracked. `docs/changelog/` being untracked as
a whole directory means my new changelog entry is untracked inside it.
