# Cross-Skill Consistency Review: /inline Integration

**Date:** 2026-02-27
**Scope:** design, runbook, inline, orchestrate, deliverable-review
**References:** continuation-passing.md, pipeline-contracts.md

---

## 1. Routing Correctness

### /design Phase B and C.5 invoke /inline — PASS

- Phase B (line 331): `invoke /inline plans/<job> execute`
- Phase C.5 (line 424): `Invoke /inline plans/<job> execute`
- Both use `execute` entry point, consistent with /inline entry point table (line 26)

### /runbook Tier 1 and Tier 2 invoke /inline — PASS

- Tier 1 (line 122): `Invoke /inline plans/<job> execute`
- Tier 2 (line 138): `invoke /inline plans/<job> execute`
- Both use `execute` entry point

### /runbook Tier 3 does NOT invoke /inline — PASS

- Tier 3 (line 169): `Planning process below — existing pipeline unchanged`
- Routes to prepare-runbook.py (line 204) then `/handoff --commit` (line 215)
- No /inline reference in Tier 3

### /inline description mentions callers — PASS

- Description (line 5-7): "when /design and /runbook route Tier 1/2 execution-ready work"
- Body (line 17): "Replaces ad-hoc execution sequences in /design Phase B/C.5 and /runbook Tier 1/2"

---

## 2. Continuation-Passing Alignment

### /inline frontmatter matches table — PASS

- Frontmatter (lines 10-12): `cooperative: true`, `default-exit: ["/handoff --commit", "/commit"]`
- Table entry: `/inline` | `["/handoff --commit", "/commit"]` | Inline execution lifecycle (Tier 1/2)
- Match confirmed

### /orchestrate frontmatter matches table — PASS

- Frontmatter (lines 6-8): `cooperative: true`, `default-exit: ["/handoff --commit", "/commit"]`
- Table entry: `/orchestrate` | `["/handoff --commit", "/commit"]`
- Match confirmed

### /design frontmatter — FAIL (Major)

- **Expected:** `continuation:` block with `cooperative: true` and `default-exit: ["/handoff --commit", "/commit"]`
- **Actual:** No `continuation:` block in frontmatter (lines 1-10)
- **Table claim:** continuation-passing.md line 69 lists `/design` with default-exit `["/handoff --commit", "/commit"]`
- **Body evidence:** /design does use `/handoff [CONTINUATION: /commit]` at lines 335, 425 — the behavior exists but isn't declared in frontmatter
- **Impact:** Hook-based continuation parsing may not recognize /design as cooperative. The continuation-passing.md "Adding Continuation to a New Skill" checklist (line 136) says step 1 is "Add continuation: block to YAML frontmatter."

### /runbook frontmatter — FAIL (Major)

- **Expected:** `continuation:` block with `cooperative: true` and `default-exit: ["/handoff --commit", "/commit"]`
- **Actual:** No `continuation:` block in frontmatter (lines 1-15)
- **Table claim:** continuation-passing.md line 70 lists `/runbook` with default-exit `["/handoff --commit", "/commit"]`
- **Body evidence:** /runbook Tier 3 Phase 4 tail-calls `/handoff --commit` (line 215) — the behavior exists but isn't declared in frontmatter
- **Impact:** Same as /design — undeclared cooperative status

### /design lacks Continuation section in body — FAIL (Minor)

- /inline has explicit `## Continuation` section (lines 167-178)
- /orchestrate has explicit `## Continuation Protocol` section (lines 291-294)
- /design has no such section — continuation behavior is implicit in routing actions (lines 331-335, 424-425)
- Lower severity because /design's exit paths are well-defined at their points of use

### /runbook lacks Continuation section in body — FAIL (Minor)

- Same pattern: /runbook Phase 4 tail-calls `/handoff --commit` (line 215) but has no explicit `## Continuation` section
- Lower severity: Tier 3 has a single, clear exit path

---

## 3. Allowed-Tools Consistency

### /design has Skill — PASS

- Line 8: `allowed-tools: Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch, Skill`

### /runbook has Skill — PASS

- Line 7: `allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, ...)`

### /inline has Skill — PASS

- Line 8: `allowed-tools: Task, Read, Write, Edit, Bash, Grep, Glob, Skill`

### /orchestrate has Skill — PASS

- Line 4: `allowed-tools: Task, Read, Write, Bash(git:*), Skill`

### /deliverable-review lacks Skill — PASS (not required)

- Line 8-15: `allowed-tools: Task, Read, Grep, Glob, Bash, Write`
- /deliverable-review is not a cooperative skill in the continuation table
- Does not tail-call other skills
- Not needing Skill is correct for its role

---

## 4. Execution Lifecycle Coverage

### Simple path — PASS

- /design line 118-123: Simple routes to recall-explore-execute inline, no /inline
- Correct: Simple work doesn't need lifecycle wrapper (no corrector, no triage feedback)

### Moderate path — PASS

- /design line 124: Moderate routes to `/runbook`
- /runbook Tier 1 (line 122): routes to `/inline plans/<job> execute`
- /runbook Tier 2 (line 138): routes to `/inline plans/<job> execute`
- Complete chain: /design (moderate) -> /runbook -> /inline

### Complex path (design-sufficient) — PASS

- /design Phase B sufficiency gate (line 331): execution-ready -> `/inline plans/<job> execute`
- /design Phase B (line 333-335): not execution-ready -> `/runbook`
- /runbook Tier 1/2 -> /inline, Tier 3 -> prepare-runbook.py -> /orchestrate
- No gaps

### Complex path (full design) — PASS

- /design Phase C.5 (line 424): execution-ready -> `/inline plans/<job> execute`
- /design Phase C.5 (line 425): not execution-ready -> `/handoff [CONTINUATION: /commit]` with /runbook as next task
- Same downstream chain as moderate

### Defect path — PASS

- /design line 126: Defect -> structured-bugfix workflow
- No /inline invocation — correct (investigation structure, not lifecycle execution)

### No execution gap between /design and /inline — PASS

- Every execution-ready path in /design explicitly invokes `/inline plans/<job> execute`
- Every not-ready path routes to `/runbook` or `/handoff` with continuation
- No path says "execute" without naming /inline or /orchestrate

---

## 5. Downstream Consumer Sections

### /design mentions both /runbook and /inline — PASS

- Lines 18-19: Downstream Consumers section explicitly names both:
  - Planning: `/runbook`
  - Execution: `/inline` with specific references to Phase B and C.5

### /runbook mentions /inline and /orchestrate — PARTIAL PASS (Minor)

- /runbook Tier 1 (line 122) and Tier 2 (line 138) reference /inline
- /runbook Tier 3 Phase 4 (line 204-215) references prepare-runbook.py -> /orchestrate flow
- However: /runbook has no explicit "Downstream Consumers" section. /orchestrate and /inline are mentioned inline at their routing points, not in a structured summary
- Minor: the routing is clear at each point of use, but a summary section would improve navigability

---

## 6. Deliverable-Review Integration

### /inline chains to /deliverable-review via pending task — PASS

- /inline Phase 4c (lines 148-153): Creates pending task in session.md format
- Task format: `- [ ] **Deliverable review: <job>** — /deliverable-review plans/<job> | opus | restart`
- Not a direct invocation — handoff captures it from conversation context

### /deliverable-review doesn't need /inline awareness — PASS

- No references to /inline in deliverable-review/SKILL.md
- Correct: /deliverable-review reviews artifacts post-execution, source-agnostic

### /orchestrate also chains to /deliverable-review via pending task — PASS

- /orchestrate lines 257-261: Creates pending task in same format as /inline
- Consistent approach between /inline and /orchestrate

---

## Summary

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Routing correctness | PASS (all 4 checks) |
| 2 | Continuation-passing alignment | 2 Major, 2 Minor issues |
| 3 | Allowed-tools consistency | PASS (all 5 checks) |
| 4 | Execution lifecycle coverage | PASS (all 5 paths) |
| 5 | Downstream consumer sections | 1 Minor issue |
| 6 | Deliverable-review integration | PASS (all 3 checks) |

### Issues Found

| # | Severity | Skill | Issue | Fix |
|---|----------|-------|-------|-----|
| 1 | Major | /design | Missing `continuation:` frontmatter block. Table in continuation-passing.md claims it's cooperative, but frontmatter doesn't declare it. | Add `continuation:` block: `cooperative: true`, `default-exit: ["/handoff --commit", "/commit"]` |
| 2 | Major | /runbook | Missing `continuation:` frontmatter block. Same gap as /design. | Add `continuation:` block: `cooperative: true`, `default-exit: ["/handoff --commit", "/commit"]` |
| 3 | Minor | /design | No explicit `## Continuation` body section. Exit behavior is scattered across Phase B (line 331-335) and C.5 (line 424-425). | Add `## Continuation` section at end of skill with consumption protocol |
| 4 | Minor | /runbook | No explicit `## Continuation` body section. Exit behavior is in Phase 4 (line 215) only. | Add `## Continuation` section at end of skill with consumption protocol |
| 5 | Minor | /runbook | No "Downstream Consumers" summary section. /inline and /orchestrate are mentioned inline but not in a structured overview. | Add section after H1 matching /design's format |

### Assessment

Routing correctness and execution lifecycle coverage are solid — the /inline integration achieved its primary goal of eliminating ad-hoc execution sequences. The pipeline-contracts.md T6.5 row is present and correctly describes the inline transformation.

The major issues (1, 2) are structural: /design and /runbook predate the continuation-passing protocol and were never retrofitted with frontmatter declarations. The behavioral exit paths exist in their bodies, but the frontmatter — which hooks and tooling may inspect programmatically — doesn't declare cooperative status. This is the "Pipeline integration" pending task's scope (continuation-passing.md table entry for /inline was deferred from skill creation, but /design and /runbook entries are already in the table without matching frontmatter).

Minor issues (3, 4, 5) are consistency gaps that don't affect correctness but reduce navigability.
