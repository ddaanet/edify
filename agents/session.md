# Session Handoff: 2026-03-25

**Status:** RC12 review complete (1C/0M/22m) + design context prerequisite briefed. Next: fix RC12 critical with outline.md in context.

## Completed This Session

**Handoff-cli RC12 deliverable review:**
- Full-scope review: L1 (3 opus agents: code, test, prose+config) + L2 (interactive cross-cutting)
- Verified RC11 M-1 (H-2 committed detection) and M-2 (H-4 step_reached) both FIXED
- Found C-1: `session/cli.py:29-32` catches `CleanFileError` from `commit_pipeline()` but not `CommitInputError` — regression from m-2/m-3 fix. Violates S-3 on output channel (stderr), format (Click vs structured markdown), exit code (1 vs 2)
- L1 code agent incorrectly marked m-2/m-3 as FIXED (checked raise site, not catch site scope)
- Report: `plans/handoff-cli-tool/reports/deliverable-review.md` (RC12)
- Lifecycle: `rework`

**Design context prerequisite discussion:**
- Root cause of 12-round plateau: fix agents operated without design specification. Report references requirement IDs (S-3, H-2) but definitions live in outline.md. Agent inferred spec from finding description — incomplete, causing regressions.
- Broader principle: any agent modifying existing code needs design specification in context. If absent, reverse-engineer + user-validate. TDD step agents exempt (deliberately context-restricted, design pre-distilled into step boundaries).
- Briefed: `plans/design-context-prerequisite/brief.md`

## In-tree Tasks

- [x] **Handoff-cli RC12** — `/deliverable-review plans/handoff-cli-tool` | opus | restart
- [ ] **Fix handoff-cli RC12** — `/design plans/handoff-cli-tool/reports/deliverable-review.md plans/handoff-cli-tool/outline.md` | opus
- [ ] **Runbook warnings** — `/design plans/runbook-warnings/brief.md` | sonnet
  - Plan: runbook-warnings | Status: briefed
- [ ] **Stop hook spike** — `/design plans/stop-hook-status-spike/brief.md` | haiku
  - Spike complete. Findings positive. Production integration deferred to status CLI.
- [ ] **Outline template trim** — `/design plans/outline-template-trim/brief.md` | opus | restart

## Worktree Tasks

- [ ] **Planstate disambiguation** — `/design plans/planstate-disambiguation/brief.md` | sonnet
- [ ] **Historical proof feedback** — `/design plans/historical-proof-feedback/brief.md` | sonnet
  - Prerequisite: updated proof skill integrated in all worktrees
- [ ] **Learnings startup report** — `/design plans/learnings-startup-report/brief.md` | sonnet
- [ ] **Submodule vet config** — `/design plans/submodule-vet-config/brief.md` | sonnet
- [!] **Resolve learning refs** — `/design plans/resolve-learning-refs/brief.md` | sonnet
  - Blocker: blocks invariant documentation workflow (recall can't resolve learning keys)
- [ ] **Runbook integration-first** — `/design plans/runbook-integration-first/brief.md` | sonnet
  - Addendum to runbook-quality-directives plan
- [ ] **Commit drift guard** — `/design plans/commit-drift-guard/brief.md` | opus
  - Design how _commit CLI verifies files haven't changed since last diff
- [ ] **Skill-CLI integration** — `/design plans/skill-cli-integration/brief.md` | opus | restart
  - Split from M#4: wire commit/handoff/status skills to CLI tools
- [ ] **Inline resume policy** — `/design plans/inline-resume-policy/brief.md` | sonnet
  - Add resume-between-cycles directive to /inline delegation protocol
- [ ] **Pending brief generation** — `/design plans/pending-brief-generation/brief.md` | sonnet
  - p: directive should create plans/<slug>/brief.md to back the task
- [ ] **Inline dispatch recall** — `/design plans/inline-dispatch-recall/brief.md` | sonnet
  - Fix review-dispatch-template to enforce artifact-path-only recall pattern
- [ ] **Worktree ls filtering** — `/design plans/worktree-ls-filtering/brief.md` | sonnet
  - _worktree ls dumps all plans across all trees; handoff only needs session.md plan dirs
- [ ] **Design context prereq** — `/design plans/design-context-prerequisite/brief.md` | opus | restart
  - Agents modifying code need design spec in context. Fragment change.

## Blockers / Gotchas

**Learnings at soft limit (138 lines):**
- `/codify` overdue — next session should consolidate older learnings

**pretooluse-recall-check hook regex:**
- `[^/]+` matches across newlines/spaces, capturing prose text between `plans/` and next `/`. Brief at `plans/inline-dispatch-recall/brief.md` covers fix.

**Flaky test:**
- `test_worktree_merge_learnings.py::test_merge_learnings_segment_diff3_prevents_orphans` — intermittent merge conflict failure. Passes on retry.

## Reference Files

- `plans/handoff-cli-tool/reports/deliverable-review.md` — RC12 findings (1C/0M/22m)
- `plans/design-context-prerequisite/brief.md` — design context prerequisite brief

## Next Steps

Fix RC12 critical: add `CommitInputError` to except clause at `session/cli.py:31`. Fix task includes outline.md for full S-3 contract context.
