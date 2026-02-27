# Recall-Null Execution Outline

**Context:** Add null mode to when-resolve.py, propagate D+B gate anchoring and post-explore recall gates to pipeline skills.
**Classification:** plans/recall-null/classification.md
**Tier:** 2 — Lightweight Delegation

---

## Requirements Mapping

| Requirement | Phase | Items | Notes |
|-------------|-------|-------|-------|
| Null mode argument | 1 | 1.1, 1.2 | Behavioral code, TDD |
| D+B gate anchoring | 2 | 2.1-2.5 | Skill prose edits |
| Post-explore recall gate | 2 | 2.1, 2.4 | Where skills have exploration |

---

## Phase Structure

### Phase 1: Null mode implementation (type: tdd, model: sonnet)

**Objective:** Add `null` argument handling to when-resolve.py CLI so D+B gates have an equal-cost negative path.

- Cycle 1.1: null query exits silently
  - RED: CliRunner invokes `when_cmd` with `["null"]`. Assert exit 0, empty output.
  - GREEN: After `_collect_queries()`, filter null queries (bare "null" after `_strip_operator`). If filtered list is empty (all-null), return early — exit 0, no output. Also handle "when null" → stripped to "null" by existing operator logic.

- Cycle 1.2: null mixed with real queries
  - RED: CliRunner invokes `when_cmd` with `["null", "when writing recall artifacts"]`. Assert exit 0, output contains resolved content for real query only. Requires memory-index.md and a decision file in tmp_path fixture.
  - GREEN: Filter null entries from query list before `_resolve_queries()`. Only early-return when filtered list is empty. Mixed case proceeds with non-null queries.

**Test file:** `tests/test_when_null.py` (new — isolated from existing test_when_*.py files)

---

### Phase 2: Skill gate language (type: inline, model: opus)

**Objective:** Propagate D+B gate anchoring to all pipeline skills that perform recall. Add post-explore recall gates where exploration phases exist.

**Canonical pattern** (from /design A.2.5):

```
**Gate anchor (mandatory tool call on both paths):**
- **New entries found:** `agent-core/bin/when-resolve.py "when <trigger>" ...` — resolve into context
- **No new entries:** `agent-core/bin/when-resolve.py null` — no-op, proves gate was reached
```

**Post-explore pattern** (from /design A.2.5):

```
[Exploration] surfaces codebase areas not caught by [recall step]. Re-scan memory-index
(already in context) for entries relevant to domains discovered during [exploration].

**Gate anchor (mandatory tool call on both paths):**
- **New entries found:** `agent-core/bin/when-resolve.py "when <trigger>" ...` — resolve,
  append entry keys to recall artifact if forward value for downstream consumers
- **No new entries:** `agent-core/bin/when-resolve.py null` — no-op, proves gate was reached
```

**Edit map:**

- 2.1 `/requirements` SKILL.md
  - (a) Recall Pass section: `/recall all` Skill invocation is already a tool call. Add note: empty recall artifact is valid negative-path evidence (artifact still written, downstream sees "no entries").
  - (b) New section after step 2 "Lightweight Codebase Discovery": post-explore gate. Discovery via Glob/Grep may surface domains not anticipated during recall. Re-scan memory-index, resolve new entries, update recall artifact.

- 2.2 `/design` SKILL.md
  - Verify A.2.5 matches canonical pattern. Standardize wording if minor drift. Likely no-op or minimal.

- 2.3 `/runbook` SKILL.md (Tier 1/2 sections only)
  - Wrap existing "if artifact exists / if not, lightweight recall" into explicit D+B two-path structure. Current language has implicit skip path ("if no artifact exists" → agent may skip entirely). Negative path: no artifact AND no relevant entries → `when-resolve.py null`. Positive path: batch-resolve as written.
  - No post-explore gate for T1/2 (no exploration phase within runbook at these tiers).

- 2.4 `/runbook` references/tier3-planning-process.md
  - (a) Phase 0.5 step 1: already has `when-resolve.py` tool call. Add explicit D+B framing (both-paths language).
  - (b) New gate between Phase 0.5 step 3 (Glob/Grep verification) and Phase 0.75 (outline generation). Step 3 discovers actual file locations — may reveal modules not anticipated during step 1 recall. Canonical post-explore pattern.

- 2.5 `/inline` SKILL.md
  - Phase 2.3 Recall: wrap into D+B two-path structure. Negative path: no artifact AND no relevant memory-index entries → `when-resolve.py null`. Positive path: batch-resolve as written.
  - No post-explore gate (no exploration between recall and execution in /inline).

---

## Execution Model

**Dispatch protocol:**

| Phase | Agent | Model | Recall Artifact |
|-------|-------|-------|----------------|
| 1 (TDD) | test-driver (Task) | sonnet | `plans/recall-null/tdd-recall-artifact.md` |
| 2 (inline) | direct (session) | opus | In-context (loaded via /recall broad at session start) |

**Phase 1:** Piecemeal TDD dispatch — one cycle per test-driver invocation, resume between. Prompt includes: "Read `plans/recall-null/tdd-recall-artifact.md`, then batch-resolve ALL entries via `agent-core/bin/when-resolve.py`."

**Phase 2:** Direct edits in session. All decisions pre-resolved from existing A.2.5 pattern; insertion points identified per edit map. No delegation — pre-resolved prose propagation per `workflow-optimization.md §When Delegating Well-Specified Prose Edits`.

**Post-execution:**
- Corrector (Phase 4a): scope = `git diff --name-only $BASELINE`. Recall: `plans/recall-null/review-recall-artifact.md`
- Skill-reviewer: scope = modified skill files (cross-project context needed per `pipeline-contracts.md §When Reviewing Skill Deliverable`). Recall: `plans/recall-null/skill-review-recall-artifact.md`. Optional — corrector may suffice for standardized pattern propagation. Invoke if corrector flags skill-specific issues.

**Recall Injection:** Each prompt includes:
```
Read plans/recall-null/<type>-recall-artifact.md, then batch-resolve ALL entries via:
agent-core/bin/when-resolve.py "<entry-1>" "<entry-2>" ...
```

---

## Key Decisions Reference

- D-1: Null mode = silent exit 0 (`defense-in-depth.md §When Selecting Gate Anchor Tools`)
- D-2: D+B = mandatory tool call on both paths (`defense-in-depth.md §When Anchoring Gates With Tool Calls`)
- D-3: Post-explore = re-scan after Glob/Grep discovery (`/design A.2.5`)
- D-4: Direct opus for pre-resolved prose (`workflow-optimization.md §When Delegating Well-Specified Prose Edits`)
- D-5: Piecemeal TDD dispatch (`orchestration-execution.md §When Delegating TDD Cycles To Test-Driver`)
