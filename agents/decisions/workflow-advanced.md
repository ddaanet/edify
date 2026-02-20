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

**Decision:** Learnings → learnings.md → /remember → permanent doc → index entry.

**Anti-pattern:** Adding memory-index entries for concepts without permanent docs.

**Rationale:** Index entries are discovery surfaces for on-demand knowledge; they must point somewhere.

**Impact:** Index serves as reliable discovery mechanism, not aspirational wishlist.

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
