## Current task

The `/code-review` findings over `origin/main...HEAD` are resolved: `/orchestrate` regained `Skill`/`Write`/`TaskStop`; the opus re-dispatch prompt must say "this run is the opus escalation" (mirrored into `docs/design.md` D-30); `refactor`'s `plans/` prohibition is rescoped to plan sources with `reports/` excepted; the per-slice test review owns the SUT stub for stub completion; `tdd-auditor` check 3 audits test ids against the test-review report rather than an unavailable RED-report diff; `/inline` persists its baseline to `tmp/inline-baseline` since a `$BASELINE` shell variable dies between Bash calls; `verify-step.sh`'s internal-failure branch exits 2 rather than colliding with the DIRTY verdict. One finding was rejected as by-design — restoring the submodule pointer-sync check would revert D6. `just precommit` green.

Next is dogfooding the simplified pipeline end to end; it is still unexercised, and every contract fixed above was settled on paper only.
