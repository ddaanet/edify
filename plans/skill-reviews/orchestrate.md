# plugin-dev:skill-reviewer on plugin/skills/orchestrate (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — parts 2 and 3 pending.**

Measured: `SKILL.md` 203 lines, 1296 body words, 9034 body chars; description 23
words / 163 chars. `references/dispatch-composition.md` 80 lines, 633 words, 4274
chars. Also read `fragments/{review-requirement,delegation,continuation-passing,escalation-acceptance}.md`,
`scripts/verify-step.sh`, `agents/{refactor,corrector,test-driver,tdd-auditor}.md`.
Tally: 2 critical, 8 major, 9 minor.

Reviewer's overall read: the dispatch model, the four-dispatch TDD slice and the
model-assignment rules are coherent and well factored. The defects are in state
derivation at phase boundaries, an unresolved job argument, tool names that do not
exist or are prohibited, and four places where SKILL.md and its fragments give
opposite instructions.

## Critical

**C1. The phase-boundary changed-files list is always empty, so every phase boundary
STOPs.** SKILL.md:137 derives it with bare `git diff --name-only`, which compares
working tree to index. Section 3 (:110-118) guarantees a clean tree after every
committed dispatch and `verify-step.sh:20-24` enforces it, so at a phase boundary the
command prints nothing. SKILL.md:145 then says "the changed-files list present —
empty fields → STOP before delegating", so the gate fires on every well-behaved run.
It needs a range against the phase's base commit. Verified empirically in this repo:
on tracked-clean state the command returns nothing, and it never lists untracked
files even mid-work. The same bare command is prescribed at
`fragments/review-requirement.md:55`, so the defect is inherited, and SKILL.md:175-177
repeats it as "the whole diff" with no range named.

**C2. Nothing resolves `<job>`.** SKILL.md:24 opens with `Read plans/<job>/runbook.md`
and no step maps the invocation to that path. `fragments/continuation-passing.md:57,62,66`
shows the user form as `/orchestrate myplan`, a bare name, while SKILL.md:24,29
assume `plans/<job>/`. The description also claims the skill triggers "when /runbook
hands off in a fresh session", and that path supplies no argument; SKILL.md never
says to read `.claude/handoff-task.md` for it.

## Major

**M1. `TaskOutput` is not a resolvable tool here, and its documented behaviour is
prohibited.** SKILL.md:4 lists it in `allowed-tools` and :163 makes it the only
procedure for a non-returning agent. A ToolSearch over this session's deferred set
returns `TaskStop`, `Monitor`, `SendMessage`, the cron and worktree tools — no
`TaskOutput`. Separately, `memory/ddaanet/cc-async-task-notification-quirks.md:11`
records that `TaskOutput(task_id, block=false)` on a running `local_agent` can dump
the raw JSONL transcript, and `shared-claude.md` forbids reading subagent
transcripts. The escalation path is either unavailable or forbidden.

**M2. The TDD audit is told to read subagent transcripts.** SKILL.md:180-182 gives
`tdd-auditor` "the session's `subagents/` transcripts as fallback where a report is
missing", the exact fallback the ddaanet standing rule forbids.
`agents/tdd-auditor.md:53` and `:184` carry the same instruction, so caller and agent
are wrong together. The rule's own remedy — artifact, `git log`, tree — is already
half-present at SKILL.md:182.

**M3. Inline items get no post-item verification.** SKILL.md:39-41 has the
orchestrator apply edits, run `just precommit` and commit; :112-114 enumerates what
verification follows (GREEN, code review, "any general item") and inline items are
absent, while :54 explicitly sends general items to Section 3 and :38-48 never does.
This is the one item type the orchestrator executes itself, so the one with no
independent clean-tree gate.

**M4. A general item that is itself a review will be misread as a failure.**
SKILL.md:53 routes review items to `edify:corrector`, and
`dispatch-composition.md:27-28` says a review dispatch commits nothing — the
orchestrator commits the fixes. SKILL.md:54 then sends every general item to
Section 3, whose contract is "after every dispatch whose work is committed", so
`verify-step.sh` exits 1 and :123-128 starts remediating a designed state. Section 3
already carves out (a)/(b) for this reason.

**M5. "The corrector never commits" is asserted only by the caller** (SKILL.md:91,
`dispatch-composition.md:27-28`), and the post-slice commit step depends on it.
`agents/corrector.md` contains no such prohibition — the reviewer grepped the
negative forms — and the agent holds `Bash`. Compare `agents/test-driver.md:49`,
which states its absolute prohibition inside the agent definition where it binds.

**M6. The reviewer routing table is bypassed everywhere it matters.**
`fragments/review-requirement.md:35-38` routes skill definitions to
`plugin-dev:skill-reviewer` and design documents to `edify:design-corrector` (opus),
with a fallback at :46. SKILL.md hardcodes `edify:corrector` at :53, :67, :83, :140,
:175 and cites the fragment only at :44-48 for proportionality. Meanwhile
`dispatch-composition.md:47-52` (D-42) singles out `plugin/skills/`, `plugin/fragments/`,
`plugin/agents/` and `docs/design.md` as the class needing opus — precisely the class
the routing table redirects. The runbooks this repo executes edit those paths.

**M7. Dirty-tree remediation contradicts the escalation fragment.** SKILL.md:123-128
on exit 1 resumes the agent with "Fix and commit", then a fresh artisan, then the
user. `fragments/escalation-acceptance.md:33-39` says the opposite for the same
trigger: do not proceed, do not clean up on behalf of the item, revert to the last
clean commit, report and escalate. SKILL.md cites that fragment at :165, so both
readings are in scope. Related hazard in the fragment: its remedy
`git checkout -- . && git clean -fd` (:38) destroys uncommitted and untracked work
with no confirmation, a poor default for a document an agent follows mechanically.

**M8. The phase-boundary halt check is narrower than the fragment's.** SKILL.md:143-145
requires IN/OUT non-empty and changed-files present; `review-requirement.md:52-56`
makes the Requirements summary required too, and :134 puts a missing Constraints
section into the same halt condition.

## Minor

**m1. The description carries no natural-language trigger** (SKILL.md:3 names
`/orchestrate` and the `/runbook` handoff only). Siblings offer spoken forms
("execute inline", "run task"; architecture and planning requests). "Execute the
runbook" matches nothing here.

**m2. Mixed voice.** Sections 1, 2.1, 2.2 and the post-slice steps are third-person
description (:16, :39, :92); Sections 3 and 5 are imperative (:123, :157). The
descriptive half reads as documentation about a third party.

**m3. "Checkpoint form" is coined and never defined** (:46, :140; a grep finds only
those two occurrences). Section 4 describes the shape inline, so the forward
reference resolves, but nothing names the term.

**m4. Redundant precommit at the phase boundary** (:136) right after
`verify-step.sh:26` already ran it for the phase's last committed item.

**m5. Untracked files flip the verdict and the skill does not say so.**
`verify-step.sh:9` exempts exactly one line, ` M memory`; untracked paths are DIRTY.
The current tree carries `?? inbox/` and `?? plans/skill-reviews/`, so a run started
today reports DIRTY on its first verification for reasons unrelated to any dispatch.
State that untracked files are dirt by design, or filter the scratch paths.

**m6. Trace output on every verification call**: `verify-step.sh:2-3` combines
`exec 2>&1` with `set -x`, interleaving the full trace with the verdict lines while
Section 3 keys only on exit codes.

**m7. `TaskStop` is presented as procedure against the fragment's own caution**
(SKILL.md:163-166 vs `escalation-acceptance.md:53`, which says its fitness "has not
been tested. Do not treat it as the guard until probed").

**m8. `Write` in `allowed-tools` has no named use** (:4). :187-188 says the skill
never writes the task frame and reports are written by dispatched agents; the only
in-skill mutation described is the runbook list revision at :105-108, which is an
edit. Plausibly for inline items at :39-41, but the body does not say so.

**m9. Progressive disclosure is thin where the content is densest**: one reference
(80 lines, 633 words) against a 203-line, 1296-word SKILL.md, with Section 2.3
carrying four dispatch specifications, per-mode scope rules, the stub-completion
carve-out, the mutation-testing allowance and the exact escalation wording inline.
Shape observation rather than a defect.

## Correct, and easy to break later

The opus-escalation wording requirement (SKILL.md:100-104) matches
`agents/refactor.md:32-36` exactly, including why the agent cannot infer its own
model. The RED/GREEN mode requirement (SKILL.md:61, :74;
`dispatch-composition.md:38-39`) matches `agents/test-driver.md:13-16, 79`.
