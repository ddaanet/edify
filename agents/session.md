# Session Handoff: 2026-03-23

**Status:** Handoff-cli round 2 rework complete (10 findings fixed). Corrector caught and fixed 1 critical regression (Python 2 except syntax). Three new pending tasks from session observations.

## Completed This Session

**Handoff-cli round 2 rework:**
- Composite triage: 11 findings decomposed, M#4 (skill-CLI integration) split to separate plan
- Integration-first TDD: 7 cycles across 5 phases, all green
- C#1: `_commit_submodule` `check=True` — submodule commit failure now propagates error
- M#2: SKILL.md `claudeutils:*` added to handoff allowed-tools
- M#3: `_error()` fallback changed from `str(exc)` to `f"exit code {exc.returncode}"` — no more raw CalledProcessError repr
- M#5: `aggregate_trees` dedup removed — plans shown per-tree, not deduplicated to main
- m-1: Dead `render_next` deleted (function + 10 tests)
- m-2: `render_pending` ▶ now skips worktree-marked tasks
- m-3: `_is_dirty` uses raw subprocess instead of `_git()` to preserve porcelain format
- m-4: Dead `step_reached` field removed from `HandoffState`
- m-5: Old section name `## Pending Tasks` detected and rejected with exit 2
- m-6: Weak `or` assertion split into two separate assertions
- Corrector review: 1 critical regression caught (Python 2 `except ValueError, AttributeError:` → fixed to tuple form)
- Report: `plans/handoff-cli-tool/reports/review.md`

**RCA: inline recall keywords in delegation prompt:**
- Deviation: inlined recall keywords in corrector dispatch instead of referencing artifact path
- Root cause: pattern entrainment from 6 prior test-driver dispatches
- Classification: insufficient context at decision point + unanchored gate
- Brief written: `plans/inline-dispatch-recall/brief.md`

## In-tree Tasks

- [x] **Review handoff-cli rework** — `/deliverable-review plans/handoff-cli-tool` | opus | restart
  - Plan: handoff-cli-tool
- [x] **Fix handoff-cli round 2** — `/design plans/handoff-cli-tool/reports/deliverable-review.md` | sonnet
  - Plan: handoff-cli-tool | 10 findings fixed, corrector-reviewed
- [ ] **Handoff-cli RC3** — `/deliverable-review plans/handoff-cli-tool` | opus | restart
  - Plan: handoff-cli-tool
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

## Blockers / Gotchas

**Learnings at soft limit (111 lines):**
- `/codify` overdue — next session should consolidate older learnings

**pretooluse-recall-check hook regex:**
- `[^/]+` matches across newlines/spaces, capturing prose text between `plans/` and next `/`. Three blocked dispatches this session. Brief at `plans/inline-dispatch-recall/brief.md` covers fix.

## Reference Files

- `plans/handoff-cli-tool/reports/review.md` — corrector review (1C fixed, 1m deferred)
- `plans/handoff-cli-tool/reports/deliverable-review.md` — round 2 findings (input)
- `plans/handoff-cli-tool/runbook.md` — Tier 2 runbook (integration-first TDD)
- `plans/skill-cli-integration/brief.md` — M#4 split-out brief

## Next Steps

Deliverable review for handoff-cli round 2 rework, then `/codify` to consolidate learnings (111 lines, soft limit 80).
