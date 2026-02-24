---
name: recall-tool-anchoring
model: sonnet
---

# Recall Tool Anchoring

**Context:** Tool-anchor 31 recall gates across 13 files. Convert prose-only gates to D+B hybrid pattern (open with tool call), backed by 3 prototype shell scripts and a PreToolUse hook.
**Design:** `plans/recall-tool-anchoring/outline.md`
**Status:** Ready
**Created:** 2026-02-24

---

## Weak Orchestrator Metadata

**Total Steps:** 7 (3 general + 2 inline + 2 general)

**Execution Model:**
- Steps 1.1–1.3: Sonnet (prototype shell scripts)
- Phase 2: Inline — orchestrator-direct (format conversion)
- Phase 3: Inline — orchestrator-direct, opus (architectural artifacts — skills, agents)
- Steps 4.1–4.2: Sonnet (hook + config)

**Step Dependencies:** Sequential (Phase 1 → Phase 2 → Phase 3 → Phase 4). Phase 1 scripts must exist before Phase 3 references them.

**Error Escalation:**
- Sonnet → User: script fails to parse manifest or call when-resolve.py correctly
- Opus (inline) → User: D+B edit changes gate semantics beyond tool-anchoring

**Report Locations:** `plans/recall-tool-anchoring/reports/`

**Success Criteria:** All 3 scripts executable, recall-artifact in reference manifest format, 8 files have tool-anchored recall gates (Bash call as first instruction), hook fires on Task delegation with missing artifact.

**Prerequisites:**
- `agent-core/bin/when-resolve.py` exists (✓ verified)
- All 8 target skill/agent files exist (✓ verified via Glob)
- Existing PreToolUse hook pattern available as reference (✓ `pretooluse-recipe-redirect.py`)

---

## Common Context

**Design decisions:**
- D-1: Reference manifest over content dump — format forces resolution call
- D-2: Throwaway prototype, not production CLI — shell scripts, no TDD
- D-3: Three scripts: check (exists?), resolve (expand references), diff (what changed?)
- D-5: diff anchors write-side gates — provides data for re-evaluation judgment
- D-6: Injection gates (14) stay prose — can't be tool-anchored without fragile text matching
- D-7: Resolution caching deferred — measure first

**Scope boundaries:**
- IN: 3 scripts, reference manifest format, D+B restructure of 8 files, PreToolUse hook, settings.json
- OUT: claudeutils CLI integration, TDD, `_recall generate`, resolution caching, injection gate validation, changes to prepare-runbook.py or when-resolve.py

**Recall (from artifact):**

Constraint format (sonnet/haiku consumers):
- DO open every recall gate with a Bash tool call — prose-only gates get skipped (D+B Hybrid convention)
- DO keep lightweight recall fallback when artifact absent — memory-index + when-resolve.py
- DO NOT change gate semantics — only add tool-call anchor, preserve existing conditional logic
- DO NOT edit injection gates (14 instances) — stays prose per D-6

Rationale format (opus consumers — Phase 3):
- Execution-mode cognition skips prose gates. Anchoring with Bash call converts "knowledge to remember" into "action to execute." Existing conditionals (if artifact exists → read; if absent → lightweight recall) are preserved — the tool call provides data, judgment remains.
- Hook (Layer 3) reinforces, not contradicts, D+B gates (Layer 1). Hook warns on missing artifact; skill gates handle resolution.
- "Proceed without it" phrasing is an anti-pattern — standardize to "do lightweight recall" across all artifact-absent branches.

**Project Paths:**
- `agent-core/bin/` — prototype scripts destination
- `agent-core/hooks/` — hook script destination
- `agent-core/skills/*/SKILL.md` — skill files (5 targets)
- `agent-core/agents/*.md` — agent files (3 targets)
- `.claude/settings.json` — hook registration and permissions
- `plans/recall-tool-anchoring/recall-artifact.md` — format conversion target

---

### Phase 1: Prototype scripts (type: general, model: sonnet)

## Step 1.1: Write recall-check.sh

**Objective:** Create existence/non-empty validator for recall artifacts.
**Script Evaluation:** Small (≤25 lines inline)
**Execution Model:** Sonnet

**Implementation:**
- File: `agent-core/bin/recall-check.sh`
- Shebang + `set -euo pipefail`
- Accept `<job-name>` argument
- Check `plans/<job-name>/recall-artifact.md` exists and is non-empty
- Exit 0 with no output on success
- Exit 1 with diagnostic on stderr: "recall-artifact.md missing for <job>" or "recall-artifact.md empty for <job>"
- Make executable (`chmod +x`)

**Expected Outcome:** Script validates artifact existence. Used by PreToolUse hook (Phase 4) and available for ad-hoc checks.

**Error Conditions:** Missing argument → usage message to stderr, exit 1.

**Validation:** Run against this plan's artifact (should exit 0). Run against nonexistent job (should exit 1 with diagnostic).

---

## Step 1.2: Write recall-resolve.sh

**Objective:** Create reference manifest resolver — parse manifest, feed triggers to when-resolve.py.
**Script Evaluation:** Small (≤25 lines inline)
**Execution Model:** Sonnet

**Implementation:**
- File: `agent-core/bin/recall-resolve.sh`
- Shebang + `set -euo pipefail`
- Accept `<artifact-path>` argument
- Read file, strip `—` annotations (everything after ` — ` on each line), trim whitespace
- Skip blank lines and comment lines (starting with `#`)
- Collect trigger phrases as arguments to `agent-core/bin/when-resolve.py`
- Pass all triggers in a single invocation: `agent-core/bin/when-resolve.py "when <trigger1>" "how <trigger2>" ...`
- Each manifest line's first word determines prefix: lines starting with `when` or `how` use that prefix as-is; other lines default to `when` prefix
- Output resolved content to stdout

**Expected Outcome:** Manifest references expand to full decision file content via when-resolve.py.

**Error Conditions:**
- Missing/unreadable artifact → stderr diagnostic, exit 1
- when-resolve.py fails → propagate exit code
- Empty manifest (no triggers after parsing) → stderr warning, exit 0

**Validation:** Run against this plan's artifact after Phase 2 conversion. Verify stdout contains resolved decision content.

---

## Step 1.3: Write recall-diff.sh

**Objective:** Show what changed in plan directory since last artifact update.
**Script Evaluation:** Small (≤25 lines inline)
**Execution Model:** Sonnet

**Implementation:**
- File: `agent-core/bin/recall-diff.sh`
- Shebang + `set -euo pipefail`
- Accept `<job-name>` argument
- Find `plans/<job-name>/recall-artifact.md` — if missing, report and exit 1
- Get artifact's last-modified time
- Use `git log --since="<mtime>" --name-only --pretty=format: -- "plans/<job-name>/"` to list files changed since artifact mtime
- Exclude `recall-artifact.md` itself from output
- Output changed file list to stdout (one per line)
- If no changes found, output nothing, exit 0

**Expected Outcome:** Write-side gates use this to see what exploration/discussion changed since last artifact update.

**Error Conditions:**
- Missing argument → usage message, exit 1
- Not in git repo → stderr diagnostic, exit 1
- Artifact missing → stderr diagnostic, exit 1

**Validation:** Run against this plan. After modifying a file in `plans/recall-tool-anchoring/`, re-run — should show the modified file.

---

### Phase 2: Reference manifest conversion (type: inline, model: sonnet)

Convert `plans/recall-tool-anchoring/recall-artifact.md` from content-dump format to reference manifest format.

**Current format:** 16 sections, each with `## Heading`, `**Source:**`, `**Relevance:**`, bullet excerpts.

**Target format:** One line per entry: `<trigger phrase> — <one-line relevance annotation>`. Trigger phrase matches the heading converted to memory-index trigger format (lowercase, activity-at-decision-point). The header line `# Recall Artifact: recall-tool-anchoring` is preserved.

**Conversion mapping** (all 16 entries):
```
how to prevent skill steps from being skipped — core D+B pattern being applied
when designing quality gates — layered enforcement for recall gates
when placing quality gates — ambient rules fail, gate at chokepoint
when splitting validation into mechanical and semantic — script vs agent check separation
when sub-agent rules not injected — correctors need explicit recall
how to recall sub-agent memory — bash transport for when-resolve.py
when choosing script vs agent judgment — recall resolution is non-cognitive
when agent ignores injected directive — positional authority of gates
when hook fragment alignment needed — hook must reinforce D+B gates
when using hooks in subagents — PreToolUse fires in main session only
when embedding knowledge in context — tool anchoring converts knowledge to action
when declaring phase type — inline for prose edits, general for scripts
when selecting model for prose artifact edits — opus for skills/agents
when bootstrapping self-referential improvements — scripts before D+B
when agent context has conflicting signals — Common Context must be phase-neutral
when writing rules for different models — format per consumer tier
```

---

### Phase 3: D+B restructure of recall gates (type: inline, model: opus)

Apply D+B tool-anchoring pattern to recall gates in 8 files. Two sub-patterns based on gate type.

**Read-side pattern** (6 files) — replace prose "Read recall-artifact.md" with:
```
**Recall context:** `Bash: agent-core/bin/recall-resolve.sh plans/<job>/recall-artifact.md`

If recall-resolve.sh succeeds, its output contains resolved decision content — use for review.
If artifact absent or recall-resolve.sh fails: do lightweight recall — Read `memory-index.md` (skip if already in context), identify review-relevant entries, batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`. Proceed with whatever recall yields.
```

**Write-side pattern** (2 files, 3 gates) — open re-evaluation sections with:
```
**Recall diff:** `Bash: agent-core/bin/recall-diff.sh <job-name>`

Review the changed files list. If files changed that affect which recall entries are relevant, update the artifact: add entries surfaced by changes, remove entries that no longer apply. Write updated artifact back.
```

**Variation table with locations:**

| File | Gate section | Pattern | Notes |
|---|---|---|---|
| `agent-core/agents/design-corrector.md` | `### 1.5. Load Recall Context` | read-side | Replace entire section body |
| `agent-core/agents/outline-corrector.md` | `### 2. Load Context` item 4 | read-side | Replace item 4 text |
| `agent-core/agents/runbook-outline-corrector.md` | `### 2. Load Context` item 4 | read-side | Replace item 4 text |
| `agent-core/skills/review-plan/SKILL.md` | Recall Context section (~line 63) | read-side | Replace section body |
| `agent-core/skills/deliverable-review/SKILL.md` | Layer 2 recall (~line 106) | read-side | Replace recall paragraph |
| `agent-core/skills/orchestrate/SKILL.md` | Review recall (~line 174) | read-side | Also fix "proceed without it" → lightweight recall |
| `agent-core/skills/design/SKILL.md` | A.5 re-eval (~line 156), C.1 re-eval (~line 275) | write-side | 2 gates in same file |
| `agent-core/skills/runbook/SKILL.md` | Phase 0.75 re-eval (~line 252) | write-side | 1 gate |

**Constraints:**
- DO NOT change gate semantics — only add tool-call anchor
- DO NOT edit injection gates (14 instances per D-6)
- DO NOT modify recall generation gates (design A.1, runbook Phase 0.5) — these create artifacts, not read them
- Preserve all conditional logic (if present → resolve; if absent → lightweight recall)
- Standardize "proceed without it" → "do lightweight recall" where encountered

---

### Phase 4: PreToolUse hook + config (type: general, model: sonnet)

## Step 4.1: Write pretooluse-recall-check.py

**Objective:** Soft enforcement at Task delegation boundary — warn when recall artifact missing.
**Script Evaluation:** Small (≤25 lines inline)
**Execution Model:** Sonnet

**Implementation:**
- File: `agent-core/hooks/pretooluse-recall-check.py`
- Follow `pretooluse-recipe-redirect.py` pattern: read JSON from stdin, check tool_input, output JSON with additionalContext
- Parse `tool_input.prompt` for `plans/<job>/` path pattern (regex: `plans/([^/]+)/`)
- Extract first match as job name
- Check if `plans/<job>/recall-artifact.md` exists (os.path.exists, not subprocess)
- If missing → output additionalContext: "⚠️ No recall-artifact.md for plans/<job>/. Consider /recall or generating artifact before delegation."
- If present or no plans/ path detected → exit 0 (no output, no interference)
- Shebang: `#!/usr/bin/env python3`

**Expected Outcome:** Task delegations referencing a plan directory get a soft reminder if recall artifact is missing. Does not block.

**Error Conditions:**
- Malformed hook input → exit 0 silently (defensive — hook must not break delegation)
- Multiple plans/ matches → use first match

**Validation:** Test with mock JSON input containing plans/ path and missing artifact. Verify additionalContext in output.

---

## Step 4.2: Update settings.json

**Objective:** Register hook and add script permissions.
**Script Evaluation:** Direct (inline edit)
**Execution Model:** Sonnet

**Implementation:**
Two edits to `.claude/settings.json`:

1. **Permissions:** Add `"Bash(agent-core/bin/recall-*:*)"` to `permissions.allow` array (after the existing `agent-core/bin/` entries).

2. **Hook registration:** Add new entry to `hooks.PreToolUse` array:
```json
{
  "matcher": "Task",
  "hooks": [
    {
      "type": "command",
      "command": "python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/pretooluse-recall-check.py"
    }
  ]
}
```

**Expected Outcome:** `recall-*.sh` scripts callable without permission prompts. Hook fires on every Task tool use.

**Error Conditions:** JSON syntax error → `just precommit` catches it.

**Validation:** `just precommit` passes. Verify JSON is valid.
