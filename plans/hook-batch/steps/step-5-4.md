# Step 5.4

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Step 5.4: Run sync-to-parent + Verify

**Objective:** Execute `just sync-to-parent` to deploy hooks, verify settings.json updated correctly, note restart requirement.

**Script Evaluation:** Direct — verification commands only.

**Execution Model:** Haiku

**Note:** This step requires `dangerouslyDisableSandbox: true` because sync-hooks-config.py writes `.claude/settings.json` (in `denyWithinAllow`).

**Prerequisite:**
- Steps 5.1-5.3 complete
- Clean working tree preferred (sync produces only settings.json changes)

**Implementation:**

```bash
# Run sync-to-parent (requires dangerouslyDisableSandbox for settings.json write)
just sync-to-parent
```

Then verify:
```bash
# Verify all new hook events present
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
hooks = d.get("hooks", {})
print("Events:", list(hooks.keys()))
'
# Expected output includes: SessionStart, Stop, and existing UserPromptSubmit, PreToolUse, PostToolUse

# Verify PreToolUse Bash has both submodule-safety AND recipe-redirect
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
bash_hooks = [e for e in d["hooks"].get("PreToolUse", []) if e.get("matcher") == "Bash"]
if bash_hooks:
    cmds = [h["command"] for h in bash_hooks[0]["hooks"]]
    print("Bash hooks:", cmds)
'
# Expected: both submodule-safety.py and pretooluse-recipe-redirect.py

# Verify existing Write|Edit PreToolUse hooks preserved (block-tmp, symlink-redirect)
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
we_hooks = [e for e in d["hooks"].get("PreToolUse", []) if e.get("matcher") == "Write|Edit"]
if we_hooks:
    cmds = [h["command"] for h in we_hooks[0]["hooks"]]
    print("Write|Edit hooks:", cmds)
'
# Expected: pretooluse-block-tmp.sh and pretooluse-symlink-redirect.sh still present

# Verify PostToolUse Bash (submodule-safety) preserved AND Write|Edit (autoformat) added
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
ptu = d["hooks"].get("PostToolUse", [])
bash_hooks = [e for e in ptu if e.get("matcher") == "Bash"]
we_hooks = [e for e in ptu if e.get("matcher") == "Write|Edit"]
print("PostToolUse Bash hooks:", [h["command"] for h in bash_hooks[0]["hooks"]] if bash_hooks else "MISSING")
print("PostToolUse Write|Edit hooks:", [h["command"] for h in we_hooks[0]["hooks"]] if we_hooks else "MISSING")
'
# Expected: Bash has submodule-safety.py; Write|Edit has posttooluse-autoformat.sh

# Verify UserPromptSubmit not duplicated
python3 -c '
import json
d = json.load(open(".claude/settings.json"))
ups = d["hooks"].get("UserPromptSubmit", [])
all_cmds = [h["command"] for entry in ups for h in entry["hooks"]]
print("UPS commands:", all_cmds)
print("Duplicate?:", len(all_cmds) != len(set(all_cmds)))
'
# Expected: one UPS command, no duplicate
```

**Expected Outcome:** settings.json updated with 5 new/merged hook entries. All existing hooks preserved. No duplicates.

**Post-run note:** Session restart required. Hook scripts are discovered at session start. Note in commit message: "Restart session after deploying to activate new hooks."

**Error Conditions:**
- `just sync-to-parent` fails → check sync-hooks-config.py error output; verify dangerouslyDisableSandbox is set
- Settings verification fails (missing keys) → run sync-hooks-config.py directly with debug output
- Duplicate UPS command detected → investigate dedup logic in sync-hooks-config.py

---


**Success criteria:**
- `agent-core/hooks/hooks.json` valid JSON with 5 event entries
- `agent-core/bin/sync-hooks-config.py` idempotent, handles all merge cases
- `agent-core/justfile` sync-to-parent calls sync-hooks-config.py
- `.claude/settings.json` has all new hooks merged (verified above)
- All existing hooks preserved: UPS, PreToolUse Write|Edit (block-tmp + symlink-redirect), PostToolUse Bash (submodule-safety)
- `pytest tests/ -v` → all tests pass

**Restart required:** Session restart activates new hooks (agents are discovered at session start).

**Depends on:** All phases 1-4 must be complete before Step 5.4 (sync deploys all scripts).
