# Planstate Brief Inference

Fix planstate to infer correct next-action for brief-only plans.

## Requirements

### Functional Requirements

**FR-1: Detect brief-only plan state**
When a plan directory contains only `brief.md` (no `requirements.md`, no `outline.md`, no `design.md`), planstate should report status `briefed` and emit next-action `/design plans/<name>/brief.md`.
- Acceptance: `plans/foo/` contains only `brief.md` → `claudeutils _worktree ls` shows `[briefed] → /design plans/foo/brief.md`
- Acceptance: `plans/foo/` contains `brief.md` + `requirements.md` → status based on requirements.md (brief doesn't override)

### Constraints

**C-1: Existing planstate logic**
Fix is in `src/claudeutils/validation/planstate.py`. Brief-only is a new state in the inference chain, inserted before the requirements.md fallback.

### Out of Scope

- Plans with `brief.md` alongside other artifacts (brief is supplementary context, not a state indicator, when other files exist)
