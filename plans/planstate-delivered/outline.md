## Planstate Post-Ready Lifecycle

**Approach:** Extend the plan state machine with 4 post-execution states. Pre-ready states use functional artifact detection (existing pattern). Post-ready states use a single `lifecycle.md` file with append-only entries — last entry determines state. Two name changes from brief based on grounding: `defective` → `rework`, `completed` → `reviewed`.

**Grounded lifecycle:**
`requirements → designed → planned → ready → review-pending → [rework ↔ review-pending] → reviewed → delivered`

### Key Decisions

**D-1 (updated):** Post-ready states: `review-pending` (execution done) → `rework` (review failed) or `reviewed` (review passed) → `delivered` (merged to main).

**D-2 (from brief):** Two delivery paths:
- **Worktree path:** `_worktree merge` appends `delivered` entry for plans with `reviewed` as current state.
- **In-main path:** Plans executed without a worktree (e.g., inline execution on main). `deliverable-review` appends both `reviewed` and `delivered` entries in sequence — no merge step required.

**D-3 (revised from brief — discussion D-2026-02-21):** Single `lifecycle.md` file per plan, append-only. Each line: `{ISO-date} {state} — {source}`. Last line determines current state. Pre-ready states still detected from functional artifacts (design.md, runbook-phase-*.md, etc.). `lifecycle.md` only governs post-ready states.

**Example lifecycle.md:**
```
2026-02-20 review-pending — /orchestrate
2026-02-20 rework — /deliverable-review
2026-02-21 review-pending — /deliverable-review
2026-02-21 reviewed — /deliverable-review
2026-02-21 delivered — _worktree merge
```

**Rationale for change from brief's D-3 (marker files):** Pre-ready states are detected from functional artifacts — `design.md` exists because you wrote a design. Post-ready states are purely lifecycle markers with no functional content. The review loop (`rework ↔ review-pending`) requires file deletion with marker files because existence-based detection can't model cycles. Single append-only file resolves this: no deletion, no priority ambiguity in loops, built-in audit trail.

**D-4 (simplified):** Pre-ready priority unchanged: `ready > planned > designed > requirements`. Post-ready: last entry in `lifecycle.md` wins. If `lifecycle.md` exists, its state always outranks pre-ready states. No priority ordering needed between post-ready states — the append-only log is inherently ordered.

**D-5 (updated from grounding):** Next actions:
- `review-pending` → `/deliverable-review plans/{name}`
- `rework` → `""` (requires manual fix, then re-review)
- `reviewed` → `""` (agent derives merge command from context)
- `delivered` → `""` (terminal)

**D-6 (from brief):** `#status` excludes `delivered` plans from Unscheduled Plans display.

**D-7 (new — grounding-driven):** Terminology in `execute-rule.md` updated to reflect grounded names. No "defective" or "completed" in plan context.

### Phase Breakdown

**Phase 1: Core inference (TDD)** — `inference.py` + tests (D-3, D-4, D-5)
- Add `lifecycle.md` parsing to `_determine_status`: read file, parse last line, extract state keyword. Valid states: `review-pending`, `rework`, `reviewed`, `delivered`. Line format: `{ISO-date} {state} — {source}` (D-3)
- `lifecycle.md` present → post-ready state from last entry; absent → existing pre-ready logic unchanged (D-4)
- Add `lifecycle.md` to `_collect_artifacts`
- Extend `_derive_next_action` with 4 new match arms (D-5): `review-pending` → `/deliverable-review`, `rework` → `""`, `reviewed` → `""`, `delivered` → `""`
- Note: `PlanState.status` is `str` (not enum-constrained) — new status values require no model changes
- Tests: each post-ready state detection, lifecycle.md with multiple entries (last wins), review loop cycle (rework → review-pending → reviewed — no file deletion needed), coexistence with pre-ready artifacts, missing/empty lifecycle.md fallback, malformed line handling

**Phase 2: Merge integration (TDD)** — `merge.py` + tests (D-2 worktree path)
- After successful merge commit, scan plan dirs for `lifecycle.md` where last entry is `reviewed`
- Append `{date} delivered — _worktree merge` entry using same line format as D-3
- Must use lifecycle.md parsing from Phase 1 (or shared utility) to detect current state
- Test: merge appends delivered, skips non-reviewed plans, handles plans without lifecycle.md, handles plans with lifecycle.md in non-reviewed state
- Note: In-main delivery path handled by deliverable-review skill (Phase 3), not merge

**Phase 3: Skill/prose updates (general)** — D-2 in-main path, D-6, D-7, lifecycle entry creation triggers
- `orchestrate/SKILL.md`: append `review-pending` entry to `lifecycle.md` at orchestration completion (after final step commit)
- `deliverable-review/SKILL.md`: append `reviewed` (pass) or `rework` (fail) entry; on re-review of plan in `rework` state, append `review-pending` entry first (re-entering review loop — no deletion needed); for in-main plans (no worktree, execution on main), also append `delivered` after `reviewed` (D-2 in-main path)
- `execute-rule.md`: update Unscheduled Plans to exclude `delivered` (D-6); update terminology to grounded names (D-7); update status values list if present

### Scope

**IN:** `_determine_status`, `_derive_next_action`, `_collect_artifacts`, `lifecycle.md` file format and parsing, `_worktree merge` delivered entry, skill updates (orchestrate + deliverable-review), `execute-rule.md` terminology, tests.

**OUT:** Deliverable review self-review shortcut logic (already exists in deliverable-review skill — this job adds lifecycle entry creation, not shortcut criteria). CLI-level filtering of delivered plans from display (agent-side in execute-rule.md, not planstate code). Review report format changes. Rework automation (manual fix cycle).

**Resume edge case:** lifecycle.md is append-only — interrupted writes leave at most a partial last line. Recovery: truncate partial line, re-append. No deletion-based state transitions, so no stuck-state risk from the review loop.

### Affected Files

- `src/claudeutils/planstate/inference.py` — lifecycle.md parsing, post-ready state detection, next-action extensions
- `src/claudeutils/planstate/models.py` — no changes needed (`PlanState.status` is `str`, not enum-constrained)
- `tests/test_planstate_inference.py` — new test cases for all 4 post-ready states
- `src/claudeutils/worktree/merge.py` — delivered entry creation post-merge
- `tests/test_worktree_merge.py` or new test file — merge lifecycle tests
- `agent-core/skills/orchestrate/SKILL.md` — review-pending entry creation
- `agent-core/skills/deliverable-review/SKILL.md` — reviewed/rework entry creation, in-main delivered path
- `agent-core/fragments/execute-rule.md` — terminology + delivered filtering

### Open Questions

None — all resolved by grounding + discussion.
