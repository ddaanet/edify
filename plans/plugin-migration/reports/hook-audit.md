# Hook Script Audit Report

**Date:** 2026-03-21
**Step:** 2.1 — Audit hook scripts for env var usage

## Summary

Four scripts audited. Two required fixes (hardcoded `agent-core/` path). Two needed no changes. `pretooluse-symlink-redirect.sh` deleted.

---

## Script Findings

### pretooluse-recipe-redirect.py

**Finding:** no-change-needed

**Rationale:** No `$CLAUDE_PROJECT_DIR` usage, no `agent-core/` references, no relative path dependencies. Script reads stdin JSON and matches command patterns — fully stateless with respect to filesystem paths.

---

### pretooluse-recall-check.py

**Finding:** no-change-needed

**Rationale:** Uses `os.path.exists("plans/{job}/recall-artifact.md")` — relative path. This works correctly because hooks execute with cwd = `$CLAUDE_PROJECT_DIR` (the project root). No `agent-core/` references. No changes needed.

---

### sessionstart-health.sh

**Finding:** fix-required — Line 21

**Original:**
```bash
learnings_status=$(python3 "$CLAUDE_PROJECT_DIR/agent-core/bin/learning-ages.py" \
  "$CLAUDE_PROJECT_DIR/agents/learnings.md" --summary 2>/dev/null \
  || echo "⚠️ Learnings status unavailable")
```

**Fixed:**
```bash
learnings_status=$(python3 "$CLAUDE_PLUGIN_ROOT/bin/learning-ages.py" \
  "$CLAUDE_PROJECT_DIR/agents/learnings.md" --summary 2>/dev/null \
  || echo "⚠️ Learnings status unavailable")
```

**Rationale:** `$CLAUDE_PROJECT_DIR/agent-core/` is a hardcoded submodule path. Under plugin context, the script lives in the plugin directory — `$CLAUDE_PLUGIN_ROOT` resolves to the plugin root regardless of installation mode. `$CLAUDE_PROJECT_DIR` is retained for the `agents/learnings.md` argument because that file belongs to the project, not the plugin.

**Fix applied:** Yes.

---

### stop-health-fallback.sh

**Finding:** fix-required — Line 28

**Original:**
```bash
learnings_status=$(python3 "$CLAUDE_PROJECT_DIR/agent-core/bin/learning-ages.py" \
  "$CLAUDE_PROJECT_DIR/agents/learnings.md" --summary 2>/dev/null \
  || echo "⚠️ Learnings status unavailable")
```

**Fixed:**
```bash
learnings_status=$(python3 "$CLAUDE_PLUGIN_ROOT/bin/learning-ages.py" \
  "$CLAUDE_PROJECT_DIR/agents/learnings.md" --summary 2>/dev/null \
  || echo "⚠️ Learnings status unavailable")
```

**Rationale:** Same as `sessionstart-health.sh` — identical line, identical fix. `$CLAUDE_PLUGIN_ROOT/bin/` for the script, `$CLAUDE_PROJECT_DIR` for the project-local data file.

**Fix applied:** Yes.

---

## Deleted Script

**pretooluse-symlink-redirect.sh** — deleted. Purpose eliminated by plugin migration. This script blocked writes to symlinked `.claude/` files and redirected to the `agent-core/` source. Plugin auto-discovery replaces symlinks entirely — no symlinks remain to protect.

---

## Validation

- `grep -r 'agent-core/' agent-core/hooks/*.py agent-core/hooks/*.sh` — no matches
- `ls agent-core/hooks/pretooluse-symlink-redirect.sh` — No such file
