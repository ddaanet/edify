# Update Prioritize Skill

## Requirements

### Functional Requirements

**FR-1: Replace `list_plans()` ad-hoc Python with CLI**
The prioritize skill (SKILL.md Step 1) currently instructs agents to call `list_plans(Path('plans'))` — an ad-hoc Python import. Replace with `claudeutils _worktree ls` which already provides plan names, statuses, and next actions. The skill needs plan status to score Marginal Effort; `_worktree ls` rich output includes `[status]` per plan.

Acceptance criteria:
- SKILL.md Step 1 references `claudeutils _worktree ls` (or `--porcelain`) instead of `list_plans()`
- Agent no longer needs to write ad-hoc Python to get plan statuses
- All plan statuses currently available from `list_plans()` remain accessible

**FR-2: Extract scoring arithmetic into prototype script**
Move the WSJF scoring computation (CoD/Size formula, tiebreaking, rounding) from agent-executed arithmetic to a deterministic script at `plans/prototypes/score.py`. Agent produces JSON input with per-task component scores; script computes CoD, Size, Priority, applies tiebreaking, sorts, and outputs a markdown table.

Acceptance criteria:
- Script accepts JSON on stdin with per-task score components (WF, DP, CRR, ME, CRC)
- Script outputs markdown priority table (same format as SKILL.md Step 5)
- Tiebreaking rules (CRR → Size → WF) applied deterministically
- Rounding to one decimal place
- Exit code 0 on success, non-zero on malformed input

**FR-3: Update SKILL.md to use prototype for computation**
Revise the skill procedure so the agent's role is evidence collection and scoring judgment, while arithmetic and formatting are delegated to the prototype script.

Acceptance criteria:
- Steps 1-2 (load inventory, score components) remain agent work (requires judgment)
- Step 3 (calculate) delegates to `python3 plans/prototypes/score.py`
- Step 5 (generate output) consumes script output rather than manually constructing table
- Scoring tables reference remains unchanged (agent still needs criteria for judgment)

### Non-Functional Requirements

**NFR-1: JSON input schema**
Agent-produced input must be unambiguous to parse. JSON eliminates markdown-parsing edge cases. Schema should be minimal — flat array of task objects with named score fields.

**NFR-2: Markdown output for reports**
CLI output is markdown — consumed by both agents (for report writing) and humans (in plan reports). Matches the LLM-native CLI convention (stdout markdown, no stderr).

### Constraints

**C-1: LLM-native CLI conventions**
The `_prioritize` command is internal/hidden (underscore prefix). All output to stdout as markdown. Exit code carries success/failure. Error messages are facts-only, no suggestions (per `when cli error messages are llm-consumed`).

**C-2: Two-phase delivery**
Phase 1 (this scope): Create `plans/prototypes/score.py` and update SKILL.md to use it. Prototype scripts don't need runbooks, TDD, or test files per `when routing prototype work through pipeline`. Phase 2 (future scope): Promote to `claudeutils _prioritize score` CLI command with Click group, tests, and pyproject.toml wiring.

### Out of Scope

- Parallel batch identification — remains agent work (requires file-set conflict analysis)
- Scheduling modifier detection — remains agent work (requires session.md parsing judgment)
- Scoring criteria changes — tables and methodology unchanged
- Evidence collection automation — agent reads git log, session.md, RCA reports as before
- `_worktree ls` output format changes — consume existing format as-is

### Dependencies

- `claudeutils _worktree ls` — must provide plan status in parseable form (already does via rich output `[status]`)
- `PlanState` model in `src/claudeutils/planstate/models.py` — may be useful for type definitions but CLI can be independent

### References

- `agent-core/skills/prioritize/SKILL.md` — current skill being updated
- `agent-core/skills/prioritize/references/scoring-tables.md` — scoring criteria (unchanged)
- `plans/reports/deliverable-review-prioritize.md` — prior review findings
- `plans/update-prioritize-skill/recall-artifact.md` — recall entries informing requirements
