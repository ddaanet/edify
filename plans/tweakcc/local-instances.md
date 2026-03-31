# Project-Local Claude Code Installations with tweakcc

Research findings on setting up project-local Claude Code installations and driving tweakcc patches from them.

## Executive Summary

**Key Findings:**
- Claude Code CAN be installed locally via npm as a project dependency
- tweakcc CAN target local npm installations via `TWEAKCC_CC_INSTALLATION_PATH` env var
- Local npm installation provides JavaScript directly (no binary unpacking needed)
- Per-project tweakcc configurations are NOT natively supported (global config only)
- **Critical limitation:** tweakcc patches do NOT survive npm updates (patches lost on reinstall)
- **Recommended approach:** Use tweakcc as a build step to apply patches after installation

---

## 1. Project-Local Claude via npm

### Installation Methods

Claude Code is available as `@anthropic-ai/claude-code` on npm, though npm installation is **officially deprecated** in favor of native binary installation.

**Global installation (deprecated):**
```bash
npm install -g @anthropic-ai/claude-code
```

**Local installation (project dependency):**
```bash
# Add to package.json devDependencies
npm install --save-dev @anthropic-ai/claude-code

# Or install without saving
npm install --no-save --prefix ./path @anthropic-ai/claude-code
```

### Package Structure

When installed locally via npm, Claude Code appears in `node_modules/@anthropic-ai/claude-code/`:

```
@anthropic-ai/claude-code/
├── cli.js                    # Main executable (11.3 MB, bundled JS)
├── package.json              # Package metadata
├── vendor/
│   └── ripgrep/             # Platform-specific ripgrep binaries
├── resvg.wasm               # SVG rendering
├── tree-sitter*.wasm        # Syntax parsing
└── sdk-tools.d.ts           # TypeScript definitions
```

**Key details:**
- `cli.js` is a Node.js executable with shebang: `#!/usr/bin/env node`
- Total unpacked size: ~71 MB
- No dependencies (everything bundled)
- Requires Node.js 18+

### Running Locally-Installed Claude

**Via npx (recommended):**
```bash
npx claude --version  # Finds local installation first
```

**Direct bin execution:**
```bash
./node_modules/.bin/claude --version
```

**Via package.json script:**
```json
{
  "scripts": {
    "claude": "claude"
  }
}
```

Then: `npm run claude`

### Version Pinning

You can pin specific Claude Code versions in `package.json`:

```json
{
  "devDependencies": {
    "@anthropic-ai/claude-code": "2.1.37"
  }
}
```

**Available versions:** 318 versions published (latest: 2.1.37, stable: 2.1.25)

**Caution:** Version pinning prevents auto-updates. The native binary installation auto-updates by default, but npm installations do not.

### npm vs Native Binary Differences

| Aspect | npm Installation | Native Binary |
|--------|------------------|---------------|
| **Format** | JavaScript (cli.js) | Mach-O/ELF/PE executable |
| **Size** | ~71 MB unpacked | ~15-25 MB (platform-specific) |
| **Auto-updates** | No | Yes (configurable) |
| **Installation** | Per-project or global | User-wide |
| **tweakcc patching** | Direct JS modification | Extract → patch → repack |
| **Packaging** | Same JS across platforms | Platform-specific binaries |
| **Official status** | Deprecated | Recommended |

**Key insight:** npm installations are **easier to patch** with tweakcc because they're already JavaScript — no binary extraction/repacking needed.

---

## 2. tweakcc with Local Instances

### Installation Detection

tweakcc detects Claude Code installations using this **priority order**:

1. **Direct path specification** (via `--path` flag or API options)
2. **Environment variable**: `TWEAKCC_CC_INSTALLATION_PATH`
3. **Config file setting**: `ccInstallationPath` in `~/.tweakcc/config.json`
4. **PATH discovery**: Locates `claude` executable in system PATH
5. **Hard-coded search paths**: Platform-specific default installation directories

### Targeting Local npm Installation

**Method 1: Environment variable (recommended for automation)**

```bash
export TWEAKCC_CC_INSTALLATION_PATH=/path/to/project/node_modules/@anthropic-ai/claude-code/cli.js
npx tweakcc --apply
```

**Method 2: Config file**

Edit `~/.tweakcc/config.json`:

```json
{
  "ccInstallationPath": "/path/to/project/node_modules/@anthropic-ai/claude-code/cli.js",
  "ccVersion": "2.1.37",
  "changesApplied": true,
  "settings": { /* customizations */ }
}
```

**Method 3: Programmatic API**

```javascript
import * as tweakcc from 'tweakcc';

const installation = await tweakcc.tryDetectInstallation({
  path: './node_modules/@anthropic-ai/claude-code/cli.js'
});

let content = await tweakcc.readContent(installation);
content = content.replace(/old/g, 'new');
await tweakcc.writeContent(installation, content);
```

### How tweakcc Handles npm vs Native

**npm installations:**
- **Read:** Direct file read of `cli.js`
- **Write:** Direct file write to `cli.js`
- **No repacking:** JavaScript is already accessible

**Native binary installations:**
- **Read:** Use `node-lief` to extract embedded JavaScript
- **Write:** Repack binary with modified JS, re-sign on macOS (ad-hoc)
- **Complex:** Requires breaking hard links, preserving permissions

**Result:** npm installations are **significantly simpler** for tweakcc to patch.

---

## 3. Per-Project tweakcc Configs

### Current Limitations

**Global config only:**
- tweakcc stores configuration in `~/.tweakcc/config.json`
- **No built-in support** for per-project configuration files
- All customizations are user-wide, not project-specific

**Config directory locations (priority order):**
1. `$TWEAKCC_CONFIG_DIR` (env var override)
2. `$XDG_CONFIG_HOME/tweakcc` (XDG standard)
3. `~/.tweakcc` (default)

### Workarounds for Per-Project Configs

**Option 1: Environment variable override**

```bash
# Set per-project config directory
export TWEAKCC_CONFIG_DIR=/path/to/project/.tweakcc
npx tweakcc --apply
```

**Limitations:**
- Must export env var before each tweakcc invocation
- Not well-documented
- Config directory must exist

**Option 2: Programmatic API with custom patches**

```javascript
// project-patches.mjs
import * as tweakcc from 'tweakcc';
import fs from 'fs/promises';

const projectConfig = JSON.parse(
  await fs.readFile('./tweakcc-config.json', 'utf-8')
);

const installation = await tweakcc.tryDetectInstallation({
  path: './node_modules/@anthropic-ai/claude-code/cli.js'
});

let content = await tweakcc.readContent(installation);

// Apply project-specific patches
for (const patch of projectConfig.patches) {
  content = content.replace(
    new RegExp(patch.pattern, patch.flags),
    patch.replacement
  );
}

await tweakcc.writeContent(installation, content);
console.log('Project patches applied');
```

**Usage:**
```bash
node project-patches.mjs
```

**Option 3: Ad-hoc patching command**

tweakcc supports one-off patches without UI:

```bash
# String replacement
npx tweakcc adhoc-patch --string '"old"' '"new"'

# Regex replacement
npx tweakcc adhoc-patch --regex '/pattern/g' 'replacement'

# JavaScript script from file
npx tweakcc adhoc-patch --script '@./patch.js'
```

**Script format:**
```javascript
// patch.js
// Modify global 'js' variable and return it
js = js.replace(/old/g, 'new');
return js;
```

### Recommended Per-Project Pattern

**Project structure:**
```
my-project/
├── package.json
├── tweakcc-patches/
│   ├── apply-patches.mjs    # Script to apply all patches
│   ├── config.json          # Project-specific tweakcc settings
│   └── patches/
│       ├── tool-descriptions.patch.mjs
│       └── system-prompts.patch.mjs
├── node_modules/
│   └── @anthropic-ai/claude-code/
└── scripts/
    └── setup-claude.sh      # Run after npm install
```

**setup-claude.sh:**
```bash
#!/usr/bin/env bash
set -euo pipefail

# Install npm dependencies (includes Claude Code)
npm install

# Apply tweakcc patches
node tweakcc-patches/apply-patches.mjs

echo "Claude Code patched and ready"
```

**package.json:**
```json
{
  "scripts": {
    "postinstall": "node tweakcc-patches/apply-patches.mjs",
    "claude": "claude",
    "claude:patch": "node tweakcc-patches/apply-patches.mjs"
  },
  "devDependencies": {
    "@anthropic-ai/claude-code": "2.1.37",
    "tweakcc": "^3.4.0"
  }
}
```

---

## 4. Integration with edify (Edify Wrapper)

### Current Project Structure

The `edify` project has:
- **justfile recipes** for project tasks
- **No existing Claude wrapper** (grep found no "edify" mentions in code)
- **Session.md mentions** "Edify just wrapper" as a pending task

From session.md:
```
- [ ] **Integrate tweakcc with Edify just wrapper** — tweakcc patches prompt strings
      in local Claude Code. Evaluate as Edify's tool description override mechanism.
      Key: Edify already runs `--system-prompt` disabled; tweakcc fills gap for tool
      descriptions. Research: survives npm updates? Post-install hook?
      Version-control patches?

- [ ] **Include custom system prompt injection in Edify just wrapper** — Override/replace
      builtin tool descriptions and system prompt components when wrapping `claude` CLI
```

### Proposed Integration Approaches

**Approach 1: Just recipe wrapper**

```just
# edify/justfile

# Run Claude Code with project-specific patches applied
claude *ARGS:
    #!/usr/bin/env bash
    set -euo pipefail

    # Ensure local Claude is patched
    if [ ! -f .claude-patched ] || [ node_modules/@anthropic-ai/claude-code/cli.js -nt .claude-patched ]; then
        echo "Applying tweakcc patches..."
        node tweakcc-patches/apply-patches.mjs
        touch .claude-patched
    fi

    # Run patched local Claude
    ./node_modules/.bin/claude {{ ARGS }}
```

**Usage:**
```bash
just claude          # Runs patched Claude in current directory
just claude --help   # Pass arguments through
```

**Approach 2: Shell wrapper script**

```bash
#!/usr/bin/env bash
# bin/edify-claude

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_BIN="$PROJECT_ROOT/node_modules/.bin/claude"
PATCH_SCRIPT="$PROJECT_ROOT/tweakcc-patches/apply-patches.mjs"

# Apply patches if needed
if [ ! -f "$PROJECT_ROOT/.claude-patched" ] || \
   [ "$PROJECT_ROOT/node_modules/@anthropic-ai/claude-code/cli.js" -nt "$PROJECT_ROOT/.claude-patched" ]; then
    echo "Applying tweakcc patches..." >&2
    node "$PATCH_SCRIPT"
    touch "$PROJECT_ROOT/.claude-patched"
fi

# Run with custom system prompt disabled if specified
exec "$CLAUDE_BIN" "$@"
```

**Approach 3: npm script + just launcher**

```json
{
  "scripts": {
    "claude": "node tweakcc-patches/check-and-patch.mjs && claude",
    "claude:patch": "node tweakcc-patches/apply-patches.mjs"
  }
}
```

```just
# Launch patched Claude
claude *ARGS:
    npm run claude -- {{ ARGS }}

# Force re-apply patches
claude-patch:
    npm run claude:patch
```

### Interaction with `--system-prompt` Flag

**Current behavior:**
- `claude --system-prompt=false` disables custom system prompts
- Does NOT disable builtin tool descriptions
- Does NOT disable core behavioral instructions

**tweakcc fills the gap:**
- Modifies embedded tool description strings in cli.js
- Can override builtin behavioral instructions
- Operates at a lower level than `--system-prompt` flag

**Combined usage:**
```bash
# Run with custom prompts disabled + tweakcc tool overrides
just claude --system-prompt=false
```

**Result:**
- User's CLAUDE.md and fragments: Disabled
- Builtin tool descriptions: Overridden by tweakcc
- Core instructions: Potentially overridden by tweakcc

---

## 5. Practical Workflow & Update Survival

### Developer Workflow (Ideal)

**Initial setup:**
```bash
# 1. Clone project
git clone https://github.com/org/project.git
cd project

# 2. Install dependencies (including local Claude Code)
npm install

# 3. Patches applied automatically via postinstall hook
# (or manually: npm run claude:patch)

# 4. Run patched Claude
npx claude
# or: npm run claude
# or: just claude
```

**Day-to-day usage:**
```bash
# Just run Claude - patches auto-apply if needed
npx claude

# Check patch status
npm run claude:patch -- --dry-run  # (if implemented)
```

### Update Survival: **NO**

**Critical finding:** tweakcc patches do **NOT** survive npm updates.

**Why:**
- npm reinstalls packages by **replacing** the entire directory
- `cli.js` is overwritten with the original from npm registry
- All patches lost

**Evidence:**
```bash
npm install @anthropic-ai/claude-code@2.1.37  # Patches applied
npm update @anthropic-ai/claude-code          # Patches LOST
npm install                                   # Patches LOST (if version changed)
```

### Post-Install Hooks: Required Pattern

**Solution:** Use `postinstall` hook to reapply patches after every install.

**package.json:**
```json
{
  "scripts": {
    "postinstall": "node tweakcc-patches/apply-patches.mjs"
  },
  "devDependencies": {
    "@anthropic-ai/claude-code": "2.1.37",
    "tweakcc": "^3.4.0"
  }
}
```

**How it works:**
1. `npm install` runs
2. Installs/updates `@anthropic-ai/claude-code`
3. Runs `postinstall` script automatically
4. Reapplies patches to fresh `cli.js`

**Limitations:**
- Adds ~1-3 seconds to install time
- Requires tweakcc as a dependency
- Fails silently if patch script has errors (unless `set -e`)

### Version-Control Considerations

**What to commit:**
```
✅ tweakcc-patches/           # Patch scripts and config
✅ package.json               # Pins Claude version + includes postinstall
✅ package-lock.json          # Locks exact versions
✅ justfile / wrapper scripts # Launch commands
❌ node_modules/              # Never commit (includes patched Claude)
❌ .claude-patched            # Ephemeral timestamp file
```

**Why not commit patched cli.js:**
- Huge file (11 MB)
- Binary format (poor diffs)
- Regenerated on every install
- Patches are code-reviewed via patch scripts, not the patched output

**Recommended .gitignore:**
```gitignore
node_modules/
.claude-patched
```

### Comparison: Native Binary vs npm Approach

| Aspect | Native Binary + Manual tweakcc | npm + Postinstall Hook |
|--------|-------------------------------|------------------------|
| **Updates** | Auto-updates, loses patches | Manual via package.json, patches auto-reapply |
| **Team sync** | Each dev runs tweakcc manually | `npm install` applies patches automatically |
| **Version control** | tweakcc config in ~/.tweakcc | Patch scripts in repo |
| **Portability** | Platform-specific binaries | Cross-platform JavaScript |
| **Patch application** | Binary extraction + repack | Direct JS modification |
| **Complexity** | High (binary manipulation) | Low (text replacement) |
| **Recommended for** | Individual customization | Team/project standards |

**Verdict for edify/Edify:**
- **Use npm installation** for project-local control
- **Use postinstall hook** to reapply patches automatically
- **Store patch scripts** in repo for version control
- **Pin Claude version** in package.json to prevent surprise updates

---

## 6. Advanced: tweakcc API Integration

### Programmatic Patching Example

```javascript
// tweakcc-patches/apply-patches.mjs
import * as tweakcc from 'tweakcc';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

async function applyProjectPatches() {
  // Detect local installation
  const installation = await tweakcc.tryDetectInstallation({
    path: join(projectRoot, 'node_modules/@anthropic-ai/claude-code/cli.js')
  });

  console.log(`Found Claude ${installation.ccVersion} at ${installation.path}`);
  console.log(`Installation type: ${installation.kind}`);

  // Read current content
  let content = await tweakcc.readContent(installation);

  // Create backup
  await tweakcc.backupFile(
    installation.path,
    join(projectRoot, '.claude-backup')
  );

  // Apply patches
  const patches = [
    {
      name: 'Disable telemetry',
      pattern: /"enableTelemetry":\s*true/g,
      replacement: '"enableTelemetry": false'
    },
    {
      name: 'Custom thinking verbs',
      pattern: /"thinking"/g,
      replacement: '"pondering"'
    },
    {
      name: 'Override Bash tool description',
      pattern: /Executes a given bash command/g,
      replacement: 'Executes bash commands with project-specific constraints'
    }
  ];

  for (const patch of patches) {
    const before = content;
    content = content.replace(patch.pattern, patch.replacement);
    const matches = (before.match(patch.pattern) || []).length;
    console.log(`  ✓ ${patch.name}: ${matches} replacement(s)`);
  }

  // Write back
  await tweakcc.writeContent(installation, content);
  console.log('All patches applied successfully');
}

applyProjectPatches().catch(err => {
  console.error('Patch failed:', err);
  process.exit(1);
});
```

### Key API Functions

From tweakcc's exported API:

**Installation detection:**
```javascript
// Find all installations
const installations = await tweakcc.findAllInstallations();

// Auto-detect with fallback
const inst = await tweakcc.tryDetectInstallation({ interactive: true });

// Interactive picker
const selected = await tweakcc.showInteractiveInstallationPicker(installations);
```

**Content manipulation:**
```javascript
// Read (handles both npm and native)
const jsContent = await tweakcc.readContent(installation);

// Write (handles repacking for native)
await tweakcc.writeContent(installation, modifiedContent);
```

**Backup/restore:**
```javascript
// Backup
await tweakcc.backupFile(installation.path, backupPath);

// Restore
await tweakcc.restoreBackup(backupPath, installation.path);
```

**Configuration:**
```javascript
// Get paths
const configDir = tweakcc.getTweakccConfigDir();
const configPath = tweakcc.getTweakccConfigPath();
const promptsDir = tweakcc.getTweakccSystemPromptsDir();

// Read config
const config = await tweakcc.readTweakccConfig();
```

**Utility helpers:**
```javascript
// Find minified variable names for advanced patching
const chalk = tweakcc.findChalkVar(content);
const react = tweakcc.getReactVar(content);
const require = tweakcc.getRequireFuncName(content);

// Apply replacements with diff output
const result = tweakcc.globalReplace(content, /pattern/g, 'replacement');

// Clear caches when processing multiple installations
tweakcc.clearCaches();
```

---

## 7. Recommendations for edify

### Short-term (Immediate Implementation)

1. **Add npm Claude as devDependency:**
   ```json
   {
     "devDependencies": {
       "@anthropic-ai/claude-code": "2.1.37",
       "tweakcc": "^3.4.0"
     }
   }
   ```

2. **Create patch script directory:**
   ```
   tweakcc-patches/
   ├── apply-patches.mjs        # Main patch application script
   ├── patches/
   │   ├── tool-overrides.mjs   # Tool description patches
   │   └── behavioral.mjs       # Behavioral instruction patches
   └── config.json              # Project-specific settings
   ```

3. **Add postinstall hook:**
   ```json
   {
     "scripts": {
       "postinstall": "node tweakcc-patches/apply-patches.mjs",
       "claude": "claude",
       "claude:patch": "node tweakcc-patches/apply-patches.mjs"
     }
   }
   ```

4. **Add just recipe launcher:**
   ```just
   # Run project-local Claude
   claude *ARGS:
       npx claude {{ ARGS }}

   # Reapply patches manually
   claude-patch:
       npm run claude:patch
   ```

### Medium-term (After Initial Testing)

1. **Document patching workflow** in project README
2. **Add patch validation** (verify patches applied correctly)
3. **Create patch library** for common overrides
4. **Add --dry-run mode** to preview patches without applying

### Long-term (Advanced Integration)

1. **Evaluate tweakcc alternatives** if better tools emerge
2. **Contribute upstream** to Claude Code for official override mechanisms
3. **Monitor feature requests** submitted to anthropics/claude-code
4. **Consider custom fork** if patches become too complex

---

## 8. Gotchas & Limitations

### Sandboxing Issues

**Problem:** Claude Code's sandbox blocks writes to certain paths.

**Impact on tweakcc:**
- May fail to write patched cli.js if sandboxed
- Config writes to `~/.tweakcc/` may be blocked

**Solution:**
- Run tweakcc with `dangerouslyDisableSandbox: true` if needed
- Or apply patches outside Claude Code environment (e.g., via npm script)

### Permission Errors

**Problem:** `cli.js` may have restrictive permissions after npm install.

**Symptoms:**
```
Error: EACCES: permission denied, open 'node_modules/@anthropic-ai/claude-code/cli.js'
```

**Solution:**
```bash
chmod u+w node_modules/@anthropic-ai/claude-code/cli.js
node tweakcc-patches/apply-patches.mjs
```

### npm vs npx Confusion

**Problem:** Multiple Claude installations can conflict.

**Scenario:**
- Global native binary: `/usr/local/bin/claude`
- Global npm: `~/.npm-global/bin/claude`
- Local npm: `./node_modules/.bin/claude`

**Which runs when:**
- `claude` → First in PATH (usually global native)
- `npx claude` → Local first, then global npm
- `./node_modules/.bin/claude` → Explicitly local

**Solution for project-local:**
```bash
# Always use npx or explicit path
npx claude           # Finds local installation
npm run claude       # Via package.json script
just claude          # Via justfile wrapper
```

### Patch Brittleness

**Problem:** String replacements break when Claude Code updates its internal structure.

**Example:**
```javascript
// Works in 2.1.37
content = content.replace(/Executes a given bash command/g, 'Override');

// Breaks in 2.1.38 if Anthropic changes wording to:
// "Runs a bash command"
```

**Mitigations:**
1. **Pin Claude version** in package.json
2. **Use regex patterns** that are less brittle
3. **Add patch validation** to detect failures
4. **Maintain patch compatibility matrix**

### System Prompt Interaction

**Problem:** tweakcc patches and `--system-prompt` flag overlap.

**Overlap areas:**
- Tool descriptions (tweakcc can override)
- Core instructions (tweakcc can override)
- User CLAUDE.md (only affected by --system-prompt flag)

**Recommendation:**
- Use `--system-prompt=false` to disable user overrides
- Use tweakcc to set project-wide tool behavior
- Keep them orthogonal: tweakcc for tool layer, CLAUDE.md for user layer

---

## 9. Alternatives Considered

### Alternative 1: Fork Claude Code

**Approach:** Maintain a custom fork of `@anthropic-ai/claude-code` with modifications.

**Pros:**
- Full control over all changes
- No patching needed
- Can add new features

**Cons:**
- Must merge upstream updates manually
- Diverges from official releases
- Hard to distribute to team
- Significant maintenance burden

**Verdict:** Not recommended unless making substantial modifications.

### Alternative 2: MCP Server for Tool Overrides

**Approach:** Use Model Context Protocol (MCP) to provide custom tool implementations.

**Pros:**
- Official extension mechanism
- No patching required
- Portable across Claude installations

**Cons:**
- Cannot override builtin tools (yet)
- Cannot modify core behavioral instructions
- Limited to additive functionality

**Verdict:** Complementary to tweakcc, not a replacement. Use MCP for new tools, tweakcc for overriding builtins.

### Alternative 3: Claude Code Plugin System

**Status:** Not currently available.

**Future possibility:** If Claude Code adds an official plugin system for tool overrides, it would supersede tweakcc patching.

**Action:** Monitor `anthropics/claude-code` releases and feature requests.

### Alternative 4: Shell Wrapper with Env Vars

**Approach:** Intercept Claude invocations and inject instructions via environment variables.

**Example:**
```bash
CLAUDE_TOOL_BASH_OVERRIDE="Use specialized tools instead of Bash" \
  claude
```

**Status:** Claude Code does not support env var overrides (as of 2.1.37).

**Verdict:** Not currently viable.

---

## 10. References & Resources

### Documentation

- **Claude Code Setup:** https://code.claude.com/docs/en/setup
- **tweakcc GitHub:** https://github.com/Piebald-AI/tweakcc
- **npm Package:** https://www.npmjs.com/package/@anthropic-ai/claude-code
- **tweakcc npm:** https://www.npmjs.com/package/tweakcc

### Related Issues

- **Feature request context:** See `plans/feature-requests/gh-issue-tool-overrides.md`
- **Fragment redundancy:** See `plans/feature-requests/fragment-redundancy-analysis.md`

### Related Projects

- **cc-mirror:** Demonstrates using tweakcc API for multiple Claude variants (mentioned in tweakcc docs)
- **Piebald AI system prompts:** https://github.com/Piebald-AI/claude-code-system-prompts

### Key Files in edify

- **session.md:** Pending tasks for Edify wrapper integration
- **justfile:** Existing project recipes (no Claude wrapper yet)
- **No existing Edify code found** (term mentioned only in session.md)

---

## 11. Next Steps for Implementation

### Phase 1: Proof of Concept (1-2 hours)

1. Add `@anthropic-ai/claude-code` and `tweakcc` to devDependencies
2. Create minimal `tweakcc-patches/apply-patches.mjs` script
3. Test patching tool description strings
4. Verify patches survive `npm install`

### Phase 2: Integration (2-4 hours)

1. Create comprehensive patch script with validation
2. Add postinstall hook
3. Create `just claude` launcher recipe
4. Document usage in README
5. Test with team members

### Phase 3: Refinement (2-4 hours)

1. Add dry-run mode for patch preview
2. Create patch library for common overrides
3. Add error handling and rollback
4. Integrate with existing edify workflows

### Phase 4: Maintenance (Ongoing)

1. Monitor Claude Code updates for breaking changes
2. Update patches as needed
3. Evaluate alternative approaches as they emerge
4. Contribute improvements back to tweakcc

---

## Conclusion

**Key Takeaways:**

✅ **Feasible:** Project-local Claude Code + tweakcc patching is viable
✅ **Automatable:** postinstall hooks make patches transparent to users
✅ **Version-controllable:** Patch scripts in repo enable team consistency
❌ **Not persistent:** Patches don't survive updates without automation
⚠️ **Brittle:** String replacements may break on Claude Code updates

**Recommended Pattern:**

```
1. npm install @anthropic-ai/claude-code (local dependency)
2. Add tweakcc as devDependency
3. Create patch scripts in tweakcc-patches/
4. Add postinstall hook to reapply patches
5. Launch via: npx claude, npm run claude, or just claude
```

**For Edify/edify specifically:**

The pending session.md tasks are achievable:
- **"Integrate tweakcc with Edify just wrapper"** → Use npm + postinstall pattern
- **"Include custom system prompt injection"** → Use tweakcc API for tool overrides
- **"Research: survives npm updates?"** → **No**, requires postinstall hook
- **"Post-install hook?"** → **Yes**, required pattern
- **"Version-control patches?"** → **Yes**, store patch scripts in repo

This approach fills the gap between `--system-prompt` (user overrides) and builtin behavior (tool descriptions, core instructions).
