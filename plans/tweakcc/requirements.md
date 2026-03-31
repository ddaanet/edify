# tweakcc Integration Requirements

## Problem

Claude Code loads ~3720 tokens of builtin system/tool prompts that overlap with or contradict project CLAUDE.md fragments. These tokens load every session regardless of project configuration. No official override mechanism exists.

## Goal

Drive tweakcc from edify to customize project-local Claude Code instances. Two phases:

**Phase 1 (stopgap):** Remove redundant builtin system prompts via tweakcc patches. Fragments stay in CLAUDE.md for clean environment compatibility.

**Phase 2 (end state):** Full customization of system prompt (most of CLAUDE.md content) and tool prompts via tweakcc. CLAUDE.md/fragments are the authoring format; tweakcc patches are the delivery format.

## Constraints

- Fragments MUST remain in CLAUDE.md — required for unpatched/clean environments
- Claude Code installed as npm local dependency (not native binary) for direct JS patching
- Patch scripts version-controlled in repo, patched output is not
- Patches reapplied automatically after `npm install` (postinstall hook)
- edify drives the workflow (just recipes, not manual tweakcc CLI)

## Functional Requirements

### FR-1: Project-local Claude installation

Install `@anthropic-ai/claude-code` as npm devDependency with pinned version. Provides JS-based Claude that tweakcc can patch directly (no binary unpack/repack).

### FR-2: tweakcc patch infrastructure

Project-local patch scripts using tweakcc programmatic API. Target: `node_modules/@anthropic-ai/claude-code/cli.js`. Patches stored in `plans/tweakcc/patches/` or similar version-controlled location.

### FR-3: Phase 1 — Remove redundant builtins

Override these builtin prompts with empty/minimal replacements:

| Builtin file | Tokens | Action |
|---|---|---|
| `tool-description-bash-git-commit-and-pr-creation-instructions.md` | 1731 | Empty — `/commit` skill owns commit behavior |
| `tool-description-bash-sandbox-note.md` | 513 | Replace — remove "NEVER set dangerouslyDisableSandbox" noise, keep failure analysis guidance |
| `system-prompt-scratchpad-directory.md` | 230 | Empty — contradicts project `tmp/` rule |
| `tool-description-bash.md` "Avoid using Bash with..." section | ~150 | Remove section — hook enforcement replaces this |

Token counts measured via `edify tokens sonnet` against `~/.tweakcc/system-prompts/` files.

### FR-4: Automatic patch application

`npm install` triggers postinstall hook that reapplies patches. Idempotent — safe to run multiple times. Detects if patches already applied to avoid unnecessary writes.

### FR-5: Just recipe launcher

`just claude` launches the patched local Claude instance. Verifies patches are applied before launch.

### FR-6: Phase 2 — Custom system and tool prompts

Extend patch infrastructure to inject custom content into system prompt and tool descriptions. Source material: CLAUDE.md fragments compiled into tweakcc patches.

## Non-Requirements

- Patching native binary (npm JS-only approach)
- Per-project tweakcc config directory (use programmatic API instead)
- Removing CLAUDE.md fragments (kept for clean environments)
- Auto-updating Claude Code version (pinned in package.json)

## Research

- `plans/tweakcc/research.md` — tweakcc mechanics, patch survival, config structure
- `plans/tweakcc/local-instances.md` — npm local install, programmatic API, integration patterns
- `plans/feature-requests/fragment-redundancy-analysis.md` — fragment vs builtin overlap analysis

## Open Questions

- Should Phase 2 compile fragments into patches at build time or maintain separate patch content?
- How to handle tweakcc version compatibility across Claude Code updates?
- Validation: how to verify patches applied correctly (diff check, token count, runtime test)?
