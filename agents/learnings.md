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
## When selecting review model
- Anti-pattern: Matching review model to author's model ("haiku wrote it → sonnet reviews it"). Also: blanket opus review because orchestrator is opus (inheritance makes everything opus).
- Correct pattern: Match review model to the correctness property being verified. State machine routing (architectural wiring, design invariant compliance like D-5 ordering) → opus vet. Behavioral changes within functions (check=False, abort removal) → sonnet vet. Prose artifacts consumed by LLMs → opus vet. Mechanical substitutions → sonnet vet.
- Rationale: Haiku can write state machine code that looks plausible but has subtle wiring errors (wrong routing target, wrong detection order). These are architectural properties that sonnet vet may accept. Conversely, opus reviewing grep-and-replace is waste — the test pass/fail is sufficient signal for mechanical changes.
## When holistic review applies fixes
- Anti-pattern: Fixing one reference to a changed value without checking for other references in the same artifact. Holistic review corrected Cycle 2.1 assertion section (exit code 3 → 0 or 3) but missed the test setup section 5 lines below that still said "exit code == 3".
- Correct pattern: After changing a value in a reviewed artifact, grep the artifact for all other references to the old value. Fix-all means all occurrences, not just the first one found.
- Evidence: Cycle 2.1 step file had "exit code is 0 or 3" in assertions but "Assert exit code == 3" in test setup. Agent writing test would see conflicting instructions.
## When haiku rationalizes test failures
- Anti-pattern: Haiku commits code despite failing regression tests, rationalizing failures as "expected behavior change from state-based routing." The regressions were real bugs — branches at HEAD satisfy `git merge-base --is-ancestor` (every commit is its own ancestor), triggering wrong state detection.
- Correct pattern: Regression test failures during TDD GREEN phase are bugs, not expected behavior. The step file's regression check command defines the contract. If tests fail, fix the implementation before committing.
- Evidence: Cycle 1.2 haiku committed with 3 failing tests (test_merge_ours_clean_tree, test_merge_submodule_fetch, test_merge_branch_existence). Required sonnet escalation to diagnose and fix.
## When step agents leave uncommitted files
- Anti-pattern: Step agents create report files (execution notes, diagnostics) but don't commit them, leaving untracked files that violate the "clean tree after every step" invariant.
- Correct pattern: Step agents must commit ALL generated artifacts including reports. Orchestrator should not need to commit on behalf of step agents. If the step creates a report, the step's commit includes it.
- Evidence: Cycles 2.2, 3.1 left report files uncommitted. Orchestrator committed them manually each time.
## When scoping vet for cross-cutting invariants
- Anti-pattern: Scoping vet "Changed files" to only files modified in the current phase. For cross-cutting design decisions (D-8 "all output to stdout", NFR-2 "no data loss"), the invariant domain spans the entire call graph, not just changed files.
- Correct pattern: Add "Verification scope" to vet execution context listing all files that participate in the cross-cutting invariant. Identify via grep (e.g., `err=True` across merge call graph for D-8, `MERGE_HEAD` across all paths for lifecycle).
- Evidence: resolve.py has `err=True` calls in the merge code path but wasn't in Phase 5's changed-files list. Precommit handler drops stdout but wasn't flagged because `err=True` removal was the vet criterion, not "all output reaches stdout."
## When reviewing final orchestration checkpoint
- Anti-pattern: Scoping the final phase vet to only that phase's changes, even when the checkpoint already performs cross-cutting audits (exit code audit traced all SystemExit calls). Selective application of cross-cutting methodology.
- Correct pattern: Final checkpoint should include lifecycle audits for all stateful objects created during the implementation (MERGE_HEAD, staged content, lock files). Same methodology as exit code audit: trace through all code paths, flag any path that exits success with state still active.
- Evidence: Phase 5 opus vet audited all 12 SystemExit calls (cross-cutting). Did not audit MERGE_HEAD lifecycle — same class of trace, just applied to git state instead of exit codes. Submodule MERGE_HEAD persists after successful parent merge (exit 0).
## When tracking worktree tasks in session.md
- Anti-pattern: Separate Worktree Tasks section with move semantics (Pending → Worktree on create, Worktree → Completed on rm). Creates merge-commit amend ceremony (`_update_session_and_amend`), requires manual editing for bare-slug worktrees, drifts from filesystem state.
- Correct pattern: Tasks stay in Pending with inline `→ \`slug\`` marker. `#status` renders worktree section from `_worktree ls`, not from a session.md section. Single source of truth is git worktree state.
- Rationale: Worktree Tasks is a UI concern baked into the data model. The `_update_session_and_amend` code path in both `merge` and `rm` is a failure source (exit 128 during this session's merge). Inline markers + filesystem query handles all use cases with fewer failure modes.
## When naming session tasks
- Anti-pattern: Prefixing task names with pipeline-stage verbs (Design X, Execute X, Implement X). The verb encodes the *next action*, which grows stale as the task progresses through the pipeline.
- Correct pattern: Noun-based task names identifying *what changes*. Drop pipeline verbs (Design, Plan, Execute). Keep nature verbs that describe the work itself (Fix, Rename, Migrate, Simplify). Pipeline stage belongs in metadata (command field, plan status).
- Evidence: "Design quality gates" stays "Design" after design completes and planning begins. "Execute plugin migration" is wrong the moment the outline needs refresh. "Remember skill update" (already noun-ish) works well.
- Complements: "When constraining task names for slug validity" (layers don't share constraints).
## When merging worktree with consolidated learnings on main
- Anti-pattern: Git merge brings in the branch's full learnings.md (pre-consolidation content) over main's consolidated version. Branch diverged before consolidation; merge favors longer file.
- Correct pattern: After merging a branch that diverged before a learnings consolidation, verify learnings.md line count. Only the delta (new entries added on branch after branch point) should be appended to main's consolidated version. Pre-consolidation content is already in permanent docs.
- Evidence: This session — merge brought 199 lines (branch) over 30 lines (main consolidated). 175 lines were pre-consolidation duplicates. Only 24 lines were genuine new content.
## When inlining reference file subsets for optimization
- Anti-pattern: Inline a "top N" subset of a reference file (e.g., top-10 gitmoji) to avoid a Read call. Agent picks from the visible subset, unaware better matches exist in the full file. Creates a knowledge ceiling — the agent is confidently wrong.
- Correct pattern: Either keep the full Read (agent sees all options) or move selection to a CLI tool (embeddings search over full corpus). Partial inlining is worse than both alternatives.
- Rationale: Optimization must not degrade decision quality. The agent cannot know what it hasn't seen.

## When triaging external diagnostic suggestions
- Anti-pattern: Treating diagnostic report output (e.g., /insights) as a backlog intake pipeline — every suggestion becomes a pending task. Inflates the task list just after compression.
- Correct pattern: Triage by routing. Superseded → discard. Skill-specific → annotate existing skill task. Simple → inline immediately (write the fragment, don't defer it). Only genuinely new substantial work becomes standalone tasks.
- Evidence: 15 suggestions triaged to 3 inlined fragments + 5 tasks + 4 annotations. Initial draft had 8 standalone tasks before user caught that fragments were single edits.
