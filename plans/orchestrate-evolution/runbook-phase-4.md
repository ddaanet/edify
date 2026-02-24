### Phase 4: Skill and prose updates (type: general, model: opus)

**Scope:** Rewrite orchestrate SKILL.md, update refactor agent and delegation fragment. Final phase — all code/infrastructure from Phases 1-3 exists; opus writes about implemented artifacts, not forward references.

**Files:** `agent-core/skills/orchestrate/SKILL.md` (rewrite), `agent-core/agents/refactor.md` (modify), `agent-core/fragments/delegation.md` (modify)

**Depends on:** Phase 1 (agent caching model — `{name}-task` naming, Plan Context embedding), Phase 2 (verify-step.sh, structured orchestrator plan format with pipe-delimited steps), Phase 3 (TDD agents: tester/implementer/test-corrector/impl-corrector, step file splitting, verify-red.sh, TDD role markers)

**Key constraints:**
- All files are architectural artifacts → opus mandatory (per recall: "When Selecting Model For Prose Artifact Edits")
- SKILL.md every section must open with a tool call (per recall: "How to Prevent Skill Steps From Being Skipped" — D+B hybrid pattern)
- Positional authority in agent definitions: constraints in primacy, plan context middle, scope enforcement recency (per recall artifact)
- Design section references: D-1 through D-6 must all be addressed in SKILL.md rewrite
- Prose atomicity: all SKILL.md edits in a single step (one opus pass writes complete skill)
- Sonnet default (D-1): remove haiku orchestrator assumption throughout
- delegation.md is a CLAUDE.md fragment loaded via @-reference — changes affect all sessions

---

## Step 4.1: SKILL.md complete rewrite (including TDD orchestration loop)

**Objective:** Rewrite orchestrate SKILL.md from ~517 lines to ~250 lines. Single opus pass produces complete skill covering both general execution loop and TDD orchestration loop.

**Execution Model:** Opus

**Implementation:**

The rewrite replaces the current SKILL.md with a new version reflecting all design decisions (D-1 through D-6) and the infrastructure built in Phases 1-3.

**Sections to preserve (adapt, not delete):**
- Frontmatter: update `description`, remove `allowed-tools` constraint
- "When to Use" / "Do NOT use when" sections (update content)
- Deliverable review assessment (Section 6, steps 4-5)
- Progress tracking (Section 5 — simplify)
- Continuation protocol (cooperative continuation, default-exit)
- Error escalation structure (Section 4 — restructure for 2-level model)

**Sections to rewrite:**
- Section 1 (Verify Runbook Preparation): Update artifact names from `crew-<name>` to `<plan>-task`, add TDD agent verification (`<plan>-tester`, `<plan>-implementer`, etc.)
- Section 2 (Read Orchestrator Plan): Update for new structured plan format (pipe-delimited steps, `## Steps` section, `**Agent:**`/`**Type:**` header fields)
- Section 3 (Execute Steps): Complete rewrite — two execution paths:
  - **General loop:** Read plan → dispatch with file reference → verify-step.sh → remediate (D-3) → phase boundary corrector → inline handling (D-6)
  - **TDD loop:** dispatch tester → RED gate (verify-red.sh) → test-corrector (if RED fails) → dispatch implementer → GREEN gate (`just test` + verify-step.sh) → impl-corrector (if GREEN fails) → next cycle
- Section 3.3 (Post-step verification): Replace `git status --porcelain` with `verify-step.sh` invocation
- Section 4 (Error Escalation): Simplify to 2-level model (sonnet → user). Remove haiku → sonnet level. Remove `max_turns: 150` (replaced by per-step max_turns from orchestrator plan)

**New sections to add:**
- **Post-step remediation protocol (D-3):** Resume agent → recovery delegation → RCA task generation (FR-2, FR-3). Reference design section, do not reproduce full protocol.
- **TDD orchestration loop (D-5):** Complete ping-pong cycle: tester → RED gate → test-corrector → implementer → GREEN gate → impl-corrector. Mechanical gates (verify-red.sh, verify-step.sh) — no judgment.
- **Agent resume strategy:** Resume tester/implementer across cycles (save agent ID). Fresh launch if >15 messages. Correctors never resumed.
- **Cleanup step:** After completion, delete `.claude/agents/<plan>-*.md` files (task, corrector, tester, implementer, test-corrector, impl-corrector).
- **Dispatch pattern:** File reference only — `"Execute step from: plans/<name>/steps/step-N-M.md"` (not inline content). Model from orchestrator plan step entry.

**Sections to remove:**
- `allowed-tools` frontmatter constraint (D-1: sonnet orchestrator can use all tools)
- Phase-Agent Mapping table references (replaced by structured plan header)
- Haiku-specific model selection warnings ("CRITICAL — Model selection: The orchestrator itself may run on haiku...")
- Level 1 escalation (haiku → sonnet) — sonnet is now the orchestrator

**Design decision coverage checklist:**
- D-1 (sonnet default): Remove haiku assumptions, sonnet orchestrator throughout
- D-2 (agent caching): File reference dispatch, `{name}-task`/`{name}-corrector` naming
- D-3 (remediation): Post-step remediation protocol section
- D-4 (escalation): 2-level model (sonnet → user)
- D-5 (ping-pong TDD): TDD orchestration loop section
- D-6 (inline phases): Inline handling preserved (Section 3.0 adapted)

**Expected Outcome:** SKILL.md rewritten to ~250 lines. All design decisions reflected. Both general and TDD execution loops defined. verify-step.sh and verify-red.sh referenced (scripts exist from Phases 2-3).

**Error Conditions:**
- Rewritten skill exceeds 350 lines → review for verbosity, remove redundant examples
- Missing design decision coverage → check against D-1 through D-6 checklist above
- D+B hybrid violation (prose-only section) → ensure every numbered step opens with Read/Bash/Glob

**Validation:**
- SKILL.md line count between 200-350
- All 6 design decisions (D-1 through D-6) addressed
- verify-step.sh and verify-red.sh referenced by correct paths
- Agent naming uses `{name}-task`, `{name}-tester`, etc. (not `crew-` prefix)
- No `allowed-tools` in frontmatter
- Continuation protocol preserved
- Deliverable review assessment preserved

---

## Step 4.2: Refactor agent and delegation fragment updates

**Objective:** Update refactor.md and delegation.md to align with new orchestration model.

**Execution Model:** Opus

**Implementation:**

**refactor.md (244 lines → ~274 lines):**

Three targeted additions to existing agent definition:

1. **Deslop directives** — Insert before Step 3 (Refactoring Protocol, line 99):
   - "Prefer factorization over splitting: extract shared logic into helpers before considering module splits"
   - "Remove dead code during refactoring — don't preserve unused imports, functions, or variables"
   - "Token economy: reference file paths, don't repeat file contents in reports"
   - Per recall: "When Refactoring Agents Need Quality Directives"

2. **Factorization-before-splitting rule** — Add to Refactoring Evaluation section (after line 42):
   - "Before splitting a module: check for duplicate code, unused helpers, repeated kwargs patterns. Extract shared logic first — the module may shrink below threshold without splitting."
   - Per recall artifact: "When Hitting File Line Limits"

3. **Resume pattern** — Add to Return Protocol section (after line 183):
   - "If interrupted mid-refactoring: orchestrator should resume this agent (save agent ID). Fresh launch only if >15 messages exchanged."
   - Per delegation.md Delegate Resume pattern

**delegation.md (55 lines → ~55 lines, net zero change):**

Four modifications to existing fragment:

1. **Sonnet default** — Replace Model Selection list (lines 9-17):
   - Remove "Haiku: Execution, implementation, simple edits, file operations"
   - Change "Sonnet: Default for most work, balanced capability" to "Sonnet: Default for all execution tasks"
   - Keep "Opus: Architecture, complex design decisions only"
   - Remove "Never use opus for straightforward execution tasks." (covered by orchestrate skill)

2. **File reference pattern** — Add after Pre-Delegation Checkpoint (after line 23):
   - "Dispatch with file reference: `Execute step from: plans/<name>/steps/step-N.md` — agent reads step file for full context. Do not inline step content in prompt."

3. **Agent caching note** — Add after file reference pattern:
   - "Plan-specific agents (`{name}-task`, `{name}-corrector`) embed design and outline context. Prompt needs only the step file reference — Plan Context is baked into the agent definition."

4. **Remove haiku line** — Delete "Haiku: Execution, implementation, simple edits, file operations" from Model Selection

**Expected Outcome:** refactor.md gains ~30 lines of quality directives and resume pattern. delegation.md updated to reflect sonnet-default model with file reference dispatch.

**Error Conditions:**
- Insertion at wrong location disrupts agent flow → verify surrounding context before inserting
- delegation.md changes conflict with CLAUDE.md @-reference loading → validate fragment still parseable

**Validation:**
- `just precommit` passes (lint, format)
- refactor.md: search for "factorization" — present in Evaluation section
- refactor.md: search for "deslop" or "dead code" — present before Step 3
- refactor.md: search for "resume" — present in Return Protocol section
- delegation.md: no "Haiku" in Model Selection list
- delegation.md: contains "file reference" pattern
- delegation.md: contains "agent caching" or "Plan Context" note
