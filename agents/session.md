# Session Handoff: 2026-03-23

**Status:** Handoff-cli round 3 Simple batch complete (5/10 findings fixed). Design skill loophole fixed. Moderate items (M#1, M#2, m-pre-3) remain for /runbook.

## Completed This Session

**Design skill fix:**
- Fixed Simple routing loophole: "implement directly" in step 3 competed with /inline chain
- Removed step 3 execution permission, replaced with "chain to /inline"

**Handoff-cli round 3 Simple batch (5 fixes):**
- m#1: `_check_old_section_name` substring → `re.search` line-anchored regex
- m-pre-1: `_fail` dedup — 3 copies consolidated to single in `claudeutils.git`
- m-pre-4: double `read_text()` eliminated — `parse_session` accepts optional `content` param
- m-pre-5: `_strip_hints` now filters `advice:` lines alongside `hint:`
- m-pre-6: `_init_repo` dedup — 3 test files replaced with shared `init_repo_at` import
- Corrector review clean (0C/0M), report: `plans/handoff-cli-tool/reports/review.md`

**Dropped findings:**
- m#2 (`load_state()` compat): dropped per user — near-zero impact
- m-pre-2 (▶ format): design spec outdated — current format prototyped with user post-design

## In-tree Tasks

- [x] **Handoff-cli RC3** — `/deliverable-review plans/handoff-cli-tool` | opus | restart
  - Plan: handoff-cli-tool | 0C/0M(delta), 2m(delta), 2M+6m(pre-existing)
- [ ] **Fix handoff-cli round 3** — `/design plans/handoff-cli-tool/reports/deliverable-review.md` | sonnet
  - Plan: handoff-cli-tool | Simple batch done (5 fixes). Remaining: M#1 (blocker detection wiring), M#2 (vet file detail), m-pre-3 (completed parser blank lines) — Moderate, need /runbook with TDD
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
- `[^/]+` matches across newlines/spaces, capturing prose text between `plans/` and next `/`. Brief at `plans/inline-dispatch-recall/brief.md` covers fix.

## Reference Files

- `plans/handoff-cli-tool/reports/review.md` — corrector review of Simple batch (clean)
- `plans/handoff-cli-tool/reports/deliverable-review.md` — RC3 findings (source for remaining Moderate items)

## Next Steps

Fix handoff-cli round 3 Moderate items (M#1, M#2, m-pre-3) via /design → /runbook, then `/codify`.
