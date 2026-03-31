# tweakcc Research Report

Research date: 2026-02-08

## 1. tweakcc Mechanics

### How it works

tweakcc modifies Claude Code installations by patching the compiled JavaScript at the installation level:

**For npm installations:**
- Directly patches the minified `cli.js` file on disk
- Reads configuration from `~/.tweakcc/config.json`
- Applies patches each time Claude Code runs

**For native/binary installations (Apple Silicon, etc.):**
- Uses **node-lief** (Node.js bindings for LIEF binary parser) to extract embedded JavaScript from Mach-O executables
- Applies patches to extracted JavaScript
- Repacks the binary with ad-hoc signing support
- Commands: `npx tweakcc unpack <output-js>` and `npx tweakcc repack <input-js>`

### What prompt strings can it modify

tweakcc can customize:

- **System prompts**: All of Claude Code's system prompts (version-specific, updated within minutes of new CC releases)
- **UI themes**: Custom color schemes via HSL/RGB picker
- **Thinking verbs**: Custom words displayed while processing
- **Spinner animations**: Custom thinking indicators with configurable speeds
- **User messages**: Styling for chat history messages
- **Input box**: Border removal and styling options
- **Model selection**: Subagent model assignment and context limits
- **Table formats**: Unicode, ASCII, or custom formatting
- **Session naming**: `/title` and `/rename` commands

### How it locates Claude Code installation

Installation detection follows a prioritized sequence:

1. `options.path` parameter (if provided to CLI)
2. `TWEAKCC_CC_INSTALLATION_PATH` environment variable
3. `ccInstallationPath` in `~/.tweakcc/config.json`
4. `claude` command in `$PATH`
5. Hard-coded search directories (platform-specific)

Interactive picker (using Ink + React components) displays if multiple installations found.

### Current version and supported Claude Code version

- **tweakcc version**: v3.4.0 (released 2026-01-19)
- **Verified Claude Code version**: 2.1.32
- System prompt patching works across older versions if prompts exist in repository
- Non-system-prompt patches may vary by version

## 2. Project-local Claude Installations

### This project's Claude installation

**Installation type:** Native binary (Mach-O 64-bit executable arm64)

**Location:** `/Users/david/.local/bin/claude` (symlink to `/Users/david/.local/share/claude/versions/2.1.37`)

**Available versions:**
```
/Users/david/.local/share/claude/versions/
├── 2.1.34 (173 MB)
├── 2.1.36 (empty/placeholder)
└── 2.1.37 (173 MB) ← current
```

**Configuration directory:** `~/.claude/` (39 items, 3.6 MB)

Notable subdirectories:
- `.claude/plugins/` - plugin configurations
- `.claude/projects/` - project-specific settings
- `.claude/debug/` - 1412 files
- `.claude/file-history/` - 607 files
- `history.jsonl` - 2.7 MB

### Node.js environment

- **Node version**: v25.4.0 (installed via Homebrew at `/opt/homebrew/bin/node`)
- **No nvm**: Not using node version manager
- **No global npm Claude installation**: Claude not installed via npm

### tweakcc installation status

- **Not currently installed**: No `~/.tweakcc/` directory exists
- **Can be used via npx**: `npx tweakcc` works (installs on-demand)
- **Latest version available**: v3.4.0

## 3. Patch Survival and Re-application Strategy

### Does tweakcc survive npm update?

**No, patches are overwritten by updates**, but configuration is preserved.

When Claude Code updates:
1. Customizations are lost (binary/cli.js file replaced)
2. Configuration remains in `~/.tweakcc/config.json`
3. Patches can be reapplied: `npx tweakcc --apply`

### Backup mechanism

tweakcc maintains a backup of the original installation, allowing it to start from a clean state each time patches are applied. This ensures idempotent patch application.

### Version control for patches

**Recommended by tweakcc authors**: Initialize Git repository in `~/.tweakcc/`

From documentation:
> "This is a great idea, and we recommend it; in fact, we have one ourselves here. It allows you to keep your modified prompt safe in GitHub or elsewhere, and you can also switch from one set of prompts to another via branches, for example."

tweakcc provides auto-generated `.gitignore` and plans future integration for automated Git management.

**Current implementation**: Manual Git initialization and management required.

### Post-install hooks

**No automatic post-install hooks** in tweakcc package.json. Users must manually run `npx tweakcc --apply` after Claude Code updates.

**Potential automation strategies:**
1. Shell alias/wrapper that checks tweakcc config timestamp vs Claude Code binary timestamp
2. Cron job or launchd agent to monitor Claude Code updates
3. Manual workflow: update Claude Code → run `npx tweakcc --apply`

## 4. Integration with Edify/Project Wrappers

### Current project wrapper configuration

**No evidence of "Edify" wrapper found** in the project.

**Existing Claude CLI configurations:**

From `.claude/tools.md`:
```bash
# Example disallowed tools configurations
claude --disallowed-tools "Task,TaskOutput,Glob,Grep,Read,Bash,Edit,Write,..."
claude --disallowed-tools "NotebookEdit,ExitPlanMode,EnterPlanMode,WebFetch,WebSearch,Skill"
```

From `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [...],
    "additionalDirectories": [
      "/Users/david/code/claude-code-system-prompts"
    ]
  }
}
```

**No `--system-prompt` usage detected** in project files.

### How tweakcc would fit with `--system-prompt` wrappers

**Architecture insights:**

tweakcc operates at a **different layer** than `--system-prompt`:

| Layer | Mechanism | Scope |
|-------|-----------|-------|
| **Installation-level** (tweakcc) | Patches compiled JavaScript | Persistent across all invocations |
| **Runtime-level** (`--system-prompt`) | CLI flag | Per-invocation override |

**Integration pattern:**

1. **tweakcc patches**: Modify tool descriptions, UI elements, default prompts
2. **`--system-prompt` wrapper**: Override main system prompt per invocation
3. **Result**: Layered customization

**Complementary, not conflicting**: A wrapper using `--system-prompt` can coexist with tweakcc patches. They modify different components:
- tweakcc: Tool descriptions, UI, default system prompt
- `--system-prompt`: Main system prompt override (wins over tweakcc's system prompt patch)

### Integration with fragment override strategy

From `plans/feature-requests/fragment-redundancy-analysis.md`:

**Project's current problem:**
- ~650 tokens in CLAUDE.md fragments
- ~3095 tokens in builtin prompts that overlap
- ~3745 tokens total redundancy per session

**tweakcc integration plan (from fragment-redundancy-analysis.md):**

**Phase 1: Override builtin prompts via tweakcc**
- Remove git commit/PR instructions (~1615 tokens)
- Replace sandbox note with project-specific guidance
- Remove scratchpad directory guidance
- Remove "Avoid using Bash with..." section

**Phase 2: Fragment cleanup**
- Remove `tmp-directory.md` (after sandbox note overridden)
- Remove `commit-skill-usage.md` (after git instructions removed)
- Keep edit-level batching, delegation framing, project-specific patterns

**Phase 3: PreToolUse hook enforcement**
- Replace prompt-level "use specialized tools" with runtime hook

### Wrapper integration examples

**Related projects** demonstrating integration patterns:
- [clotilde](https://github.com/fgrehm/clotilde) - Session management wrapper
- [ccstatusline](https://github.com/sirmalloc/ccstatusline) - Status line formatter
- [cc-mirror](https://github.com/numman-ali/cc-mirror) - Multi-variant manager using tweakcc customizations

**No documented examples** of combining tweakcc with `--system-prompt` wrappers specifically.

### Ad-hoc patching for custom modifications

tweakcc provides three patching modes for custom modifications:

**1. Fixed string replacement:**
```bash
npx tweakcc adhoc-patch --string 'old text' 'new text'
```

**2. Regex-based:**
```bash
npx tweakcc adhoc-patch --regex 'pattern' 'replacement'
```
Supports capture groups for complex replacements.

**3. Custom Node.js scripts:**
```bash
npx tweakcc adhoc-patch --script <path-to-script.js>
# Or remote:
npx tweakcc adhoc-patch --script https://example.com/patch.js
```

Scripts receive:
- Full JavaScript content as global `js` variable
- Utility references in `vars` object
- Sandboxed execution using `--experimental-permission`

### Remote configuration support

```bash
npx tweakcc --apply --config-url https://example.com/config.json
```

Remote settings merge into `remoteConfig.settings` without overwriting local configuration. Useful for:
- Team-shared configurations
- Multiple environment profiles
- Version-controlled config distribution

## 5. Implementation Recommendations

### For this project (edify-bash-git-prompt)

**Immediate next steps:**

1. **Initialize tweakcc configuration:**
   ```bash
   npx tweakcc
   # Configure to remove redundant builtin prompts
   git init ~/.tweakcc
   cd ~/.tweakcc && git add . && git commit -m "Initial tweakcc config"
   ```

2. **Target builtin prompts for removal/override:**
   - `tool-description-bash-git-commit-and-pr-creation-instructions.md` → empty
   - `tool-description-bash-sandbox-note.md` → replace with project-specific
   - `system-prompt-scratchpad-directory.md` → empty
   - Bash tool "Avoid using Bash with..." → empty (use PreToolUse hook instead)

3. **Create wrapper script** (if needed for `--system-prompt`):
   ```bash
   #!/usr/bin/env bash
   # ~/.local/bin/claude-wrapped
   exec /Users/david/.local/bin/claude --system-prompt /path/to/custom-system-prompt.md "$@"
   ```

4. **Post-update workflow:**
   ```bash
   # After Claude Code updates:
   npx tweakcc --apply
   ```

### Automation opportunities

**Shell alias with update detection:**
```bash
alias claude='[ ~/.tweakcc/config.json -nt /Users/david/.local/share/claude/versions/$(readlink /Users/david/.local/bin/claude | xargs basename) ] || npx tweakcc --apply; /Users/david/.local/bin/claude'
```

**Justfile recipe:**
```just
# Apply tweakcc patches if Claude Code updated
tweakcc-check:
    #!/usr/bin/env bash
    config=~/.tweakcc/config.json
    claude_bin=/Users/david/.local/share/claude/versions/2.1.37
    if [ "$claude_bin" -nt "$config" ]; then
        npx tweakcc --apply
    fi
```

### Known limitations

1. **No automatic post-install hooks**: Manual `--apply` required after updates
2. **Binary patching risks**: Ad-hoc signing may cause issues with some macOS security settings
3. **Version-specific patches**: Non-system-prompt patches may break across Claude Code versions
4. **No wrapper-level integration**: tweakcc operates at installation level, not runtime
5. **`excludedCommands` unreliable**: Known bugs with sandbox bypass (use `dangerouslyDisableSandbox: true` instead)

### Alternative: Feature request strategy

Instead of tweakcc (or alongside it), this project has **three pending feature requests** to Claude Code:

1. **Tool description overrides** (`gh-issue-tool-overrides.md`) - Settings to override builtin tool description components
2. **Sandbox denial behavior** (`gh-issue-sandbox-deny-default.md`) - Stop agent on sandbox denial instead of auto-retry
3. **Configurable sandbox allowlist** (`gh-issue-sandbox-allowlist.md`) - Project-specific write allowlist

If these feature requests are accepted, tweakcc becomes **unnecessary for this project's use case**.

**Recommendation**: Submit feature requests first, use tweakcc as interim solution if needed.

## 6. References

- **tweakcc repository**: https://github.com/Piebald-AI/tweakcc
- **node-lief dependency**: Binary parsing library for Mach-O/ELF/PE executables
- **Claude Code system prompts**: https://github.com/Piebald-AI/claude-code-system-prompts (v2.0.76 analyzed in this project)
- **Fragment redundancy analysis**: `plans/feature-requests/fragment-redundancy-analysis.md`
- **Feature request drafts**: `plans/feature-requests/gh-issue-*.md`

## 7. Token Cost Analysis

### Current state (without tweakcc)

| Component | Tokens | Notes |
|-----------|--------|-------|
| Project fragments | ~650 | CLAUDE.md loaded content |
| Builtin overlapping prompts | ~3095 | Cannot be disabled without tweakcc |
| **Total redundancy** | **~3745** | Per session waste |

### With tweakcc (projected)

| Component | Tokens | Notes |
|-----------|--------|-------|
| Project fragments | ~400 | After removing tmp-directory.md, commit-skill-usage.md |
| Builtin overlapping prompts | ~200 | After overriding/removing via tweakcc |
| **Total** | **~600** | ~3145 token savings (84% reduction) |

### ROI calculation

- **Savings per session**: ~3145 tokens
- **Sessions per day**: ~10-20 (estimated)
- **Daily savings**: ~31,450-62,900 tokens
- **Monthly savings**: ~944,000-1,887,000 tokens

At typical API costs, this represents significant cost reduction for high-volume usage.
