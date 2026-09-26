# Item 2.6 — `plugin/skills/build/references/escalation.md`

Status: **applied.**

Requirements: orch M1, m7, M7, C2; orch m5 (Exit-1 bullet).

## Per bullet

- **Exit-1 bullet, at its head (KD-7, orch m5).** The bullet now opens with the
  mask case: a `DIRTY:` listing the `sandbox-lies` hook annotates as sandbox
  masks is re-run once, not remediated, with KD-7's reason (masks reach an
  unsandboxed reader when a sandboxed Bash call runs concurrently). Every other
  exit 1 goes to the unchanged remediation chain. This is the rule `SKILL.md`
  §2's DIRTY bullet points at ("re-run instead, per `references/escalation.md`
  §Post-item remediation"), so the bullet names both call sites: the re-run's
  verdict is acted on "at the entry gate as after an item".
- **"Agent never returns" (KD-4, orch M1, m7).** `TaskOutput` and "stop the
  task" are gone. The procedure is KD-4's: check the report path, `git log` and
  the tree, since silence or an idle reply is not death; resume by name once;
  then escalate to the user. The trailing "no in-band turn or duration bound"
  sentence and its fragment pointer are kept. `SKILL.md` frontmatter already
  dropped both tools (Item 2.1), so no surface still names them in `/build`.
- **§Post-item remediation governs the dirty-tree rule (KD-5, orch M7).** A
  paragraph after the bullets states the section is `/build`'s dirty-tree rule
  and that `../../fragments/escalation-acceptance.md` §Dirty tree recovery
  defers to it (Item 2.8 lands the fragment side). It carries KD-5's two
  clauses the chain above did not: the orchestrator never cleans up in its own
  session, and `git checkout -- . && git clean -fd` runs only where no agent
  owns the dirt and only after the user confirms, because it destroys untracked
  work. The resume message gained "or revert your own uncommitted work", so
  the owning agent's remit matches KD-5's "commit or revert its own work".
- **§Resuming (KD-6, KD-1, orch C2).** Re-invoke `/build` with the same
  `plans/<job>` path; nothing infers it, and `/build` never writes the task
  frame (the reason KD-6 gives). The phase-base resolution is copied from
  `references/phase-boundary.md`: its phase-1 and phase-P>1 sentences and its
  `git log --diff-filter=A` block, verbatim apart from the lead-in.

## Judgement calls

- **A re-run annotated again.** KD-7 says an annotated verdict "is re-run once,
  not remediated" and is silent on the second. Read literally, a second
  annotated verdict is not remediated either, and a remediating agent has
  nothing to fix in a mask, so it stops and reports to the user. A re-run DIRTY
  without the annotation is an ordinary verdict and takes its call site's path:
  STOP at the entry gate, remediation after an item.
- **Keeping `tmp/build-baseline` on resume.** KD-1's phase-1 base, and
  `finishing.md` §1's whole-run diff, are that file. `SKILL.md` §2 captures it
  "before any edits", and a re-invoked `/build` passes through §2 again, so a
  resumed run recapturing it would silently shrink both diffs. §Resuming now
  says the resumed run keeps the file. `SKILL.md` §2 itself is not edited (out
  of this item); `SKILL.md` §6 already routes a resuming run through this file
  "before acting on the state", which is where the clause is read.
- **"the user", not "my human partner".** This file already says "the user"
  throughout; the new text follows it.

## Noticed, not changed

- The top §Escalation list's intro ("Every resolution must pass precommit,
  leave a clean tree") does not name the KD-7 exemptions; "clean" there reads
  as `verify-step.sh`'s CLEAN. Outside the named sections.
- `SKILL.md` §2 does not itself say a resumed run skips the baseline capture;
  the clause lives here only.
