# Deliverable Review: Skill Definitions (workflow-rca-fixes)

**Date:** 2026-02-15
**Scope:** 7 skill files + 3 reference files implementing FRs 2, 3, 4, 6, 10, 12, 13, 14, 15, 19
**Methodology:** Agentic prose axes (conformance, functional correctness, completeness, vacuity, excess, actionability, constraint precision, determinism, scope boundaries)

---

## Summary

- Files reviewed: 10
- Critical findings: 1
- Major findings: 4
- Minor findings: 6
- Total: 11

---

## agent-core/skills/memory-index/SKILL.md (290 lines, FR-13)

### Critical

**C1: Index content drifted from canonical source** (~line 38-290)
- Axis: Functional correctness
- The skill contains a sync comment `<!-- Synced from agents/memory-index.md -->` but the index content has diverged from the canonical `agents/memory-index.md` in two ways:
  1. **Missing entries:** 3 entries from `agents/decisions/orchestration-execution.md` were added to the canonical after the skill was snapshotted: `/when local recovery suffices`, `/when global replanning is needed`, `/when item-level escalation blocks execution`. These are FR-17-adjacent entries that sub-agents cannot discover.
  2. **Section ordering mismatch:** The skill places `pipeline-contracts.md` entries before `deliverable-review.md`, while the canonical places them after `operational-practices.md` and `orchestration-execution.md`. The `operational-practices.md` and `orchestration-execution.md` sections are reordered relative to canonical.
- Impact: Sub-agents using this skill get a stale index snapshot. When they invoke `when-resolve.py` with a trigger from a missing entry, the lookup succeeds (it reads the canonical file), but the sub-agent would never discover the trigger because it is not in their injected index. Discovery is the primary function of the skill.
- Severity: Critical because it undermines FR-13's core purpose (sub-agent memory discovery).

### Major

**M1: No automated sync mechanism documented** (~line 35)
- Axis: Functional completeness
- The sync comment says "update both when index changes" but there is no script, recipe, or pre-commit check to detect drift. Given the file is 290 lines of manually-synced content, drift is inevitable (and already occurred).
- The design spec says "wraps agents/memory-index.md with Bash transport prolog" -- wrapping implies the index content should stay in sync, but no enforcement mechanism exists.

### Minor

**m1: Navigation syntax not included in transport prolog** (~line 12-31)
- Axis: Functional completeness
- The canonical memory-index.md includes navigation syntax (`/when .Section Title` for section lookup, `/when ..file.md` for full file access). The skill's Bash transport prolog shows only basic `when "<trigger>"` invocation. Sub-agents may not discover navigation features.
- Mitigated: The canonical index header (which contains this syntax) is not part of the `## agents/decisions/` section, so it's arguably outside the index content scope. But sub-agents have no other way to learn about `.Section` and `..file.md` syntax.

---

## agent-core/skills/project-conventions/SKILL.md (39 lines, FR-12)

### Minor

**m2: Design specifies ~400 tokens, actual file is ~1400 bytes (~350 tokens)** (~line 1-39)
- Axis: Conformance
- File is 1403 bytes. At ~4 chars/token, this is approximately 350 tokens -- within range of the design's "~400 tokens" target. No actual issue; noting for completeness that the estimate was reasonable.
- Severity: Minor (informational, no action needed).

**m3: Omits code-removal rules** (~line 1-39)
- Axis: Functional completeness
- FR-12 in the requirements says "Wrap key fragments (deslop, error-handling, code-removal)". The design refined this to "deslop + token-economy + tmp-directory". The project-conventions skill follows the design (deslop, token-economy, tmp-directory) but omits `code-removal` mentioned in requirements. Design decision (code-removal moved to error-handling or dropped) -- not a design conformance issue since the design explicitly specifies the three included topics.
- Severity: Minor (requirements-to-design gap, not design-to-implementation gap).

No other findings. The skill is well-structured: concise, actionable rules without ceremony. Each section distills the source fragment to its essential rules.

---

## agent-core/skills/error-handling/SKILL.md (20 lines, FR-12)

No findings. The skill accurately captures error suppression rules with the `|| true` exception. At ~100 tokens, it matches the design's target. Description frontmatter correctly scopes it to "bash-heavy agents."

---

## agent-core/skills/review-plan/SKILL.md (504 lines, FR-2)

### Minor

**m4: Section 11.1 General vacuity detection has redundant bullet** (~line 273-278)
- Axis: Excess
- Lines 274-276 list three general detection bullets, then line 277 adds a fourth bullet labeled "**Behavioral vacuity detection:**" that restates the same check as line 275 ("Step N+1 produces outcome achievable by extending step N alone -- merge"). The behavioral vacuity detection bullet is a more verbose restatement of the preceding bullet.
- Impact: Adds ~30 words without new information. An agent following both bullets would do the same check twice.

**m5: Section 11.3 Density general check uses "LOC delta" threshold without calibration context** (~line 293)
- Axis: Constraint precision
- "`Adjacent steps on same artifact with <20 LOC delta`" -- the 20 LOC threshold appears without rationale or calibration guidance. For prose artifacts (which this plan exclusively produces), "LOC" is less meaningful than for code. An agent reviewing a prose-edit runbook might not know how to interpret "20 LOC delta" for markdown files.
- Severity: Minor. The threshold is borrowed from the design/runbook-review axes and is reasonable for code-centric runbooks. For prose runbooks specifically, the heuristic may not apply, but this is a design limitation not an implementation error.

No critical or major findings. All three sections (11.1, 11.2, 11.3) have explicit `**General:**` bullet groups as required by FR-2.

---

## agent-core/skills/runbook/SKILL.md (824 lines, FR-3, FR-4, FR-6)

### Major

**M2: References section does not list general-patterns.md** (~line 806-809)
- Axis: Functional completeness (FR-4)
- The References section at line 806-809 lists: `patterns.md`, `anti-patterns.md`, `error-handling.md`, `examples.md`. The new `general-patterns.md` file created by FR-4 (126 lines, granularity criteria, prerequisite validation, step structure template) is not listed. The file exists on disk at `agent-core/skills/runbook/references/general-patterns.md` but is not discoverable through the skill's reference list.
- Impact: Agents loading the runbook skill see no reference to general-patterns.md. The file becomes orphaned documentation that exists but is never pointed to.

**M3: Cycle/Step Ordering Guidance references patterns.md but not general-patterns.md** (~line 719)
- Axis: Functional completeness (FR-4)
- Line 719: `See references/patterns.md for granularity criteria, numbering, common patterns.` But granularity criteria for general steps are in `general-patterns.md`, not `patterns.md`. An agent looking for general-step granularity guidance would read `patterns.md` and find only TDD patterns, missing the general-step guidance.
- Related to M2 -- both stem from FR-4 creating a new reference file without updating the skill's cross-references.

### Minor

**m6: Phase 0.95 LLM gate density check is TDD-specific** (~line 345)
- Axis: Functional correctness (FR-3)
- The gate checks: "Density: adjacent items on same function with <1 branch difference?" This is the TDD-specific density heuristic. For general outlines (which this plan was), density should check "adjacent items on same artifact with <20 LOC delta" or "multi-step sequences collapsible to single step." The gate runs before type-specific expansion, so it should use type-appropriate checks.
- Severity: Minor because the gate covers vacuity, ordering, and checkpoints type-neutrally. Only density uses TDD-specific language. In practice, most outlines at Phase 0.95 are pre-type-expansion, so the function-level heuristic partially applies.

FR-6 (Phase 1.4 deletion): Confirmed complete. No references to "Phase 1.4" or "file size awareness" remain in the file.

---

## agent-core/skills/design/SKILL.md (367 lines, FR-14, FR-15, FR-19)

### Major

**M4: Agent-name validation uses hardcoded directory list** (~line 199)
- Axis: Determinism (FR-19)
- The validation says: "Glob `agent-core/agents/*.md` and `.claude/agents/*.md`". This misses agents defined in plugin directories (`.claude/plugins/*/agents/`) or symlinked from other locations. If the project adds agent definitions in new locations, this check would silently miss them.
- Severity: Major because false negatives (missed agent references) are the exact class of defect FR-19 was created to prevent. The design spec uses the same hardcoded list, so this is design-conformant but the validation could be more robust.
- Mitigated: Current project only defines agents in these two directories, so the practical impact is currently zero.

### Minor

**m7: Density checkpoint heuristic range is a rough guideline** (~line 189)
- Axis: Constraint precision (FR-14)
- "items-per-phase x avg-LOC-per-item should fall in the 100-300 range" -- this product-based heuristic works for code phases but is harder to apply to prose-edit phases where "LOC per item" is variable and hard to estimate pre-design.
- Severity: Minor. The heuristic provides a useful sanity check even if imprecise for prose work.

FR-15 (Repetition helper prescription): Present at line 192-194. Specifies 5-repetition threshold with rationale. Actionable: "recommend extracting a helper function or script."

FR-19 (Late-addition completeness check): Present at line 204-211. Specifies traceability and mechanism as two required attributes. Includes grounding reference (FR-18 incident).

All three FR-14, FR-15, FR-19 additions are present and conform to design specifications.

---

## agent-core/skills/orchestrate/SKILL.md (462 lines, FR-10)

### Minor

**m8: Template enforcement guidance uses MUST without mechanical enforcement** (~line 156-161)
- Axis: Actionability (FR-10)
- The template enforcement section says "MUST provide structured IN/OUT scope" and "Fail loudly if template fields empty" but does not specify what "fail loudly" means mechanically. The orchestrator is a weak pattern agent -- it needs a concrete action: "If IN list is empty or contains only prose (no bullet items), STOP orchestration and report: 'Checkpoint template incomplete: IN scope must be a bulleted list of concrete artifacts.'"
- Severity: Minor. The MUST constraints are clear enough for a sonnet-class orchestrator to follow. The "fail loudly" language is slightly vague but the intent is unambiguous.

No other findings. The checkpoint delegation template at lines 133-154 is well-structured with explicit IN/OUT/Changed/Requirements fields. The enforcement guidance at lines 156-161 adds the validation layer FR-10 requires.

---

## agent-core/skills/runbook/references/general-patterns.md (126 lines, FR-4)

No findings. The file provides:
- Granularity criteria (atomic/composable/complex with when-to-split and when-to-merge)
- Prerequisite validation patterns (creation, transformation, investigation gates)
- Step structure template with all required fields

Content is actionable, non-vacuous, and deterministic. Each pattern has a concrete heuristic and example.

---

## agent-core/skills/runbook/references/anti-patterns.md (34 lines, FR-4)

### Minor

**m9: General step anti-patterns section has only 6 entries** (~line 23-33)
- Axis: Functional completeness
- The TDD anti-patterns section (original) has 9 entries. The new general step section has 6 entries. While this is not inherently a problem (general steps have fewer failure modes), the section could benefit from coverage of: steps with missing Error Conditions, steps that validate only structure (which IS included), and steps that bundle multiple file types requiring different reviewers.
- Severity: Minor. The 6 entries cover the most important anti-patterns. The "structure-only validation" entry particularly addresses the conformance gap from RCA #5.

---

## agent-core/skills/runbook/references/examples.md (344 lines, FR-4)

### Minor

**m10: General step examples reference workflow-rca-fixes plan** (~line 246, 287, 325)
- Axis: Scope boundaries
- Both general step examples use `plans/workflow-rca-fixes/reports/` as the report location. While this makes them grounded in real work, it ties the reference examples to a specific completed plan rather than using generic placeholders like the TDD example does (which uses `plans/auth-feature/`).
- Severity: Minor. The examples are functional and correct. Using real plan names as examples is arguably better (demonstrates real usage) than generic placeholders.

No other findings. The creation step example (vet-taxonomy) and transformation step example (Phase 1.4 deletion) demonstrate the key distinction between investigation-requiring and self-contained steps.

---

## Cross-Cutting Observations

**Positive patterns across all files:**
- All skills have correct frontmatter (`user-invocable: false` for injection skills, proper `description` fields)
- Deslop standards met: no hedging, no preamble, no ceremonial prose
- Token economy followed: file references used instead of content repetition
- Scope boundaries explicit in each skill

**Systemic gap:**
- The `general-patterns.md` reference file is well-crafted but orphaned from the runbook skill's discovery path (M2, M3). This is a single root cause (FR-4 created the file but did not update the skill's cross-references) producing two findings.

**Memory-index drift (C1) is a process issue:**
- The memory-index skill was created as a point-in-time snapshot. New entries added to the canonical `agents/memory-index.md` during subsequent workflow phases were not propagated to the skill. This is expected given C-1 (prose edits only, no automation), but the sync comment creates an implicit contract that is already broken.
