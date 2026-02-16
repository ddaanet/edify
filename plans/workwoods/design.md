# Workwoods Design

## Problem

Plan status tracking is manual (jobs.md) and drifts from reality. Cross-tree awareness is absent — agents working in worktrees cannot see what's happening in main or sibling trees. Worktree merge auto-deletes (Mode C calls `rm` after merge), preventing long-lived bidirectional worktrees. Session.md merge is task-additive only; volatile sections (Status, Completed, Next Steps) and Blockers/Gotchas have no merge strategy.

## Requirements

**Source:** `plans/workwoods/requirements.md`

**Functional:**
- FR-1: Cross-tree status display — addressed by Phase 3 (aggregation) + Phase 4 (CLI)
- FR-2: Vet artifact staleness — addressed by Phase 2 (mtime-based detection)
- FR-3: Plan state inference from filesystem — addressed by Phase 1 (planstate module)
- FR-4: Bidirectional worktree merge — addressed by Phase 5 (skill update)
- FR-5: Per-section session.md merge strategies — addressed by Phase 5 (merge code). Note: requirements.md titles this "Additive task merge" but design broadens to per-section strategies as resolved in discussion round D-5.
- FR-6: Eliminate jobs.md — addressed by Phase 6 (planstate adoption, archive)

**Non-functional:**
- NFR-1: No writes during status computation — all phases use read-only aggregation
- NFR-2: No unversioned shared state — each tree owns session.md; aggregation is read-only
- NFR-3: Git-native — all state is versioned or computed from versioned artifacts

**Constraints:**
- C-1: Filesystem mtime for vet staleness (captures uncommitted edits)
- C-2: Git commit hash anchor for work counting (stable across checkout/touch)
- C-3: Sandbox permissions already sufficient (no new config)

**Out of scope:**
- Separate tasks.md extraction
- Model tier changes
- Handoff review agent
- worktree-merge-data-loss implementation (separate plan, execution dependency)

## Architecture

### Module Structure

New package: `src/claudeutils/planstate/`

```
src/claudeutils/planstate/
    __init__.py        # Public API: infer_state(), get_vet_status(), aggregate_trees()
    inference.py       # Plan state inference from directory artifacts
    vet.py             # Vet staleness detection via mtime
    aggregation.py     # Cross-tree status collection
    models.py          # Data models (PlanState, VetStatus, TreeStatus, AggregatedStatus)
```

Modified packages:
- `src/claudeutils/worktree/cli.py` — `ls` command upgrade (Phase 4)
- `src/claudeutils/worktree/merge.py` — Per-section merge strategies (Phase 5)
- `src/claudeutils/worktree/session.py` — Blockers/Gotchas extraction (Phase 5)
- `src/claudeutils/validation/` — New planstate validator replaces jobs.py (Phase 6)

Modified skills/docs:
- `agent-core/skills/worktree/SKILL.md` — Mode C: decouple rm from merge (Phase 5)
- `agent-core/fragments/execute-rule.md` — STATUS uses planstate instead of jobs.md (Phase 5)
- `agent-core/skills/handoff/SKILL.md` — Plan archive write replaces jobs.md update (Phase 6)
- `agent-core/skills/design/SKILL.md` — A.1 loads plan-archive.md (Phase 6)

### Data Models

```python
@dataclass
class PlanState:
    name: str                    # Plan directory name
    status: str                  # requirements | designed | planned | ready
    next_action: str             # Command string (e.g., "/design plans/foo/requirements.md")
    gate: str | None             # Advisory gate condition (e.g., "vet stale — re-vet first")
    artifacts: set[str]          # Which artifacts exist (for debugging)

@dataclass
class VetStatus:
    plan_name: str
    chains: list[VetChain]       # Each source→report pair
    any_stale: bool              # Convenience: any chain stale?

@dataclass
class VetChain:
    source: str                  # e.g., "outline.md"
    report: str | None           # e.g., "reports/outline-review.md" (None if missing)
    stale: bool                  # True if source mtime > report mtime or report missing
    source_mtime: float
    report_mtime: float | None

@dataclass
class TreeStatus:
    path: Path                   # Worktree path (or main repo path)
    slug: str | None             # None for main tree
    branch: str
    is_main: bool
    commits_since_handoff: int   # Count of commits since last session.md change
    latest_commit_subject: str
    latest_commit_timestamp: int # Unix epoch for sorting
    is_dirty: bool               # Uncommitted tracked changes
    task_summary: str | None     # First pending task name from session.md

@dataclass
class AggregatedStatus:
    trees: list[TreeStatus]      # Sorted by latest_commit_timestamp descending
    plans: list[PlanState]       # All plans across all visible trees
    vet_statuses: list[VetStatus]  # Per-plan vet chain status
```

### State Inference Rules

Artifact detection scans `plans/<name>/` for specific files. The highest-artifact-level determines status:

| Artifacts Present | Status | Next Action |
|---|---|---|
| `requirements.md` only (or `problem.md` only) | `requirements` | `/design plans/<name>/requirements.md` |
| `outline.md` exists (no `design.md`) | `requirements` | `/design plans/<name>/requirements.md` (resume Phase C) |
| `design.md` exists (no `runbook-phase-*.md`) | `designed` | `/runbook plans/<name>/design.md` |
| `runbook-phase-*.md` files exist (no `steps/`) | `planned` | `agent-core/bin/prepare-runbook.py plans/<name>` |
| `steps/*.md` + `orchestrator-plan.md` exist | `ready` | `/orchestrate plans/<name>/orchestrator-plan.md` |

**Refinement:** `outline.md` without `design.md` maps to `requirements` status, not `designed`. The outline is an intermediate artifact of the design process — the design skill's sufficiency gate may promote it, but from planstate's perspective, `designed` requires `design.md`.

**Exclusions:**
- `plans/reports/` — shared reports directory, not a plan
- `plans/claude/` — ephemeral plan-mode files
- Directories containing only non-standard files (no recognized artifacts)

### Vet Chain Conventions

Source → Report mapping uses naming conventions derived from codebase observation:

| Source Artifact | Expected Report | Notes |
|---|---|---|
| `outline.md` | `reports/outline-review.md` | May have `outline-review-N.md` (iterative) |
| `design.md` | `reports/design-review.md` | Opus design vet |
| `runbook-outline.md` | `reports/runbook-outline-review.md` | |
| `runbook-phase-N.md` | `reports/phase-N-review.md` | Per-phase vet |

**Naming variance:** Some older plans use `checkpoint-N-vet.md` instead of `phase-N-review.md` for phase-level reports (e.g., when-recall). Similarly, escalation reviews may use `-opus` suffix (e.g., `runbook-outline-review-opus.md`). Implementation should try the primary pattern first, then fall back to glob `reports/*N*{review,vet}*` for the matching phase number. Only the most recent match counts per source artifact.

**Staleness rule:** `stale = source_mtime > report_mtime` (C-1: filesystem mtime for uncommitted visibility).

**Missing report:** Treated as stale (report_mtime = None → stale = True).

**Iterative reviews:** Only the highest-numbered review file counts. `outline-review-3.md` supersedes `outline-review.md`. Escalation variants (`*-opus.md`) are treated as additional reviews — highest mtime among all matching reports wins.

### Workflow Gates (D-7)

Gates are advisory preconditions computed from planstate + vet status. They appear in STATUS display and wt-ls output but do not block operations.

| Condition | Gate Message |
|---|---|
| Design vet stale | "design vet stale — re-vet before planning" |
| Outline vet stale | "outline vet stale — re-review before design" |
| Phase N vet stale | "phase N vet stale — re-review" |
| Runbook outline vet stale | "runbook outline vet stale — re-review before expansion" |

Gate computation: `PlanState.gate = first_stale_vet_message(vet_status)`. Only the highest-priority gate is shown (design > runbook > phase-level).

### Cross-Tree Aggregation

**Tree discovery:** `git worktree list --porcelain` returns all worktrees including main. Parse to get paths and branches.

**Per-tree data collection** (read-only, no writes — NFR-1):

1. **Commits since handoff:**
   - Anchor: `git -C <tree> log -1 --format=%H -- agents/session.md`
   - Count: `git -C <tree> rev-list <anchor>..HEAD --count` (0 if no anchor = no session.md commits)

2. **Latest commit:** `git -C <tree> log -1 --format=%s%n%ct` (subject + unix timestamp)

3. **Clean/dirty:** `git -C <tree> status --porcelain --untracked-files=no` (non-empty = dirty)

4. **Task summary:** Read `<tree>/agents/session.md`, extract first pending task name via `extract_task_blocks()`

5. **Plan discovery:** Glob `<tree>/plans/*/` for each tree. Run `infer_state()` per plan directory.

**Sort:** Trees sorted by `latest_commit_timestamp` descending (most recent first — FR-1).

**Main tree inclusion:** Main repo path (first entry in `git worktree list`) is included with `is_main=True`, `slug=None`.

### Upgraded wt-ls CLI (D-2)

**Default output (rich):** Human-readable, one block per tree:

```
main (design-workwoods)  ●  3 commits since handoff
  Task: Design workwoods
  Plan: workwoods [requirements] → /design plans/workwoods/requirements.md
  Gate: design vet stale — re-vet before planning

plugin-migration (plugin-migration)  ○  clean
  Task: Execute plugin migration
  Plan: plugin-migration [ready] → /orchestrate plans/plugin-migration/orchestrator-plan.md
```

Format elements:
- Line 1: `<slug|"main"> (<branch>)  <●|○>  <N commits since handoff | "clean">`
- `●` = dirty (uncommitted changes), `○` = clean
- Task line: first pending task name (omitted if none)
- Plan line: `<plan-name> [<status>] → <next-action>` (one per plan in that tree)
- Gate line: advisory gate condition (omitted if no gates)

**Porcelain output (`--porcelain`):** Backward-compatible tab-separated format:

```
<slug>\t<branch>\t<path>
```

Identical to current `ls` output. Existing consumers unaffected.

**Implementation:** `ls` command gets `--porcelain` flag (default: False). When False, calls `aggregate_trees()` from planstate module and formats rich output. When True, uses existing `_parse_worktree_list()` logic.

### Per-Section Merge Strategies (D-5)

Upgrade `_resolve_session_md_conflict()` in `merge.py` with per-section handling:

| Section | Strategy | Implementation |
|---|---|---|
| Status line (H1 + `**Status:**`) | Squash | Keep ours (discard worktree's) |
| Completed This Session | Squash | Keep ours (worktree completions are worktree-scoped) |
| Pending Tasks | Additive | Existing behavior — union by task name |
| Worktree Tasks | Preserve main's | Keep ours (main tracks worktree assignments) |
| Blockers / Gotchas | Evaluate | Extract from theirs, append with `[from: <slug>]` tag |
| Reference Files | Squash | Keep ours (worktree paths don't apply to main) |
| Next Steps | Squash | Keep ours (worktree direction is session-local) |

**Classification table is binding.** Planners and implementers must follow these strategies literally.

**Blockers evaluation implementation:**
1. Parse theirs session.md for `## Blockers / Gotchas` section
2. Extract each blocker item (bullet + continuation lines)
3. Tag each with `[from: <slug>]` suffix
4. Append to ours Blockers section (create section if missing in ours)
5. Agent reviews tagged blockers at next handoff and removes resolved ones

This is the only strategy requiring new code beyond `_resolve_session_md_conflict()`. The others compose existing patterns (keep-ours, additive-tasks).

**Section identification:** Use `find_section_bounds()` from `session.py` to locate each section. Section names are exact-match on `## <name>` headers.

### Bidirectional Merge (D-4)

The merge CLI command (`_worktree merge`) already does not delete worktrees — deletion is the skill's Mode C calling `rm` afterward.

**Change:** Update `agent-core/skills/worktree/SKILL.md` Mode C step 3 (exit code 0 path):
- Current: "Use Bash to invoke: `claudeutils _worktree rm <slug>` to clean up"
- New: "Output merge success. Inform user: worktree preserved. To remove: `wt-rm <slug>`."

No CLI code changes needed. The merge command is already bidirectional-compatible.

### Plan Archive (D-8)

New file: `agents/plan-archive.md`

```markdown
# Plan Archive

Completed plans with summaries. Loaded on demand during design research (Phase A.1)
and diagnostic/RCA sessions.

## grounding-skill

Ground skill with diverge-converge research procedure. Produces grounded reference
documents via parallel internal + external research. Affected: agent-core/skills/ground/,
plans/reports/. Key decision: mandatory web search for methodology claims.

## when-recall

Memory recall system using /when and /how triggers. 12 phases, merged to main.
Affected: src/claudeutils/when/, agent-core/skills/when/. Key decision: bash transport
for sub-agent consumption.

...
```

**Entry format:** H2 heading (plan name) + paragraph (2-4 sentences: what was delivered, affected modules, key decisions). Richer than jobs.md one-liners because on-demand loading makes cost affordable.

**Migration:** Phase 6 reads jobs.md "Complete (Archived)" section, converts each entry to paragraph format using git history for detail enrichment: `git log --all --oneline -- plans/<name>/` recovers commit messages that describe deliverables.

### jobs.md Elimination (D-3, FR-6)

**Direct replacement, no transition.** The phases are the migration:

1. Phase 1: `infer_state()` provides status for any plan directory
2. Phase 5: execute-rule.md STATUS and worktree skill switch from jobs.md reads to planstate calls
3. Phase 6:
   - New planstate validator replaces `validation/jobs.py`
   - Handoff skill writes plan-archive.md instead of jobs.md
   - Remove jobs.md from CLAUDE.md @-reference
   - Remove `validation/jobs.py` and its precommit integration
   - Remove merge auto-resolution for jobs.md conflicts (no longer needed)
   - Remove jobs.md exemption from clean-tree checks

**Validator replacement:** New `validation/planstate.py` checks:
- Every `plans/<name>/` directory has at least one recognized artifact
- Artifacts are internally consistent (no `steps/` without `runbook-phase-*.md`)
- Plan-archive entries reference plans not in `plans/` (they should be deleted)

vs. current `validation/jobs.py`:
- Plans in directory must appear in jobs.md
- Plans in jobs.md (non-complete) must exist in directory

The new validator is strictly more useful — it validates artifact consistency, not just presence.

## Design Decisions

**D-1: New planstate module, not worktree extension.** Plan state inference is conceptually independent. Cross-tree aggregation composes planstate + worktree discovery + git queries. Separation keeps `worktree/` focused on lifecycle operations and enables planstate reuse outside worktree contexts (e.g., `#status` mode in main tree).

**D-2: Upgrade existing `wt-ls`, don't create new command.** Same entry point, richer output. `--porcelain` preserves old format. Avoids command proliferation.

**D-3: Direct jobs.md replacement.** Jobs.md drifts because it's manually maintained. Validating planstate against an unreliable source adds complexity for no value. Phases themselves are the migration path.

**D-4: Bidirectional merge = skill update only.** The `merge` CLI already doesn't delete worktrees. Mode C's auto-rm is the skill behavior, not the CLI behavior. Update skill to present `wt-rm` as separate user decision.

**D-5: New code for Blockers evaluation.** Existing `_resolve_session_md_conflict()` handles task additive merge. Per-section strategies are new: squash for volatile sections, evaluate-and-tag for Blockers. All other strategies use keep-ours (trivial).

**D-6: worktree-merge-data-loss is execution dependency.** Its Track 1 (removal guard) and Track 2 (merge correctness) must be deployed before Phase 5. Design proceeds independently.

**D-7: Workflow gates as advisory preconditions.** `infer_state()` returns `(state, next_action, gate)` tuples. Gates are displayed, not enforced. Natural extension of next-action computation. Keeps planstate purely informational.

**D-8: Plan archive on demand.** Completed plans move to `agents/plan-archive.md` with paragraph summaries. Not in CLAUDE.md @-references — loaded at design skill A.1 and RCA sessions. On-demand loading makes richer entries affordable (no context budget pressure).

## Implementation Notes

### Phase 1: Plan State Inference (TDD)

**Module:** `src/claudeutils/planstate/inference.py`

**Core function:** `infer_state(plan_dir: Path) -> PlanState`

Scan order (highest status wins):
1. `orchestrator-plan.md` + `steps/` → `ready`
2. `runbook-phase-*.md` (glob) → `planned`
3. `design.md` → `designed`
4. `requirements.md` OR `outline.md` OR `problem.md` → `requirements`
5. No recognized artifacts → skip (not a plan)

Next action maps directly from status (see State Inference Rules table).

**Gate computation:** After status, query vet status and attach first applicable gate.

**Test strategy:** Parametrized tests with `tmp_path` fixtures creating various artifact combinations. Cover: each status level, edge cases (empty dirs, `reports/` only, mixed artifacts), next action derivation, gate attachment.

**Helper function extraction:** `list_plans(plans_dir: Path) -> list[PlanState]` scans all plan directories and returns inferred states. Replaces `get_plans_directories()` + `parse_jobs_md()` combination.

### Phase 2: Vet Staleness Detection (TDD)

**Module:** `src/claudeutils/planstate/vet.py`

**Core function:** `get_vet_status(plan_dir: Path) -> VetStatus`

For each source artifact found in `plan_dir`, look up expected report via naming convention table. Compare mtimes. Handle iterative reviews (highest-numbered file wins).

**Test strategy:** `tmp_path` fixtures with files at known mtimes (use `os.utime()`). Cover: stale, fresh, missing report, iterative review numbering, all source types.

**Integration with Phase 1:** `infer_state()` calls `get_vet_status()` to populate gate field.

### Phase 3: Cross-Tree Aggregation (TDD)

**Module:** `src/claudeutils/planstate/aggregation.py`

**Core function:** `aggregate_trees() -> AggregatedStatus`

Calls `git worktree list --porcelain`, parses output, collects per-tree data (commits, latest commit, dirty state, task summary). Runs `list_plans()` for each tree's `plans/` directory.

**Git interaction:** Uses `subprocess.run()` with `-C <tree_path>` for per-tree commands. Same pattern as worktree module's `_git()` helper.

**Test strategy:** Real git repos via `tmp_path` fixtures (same pattern as worktree test suite). Create main repo with worktrees, verify aggregation output. Cover: multiple trees, main-only, dirty/clean states, commit counting with and without session.md anchor.

### Phase 4: Upgraded wt-ls CLI (TDD)

**Location:** `src/claudeutils/worktree/cli.py` — modify `ls` command

Add `--porcelain` flag. Default: rich output using `aggregate_trees()`. Porcelain: existing behavior.

**New dependency:** `worktree/cli.py` imports from `planstate.aggregation`.

**Test strategy:** CLI output assertions (rich format structure, porcelain backward compatibility). Integration test with real worktrees verifying correct plan status display.

### Phase 5: Merge Strategies + Skill Update (mixed)

**TDD portion:** Per-section merge in `merge.py`, Blockers extraction in `session.py`.

Refactor `_resolve_session_md_conflict()` to:
1. Parse ours into sections using `find_section_bounds()`
2. For each section, apply strategy from classification table
3. Pending Tasks: existing additive logic (preserved)
4. Blockers: extract from theirs, tag with `[from: <slug>]`, append to ours
5. All others: keep ours (trivial)

**New function in session.py:** `extract_blockers(content: str) -> list[str]` — returns blocker items as line groups.

**General portion (non-TDD):**
- Worktree skill SKILL.md: Mode C step 3 update (no auto-rm)
- execute-rule.md STATUS: replace jobs.md reads with planstate calls. STATUS display reads `list_plans()` instead of `parse_jobs_md()`. Unscheduled Plans becomes: plans with no associated pending task (same logic, different data source). Note: Unscheduled Plans section also references jobs.md for status values — this fully transitions to planstate in Phase 5, with the jobs.md @-reference removal deferred to Phase 6.

**Dependency:** worktree-merge-data-loss Track 1 + Track 2 must be deployed first (D-6).

### Phase 6: jobs.md Elimination + Archive (mixed)

**TDD portion:** `validation/planstate.py` — new validator.

**General portion:**
- Create `agents/plan-archive.md` by migrating jobs.md Complete section
- Update handoff skill: plan completion writes to plan-archive.md
- Remove from CLAUDE.md: `@agents/jobs.md` reference
- Remove `validation/jobs.py` and CLI integration
- Remove `_resolve_jobs_md_conflict()` from `merge.py` (note: `_resolve_session_md_conflict` and `_resolve_learnings_md_conflict` remain; remove only the jobs call from `_phase3_merge_parent`)
- Remove jobs.md from `_check_clean_for_merge()` exempt_paths
- Remove jobs.md from session file exemptions in clean-tree check
- Update `focus_session()` if it references jobs.md
- Update worktree skill Mode B (parallel group analysis): reads planstate instead of jobs.md

### Affected Files Summary

| File | Phase | Change |
|---|---|---|
| `src/claudeutils/planstate/__init__.py` | 1 | New: public API |
| `src/claudeutils/planstate/models.py` | 1 | New: data models |
| `src/claudeutils/planstate/inference.py` | 1 | New: state inference |
| `src/claudeutils/planstate/vet.py` | 2 | New: staleness detection |
| `src/claudeutils/planstate/aggregation.py` | 3 | New: cross-tree collection |
| `src/claudeutils/worktree/cli.py` | 4 | Modify: ls upgrade |
| `src/claudeutils/worktree/merge.py` | 5 | Modify: per-section strategies |
| `src/claudeutils/worktree/session.py` | 5 | Modify: Blockers extraction |
| `agent-core/skills/worktree/SKILL.md` | 5 | Modify: Mode C no auto-rm |
| `agent-core/fragments/execute-rule.md` | 5 | Modify: STATUS uses planstate |
| `src/claudeutils/validation/planstate.py` | 6 | New: replaces jobs.py |
| `src/claudeutils/validation/cli.py` | 6 | Modify: swap validator |
| `src/claudeutils/validation/jobs.py` | 6 | Delete |
| `agents/plan-archive.md` | 6 | New: completed plan summaries |
| `agent-core/skills/handoff/SKILL.md` | 6 | Modify: archive instead of jobs.md |
| `agent-core/skills/design/SKILL.md` | 6 | Modify: A.1 loads archive |
| `CLAUDE.md` | 6 | Modify: remove jobs.md @-ref |
| `agents/jobs.md` | 6 | Delete |

### Testing Strategy

**All TDD phases:** Real git repos via `tmp_path` fixtures (established pattern from worktree test suite). No mocked subprocess for git operations.

**Test file organization:**
- `tests/test_planstate_inference.py` — Phase 1
- `tests/test_planstate_vet.py` — Phase 2
- `tests/test_planstate_aggregation.py` — Phase 3
- `tests/test_worktree_ls_upgrade.py` — Phase 4
- `tests/test_worktree_merge_sections.py` — Phase 5 (merge strategies)
- `tests/test_validation_planstate.py` — Phase 6

**Existing test impact:** `tests/test_validation_jobs.py` is deleted in Phase 6. `tests/test_worktree_merge_*.py` may need updates for Phase 5 merge strategy changes.

### Phase Type Classification

| Phase | Type | Rationale |
|---|---|---|
| 1: Plan state inference | TDD | New module with clear behavioral contracts |
| 2: Vet staleness | TDD | Mtime comparison logic needs edge case coverage |
| 3: Cross-tree aggregation | TDD | Git interaction correctness requires real-repo tests |
| 4: wt-ls CLI upgrade | TDD | Output format + backward compat needs regression tests |
| 5: Merge + skill | Mixed | Merge code = TDD; skill/doc edits = general |
| 6: Elimination + archive | Mixed | Validator = TDD; removals/migrations = general |

### Execution Model

- Phases 1-4: sonnet (standard TDD implementation)
- Phase 5 TDD: sonnet; Phase 5 general: sonnet (skill/doc editing, not architectural)
- Phase 6 TDD: sonnet; Phase 6 general: sonnet (mechanical removals)
- Skill edits in Phases 5-6: opus required (workflow/skill modifications per design directive)

## Dependencies

**External:** worktree-merge-data-loss Track 1 + Track 2 must be deployed before Phase 5 execution. Phases 1-4 can proceed independently.

**Internal:**
- Phase 2 depends on Phase 1 (planstate module must exist for vet integration)
- Phase 3 depends on Phases 1+2 (aggregates planstate + vet status)
- Phase 4 depends on Phase 3 (CLI consumes aggregation)
- Phase 5 depends on Phase 1 (execute-rule.md uses planstate)
- Phase 6 depends on Phases 1+5 (completes elimination after adoption)

## Risks

**R-1: Vet naming conventions.** Phase 2 assumes specific naming (outline.md → reports/outline-review.md). If conventions vary across plans, false staleness. Mitigation: conventions are codified as constants, tested against actual plan directories.

**R-2: Filesystem mtime reliability.** Git checkout and touch operations can modify mtime. Mitigation: documented limitation; mtime is sufficient for normal workflows, not adversarial cases.

**R-3: Blockers evaluation complexity.** Extracting and tagging blockers is mechanical, but determining continued relevance requires agent judgment. Mitigation: extract and tag — agent reviews at handoff.

## References

- `plans/workwoods/requirements.md` — functional and non-functional requirements
- `plans/workwoods/outline.md` — validated outline (8 decisions, all Qs resolved)
- `plans/workwoods/reports/explore-worktree-cli.md` — worktree CLI structure and behavior
- `plans/workwoods/reports/explore-session-jobs.md` — session.md and jobs.md usage patterns
- `plans/workwoods/reports/explore-plan-dirs.md` — plan directory artifacts and progression
- `plans/workwoods/reports/explore-worktree-update.md` — merge implementation and known bugs
- `plans/worktree-merge-data-loss/design.md` — execution dependency design

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/architecture.md` — module patterns (skip if not found in worktree)
- `plans/workwoods/reports/explore-worktree-cli.md` — current CLI implementation
- `plans/workwoods/reports/explore-plan-dirs.md` — artifact progression patterns
- `src/claudeutils/worktree/merge.py` — current merge implementation
- `src/claudeutils/worktree/session.py` — task block parsing
- `src/claudeutils/validation/jobs.py` — validator being replaced
- `src/claudeutils/validation/cli.py` — validator registration pattern

**Additional research allowed:** Planner may read test files for existing patterns and other validation modules for structural conventions.

## Next Steps

Route to `/runbook` for phase expansion. Per-phase type tagging: Phases 1-4 TDD, Phases 5-6 mixed.

Skill edits (worktree SKILL.md, handoff SKILL.md, execute-rule.md, design SKILL.md) in Phases 5-6: opus required.
