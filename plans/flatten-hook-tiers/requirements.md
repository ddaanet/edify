# Flatten Hook Tiers

## Requirements

### Functional Requirements

**FR-1: Parallel feature detection (no early returns)**
Remove all early-return statements from `main()`. All feature detectors — commands, directives, pattern guards, continuations — run independently on every prompt. Each appends to shared `context_parts`/`system_parts` accumulation lists. Single output assembly at end.

Acceptance criteria:
- A prompt containing a command AND a directive produces output from both
- A prompt containing a directive AND a continuation produces output from both (currently blocked by directive early return at line 953)
- A prompt matching a pattern guard AND a continuation produces output from both (currently works, must not regress)

**FR-2: Commands accumulate with other features**
When a command keyword appears on its own line in a multi-line prompt, the command expansion joins the output alongside any other features that match. Single-line command prompts preserve current behavior (systemMessage + additionalContext).

Acceptance criteria:
- `"s\nd: discuss something"` → output includes both status expansion and discuss expansion in additionalContext
- `"s"` (single-line) → identical output to current behavior (systemMessage + additionalContext)
- `"x\nsome context"` (command + plain text, no other feature match) → output includes command expansion only, no systemMessage (same as current multi-line command behavior)

**FR-3: First command wins with multi-command warning**
When multiple command keywords appear on separate lines, only the first fires. Remaining lines continue through all other feature detectors. A warning surfaces in systemMessage so the user sees the silent drop rather than wondering why the second command was ignored.

Acceptance criteria:
- `"s\nx"` → only status expansion in output, not execute
- `"x\ns"` → only execute expansion in output, not status
- `"s\nx"` → systemMessage includes warning noting both commands were detected and which was used (e.g., `"Multiple commands (s, x) — using first"`)
- Single-command prompts produce no warning

**FR-4: Directive + continuation co-firing**
Directives no longer block continuation parsing. A prompt with a directive prefix and multi-skill references produces both directive expansion and continuation chain context.

Acceptance criteria:
- `"p: new task\n/skill1 args and /skill2"` (with cooperative registry mock) → output includes both pending expansion and CONTINUATION-PASSING context

**FR-5: Unified output assembly**
Single output point at end of `main()`. No mid-function `print(json.dumps(output)); return` statements (except early exit when no features match → `sys.exit(0)`).

Acceptance criteria:
- Assembly: `additionalContext = "\n\n".join(context_parts)`, `systemMessage = " | ".join(system_parts)`
- Empty context_parts → silent pass-through (exit 0)
- Format identical to current: `hookSpecificOutput.hookEventName`, `hookSpecificOutput.additionalContext`, optional `systemMessage`

**FR-6: Characterization tests (pre-refactor)**
Integration tests that lock current behavior for every existing feature in isolation, run before any refactoring begins. Serve as regression guard.

Acceptance criteria:
- Each command (s, x, xc, r, h, hc, ci, c, y, ?) output locked
- Each directive (d, p, b, q, learn) output locked
- Each pattern guard (edit-skill, edit-slash, CCG) output locked
- Continuation parsing output locked (multi-skill chain)
- No-match pass-through locked
- All tests pass on current code before refactor begins

**FR-7: Feature combination integration tests (post-refactor)**
Tests for pairwise and meaningful triple feature combinations enabled by the flattened architecture.

Acceptance criteria:
- Command + directive combination (new behavior)
- Command + pattern guard combination (new behavior)
- Command + continuation combination (new behavior)
- Directive + continuation combination (new behavior, was blocked)
- Command + directive + pattern guard (new behavior)
- Each test verifies both additionalContext content and systemMessage content

### Constraints

**C-1: Hook timeout budget**
All features must complete within the 5s shared hook timeout. No performance regression from refactor. The refactor changes control flow (remove early returns), not algorithmic complexity.

**C-2: Output format stability**
`hookSpecificOutput.additionalContext` and `systemMessage` JSON structure must remain compatible with Claude Code's hook processing. The systemMessage format is a scraping contract for calibration (per UPS outline D-10).

**C-3: Single-feature backward compatibility**
Prompts triggering exactly one feature must produce identical output to current behavior. The refactor changes multi-feature interaction, not single-feature semantics. Verified by FR-6 characterization tests.

### Out of Scope

- Topic injection integration — dependent task, integrates into the flattened architecture after this completes
- New feature detectors — only restructure existing features (commands, directives, pattern guards, continuations)
- Token counting infrastructure — deferred per UPS outline
- Continuation registry cache migration to `tmp/` — separate pending task
- systemMessage format redesign — format stays as-is, just accumulated from all features
- Command matching on partial lines — commands still require own line (`stripped in COMMANDS`)

### Dependencies

- None — this IS the prerequisite for UPS topic injection

### References

- `plans/userpromptsubmit-topic/outline.md` — prerequisite section describing target architecture
- `agents/decisions/hook-patterns.md` — hook output channels, tier injection patterns
- `agents/decisions/workflow-execution.md` — hook-based parsing decision (deterministic vs fragment)
- `plans/flatten-hook-tiers/recall-artifact.md` — recall entries for this job

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (hook restructuring is the core of this work)
