# Verification of `plans/skill-reviews/orchestrate.md` — 2026-09-21

`plugin/skills/orchestrate/` no longer exists. Its successor is
`plugin/skills/build/` — `SKILL.md` (218 lines) plus `references/`
{`dispatch-composition.md` 97, `finishing.md` 74, `phase-boundary.md` 22,
`resuming.md` 13, `review-dispatch-template.md` 137, `tdd-slice.md` 79} and
`scripts/verify-step.sh` (35). `orchestrate/references/dispatch-composition.md`
became `build/references/dispatch-composition.md`.
`plugin/fragments/continuation-passing.md` no longer exists.

**Line budget:** `build/SKILL.md` is allowlisted at ceiling **218** and measures
exactly 218 — edits to it must be net-zero or shrinking.

Review tally (the reviewer's own): 2 critical, 8 major, 9 minor = 19. My table
carries 19.

| ID | Sev | Status | Evidence |
|---|---|---|---|
| C1 | Critical | migrated | `build/references/phase-boundary.md:9` still runs a bare `git diff --name-only`, and :18-19 still halts on it: "IN/OUT lists must be non-empty and the changed-files list present — empty fields → STOP before delegating." `scripts/verify-step.sh:20-24` still guarantees a clean tree after every committed dispatch, so at a phase boundary the bare command prints nothing and the gate fires on every well-behaved run. The inherited copy also survives at `plugin/fragments/review-requirement.md:125` ("Explicit file list (from `git diff --name-only` …)"). `finishing.md:13` shows the correct form — `git diff --name-only "$(cat tmp/build-baseline)"` — so the fix is already written down one file away. |
| C2 | Critical | migrated | `build/SKILL.md:26-28` still opens `ls plans/<job>` with no step mapping the invocation to that path. Two mitigations arrived: both upstream callers now name the full path (`design/SKILL.md:216-218` "name `/build plans/<job>` as the next command"; `route-to-execution.md:54-55` the same), and the bare-name caller form the finding cited is gone with `continuation-passing.md`. Still unresolved: nothing says where `<job>` comes from on a fresh-session resume, and `.claude/handoff-task.md` is named nowhere in `build/` — `runbook/SKILL.md:146` hands off through `/handoff:handoff` and stops. |
| M1 | Major | migrated | `build/SKILL.md:8` still declares `TaskOutput` in `allowed-tools`, and :198 still makes it the procedure: "**Agent never returns** → check with `TaskOutput`; hanging → stop the task and escalate." This session's deferred tool set resolves `TaskStop`, `Monitor`, `SendMessage`, the cron and worktree tools — no `TaskOutput`. `memory/ddaanet/cc-async-task-notification-quirks.md` still records the raw-JSONL hazard, and the shared conventions still forbid reading subagent transcripts. The escalation path is unavailable or forbidden either way. |
| M2 | Major | migrated (agent half) | Caller side **fixed**: `finishing.md:65-69` now reads "Its inputs are the RED, GREEN and review reports of every slice; git serves only to confirm and diff the commit a report names. Where a report is missing, resume the agent named for that dispatch and get it" — exactly the rule's own remedy. Agent side still wrong: `plugin/agents/tdd-auditor.md:52-53` "Fallback where a report is missing: the dispatch's transcript under the session's `subagents/` directory", repeated at :192-193. `tdd-auditor.md` is **not** on the line-limit allowlist, so the fix is unconstrained. |
| M3 | Major | fixed | `build/SKILL.md:131-135` §4.4: "After every dispatch whose work is committed — a slice's GREEN, a slice's code review once its fixes are committed, **and any general or directly executed item**." The item type the orchestrator executes itself is now named in the verification set, and §4.1 (:109-117) is the path it covers. |
| M4 | Major | migrated | Narrower but alive. `build/SKILL.md:122` routes "`edify:corrector` where the item is itself a review", and §4.4:131 verifies "any general or directly executed item" — but a review dispatch commits nothing (`dispatch-composition.md:31-32`), so verification straight after it still sees the corrector's uncommitted fixes and exits 1. `tdd-slice.md:62-66` solves this for slices ("**Commit the review fixes:** the corrector never commits. If (d) changed anything, commit it … before the post-item verification"); nothing states it for a general item that is a review. |
| M5 | Major | open-design | Still asserted only by callers: `dispatch-composition.md:31-32` and `tdd-slice.md:63`. `plugin/agents/corrector.md` contains no such prohibition — a grep for `commit` in that file returns only scope descriptions (:222, :243, :251) and report-template text (:456-477) — and the agent holds `Bash`. `plugin/agents/test-driver.md:62` shows the right shape ("**Never edit a test file.** The prohibition is absolute for this mode"). **Pending job (4)** — corrector-family dedup: `corrector.md` is allowlisted at ceiling **682** and measures exactly 682, so the prohibition cannot be added without the dedup freeing lines. |
| M6 | Major | fixed | The gate now routes through the table it was bypassing. `finishing.md:10` "Read `../../fragments/review-requirement.md` and route changed files to the appropriate reviewer by its routing table", with the two dispatch patterns at :20-29 naming `plugin-dev:skill-reviewer` explicitly. `dispatch-composition.md:52-60` (D-42) is now artifact-kind based and says so — "The test is the artifact kind, not the path … those are examples, not the definition" — so it no longer competes with the routing table. |
| M7 | Major | migrated | `build/SKILL.md:144-149` on exit 1: "resume the named agent once … dispatch a fresh `edify:artisan` (sonnet) … If recovery fails, escalate to the user." `plugin/fragments/escalation-acceptance.md:46-52` still says the opposite for the same trigger: "Do NOT proceed regardless of whether changes look expected / Do NOT clean up on behalf of the item / Revert to last clean commit: `git checkout -- . && git clean -fd` / Report the dirty tree and escalate." `build/SKILL.md:200` still cites that fragment, so both readings remain in scope. The destructive-remedy hazard (`git clean -fd` with no confirmation) is unchanged. |
| M8 | Major | migrated | `phase-boundary.md:18-19` still requires only non-empty IN/OUT and a present changed-files list. `plugin/fragments/review-requirement.md:116-129` makes the Requirements summary required too ("Must reference specific FRs, acceptance criteria, or behavioral expectations"), and :184-188 puts a missing Constraints section into the same halt condition. Same defect as inline M2, which is the template side of it. |
| m1 | Minor | fixed | `build/SKILL.md:5-6` carries spoken forms: "Triggers on /build, "execute the runbook", "execute this plan", or when /design or /runbook hands work off for execution." |
| m2 | Minor | fixed | The body is imperative throughout the procedure: :30 "Take the first that exists", :56 "Run it with `dangerouslyDisableSandbox: true`", :101 "Walk the work in order", :111 "Read the targets, apply the edits", :151 "**Invent no further checkpoints.**" The one descriptive block (:18-22) is the hub's design rationale, not a step. |
| m3 | Minor | migrated | "checkpoint form" is still coined and still undefined, at `build/SKILL.md:116-117` ("dispatch `edify:corrector` in its checkpoint form") and `phase-boundary.md:14` ("compose by it a checkpoint-form dispatch"). `phase-boundary.md:14-19` describes the shape inline, so the forward reference resolves; nothing names the term. |
| m4 | Minor | migrated | `phase-boundary.md:8` runs `verify-step.sh` — which runs `just precommit` (`verify-step.sh:27`) — immediately after `build/SKILL.md` §4.4 already ran the same script for the phase's last committed item. |
| m5 | Minor | migrated | `verify-step.sh:5-9` still exempts exactly one line, ` M memory`; every untracked path is DIRTY. `build/SKILL.md:52-63` states what each exit code means but never says untracked files are dirt by design. Still live: today's tree carries `?? inbox/`, `?? plans/remaining-sweep/`, `?? tests/line_limits_helpers.py` and others, so a `/build` started now reports DIRTY at its entry gate for reasons unrelated to any dispatch. |
| m6 | Minor | fixed | `verify-step.sh:2-3` is now `exec 2>&1` / `set -euo pipefail` — the `set -x` trace flag is gone, so the verdict lines are not interleaved with a trace. |
| m7 | Minor | migrated | `build/SKILL.md:8` still declares `TaskStop` and :198-199 still presents stopping the task as procedure, against `plugin/fragments/escalation-acceptance.md:70-74`: "A `TaskStop` tool exists … but that is out-of-band supervision by the orchestrator rather than a spawn-time bound, and its fitness for this has not been tested. Do not treat it as the guard until probed." |
| m8 | Minor | fixed | `Write` now has a named use: `build/SKILL.md:176` `Write(plans/<job>/reports/review-skip.md)`, and `review-dispatch-template.md:66-67` gives the calling session a second ("The **calling session** then writes the returned findings to `plans/<job>/reports/review-<group>.md`"). |
| m9 | Minor | fixed | Progressive disclosure is now the hub's organising principle: `build/SKILL.md:18-22` ("A lean hub … The steps that fire once — a phase boundary, finishing the job — are reference nodes, each named below with the condition that reaches it") with six reference nodes listed at :206-219, none loaded unconditionally. |

## Also recorded by the reviewer as "correct, and easy to break later"

Both still hold. The opus-escalation wording requirement is now at
`tdd-slice.md:70-75` ("The prompt must state, in those words, that **this run is
the opus escalation** — the agent cannot see its own model and branches on that
sentence") and still matches `plugin/agents/refactor.md`. The RED/GREEN mode
requirement is at `dispatch-composition.md:42-43` ("the agent refuses a prompt
that names neither") and `tdd-slice.md:11`, :41, matching
`plugin/agents/test-driver.md:3`, :26, :54.

## Cross-file links

- C1, M8 and inline M2/m10/m12 are one wound: the review and checkpoint gates
  derive their changed-files set from the wrong reference point. `finishing.md:13`
  already has the right form.
- M1 and m7 are the same tool-availability problem, one per tool.
- M4 is the general-item case of what `tdd-slice.md:62-66` already fixed for
  slices.
- M5 sits inside pending job (4); the `corrector.md` line budget is the blocker.

## Exact edits for `open-mechanical`

None. Every still-true finding is `migrated` (fix belongs with the successor
file) or `open-design` (M5, blocked on job 4). The migrated fixes are written up
below; C1/M8 and inline M2 are one change, so apply them together.

### `plugin/skills/build/references/phase-boundary.md`

**C1** — :7-10:

- old: ```` ```bash ````
  `plugin/skills/build/scripts/verify-step.sh`
  `git diff --name-only`
  ```` ``` ````
- new: ```` ```bash ````
  `plugin/skills/build/scripts/verify-step.sh`
  `git diff --name-only "$(git rev-parse HEAD~$(<phase item count>))"  # see below`
  ```` ``` ````
  Better, and consistent with `finishing.md:13`: record the phase's base commit at
  the phase's start and diff against it. Add before the block:
  `Record the phase base once, at the phase's first item:`
  `` `git rev-parse HEAD > tmp/build-phase-base`. The changed-files list is ``
  `` `git diff --name-only "$(cat tmp/build-phase-base)"` — a bare ``
  `` `git diff --name-only` compares the working tree to the index, and every ``
  `committed dispatch leaves that empty, so the halt below would fire on every`
  `well-behaved run.`

**M8** — :18-19:

- old: `§Prompt contents rule under the dispatch name `phase-P-corrector`. IN/OUT lists`
  `must be non-empty and the changed-files list present — empty fields → STOP`
  `before delegating.`
- new: `§Prompt contents rule under the dispatch name `phase-P-corrector`. Halt before`
  `delegating on any empty field that`
  `` `../../fragments/review-requirement.md` §Execution Context requires: IN, OUT, ``
  `changed files, Requirements summary, and the Constraints section.`

**m4** — :7-8, drop the redundant run:

- old: the `verify-step.sh` line in the code block
- new: delete it, and add: `§4.4 has already run `verify-step.sh` for the phase's`
  `last committed item; do not run it again here.`

### `plugin/fragments/review-requirement.md`

**C1**, inherited copy — :125-126:

- old: `- **Changed files:** Explicit file list (from `git diff --name-only` or known`
  `  from implementation). Must not be empty.`
- new: `- **Changed files:** Explicit file list, from `git diff --name-only <base>``
  `  against the run's or phase's recorded base commit — never a bare`
  `  `git diff --name-only`, which is empty after every commit. Must not be empty.`

### `plugin/agents/tdd-auditor.md`

**M2** — :52-53 and :192-193, both sites:

- old: `- Fallback where a report is missing: the dispatch's transcript under the`
  `  session's `subagents/` directory.`
- new: `- Fallback where a report is missing: resume the agent named for that dispatch`
  `  (`SendMessage` to its `name`) and get the report. Never read a subagent`
  `  transcript — it is the full JSONL conversation and overflows the context`
  `  window.`

### `plugin/skills/build/SKILL.md` — net-zero required

**M1 + m7** — :8 and :198-199:

- :8 old: `allowed-tools: Agent, Read, Write, Edit, Bash, Skill, SendMessage, TaskOutput, TaskStop`
  new: `allowed-tools: Agent, Read, Write, Edit, Bash, Skill, SendMessage`
- :198-199 old: `- **Agent never returns** → check with `TaskOutput`; hanging → stop the task and`
  `  escalate. There is no in-band turn or duration bound`
  new: `- **Agent never returns** → check the artifact, `git log` and the tree; an idle`
  `  reply is not evidence it died. Then resume by name once, and escalate. There`
  `  is no in-band turn or duration bound`

**M4** — :131-132:

- old: `After every dispatch whose work is committed — a slice's GREEN, a slice's code`
  `review once its fixes are committed, and any general or directly executed item.`
- new: `After every dispatch whose work is committed — a slice's GREEN, a code review`
  `once its fixes are committed (commit them first: the corrector never does), and`
  `any general or directly executed item.`

**M7** — :144 and :200, state the fragment's scope rather than contradict it:

- :144 old: `- Exit 1 → remediate: resume the named agent once (`SendMessage to: <name>`,`
  new: `- Exit 1 → remediate, which overrides`
  `` `plugin/fragments/escalation-acceptance.md` §Dirty tree recovery for a ``
  `` dispatch's own tree: resume the named agent once (`SendMessage to: <name>`, ``
  (+1 line; pay for it from the M1 edit above, which is net-zero, or from m3)

**m3** — define the term once, at :116-117:

- old: `every self-review condition in `plugin/fragments/review-requirement.md``
  `§Proportionality holds; otherwise dispatch `edify:corrector` in its checkpoint`
  `form. This is the one path where the executor would review its own edits, and`
- new: `every self-review condition in `plugin/fragments/review-requirement.md``
  `§Proportionality holds; otherwise dispatch `edify:corrector` scoped to this`
  `item's changes only (`references/phase-boundary.md` shows the shape). This is`
  `the one path where the executor would review its own edits, and`
  and at `phase-boundary.md:14`, replace "a checkpoint-form dispatch" with "a
  dispatch scoped to the phase's items".

**m5** — :53, state the rule inside the verdict:

- old: `- Exit 1 with `DIRTY:` → STOP: "Dirty tree. Commit or stash before /build."`
- new: `- Exit 1 with `DIRTY:` → STOP: "Dirty tree. Commit or stash before /build."`
  `  Untracked files count as dirt by design; only ` M memory` is exempt.`
  (+1 line; pay for it from m4's deletion in `phase-boundary.md` — no, that is a
  different file. Pay from the M1 edit's net-zero surplus, or delete :57-58's
  sandbox note, which `verify-step.sh` call sites repeat three times.)

### `plugin/fragments/escalation-acceptance.md`

**M7**, fragment side — :49-52, scope the rule and drop the unconfirmed
destructive default:

- old: `- Do NOT proceed regardless of whether changes look expected`
  `- Do NOT clean up on behalf of the item`
  `- Revert to last clean commit: `git checkout -- . && git clean -fd``
  `- Report the dirty tree and escalate`
- new: `- Do NOT proceed regardless of whether changes look expected`
  `- Do NOT clean up on behalf of the item`
  `- Resume the dispatching agent once to commit or revert its own work`
  `` (`plugin/skills/build/SKILL.md` §4.4). Only where no agent owns the dirt, and ``
  `  only with the user's confirmation, revert to the last clean commit —`
  `` `git checkout -- . && git clean -fd` destroys uncommitted *and* untracked ``
  `  work`
  `- Report the dirty tree and escalate`
