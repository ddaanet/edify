# Step 6.3

**Plan**: `plans/plugin-migration/runbook-phase-6.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Execute after plugin verified working. Irreversible within session.

---

---

## Step 6.3: Validate migration completeness (checkpoint)

**Objective**: Final validation gate before Phase 7 rename. Verify all functional requirements met post-symlink-removal.

**Prerequisites**:
- Steps 6.1, 6.2 complete

**Implementation**:
1. **FR-1**: Plugin auto-discovery works without symlinks (automated via `-p` headless mode):
   ```bash
   claude -p "list your available slash commands" --plugin-dir ./agent-core 2>&1 | tee tmp/migration-verify-skills.txt
   claude -p "list your available agents" --plugin-dir ./agent-core 2>&1 | tee tmp/migration-verify-agents.txt
   ```
   - Skills and agents must appear in output (no symlinks, `--plugin-dir` only)
2. **FR-7**: All functionality preserved
   - `grep -r '@agent-core/' CLAUDE.md agents/ .claude/rules/ | grep -v Binary` — each path must exist: `ls <path>` for each returned reference
   - `grep -rh '^@' agent-core/fragments/ agent-core/skills/ | sort -u` — verify each referenced fragment path exists on disk
3. **FR-9**: All hooks fire from plugin, settings.json hooks section empty
   - Verify hooks.json contains all hooks
   - Verify settings.json has no hooks section
4. **NFR-2**: Validated architecturally — same content loaded via plugin auto-discovery instead of symlinks. No empirical measurement needed.
5. **Run `just precommit`** — full validation gate
   - Must pass completely (lint, format, type check, tests, version consistency)

**Expected Outcome**:
- All FRs verified
- `just precommit` passes
- System fully functional without symlinks

**Error Conditions**:
- If `just precommit` fails → fix issues before proceeding to Phase 7
- If any FR check fails → diagnose and fix or escalate

**Validation**:
- Validation checkpoint — STOP and report results before Phase 7
- All checks must pass before proceeding to directory rename
