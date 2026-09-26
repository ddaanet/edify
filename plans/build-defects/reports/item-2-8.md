# Item 2.8 — `plugin/fragments/escalation-acceptance.md`

Status: **applied.**

Requirements: orch M7.

## Per bullet

- **§Dirty tree recovery, per KD-5 (orch M7).** The section prescribed the
  opposite of `/build` for the same trigger: "Do NOT clean up on behalf of the
  item", then an unconfirmed `git checkout -- . && git clean -fd`, then
  escalate. It now opens by naming
  `plugin/skills/build/references/escalation.md` §Post-item remediation as the
  governing rule and saying this section defers to it. The bullets restate
  KD-5, matching what Item 2.6 put in that section:
  - "Do NOT proceed regardless of whether changes look expected" — kept; the
    governing rule agrees (exit 1 is never proceeded on).
  - The owning agent commits or reverts its own work: resume once, fresh
    `edify:artisan`, escalate. The orchestrator never cleans up in its own
    session. This replaces "Do NOT clean up on behalf of the item", which said
    the same about the orchestrator but gave no path for the owner.
  - `git checkout -- . && git clean -fd` only where no agent owns the dirt, and
    only after the user confirms, because it destroys untracked work. This
    replaces the unconditional revert.
  - "Report the dirty tree and escalate" is folded into the chain's last step.

## Surfaces read against each other

The rule lives in two places (`audit-a-contract-across-its-surfaces`). After
Items 2.6 and 2.8 they state one rule: `escalation.md` §Post-item remediation
says it is `/build`'s dirty-tree rule and that this section defers to it; this
section names that section as governing and restates the same three clauses
(owner commits or reverts, orchestrator never cleans up, destructive revert
only unowned and confirmed) and the same resume → artisan → escalate chain.
The consumer side, `SKILL.md` §4.4, routes every non-zero exit to
§Post-item remediation, so no reader reaches the fragment's text as the
operative one inside `/build`.

## Judgement calls

- **Restating rather than a bare pointer.** A bare pointer would leave the
  fragment empty for a reader outside `/build` (it is loaded by
  `.claude/rules/planning-work.md` for runbook work). The restatement names the
  governing section first, so a drift is resolved in the reference's favour.
- **Path form.** This file had no `plugin/…` pointer before; the new one uses
  the repo-relative `plugin/skills/build/references/…` form the sibling
  fragments (`delegation.md`, `review-requirement.md`) already use.
- **"the user".** The file's own voice; the outline's "my human partner" is
  not carried into shipped fragment text.

## Noticed, not changed

- §Rollback protocol, outside the named section, still offers
  `git checkout -- .` "if uncommitted" with no confirmation or ownership check.
- §Required and §Verification sequence define clean as `git status --porcelain`
  returning empty, which disagrees with KD-7's three exempt paths.
