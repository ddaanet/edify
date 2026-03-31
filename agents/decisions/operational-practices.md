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

**Correct pattern:** Include explicit code quality and factorization directives in refactor prompts.

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

**Specific case — brainstorm-name:** Do not launch a new brainstorm-name agent with "do NOT repeat" constraints. Resume the prior agent. It retains its full context — existing candidates, conceptual space explored, metaphor domains considered. Resumption produces genuinely novel names; fresh launch risks adjacent-to-excluded names.

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

### When Merging Worktree With Consolidated Learnings

**Decision Date:** 2026-02-20

**Anti-pattern:** Git merge brings branch's full learnings.md (pre-consolidation content) over main's consolidated version. Branch diverged before consolidation; merge favors longer file.

**Correct pattern:** After merging a branch that diverged before a learnings consolidation, verify learnings.md. Only the delta (new entries added on branch after divergence) should be appended to main's consolidated version.

### When Batch Review Routing Overrides Per-Artifact Judgment

**Decision Date:** 2026-02-21

**Anti-pattern:** Collapsing multi-file batch into single reviewer. Agent fabricates capability limitations on the correct reviewer to justify the simpler single-reviewer path. Same root cause as "batch momentum skip prevention."

**Correct pattern:** Apply proportionality per-file (trivial → self-review). Route remaining by artifact type per routing table. Routing is per-artifact-type, not per-batch.

### When Discovery Decomposes By Data Point

**Decision Date:** 2026-02-21

**Anti-pattern:** Brief presents N items sharing identical structure. Agent mirrors the table — one verification chain per row — instead of recognizing a single parametrized operation.

**Correct pattern:** Identify the operation pattern first. Verify it holds (1-2 spot checks). Produce a single inline step with a variation table, not N separate steps.

### When Verifying Delivered Plan Artifacts

**Decision Date:** 2026-02-21

**Anti-pattern:** Checking file existence (`test -f`) as proof of delivery. Presence ≠ completeness.

**Correct pattern:** Verify content — line counts for substance, function/class signatures for API coverage, test counts for coverage. Cross-reference against requirements.

### When Assessing Fragment Demotion

**Decision Date:** 2026-02-20

**Anti-pattern:** Defending "frequently useful" as "always needed." Treating workflow-specific content as cross-cutting.

**Correct pattern:** Distinguish behavioral rules (shape every interaction, no injection point) from procedural/reference content (needed at specific workflow steps, injectable via skills/hooks). Passive fragments that don't trigger behavior are dead weight regardless of content quality.

### When Evaluating Recall System Effectiveness

**Decision Date:** 2026-02-20

**Anti-pattern:** Measuring "did the agent use the lookup tool" as proxy for recall improvement. The lookup tool requires the same metacognitive recognition step as the passive index it replaced.

**Correct pattern:** Distinguish recognition (knowing when to look something up) from retrieval (performing the lookup). Tools that improve retrieval without addressing recognition produce no measurable improvement. Forced injection (hooks detect topic mechanically, inject content) bypasses recognition entirely.

**Evidence:** 801 sessions, 22 `/when` invocations in 8/193 post-merge sessions (4.1%). Baseline skill activation ~20%; `/when` at 4.1% suggests metacognitive triggers have additional activation penalty vs procedural triggers.

### When Loading Context Before Skill Edits

**Decision Date:** 2026-02-20

**Anti-pattern:** Modifying skill `description` frontmatter without loading the platform skill guide first.

**Correct pattern:** Load `/plugin-dev:skill-development` before editing any skill file. The `description` frontmatter is what Claude Code displays in the CLI slash command picker — it serves dual duty (agent triggering + user display). Lead with an action verb describing what the skill does, then include trigger phrases. The H1 title is body content only — not shown in the picker.

### When Reusable Components Reference Project Paths

**Decision Date:** 2026-02-20

**Anti-pattern:** Hardcoding project-specific paths (e.g., `plugin/skills/**`) in reusable packages or submodule code.

**Correct pattern:** Project-specific paths belong in project-level configuration (e.g., `pyproject.toml`). Reusable code reads config, doesn't hardcode paths.

### When Validate-Runbook Flags Pre-Existing Files

**Decision Date:** 2026-02-21

**Anti-pattern:** Treating lifecycle exit 1 violations as blocking when the runbook modifies pre-existing files.

**Correct pattern:** Verify flagged files exist on disk. If pre-existing, the violation is a false positive. Real violations are "modify before create" for NEW files.

### When Execution Routing Preempts Skill Scanning

**Decision Date:** 2026-02-20

**Anti-pattern:** Forming an execution plan (Read → Edit → Write) without checking if a skill handles the workflow. Skill matching gate never fires.

**Correct pattern:** Skill matching must precede execution routing. Structural fix: UserPromptSubmit hook injects skill-trigger reminders. Rule strengthening alone doesn't work.

**Evidence:** Forced-eval hook reaches 84% activation vs 20% baseline.

### When Skill Sections Cross-Reference Context

**Decision Date:** 2026-02-20

**Anti-pattern:** Back-referencing criteria from a different gate that has context-dependent framing. The referenced gate's framing only applies under different preconditions.

**Correct pattern:** Inline shared criteria at each usage site with context-appropriate framing.

### When Recovering Broken Submodule Worktree Refs

**Decision Date:** 2026-02-21

**Correct pattern:** `git worktree repair` for parent repo links. For submodule worktrees: remove broken `.git` pointer files, remove stale admin dirs, then `git -C <submodule> worktree add --detach <path> HEAD`. Fix HEAD: `git ls-tree HEAD <submodule>` gives expected commit.

**Root cause:** `core.worktree` in `.git/modules/<submodule>/config` gets overwritten when a worktree runs `submodule init`.
