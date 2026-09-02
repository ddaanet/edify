# Fix report: `/orchestrate` artifact group

**Date:** 2026-09-02
**Source:** `reports/deliverable-review.md`, design intent `outline.md` D3–D6, D14
**Files touched:** `plugin/skills/orchestrate/SKILL.md`,
`plugin/skills/orchestrate/references/dispatch-composition.md`,
`plugin/skills/orchestrate/scripts/verify-step.sh`. No others.

## Findings applied

| Finding | Site | Change |
|---|---|---|
| Critical 1 (commit owner for review fixes) | `SKILL.md:89-93` | New "After the slice" step 1: the corrector never commits; the orchestrator commits `(d)`'s fixes as `<type>: Item N.M/k — code-review fixes` before the Section 3 gate, the same step §4 takes at a phase boundary. Nothing to commit → straight to verification. |
| Critical 1 (gate wording) | `SKILL.md:108-110` | §3 now reads "After every dispatch whose work is committed — GREEN (c), code review (d) once the orchestrator has committed its fixes, and any general item", so the gate never runs on a tree the review left dirty. |
| Critical 2 (commit subject) | `SKILL.md:75-79` | GREEN's subject is `<type>: Item N.M/k — <title>`; type is the executor's choice, nothing keys on it; the GREEN report names the slice commit hash. |
| Critical 2 (dispatch done criteria) | `dispatch-composition.md:19-28` | Done criteria state the `<type>:` convention, list the legitimate types, record that the `commit-msg` hook rewrites the prefix to an emoji, and fix `Item N.M/k` as the only matchable part of a subject. Overrides: RED commits nothing; a review dispatch commits nothing either. |
| Major 1 (report paths collide) | `dispatch-composition.md:29-35` | §Prompt contents item 5 is now the single rule: the path is always `plans/<job>/reports/<dispatch name>.md`, the prompt assigns it, the agent writes exactly there whatever default its own definition carries. Names it as the mechanism that keeps a slice's two reviews apart and lets `tdd-auditor` find them. |
| Major 1 (naming coverage) | `dispatch-composition.md:60-65` | §Naming adds `final-review` and `tdd-audit` so the completion dispatches have names the path rule can consume. |
| Major 1 (SKILL.md:126,159,161) | `SKILL.md:136-138`, `:169-176` | Hardcoded `checkpoint-P-review.md`, `review.md` and `tdd-process-review.md` replaced by dispatch names `phase-P-corrector`, `final-review`, `tdd-audit` plus a pointer to the composition rule. One rule, stated once. |
| Major 2 (recall by path) | — | No change. `dispatch-composition.md:14-16` stands: the grouped `recall-artifact.md` goes by path and the agent Reads the files it lists. |
| Major 5 (`escalated:` has no consumer) | `SKILL.md:94-101` | On `escalated: <reason>` the orchestrator re-dispatches `edify:refactor` once with model opus (the Agent tool's `model` override) and the reason quoted in the prompt; a second `escalated` goes in the run summary and execution continues. `error` still logs and continues. The commit line no longer names a `refactor:` prefix. |
| Major 8 (precommit gate) | `dispatch-composition.md:19` | Done-criterion `just precommit` green kept, commit wording updated. GREEN mode's own text is the agents group's edit. |
| Minor (`verify-step.sh:6` masks git failure) | `verify-step.sh:6-16` | `git status --porcelain` captured into `porcelain` first so `set -e` aborts on its failure; grep runs on a herestring and only exit 1 (everything filtered out) becomes an empty status. Any other grep code prints `ERROR: filtering git status failed` and exits 1. |
| Minor (frontmatter) | `SKILL.md:4` | `allowed-tools: Agent, Read, Edit, Bash, SendMessage, TaskOutput`, matching `runbook/SKILL.md` and `inline/SKILL.md` form. |
| Minor (opus rule ambiguity) | `dispatch-composition.md:53-56` | Rule left as written, plus one sentence making precedence explicit: `Model:` line beats the artifact-type override, which beats the type default; nothing else changes the model. `delegation.md` is the fragments group's edit. |

## Review report naming chosen

The path rule is mechanical: **`plans/<job>/reports/<dispatch name>.md`**, and
nothing else. The dispatch names are:

- `item-N-M.md` — general item
- `item-N-M-s<k>-red.md` — RED report
- `item-N-M-s<k>-test-review.md` — test review (per slice, not one shared file)
- `item-N-M-s<k>-green.md` — GREEN report, names the slice commit hash
- `item-N-M-s<k>-code-review.md` — code review (per slice)
- `phase-P-corrector.md` — phase-boundary checkpoint
- `final-review.md` — single-phase run's closing corrector
- `tdd-audit.md` — the auditor's own report

`tdd-auditor`'s inputs should be the RED, GREEN and review reports under those
names, with the session's `subagents/` transcripts as fallback where a report is
missing; git only confirms and diffs the commit a report names. `SKILL.md:172-176`
states that inline.

## Flag for the agents group

The review-fix commit means a slice can carry **two** commits with the
`Item N.M/k` marker: the GREEN slice commit, and the orchestrator's
code-review-fix commit when `(d)` changed something. An auditor check of the
"exactly one commit per slice" form would now fire on every reviewed slice.
The check should be "the GREEN report's named commit carries tests and
implementation together with the suite green", not a commit count.

Amending the fixes into the GREEN commit was rejected: it invalidates the hash
the GREEN report names, which is the auditor's primary key.

## Left undone

Nothing in the assigned scope. Findings against `plugin/agents/*`,
`plugin/fragments/*`, `/inline`, `/runbook`, `docs/design.md`, `plugin/README.md`
and `outline.md` D5/D14 are the sibling groups' and were not touched.

## Validation

`just precommit` green, exit 0, with `.venv/bin` on PATH:

```
# version consistency
Version consistent: 0.1.1
Tests cached (inputs unchanged)
✓ Precommit OK
```

Tests were served from the sentinel cache; the sentinel hashes `src/`, `tests/`,
`plugin/hooks/`, `plugin/bin/`, none of which this change touches. No test covers
`verify-step.sh` (`grep -rn verify-step tests/ src/` returns nothing), so its
rewritten filter was verified by hand in a scratch git repo: clean tree → `CLEAN`
exit 0, untracked file → `DIRTY` exit 1, a `git status` failure now aborts with
git's own error instead of being masked into `CLEAN`, and a sole ` M memory` line
still filters to empty. Not committed.
