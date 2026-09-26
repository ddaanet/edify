# When a Run Goes Wrong

Read on any of: a post-item verification that did not come back clean, a
dispatch that errored or returned an unexpected result, an agent that never
returned, or a run resuming after a context ceiling or a kill.

## Post-item remediation

`scripts/verify-step.sh` after a dispatch whose work is committed:

- Exit 2 → the script itself failed, not the dispatch. Stop and report; do not
  remediate, since there is no established verdict to remediate against.
- Exit 1 → first, a `DIRTY:` listing the `sandbox-lies` hook annotates as
  sandbox masks is re-run once, not remediated: masks reach an unsandboxed
  reader when a sandboxed Bash call runs concurrently, so they say nothing about
  the dispatch. The re-run's verdict is the one acted on, at the entry gate as
  after an item; a re-run annotated again → stop and report to the user. Any
  other exit 1 → remediate. Where there is no named agent (an item executed in
  session and self-reviewed), or the named agent commits nothing (a review
  dispatch) or holds no edit tools, skip the resume and go to the fresh
  `edify:artisan`. Otherwise resume the named agent once
  (`SendMessage to: <name>`, "Your dispatch left uncommitted changes or
  precommit failures. Fix and commit, or revert your own uncommitted work."). If
  the resume fails or returns without progress, dispatch a fresh `edify:artisan`
  (sonnet) with the git status, diff and error output — recovery is mechanical,
  no design context needed. If recovery fails, escalate to the user. After any
  remediation, note the RCA follow-up in the run summary.

This section is `/build`'s dirty-tree rule, and
`../../fragments/escalation-acceptance.md` §Dirty tree recovery defers to it.
The agent that owns the dirt commits or reverts its own work; the orchestrator
never cleans up in its own session. `git checkout -- . && git clean -fd` runs
only where no agent owns the dirt, and only after the user confirms it, because
it destroys untracked work.

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
- **Agent never returns** → check its report path, `git log` and the tree:
  silence or an idle reply is not evidence it died. Then resume it by name once,
  and then escalate to the user. There is no in-band turn or duration bound
  (`../../fragments/escalation-acceptance.md`) — a runaway agent's only stop is
  the user.

## Resuming after a context ceiling or a kill

A run that hit a context ceiling, or whose session was killed, resumes from
committed state rather than from memory of what it was doing. Re-invoke `/build`
with the same `plans/<job>` path the run started with: nothing infers it, and
`/build` never writes the task frame, so it cannot be read back from there. A
run is resumed when the invocation says so, or when `plans/<job>/reports/`
already holds this run's reports.

Where the work is a phased runbook, the current phase's base resolves as
`references/phase-boundary.md` says. A resumed run keeps `tmp/build-baseline`,
phase 1's base, rather than recapturing it.

1. Find the last committed item or phase-boundary commit in `git log`
   (`Item N.M` subjects, `item-N-M*.md` and `phase-<P>-corrector.md` reports).
2. Run `scripts/verify-step.sh`. Anything but exit 0 → §Post-item remediation
   above, before anything else; the entry gate then finds the tree clean.
3. Build the inventory of remaining work: the work's items minus those step 1
   shows landed.
4. Run `/build` §2 (without the baseline capture) and §3, then start §4 at the
   first remaining item.

**Do not use `just precommit` as a state-assessment tool.** It is a pass/fail
gate, not a diagnostic: a green run says the tree is valid, never which items
already landed, and a red one says nothing about where the run stopped.
