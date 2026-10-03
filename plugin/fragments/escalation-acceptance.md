## Escalation Acceptance Criteria

When an error is escalated and a fix is attempted (by Sonnet diagnostic,
refactor agent, or manual intervention), all three criteria must pass before the
item is considered resolved:

**Required (all three):**
- `just precommit` passes — mechanical validation (lint, format, type checks)
- Git tree clean — `plugin/skills/build/scripts/verify-step.sh` exits 0, the
  single definition of a clean tree `/build` uses. It tolerates three paths
  dirty by convention — `memory`, `.claude/handoff-*.md` and `inbox/*.md` — so
  the test is not an empty `git status --porcelain`, which any of them fails
- Output validates against item acceptance criteria — the item's stated
  objective is met

**Verification sequence:**

```
1. Apply fix
2. Run `just precommit`
   - If fails: fix issues, re-run (loop until pass or give up)
3. Run `plugin/skills/build/scripts/verify-step.sh`
   - If `DIRTY:`: commit the fix by name (`git commit -- <paths>`), re-run
     until it exits 0
4. Validate the output against the acceptance criteria in the dispatch prompt
   - If criteria undefined: escalate as ambiguity error
5. All three pass → item resolved, resume execution
   Any fails after reasonable attempts → escalate to next level
```

**Rollback protocol:**

When escalation fails partway through an item — the fix attempt itself causes
new issues or acceptance criteria cannot be met:

- Fix committed: revert to the last clean commit before the failed item with
  `git revert HEAD`
- Fix uncommitted: escalate to the user with the `verify-step.sh` listing and
  what the attempt found. Nothing reverts it by default. A path the user decides
  to revert is reverted by name, by the one call
  `plugin/skills/build/references/escalation.md` §Post-item remediation gives —
  never by `git checkout -- .`, which reverts every modified tracked path at
  once, the exempt ones included
- This is a simplification of the Saga compensating transaction pattern, enabled
  by git's atomic snapshot model: reverting a commit restores state (no
  concurrent modifications within single orchestration)
- **Assumption:** All relevant state is git-managed. If non-git state is
  involved (external service calls, task-frame edits outside repo), the simple
  revert model breaks — escalate to user.
- After rollback, re-execute the item from clean state or escalate to user

**Dirty tree recovery:**

When an item leaves the tree dirty — `verify-step.sh` reports `DIRTY:` after the
item — follow `plugin/skills/build/references/escalation.md` §Post-item
remediation. That section is the one copy of the procedure; this fragment keeps
none.

**Timeout handling:**

Two independent guards for two independent failure modes:

| Failure Mode | Guard | Threshold | Basis |
|-------------|-------|-----------|-------|
| Spinning (high activity, no convergence) | none available | ~150 turns | Clean data: p90=40, p95=52, p99=73, max=129 |
| Hanging (no activity, wall-clock grows) | none available | ~600s | Clean data: p90=225s, p95=301s, p99=485s, max=855s |

**Guard availability corrected 2026-08-10.** This previously read "`max_turns`
is actionable now — parameter already exists on Task tool." It does not. The
spawn tool is `Agent`, and its parameters are `description`, `prompt`,
`subagent_type`, `name`, `model`, `isolation` (plus `mode`/`team_name` where
exposed). There is no `max_turns`, no `run_in_background`, and no `resume`.
Verified against three agent types.

- **Neither guard is currently implementable in-band.** Both now require Claude
  Code infrastructure support.
- A `TaskStop` tool exists (deferred, reachable via `ToolSearch`) and could in
  principle terminate a runaway agent externally, but that is out-of-band
  supervision by the orchestrator rather than a spawn-time bound, and its
  fitness for this has not been tested. Do not treat it as the guard until
  probed.
- The thresholds below remain valid — they are measurements of agent behaviour,
  not of any parameter.
- If a turn bound ever becomes available, a single blanket value suffices across
  agent types — the spinning failure mode is type-independent
- Per-type refinement deferred until false positives observed
- Calibrated from 938 clean observations with sleep-inflated outliers filtered
  (>30s/tool flagged as laptop-suspend artifacts)
