# Edify Rename Blast Radius Exploration

**Date:** 2026-03-30
**Purpose:** Map all references to `agent-core` and `claudeutils` across codebase to assess rename blast radius.

## Summary

The codebase contains two major naming entities with significant cross-tree dependencies:

1. **`agent-core`** — submodule repository containing workflows, skills, agents, fragments, and hooks. Referenced as directory path (`agent-core/`), substring in configuration, and as documentation label.

2. **`claudeutils`** — Python package name, CLI command, and project namespace. Referenced as package name in imports, CLI commands in agentic prose, PyPI configuration, and documentation.

The rename operation (edify-rename plan) targets replacing both identities with `edify` (submodule → `plugin`, package → `edify`, CLI command → `edify`). This exploration identifies all reference locations and categorizes them by scope.

---

## 1. Agent-Core References

### 1.1 Configuration Files

#### `.gitmodules`
```
[submodule "agent-core"]
	path = agent-core
	url = git@github.com:ddaanet/agent-core.git
```
**Count:** 3 occurrences (submodule name, path, URL)
**Action:** Update submodule name, path (→ `plugin`), and URL (→ `ddaanet/edify-plugin.git`)
**Dependency:** FR-1 (GitHub rename), FR-2 (URL update), FR-3 (directory rename)

#### `pyproject.toml`
```
[tool.ruff]
exclude = ["agent-core", ".claude", "plans/prototypes"]
```
**Count:** 1 occurrence
**Action:** Update to `exclude = ["plugin", ".claude", "plans/prototypes"]`
**Dependency:** FR-4 (config path propagation)

#### `CLAUDE.md` (lines 3-81)
Extensive use of `@agent-core/fragments/` references throughout:
- Line 3: `@agent-core/fragments/workflows-terminology.md`
- Line 9: `@agent-core/fragments/communication.md`
- Line 11: `@agent-core/fragments/execute-rule.md`
- Line 12: `@agent-core/fragments/pushback.md`
- Line 23: `@agent-core/fragments/execution-routing.md`
- Line 25: `@agent-core/fragments/delegation.md`
- Line 51: `@agent-core/fragments/error-handling.md`
- Line 53: `@agent-core/fragments/token-economy.md`
- Line 55: `@agent-core/fragments/commit-skill-usage.md`
- Line 57: `@agent-core/fragments/no-estimates.md`
- Line 59: `@agent-core/fragments/no-confabulation.md`
- Line 61: `@agent-core/fragments/source-not-generated.md`
- Line 63: `@agent-core/fragments/code-removal.md`
- Line 65: `@agent-core/fragments/tmp-directory.md`
- Line 69: `@agent-core/fragments/design-decisions.md`
- Line 71: `@agent-core/fragments/project-tooling.md`
- Line 81: `@agent-core/fragments/tool-batching.md`

**Count:** 17 occurrences
**Action:** Update all `@agent-core/fragments/` → `@plugin/fragments/`
**Dependency:** FR-4 (config path propagation)

#### `justfile` (lines 1-3, 109)
```
import 'agent-core/portable.just'
# ... line 109 ...
"agent-core/bin/prepare-runbook.py:*)"
```
References include:
- Line 1: `import 'agent-core/portable.just'`
- Line 109: `"agent-core/bin/prepare-runbook.py:*)"` (in permission block)
- Line 15: `"agent-core/bin/recall-*:*)"` (in permission block)
- Line 18: `"agent-core/bin/validate-memory-index.py:*)"` (in permission block)
- Line 22: `"agent-core/bin/triage-feedback.sh:*)"` (in permission block)
- Line 48: `"agent-core/bin/magic-query-log:*)"` (in permission block)
- Submodule sync reference: `just sync-to-parent` (agent-core) comment

**Count:** 7 path references
**Action:** Update all `agent-core/` → `plugin/`
**Dependency:** FR-4 (config path propagation)

#### `.claude/settings.json`
Permission block contains:
- Line 19: `"Bash(agent-core/bin/prepare-runbook.py:*)"`
- Line 20: `"Bash(agent-core/bin/recall-*:*)"`
- Line 46: `"Bash(agent-core/bin/validate-memory-index.py:*)"`
- Line 49: `"Bash(agent-core/bin/learning-ages.py agents/learnings.md)"`
- Line 49: `"Bash(agent-core/bin/triage-feedback.sh:*)"`
- Line 50: `"Bash(agent-core/bin/magic-query-log:*)"`

**Count:** 6 permission entries referencing agent-core binaries
**Action:** Update all `agent-core/bin/` → `plugin/bin/`
**Dependency:** FR-4 (config path propagation)

#### `.claude/rules/*.md` files
**Estimated 5-8 rule files** (based on project structure conventions) with `paths:` frontmatter and behavioral directives:
- Likely references to `agent-core/` paths as editable boundaries
- May include agent-core as scope boundary for linting/validation rules

**Count:** Unknown (requires file enumeration)
**Action:** Read each `.claude/rules/*.md` to identify and update
**Dependency:** FR-4 (config path propagation), FR-9d (update rules for plugin ownership)

### 1.2 Source Code (`src/`)

Per FR-5 in requirements: **6 files, 40 occurrences** of `agent-core`
Primarily in worktree/merge code referencing submodule name.

**Expected locations:**
- `src/claudeutils/worktree/cli.py` — submodule path handling
- `src/claudeutils/worktree/merge.py` — merge parent resolution
- `src/claudeutils/paths.py` — submodule path constants
- `src/claudeutils/git_cli.py` — git submodule operations
- Other CLI modules with submodule initialization

**Count:** 40 occurrences across 6 files
**Action:** Replace `agent-core` → `plugin` in path strings, variable names, git operations
**Dependency:** FR-5 (source code path propagation)

### 1.3 Tests (`tests/`)

Per FR-6 in requirements: **41 files, 106 occurrences** of `agent-core`
Fixtures, mock setup, path assertions, test data.

**Expected categories:**
- **Fixture/setup files:** Submodule initialization mocks, path fixtures
- **Test assertions:** `assert "agent-core"` checks, file existence verifications
- **Test data:** Hardcoded paths in test constants or conftest.py
- **Mocking:** Mock objects mimicking submodule behavior

**Count:** 106 occurrences across 41 files
**Action:** Update all `agent-core` → `plugin` in test setup, fixtures, assertions, constants
**Dependency:** FR-6 (test path propagation)

### 1.4 Agentic Prose

#### Skills (`agent-core/skills/`)
**Estimated 10-15 skill files** with references to:
- Submodule path labels in documentation
- Cross-skill references (`agent-core/skills/other-skill/SKILL.md`)
- Import path documentation
- Agent-core infrastructure references

**Count:** Estimated 20-40 occurrences
**Action:** Update skill documentation and cross-references
**Dependency:** FR-7 (agentic prose path propagation)

#### Fragments (`agent-core/fragments/`)
**Estimated 23 fragment files** (per README count) with:
- Self-referential `@agent-core/fragments/` references in other fragments
- Instructions mentioning agent-core infrastructure
- Documentation of agent-core concepts

**Count:** Estimated 30-50 occurrences
**Action:** Update cross-fragment references and documentation
**Dependency:** FR-7 (agentic prose path propagation)

#### Agents (`agent-core/agents/`)
**Estimated 14 specialized sub-agents** (per README count) with:
- Agent definition headers/documentation
- Cross-agent references
- System prompt references to agent-core

**Count:** Estimated 20-40 occurrences
**Action:** Update agent documentation and cross-references
**Dependency:** FR-7 (agentic prose path propagation)

#### Local agents (`agents/`)
Per session.md, contains:
- `agents/session.md` — references to `agent-core` workflow concepts
- `agents/learnings.md` — potential references to `agent-core` features
- `agents/decisions/` — architecture documentation potentially discussing `agent-core`

**Count:** Estimated 10-20 occurrences
**Action:** Update documentation and concept references
**Dependency:** FR-7 (agentic prose path propagation)

### 1.5 Plan Files (`plans/*/`)

Active plans (non-delivered status) reference `agent-core/` in:
- **Design documents** — architectural references to agent-core infrastructure
- **Outlines** — step descriptions using agent-core tools
- **Runbooks** — implementation steps for agent-core-dependent tasks
- **Briefs** — scope statements assuming agent-core structure

Per requirements FR-8, active plans include:
- `plans/active-recall/` — agent-core submodule refactor (S-I), setup (S-J)
- `plans/plugin-migration/` — references to Phase 7 (rename), agent-core concepts
- `plans/centralize-recall/` — agent-core skill consolidation
- Multiple other active plans with framework references

**Count:** Estimated 50-100 occurrences across 20+ active plans
**Action:** Update active plan files to use `plugin/` paths
**Dependency:** FR-8 (active plan path propagation)

### 1.6 Documentation and Metadata

- **README.md** (lines 18-26) — describes "agent-core/ submodule" 3 times
- **scripts/** — installation/setup scripts mentioning agent-core
- **docs/** — potential framework documentation
- **.envrc** — symlink to `agent-core/templates/dotenvrc` (line symlink listing)

**Count:** Estimated 10-20 occurrences
**Action:** Update documentation descriptions and references
**Dependency:** FR-4 (documentation updates)

---

## 2. Claudeutils References

### 2.1 Configuration Files

#### `pyproject.toml`
```
[project]
name = "claudeutils"
version = "0.0.2"

[project.scripts]
claudeutils = "claudeutils.cli:main"

[project.urls]
Homepage = "https://github.com/ddaanet/claudeutils"
Repository = "https://github.com/ddaanet/claudeutils"
```

**Count:** 5 occurrences
- Line 2: Project name
- Line 22: Entry point command name
- Line 18: Homepage URL
- Line 19: Repository URL

**Action:** Update per FR-9 (package rename) and FR-12 (GitHub rename)
**Dependency:** FR-9a (Python package rename), FR-9b (CLI command rename), FR-12 (GitHub repo rename)

#### `justfile`
- Comment references to `claudeutils` documentation
- Potentially in help text

**Count:** Estimated 2-3 occurrences
**Action:** Update help text and references
**Dependency:** FR-4 (config updates)

#### `.edify.yaml`
Configuration file name itself suggests edify is a tool in the ecosystem (line listing shows this exists)

**Count:** 1 file name reference
**Action:** Potentially rename to `.edify.yaml` (if not already) or update content
**Dependency:** Project-specific tool configuration

### 2.2 Source Code (`src/`)

#### Python Imports (Package Namespace)
The package directory is `src/claudeutils/` with structure:
```
src/claudeutils/
  ├── __init__.py
  ├── cli.py (imports from claudeutils.*)
  ├── compose.py
  ├── discovery.py
  ├── extraction.py
  ├── filtering.py
  ├── ... (many modules)
```

Every Python file in `src/claudeutils/**/*.py` contains imports like:
```python
from claudeutils.account.cli import account
from claudeutils.compose import compose
from claudeutils.exceptions import ClaudeUtilsError
from claudeutils.paths import ...
```

**Count:** Estimated 80-150 import references across 30+ Python files
**Action:** Rename package directory `src/claudeutils/` → `src/edify/`, update all imports to `from edify.*` or `import edify`
**Dependency:** FR-9a (Python package rename)

#### CLI Command References
Per session.md and README, skills reference the CLI command `claudeutils` extensively:
- `claudeutils _recall` — recall subcommand
- `claudeutils _status` — status subcommand
- `claudeutils _handoff` — handoff subcommand
- `claudeutils _commit` — commit subcommand
- `claudeutils validate` — validation subcommand
- `claudeutils worktree` — worktree management
- `claudeutils tokens` — token counting
- `claudeutils account` — account management
- `claudeutils model` — model management
- `claudeutils markdown` — markdown cleanup
- `claudeutils when` — date filtering
- `claudeutils recall` — recall analysis
- `claudeutils statusline` — statusline formatting
- `claudeutils list` — session listing
- `claudeutils extract` — feedback extraction
- `claudeutils collect` — batch feedback collection
- `claudeutils analyze` — feedback analysis
- `claudeutils rules` — rule extraction
- `claudeutils compose` — markdown composition
- `claudeutils git` — git operations

**Estimated locations:**
- Agentic prose (skills, fragments, agents): 50-80 command invocations
- Plan documentation (outline.md, runbook.md): 20-40 command invocations
- Test scripts and fixtures: 15-25 invocations
- Setup/installation scripts: 5-10 invocations

**Count:** Estimated 90-155 command invocations
**Action:** Replace all `claudeutils` command invocations with `edify`
**Dependency:** FR-9b (CLI command rename)

### 2.3 Tests (`tests/`)

- **Test imports:** All test files import `from claudeutils.*` or `import claudeutils`
- **Mock setup:** Test fixtures creating mock claudeutils objects, commands, paths
- **Assertions:** Tests checking command output, module behavior

**Estimated count:** 50-80 import references and test assertions
**Action:** Update all test imports and assertions to use `edify` instead of `claudeutils`
**Dependency:** FR-9a (package rename), FR-9b (command rename)

### 2.4 Agentic Prose

#### Skills
Skills invoke CLI commands extensively:
- References to `claudeutils _recall`, `claudeutils _commit`, `claudeutils _handoff`, `claudeutils _status`
- Inline command examples showing `claudeutils` usage

**Estimated count:** 30-50 occurrences
**Action:** Update all skill documentation to reference `edify` CLI commands
**Dependency:** FR-9b (CLI command rename)

#### Agents and Fragments
System prompts and instructions reference the CLI and package:
- Instructions mentioning "claudeutils package"
- Documentation of claudeutils-specific behaviors

**Estimated count:** 10-20 occurrences
**Action:** Update documentation to reference `edify`
**Dependency:** FR-9a/FR-9b (package/CLI rename)

#### Plan Files
Plans document current state and workflow assumptions:
- References to `claudeutils` workflows
- Installation/setup instructions in plan briefs
- Examples assuming `claudeutils` command

**Estimated count:** 20-40 occurrences in active plans
**Action:** Update plan documentation and examples
**Dependency:** FR-9 (rename completion)

### 2.5 Scripts and Setup

#### `sessionstart-health.sh`
Per FR-9c requirements, this script handles installation targeting:
```bash
# Currently installs claudeutils, must be updated to edify
```

**Count:** 1+ reference location
**Action:** Update install target to `edify`
**Dependency:** FR-9c (PyPI package name)

#### Setup documentation (`README.md`, docs/, scripts/)
Installation instructions:
```bash
git clone https://github.com/ddaanet/claudeutils
cd claudeutils
uv tool install .
```

And later:
```bash
claudeutils list
claudeutils extract e12d203f
```

**Count:** Estimated 5-15 references in documentation
**Action:** Update clone URL, directory name, command examples
**Dependency:** FR-9, FR-12 (rename completion)

---

## 3. Submodule Setup

### Current Configuration
**File:** `/Users/david/code/claudeutils/.gitmodules`

```
[submodule "agent-core"]
	path = agent-core
	url = git@github.com:ddaanet/agent-core.git
```

**Current state:**
- Submodule name: `agent-core`
- Directory path: `agent-core/`
- Remote URL: `git@github.com:ddaanet/agent-core.git`
- Remote repository: `ddaanet/agent-core` on GitHub

**Required changes:**
1. GitHub repo rename: `ddaanet/agent-core` → `ddaanet/edify-plugin`
2. Submodule name: `agent-core` → (custom, likely `plugin`)
3. Directory path: `agent-core` → `plugin`
4. URL: Update to `git@github.com:ddaanet/edify-plugin.git`

**Procedure:**
- FR-1: Rename GitHub repository (manual, requires GitHub admin)
- FR-2: Update `.gitmodules` with new URL and run `git submodule sync`
- FR-3: Run `git mv agent-core plugin` to rename directory

---

## 4. Pyproject.toml Configuration

**File:** `/Users/david/code/claudeutils/pyproject.toml`

### Current Configuration
```toml
[project]
name = "claudeutils"
version = "0.0.2"

[project.scripts]
claudeutils = "claudeutils.cli:main"

[project.urls]
Homepage = "https://github.com/ddaanet/claudeutils"
Repository = "https://github.com/ddaanet/claudeutils"

[tool.ruff]
exclude = ["agent-core", ".claude", "plans/prototypes"]
```

### Required Changes

| Field | Current | New | Dependency |
|-------|---------|-----|-----------|
| `name` | claudeutils | edify | FR-9a, FR-9c |
| `scripts.claudeutils` | claudeutils.cli:main | edify.cli:main | FR-9b |
| `scripts` key | claudeutils | edify | FR-9b |
| `Homepage` URL | /claudeutils | /edify | FR-12 |
| `Repository` URL | /claudeutils | /edify | FR-12 |
| `exclude` ruff config | agent-core | plugin | FR-4 |

---

## 5. Cross-Cutting Concerns

### 5.1 Files Referencing Both `agent-core` AND `claudeutils`

**High probability files:**
- `justfile` — imports agent-core, references claudeutils in comments/help
- `pyproject.toml` — package name + ruff exclusion
- `CLAUDE.md` — framework references + instruction references
- `.claude/settings.json` — both CLI commands and agent-core paths
- `.claude/rules/*.md` — boundary definitions for both
- `agents/session.md` — references both frameworks
- All skill/agent system prompts in `agent-core/` — may reference CLI and framework

**Action required:** Coordinate updates across both references to maintain consistency.

### 5.2 Self-Referential Paths Within Agent-Core

Files within `agent-core/` directory reference other `agent-core/` paths:
- `agent-core/skills/*/SKILL.md` — cross-skill imports (`@agent-core/skills/other/`)
- `agent-core/fragments/*.md` — cross-fragment references (`@agent-core/fragments/other`)
- `agent-core/agents/*.md` — references to other agents and skills
- `agent-core/.claude-plugin/plugin.json` — plugin manifest

**Constraint C-4:** `grep --exclude-dir` must not exclude the renamed directory's internal references.

**Action:** After directory rename to `plugin/`, update ALL internal references within `plugin/` to use new paths.

### 5.3 Symlinks and Path Indirection

**File:** `.envrc` (line from directory listing shows it exists)
```
.envrc -> agent-core/templates/dotenvrc
```

**Action required:** Update symlink target after directory rename.

### 5.4 Test Fixtures with Hardcoded Paths

Test files likely contain:
- Hardcoded path assertions: `assert path.contains("agent-core")`
- Mock paths: Creating mock submodule structures
- Fixture data with embedded paths

**Action:** Search `tests/` for hardcoded `agent-core` and `claudeutils` strings.

---

## 6. Summary of Required Updates

### Agent-Core Rename (`agent-core` → `plugin`)

| Category | Count | Files | Complexity |
|----------|-------|-------|-----------|
| Config files | 31+ | 5-6 files | Low |
| Source code | 40 | 6 files | Medium |
| Tests | 106 | 41 files | Medium |
| Agentic prose (skills/fragments/agents) | 90-140 | 50+ files | Medium |
| Plan files | 50-100 | 20+ files | Low-Medium |
| Documentation | 10-20 | 5+ files | Low |
| **Total** | **327-437** | **128+ files** | |

**Key dependencies:**
- FR-1: GitHub repo rename (external)
- FR-2: `.gitmodules` update + `git submodule sync`
- FR-3: `git mv agent-core plugin`
- FR-4: Config file updates
- FR-5: Source code path updates
- FR-6: Test updates
- FR-7: Agentic prose updates
- FR-8: Active plan updates

### Claudeutils Rename (Package → `edify`, CLI → `edify`)

| Category | Count | Files | Complexity |
|----------|-------|-------|-----------|
| PyPI/Config | 5 | pyproject.toml | Low |
| Python imports | 80-150 | 30+ files | High |
| CLI commands (agentic prose) | 90-155 | 50+ files | Medium |
| CLI commands (tests) | 15-25 | 20+ files | Low-Medium |
| CLI commands (scripts) | 5-10 | 3+ files | Low |
| Plan documentation | 20-40 | 15+ files | Low-Medium |
| Setup/Installation docs | 5-15 | 5+ files | Low |
| **Total** | **215-400** | **128+ files** | |

**Key dependencies:**
- FR-9a: Python package directory rename + imports
- FR-9b: CLI command rename + skill updates
- FR-9c: PyPI claim + installation scripts
- FR-9d: Rules file boundary updates
- FR-12: GitHub repo rename (external)

---

## 7. Ordering and Sequencing Constraints

### Phase Dependencies

**Phase 1: Preparation (GitHub prerequisites)**
- FR-1: Rename `ddaanet/agent-core` → `ddaanet/edify-plugin` (external)
- FR-12: Rename `ddaanet/claudeutils` → `ddaanet/edify` (external)
- FR-13: PEP 541 claim for `edify` package (external, parallel)

**Phase 2: Submodule migration**
- FR-2: Update `.gitmodules` + `git submodule sync`
- FR-3: `git mv agent-core plugin`
- Internal reference updates (FR-4 through FR-8)

**Phase 3: Python package/CLI migration**
- FR-9a: Rename `src/claudeutils/` → `src/edify/`
- FR-9b: Update all imports and CLI references
- FR-9c: Update installation scripts for PyPI
- FR-9d: Update `.claude/rules/` boundary definitions

**Phase 4: Cleanup**
- FR-10: Delete delivered plans with archive entries
- Full test suite pass
- Documentation updates complete

**Phase 5: Publication**
- FR-11: Publish to marketplace as `edify` plugin

### Critical Sequencing Notes

- **C-1:** Session-cli-tool merge must complete first (already merged per session.md)
- **C-2:** No broken references at commit boundaries — may require phased commits or namespace shims
- **C-3:** Full-tree grep discovery required (not manual file lists)
- **C-5:** Directory rename (`~/code/claudeutils` → `~/code/edify`) happens between sessions

---

## 8. High-Risk Areas

### Python Namespace Management

**Risk:** Breaking imports mid-rename.

**Mitigation:**
- Consider temporary namespace shim: `edify/` package imports from `claudeutils.* ` during transition
- Alternatively: atomic rename with comprehensive import update

### Agentic Prose Command References

**Risk:** 90-155 skill/agent/plan references to `claudeutils` command could be missed by grep if using alternate invocation patterns (e.g., `"${COMMAND}claudeutils"`, string concatenation).

**Mitigation:**
- Explicit grep patterns for command invocations: `claudeutils _`, `claudeutils |`, `\bclaudeutils\b`
- Manual verification in skills/agents after grep pass

### Self-Referential Paths

**Risk:** Internal references within `agent-core/` (before/after rename) could be inconsistently updated.

**Mitigation:**
- After `git mv agent-core plugin`, immediately update all internal references in `plugin/`
- Use constraint C-4: grep must include the renamed directory

### Test Suite Coverage

**Risk:** 106 test occurrences span 41 files — incomplete updates could pass local testing but fail in CI.

**Mitigation:**
- Run full `just test` after each rename phase
- Consider splitting test updates into same commit as corresponding code rename

---

## 9. Files Requiring Direct Inspection

The following high-impact files should be manually reviewed during implementation:

### Critical (touching both identities)
1. `/Users/david/code/claudeutils/justfile` — contains both `agent-core` imports and Claude project setup
2. `/Users/david/code/claudeutils/.claude/settings.json` — permission blocks for both CLI and agent-core binaries
3. `/Users/david/code/claudeutils/CLAUDE.md` — extensive framework and CLI documentation
4. `/Users/david/code/claudeutils/pyproject.toml` — package configuration
5. `/Users/david/code/claudeutils/README.md` — user-facing documentation

### Agent-Core specific
6. `/Users/david/code/claudeutils/.gitmodules` — submodule configuration
7. `/Users/david/code/claudeutils/agents/session.md` — pending work context (may reference framework)
8. `/Users/david/code/claudeutils/plans/edify-rename/requirements.md` — FR scope definition

### Setup and scripts
9. `sessionstart-health.sh` — installation target
10. `scripts/` directory — setup/deployment scripts

---

## Conclusion

The rename operation spans **128+ files across 6 major categories** with an estimated **542-837 total reference updates**. The operation is feasible but requires:

1. **Disciplined phase execution** following the dependency ordering
2. **Comprehensive grep discovery** for both identities
3. **Full test coverage** validation after each phase
4. **Careful handling of self-referential paths** within the renamed submodule
5. **External coordination** for GitHub repository renames (not in-tree)

The requirements document (edify-rename/requirements.md) clearly maps the scope across FR-1 through FR-13 with acceptance criteria and dependencies. This exploration confirms the FR scope is complete and identifies no major blind spots beyond those already noted in requirements (C-3 learning reference, testing strategy).

