# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.
## When selecting agent type for orchestrated steps
- Anti-pattern: Substituting a built-in agent type (`tdd-task`) when the plan-specific agent (`<plan>-task`) isn't found. Silent substitution loses the common context injected by prepare-runbook.py and violates the orchestration contract.
- Correct pattern: Plan-specific agent is mandatory for `/orchestrate`. If `<plan>-task` isn't available as a subagent_type, STOP and report — don't substitute. Session restart makes custom agents in `.claude/agents/` discoverable. `tdd-task` is only for ad-hoc TDD cycles outside prepared runbooks.
- Evidence: Dispatched Cycle 1.1 via `tdd-task` instead of `runbook-generation-fixes-task`. User corrected: restart had made the custom agent available. Remaining 12 cycles used the correct agent type.
## When TDD cycles grow a shared test file past line limits
- Anti-pattern: Each cycle agent adds tests to the designated test module without awareness of cumulative line count. The 400-line limit surfaces as a precommit failure requiring refactor escalation — 3 escalations across Cycles 3.1, 3.2, 3.3, and 4.1 for the same root cause.
- Correct pattern: Step files for later cycles should include conditional split instructions: "If `test_prepare_runbook_mixed.py` exceeds 380 lines, extract `TestPhaseContext` to `test_prepare_runbook_phase_context.py` before adding tests." Alternatively, runbook planning should pre-assign test classes to separate files when cumulative growth is predictable.
- Evidence: `test_prepare_runbook_mixed.py` grew from 382 → 409 → 478 → 465 lines across Phases 3-4. Each refactor escalation cost ~80-110K tokens. TDD process review flagged this as the primary compliance issue.
## When custom agents aren't available as Task subagent_types
- Anti-pattern: Assuming `.claude/agents/*.md` files with proper frontmatter are automatically available as `subagent_type` values in the Task tool. Attempting to use them produces "Agent type not found" errors.
- Correct pattern: Use built-in agent types (`test-driver`, `artisan`, `general-purpose`, etc.) with phase context injected in the prompt. Include the agent's instructions (TDD protocol, stop conditions, output format) directly in the Task prompt. Read the phase context file path so the agent can load it.
- Evidence: 5 custom agents (`hb-p1` through `hb-p5`) created with valid YAML frontmatter, not discoverable. Session restart was noted as required but didn't resolve. All 16 steps executed successfully via built-in types.
## When step file inventory misses codebase references
- Anti-pattern: Runbook step lists ~30 files for substitution propagation based on Phase 0.5 discovery. Actual codebase has ~45 files with old names — discovery missed skills, decisions, fragments, agents, and script code paths.
- Correct pattern: Discovery inventory should use `grep -r` across the full tree, not manual file listing. The verification step is the safety net, but discovery should cast a wider net initially.
- Evidence: Step 1.6 opus agent modified 30 listed files, hit ceiling. Second opus agent fixed 17 additional files. Orchestrator fixed 3 more path references.
## When haiku GREEN phase uses pytest without lint
- Anti-pattern: Step file specifies `just test` or `pytest` for GREEN verification. Haiku runs tests (pass), commits, writes report — but lint errors exist. Separate fix commit required before REFACTOR can run.
- Correct pattern: GREEN verification command must be `just check && just test` (or `just lint && just test`). The runbook template's TDD cycle GREEN section should list lint as a required gate before the commit, not just test pass.
- Evidence: Cycle 1.1 GREEN commit `a097b114` had F821 (undefined `Never`) and PLC0415 (local imports). Fix commit `1100569d` required. TDD audit flagged as the primary compliance violation.
## When delegating well-specified prose edits
- Anti-pattern: Applying "opus for prose artifacts" model rule to justify delegation when the cognitive work (designing what to add) was already done at opus during design. Launches N agents for N independent file edits, each re-reading files already in planner context.
- Correct pattern: The "opus for prose artifacts" rule targets cases where design decisions happen during editing. When an outline pre-resolves all decisions and specifies exact insertion points, execution is mechanical — sonnet follows the outline. The "design resolves to simple execution" decision applies: delegation ceremony exceeds edit cost for all-prose work.
- Evidence: 4 opus artisan agents launched for 47 lines of prose insertions across 4 skill files. User corrected: "why not inline?" The existing decision file explicitly warns against this pattern.
## When writing instructions that reference memory-index
- Anti-pattern: Using "scan memory-index" or "check loaded memory-index" language. "Scan file" triggers agents to Read the file even when it's already in context, wasting tokens on redundant reads.
- Correct pattern: "Read memory-index.md (skip if already in context)" — on-demand read with explicit skip condition. First recall point in a session reads it; subsequent points find it loaded. Never assume ambient preloading via CLAUDE.md @-reference.
- Rationale: Memory-index was removed from CLAUDE.md because it was useless without explicit action. The recall pass provides explicit action at cognitive boundaries, making on-demand reading the right pattern.
## When memory-index amplifies thin user input
- Memory-index keyword-rich entries surface relevant decisions even from sparse queries — cross-references between entries create an amplification effect superior to direct corpus search.
- This makes pipeline recall effective even on the moderate path (no formal requirements): derive domain keywords from user request, match against memory-index, follow cross-references to discover relevant decisions the user didn't explicitly mention.