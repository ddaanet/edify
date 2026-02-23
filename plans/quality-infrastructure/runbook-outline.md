# Runbook Outline: Quality Infrastructure Reform

**Design:** plans/quality-infrastructure/outline.md (design-as-outline)
**Requirements:** plans/quality-infrastructure/requirements.md

## Requirements Mapping

| Requirement | Phase | Steps/Items | Notes |
|-------------|-------|-------------|-------|
| FR-3a: review/correct renames | 1 | 1.1, 1.2, 1.4 | 6 renames + 1 embed + 1 deprecation |
| FR-3b: execution renames | 1 | 1.1, 1.4 | 5 renames |
| FR-3c: plan-specific deletions | 1 | 1.3 | 8 .claude/agents/ files |
| FR-3: skill + fragment renames | 1 | 1.5 | vet→review dir, vet-requirement→review-requirement |
| FR-3: terminology propagation | 1 | 1.6 | ~30 files, substitution table |
| FR-3: symlink sync + verification | 1 | 1.7 | Stale removal, sync, grep |
| FR-1: prose rules → communication.md | 2 | inline | 5 rules merged |
| FR-1: code rules → project-conventions | 2 | inline | Missing rule added, skill frontmatter |
| FR-1: deslop.md removal | 2 | inline | CLAUDE.md ref, file delete, stale refs |
| FR-2: code density entries | 3 | inline | 5 entries in cli.md |
| FR-2: memory-index triggers | 3 | inline | 5 /when triggers |

## Phase Structure

### Phase 1: Agent Rename (type: general)

**Objective:** Rename 11 agent files, embed taxonomy, delete deprecated agents and plan-specific detritus, propagate all name changes across codebase, regenerate symlinks.
**Complexity:** High (~43 files touched, cross-codebase coordination)
**Checkpoint:** full

- Step 1.1: Batch rename agent definition files
  - git mv 11 files in agent-core/agents/:
    - vet-fix-agent.md → corrector.md
    - design-vet-agent.md → design-corrector.md
    - outline-review-agent.md → outline-corrector.md
    - runbook-outline-review-agent.md → runbook-outline-corrector.md
    - plan-reviewer.md → runbook-corrector.md
    - review-tdd-process.md → tdd-auditor.md
    - quiet-task.md → artisan.md
    - quiet-explore.md → scout.md
    - tdd-task.md → test-driver.md
    - runbook-simplification-agent.md → runbook-simplifier.md
    - test-hooks.md → hooks-tester.md
  - Requires `dangerouslyDisableSandbox: true` (git mv writes .git tracking)
  - Commit all renames atomically
  - Model: haiku

- Step 1.2: Embed vet-taxonomy and delete deprecated agents
  - Depends on: Step 1.1 (corrector.md must exist after rename)
  - Read agent-core/agents/vet-taxonomy.md (62 lines: status table, subcategory codes, investigation format, deferred items template)
  - Insert full taxonomy content into corrector.md after the role description section, before any existing status taxonomy reference. Preserve all tables and examples.
  - Delete agent-core/agents/vet-taxonomy.md
  - Delete agent-core/agents/vet-agent.md (deprecated per D-1: zero active call sites, confirmed by reports/explore-reviewer-usage.md)
  - Commit changes
  - Model: sonnet (mechanical content insertion + file deletion)

- Step 1.3: Delete plan-specific agent detritus
  - Delete 8 standalone files in .claude/agents/:
    - error-handling-task.md, pushback-task.md, runbook-quality-gates-task.md, when-recall-task.md
    - workflow-rca-fixes-task.md, worktree-merge-data-loss-task.md, worktree-merge-resilience-task.md, workwoods-task.md
  - These are generated artifacts from past prepare-runbook.py runs, not symlinks
  - Do NOT delete: hb-p*.md, quality-infrastructure-task.md, runbook-generation-fixes-task.md (active plans)
  - Commit changes
  - Model: haiku

- Step 1.4: Update renamed agent internals
  - Depends on: Step 1.1 (all 11 renamed files must exist at new paths)
  - Update `name:` YAML frontmatter in all 11 renamed agents to match new filename (without .md)
  - Update cross-references between agents per substitution table:
    - tdd-auditor.md: vet-fix-agent → corrector
    - runbook-corrector.md: vet-fix-agent → corrector
    - runbook-outline-corrector.md: vet-fix-agent → corrector
    - outline-corrector.md: vet-fix-agent → corrector
  - Update `skills:` frontmatter lists if any reference old agent names
  - Grep each renamed file for any remaining old names from substitution table
  - Commit changes
  - Model: sonnet (mechanical YAML frontmatter + grep-and-replace substitutions)

- Step 1.5: Rename skill directory and fragment file
  - Depends on: Step 1.1 (new agent names in substitution table must exist)
  - git mv agent-core/skills/vet/ → agent-core/skills/review/
  - git mv agent-core/fragments/vet-requirement.md → agent-core/fragments/review-requirement.md
  - Update review/SKILL.md: all vet→review terminology, agent name references per substitution table
  - Update review-requirement.md: agent name references per substitution table (vet-fix-agent→corrector, design-vet-agent→design-corrector, etc.), vet→review terminology
  - Requires `dangerouslyDisableSandbox: true`
  - Commit changes
  - Model: opus (skill + fragment prose)

- Step 1.6: Propagate name changes across codebase
  - Depends on: Steps 1.1, 1.2, 1.4, 1.5 (all renames, embeds, and internal updates complete)
  - Apply full substitution table across all files below. For each file: Read, apply all applicable substitutions (agent names + terminology), Edit.
  - **Skills** (11 files):
    - agent-core/skills/commit/SKILL.md — vet-requirement → review-requirement
    - agent-core/skills/design/SKILL.md — design-vet-agent → design-corrector
    - agent-core/skills/deliverable-review/SKILL.md — vet-fix-agent → corrector
    - agent-core/skills/orchestrate/SKILL.md — vet terminology, agent names
    - agent-core/skills/doc-writing/SKILL.md — vet references
    - agent-core/skills/plugin-dev-validation/SKILL.md — vet references
    - agent-core/skills/runbook/SKILL.md — runbook-outline-review-agent, plan-reviewer, runbook-simplification-agent, vet-fix-agent
    - agent-core/skills/runbook/references/examples.md — vet delegation examples
    - agent-core/skills/runbook/references/general-patterns.md — vet patterns
    - agent-core/skills/remember/SKILL.md — /vet reference
    - agent-core/skills/memory-index/SKILL.md — vet-fix-agent reference
  - **Decision files** (9 files):
    - agents/decisions/pipeline-contracts.md — vet-fix-agent routing, reviewer table
    - agents/decisions/operational-practices.md — vet delegation learnings
    - agents/decisions/workflow-optimization.md — design-vet-agent, vet context reuse
    - agents/decisions/project-config.md — agent composition references
    - agents/decisions/orchestration-execution.md — vet delegation patterns
    - agents/decisions/workflow-planning.md — vet-fix-agent, vet-agent, design-vet-agent references
    - agents/decisions/workflow-core.md — /vet skill reference, vetting terminology
    - agents/decisions/deliverable-review.md — vet-fix-agent routing reference
    - agents/decisions/prompt-structure-research.md — vet-requirement reference
  - **Docs** (2 files):
    - agent-core/docs/tdd-workflow.md
    - agent-core/docs/general-workflow.md
  - **Other agent-core** (2 files):
    - agent-core/README.md — agent inventory
    - agent-core/bin/focus-session.py — agent references
  - **Project root** (5 files):
    - CLAUDE.md — @vet-requirement → @review-requirement, any vet-fix-agent references
    - agents/memory-index.md — vet-related /when triggers and agent name references
    - agents/session.md — task descriptions referencing old names
    - agents/learnings.md — vet-related learning descriptions
    - .claude/rules/plugin-dev-validation.md — vet → review references
  - Commit all changes atomically
  - Model: opus (architectural artifact prose)

- Step 1.7: Symlink sync, stale removal, and verification
  - Depends on: Steps 1.1-1.6 (all renames and propagation complete before verification)
  - Find and remove dangling symlinks in .claude/agents/ and .claude/skills/ (old-name targets gone after git mv)
  - Run `just sync-to-parent` to regenerate correct symlinks
  - Grep entire codebase for all old names from substitution table to catch stragglers (check: vet-fix-agent, quiet-task, tdd-task, plan-reviewer, design-vet-agent, outline-review-agent, runbook-outline-review-agent, review-tdd-process, quiet-explore, runbook-simplification-agent, test-hooks, vet-agent, vet-taxonomy, vet-requirement, /vet)
  - Fix any stragglers found
  - Commit if changes made
  - Model: haiku

### Phase 2: Deslop Restructuring (type: inline)

**Objective:** Split deslop.md content: prose rules → communication.md (ambient), code rules stay in project-conventions. Delete deslop.md.
**Complexity:** Low (additive prose edits, all decisions pre-resolved)

- Merge 5 prose deslop rules into agent-core/fragments/communication.md as new subsection after existing rules. Rules only — strip ❌/✅ examples to keep ambient context lean. Discard principle line ("Slop is the gap between what's expressed and what needed expressing. Deslopping is precision — cutting to the signal, not to the bone.").
- Update agent-core/skills/project-conventions/SKILL.md: remove "Prose" subsection under Deslop section (now in communication.md, ambient for all sessions). Add missing code rule to Code subsection: "Expose fields directly until access control needed." Restructure Deslop heading to "Code Quality" or similar since it now contains only code rules.
- Add `skills: ["project-conventions"]` to YAML frontmatter of agent-core/agents/artisan.md (renamed from quiet-task.md in Phase 1) and agent-core/agents/test-driver.md (renamed from tdd-task.md in Phase 1). Code-producing agents currently missing this injection per D-3.
- Remove "Code Quality" section from agent-core/agents/artisan.md (8 bullets: docstrings, comments, banners, abstractions, guards, fields, requirements, deletion test) — now redundant with project-conventions skill injection via `skills:` frontmatter.
- Remove `@agent-core/fragments/deslop.md` line from CLAUDE.md @-references. Delete agent-core/fragments/deslop.md. Update remaining "deslop" references — distinguish fragment references (remove/update) from descriptive uses (keep or update term):
  - agent-core/README.md — update inventory description
  - agent-core/skills/memory-index/SKILL.md — update if references deslop fragment
  - agents/memory-index.md — update deslop-related /when triggers
  - agents/decisions/operational-practices.md — descriptive uses in learning text (update term to "code quality" or "prose quality" as appropriate)
  - agents/session.md — update task descriptions if referencing deslop fragment

### Phase 3: Code Density Decisions (type: inline)

**Objective:** Add 5 grounded code density principles to decision files with memory-index discoverability.
**Complexity:** Low (additive entries, content sourced from plans/reports/code-density-grounding.md)

- Add 5 entries to agents/decisions/cli.md. Each states general principle first, project instance second (per /ground framing rule). Source content from plans/reports/code-density-grounding.md:
  1. Expected state checks return booleans — normal states checked with boolean returns, not exceptions. Project: `_git_ok(*args) -> bool`
  2. Consolidate display and exit — error termination as single call. Project: `_fail(msg, code=1) -> Never`
  3. Formatter expansion signals abstraction need — 5+ lines after formatting = extract helper. Project: default kwargs pattern
  4. Exceptions for exceptional events only — custom exception classes, not ValueError. Project: lint satisfaction via proper design
  5. Error handling layers don't overlap — context at failure site, display at top level. Project: never both
- Add 5 /when triggers to agents/memory-index.md under the `## agents/decisions/cli.md` section. Match existing trigger format (activity at decision point).

## Key Decisions Reference

- D-1: vet-agent deprecated → Phase 1, Step 1.2 (delete)
- D-2: vet-taxonomy embedded in corrector → Phase 1, Step 1.2 (embed)
- D-3: Code deslop via project-conventions skill → Phase 2 (skill update + frontmatter)
- D-4: Prose deslop → communication.md → Phase 2 (merge into ambient)
- D-5: Phase ordering FR-3 → FR-1 → FR-2 → runbook phase structure
- D-6: vet-requirement → review-requirement → Phase 1, Step 1.5 (rename)
- D-7: /vet skill → /review skill → Phase 1, Step 1.5 (directory rename)

## Substitution Table

**Cross-cutting scope:** Agent name substitutions addressed by Steps 1.4 (internals), 1.5 (skill/fragment), 1.6 (codebase propagation), 1.7 (verification). Terminology substitutions addressed by Steps 1.5, 1.6. Deprecation deletions addressed by Steps 1.2, 1.3. Out of scope: prepare-runbook.py crew- prefix generation (future work).

**Agent name renames** (Steps 1.4, 1.5, 1.6):

| Old | New |
|-----|-----|
| vet-fix-agent | corrector |
| design-vet-agent | design-corrector |
| outline-review-agent | outline-corrector |
| runbook-outline-review-agent | runbook-outline-corrector |
| plan-reviewer | runbook-corrector |
| review-tdd-process | tdd-auditor |
| quiet-task | artisan |
| quiet-explore | scout |
| tdd-task | test-driver |
| runbook-simplification-agent | runbook-simplifier |
| test-hooks | hooks-tester |

**Terminology renames** (Steps 1.5, 1.6):

| Old | New |
|-----|-----|
| vet report | review report |
| vet-fix report | correction |
| vetting | review/correction |
| vet-requirement | review-requirement |
| /vet | /review |
| vet/ (skill directory) | review/ |

**Deprecated — delete references:**

| Old | Action |
|-----|--------|
| vet-agent | Delete references (zero call sites per D-1) |
| vet-taxonomy | Delete references (embedded in corrector per D-2) |

## Post-Completion

- **Restart recommended** after all phases complete — agent definitions load at session start. New names won't be available as `subagent_type` values until restart.
- Phases 2-3 (inline) execute in the same orchestration session as Phase 1 since they don't require loaded agent definitions.

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Phase 1 step consolidation candidates:**
- Steps 1.1 and 1.3 are both mechanical file operations (git mv and rm) at haiku tier. Could merge if atomicity isn't required, but separate commits for renames vs deletions is cleaner for git history. Keep separate.
- Steps 1.2 and 1.4 are both post-rename internal updates. 1.2 is embed+delete (content manipulation), 1.4 is frontmatter+cross-refs (mechanical substitution). Different operations on different files -- keep separate.

**Step expansion notes:**
- Step 1.1: Include sandbox note in expansion -- `dangerouslyDisableSandbox: true` required for git mv. Single commit for all 11 renames.
- Step 1.2: Expansion should specify exact insertion point in corrector.md (after role description, before tools/skills sections). Read vet-taxonomy.md content and verify section boundaries before insertion.
- Step 1.5: Two git mv operations plus two file edits. Expansion should note that review/SKILL.md content references the old `/vet` command name -- update trigger phrase, description, and all internal references.
- Step 1.6: Largest step (24 files). Expansion should batch Read calls (parallel reads, sequential edits per file). Note that some files may have multiple substitution targets (e.g., pipeline-contracts.md has both agent name references and terminology references).
- Step 1.7: Grep validation pattern should match the full old-name list from the substitution table. Expansion should include the exact grep command.

**Checkpoint guidance:**
- Phase 1 checkpoint after Step 1.7: Verify zero grep hits for all old names. Verify `just sync-to-parent` succeeds. Verify `just precommit` passes.
- No checkpoint needed between Phases 2-3 (both inline, low complexity, additive).

**Model selection rationale:**
- Steps 1.1, 1.3, 1.7: haiku -- mechanical file operations (git mv, rm, grep verification)
- Steps 1.2, 1.4: sonnet -- content insertion and substitution requiring file comprehension but not architectural judgment
- Step 1.5: opus -- skill SKILL.md and review-requirement.md contain nuanced workflow prose where terminology changes affect meaning
- Step 1.6: opus -- 24 files across architectural artifacts where substitutions interact with contextual meaning (decision files, skill files with workflow descriptions)
- Phases 2-3: inline execution, no separate agent dispatch
