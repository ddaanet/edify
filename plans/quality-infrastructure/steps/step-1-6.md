# Step 1.6

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.6: Sync symlinks and verify

**Objective**: Remove stale symlinks, regenerate correct ones, final verification grep.

**Execution Model**: Haiku

**Implementation**:

1. Remove stale symlinks in .claude/agents/ pointing to old names (now non-existent targets):
   - vet-fix-agent.md, design-vet-agent.md, outline-review-agent.md, runbook-outline-review-agent.md, plan-reviewer.md, review-tdd-process.md
   - quiet-task.md, quiet-explore.md, tdd-task.md, runbook-simplification-agent.md, test-hooks.md
   - Note: vet-agent.md symlink if present (source file deleted in 1.1)

2. Remove stale symlink in .claude/skills/:
   - vet → (old target, now renamed to review)

3. Run: `cd agent-core && just sync-to-parent` to regenerate all symlinks from agent-core/ to .claude/.

4. Verify new symlinks exist and resolve:
   - .claude/agents/ should contain symlinks: corrector.md, design-corrector.md, outline-corrector.md, runbook-outline-corrector.md, runbook-corrector.md, tdd-auditor.md, artisan.md, scout.md, test-driver.md, runbook-simplifier.md, hooks-tester.md (plus unchanged: refactor.md, brainstorm-name.md, remember-task.md, memory-refactor.md, hook-batch-task.md)
   - .claude/skills/ should contain review/ (not vet/)

5. Final verification — grep for ALL old names across production directories:
   ```
   grep -rl "vet-fix-agent\|design-vet-agent\|outline-review-agent\|runbook-outline-review-agent\|plan-reviewer\|review-tdd-process\|quiet-task\|quiet-explore\|tdd-task\|runbook-simplification-agent\|test-hooks\|vet-agent\|vet-taxonomy\|vet-requirement" --include="*.md" --include="*.py" --include="*.json" agent-core/ agents/decisions/ agents/memory-index.md agents/session.md agents/learnings.md .claude/ CLAUDE.md
   ```
   Expected: zero files. If any found: list them and STOP.

**Expected Outcome**: All symlinks valid, pointing to renamed files. Zero stale references in production files.

**Error Conditions**:
- sync-to-parent fails → STOP, examine justfile and error output
- Stale references found → List files and STOP for manual review
- Broken symlinks remain → STOP, check agent-core paths match .claude targets

**Validation**: `find .claude/agents/ -type l -exec test ! -e {} \; -print` returns nothing (no broken symlinks). `find .claude/skills/ -type l -exec test ! -e {} \; -print` returns nothing. Final grep returns zero hits.

---

### Light Checkpoint: Phase 1 Complete

1. **Fix**: Run `just dev` from project root. If any checks fail, diagnose and fix. Commit when passing.
2. **Functional**: Verify renames are real (files exist at new paths, content is updated) — not just filesystem moves with stale content.
3. **Commit**: `git add -A && git commit` with rename summary.
4. **Session restart required** — agent definitions load at session start. New session must use new agent names.

---


**2a. Merge prose deslop rules into communication.md:**
- Read agent-core/fragments/deslop.md — extract the 5 prose rules (### Prose section):
  1. State information directly — no hedging, framing, or preamble
  2. Answer immediately — skip acknowledgments and transitions
  3. Reference, never recap — assume the reader has context
  4. Let results speak — no framing around output that's already visible
  5. Commit to your answer — no hedging qualifiers after delivering it
- Add as new subsection `### Prose Quality` in agent-core/fragments/communication.md after the existing 5 numbered rules
- Rules only — strip all ❌/✅ examples (ambient context must be lean)
- Discard principle line ("Slop is the gap between what's expressed and what needed expressing. Deslopping is precision — cutting to the signal, not to the bone.")

**2b. Update project-conventions skill:**
- Read agent-core/skills/project-conventions/SKILL.md
- Remove prose deslop section if present (content now in communication.md, which is ambient/always-loaded)
- Add missing code rule: "Expose fields directly until access control needed" (from deslop.md line 40-42, missing from project-conventions)
- Keep: code quality section, token economy rules, tmp directory rules

**2c. Add skills: frontmatter to code-producing agents:**
- Read agent-core/agents/artisan.md: add `skills: ["project-conventions"]` to YAML frontmatter (or append to existing skills list)
- Read agent-core/agents/test-driver.md: add `skills: ["project-conventions"]` to YAML frontmatter (or append to existing skills list)

**2d. Remove inline code quality duplication from artisan:**
- Read agent-core/agents/artisan.md — find the "Code Quality" section containing rules about docstrings, comments, banners, abstractions, guards, fields, requirements
- Remove the entire "Code Quality" section — this content is now injected via the project-conventions skill added in 2c

**2e. Cleanup — remove deslop.md and stale references:**
- Edit CLAUDE.md: remove the `@agent-core/fragments/deslop.md` line
- `git rm agent-core/fragments/deslop.md`
- Update remaining "deslop" references (update terminology or remove as context dictates):
  - agent-core/README.md — update fragment inventory (remove deslop.md entry)
  - agent-core/skills/memory-index/SKILL.md — update if references deslop fragment
  - agents/memory-index.md — update /when triggers if referencing deslop
  - agents/decisions/operational-practices.md — update deslop references to point to communication.md and project-conventions
  - agents/session.md — update or remove deslop task references (historical context may be kept but updated)

---


**3a. Add 5 entries to agents/decisions/cli.md:**
- Read plans/reports/code-density-grounding.md for grounded content
- Each entry: general principle first, project instance second (per /ground framing rule)
- Add under appropriate section in cli.md (create new section if needed):

  1. **When Checking Expected State** — Decision: Boolean returns for normal program states, not exceptions. Project: `_git_ok(*args) -> bool` for exit-code checks.
  2. **When Terminating On Error** — Decision: Consolidate display and exit into single call. Project: `_fail(msg, code=1) -> Never`.
  3. **When Formatter Expands Code** — Decision: 5+ lines after opinionated formatting signals abstraction need. Extract helper with default kwargs.
  4. **When Choosing Exception Type** — Decision: Custom exception classes for exceptional events, not ValueError. Lint satisfaction via proper design (custom class), not circumvention (intermediate variable).
  5. **When Structuring Error Handling** — Decision: Context collection at failure site, display at top level. Layers don't overlap.

**3b. Add /when triggers to agents/memory-index.md:**
- Read agents/memory-index.md to match existing trigger format
- Add 5 new triggers under the `agents/decisions/cli.md` section:
  - When checking expected state → `.When Checking Expected State`
  - When terminating on error → `.When Terminating On Error`
  - When formatter expands code → `.When Formatter Expands Code`
  - When choosing exception type → `.When Choosing Exception Type`
  - When structuring error handling → `.When Structuring Error Handling`

---

### Full Checkpoint: All Phases Complete

1. **Fix**: Run `just dev`. Diagnose and fix any failures. Commit.
2. **Vet**: Delegate to corrector (formerly vet-fix-agent) for accumulated changes review. Scope IN: all 3 FRs. Scope OUT: FR-4 codebase sweep, context optimization, prepare-runbook.py updates. Apply all fixes. Commit.
3. **Functional**: Verify:
   - Grep for old names in production files returns zero hits
   - communication.md has 5 new prose rules
   - project-conventions has "Expose fields directly" rule
   - artisan.md and test-driver.md have `skills: ["project-conventions"]`
   - artisan.md has no "Code Quality" section
   - deslop.md deleted, CLAUDE.md @-reference removed
   - cli.md has 5 new decision entries
   - memory-index.md has 5 new /when triggers
