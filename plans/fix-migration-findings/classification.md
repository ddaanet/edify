# Classification: Fix Migration Findings

**Source:** plans/plugin-migration/reports/deliverable-review.md
**Date:** 2026-03-22

## Group A — Inline execution (9 items)

### Critical #1 — FR-5 staleness nag vacuous (sessionstart-health.sh:52-83)
- **Classification:** Defect
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** Yes — logic reorder in bash conditional flow
- **Work type:** Production
- **Artifact destination:** production
- **Fix:** Read .edify.yaml version and compare BEFORE writing. Currently write (line 52-68) precedes compare (line 80-83) — after write, versions always match.

### Critical #2 — portable.just path wrong (update/SKILL.md:53)
- **Classification:** Simple (Defect)
- **Behavioral code check:** No — agentic prose path reference
- **Artifact destination:** agentic-prose
- **Fix:** `$CLAUDE_PLUGIN_ROOT/just/portable.just` → `$CLAUDE_PLUGIN_ROOT/portable.just`

### Minor #4 — EDIFY_VERSION hardcoded (sessionstart-health.sh:22)
- **Classification:** Simple (Defect)
- **Behavioral code check:** Yes — adds logic to bump script
- **Artifact destination:** production
- **Fix:** Add EDIFY_VERSION bump to bump-plugin-version.py or release recipe

### Minor #8 — Excess allowed-tools (init/SKILL.md:4, update/SKILL.md:4)
- **Classification:** Simple
- **Behavioral code check:** No
- **Artifact destination:** agentic-prose
- **Fix:** Remove `Bash(python3:*)` and `Bash(find:*)` from allowed-tools frontmatter

### Minor #9 — Inconsistent bash prefix (hooks.json)
- **Classification:** Simple
- **Behavioral code check:** No
- **Artifact destination:** production (config)
- **Fix:** Standardize to bare invocation (all scripts have shebangs)

### Minor #10 — pip fallback structure (sessionstart-health.sh:33-36)
- **Classification:** Defect
- **Behavioral code check:** Yes — changes install logic path
- **Artifact destination:** production
- **Fix:** Replace `pip install --target $VENV_DIR/lib` with proper venv creation via `python3 -m venv`

### Minor #11 — Error message inaccurate (sessionstart-health.sh:38)
- **Classification:** Simple
- **Behavioral code check:** No
- **Artifact destination:** production
- **Fix:** "uv not found" → "neither uv nor pip found"

### Minor #12 — Template coverage (CLAUDE.template.md)
- **Classification:** Simple
- **Behavioral code check:** No
- **Artifact destination:** agentic-prose
- **Fix:** Add @-references for missing fragments

### Minor #13 — SHA-256 determinism (init/SKILL.md:95-96)
- **Classification:** Simple
- **Behavioral code check:** No
- **Artifact destination:** agentic-prose
- **Fix:** Prescribe `sha256sum` as the single method

## Group B — Separate task (1 item)

### Major #3 — No UPS fallback for setup (hooks.json + sessionstart-health.sh)
- **Classification:** Moderate (Defect)
- **Behavioral code check:** Yes — new script, new hook config entry, refactored control flow
- **Artifact destination:** production
- **Fix:** Extract setup section into shared script, add UPS hook entry, flag-file dedup

## Deferred (pre-rename state)

- Minor #5 — Package name claudeutils vs edify (sessionstart-health.sh:30)
- Minor #6 — Hardcoded agent-core path (check-version-consistency.py:11)
- Minor #7 — Hardcoded agent-core paths (portable.just)
