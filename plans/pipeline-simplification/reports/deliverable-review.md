# Deliverable Review: pipeline-simplification

**Date:** 2026-09-02
**Methodology:** docs/design.md §6.8 "Deliverable review"
**Range:** `f3f1015b..993b23b7` (the task-list fossil deletions bundled into
`f3f1015b` itself predate this plan and are excluded). `just precommit` green
at HEAD (FR-2 acceptance).
**Baseline:** `requirements.md` (FR-1..7, NFR-1..2, C-1..5) and `outline.md`
(D1–D11, D13–D15; D12 struck at `/proof`).
**Layers:** Layer 1 delegated — `deliverable-review-agentic-prose.md`,
`deliverable-review-docs.md`; Layer 2 interactive cross-cutting (this file
folds both in; every Layer 1 finding carried here was re-verified against the
files).

## Inventory

Changed lines in range, surviving files only (deletions listed separately):

| Type | File | Lines |
|---|---|---|
| Agentic prose | plugin/skills/runbook/SKILL.md | 151 |
| Agentic prose | plugin/skills/runbook/references/runbook-format.md (new) | 121 |
| Agentic prose | plugin/skills/orchestrate/SKILL.md | 181 |
| Agentic prose | plugin/skills/orchestrate/references/dispatch-composition.md (new) | 58 |
| Code | plugin/skills/orchestrate/scripts/verify-step.sh | 19 |
| Agentic prose | plugin/agents/test-driver.md | 101 |
| Agentic prose | plugin/agents/tdd-auditor.md | 155 |
| Agentic prose | plugin/agents/runbook-corrector.md (renamed) | 214 |
| Agentic prose | plugin/agents/runbook-simplifier.md | 163 |
| Agentic prose | plugin/agents/refactor.md | 190 |
| Agentic prose | plugin/agents/artisan.md | 122 |
| Agentic prose | plugin/agents/corrector.md | 595 |
| Agentic prose | plugin/agents/design-corrector.md, outline-corrector.md | 394, 388 |
| Agentic prose | plugin/skills/inline/SKILL.md, references/review-dispatch-template.md | 165, 82 |
| Agentic prose | plugin/skills/design/SKILL.md, references/design-content-rules.md | 186, 151 |
| Agentic prose | plugin/skills/{proof,requirements,review} changed lines | — |
| Human docs | plugin/fragments/{delegation,continuation-passing,escalation-acceptance,execution-routing,review-requirement,workflows-terminology}.md | 87, 164, 57, 41, 176, 27 |
| Human docs | docs/design.md | 1028 |
| Human docs | docs/changelog.md | 147 |
| Human docs | README.md, plugin/README.md, agents/learnings.md | 73, 80, 195 |
| Human docs | plans/pilfer-superpowers/requirements.md | 229 |
| Human docs | memory/workflow-pipeline-revival.md + MEMORY.md line | 31 |
| Configuration | CLAUDE.md, .claude/rules/workflow-work.md | 213, 8 |

Deleted (D10): 4 scripts, `verify-red.sh`, 2 tests, `plugin/skills/review-plan/`,
old `runbook-corrector.md`, `plugin/docs/`, 10 `runbook/references/`,
`orchestrate/references/{progress-tracking,common-scenarios}.md` — 7,029
lines / 97,724 tokens per `reports/measurements.md`. `rg` for every removed
name over the sweep corpus returns only past-tense or §7 mentions.

**Design conformance summary:** every D10/D11 item and every FR is present in
the deliverables. The conformance gaps are behavioural: the per-slice
execution loop as written cannot run clean (Critical 1–2), and several
agent-to-agent contracts disagree (Major 1–9).

## Critical Findings

**1. Code-review fixes have no commit owner, so the post-slice gate fails on
every slice the review touched.** `plugin/skills/orchestrate/SKILL.md:96-98`
runs `verify-step.sh` after code review (d); `verify-step.sh:6-11` exits 1 on
any dirty path; `plugin/agents/corrector.md` applies fix-all (§3.5, §5) and
never commits — "commit" appears only in template and scope prose
(`:174,261,389`). Design: D5, D6, D-27. Impact: each slice whose review fixed
anything enters the remediation branch (`orchestrate/SKILL.md:105-111`) and
logs an RCA, so the run summary's RCA count measures the missing commit step,
not execution defects. The phase-boundary path (§4 "Otherwise commit and
continue") shows the orchestrator committing the corrector's fixes; §2.3(d)
needs the same step, or the corrector needs a commit contract.

**2. `tdd-auditor`'s commit-subject checks cannot match commits in this
repo.** `plugin/agents/tdd-auditor.md:57,72` grep for `feat: Item N.M/k — …`
and `refactor:`; the installed `commit-msg` hook (`.git/hooks/gitmoji.sh:53-66`)
rewrites every conventional prefix to an emoji before the commit is written
(`git log`: `✨`, `♻️`, `📝`, no `feat:` anywhere). Design: D5 (commit
subject), D14 ("conventions exist to make these checks mechanical"). Impact:
in the dogfood target repo, checks 2 and 4 report a violation for every
compliant slice, so FR-5's named detector for the implementation-shortcut risk
is inoperative. `test-driver.md:60` and `refactor.md:154` prescribe the same
pre-hook subjects.

The subject prefix is the wrong key on a second count: a slice's commit is
not always a feature. A slice that pins an error path lands as a fix (`🐛`),
one that changes a build or config surface as `🔧`/build, and docs, perf and
test slices carry their own types — so even a hook-aware `✨` match would
flag legitimate slices. The commit type should be the executor's choice and
the auditor should not key on it at all. What identifies the slice commit is
the GREEN report: `test-driver.md` GREEN step 6 writes one per slice, and
the report is where the commit hash, the tests run and the one-at-a-time
sequence belong. The auditor should work off the implementer reports (RED
report → test review → GREEN report, each naming its commit), with the
transcript as a fallback source where a report is missing — sub-agent
transcripts sit under the session's `subagents/` directory
(`session-jsonl-schema`, `jsonl-sidechain-segregation`). Git history then
serves only to confirm the named commit exists and to diff it. D5's
`feat: Item N.M/k — <title>` convention should become `<type>: Item N.M/k —
<title>` with the type free, and the `Item N.M/k` marker — which the hook
preserves — the only thing the auditor may match in a subject. Fix sites:
`tdd-auditor.md:57,72` (checks 2 and 4), `:88-91` (inputs), the GREEN
report contents in `test-driver.md:62-63`, `dispatch-composition.md:19-21`
(done criteria), D5 and D14 in `outline.md`, `docs/design.md` §5.3/D-26.

**3. (Pre-existing, outside D10/D11) The continuation hook described in
`plugin/fragments/continuation-passing.md:7-13,79,89` does not exist.**
`plugin/hooks/hooks.json` registers only `SessionStart → bootstrap-venv.sh`;
`rg CONTINUATION-PASSING` hits only this fragment. A skill following the
"first invocation (hook → skill)" path waits for context never injected. Every
pipeline skill's §Continuation reads this fragment. Equally false at
`f3f1015b`; reported because the fragment was in the rewrite set.

## Major Findings

**1. Review report paths collide.** `corrector.md:364-366` writes to
`tmp/review-<ts>.md` or `plans/<plan>/reports/review.md` and nowhere says the
prompt's path governs; `dispatch-composition.md:22` assigns
`reports/<dispatch name>.md`; `orchestrate/SKILL.md:126,159,161` assign
`checkpoint-P-review.md`, `review.md`, `tdd-process-review.md`. Three rules
for one field. Impact: per-slice test and code reviews overwrite one file,
and `tdd-auditor` (`:41-43`) expects per-slice review reports it cannot find.
Design: D4, D5, D14.

**2. Recall passing to sub-agents is specified three incompatible ways.**
`runbook/SKILL.md:130-132` says "include review-relevant entries from
`recall-artifact.md` in the delegation prompt"; `delegation.md:83-87` says
pass the path only and never inline content, and `:70-74` calls handing a
grouped pipeline artifact to a sub-agent an anti-pattern; `dispatch-composition.md:14-15`
hands sub-agents exactly that grouped artifact (per D4); the corrector family
ignores all three and runs `Skill(edify:recall)` itself
(`corrector.md:184`, `runbook-corrector.md:59`). The per-type flat artifacts
that made the delegation rule true were deleted by D1. Partly tracked already
(task frame, pilfer defect 21 observation); the `runbook/SKILL.md` line is new
in this range.

**3. `refactor`'s commit has no staging step.** `refactor.md:150-155`: "Commit
the refactoring as its own commit: `git commit -m "refactor: …"`" with no
`git add`; the command exits non-zero on unstaged edits. Design: D3.

**4. `refactor` Step 5 rewrites the plan directory mid-slice.**
`refactor.md:131-135` sweeps `plans/` "all designs and runbooks" for old
references. `refactor` now runs inside the slice loop (D3), where
`runbook.md` is the orchestrator's artifact whose diff records list revisions
(D4); `corrector.md:300-304` flags an item mutating its own plan directory as
MAJOR. Two writers on `runbook.md` within one slice.

**5. `escalated:` has no consumer.** `refactor.md:29-30,54-56,88-92` return
`escalated: <reason>` for architectural refactorings; `orchestrate/SKILL.md:88-89`
only notes it in the run summary. Nothing dispatches an opus refactor, though
D3 kept the agent partly for "the opus escalation". Either name the dispatch
or state that escalation is a report.

**6. `runbook-simplifier` reads only `design.md`.** `runbook-simplifier.md:50-51`;
every sibling accepts `outline.md` or `design.md` (`runbook/SKILL.md:29-31`,
`runbook-corrector.md:40`, `orchestrate/SKILL.md:24`, `dispatch-composition.md:15`).
This plan itself has only `outline.md`. Design: D9.

**7. `/inline` routes designs and outlines to `runbook-corrector`.**
`review-dispatch-template.md:47`, `inline/SKILL.md:123`; but
`review-requirement.md:37-42` routes designs to `design-corrector`,
`outline-corrector` owns outlines, and `runbook-corrector.md:42-51` rejects
anything that is not `runbook.md`. Design: D-26 T1/T2, D1.

**8. GREEN mode never runs `just precommit`.** `test-driver.md:54` ends at
"full suite + `just lint`", then `:56-58` reports "precommit warnings" from a
command the mode never invokes. D3 specifies "lint + `just precommit` + the
slice commit". The gate survives only as a dispatch done-criterion
(`dispatch-composition.md:19-21`).

**9. `plugin/README.md:72-73` states the wrong gate condition.**
"`verify-step.sh` … `/orchestrate` runs after each dispatch" — D5,
`docs/design.md:157-160` and `orchestrate/SKILL.md:96-97` all say after
committing dispatches only, never after RED.

**10. `docs/design.md:992` (L-5) size figure is stale.** "~28.9 KB"; measured
32,420 bytes. §1 pins the consolidation task to it (NFR-2). Already in the
task frame's remaining list.

**11–13. (Pre-existing, outside D10/D11)** `execution-routing.md:5` cites the
retired `Session.md`; `execution-routing.md:17` and `continuation-passing.md:89`
cite a `Task` tool that D-72 states does not exist; `escalation-acceptance.md:24`
"(D-5)" and `continuation-passing.md:111` "(D-1)" point at unrelated
`docs/design.md` decisions (pre-fold `agents/decisions/` numbering).

## Minor Findings

**Conformance notes**

- FR-5 acceptance 4 asks the auditor to check "test-at-a-time from the commit
  sequence"; under D5's one commit per slice that is unauditable, and neither
  `tdd-auditor.md` nor `docs/design.md` L-6 records the substitution (D14's
  tests-unmodified check).
- `reports/measurements.md:100` attributes the corrector growth to "D12";
  D12 was struck — the slice-review protocols are D5.

**Actionability / determinism**

- `tdd-auditor.md:58-60` "confirm each `feat:` commit's report or CI
  evidence" — no CI exists.
- `tdd-auditor.md:148` "ask the caller for the range" — a one-shot sub-agent
  cannot; should be `blocked: …` per `delegation.md:30-33`.
- `verify-step.sh:6` — under `pipefail`, `|| true` also masks a `git status`
  failure, not only grep's no-match.
- `runbook-simplifier.md:87,154` — "≤8 assertions", "≤10 items" thresholds
  unlabelled as ungrounded, unlike `runbook-corrector.md:78,99`.

**Vocabulary residue** (all removed-name patterns: zero live hits)

- "step" as the unit of work: `corrector.md:156,301`;
  `escalation-acceptance.md:3,8,20,26,28,31,35,37`; `delegation.md:79`.
- `tdd-auditor.md:33` "planned-vs-executed cycle count".
- `agents/learnings.md:102-103` "step files" — dated incident log, D10 scoped
  learnings to two lines; noted, no action implied.

**Frontmatter**

- `orchestrate/SKILL.md` declares no `allowed-tools` (siblings do); body uses
  Agent, Read, Edit, Bash, SendMessage, TaskOutput. Pre-existing.
- `runbook/SKILL.md:7` `allowed-tools` lists `mkdir:*` and `echo:*|pbcopy`
  with no call site.

**Accuracy / consistency (docs)**

- `docs/design.md:7` "Verified against: `06a431ec`" predates the task-9 edit
  in `6facc2ea`.
- `docs/design.md:135-136` "one verification script" omits
  `triage-feedback.sh`, half of D-26 T5.
- D-26 has no row for design → outline (`outline-corrector`); pre-existing.
- `continuation-passing.md:107` "Six cooperative skills" — four declare
  `cooperative: true`. Pre-existing.
- `review-requirement.md:41` routes agent-definition review to
  `plugin-dev:agent-creator`, a creator. Pre-existing.
- `plugin/README.md:63` "(Python 3)" heads a table with two shell scripts.
- `memory/workflow-pipeline-revival.md:28-31` points at `docs/design.md` §7
  for the `runbook-outline` retirements; §7 names the model, not those names
  (the changelog pointer does).
- `dispatch-composition.md` "Model Selection" and `delegation.md:11-14` state
  the opus rule differently (reviewer-tier vs artifact-type only).

**Excess / housekeeping**

- `plugin/scripts/__pycache__/split-execution-plan.cpython-314.pyc` survives
  untracked; delete the directory.
- `refactor.md:187-190` "Created: 2026-01-30 / Purpose:" footer.
- `artisan.md:65` "Use Bash `rg` instead of `grep` or `rg`".
- `agents/learnings.md` lost a third line (the `triage-feedback.sh plans/<job>`
  note) beyond D10's two; justified by `inline/SKILL.md:150`, but unscoped.

## Gap Analysis

| Requirement | Status | Reference |
|---|---|---|
| FR-1 one runbook stage, `runbook.md` terminal | covered | `runbook-format.md:3-6`, `runbook/SKILL.md:23`; no `runbook-outline`/`steps/` hits |
| FR-2 delete expansion machinery, `rg` clean, precommit green | covered | measurements.md; sweep tables in both Layer 1 reports; `just precommit` OK |
| FR-3 rename to `runbook-corrector`, expansion criteria gone, D-26 T2 | covered | `runbook-corrector.md`; `docs/design.md:421-430` |
| FR-4 orchestrator composes prompts, no preflight | covered | `orchestrate/SKILL.md:15-27`; `dispatch-composition.md` |
| FR-5 slice-batched TDD, RED separate, auditor checks | partial | sequence covered `orchestrate/SKILL.md:57-93`; Critical 1–2 break the loop and the auditor; test-at-a-time note above |
| FR-6 prose + interfaces, corrector flags code blocks | covered | `runbook-format.md:66-71`; `runbook-corrector.md:123-126` |
| FR-7 design record rewired, changelog entry | covered | every D11 item located (docs report); Major 10 (L-5 figure) |
| NFR-1 five distinguishers survive, deterministic validation stated lost | covered | `docs/design.md` §7 validator entry; D-26; `test-driver.md:13` |
| NFR-2 measured before/after, unvalidated claims labelled | covered | `reports/measurements.md`; L-6 |
| C-1..C-5 | covered | §7 weak-orchestrator entry; inline execution on main (git log) |
| D1 `/inline` never consumes a runbook | covered | `inline/SKILL.md:18,85`; Major 7 on its review routing |
| D2 test-driver modes | covered | `test-driver.md:13-16,48-50` |
| D3 refactor per slice | partial | Major 3, 4, 5, 8 |
| D4 dispatch composition, run summary | covered | Major 1 (report path), Major 2 (recall) |
| D5/D6 gate placement, `verify-step.sh` | partial | Critical 1 |
| D7/D8 format, one-path `/runbook` (905 words) | covered | `runbook-format.md`; `runbook/SKILL.md` |
| D9 corrector criteria, simplifier | partial | Major 6 |
| D10 deletion set, sweep, sites | covered | docs report sweep table; `plugin/scripts/__pycache__` residue |
| D11 design.md rewire | covered | docs report conformance table |
| D13 general/inline items | covered | `orchestrate/SKILL.md:37-53` |
| D14 auditor criteria | partial | Critical 2 |
| D15 measurement | covered | `reports/measurements.md` |
| Unspecified deliverables | none beyond the two new references the outline names | — |

## Summary

| Severity | Count | Of which pre-existing, outside this plan's contract |
|---|---|---|
| Critical | 3 | 1 |
| Major | 13 | 3 |
| Minor | 24 | 6 |

Layer 1 reports: `deliverable-review-agentic-prose.md` (1 / 7 / 12),
`deliverable-review-docs.md` (1 / 5 / 9). Overlaps are merged above; every
finding carried from Layer 1 was re-verified against the file.
