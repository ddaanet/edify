# When a Run Goes Wrong

Read on any of: a post-item verification that did not come back clean, a
dispatch that errored or returned an unexpected result, an agent that never
returned, or a run resuming after a context ceiling or a kill.

## Post-item remediation

`scripts/verify-step.sh` after a dispatch whose work is committed:

- Exit 2 → the script itself failed, not the dispatch. Stop and report; do not
  remediate, since there is no established verdict to remediate against.
- Exit 1 → remediate: resume the named agent once (`SendMessage to: <name>`,
  "Your dispatch left uncommitted changes or precommit failures. Fix and
  commit."). If the resume fails or returns without progress, dispatch a fresh
  `edify:artisan` (sonnet) with the git status, diff and error output — recovery
  is mechanical, no design context needed. If recovery fails, escalate to the
  user. After any remediation, note the RCA follow-up in the run summary.

## Escalation

**2-level model:** execution-level issues (missing files, failed commands, dirty
tree) are handled here; design-level issues escalate to the user. Every
resolution must pass precommit, leave a clean tree, and satisfy the item's own
criteria.

- **Unexpected result, no error** → stop and report to the user: the planning
  assumptions were wrong.
- **Report file missing after an agent completes** → ask the agent for the
  report (resume by name); if that fails, investigate before proceeding.
- **Same error from two dispatches** → stop and report the pattern: a systemic
  issue, not a one-off.
- **Agent never returns** → check with `TaskOutput`; hanging → stop the task and
  escalate. There is no in-band turn or duration bound
  (`../../fragments/escalation-acceptance.md`) — a runaway agent's only stop is
  the user.

## Resuming after a context ceiling or a kill

A run that hit a context ceiling, or whose session was killed, resumes from
committed state rather than from memory of what it was doing.

1. Find the last checkpoint commit in `git log`.
2. Run that checkpoint's verification.
3. Build the inventory of remaining work from its output.
4. Resume from the next item.

**Do not use `just precommit` as a state-assessment tool.** It is a pass/fail
gate, not a diagnostic: a green run says the tree is valid, never which items
already landed, and a red one says nothing about where the run stopped.
