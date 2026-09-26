# build-defects — leg 6 (finished: Items 2.5–2.9 and §5 Finish)

**Status: run finished.** Items 2.5–2.9 are committed. §5's review gate, its
triage feedback and its completion steps ran. The follow-up is
`/deliverable-review plans/build-defects` (opus, fresh session).

## Step 0 — loaded skill

`Skill(edify:build)` reported "Base directory for this skill:
`/Users/david/code/edify/dist/plugin/skills/build`". That is under
`dist/plugin/`, so the leg proceeded. All edits went to `plugin/…`.
`dist/plugin/` was read only to check that its `finishing.md` matched the
source (it did); it differed only in the files this leg edits.

Every `Edit` under `plugin/` in this leg landed, both mine and those of the
dispatched agents, and none was refused. The legs 2–5 blocker is gone.

## Entry state

- HEAD `3435fb42`, the leg 5 report. `tmp/build-baseline` held
  `f44ddbbf89c4bea2ffa49a0fdfdd961cbe167474` and was not rewritten.
- The pre-staged `.claude/handoff-task.md`, `.claude/handoff-todo.md` and
  `memory` gitlink were not mine. They were kept out of every commit by the
  pathspec form, and the untracked `inbox/…md` was left alone.
- §2's entry gate was not re-run. For §3 there is no `brief.md` and no
  `recall-artifact.md`. Recall reused leg 5's selections and added one:
  `edify-commit-hook-gotchas`, `audit-a-contract-across-its-surfaces` and
  `subagent-write-blocks-report-basenames`.

## Per item

- **Item 2.5, `cc99d225`.** Applied in session with `Edit` from
  `item-2-5.md`, then reflowed by `just format`. It failed §Proportionality
  (three files, a contract change), so an opus `edify:corrector` reviewed it
  (`item-2-5-review.md`) and fixed three seams:
  - item 5 got the consumer side of the part protocol;
  - `<group>` is now a one-word slug;
  - `refactor.md` now says why the paths are named.

  No UNFIXABLE. Post-item verify was CLEAN.
- **Items 2.6–2.9.** One opus `edify:artisan` applied them, one commit each:
  - `167db2e5` Item 2.6, `escalation.md`;
  - `52028fbb` Item 2.7, `review-requirement.md`;
  - `7bf20896` Item 2.8, `escalation-acceptance.md`;
  - `e35bc1dc` Item 2.9, `delegation.md`;
  - `29379e06`, its run summary `items-2-6-to-2-9.md`.

  Item reports are `item-2-6.md` to `item-2-9.md`. Post-item verify was
  CLEAN. Per §4.2, the review came from §5's gate.

The work is an outline with no phases, so no phase boundary ran.

Dispatch note: teammates cannot name spawned agents ("the team roster is
flat"). Every dispatch therefore ran unnamed and was resumed by agentId. Each
ended "without delivering a report through SubagentHandback". Each report
file was on disk and was read there. The report-only reviewer's parts were
relayed by the team lead.

## §5 Finish

**Review gate, §1.** The changed files came from
`git diff --name-only f44ddbbf…`. Four groups were dispatched in sequence and
each report was Read. Reports, `.claude/handoff-*`, `memory`, `outline.md`
(a planning artifact) and `.bin/claude` / `.gitignore` / `justfile`
(`18890cfc`, the dist-sync change, not this job) were left out.

| Group | Reviewer | Report | Commit | Outcome |
|---|---|---|---|---|
| code | `edify:corrector` (opus) | `review-code.md` | `158a8bd8` | 1 major fixed: the `memory` gitlink exemption had no test. `test_memory_gitlink_is_clean_and_a_sibling_name_is_not` added, mutation-checked. 1 minor DEFERRED (shared `_run_git` helper) |
| agents | `edify:corrector` (opus) | `review-agents.md` | `c458446c` | No issues. The first pass stopped on a project-hook refusal of its own scratch probe (`git add .`). It was resumed once, told not to re-probe, and completed the `plugin-dev:agent-development` criteria |
| fragments | `edify:corrector` (opus) | `review-fragments.md` | `3e8336cd` | 3 minor fixed: mask re-run and conditional chain in dirty-tree recovery; phase-base pointer for changed files. 2 OUT-OF-SCOPE, below |
| skill | `plugin-dev:skill-reviewer` (opus, report-only) | `review-skill.md` | `df619c7c` | 3 major + 11 minor, all applied by this session. Second pass (resume, once): 1 major + 7 minor, all applied. No further pass |

No UNFIXABLE was raised in any report; the `rg` hits are prose mentions.
Verify after the last review commit was CLEAN.

Skill-group changes worth knowing before the deliverable review:

- **KD-1's literal command is refined.** `finishing.md` §1 and
  `phase-boundary.md` now diff `<base> HEAD`, not `<base>`, so tracked exempt
  dirt (`memory`, `.claude/handoff-*.md`) stays out of the list. This run
  had to drop those paths by hand. `review-requirement.md` keeps the
  working-tree form for `/review`'s uncommitted scope. `outline.md` KD-1 was
  not edited.
- **§4.1's in-session item** now commits by pathspec under an `Item N.M`
  subject. Its corrector is named `item-N-M` and committed before §4.4.
- **Resume path.** `SKILL.md` §1 routes a resumed run to `escalation.md`
  §Resuming. That section defines "resumed" and routes a dirty tree to
  remediation, and §2 skips the baseline capture.
- `SKILL.md` sits at exactly its 200-line hard cap. To hold it there, §2's
  and §3's rationale paragraphs were condensed to one clause each. Each kept
  its reason, which the second-pass reviewer confirmed.

**The two checks leg 5 owed.**
- Item 2.3's KD-2 reading was judged sound. Its wording was fixed: it is now
  a resume of `review-<group>`, appended under a second-pass heading, with
  no further pass.
- Item 2.4's pointers resolve: §Prompt contents, and §Naming and resumption.

**Triage feedback, §2.** `triage-feedback.sh build-defects f44ddbbf…`
returned Files changed 54, Reports 28, Behavioral code yes, Review artifact
review, Verdict `match`, with no warning. Its log line was committed in
`72f92c3a`.

**Completion, §3.**
- Final review was not dispatched: §1 covered every implementation group.
- The TDD audit (`edify:tdd-auditor`) is `tdd-audit.md`, committed in
  `72f92c3a`. Slices 1.1/1 and 1.2/1 are compliant. Two findings:
  - Slice 1.2/2's RED used one batched mutant for four tests; the test
    review's per-test mutants closed that gap.
  - Every reviewed slice has a third marker-bearing commit, from
    classifier-refused fixes applied out of band. All three are narrated in
    legs 1–2.

  Its minor 2, the KD-7 staged-dirt UNFIXABLE, was settled by leg 2's
  decision 1 (a), `9ccbcecc`, before Item 2.1.

## Run summary (§3 step 3)

- Item 1.1: `item-1-1-s1-red`, `-test-review`, `-green`, `-code-review` (leg 1).
- Item 1.2: `item-1-2-s1-*` and `item-1-2-s2-*`, four each (legs 1–2).
- Items 2.1–2.4: `item-2-1.md`–`item-2-4.md` (leg 2).
- Item 2.5: `item-2-5.md`, `item-2-5-review.md` (leg 6).
- Items 2.6–2.9: `item-2-6.md`–`item-2-9.md`, `items-2-6-to-2-9.md` (leg 6).
- Review gate: `review-code.md`, `review-agents.md`, `review-fragments.md`,
  `review-skill.md`. TDD audit: `tdd-audit.md`.
- Remediation RCAs: none in this leg. No post-item verify came back non-clean.
- List revisions: slice 1.2/2 was added and Item 2.5 widened (`9ccbcecc`,
  leg 2). None in this leg.
- **Follow-up:** `/deliverable-review plans/build-defects` (opus, fresh
  session).

## Final `verify-step.sh` output

After `72f92c3a`, sandbox disabled:

```
# version consistency
Version consistent: 0.3.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
CLEAN: tree clean, just precommit passed
exit=0
```

## Deferred and routed

Open design calls for my human partner:
- Scope `tmp/build-baseline` per job (`tmp/build-baseline-<job>`)? Nothing
  deletes the file at completion. A stale file from an earlier job therefore
  looks like a resumable one. (`review-skill.md` M3.)
- Fix the `review-<group>` slug list (`code`, `skill`, `agent`, `design`)
  rather than leaving each run to choose? This run used `code`, `agents`,
  `fragments`, `skill`; `fragments` is not a routing-table group.
  (`review-skill.md` Check 3, optional.)
- The confirmed `git checkout -- . && git clean -fd` also destroys KD-7
  exempt dirt: handoff edits and untracked `inbox/*.md` briefs. The
  confirmation text does not say so. A path-scoped revert over the `DIRTY:`
  listing would avoid it, but that changes KD-5's command.
  (`review-fragments.md` issue 5.)

Recorded, not fixed:
- `escalation-acceptance.md` §Rollback protocol's unconfirmed
  `git checkout -- .`. Also its "clean = empty porcelain" definition, which
  ignores KD-7. Also `review-requirement.md` self-review using `git diff HEAD`,
  which is empty after §4.1's commit-before-review. (Artisan and skill
  reviewer.)
- Shared `_run_git` test helper, now in three copies (`review-code.md`,
  REFACTOR-NEEDED).
- The RED procedure should require one mutant per named test for multi-test
  mutation reds (`tdd-audit.md`).
- `triage-feedback.sh` counts the §4.1 corrector's `item-N-M` report in
  `reports_count` (Q-2).

Carried from earlier legs:
- The `C` half of `verify-step.sh`'s `[^RC][^RC]` guard is unpinned.
- Unmerged exempt paths read CLEAN; `"?…"?` accepts an unbalanced quote.
- `tdd-slice.md`'s orchestrator commits lack the pathspec form.
- `review-dispatch-template.md` §Example's skill-group routing.
- `triage-feedback.sh`'s `xargs` / `|| true` item.
- `just lint`'s RUF100 in `tests/line_limits_helpers.py`.

## Resume block

None needed: the run finished. `tmp/build-baseline` still holds
`f44ddbbf…`. It is left for the deliverable review and not deleted.
