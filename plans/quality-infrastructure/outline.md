# Quality Infrastructure Reform — Outline

## Approach

Three FRs executed in dependency order: rename first (largest, most coordination), then deslop restructuring (uses new names), then code density decisions (uses new names, additive).

## Key Decisions

**D-1: vet-agent → deprecate, not rename.**
Zero active call sites (exploration report: `reports/explore-reviewer-usage.md`). All production delegation routes to fix-capable agents. The review-only intermediate state it was designed for doesn't occur in practice. Delete the file; don't create `reviewer.md` for something unused.

**D-2: vet-taxonomy.md → embed in corrector.**
63 lines (status table, subcategory codes, investigation format). Inline in corrector agent definition's existing "Status taxonomy" reference. One fewer file to maintain.

**D-3: Code deslop injection via `project-conventions` skill.**
Already contains code quality rules (lines 22-28). Currently 6 agents load it via `skills:` frontmatter (design-vet-agent, outline-review-agent, plan-reviewer, refactor, runbook-outline-review-agent, vet-fix-agent). Add to artisan (quiet-task) and test-driver (tdd-task) — the two code-producing agents currently missing it. Remove inline code quality duplication from quiet-task (lines 94-101). Main session doesn't need code deslop — substantial code work is delegated to agents.

**D-4: Prose deslop → communication.md.**
Merge 5 prose deslop rules into existing communication.md (currently 5 lines). Natural fit — both govern interaction style. Discard principle line ("Slop is the gap...") — it's a nice summary but doesn't add actionable information beyond the rules themselves.

**D-5: Phase ordering — FR-3 → FR-1 → FR-2.**
FR-3 (rename) first because it touches the most files and all subsequent work should use new names. FR-1 (deslop) second because it modifies agent definitions that FR-3 renamed. FR-2 (decisions) last because it's additive prose using new terminology.

**D-6: vet-requirement.md → review-requirement.md.**
Rename to align with vet→review terminology. Update internal agent references (vet-fix-agent→corrector, design-vet-agent→design-corrector, etc.). Keep in CLAUDE.md @-references — demotion is a separate optimization decision.

**D-7: vet skill → review skill.**
Rename directory `agent-core/skills/vet/` → `agent-core/skills/review/`. Update SKILL.md internal references.

## Scope Boundaries

**IN:**
- 10 agent renames per FR-3a/3b tables (5 review/correct + 5 execution)
- vet-agent deprecation (delete, not rename)
- 8 plan-specific agent deletions per FR-3c
- All ~37 reference file updates per Impact Inventory
- Deslop fragment split (prose→communication, code stays in project-conventions)
- Deslop.md removal from CLAUDE.md and deletion
- 5 code density decision entries in cli.md + memory-index triggers
- Symlink regeneration via `just sync-to-parent`
- Cross-reference verification

**OUT:**
- Context optimization (demotion of review-requirement.md from always-loaded) — separate task
- project-conventions restructuring beyond code deslop content
- New agent definitions or capabilities
- Codebase sweep (FR-4, separate plan)
- Changes to prepare-runbook.py crew- prefix generation (future — after rename lands)

## Phases

### Phase 1: Agent Rename (FR-3) — general

**1a. Agent definition renames (git mv):**
- 6 review/correct agents: vet-fix-agent→corrector, design-vet-agent→design-corrector, outline-review-agent→outline-corrector, runbook-outline-review-agent→runbook-outline-corrector, plan-reviewer→runbook-corrector, review-tdd-process→tdd-auditor
- 5 execution agents: quiet-task→artisan, quiet-explore→scout, tdd-task→test-driver, runbook-simplification-agent→runbook-simplifier, test-hooks→hooks-tester
- Embed vet-taxonomy.md content into corrector.md, delete vet-taxonomy.md
- Delete vet-agent.md (deprecated)

**1b. Agent internal reference updates:**
- Update `name:` frontmatter in all renamed agents
- Update cross-references between agents (tdd-auditor refs corrector, runbook-corrector refs corrector, etc.)
- Update skills: frontmatter references if any agent names appear

**1c. Delete plan-specific detritus (8 files in `.claude/agents/`):**
- error-handling-task, pushback-task, runbook-quality-gates-task, when-recall-task
- workflow-rca-fixes-task, worktree-merge-data-loss-task, worktree-merge-resilience-task, workwoods-task

**1d. Skill and fragment renames:**
- `agent-core/skills/vet/` → `agent-core/skills/review/`
- `agent-core/fragments/vet-requirement.md` → `agent-core/fragments/review-requirement.md`
- Update SKILL.md content (vet→review terminology)
- Update review-requirement.md content (agent name references)

**1e. Reference updates across codebase:**
- 7 skill files (commit, runbook, design, deliverable-review, orchestrate, doc-writing, plugin-dev-validation)
- 1 fragment (review-requirement.md — already renamed)
- 6 decision files (pipeline-contracts, operational-practices, workflow-optimization, workflow-advanced, project-config, orchestration-execution)
- 2 doc files (tdd-workflow, general-workflow)
- 2 other agent-core files (README.md, bin/focus-session.py)
- 1 memory-index (agents/memory-index.md)
- 2 session files (session.md, learnings.md)
- 1 rules file (.claude/rules/plugin-dev-validation.md)
- CLAUDE.md @-references (vet-requirement→review-requirement)
- Terminology propagation: "vet report"→"review report", "vet-fix report"→"correction", "vetting"→"review/correction" across all updated files

**1f. Symlink sync + verification:**
- Remove stale symlinks in `.claude/agents/` and `.claude/skills/` left by renames (old-name symlinks now dangling after `git mv` in agent-core)
- `just sync-to-parent` to regenerate correct symlinks
- Grep for old names across entire codebase to catch stragglers
- **Requires session restart** after completion — agent definitions load at session start

### Phase 2: Deslop Restructuring (FR-1) — inline

**2a. Merge prose deslop into communication.md:**
- Add 5 prose rules from deslop.md as new subsection in communication.md (rules only — strip ❌/✅ examples to keep ambient context lean)
- Discard principle line ("Slop is the gap...")

**2b. Update project-conventions skill:**
- Remove prose section (now in communication.md, ambient)
- Add missing code rule: "Expose fields directly until access control needed" (present in deslop.md line 40, missing from project-conventions)
- Keep code section, token economy, tmp rules

**2c. Add skills: frontmatter to code-producing agents:**
- artisan.md: add `skills: ["project-conventions"]`
- test-driver.md: add `skills: ["project-conventions"]`

**2d. Remove inline code quality duplication:**
- artisan.md (was quiet-task): remove "Code Quality" section (docstrings, comments, banners, abstractions, guards, fields, requirements — 8 bullets) — now injected via project-conventions skill

**2e. Cleanup:**
- Remove `deslop.md` from CLAUDE.md @-references
- Delete `agent-core/fragments/deslop.md`
- Update remaining "deslop" references: agent-core/README.md, memory-index SKILL.md, agents/memory-index.md, agents/decisions/operational-practices.md, agents/session.md (pushback-task.md already deleted in Phase 1c)

### Phase 3: Code Density Decisions (FR-2) — inline

**3a. Add 5 entries to `agents/decisions/cli.md`:**
- Each entry: general principle first, project instance second (per /ground framing rule)
- Content from `plans/reports/code-density-grounding.md`

**3b. Add /when triggers to memory-index.md:**
- 5 new triggers under `agents/decisions/cli.md` section

## Open Questions

None — all decisions resolved.
