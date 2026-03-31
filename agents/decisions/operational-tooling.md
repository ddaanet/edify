# Operational Tooling

Git workflow, platform constraints, code patterns, and naming conventions.

## .Git Workflow Patterns

### When Git Operation Fails

**Decision Date:** 2026-02-18

**Anti-pattern:** Attributing git failure to a plausible-sounding restriction without reading the error message. Confabulating explanations ("git refuses to merge with active worktree" — false) creates false premises for subsequent decisions, deletes test coverage to work around non-existent limitations.

**Correct pattern:** Read actual error output. Reproduce with a minimal case before restructuring. Test failures that seem like infrastructure problems may reveal real production bugs.

**Deeper pattern:** Confabulation serves as license to stop investigating. A "can't be fixed" explanation converts a solvable problem into an unsolvable one, justifying coverage-reducing workarounds.

### When No-Op Merge Orphans Branch

**Decision Date:** 2026-02-12

**Decision:** Always create merge commit when `git merge --no-commit` was initiated.

**Rationale:** Without merge commit, branch is unreachable from HEAD → `git branch -d` rejects.

### When Naming Tasks For Worktrees

**Decision Date:** 2026-02-12

**Decision:** Constrain task names to `[a-zA-Z0-9 ]` — slug derivation is near-identity.

### When Requiring Clean Git Tree

**Decision Date:** 2026-02-12

**Decision:** Require clean tree before merge/rebase operations. No `git stash` workarounds.

**Exception:** Session context files (session.md, learnings.md) auto-committed as pre-step.

**Rationale:** Stash is fragile (conflicts on pop, lost stashes). Clean tree forces explicit state management.

### When Failed Merge Leaves Debris

**Decision Date:** 2026-02-12

**Decision:** After merge abort, check for untracked files materialized during the attempt.

**Anti-pattern:** Assume aborted merge is clean — retry fails with "untracked files would be overwritten."

**Fix:** `git clean -fd -- <affected-dirs>` to remove debris, then retry.

### When Git Lock Error Occurs

**Decision Date:** 2026-02-12

**Decision:** Never delete lock files. Retry the original git command — lock contention from concurrent worktree sessions is transient and self-resolves after model latency.

**Anti-pattern:** Agent removes `.git/index.lock` after git error suggests manual removal. Also: hook blocks rm but says "retry" without specifying what — agent retries the rm instead of the original git command.

**Rationale:** Worktrees share the parent `.git` directory. Concurrent Claude sessions in different worktrees cause transient index.lock contention. The lock releases in milliseconds; model latency (3-10s) provides natural backoff. Deleting the lock risks corrupting the concurrent operation.

### When Tracking Worktree Tasks In Session.md

**Decision Date:** 2026-02-28 (supersedes 2026-02-19)

**Anti-pattern:** Single "Pending Tasks" section with move semantics (Pending → Worktree on create, Worktree → Completed on rm). Creates merge-commit amend ceremony (`_update_session_and_amend` exit 128 on merge commits), requires manual editing for bare-slug worktrees, drifts from filesystem state.

**Correct pattern:** Two-section model — "In-tree Tasks" (quick, mechanical, no isolation) + "Worktree Tasks" (plan dir + behavioral changes, or restart, or explicitly parallel). Classification is static — set at task creation, no moves between sections. `→ \`slug\`` marker added/removed inline by `add_slug_marker()`/`remove_slug_marker()`. `#status` annotates from `_worktree ls` (filesystem state).

**Rationale:** Eliminates three failure modes: (a) no move semantics removes amend ceremony, (b) bare-slug worktrees orthogonal (no session integration expected), (c) `#status` renders from filesystem, not session.md section content. Design: `plans/task-classification/outline.md` D-4.

### When Merging Worktree With Consolidated Learnings On Main

**Decision Date:** 2026-02-20

**Anti-pattern:** Git merge brings in the branch's full learnings.md (pre-consolidation content) over main's consolidated version. Branch diverged before consolidation; merge favors longer file.

**Correct pattern:** After merging a branch that diverged before a learnings consolidation, verify learnings.md line count. Only the delta (new entries added on branch after branch point) should be appended to main's consolidated version.

**Evidence:** Merge brought 199 lines (branch) over 30 lines (main consolidated). 175 lines were pre-consolidation duplicates.

### When Comparing File Versions Across Branches

**Decision Date:** 2026-02-20

**Anti-pattern:** Using `wc -l` equality to conclude files are identical. Same line count does not mean same content.

**Correct pattern:** Diff content, not counts. `git diff <base>..<branch> -- <file>` or compare actual text.

**Evidence:** Learnings.md had 62 lines on both merge base and branch → concluded "no changes." Post-merge found 36 genuine new entries.

### When Validating Worktree Merges

**Decision Date:** 2026-02-24

**Anti-pattern:** Trusting `_worktree merge` autostrategy for session.md without post-merge validation. The autostrategy resolves in favor of the branch's focused session, dropping main-only content (Worktree Tasks entries for other worktrees, blocker formatting).

**Correct pattern:** `remerge_session_md(slug)` now runs in phase 4 on ALL merge paths, structurally merging session.md via `_merge_session_contents`. Manual validation no longer required for known failure modes (WT section drops, task list loss, blocker bleed). Still validate novel merge scenarios not yet covered by tests.

**Evidence:** Merge 1 dropped "Update grounding skill" from Worktree Tasks. Merge 2 left orphaned entry + malformed blocker line. Fix: `remerge_session_md` in resolve.py.

### When Merging Completed Tasks From Branch

**Decision Date:** 2026-03-01

**Anti-pattern:** Autostrategy's additive union (`new_blocks` in `_merge_session_contents`) carries branch-completed `[x]` and branch-canceled `[–]` tasks into main's Pending Tasks. These are ephemeral — created and resolved within the worktree session. On main, they cause duplicate-section validator failures.

**Correct pattern:** Filter completed and canceled tasks from the additive merge. In `resolve.py` line 85, exclude blocks whose first line contains `- [x]` or `- [–]`. The branch's deliverables are in the merge commit; the task entries have no value on main. Only uncompleted `[ ]`, blocked `[!]`, and failed `[†]` tasks should carry over.

**Evidence:** continuation-prepend merge brought 4 `[x]` tasks into Blocked/Terminal section. Precommit validator caught "task in both Pending and Worktree." Manual fix required.

### When Choosing Task Status Markers

**Decision Date:** 2026-03-01

**Decision:** Task status notation uses single-width characters that are visually self-documenting:

| Marker | Status | Mnemonic |
|--------|--------|----------|
| `[ ]` | Pending | Empty — work not started |
| `[x]` | Completed | GFM standard checkbox |
| `[>]` | In-progress | Arrow — forward motion |
| `[!]` | Blocked | Exclamation — attention |
| `[†]` | Failed | Dagger — dead |
| `[-]` | Canceled | Hyphen — struck through |

**Rationale:** Symbols that carry meaning through visual form (`!`, `-`, `>`, `†`) beat letters requiring convention lookup (`B`, `C`, `W`, `F`). Only `[ ]` and `[x]` are valid GFM checkboxes (per spec §5.3); all others are text conventions parsed by project tooling. Changed `[✗]` → `[†]` because `✗` (U+2717) is visually confusable with `x` (U+0078) — different codepoints but near-identical in many fonts. `†` (U+2020 dagger) is unmistakable and transparently means "dead." Changed `[–]` → `[-]` because `–` (U+2013 en dash) is visually confusable with `-` (U+002D hyphen-minus) — and `-` is what humans type. Same confusability class as `✗`/`x`.

### When Codify Triggers On A Feature Branch

**Decision Date:** 2026-03-02

**Do not codify on feature branches.** Decision file changes create merge conflicts with main's decisions/. Defer codification to main. The soft-limit age calculation should account for branch context — learnings on feature branches are younger in main-branch terms.

### When Designing Hierarchical Index Structures

**Decision Date:** 2026-03-06

**Anti-pattern:** Mixed indices containing both entries and child references. Creates discoverability imbalance — inline entries are immediately visible and individually selectable, while child-referenced entries require an extra navigation step.

**Correct pattern:** Clean separation — branch indices (index-of-indices only) vs leaf indices (entries only). Uniform discovery paths: root → branch(es) → leaf → entry. Simplifies parser (no mixed-mode detection).

### When Classifying Settings.local.json Entries During Triage

**Decision Date:** 2026-03-06

**Anti-pattern:** Conflating skill `allowed-tools` (scope declaration — what tools a skill CAN invoke) with `settings.json` `permissions.allow` (friction elimination — what's pre-approved without user prompt). Concluding an entry is "session-specific" because the skill's allowed-tools already covers it.

**Correct pattern:** Check `settings.json` permissions.allow for the specific command pattern. If the script runs on every invocation of a workflow step, it needs a permanent `settings.json` entry regardless of skill allowed-tools. The two systems are independent.

## .Known Issues

### When CLI Command Fails And Raw Commands Are Denied

**Decision Date:** 2026-02-20

**Anti-pattern:** Decomposing a failed CLI tool into its constituent git commands for diagnostics. Each raw command is denied, but the denial is parsed as a permission obstacle rather than a routing signal.

**Correct pattern:** After CLI failure, retry with escalated flags (`--force`) before attempting raw commands. If `--force` isn't available, check `--help` for diagnostic subcommands. The deny list is a routing signal — it means "use the wrapper."

**Evidence:** 7 denied `git worktree`/`git branch` commands before using `claudeutils _worktree rm --force`, which succeeded immediately.

### When ClassifyHandoffIfNeeded Bug Occurs

**Bug:** `ReferenceError: classifyHandoffIfNeeded is not defined` in Claude Code's SubagentStop processing.

**Affected:** v2.1.27+. NOT fixed.

**Scope:** Only `run_in_background=false` Task calls fail. `run_in_background=true` works.

**Workaround:** Use `run_in_background=true` for Task calls.

**GitHub issues:** #22087, #22544.

## .Sub-agent Limitations

### When Sub-Agents Cannot Spawn Sub-Agents

**Limitation:** Task tool is unavailable in sub-agents. All delegation must originate from main session.

**Also unavailable:** MCP tools (Context7), hooks.

**Available:** Read, Grep, Glob, Bash, Write, Edit (direct tool use only).

### When Resolving Session.md Conflicts During Merge

**Decision Date:** 2026-02-18

**Anti-pattern:** Using `git checkout main -- agents/session.md` to resolve conflicts — discards all branch-side session data (new tasks, metadata) without verification.

**Correct pattern:** After any session.md conflict resolution, read the full file and compare against the known task list. Verify no tasks were dropped. Branch session.md may contain tasks added during worktree work that don't exist on main.

**Evidence:** "Simplify when-resolve CLI" task existed only in worktree-merge-errors branch session.md. `checkout main --` silently dropped it. Caught only because user requested explicit content verification.

### When Removing Worktrees With Submodules

**Decision Date:** 2026-02-18

**Anti-pattern:** `wt rm` removes worktree directory but leaves `.git/modules/plugin/config` `core.worktree` pointing to the deleted directory. Also doesn't check if submodule branch has unmerged commits (parent repo branch merged but submodule branch diverged).

**Correct pattern:** `wt rm` must (1) restore submodule's `core.worktree` to main checkout path, (2) check submodule branch merge status before deletion. Both are data-loss vectors — stale config breaks all submodule operations, unmerged submodule branch loses commits.

**Evidence:** `git -C plugin` failed with "cannot chdir to removed directory" after `wt rm runbook-skill-fixes`. Agent-core branch had 3 files of real diffs silently orphaned.

### When Importing Artifacts From Worktrees

**Decision Date:** 2026-02-18

**Transport:** `git show <branch>:<path>` from main — no cross-tree sandbox access needed. All worktrees share the git object store.

**Scope:** Only design.md and requirements.md are import candidates (small, authored). Runbooks (phase files, steps, orchestrator plans) are bulky, generated, implementation-oriented — require explicit intent, not casual import.

**Ownership check:** Before importing, verify no active worktree owns the target plan directory (`git worktree list` + check branch names). Importing into a worktree-owned plan creates merge conflicts when that worktree merges back.

**Supersedes:** "When worktree agents need cross-tree access" (additionalDirectories unnecessary for transport).

### When Workaround Requires Creating Dependencies

**Decision Date:** 2026-02-18

**Anti-pattern:** Escalating workarounds for a tool limitation — each fix creates a new problem requiring another fix. Each step locally rational, trajectory absurd.

**Stop condition:** If a workaround requires more than 2 steps or introduces new dependencies, stop and report the tool limitation. "Pre-resolve conflict" is bounded: edit conflicting regions of files that ALREADY EXIST on both sides. Creating new files, new modules, or new dependency chains means you've left "pre-resolution" and entered "manual reimplementation."

**Deeper pattern:** Sunk cost momentum — each workaround invests more context, making "just one more fix" feel cheaper than stopping. The "stop on unexpected results" rule doesn't fire because each step is rationalized as part of the documented workaround path.

**Evidence:** 6-step escalation chain during design-workwoods merge. Two commits on main, partially-created planstate module, still not merged.

### When Recovering Agent Outputs

**Decision Date:** 2026-02-18

**Anti-pattern:** Manually reading agent session log and retyping content.

**Correct pattern:** Script extraction from task output files. Agent Write calls are JSON-structured in `tmp/claude/.../tasks/<agent-id>.output`. Parse with jq or Python, recover deterministically.

**Prototype:** `plans/prototypes/recover-agent-writes.py`

## .Python Patterns

### When Extracting Git Helper Functions

**Pattern:** Private `_git(*args, check=True, **kwargs) -> str` helper — 1 line per call, fits 88-char limit.

**Evidence:** 24 calls replaced, 477→336 lines (30% reduction) in worktree cli.py.

### When Fixture Shadowing Creates Dead Code

**Anti-pattern:** Defining local function with same name as pytest fixture — function is unreachable dead code.

**Detection:** Grep for function definitions that duplicate fixture names, check if test functions use fixture injection.

### When Test Corpus Defines Correct Behavior

**Anti-pattern:** Rewriting fixtures to avoid triggering known bugs.

**Correct pattern:** Fixtures define correct behavior — failing tests are the signal that code needs fixing.

## .Memory Index Patterns

### .When Index Keys Must Be Exact

**Decision:** Index entry key must exactly match heading key — fuzzy matching is only for resolver runtime recovery.

**Rationale:** Exact keys are deterministic and debuggable.

### When DP Matrix Has Zero-Ambiguity

**Decision:** Initialize DP matrix with -inf for impossible states, 0.0 only for base case.

**Evidence:** "when mock tests" scored 128.0 against candidate with no matching chars — positive score from nothing.

## .Runbook Validation Patterns

### When Phase Numbering Is Flexible

**Decision:** Detect starting phase number from first file, validate sequential from that base.

**Rationale:** Design decisions may use 0-based or 1-based numbering.

### When Checking Self-Referential Modification

**Anti-pattern:** Runbook step uses `find plans/` — includes the executing plan's own directory.

**Correct pattern:** Exclude plan's own directory or enumerate specific targets.

## .Naming Patterns

### When Avoiding CLI Skill Name Collision

**Decision:** Check CLI built-ins before naming skills.

**Scope:** /help, /plan, /review, /model, /clear, /compact, and other built-in commands.

### When Choosing Name

**Decision:** Prioritize human discovery and recall over thematic alignment or cleverness.

**Applies to:** Skill names (slash commands), agent names, command names — any user-facing identifier the human must remember or search for.

**Priority order:**
1. **Discoverability** — The word the user thinks of when they need the capability should match the handle. "I need to ground this" → `/ground`, not `/found`.
2. **Recall** — Short, common words beat etymologically precise ones. If a user can't remember the name after one use, it's wrong.
3. **Thematic alignment** — Nice to have (e.g., construction metaphors pairing with a plugin named "edify"), but never at the cost of discoverability.

**Anti-pattern:** Choosing `/found` (Latin *fundare*, pairs with "edify") over `/ground` (the word people actually use when describing the need).

**Test:** "What word would someone type if they needed this capability and didn't know the command existed?" That word is the name.

### When Constraining Task Names For Slug Validity

**Decision Date:** 2026-02-19

**Anti-pattern:** Propagating the 25-char git branch slug limit to task naming time. Forces suboptimal prose keys for tasks that may never become worktrees.

**Correct pattern:** Task names are prose keys (session management layer). Slug derivation is a worktree concern. When a derived slug is too long, provide a `--slug` override at invocation time. **Gap:** No `--slug` override exists yet — current workaround is bare `_worktree new <slug>` which loses session integration.

**Rationale:** Layers should not share constraints. The enforcement point (worktree creation) is the right place to surface slug limits, not the point of task authoring.

## .Scripting Principles

### When Choosing Script Vs Agent Judgment

**Decision Date:** 2026-02-12

**Decision:** If solution is non-cognitive (deterministic, pattern-based), script it. Always auto-fix when possible.

**Anti-pattern:** Using agent judgment for deterministic operations.

**Corollary:** Reserve agent invocations for cognitive work (design, review, ambiguous decisions).

### When Script Should Generate Metadata

**Decision Date:** 2026-02-12

**Anti-pattern:** Script validates metadata presence but expects cognitive agent to generate it.

**Correct pattern:** If metadata is deterministic and standard, script injects it during assembly.

### When Bootstrapping Around Broken Tools

**Decision Date:** 2026-02-12

**Decision:** When replacing a workflow tool, assess tier from design and execute directly if feasible.

**Key insight:** The design document IS the execution plan when work is well-specified.

## .Measurement Patterns

### When Measuring Agent Durations

**Decision Date:** 2026-02-19

**Anti-pattern:** Computing duration as timestamp delta between tool_use and tool_result — includes laptop sleep time, producing artifact "outliers."

**Correct pattern:** Use `duration_ms` from Task result metadata when available. Cross-reference with tool_uses to validate: normal p50=6.6s/tool. Flag entries >30s/tool as sleep-inflated.

**Evidence:** 13/951 entries flagged, all confirmed artifacts.

### When Analyzing Sub-Agent Token Costs

**Decision Date:** 2026-02-19

**Anti-pattern:** Treating `total_tokens` from CLI `<usage>` as fresh input cost. The field sums all token types (cache reads + writes + fresh) without decomposition.

**Correct pattern:** Use main session first-turn `cache_creation_input_tokens` to measure system prompt size (~43K tokens p50). Use minimal-work agents (≤3 tool uses) for fixed overhead proxy.

**Evidence:** 709 Task calls analyzed. Minimal-work agents: 35.7K total_tokens p50. Main session cache hit rate: 94-100% after warmup.

## .Merge and Reclassification Patterns

### When Merge Fails On Main

**Decision Date:** 2026-03-02

**Anti-pattern:** Resolving conflicts and precommit failures on main after `_worktree merge`. Main lacks branch context — it resolves conflicts by reading diff markers, not understanding intent. Precommit failures leave a broken merge commit on main requiring amend.

**Correct pattern:** `git merge --abort` on failure. Branch merges main into itself first (plan: `worktree-merge-from-main`), resolves conflicts in its own context, passes precommit, then main retries. Main-side merge becomes trivially clean.

**Implication:** `worktree-merge-from-main` is a prerequisite for merge resilience, not independent. Sequence: build `merge --from-main` → modify `_worktree merge` to rollback-and-report → skill guides user to update branch then retry.

**Exception:** Session.md/learnings.md auto-resolve (`remerge_session_md`, `remerge_learnings_md`) may still run on main — these are mechanical, context-free. Rollback applies to source conflicts and precommit failures where main lacks resolution context.

**Also:** Never `--force` remove a worktree without first listing uncommitted files. Two uncommitted files lost permanently in one incident.

### When Reclassifying Tasks After Structural Changes

**Decision Date:** 2026-03-02

**Anti-pattern:** Shipping a new classification model (two-section In-tree/Worktree Tasks) without reclassifying existing tasks. Handoff perpetuates defaults — all 60+ tasks stayed In-tree despite D-9 heuristic qualifying most for Worktree Tasks. On main, this left Worktree Tasks empty, making `wt` unable to dispatch.

**Correct pattern:** Structural changes to task organization require a bulk reclassification pass on existing data. Classification heuristics apply retroactively, not just to new tasks.

**Compounding factor:** Stale decision entry in `workflow-advanced.md` (2026-02-20, single-section model) contradicted superseding entry in `operational-tooling.md` (2026-02-28, two-section model). Stale entry never cleaned up on delivery — the plan-completion ceremony gap.
