# Advanced Workflow Patterns

Requirements handling, knowledge management, and specialized workflow patterns.

## .Documentation and Knowledge Management

### When Seeding Indexes Before Generation

**Decision Date:** 2026-02-04

**Decision:** Seed indexes with entries pointing to existing permanent docs before expecting auto-generation to fill them.

**Anti-pattern:** Leaving knowledge indexes empty until consolidation runs.

**Rationale:** Non-empty index is immediately useful; seeding and consolidation are complementary bootstrap mechanisms.

**Impact:** Immediate value from indexes while consolidation builds them incrementally.

### When Adding Entries Without Documentation

**Decision Date:** 2026-02-04

**Decision:** Learnings → learnings.md → /codify → permanent doc → index entry.

**Anti-pattern:** Adding memory-index entries for concepts without permanent docs.

**Rationale:** Index entries are discovery surfaces for on-demand knowledge; they must point somewhere.

**Impact:** Index serves as reliable discovery mechanism, not aspirational wishlist.

### When Writing Memory-Index Trigger Phrases

**Decision Date:** 2026-02-24

**Anti-pattern:** Dropping articles (a, an, the) from trigger phrases when the heading contains them. `_build_heading()` does literal reconstruction — missing articles cause section lookup failure.

**Correct pattern:** Keep trigger phrasing aligned with section heading text (case-insensitive, but articles must be present if in heading). Verify with `claudeutils _recall resolve "when <trigger>"` before committing.

**Evidence:** Batch-resolve failed during planstate-delivered runbook execution. Code fix deferred to plans/when-resolve-fix (fuzzy heading match in `_resolve_trigger()`).

### How to Merge Templates Safely

**Decision Date:** 2026-02-04

**Decision:** Partial templates with explicit merge semantics — PRESERVE existing sections, ADD new items, REPLACE only specified content.

**Anti-pattern:** Generic templates that imply "replace structure with this form" (causes learnings deletion).

**Rationale:** "Template" implies blank slate; explicit semantics (preserve/add/replace) prevent unintended overwrites.

**Impact:** Safe template usage without data loss.

## .Requirements and Execution

### When Requirements Change During Execution

**Decision Date:** 2026-02-04

**Decision:** Requirements MUST NOT be updated if task execution made them outdated; updating requires explicit user confirmation.

**Anti-pattern:** Updating requirement files during task execution when implementation discovers they're outdated.

**Rationale:** Requirements document intent and decisions at planning time; execution discovering they're wrong means either (1) requirements need user review/approval before updating, or (2) implementation needs to match requirements despite being outdated.

**Impact:** Clear separation between planning (requirements) and execution (implementation).

### When Naming Memory Index Triggers

**Decision Date:** 2026-02-18

**Anti-pattern:** Naming `/when` triggers after the anti-pattern, outcome, or self-assessment ("When synthesizing ungrounded methodology", "When deliverable review catches drift", "When resuming killed agents").

**Correct pattern:** Name triggers after the activity at the decision point — what the agent is doing when it needs the knowledge. Use the broadest verb that still triggers correctly. No self-assessment terms (agent can't evaluate what it doesn't know).

**Examples:** "When writing methodology" not "When synthesizing ungrounded methodology". "When relaunching similar task" not "When resuming killed agents".

**Same principle as `/when choosing name`:** discovery and recall over precision.

## .Knowledge Discovery and Context

### When Embedding Knowledge In Context

**Decision Date:** 2026-02-04

**Research:** From Vercel study: Ambient context (100%) outperformed skill invocation (79%).

**Problem:** Skills not triggered 56% of cases — decision about "when to invoke" is failure point.

**Correct pattern:** Embed critical knowledge in loaded context (CLAUDE.md, memory-index).

**Directive:** "Prefer retrieval-led reasoning over pre-training knowledge" (memory-index.md header).

**Impact:** Always-available context beats sometimes-invoked skills.

### When Memory-Index Amplifies Thin User Input

**Decision Date:** 2026-02-24

**Decision:** Memory-index keyword-rich entries surface relevant decisions even from sparse queries — cross-references between entries create an amplification effect superior to direct corpus search.

**Implication:** Pipeline recall is effective even on the moderate path (no formal requirements): derive domain keywords from user request, match against memory-index, follow cross-references to discover relevant decisions the user didn't explicitly mention.

### When Analyzing Task Insertion Patterns

**Decision Date:** 2026-02-18

**Decision:** Insert pending tasks at estimated priority position, not appended.

**Evidence:** Session scraping + git correlation across 337 sessions, 506 commits. Overall data (n=65) showed 61.5% prepend — misleading. Segmented by origin: `p:` directives (n=29) distribute evenly (34.5% prepend). Workflow continuations dominate the prepend signal.

**Implication:** Handoff skill should say "insert at estimated priority position" not "append" — agents already exercise good judgment by origin type. Different insertion policies needed per origin type.

### How to Name Session Tasks

**Decision Date:** 2026-02-04 (updated 2026-02-19: noun-based naming, drop pipeline verbs)

**Pattern:** Task names are noun-based prose keys identifying *what changes*. Drop pipeline-stage verbs (Design, Plan, Execute, Implement). Keep nature verbs describing the work itself (Fix, Rename, Migrate, Simplify). Pipeline stage belongs in metadata (command field, plan status).

**Anti-pattern:** Prefixing task names with pipeline-stage verbs ("Design X", "Execute X"). The verb encodes the *next action*, which grows stale as the task progresses through the pipeline.

**Implementation:** git log -S for on-demand history search, case-insensitive matching.

**Benefit:** Near-zero marginal cost, natural language keys, context recovery via task-context.sh.

**Impact:** Task names are both human-readable and machine-searchable identifiers.

### When Compressing Session Tasks

**Decision Date:** 2026-02-20

**Anti-pattern:** Reducing task descriptions to one-liners during session compression. Contextual notes (insights inputs, scope expansions, discussion conclusions, domain boundaries) exist only in session task notes — plan artifacts don't contain them.

**Correct pattern:** Before compressing, classify each sub-item: (a) duplicates plan artifact content → safe to trim, (b) contextual-only (insights, scope decisions, validation approaches) → must preserve. Only trim category (a).

**Evidence:** Compression at `0418cedb` lost detail from 12 tasks. Recovery required `git show` against pre-compression commit.

## .Commit Workflow Patterns

### When Committing Rca Fixes

**Decision Date:** 2026-02-05

**Decision:** Three commit RCA fixes implemented and active in workflow.

**Fixes:**
1. **Submodule awareness:** Commit submodule first, then stage pointer in parent
2. **Artifact staging:** prepare-runbook.py stages its own artifacts via `git add`
3. **Orchestrator stop rule:** Absolute "no exceptions" language, deleted contradictory scenarios

**Impact:** Prevents submodule sync drift, missing artifacts in commits, and dirty-state rationalization.

### When Running Precommit Validation

**Decision Date:** 2026-02-05

**Decision:** `just precommit` must not modify source files (unlike `just dev` which autoformats).

**Exemption:** Volatile session state (`agents/session.md`) is exempt — `#PNDNG` token expansion runs in precommit.

**Rationale:** Precommit is validation, not transformation. Session state is ephemeral metadata, not source code.

**Impact:** Clear separation between validation (precommit) and transformation (dev) workflows.

## .Recall Workflow Patterns

### When Writing Recall Artifacts

**Decision Date:** 2026-02-25

**Anti-pattern:** Full excerpts per entry (heading + source + relevance + content excerpt). Creates stale snapshots — if decision files change between artifact creation and consumption, excerpts are outdated.

**Correct pattern:** Entry keys only. Artifact lists trigger phrases with 1-line relevance notes. Downstream consumers batch-resolve via `claudeutils _recall resolve` to get current content. No staleness, no excerpt duplication.

### When Requirements Capture Needs Recall

**Decision Date:** 2026-02-25

/requirements skill originally went straight from conversation extraction to codebase discovery without recall. This produces naive requirements that miss existing infrastructure.

**Correct pattern:** /requirements includes a recall step between mode detection and conversation scanning, producing a recall artifact. The recall grounds the extraction — agent knows what infrastructure exists before interpreting what the user asked for.

### When Recall Loads New Entries Mid-Artifact

**Decision Date:** 2026-02-27

**Anti-pattern:** Loading recall entries across multiple passes, then only applying entries that matched the original artifact structure. New entries from later passes can invalidate or extend decisions made before those entries were loaded.

**Correct pattern:** After each recall pass, re-evaluate current artifact decisions against newly loaded entries. Applies to any artifact in progress — requirements, outline, design, runbook. Later passes may reveal structural gaps, not minor refinements.

## .Task and Session Patterns

### When D: Mode Validates A Proposed Change

**Decision Date:** 2026-03-02

**Anti-pattern:** `d:` evaluation concludes with affirmative verdict ("agree, this should be done"), then stops. The validated change exists only in conversation context. No pending task created, no brief written. Change is lost on context rotation.

**Correct pattern:** When `d:` verdict is "agree, this change should be made" (or equivalent), chain to `p:` evaluation — task name, model tier, restart flag. Create brief if discussion produced design context worth preserving.

**Scope:** Applies when discussion conclusion implies future work. Pure analysis ("is X true?") or rejected proposals ("disagree") don't trigger the chain.

**Evidence:** Three consecutive misses in one session (wt-rm-dirty review, 2026-03-01) confirm this is systematic, not incidental.

### When Starting Work On A Task

**Decision Date:** 2026-03-02

**Anti-pattern:** Jumping to `/design` because the task description seems clear enough. Session.md task entries are scope (name + one-liner), not specification. The gap between task description and behavioral FRs is where design sessions waste time discovering what they're building.

**Correct pattern:** Always start from `/requirements` unless a requirement-equivalent document already exists. Requirement-equivalent: existing requirements.md, design.md with behavioral FRs, deliverable review report (findings = acceptance criteria for rework). Brief.md is NOT equivalent — transfers context but lacks testable acceptance criteria.

**Rationale:** `/requirements` includes a recall step that grounds extraction against existing infrastructure. Skipping to `/design` produces naive requirements. The `/design` Phase 0 requirements-clarity gate fires at 2.6% rate (1/38 sessions) — too late and too rare to compensate.

### When Pending Tasks Lack Recovery Context

**Decision Date:** 2026-03-02

**Anti-pattern:** Task entry has description but no backtick command. Next session's `x` has nothing to invoke. Discussion conclusions (d: mode decisions, agreed refinements, identified reuse paths) exist only in conversation context — lost on session boundary.

**Correct pattern:** Every pending task gets a backtick command in the entry. Discussion conclusions that produce pending work get captured as task notes in session.md, recoverable via `task-context.sh`. The handoff IS the recovery mechanism — if it's not in session.md, it doesn't survive.

### How To Wrap A Discussion Session

**Decision Date:** 2026-03-02

`w` (wrap) is a Tier 1 command (standalone, no colon, no user content). Sequence: findings → takeaways → submit.

- **Findings:** Summarize what the investigation/discussion discovered (factual, not narrative)
- **Takeaways:** Extract learnings (append to learnings.md), create pending tasks (`p:` evaluation for each validated change), write briefs if discussion produced design context worth preserving
- **Submit:** `/handoff` then `/commit` (or `hc`)

Trigger: user says `wrap` or `w`. Crystallizes conversation context into persistent artifacts before context rotates out. Pending absorption into directive-skill-promotion task.

### When Converting External Documentation To Recall Entries

**Decision Date:** 2026-03-02

Two trigger classes have different automation profiles:
- `how` entries (task-descriptive) — extractable mechanically from documentation headings. Sonnet automation with corrector pass
- `when` entries (situational) — require operational experience to author. Hand-curation from incidents and failures

**Anti-pattern:** Treating all trigger extraction as equivalent quality risk. Applying corrector-heavy workflows to `how` entries (unnecessary) or batch-automating `when` entries (insufficient).

**Structural insight:** Training provides reasoning capability; recall provides authoritative inputs. For operational methodology, explicit recall entries override ambiguous training-data patterns. Interaction structure (skills, tool gates, PreToolUse hooks) enforces application at the right moment.
