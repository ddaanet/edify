# Operational Practices

Agent reliability patterns, artifact management, and implementation practices.

## .Artifact and Review Patterns

### When Placing Deliverable Artifacts

**Decision Date:** 2026-02-12

**Decision:** If artifact will be referenced in a followup session → `plans/reports/`. If not → `tmp/`.

**Decision principle:** "Will this be referenced later?" — not "Is this type in a known list?"

**Specific rule:** Research synthesis documents that inform future work (prioritization, skill design, grounding reports) → `plans/reports/` (persistent, tracked, survives sessions). Only scratch computation and intermediate files → `tmp/` (gitignored).

**Anti-pattern:** Writing research synthesis to `tmp/` — it won't survive across sessions and can't be referenced in future planning.

### When Requiring Per-Artifact Vet Coverage

**Decision Date:** 2026-02-12

**Decision:** Each production artifact requires corrector review before proceeding.

**Root cause:** Batch momentum — once first artifact skips review, switching cost increases for each subsequent one.

### When Launching Task Agents In Parallel

**Decision Date:** 2026-02-12

**Decision:** Batch all independent Task calls in single message.

**Wall-clock impact:** Sequential = sum(task_times), parallel = max(task_times).

### When Background Agents Crash

**Decision Date:** 2026-02-12

**Correct pattern:** Check output files and git diff — agents complete work before classifyHandoffIfNeeded error fires.

**Recovery:** Use `run_in_background=true` to avoid the error entirely.

### When Refactoring Agents Need Quality Directives

**Decision Date:** 2026-02-12

**Correct pattern:** Include explicit deslop and factorization directives in refactor prompts.

**Rationale:** Refactor agent focuses on warnings (line limits, complexity), doesn't proactively optimize for token efficiency.

### When Triaging External Diagnostic Suggestions

**Decision Date:** 2026-02-19

**Anti-pattern:** Treating diagnostic report output (e.g., /insights) as a backlog intake pipeline — every suggestion becomes a pending task. Inflates the task list just after compression.

**Correct pattern:** Triage by routing. Superseded → discard. Skill-specific → annotate existing skill task. Simple → inline immediately (write the fragment, don't defer it). Only genuinely new substantial work becomes standalone tasks.

**Evidence:** 15 suggestions triaged to 3 inlined fragments + 5 tasks + 4 annotations. Initial draft had 8 standalone tasks before user caught that fragments were single edits.

## .Agent Reliability Patterns

### When Relaunching Similar Task

**Decision Date:** 2026-02-18

**Anti-pattern:** Launching a fresh agent with the same prompt after a stopped/killed agent, losing prior context.

**Correct pattern:** Use Task tool's `resume` parameter with the prior agent's ID. The agent retains full prior context (files read, reasoning done) and continues from where it stopped.

**Threshold for fresh launch:** If prior agent exchanged >15 messages (context likely near-full — 200K limit approaches), fresh launch is correct. Otherwise resume.

**Rationale:** Stopped agents may have completed expensive operations (file reads, web searches). Resuming preserves that work; relaunching repeats it.

### When Exploration Agents Report False Findings

**Decision Date:** 2026-02-12

**Correct pattern:** Verify file existence claims from scout agents (ls, git ls-tree).

### When Scrubbing Learnings Before Design Input

**Decision Date:** 2026-02-12

**Decision:** Validate learnings against current evidence before using as design constraints.

**Rationale:** Learnings are session-scoped observations, not verified invariants — can be stale or wrong.

### When Diagnosing Review Agent Quality Gaps

**Decision Date:** 2026-02-16

**Problem:** Review agent produces defective fixes. Need to isolate whether the cause is model tier, input content, delegation prompt, or agent instructions.

**Diagnostic procedure (2×2 controlled experiment):**

1. **Identify the defect** in the review agent's output. Note the specific confabulation or error.

2. **Recover the pre-review artifact** from git history (`git show <commit>:<path>`). This is the input the review agent received.

3. **Create test worktrees** at the pre-review commit (`just wt-new <name> <commit>`). One per experimental condition.

4. **Run the review at the alternate model tier** (e.g., opus if original was sonnet). Use the same agent type. Compare: does the alternate model avoid the defect?

5. **Run the original model on the alternate artifact** (cross condition). If the original outline was sonnet-generated, run sonnet review on opus-generated outline. Isolates input content as a variable.

6. **Extract delegation prompts** from session transcripts to control for prompt quality:
   ```python
   # Parse .jsonl session file for Task tool calls
   for msg in session:
       for block in msg.content:
           if block.type == 'tool_use' and block.name == 'Task':
               print(block.input.prompt)
   ```
   Session files at `~/.claude/projects/<project-path>/<session-id>.jsonl`.

7. **Analyze the 2×2 matrix:**

   | | Model A review | Model B review |
   |---|---|---|
   | **Model A input** | original | controlled |
   | **Model B input** | controlled | controlled |

   - Column difference = model tier effect
   - Row difference = input content effect
   - Prompt comparison = delegation quality effect (eliminated if equivalent)

**Artifacts to preserve:** Commit test worktree results before cleanup. Merge test branches with `--no-ff` then revert changes to preserve commit history without polluting the working tree.

**When to apply:** After interactive review catches defects that automated review missed. The diagnostic determines whether to change model tier, agent instructions, or both.

### When Running Multi-Reviewer Diagnostics

**Decision Date:** 2026-02-18

**Anti-pattern:** Running a single reviewer and trusting all findings. Exploration agents produce false positives from over-reading; opus reviewers miss implementation-level issues detectable only by reading source code.

**Correct pattern:** Run 3+ independent reviewers in parallel (opus review, exploration, inline RCA against source code). Cross-reference findings — real issues appear in multiple reviewers or survive verification against source. False positives get filtered by disagreement.

**Evidence:** 3-way review of runbook-phase-1.md found 8 real issues (each reviewer found unique ones) and filtered 2 false positives. Exploration flagged "critical" line number issue that was correct; opus missed `_git()` return value issue only caught by reading source code directly.

### When Performing Root Cause Analysis

**Decision Date:** 2026-02-18

**Anti-pattern:** Finding first cause and jumping to solution (e.g., "expansion has defects → add more review rounds").

**Correct pattern:** Multi-layer RCA with explicit stops between layers.
- L1: What are the symptoms? STOP.
- L2: What caused them? STOP.
- L3: Why was that cause allowed? STOP.
Only then does the fix address the cause, not the symptoms.

**Evidence:** Merge data loss RCA — L1: bugs in code. L2: haiku generated safety-critical code. L3: delegation model assigns by type not risk + no review gate covers behavioral safety. Fix: model floor for Tier 1 steps AND safety criteria in vet.

### When Searching Adjacent Domains

**Decision Date:** 2026-02-18

**Anti-pattern:** Narrowing search to one domain after user feedback (e.g., "not security?" → drop all security searches). Interpreting a correction as exclusion rather than asking for clarification.

**Correct pattern:** When user questions missing coverage ("not X?"), they may mean "why no X?" not "exclude X." Safety and security are adjacent — both warrant research even when the triggering incident is one or the other.

**Evidence:** User said "not security?" meaning "why aren't you searching for security too?" — interpreted as "this isn't about security" and dropped security entirely.

## .Architectural Principles

### When Temporal Validation Required For Analysis

**Decision Date:** 2026-02-12

**Decision:** Correlate session timestamps with git history to validate feature availability before analysis.

**Git commands:** `git log --format="%ai" --follow <file>` for creation date, session mtime for analysis window.

### .When Behavioral Triggers Beat Passive Knowledge

**Decision Date:** 2026-02-12

**Decision:** `/when` (behavioral) and `/how` (procedural) only — these prescribe action, creating retrieval intention.

**Consequence:** If a learning can't be phrased as `/when` or `/how`, it's either a fragment (ambient) or lacks actionable content.

### .When Enforcement Cannot Fix Judgment

**Decision Date:** 2026-02-12

**Decision:** Enforcement works for structural/mechanical checks; judgment requires conversation-level intervention.

**Rationale:** Writing agent can satisfy any structural check with wrong content.

### When Inlining Reference File Subsets For Optimization

**Decision Date:** 2026-02-19

**Anti-pattern:** Inline a "top N" subset of a reference file to avoid a Read call. Agent picks from the visible subset, unaware better matches exist in the full file. Creates a knowledge ceiling.

**Correct pattern:** Either keep the full Read (agent sees all options) or move selection to a CLI tool (e.g., embeddings search over full corpus). Partial inlining is worse than both alternatives.

**Rationale:** Optimization must not degrade decision quality. The agent cannot know what it hasn't seen.
