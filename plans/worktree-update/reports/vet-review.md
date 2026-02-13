# Vet Review: worktree-update Complete Implementation

**Scope**: Full worktree-update implementation (37 cycles, 7 phases)
**Date**: 2026-02-13T11:30:00
**Mode**: review + fix

## Summary

Reviewed complete worktree implementation covering all commands (new, ls, rm, merge, clean-tree, add-commit), comprehensive test coverage (2854 lines across 12 test files), skill integration, and design adherence. Implementation successfully consolidates worktree functionality from justfile prototype into Python CLI with proper separation of concerns.

All dev checks pass (796/797 tests, 1 xfail). Code quality is high: clear module boundaries, good test coverage, proper error handling.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None found.

### Major Issues

None found.

### Minor Issues

1. **Skill references stale marker convention**
   - Location: .claude/skills/worktree/SKILL.md:62, 66
   - Problem: Skill documentation shows `→ wt/<slug>` marker format but design specifies simpler `→ <slug>` format (without `wt/` prefix per design.md:231-235)
   - Note: Design explicitly states "The slug is the stable key for all operations" and "No need to embed the path in session.md"
   - **Status**: UNFIXABLE — Write tool denied. Manual fix: change `→ wt/<slug>` to `→ <slug>` in lines 62, 66

2. **Missing documentation for --task output format**
   - Location: .claude/skills/worktree/SKILL.md:60
   - Problem: Skill says `new <slug> --session` but design specifies task mode uses `new --task "<name>"` with tab-separated output `<slug>\t<path>`
   - Note: CLI implementation correctly handles both modes; skill documentation incomplete
   - **Status**: UNFIXABLE — Write tool denied. Manual fix: update step 5 to document --task flag and tab-separated output

3. **Redundant slug derivation in skill**
   - Location: .claude/skills/worktree/SKILL.md:32-33
   - Problem: Skill step 2 tells agents to derive slug manually, but `new --task` already does this
   - Note: Mode A should just use `new --task` directly without manual slug derivation (per design.md:208-214)
   - **Status**: UNFIXABLE — Write tool denied. Manual fix: remove steps 2-4, replace with single `new --task` invocation in step 2

4. **Skill temporary file management inconsistent**
   - Location: .claude/skills/worktree/SKILL.md:42-59
   - Problem: Skill has agents write to `tmp/wt-<slug>-session.md` then pass to CLI, but `new --task` generates focused session internally
   - Note: Design shows `new --task` handles focus_session() internally with temp file cleanup (design.md:91-96)
   - **Status**: UNFIXABLE — Write tool denied. Same fix as issue 3

5. **Skill Mode B redundant processing**
   - Location: .claude/skills/worktree/SKILL.md:90
   - Problem: "execute Mode A steps 2-7" when --task mode collapses those steps
   - Note: Should just invoke `new --task` for each task in parallel group
   - **Status**: UNFIXABLE — Write tool denied. Manual fix: simplify step 4 to loop over `new --task` invocations

## Fixes Applied

None. Write tool access denied. All fixes require manual editing of .claude/skills/worktree/SKILL.md.

**Manual fix summary:**

Mode A should be simplified to:
1. Read `agents/session.md` to locate task name
2. Invoke `claudeutils _worktree new --task "<task name>"` (captures tab-separated `<slug>\t<path>` output)
3. Parse output for slug and path
4. Edit session.md to move task with `→ <slug>` marker (not `→ wt/<slug>`)
5. Output launch command using parsed path

Mode B step 4 should just loop over `new --task` invocations, not "execute Mode A steps 2-7".

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Sibling directory paths | Satisfied | wt_path() in utils.py:6-20, container detection logic |
| Worktree-based submodule | Satisfied | cli.py:201-222 uses git -C agent-core worktree add |
| Sandbox registration | Satisfied | cli.py:85-98 add_sandbox_dir() writes settings.local.json |
| Submodule removal ordering | Satisfied | cli.py:313-329 removes submodule first, then parent |
| Existing branch reuse | Satisfied | cli.py:183-198 checks branch existence, reuses if present |
| Graceful branch deletion | Satisfied | cli.py:357-361 uses -d with fallback warning |
| Focus-session generation | Satisfied | cli.py:64-82 focus_session() with section filtering |
| Task-based mode | Satisfied | cli.py:268-289 --task flag with slug derivation + focused session |
| 4-phase merge ceremony | Satisfied | merge.py:154-290 implements all 4 phases from design |
| Session conflict auto-resolution | Satisfied | merge.py:74-108 extracts new tasks, keeps ours |
| Learnings conflict auto-resolution | Satisfied | merge.py:111-135 appends theirs-only lines |
| Jobs conflict auto-resolution | Satisfied | merge.py:138-151 keeps ours with warning |
| Precommit validation | Satisfied | merge.py:256-282 runs just precommit, handles failures |
| CLI registration | Satisfied | cli.py registered in main src/claudeutils/cli.py:26,148 |

**Gaps**: None. All functional requirements from design satisfied.

---

## Positive Observations

- **Excellent module organization**: Clean separation between cli.py (commands), merge.py (merge phases), utils.py (shared utilities). Each file has single responsibility.

- **Comprehensive test coverage**: 2854 lines across 12 test files covering creation, merging, conflict resolution, validation, submodule handling, and edge cases. Tests are well-structured with proper fixtures.

- **Robust error handling**: Graceful degradation throughout (missing directories, branch-only scenarios, stale registrations). Clear error messages with actionable guidance.

- **_git() helper factorization**: Both cli.py and merge.py use consistent _git() helper reducing subprocess boilerplate. Clean, maintainable pattern.

- **Design adherence**: Implementation matches design spec closely. All 4 merge phases implemented correctly, conflict resolution strategies match spec, path computation logic matches design.

- **Test quality**: Tests verify behavior not just structure. Integration tests use real git repos, test merge conflicts with actual git operations, validate submodule interactions.

- **Focused session implementation**: focus_session() properly extracts task with relevant sections (Blockers/Gotchas, Reference Files) filtered by task name and plan directory.

- **Task mode ergonomics**: Single `new --task` command handles slug derivation, focused session generation, and worktree creation. Tab-separated output enables skill parsing.

## Recommendations

Manual update needed for .claude/skills/worktree/SKILL.md to align with --task mode implementation. Implementation code is complete and production-ready. Skill documentation needs simplification to match actual CLI behavior.
