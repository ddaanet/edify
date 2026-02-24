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
## When recall-artifact.md is absent during review
- Anti-pattern: Skill says "if absent, proceed without it" and reviewer takes the early exit — no recall at all. Reviewing recall-pass deliverables without performing recall is the exact gap the deliverables are designed to close.
- Correct pattern: "If absent, do lightweight recall" — read memory-index.md, identify review-relevant entries (quality patterns, failure modes), batch-resolve. The Tier 1/2 sections in the runbook skill already have this fallback; deliverable-review was missing it.
- Evidence: Deliverable review of recall-pass ran without any recall. Fixed: added lightweight recall fallback to deliverable-review skill Layer 2.
## When validating worktree merges
- Anti-pattern: Trusting `_worktree merge` autostrategy for session.md without post-merge validation. The autostrategy resolves in favor of the branch's focused session, dropping main-only content (Worktree Tasks entries for other worktrees, blocker formatting).
- Correct pattern: After every `_worktree merge`, validate session.md: check Worktree Tasks section preserved main's entries, check Blockers formatting, check completed tasks have completion records. Manual check until merge.py autostrategy is fixed.
- Evidence: Merge 1 dropped "Update grounding skill" from Worktree Tasks. Merge 2 left orphaned entry + malformed blocker line. Both required manual recovery.
## When Simple triage skips recall that would have corrected the triage
- Anti-pattern: Classifying behavioral code changes (new functions, new call sites) as Simple based on conceptual simplicity ("just copy a file"). Simple path skips recall → misses codified decision that behavioral code is NOT simple → skips runbook → skips TDD phase typing. Recall failure and process failure share a single root cause: mis-triage.
- Correct pattern: Apply structural criteria at triage: new functions, changed logic paths, conditional branches = behavioral code = Moderate minimum. The decision at `workflow-planning.md:325` already codifies this. Design skill Simple criteria now include explicit "no behavioral code changes" gate.
- Evidence: `_copy_test_sentinel()` — new function + new call site in `_setup_worktree` — triaged as Simple. Skipped recall, skipped runbook, wrote code+tests simultaneously. Had recall loaded `workflow-planning.md`, triage would have corrected to Moderate → `/runbook` → TDD.
## When custom agents need session restart for discoverability
- Anti-pattern: Using plan-specific agents as `subagent_type` values in the same session they were created. They aren't indexed until restart.
- Correct pattern: Plan-specific agents in `.claude/agents/` ARE discoverable as Task `subagent_type` values — but only after session restart. The prepare-runbook.py → restart → orchestrate workflow naturally includes this boundary.
- Evidence: `hb-p1` through `hb-p5` not discoverable in creating session. Same agents confirmed discoverable in subsequent sessions (visible in Task tool schema). Built-in types with prompt injection work as fallback when restart isn't feasible.
## When corrector agents have no recall mechanism
- Anti-pattern: Corrector agents (design-corrector, outline-corrector, runbook-outline-corrector) had no recall loading in their protocols. Tier 3 runbook skill corrector delegations also didn't pass recall entries in prompts. Only deliverable-review had self-contained recall.
- Correct pattern: Every corrector agent needs recall via one of: (a) self-contained loading in agent body (Step 1.5 or Load Context item 4), (b) caller passing recall entries in delegation prompt, or (c) skill-level Recall Context section (review-plan/SKILL.md). runbook-corrector gets (c) via its `skills: ["review-plan"]` field; design/outline correctors need (a) directly.
- Evidence: RCA after /reflect identified the gap. Fixed 3 skills + 3 agents. Correctors without recall cannot flag project-specific failure modes like "haiku GREEN verification must include lint" or "multi-file test growth anti-pattern".
## When treating recall-artifact summary as recall pass
- Anti-pattern: Runbook Tier 2 says "Read recall-artifact.md if it exists" as terminal. After /clear, agent reads summary entries (titles + 2-line descriptions) but does not load full decision content. Proceeding on summaries misses behavioral nuance that delegation prompts need verbatim.
- Correct pattern: Read artifact to identify WHICH decisions matter, then batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...` to load WHAT they say (full decision section content). Both steps required in new sessions.
- Evidence: /reflect RCA identified the root cause. Tier 2 recall section not yet updated (corrector side fixed; planner side still has the gap per Blockers in session.md).
## When writing memory-index trigger phrases
- Anti-pattern: Dropping articles (a, an, the) from trigger phrases to keep them short, when the actual heading contains them. Trigger `"adding a new variant to enumerated system"` vs heading `"When Adding A New Variant To An Enumerated System"` — `_build_heading()` does literal reconstruction, so the missing "an" causes section lookup failure.
- Correct pattern: Keep trigger phrasing aligned with the section heading text (case-insensitive, but articles must be present if in heading). When adding an entry, verify with `when-resolve.py "when <trigger>"` before committing.
- Evidence: Batch-resolve failed during planstate-delivered runbook execution. Data fix: added "an" to memory-index.md trigger. Code fix deferred to plans/when-resolve-fix (fuzzy heading match in `_resolve_trigger()`).
## When designing context preloading mechanisms
- Anti-pattern: Injecting content via @ref expansion in session.md, then having workflow skills Read the same files. @ref expansion puts content in system prompt; Read puts content in conversation messages. Both are cumulative — content appears twice, doubling token cost.
- Correct pattern: Use explicit skill invocation (`/prime`) instead of implicit session.md injection. Skill Reads content into conversation once. No system-prompt duplication. Infrastructure to automate preloading (@ref gates, scripted checks, workflow skill modifications) exceeded the cost of one explicit skill call.
- Evidence: 8-round design discussion explored @ref preload → SessionStart hook → scripted gate → all dropped. Final: `/prime` skill chain-calls `/recall`.
## When fixing behavioral deviations identified by RCA
- Anti-pattern: Strengthening language ("no exceptions", "MUST", scenario-specific warnings) in rules the agent already saw and rationalized past. If the rule was clear and the agent overrode it, clarity wasn't the problem — the environment allowed the override.
- Correct pattern: Structural fixes — resolve conflicting directives, anchor gates with tool calls (D+B), add environmental enforcement (hooks/scripts) with guidance, ensure sufficient context loaded at decision point. Fix the environment, not the prose.
- Evidence: /reflect prescribed "no exceptions" language for design skill Simple gate after agent rationalized past existing clear behavioral-code rule. Same anti-pattern class as ambient rules without enforcement (defense-in-depth.md: "ambient rules without enforcement are aspirational").
## When companion tasks bundled into /design invocation
- Anti-pattern: Session note says "address X during /design." Agent treats companion work as exempt from design process — no recall, no skill loading, no classification gate. Rationalizes "well-specified from prior RCA" to skip all process steps.
- Correct pattern: Companion tasks get their own triage pass through the same Phase 0 gates. "Address during /design" means the /design session is the venue, not that process is optional. Each workstream needs: recall, classification, routing.
- Evidence: 4 triage fixes to design skill attempted without /recall or /skill-development loading. /reflect identified same pattern class as "Simple triage skips recall" learning.