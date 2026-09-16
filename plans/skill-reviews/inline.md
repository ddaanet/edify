# plugin-dev:skill-reviewer on plugin/skills/inline (2026-09-15)

Reply saved verbatim-in-substance by the calling session; findings are from reading only, not verified.

## Critical

1. **/design → `/inline plans/<job> execute` handoff cannot pass Phase 1.** /design writes `classification.md` (design SKILL.md ~129) and does not commit on the execution-ready branches (write-outline.md ~226 vs 228, write-design.md ~88 vs 89); the Simple route implements inside /design (design SKILL.md ~136-137). Phase 1 then stops on a dirty tree (inline SKILL.md ~41), or, if committed past, the baseline (~52) postdates the implementation and the Phase 4a diff (~111) and triage (~157) are empty. Options: (a) /design commits planning artifacts before chaining and stops implementing on Simple; (b) the execute entry tolerates a dirty tree limited to `plans/<job>/`. Cross-skill decision for my human partner.
2. **Cold start never reads the plan.** Phase 2 (~60-80) loads brief, recall and "reference files specified in the task description", but never names `plans/<job>/inline-plan.md` / `outline.md` / `design.md`; `inline-plan.md` (design SKILL.md ~143) is not mentioned anywhere in the skill. `recall-artifact.md` exists only on the outline path (write-outline.md ~55). Fix: a Read-the-plan-artifact step, STOP if none.
3. **Skill-definition review group cannot satisfy the gate.** SKILL.md ~118 says skill-reviewer has "Read plus Bash `rg`"; the agent declares Read, Grep, Glob only. Template ~35 and its example ~79-81 tell it to fix all issues and write `plans/<job>/reports/review.md`, which it cannot; the structural-proof Read (~135) finds nothing and ~138 blocks 4b. Fix: correct the tool list; calling session writes `review-skill.md` from the reply and applies fixes; a report-only template variant.

## Major

- **Report paths conflict:** SKILL.md ~124 allows `review-<type>.md`, ~135 proves only `review.md`, template hardcodes `review.md` (~35) but its example writes `review-skill.md` (~79), and dispatch-composition.md ~29-30 claims `<dispatch name>.md` is the only rule.
- **Template lacks mandatory fields** per review-requirement.md (~25, 85-88, 128-134): no Constraints block; Changed files is the whole baseline diff, not the group's list.
- **triage-feedback.sh** counts `review*.md`, so every Simple job run through /inline is logged `underclassified` (script ~18-21, 48-50); its `WARNING: No corrector report` output has no handling in SKILL.md ~164.
- **Delegated execution under-specified** (~82-98): D-39 cited for a criterion it doesn't state; no TDD slice shape; dispatch-composition assumes runbook item ids an ad-hoc task lacks.
- **Description trigger "run task"** (~5) too broad; collides with /orchestrate. Suggested: name the no-runbook `plans/<job>` condition and the `execute` chain.
- **Design-context field** assumes `outline.md`/`design.md` (template ~10, 23, 43; SKILL.md ~122); Simple writes neither, agentic-prose writes `inline-plan.md`.
- **Skip policy** (~142-152) rejects "scope is small" while review-requirement.md ~9-15 allows self-review for ≤5 lines/≤2 files, without saying it overrides.

## Minor

- ~31 claims `recall-artifact.md` exists in both entry cases; it often doesn't.
- ~93 `git status --porcelain && just lint`: `&&` doesn't guard dirtiness; "do not split" unexplained.
- ~98 "10+ delegated executions" threshold ungrounded, nothing counts it.
- ~66 `git show main:... 2>/dev/null` violates the no-stderr-suppression rule.
- ~112/117 vs 126-130: "design documents" ambiguous; planning correctors listed for a gate planning artifacts don't route through.
- ~126-130 and template ~47 duplicate the planning-artifact routing paragraph.
- "D+B anchor" (~35, 68, 102, 132) undefined in the skill.
- ~16 history note "Replaces ad-hoc execution sequences…" is not actionable.
- ~72 clipped fragment "Patterns for implementing this, not classifying it."
- ~121 "uncommitted changes" wrong under delegated execution; use "since the Phase 1 baseline".
- ~140 UNFIXABLE handling skips review-requirement.md ~156-160 validation; no re-review after report-only fixes.
- Phase 4 has no post-fix precommit.
- ~168 "final report" undefined; ~174 "step 2 applies unmodified" ambiguous.
- Template example (~46, 59-66, 70-80) is a leftover from the creating plan (C1-C4, "~1500 words" estimate), omits the recall fallback line.
- Template ~37 `UNFIXABLE:` return contract vs dispatch-composition.md ~35 `blocked: <reason>`; ~42 baseline sentence contradicts clean-tree Phase 1.
- Template has no slot for `plugin-dev:agent-development` criteria (review-requirement.md ~41, 46); frontmatter lacks `argument-hint`.

## Priority (reviewer's order)

1. Settle commit/baseline ownership at the /design → /inline boundary.
2. Cold-start Read of the plan artifact; accept `inline-plan.md` as design context.
3. Fix the report-only reviewer flow.
4. One report-path rule; prove every group report.
5. Template Constraints + per-group files; stop triage counting the review report.
