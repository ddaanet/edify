# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## When design ceremony continues after uncertainty resolves
- Anti-pattern: One-shot complexity triage at `/design` entry, no re-assessment when outline resolves architectural uncertainty. Process continues at "complex" even when outline reveals 2-file prose edits.
- Correct pattern: Two gates. Entry gate reads plan directory artifacts (existing outline can skip ceremony). Mid-stream gate re-checks complexity after outline production. Both internal to `/design` — preserves single entry point.
- Evidence: Outline-review-agent + design.md + design-vet-agent cost ~112K tokens for work that could have been done inline. Findings would have surfaced during editing.
## When deleting agent artifacts
- Anti-pattern: Treating all ceremony artifacts as equally disposable. Outline review found real issues (FR-2a gap, FR-3c contradiction); design.md restated the reviewed outline.
- Correct pattern: Distinguish audit trails with real findings from redundant restates. Review reports that improved artifacts have value; documents that reformat existing artifacts don't.
## When recovering agent outputs
- Anti-pattern: Manually reading agent session log and retyping content.
- Correct pattern: Script extraction from task output files. Agent Write calls are JSON-structured in `tmp/claude/.../tasks/<agent-id>.output`. Parse with jq or Python, recover deterministically.
- Prototype: `plans/prototypes/recover-agent-writes.py`
## When design resolves to simple execution
- Anti-pattern: Always routing from `/design` to `/runbook` after sufficiency gate, regardless of execution complexity. Complex design classification persists through the pipeline even when design resolves the uncertainty.
- Correct pattern: Execution readiness gate inline at sufficiency gate. When design output is ≤3 files, prose/additive, insertion points identified, no cross-file coordination → direct execution with vet, skip `/runbook`.
- Rationale: Design can resolve complexity. A job correctly classified as Complex for design may produce Simple execution. The gate is subtractive (creates exit ramp), not additive (more ceremony).
## When selecting reviewer for artifact vet
- Anti-pattern: Defaulting to vet-fix-agent for all artifacts because the vet-requirement fragment names it as the universal reviewer. Fragments are LLM-consumed behavioral instructions, not human documentation — doc-writing skill is wrong reviewer for them.
- Correct pattern: Check artifact-type routing table in vet-requirement.md before selecting reviewer. Skills → skill-reviewer, agents → agent-creator, design → design-vet-agent, fragments → vet-fix-agent (default, not doc-writing). The routing table is always-loaded; the process step is the enforcement gate.
- Evidence: Selected vet-fix-agent for skill edits. User corrected to skill-reviewer. Root cause: generic rule without routing lookup.
## When constraining task names for slug validity
- Anti-pattern: Propagating the 25-char git branch slug limit to task naming time. Forces suboptimal prose keys for tasks that may never become worktrees.
- Correct pattern: Task names are prose keys (session management layer). Slug derivation is a worktree concern. When a derived slug is too long, provide a `--branch` override at invocation time — not a constraint at naming time.
- Rationale: Layers should not share constraints. The enforcement point (worktree creation) is the right place to surface slug limits, not the point of task authoring.
