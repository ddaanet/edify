# Edify Rename Outline

## Approach

Sequential execution of three sub-problems targeting two naming identities:
- `agent-core` → `plugin` (submodule directory, ~1679 total references)
- `claudeutils` → `edify` (Python package + CLI command, ~817+ references in src/tests alone)

Each SP produces atomic commits satisfying C-2. Full-tree grep discovery (C-3) for all reference updates.

## Key Decisions

**D-1: Sequential execution, not parallel.**
SP-1 modifies files inside `src/claudeutils/` (agent-core path strings). SP-2 moves `src/claudeutils/` → `src/edify/`. Parallel worktrees cause merge conflicts (modify vs move on same files). Sequential eliminates this.

**D-2: SP-1 before SP-2.**
Submodule rename doesn't move files (simpler). Python rename moves every `src/` file. Start with the simpler structural change so SP-2 operates on post-SP-1 state cleanly.

**D-3: Atomic commits per SP.**
All reference updates in one commit per SP. No transition shims. Working tree may be inconsistent mid-SP; commit boundaries are clean.

**D-4: Submodule two-commit pattern.**
SP-1 requires: (1) submodule internal commit (update self-references inside agent-core), (2) parent repo commit (directory rename + external references + new submodule pointer). Transient inconsistency between commits resolved by parent commit.

**D-5: No Python namespace shim.**
`src/claudeutils/` → `src/edify/` via `git mv` + import rewrite in same commit. Clean break, no compatibility layer.

**D-6: In-tree execution.**
User opted for in-tree over worktree.

## Sub-Problems

### SP-1: Submodule Rename (agent-core → plugin)

**FRs:** FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8
**Readiness:** Ready for /runbook
**Routing:** /runbook (general phases)
**Dependency:** SP-3 complete (plan cleanup removes delivered plans first)

**Commit 1 — submodule internal** (inside agent-core/):
- Update all `agent-core/` self-references to `plugin/`
- Measured: 49 files with `agent-core` references inside submodule
- Targets: `@agent-core/fragments/`, `@agent-core/skills/`, cross-references in skills/fragments/agents
- Also update `claudeutils` CLI command refs → `edify` (53 files) — do both identities in submodule at once to avoid re-traversal
- Commit in submodule repo

**Commit 2 — parent repo** (atomic):
- `git mv agent-core plugin`
- Update `.gitmodules`: submodule name (`[submodule "agent-core"]` → `[submodule "plugin"]`), URL → `ddaanet/edify-plugin.git`
- `git submodule sync`
- Full-tree grep for remaining `agent-core` → update all matches
- Fix `.envrc` symlink target (`agent-core/templates/dotenvrc` → `plugin/templates/dotenvrc`)
- `just test` verification
- Verification grep: zero `agent-core` matches outside plans/edify-rename/

**Measured reference counts (parent repo, excluding submodule):**
- src/*.py: 39
- tests/*.py: 172
- Config (CLAUDE.md, pyproject.toml, justfile, settings.json, rules): ~31
- plans/ (active): ~50-100

### SP-2: Python/CLI Rename (claudeutils → edify)

**FRs:** FR-9a, FR-9b, FR-9d
**Readiness:** Ready for /runbook (after SP-1)
**Routing:** /runbook (general phases)
**Dependency:** SP-1 complete

**Single commit** (atomic):
- `git mv src/claudeutils src/edify`
- Update all Python imports: `from claudeutils.` → `from edify.`, `import claudeutils` → `import edify`
- Update pyproject.toml: name, entry points (`edify = "edify.cli:main"`), URLs
- Update CLI command references in agentic prose: `claudeutils _recall` → `edify _recall` etc.
- Update `.claude/rules/*.md` boundary definitions (FR-9d)
- Update `sessionstart-health.sh` install target
- Update README.md
- Reinstall package: `uv pip install -e .`
- `just test` verification
- Verification grep: zero `claudeutils` matches outside plans/edify-rename/

**Measured reference counts:**
- src/*.py: 174
- tests/*.py: 643
- plugin/ (submodule, post-SP-1): handled in SP-1 commit 1
- Config + README: ~10-20
- plans/ (active): ~20-40

**Note:** SP-1 commit 1 handles `claudeutils` → `edify` inside the submodule. SP-2 handles the rest of the tree.

### SP-3: Plan Cleanup (FR-10)

**FRs:** FR-10
**Readiness:** Ready for /inline
**Routing:** /inline (mechanical enumerate-archive-delete)
**Dependency:** Prerequisite for SP-1 (fewer files to rename, tighter verification grep)

**Scope:**
- Enumerate all plan directories with `delivered` status via planstate
- For each: read outline/design, write archive entry in `agents/plan-archive.md`
- Delete plan directory
- Exception: keep `plans/retrospective/`
- Pre-check: verify `remove-fuzzy-recall` planstate discrepancy (Q-4)

### External Actions (Human)

Not agent-executable. Tracked outside sub-problems.

- **FR-1:** GitHub rename ddaanet/agent-core → ddaanet/edify-plugin — before SP-1 (nice-to-have; GitHub redirects cover delay)
- **FR-12:** GitHub rename ddaanet/claudeutils → ddaanet/edify — before SP-2 (same)
- **FR-13:** PEP 541 claim for `edify` on PyPI — parallel, non-blocking
- **FR-9c:** Update PyPI package name — after FR-13 approval
- **FR-11:** Marketplace publishing — after SP-1 + SP-2 + FR-9c
- **C-5:** Rename ~/code/claudeutils → ~/code/edify — between sessions, after all SPs

## Dependency Graph

```
SP-3 (plan cleanup) ──→ SP-1 (submodule) ──→ SP-2 (package) ──→ FR-11 (marketplace)
                                                                     ↑
                        FR-13 (PEP 541) ──→ FR-9c (PyPI name) ─────┘
```

**Absent edges:**
- FR-1/FR-12 ↔ SP-1/SP-2: soft only (GitHub redirects)

## Completeness

- **FR-1:** External (human)
- **FR-2:** SP-1
- **FR-3:** SP-1
- **FR-4:** SP-1
- **FR-5:** SP-1
- **FR-6:** SP-1
- **FR-7:** SP-1
- **FR-8:** SP-1
- **FR-9a:** SP-2
- **FR-9b:** SP-1 (submodule) + SP-2 (rest of tree)
- **FR-9c:** External (FR-13 dependent)
- **FR-9d:** SP-2
- **FR-10:** SP-3
- **FR-11:** External (terminal)
- **FR-12:** External (human)
- **FR-13:** External (human)

## Scope Boundaries

**IN:** SP-1, SP-2, SP-3 as specified above
**OUT:**
- Fragment behavioral content changes (path refs only, not rules)
- New skill logic or workflow redesign
- CLI restructuring (bin/ → edify subcommands)
- Consumer mode ($EDIFY_PLUGIN_ROOT resolution)
- Local directory rename (C-5, between sessions)

## Risks

- **R-1:** Grep misses non-standard patterns (f-strings, string concatenation). Mitigation: post-rename verification grep confirms zero remaining matches.
- **R-2:** Submodule commit 1 creates transient inconsistency (refs say `plugin/` but dir is `agent-core/`). Mitigation: parent commit follows immediately; CI only runs on parent commits.
- **R-3:** `git mv` for submodule may interact with core.worktree config. Mitigation: recall entry "when recovering broken submodule worktree refs" documents repair.
- **R-4:** Requirements undercount. Measured tests/agent-core (172) exceeds FR-6 estimate (106). Full-tree grep discovery (C-3) catches all regardless of estimate accuracy.
