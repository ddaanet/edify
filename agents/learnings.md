# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When companion tasks bundled into /design invocation
- Anti-pattern: Session note says "address X during /design." Agent treats companion work as exempt from design process — no recall, no skill loading, no classification gate. Rationalizes "well-specified from prior RCA" to skip all process steps.
- Correct pattern: Companion tasks get their own triage pass through the same Phase 0 gates. "Address during /design" means the /design session is the venue, not that process is optional. Each workstream needs: recall, classification, routing.
- Evidence: 4 triage fixes to design skill attempted without /recall or /skill-development loading. /reflect identified same pattern class as "Simple triage skips recall" learning.
## When recall gate has skip condition
- Anti-pattern: "Read X (skip if already in context)" as a recall gate. Agent rationalizes the skip condition without verifying — substitutes related activity for the required Read. The escape hatch IS the failure mode.
- Correct pattern: Anchor recall with a tool call that proves work happened. `when-resolve.py` is the gate: it's a Bash call (unskippable), requires trigger knowledge (forces prior Read of memory-index), and produces output (proves resolution). One gate anchor is sufficient — passphrase/proof-of-Read mechanisms are redundant when the resolution tool already proves both.
- Evidence: /reflect Phase 4.5 skipped recall entirely. Same class as "treating recall-artifact summary as recall pass" — agent substitutes adjacent activity for the specific required action.
## When selecting model for discovery and audit
- Anti-pattern: Using haiku scouts to audit prose quality or detect structural anti-patterns in LLM-consumed instruction files (skills, agents, fragments). Haiku grades generously, misses dominant failure patterns, and produces false positives that require opus validation — double work.
- Correct pattern: Sonnet minimum for any discovery/audit touching skills, agents, or fragments. These are architectural prose artifacts — assessing their quality requires the same judgment tier as editing them. The "model by complexity" rule applies to analysis, not just edits.
- Evidence: Haiku scout graded 0 skills at C (sonnet found 3), missed description anti-pattern as dominant issue (18/30), produced 15 gate findings vs sonnet's 12 (3 false positives from over-flagging steps where preceding tool output naturally feeds judgment).
## When optimizing skill prose quality
- Reference: `plans/reports/skill-optimization-grounding.md` — Segment → Attribute → Compress framework adapted from LLMLingua/ProCut. 9 content categories with compression budgets per category.
- Triggers: deslop, compression, segment, attribute, budget, skill optimization, prose quality pass
## When editing skill files
- The `description` field is what Claude Code displays in the CLI slash command picker AND what the agent uses for triggering decisions (dual purpose, no separate field — filed #28934).
- Correct pattern: lead with an action verb describing what the skill does (user display), then include trigger phrases (agent matching). Example: "Save session state for the next agent. Triggers on 'handoff', 'h', 'hc', or session update requests."
- Anti-pattern: leading with "This skill should be used when..." — good for triggering but unreadable in the picker.
- The H1 title is body content only — not displayed in the picker.
- Fallback: if `description` is omitted, the first paragraph of markdown content is used instead.
- Extraction safety: every content block moved to references/ must leave a trigger condition + Read instruction in the main SKILL.md body. Verify each references/ file has a corresponding load point.
- Control flow verification: after restructuring skills with conditional branches, enumerate all execution paths and verify user-visible output on each path. Prior deslop on design skill combined two fast paths and regressed user-facing classification message.
- D+B gate additions: adding tool calls to anchor prose-only gates must not change the gate's decision outcome on existing paths. The added Read/Bash provides data for judgment — it should not introduce new content that shifts the judgment itself.
- Triggers: editing skills, skill surgery, deslop, extraction, progressive disclosure, restructuring conditional branches
## When dispatching parallel agents with shared recall
- Anti-pattern: Each parallel agent independently resolves the same recall artifact keys (N agents × 10 when-resolve.py calls = N×10 redundant Bash calls + parsing). Design/audit reports also re-read by each agent.
- Correct pattern: Pre-resolve recall to a shared file (`plans/<job>/reports/resolved-recall.md`) before dispatch. All agents Read one file instead of each running the resolver. Same approach for any shared context (design doc summaries, audit findings) — resolve once, share the output.
- Evidence: 4 execution agents each ran when-resolve.py with 10 keys independently. Pre-resolved file created for 5 convergence review agents, eliminating ~50 redundant Bash calls.
## When reviewing skills after batch edits
- Anti-pattern: Single reviewer agent for all modified skills. Context fills with 28 skill reads before review begins. Quality degrades as context grows.
- Correct pattern: Parallel reviewers split by relatedness (phase groupings natural — related skills, similar edit patterns, cross-skill consistency visible within group). Separate behavior invariance agent for conditional-branch skills. All read-only, no file conflicts.
- Evidence: 5 parallel opus reviewers (4 skill quality + 1 behavior invariance) completed convergence review. Found 7 majors that single reviewer might have missed in later skills due to context pressure.
## When splitting decision files with memory-index entries
- The validation script handles relocating memory-index entries to match their actual file locations. Do not manually move entries between sections during a file split — add new entries, let the validator handle section assignment.
- Evidence: Split workflow-optimization.md → workflow-execution.md, manually reorganized 14 memory-index entries between sections. User corrected: validator does this automatically.
## When naming learning headings
- Anti-pattern: naming the heading after the antipattern itself ("When recall step uses skip condition language"). This describes what went wrong, not where you are.
- Correct pattern: name after the situation at the decision point — the activity you're doing when the rule applies ("When recall gate has skip condition" → you're at the gate, evaluating it).
- Routes to both: **handoff** (writing new ## headings for learnings mid-session) and **codify** (consolidating learnings into permanent docs). Both contexts produce ## headings that become memory-index triggers.
- Same principle applies to memory-index trigger naming: trigger = situation, not antipattern label.
## When redesigning a process skill
- The skill's own failure modes govern its redesign if you use it on itself (circular dependency).
- Correct pattern: ground against external frameworks first. The grounding step externalizes the design reasoning — principles come from outside the system, not from the skill's own reasoning. Then the redesign is execution of grounded conclusions (moderate complexity), not design from scratch (complex).
- Corollary: by the grounded skill's own classification criteria, the redesign has clear requirements (grounding gaps with proposed fixes), no architectural uncertainty (grounding resolved it), and bounded scope → Moderate, routes to direct execution or /runbook, not full /design.
- Evidence: /design grounding produced 8 principles and 7 gaps from 6 external frameworks. All 7 gap fixes were prose-only edits to existing sections — direct execution, no runbook needed.
## When writing hook redirect messages
- Anti-pattern: "Use X instead of Y" without explaining why. Agent sees the redirect but lacks rationale to internalize the preference — may override in future invocations.
- Correct pattern: Include brief rationale in every hook message. "Use X directly — python3 prefix breaks permissions.allow matching." Rationale improves agent adherence because it provides a reason to comply, not just an instruction.
- Platform noise: Claude Code prepends `[hook-command-path]:` to stderr on exit 2 blocks. Shorten hook commands in settings.json (drop interpreter prefix, drop `$CLAUDE_PROJECT_DIR`) to reduce this noise. Scripts have shebangs; hooks execute from project root.
## When using permission deny for Bash commands
- Anti-pattern: `"Bash(rm:*/index.lock)"` in permissions deny list to block lock removal. Looks correct but never fires — rm runs within the sandbox without needing explicit permission, so the permission check (and its deny list) is bypassed entirely.
- Correct pattern: PreToolUse hook on Bash matcher with script that inspects `tool_input.command`. Hook fires unconditionally before execution, independent of sandbox/permission state.
- Evidence: deny entry `"Bash(rm:*/.git/index.lock)"` existed in settings.json and was bypassed. User confirmed: "denylist is ineffective, operation does not require sandbox bypass." Hook replaced it.
## When requirements capture needs recall
- /requirements skill lacks a recall pass. /design has A.1 (recall), but /requirements goes straight from conversation extraction to codebase discovery. This session needed `/recall deep` before `/requirements` to load 33 entries from 9 decision files — data-processing patterns, feedback pipeline architecture, CLI conventions, session format knowledge. Without recall, requirements would have been naive (e.g., UUID-only filtering when agent files also contain commit data).
- Correct pattern: /requirements should have a recall step between mode detection and conversation scanning, producing a recall artifact. The recall grounds the extraction — agent knows what infrastructure exists before interpreting what the user asked for.
- Fixed: Added recall pass to /requirements (invokes `/recall all`), updated /design A.1 to also invoke `/recall all`. Both skills now produce entry-keys-only recall artifacts — downstream consumers resolve fresh content via when-resolve.py.
## When writing recall artifacts
- Anti-pattern: Full excerpts per entry (heading + source + relevance + content excerpt). Creates stale snapshots — if decision files change between artifact creation and consumption, excerpts are outdated.
- Correct pattern: Entry keys only. Artifact lists trigger phrases with 1-line relevance notes. Downstream consumers batch-resolve via `when-resolve.py` to get current content. No staleness, no excerpt duplication.
- Evidence: `plans/skills-quality-pass/recall-artifact.md` used keys-only format; `plans/task-lifecycle/recall-artifact.md` used full excerpts. Keys-only is structurally superior — the artifact is a curated index, not a cache.
## When routing prototype/exploration work through pipeline
- Anti-pattern: Design skill's behavioral-code gate routes ALL non-prose work to /runbook. /runbook tier assessment counts files against production conventions (test mirrors, module splitting, lint gates). A C-3 prototype script in plans/prototypes/ gets assessed as Tier 3 (~20 TDD cycles). Procedural momentum from practiced pipeline (/design → /runbook → /orchestrate) overrides explicit prototype constraint.
- Correct pattern: Artifact destination determines ceremony level. Prototype scripts (plans/prototypes/, one-off analysis, spikes) don't need runbooks, TDD, or test files. Design resolves complexity; post-design a prototype is direct implementation regardless of behavioral code. The classification model conflates code type (behavioral vs prose) with work type (production vs exploration) — needs grounding.
- Fix: `plans/complexity-routing/problem.md` — grounding pass to rebuild classification + routing model from established frameworks.
- Evidence: Session-scraping prototype interrupted by user after /runbook began Phase 0.5 discovery for a "quick prototype."
## When grounding identifies gaps in existing structure
- Anti-pattern: Treating existing operational structure (e.g., three execution tiers) as ungrounded because external methodology frameworks don't prescribe it. Looking for the wrong kind of grounding — methodology frameworks validate principles, not execution mechanics.
- Correct pattern: Operational structure can be grounded in execution environment constraints (context window capacity, delegation overhead, prompt generation cost) rather than external methodology. The external frameworks validate the principle (match process weight to need); the environment constraints validate the specific structure.
- Evidence: Three-tier execution structure initially flagged as gap ("binary models adapted to three-level without external precedent"). User explained tiers map to context window economics — inline/delegate/orchestrate boundary is capacity and orchestration complexity. Reclassified from gap to grounded.
## When assessing grounding gaps for relevance
- Anti-pattern: Including gaps that solve problems from a different execution context. Time-boxing (from XP spikes) solves human-attention wandering. Prototype-to-production gate (from Lean Startup) solves organizational transition decisions. Neither applies to agentic execution where context windows bound exploration and users decide productization.
- Correct pattern: Evaluate each external framework concept for applicability to the actual execution environment before importing as a gap. The concept may be valid in its source domain but irrelevant here.
- Evidence: Time-boxing removed (context window is the natural bound), prototype-to-production gate removed (user invokes `/design` when ready — existing pipeline handles it).
## When selecting gate anchor tools
- Anti-pattern: Using a tool because it's "related" to the gate's domain without checking its preconditions match the gate's execution context. `recall-diff.sh` uses `git log --since=mtime` — requires intervening commits between artifact creation and gate point. At A.2.5, exploration reports are uncommitted; the script finds nothing.
- Correct pattern: Verify the tool's mechanism matches the gate's runtime state. The right anchor is the tool that will be called on the positive path (`when-resolve.py`) — add a no-op mode (`null`) so the negative path has equal cost.
- Evidence: A.2.5 post-explore recall gate initially used recall-diff.sh. Discussion revealed it can't detect uncommitted exploration reports.
## When design gates bypass downstream pipeline
- Anti-pattern: Direct execution gate in `/design` checks coordination complexity but not capacity. Gate bypasses `/runbook` entirely — if capacity isn't assessed, large-scope work routes to inline execution because it has "no coordination complexity."
- Correct pattern: Gates that bypass downstream stages must union the criteria of all bypassed stages. Design's direct execution gate bypasses runbook tier assessment, so it must assess both coordination complexity (is this structurally simple?) and capacity (does it fit inline?).
- Evidence: Phase B/C.5 direct execution criteria lacked session span and model constraints. Runbook Tier 1 has them because it's the inline-capacity gate.
## When mapping hook output channel audiences
- Empirical finding (TEST=1–7): `additionalContext` → agent-only (system-reminder, no user output); `systemMessage` → user-only ("PreToolUse:Bash says: ..."); `permissionDecisionReason` → both audiences, repeats twice in CLI; stderr+exit 2 → both, 1 line, `[hook-path]:` prefix noise.
- Correct pattern for PreToolUse blocks: `permissionDecision:deny` JSON on exit 0. Short non-empty `permissionDecisionReason` (goes to both, repeated — keep brief); `additionalContext` for extended agent instructions (agent-only); `systemMessage` for user summary (user-only, ~60 chars).
- Supersedes: "Platform noise: shorten hook commands" workaround in "When writing hook redirect messages" — permissionDecision:deny eliminates path noise without command shortening.
## When implementing pre-delegation gates as PreToolUse hooks
- Anti-pattern: PreToolUse hook on Task tool with exit 0 + additionalContext advisory ("consider doing recall first"). No model re-run between PreToolUse hook and tool execution for exit 0. Task dispatches, runs, completes before agent reads the advisory — the gate is post-delegation.
- Correct pattern: Block with `permissionDecision:deny`. Gate by `subagent_type` discriminator (execution agents: artisan, test-driver, corrector, runbook-corrector, design-corrector, outline-corrector, runbook-outline-corrector, tdd-auditor, refactor) — more precise than plan-path in prompt. Fragments don't load in sub-agents; recall-artifact is the only project context transport.
## When writing hook user-visible messages
- Terminal constraint: "UserPromptSubmit says: " prefix = ~29 chars; ~90 char terminal = ~60 chars for content. Authored independently from additionalContext (agent text is written for agents, not for display).
- Tier 2 injections (discuss, pending, brainstorm, quick, learn): behavioral outline + non-blank line count. Format: `discuss: assess, stress-test, state verdict. (N lines)`. Non-blank lines: `sum(1 for l in expansion.split('\n') if l.strip())`.
- Tier 2.5 guards (1-line injections): authored human summary, not verbatim content. Example: "Agent instructed to use claude-code-guide" not the raw 130-char injection text.
- Terse commands (c, y): same brief text for both audiences — instruction IS the summary.
## When a proximal requirement reveals lifecycle gaps
- Triage feedback (Gap 7) required a post-execution comparison point. Investigation: /commit too generic (fires all sessions), /handoff wrong scope (session state not execution assessment). Root cause: inline execution (Tier 1, /design direct execution) has no lifecycle skill. The pipeline state machine goes /requirements → /design → /runbook → /orchestrate → /deliverable-review → /commit, but work classified as execution-ready exits through an unstructured gap between /design and /handoff.
- Correct pattern: the proximal requirement points at the structural gap. Fix the gap (inline execution skill covering pre-work + execute + post-work), and the proximal requirement becomes one FR among many.
- Corollary: conditional gates ("skip Read if no /design ran") reintroduce prose-gate failure modes. The D+B principle applies: unconditional Read, file absence is the negative path. A Read returning file-not-found is cheaper than the risk of a missed comparison.
## When requirements-clarity gate fires
- /design Phase 0 correctly detected 5 mechanism-free open questions in `plans/triage-feedback/problem.md` and rerouted to /requirements. This is the first empirical validation of the requirements-clarity gate — previously 0 events in n=38 sessions (Gap 4 coverage note in grounding report).
- Data point: Gap 1 remains Mitigated (not Closed). The structured output block format was sufficient to trigger the correct routing decision without a full D+B tool-call anchor.
## When naming skill entry points
- Anti-pattern: Using `--flag` CLI conventions for skill workflow control (e.g., `--chain` to skip pre-work). Skills parse prose arguments, not CLI flags. The flag convention is unnatural and incompatible with the continuation passing system (`[CONTINUATION: /skill args]`).
- Correct pattern: Named entry points matching workflow phase names. `execute` instead of `--chain`. The entry point is just another token in prose args — natural, self-documenting, continuation-compatible. Each skill defines its own entry points from its workflow phases.
- Per "when parsing cli flags as tokens": flags are exact tokens for CLI tools; skill args are prose. Named entry points respect this boundary.
## When recall surfaces outline-affecting entries
- Anti-pattern: Running /recall all, loading 25+ entries across 4 passes, then only applying the entries that matched the original outline structure. New entries from later passes can invalidate or extend decisions made before those entries were loaded.
- Correct pattern: After each recall pass, re-evaluate existing outline decisions against newly loaded entries. In this session: pass 3 loaded "how chain multiple skills together" which required adding continuation protocol to D-6, and "when recall-artifact is absent during review" which required adding fallback to D-4. Both were structural gaps, not minor refinements.
## When implementation modifies pipeline skills
- Anti-pattern: Using the full runbook pipeline (prepare-runbook.py → orchestrator → step files) when the planned work modifies pipeline skills (/design, /runbook) or pipeline contracts. Self-modification coupling: a runbook step that edits the runbook skill creates stale-instruction risk for subsequent steps.
- Correct pattern: Structure as inline task sequence orchestrated through session pending tasks. Each task executes with fresh CLAUDE.md loads, sidestepping stale instructions. TDD discipline preserved — executing session dispatches test-driver via Task tool per cycle. Corrector dispatch per task replaces checkpoint gates.
- Also applies when: no parallelization benefit (strict dependency chain negates Tier 3's parallel step execution), overhead/value mismatch (pipeline coordination cost > error-recovery value for ~10 sequential work units).
## When delegating TDD cycles to test-driver
- Anti-pattern: Sending all N cycles in a single prompt. Agent loses focus on later cycles, context overloaded with spec it hasn't reached yet. Also: full prompt may trigger hooks on path patterns in test fixture descriptions.
- Correct pattern: Piecemeal — one cycle per invocation. Resume the same agent for subsequent cycles (preserves accumulated file reads + implementation context). Continue until agent context nears 150k. Fresh agent if context exhausted.
- Context priming: Sub-agents don't share parent context. Each NEW agent must self-prime by running `when-resolve.py` on relevant recall-artifact entries. Include instruction: "Read plans/X/recall-artifact.md, then batch-resolve relevant entries via `agent-core/bin/when-resolve.py`." Resumed agents already have this context.
## When assessing just precommit cost
- `just precommit` is fast when the test suite is green, thanks to test sentinel. Not a heavy operation in the common case — valid as both entry gate and exit gate without redundant overhead concern.