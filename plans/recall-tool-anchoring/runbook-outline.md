# Runbook Outline: Recall Tool Anchoring

**Design:** `plans/recall-tool-anchoring/outline.md`
**Recall artifact:** `plans/recall-tool-anchoring/recall-artifact.md` (16 entries)

## Requirements Mapping

The outline doesn't use FR-* numbering. Mapping from outline Scope → phases:

| Scope Item | Phase |
|---|---|
| Three prototype scripts (check, resolve, diff) | Phase 1 |
| Reference manifest format for recall-artifact.md | Phase 2 |
| D+B restructure of read-side gates (5 skills + 3 agents) | Phase 3 |
| D+B restructure of write-side gates (design + runbook skills) | Phase 3 |
| PreToolUse hook on Task (soft warning) | Phase 4 |
| Permission and hook registration in settings.json | Phase 4 |

## Expansion Guidance

- Phase 1 scripts are throwaway prototypes (D-2). No TDD, no Click, no module structure. Shell scripts in `agent-core/bin/`.
- Phase 2 format conversion uses this plan's own artifact as guinea pig (outline step 4).
- Phase 3 D+B restructure is the bulk. All files are architectural artifacts → opus model. The pattern is uniform: open each recall gate with a tool call to `recall-resolve.sh` (read-side) or `recall-diff.sh` (write-side). Bootstrap design-corrector first (outline step 5), then apply same pattern to remaining 7+2 files.
- Phase 4 hook follows existing `pretooluse-recipe-redirect.py` pattern. Matcher: `Task`. Detects `plans/<job>` in prompt, checks recall-artifact.md existence, injects warning via additionalContext.
- Self-referential ordering: Phase 1 (scripts) must precede Phase 3 (D+B references scripts). Phase 3 edits pipeline tools used in future runs, not this run — no bootstrapping concern for current session.

---

### Phase 1: Prototype scripts (type: general, model: sonnet)

- Step 1.1: Write `recall-check.sh` — validate `plans/<job>/recall-artifact.md` exists and is non-empty. Exit 0 (exists) / exit 1 + diagnostic (missing/empty). Arguments: `<job-name>`.
- Step 1.2: Write `recall-resolve.sh` — read reference manifest from `<artifact-path>`, strip `—` annotations from each line, collect trigger phrases, feed as arguments to `agent-core/bin/when-resolve.py`. Output resolved content to stdout. Arguments: `<artifact-path>`.
- Step 1.3: Write `recall-diff.sh` — list files changed in `plans/<job>/` since `recall-artifact.md` was last modified. Use `find` mtime comparison or `git log --since` against artifact mtime. Arguments: `<job-name>`.

### Phase 2: Reference manifest conversion (type: inline, model: sonnet)

Convert `plans/recall-tool-anchoring/recall-artifact.md` from content-dump format (16 heading+excerpt sections) to reference manifest format. Each entry becomes one line: `<trigger phrase> — <one-line relevance annotation>`. Preserve entry ordering. The 5 planning-relevant entries added during Phase 0.5 augmentation are included.

Target format (from outline):
```
when designing quality gates — layered enforcement for recall gates
how to prevent skill steps from being skipped — core pattern being applied
when sub-agent rules not injected — correctors need explicit recall
```

### Phase 3: D+B restructure of recall gates (type: inline, model: opus)

Apply D+B pattern to all recall gates identified in the inventory. Two sub-patterns:

**Read-side gates** (6 files) — open with `Bash: agent-core/bin/recall-resolve.sh <artifact-path>`:
- `agent-core/agents/design-corrector.md` — Step 1.5 "Load Recall Context": replace prose Read instruction with Bash call to `recall-resolve.sh`. Keep lightweight recall fallback (memory-index + when-resolve.py) for absent-artifact case.
- `agent-core/agents/outline-corrector.md` — Step 2 item 4 "Recall context": same pattern as design-corrector.
- `agent-core/agents/runbook-outline-corrector.md` — Step 2 item 4 "Recall context": same pattern as design-corrector.
- `agent-core/skills/review-plan/SKILL.md` — "Recall Context" section (line ~63): replace prose Read with Bash call. Keep lightweight fallback.
- `agent-core/skills/deliverable-review/SKILL.md` — Layer 2 recall gate (line ~106): replace prose Read with Bash call. Keep lightweight fallback.
- `agent-core/skills/orchestrate/SKILL.md` — "Review recall" (line ~174): replace prose Read with Bash call. This gate says "proceed without it" for missing artifact — change to "do lightweight recall" per inventory consistency recommendation.

**Write-side gates** (2 files) — open with `Bash: agent-core/bin/recall-diff.sh <job-name>`:
- `agent-core/skills/design/SKILL.md` — Phase A.5 re-evaluation (line ~156) and Phase C.1 re-evaluation (line ~275): open each re-eval section with `recall-diff.sh` call, then use diff output to guide which entries to add/remove.
- `agent-core/skills/runbook/SKILL.md` — Phase 0.75 re-evaluation (line ~252): same pattern as design skill.

**Variation table:**

| File | Gate location | Script | Sub-pattern |
|---|---|---|---|
| design-corrector.md | Step 1.5 | recall-resolve.sh | read-side + lightweight fallback |
| outline-corrector.md | Step 2 item 4 | recall-resolve.sh | read-side + lightweight fallback |
| runbook-outline-corrector.md | Step 2 item 4 | recall-resolve.sh | read-side + lightweight fallback |
| review-plan/SKILL.md | Recall Context section | recall-resolve.sh | read-side + lightweight fallback |
| deliverable-review/SKILL.md | Layer 2 recall gate | recall-resolve.sh | read-side + lightweight fallback |
| orchestrate/SKILL.md | Review recall | recall-resolve.sh | read-side + fix "proceed without" |
| design/SKILL.md | A.5 re-eval, C.1 re-eval | recall-diff.sh | write-side (2 gates) |
| runbook/SKILL.md | Phase 0.75 re-eval | recall-diff.sh | write-side (1 gate) |

### Phase 4: PreToolUse hook + config (type: general, model: sonnet)

- Step 4.1: Write `agent-core/hooks/pretooluse-recall-check.py` — PreToolUse hook on Task matcher. Parse `tool_input.prompt` for `plans/<job>` path pattern. Extract job name. Call `recall-check.sh <job>` (or inline the check). If missing → inject additionalContext warning: "No recall-artifact.md found for plans/<job>. Consider running /recall or generating artifact before delegation." Warning only, not block.
- Step 4.2: Update `.claude/settings.json` — add `"Bash(agent-core/bin/recall-*:*)"` to `permissions.allow`. Add Task matcher entry to `hooks.PreToolUse` array referencing `pretooluse-recall-check.py`.

---

## Key Decisions Reference

- **D-1:** Reference manifest over content dump (outline)
- **D-2:** Throwaway prototype, not production CLI (outline)
- **D-3:** Three scripts: check, resolve, diff (outline)
- **D-5:** diff anchors write-side gates (outline)
- **D-6:** Injection gates (14) stay prose — D+B restructure targets read/write gates only (outline)

## Complexity Per Phase

| Phase | Items | Model | Complexity |
|---|---|---|---|
| 1: Prototype scripts | 3 steps | sonnet | Low — shell scripts, no tests |
| 2: Format conversion | 1 inline | sonnet | Low — mechanical format change |
| 3: D+B restructure | 1 inline (8 files, variation table) | opus | Medium — architectural artifacts, uniform pattern |
| 4: Hook + config | 2 steps | sonnet | Low — follows existing hook pattern |
