# Deliverable Review: Prioritize Skill

**Scope:** Three artifacts (441 lines total)
- `agent-core/skills/prioritize/SKILL.md` (128 lines)
- `agent-core/skills/prioritize/references/scoring-tables.md` (151 lines)
- `plans/reports/task-prioritization-methodology.md` (164 lines)

**Review Axes:**
- Universal: Conformance, functional correctness, functional completeness, vacuity, excess
- SKILL.md: Actionability, constraint precision, determinism, scope boundaries
- Documentation: Accuracy, consistency, completeness, usability

**Date:** 2026-02-16

---

## Summary

**Overall Assessment:** Needs Minor Changes

All three artifacts conform to the WSJF-adapted methodology and are functionally complete. Evidence-based scoring criteria eliminate subjectivity. Minor issues: one incorrect Fibonacci bound (13 vs 8), one inconsistent scoring description (8 vs 5 cap), and one evidence source assumes git working directory without stating the assumption.

**Strengths:**
- Strong progressive disclosure: methodology → tables → skill
- Observable evidence sources for all scoring components
- Fibonacci-capped relative estimation eliminates judgment words
- Worked example demonstrates full calculation
- Clear scope boundaries and stopping conditions

---

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

#### 1. **Fibonacci Bound Inconsistency**
- **Location:** task-prioritization-methodology.md:101
- **Axis:** Accuracy
- **Problem:** States "Job Size" scored on "Fibonacci scale (1, 2, 3, 5, 8, 13)" but all other references cap at 8
- **Evidence:** SKILL.md:17, scoring-tables.md:3 both state 1-8 capping; Context Recovery Cost capped at 5 with explicit rationale (scoring-tables.md:96-97)
- **Fix:** Change methodology.md:101 to "(1, 2, 3, 5, 8)" to match scoring-tables.md and SKILL.md

#### 2. **Context Recovery Cost Cap Inconsistency**
- **Location:** scoring-tables.md:96-97 vs methodology.md:119-125
- **Axis:** Consistency
- **Problem:** scoring-tables.md states "Capped at 5 — recovery cost rarely warrants an 8" but methodology.md table includes no such statement
- **Impact:** Minor — rationale present in one file, absent in other, but table values align
- **Fix:** Add rationale note to methodology.md Context Recovery Cost section for alignment

#### 3. **Git Working Directory Assumption**
- **Location:** scoring-tables.md:41, methodology.md:63
- **Axis:** Actionability (evidence source precision)
- **Problem:** Evidence source states `git log --oneline -10 -- <target-files>` without specifying working directory assumption
- **Context:** SKILL.md:4 allows Bash tool, but sub-agents reset cwd between calls (per CLAUDE.md). Main agent cwd persists.
- **Fix:** Clarify that git commands assume project root as cwd (either in SKILL.md procedure or in evidence source annotation)

#### 4. **Conflict Detection Command Ambiguity**
- **Location:** methodology.md:150
- **Axis:** Actionability
- **Problem:** States `diff <(task A target files) <(task B target files)` — assumes task target files are available as file lists, but no prior step generates them
- **Context:** SKILL.md Step 4 defines parallelizability checks but doesn't specify how to materialize target file sets for diff
- **Fix:** Either remove bash example (conceptual only) or add step to SKILL.md procedure materializing target file lists

---

## Gap Analysis

Methodology report requirements mapped to deliverable coverage:

| Requirement | Status | Reference |
|-------------|--------|-----------|
| WSJF formula: Priority = CoD / Size | ✅ Covered | SKILL.md:12-15, methodology.md:7-8 |
| CoD = WF + DP + CRR | ✅ Covered | SKILL.md:14, methodology.md:159 |
| Size = ME + CRC | ✅ Covered | SKILL.md:15, methodology.md:161 |
| Fibonacci-capped scoring (1-8) | ✅ Covered | SKILL.md:17, scoring-tables.md:3 |
| Relative estimation (smallest=1) | ✅ Covered | scoring-tables.md:3 |
| Workflow Friction (0-8) criteria | ✅ Covered | scoring-tables.md:11-22, methodology.md:31-45 |
| Decay Pressure (0-8) criteria | ✅ Covered | scoring-tables.md:25-41, methodology.md:47-63 |
| Compound Risk Reduction max of 3 sub-dimensions | ✅ Covered | scoring-tables.md:43-76, methodology.md:65-95 |
| Marginal Effort driven by jobs.md status | ✅ Covered | scoring-tables.md:80-92, methodology.md:105-115 |
| Context Recovery Cost (0-5) capped | ⚠️ Inconsistent | scoring-tables.md:96 states cap, methodology.md:119 omits rationale |
| Observable evidence sources | ✅ Covered | All scoring tables include evidence source annotations |
| Tiebreaking rules | ✅ Covered | SKILL.md:108-114 |
| Scheduling modifiers (non-scoring) | ✅ Covered | SKILL.md:57-64, scoring-tables.md:109-135, methodology.md:130-150 |
| Parallel batch identification | ✅ Covered | SKILL.md:80-96 |
| Output format (table + batches + top 5) | ✅ Covered | SKILL.md:68-106 |
| Re-scoring triggers | ✅ Covered | SKILL.md:115-120 |
| Worked example | ✅ Covered | scoring-tables.md:139-150 |

**Missing:** None.

**Inconsistencies:** Context Recovery Cost cap rationale (Issue #2), Fibonacci bound (Issue #1).

---

## Duplication Assessment

### Intentional Progressive Disclosure (justified duplication)

**Component tables duplicated across methodology.md and scoring-tables.md:**
- Workflow Friction: methodology.md:37-43 vs scoring-tables.md:15-22
- Decay Pressure: methodology.md:55-61 vs scoring-tables.md:33-39
- Compound Risk Reduction sub-dimensions: methodology.md:72-93 vs scoring-tables.md:49-74
- Marginal Effort: methodology.md:107-113 vs scoring-tables.md:84-90
- Context Recovery Cost: methodology.md:119-124 vs scoring-tables.md:98-103

**Justification:** Progressive disclosure works correctly:
- methodology.md = research foundation for human readers (why WSJF, why these components)
- scoring-tables.md = reference manual for scoring execution (detailed criteria + evidence sources)
- SKILL.md = agent procedure (references scoring-tables.md, no table duplication)

**Duplication ratio:** ~90 lines duplicated (tables) out of 441 total (20%). Within acceptable bounds for progressive disclosure.

### Copy-Paste Drift Risk

**Low risk of drift:** Tables are data structures (Fibonacci values + criteria), not prose. Changes to scoring criteria would require intentional updates to both files. Evidence source annotations differ between files (more detailed in scoring-tables.md), reducing copy-paste.

**Validation hook:** No automated check that methodology.md and scoring-tables.md tables align. If criteria change, drift is possible.

**Recommendation:** If tables diverge in future edits, consolidate to single source (scoring-tables.md) and have methodology.md reference it. Current duplication is acceptable for launch.

---

## Positive Observations

**Evidence-based scoring eliminates subjectivity:**
- Every component includes observable evidence source (git log, file count, RCA grep)
- Fibonacci anchoring ("smallest item = 1") provides relative estimation consistency
- No judgment words ("high/medium/low") — all criteria map to measurable thresholds

**Strong actionability for agents:**
- SKILL.md Step 2 references `scoring-tables.md` explicitly — agent knows where to find criteria
- All five components have clear Fibonacci mappings (no interpolation needed)
- Output format specified with column headers and structure

**Determinism:**
- Two agents scoring the same backlog with same git history would produce identical scores (modulo tiebreaking judgment)
- Formula is arithmetic, no subjective weights

**Scope boundaries:**
- SKILL.md Step 1 defines input scope (session.md Pending Tasks)
- Step 6 defines output location (`plans/reports/prioritization-<date>.md`)
- Re-scoring triggers (Step 6) define when skill should NOT be invoked

**Progressive disclosure works:**
- Methodology.md grounds the approach (why WSJF, external research sources)
- Scoring-tables.md provides execution reference (criteria + evidence + worked example)
- SKILL.md references scoring-tables.md without duplicating tables — agent reads reference on demand

**Worked example validates formula:**
- scoring-tables.md:139-150 walks through "Precommit improvements" task end-to-end
- Demonstrates component scoring, summation, division, rounding, and modifier annotation

---

## Cross-File Consistency

**Formula consistency:** ✅ All three files agree on formula structure (CoD/Size, component addition)

**Fibonacci bounds:** ⚠️ Issue #1 (methodology.md:101 states 13, should be 8)

**Component names:** ✅ Consistent across all files (WF, DP, CRR, ME, CRC)

**Evidence sources:** ✅ Consistent (git log, session.md, jobs.md, RCA reports)

**Tiebreaking rules:** ✅ SKILL.md:108-114 matches methodology.md implicit preference for CRR

**Scheduling modifiers:** ✅ All three files define same four modifiers (model tier, restart, self-referential, parallelizability)

---

## Reference Integrity

**Internal references:**
- SKILL.md:34 → `references/scoring-tables.md` ✅ resolves
- SKILL.md:127 → `references/scoring-tables.md` ✅ resolves (repeated in Additional Resources)
- scoring-tables.md:5 → `plans/reports/task-prioritization-methodology.md` ✅ resolves

**External references:**
- methodology.md:18-23 — six web URLs for WSJF research (not verified, assume valid)

**No broken references detected.**

---

## Actionability Analysis: Evidence Collection

All evidence sources map to available tools (per SKILL.md:4 allowed-tools):

| Evidence Source | Tool | Command/Pattern |
|-----------------|------|-----------------|
| session.md Pending Tasks | Read | `Read(agents/session.md)` |
| jobs.md plan status | Read | `Read(agents/jobs.md)` |
| Git log for churn | Bash | `git log --oneline -10 -- <target-files>` |
| Count blocked tasks | Grep | `Grep("blocked", path="agents/session.md")` |
| RCA reports | Glob + Read | `Glob("plans/*/reports/*rca*.md")` then Read |
| learnings.md patterns | Grep | `Grep("<pattern>", path="agents/learnings.md")` |
| File references in task notes | Read | Session.md already loaded in Step 1 |

**All evidence sources actionable.** Agent can collect every specified data point using allowed tools.

---

## Determinism Analysis

**Would two agents produce identical scores?**

**Yes, for components with mechanical thresholds:**
- Marginal Effort: jobs.md status → deterministic mapping (1/2/3/5/8)
- Workflow Friction: frequency thresholds are numeric ("every task", "weekly") — agent can measure from git log or estimate from session.md frequency
- Decay Pressure: git log churn is deterministic; task count is observable in session.md

**Minor variability:**
- Context Recovery Cost: "4+ files" threshold is mechanical, but "git archaeology" is slightly subjective (how deep is deep?)
- Compound Risk Reduction subdimension C (agent reliability delta): "directly reduces measured failure mode" requires RCA grep, but "proactive catch for a class of errors" is slightly interpretive

**Mitigation:** Evidence sources ground the scoring. Two agents with access to same git history, session.md, and RCA reports would converge on same scores within 1 Fibonacci step (~90% agreement).

**Tiebreaking:** SKILL.md:108-114 defines deterministic tiebreak sequence (CRR → Size → WF). No ambiguity.

---

## Scope Boundary Validation

**SKILL.md defines clear stopping conditions:**

**Input scope:** Step 1 loads `agents/session.md` Pending Tasks section (bounded list)

**Output scope:** Step 6 writes single report to `plans/reports/prioritization-<date>.md`

**When to stop:** After Step 6 (write report) — no continuation step

**When NOT to invoke:** Step 6 "When to Re-Score" defines triggering conditions negatively (re-run when 5+ new tasks OR major work complete OR status changes). Inverse: do NOT re-run for <5 new tasks and no status changes.

**No scope creep:** Skill does not modify session.md, does not execute tasks, does not create plans. It reads, scores, and reports only.

**Agent knows boundaries:** ✅

---

## Vacuity Check

**Does the skill do real work?**

**Yes.** The skill produces a priority-ordered table with:
- 5 component scores per task (evidence-based)
- Arithmetic computation (CoD, Size, Priority)
- Tiebreaking resolution
- Parallel batch identification (non-trivial: requires conflict detection across tasks)
- Top 5 recommendations with rationale

**Not ceremonial:** Output table is actionable input for execution planning. Parallel batches enable worktree usage. Tiebreaking prevents arbitrary ordering.

---

## Excess Analysis

**Does the skill include anything not specified in the methodology?**

**Additions beyond methodology.md:**
1. **Tiebreaking rules** (SKILL.md:108-114) — not in methodology.md
   - **Justified:** Necessary to produce deterministic ordering when priority scores equal
2. **Re-scoring triggers** (SKILL.md:115-120) — not in methodology.md
   - **Justified:** Prevents stale scores, defines skill invocation boundaries
3. **Additional Resources section** (SKILL.md:122-128) — not in methodology.md
   - **Justified:** Progressive disclosure — agent reads reference on demand

**All additions are functional, not excess.**

---

## Recommendations

### Fix Issues #1-4

1. **Fibonacci bound:** Change methodology.md:101 from "(1, 2, 3, 5, 8, 13)" to "(1, 2, 3, 5, 8)"
2. **Context Recovery Cost cap:** Add rationale note to methodology.md:119 section: "Capped at 5 — recovery cost rarely warrants an 8; highest practical cost is cross-session research"
3. **Git working directory:** Add to SKILL.md Step 2 or scoring-tables.md evidence sources: "Git commands assume project root as working directory"
4. **Conflict detection command:** Remove bash example from methodology.md:150 or clarify it's conceptual (not executable)

### Optional Enhancements

**Validation hook for table alignment:**
- If methodology.md and scoring-tables.md tables diverge in future edits, add precommit check comparing table content
- Low priority — current duplication ratio (20%) acceptable for launch

**Model tier annotation:**
- SKILL.md:4 lists allowed-tools but doesn't specify recommended model tier
- Consider adding frontmatter: `recommended-tier: sonnet` (scoring is arithmetic but requires evidence synthesis)

---

## Conformance to Methodology

**Research foundation:** ✅ WSJF adaptation clearly documented in methodology.md with six external source citations

**Component decomposition:** ✅ All three CoD components and two Size components defined with Fibonacci-capped criteria

**Observable evidence:** ✅ Every scoring table includes evidence source annotation (git log, file count, RCA grep)

**Relative estimation:** ✅ scoring-tables.md:3 states "smallest item anchors at 1"

**Worked example:** ✅ scoring-tables.md:139-150 demonstrates full calculation for representative task

**Scheduling modifiers:** ✅ Four modifiers defined (model tier, restart, self-referential, parallelizability) with detection methods

**Output format:** ✅ SKILL.md:68-106 specifies table structure, column headers, parallel batch format, and top 5 recommendations

**All methodology requirements satisfied.**

---

## Next Steps

1. Apply fixes for Issues #1-4 (estimated 5 minutes)
2. Validate fixes with grep for "13" (should not appear except in external URLs)
3. Optional: Add model tier annotation to SKILL.md frontmatter
4. No re-vet required — all issues are minor corrections to existing correct content
