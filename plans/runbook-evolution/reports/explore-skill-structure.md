# Runbook SKILL.md Structure and Generation Directives

**Exploration Date:** 2026-02-17

**Scope:** Complete structural analysis of runbook SKILL.md and related guidance files for understanding current generation directives, testing strategy, prose handling, and self-modification patterns.

---

## Summary

The runbook SKILL.md (913 lines) is a comprehensive skill for creating execution runbooks with per-phase typing (TDD or general). It includes a three-tier complexity assessment, multi-phase planning process (Phases 0.5–4), per-phase expansion with per-type review, and comprehensive guidance on model selection, testing, and prose handling. The skill includes specific directives for handling artifacts (especially skills/fragments/agents requiring opus model) and references five supporting pattern/reference documents. Testing guidance emphasizes behavioral verification in RED phases, prose descriptions without prescriptive code in GREEN phases, and integration testing for composition tasks.

---

## Key Findings

### 1. Runbook SKILL.md Structure

**File:** `/Users/david/code/claudeutils-wt/design-workwoods/agent-core/skills/runbook/SKILL.md`

**Size:** 913 lines, 4 major sections

#### Section Structure with Line Ranges

| Section | Start | End | Purpose |
|---------|-------|-----|---------|
| Frontmatter | 1 | 16 | Metadata (name, model: sonnet, allowed-tools, requires) |
| Skill title & context | 18 | 25 | Brief description and workflow integration |
| **Per-Phase Type Model** | 26 | 48 | Type tagging (TDD vs general), how types determine expansion |
| **Model Assignment** | 49 | 65 | Default heuristics + artifact-type override (skills/fragments/agents/workflow-*.md → opus) |
| When to Use | 68 | 82 | Use cases and anti-patterns |
| **Three-Tier Assessment** | 85 | 175 | Tier 1/2/3 complexity evaluation, criteria, and sequences |
| Tier 1 (Direct Implementation) | 108 | 122 | Simple tasks: implement directly, vet, handoff |
| Tier 2 (Lightweight Delegation) | 123 | 163 | Moderate scope: delegate via Task without full runbook; design constraints non-negotiable |
| Tier 3 (Full Runbook) | 164 | 175 | Complex: full planning process with phases |
| **Planning Process (Tier 3)** | 178 | 194 | Phase overview (0.5–4) and process flow |
| Phase 0.5 (Discover Codebase) | 196 | 227 | Read docs, verify files via Glob/Grep, load memory-index context |
| Phase 0.75 (Generate Outline) | 229 | 273 | Create runbook-outline.md with requirements mapping, phase structure, quality verification, outline review |
| Phase 0.85 (Consolidation — Outline) | 276 | 311 | Merge trivial phases with adjacent complexity before expansion |
| Phase 0.86 (Simplification Pass) | 314 | 340 | Mandatory simplification gate: detect and consolidate redundant patterns |
| Phase 0.9 (Complexity Check) | 343 | 378 | Gate expensive expansion with callback mechanism (triggers, levels, restart points) |
| Phase 0.95 (Outline Sufficiency Check) | 380 | 411 | Skip expansion if outline sufficiently detailed; promote to runbook or proceed to Phase 1 |
| Phase 1 (Phase-by-Phase Expansion) | 414 | 470 | Per-phase expansion based on type (TDD → cycles, general → steps), reviews, domain validation |
| TDD Cycle Planning Guidance | 472 | 567 | Detailed cycle structure: numbering (X.Y), RED/GREEN prose specs, investigation prerequisites, dependencies, stop conditions, conformance validation |
| Phase 2 (Assembly & Metadata) | 570 | 625 | Pre-assembly validation, metadata prep, consistency checks, Weak Orchestrator Metadata section |
| Phase 2.5 (Consolidation — Runbook) | 627 | 651 | Merge isolated trivial items after assembly |
| Phase 3 (Final Holistic Review) | 654 | 677 | Cross-phase review by plan-reviewer (fix-all mode) |
| Phase 3.5 (Pre-Execution Validation) | 680 | 712 | Mandatory structural validation via validate-runbook.py (model-tags, lifecycle, test-counts, red-plausibility) |
| Phase 4 (Prepare Artifacts & Handoff) | 715 | 742 | Run prepare-runbook.py, copy orchestrate command, tail-call /handoff --commit |
| **Checkpoints** | 745 | 777 | Light (Fix + Functional) and full (Fix + Vet + Functional) checkpoints with integration test pattern |
| What NOT to Test | 779 | 791 | Behavior yes, presentation no (exceptions: regulatory, complex generated, machine-parsed) |
| Cycle/Step Ordering Guidance | 794 | 807 | TDD foundation-first ordering; general dependency ordering; references to references/*.md |
| Common Pitfalls | 810 | 831 | 12 avoidable pitfalls and corrective patterns |
| Runbook Template Structure | 834 | 888 | YAML frontmatter, Weak Orchestrator Metadata, Common Context, cycle/step sections |
| References | 891 | 899 | Links to 6 pattern/reference documents and pipeline-contracts.md |
| Integration & Workflow | 902 | 913 | Full workflow pipeline: /design → /runbook → plan-reviewer → prepare-runbook.py → /orchestrate |

#### Frontmatter (Lines 1–16)

```yaml
name: runbook
model: sonnet
allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, agent-core/bin/prepare-runbook.py, echo:*|pbcopy)
requires:
  - Design document from /design
  - CLAUDE.md for project conventions (if exists)
outputs:
  - plans/<job-name>/runbook.md
user-invocable: true
```

**Key directive:** allowed-tools include prepare-runbook.py and mkdir:*, reflecting the skill's responsibility for creating plan directories.

---

### 2. Testing Guidance in SKILL.md

**Location:** Scattered across TDD Cycle Planning Guidance (lines 472–567) and "What NOT to Test" (lines 779–791).

#### TDD RED Phase Assertions (Lines 499–511)

- **Format:** Prose descriptions, NOT full code blocks
- **Quality rule:** Specific not vague ("returns string containing 🥈 emoji" not "returns correct value")
- **Validation:** Assertions must distinguish correct output from empty/default output
- **Behavioral focus:** Mock file I/O, verify reads/writes to actual paths; verify correct invocation of external calls; assert output content, not just success/failure

#### TDD GREEN Phase Guidance (Lines 513–535)

- **CRITICAL directive:** "No prescriptive code" — GREEN describes BEHAVIOR and provides HINTS, NOT complete function implementations
- **Format:** Behavior (WHAT) / Approach (HOW hint) / Changes (file, action, location)
- **Purpose:** Enforce TDD discipline — executor writes code, not transcribes

#### Investigation Prerequisites (Lines 536–538)

- **Transformation cycles** (delete, move, rename): self-contained, no prerequisite needed
- **Creation cycles** (new test, new integration, touching existing): MUST include `**Prerequisite:** Read [file:lines] — understand [behavior/flow]`

#### Conformance Validation (Lines 555–567, references testing.md)

- **Trigger:** Design includes external reference (shell prototype, API spec) in `Reference:` field
- **Requirement:** Runbook MUST include validation items with exact expected strings from reference
- **Exception to prose rule:** Conformance prose MUST include exact expected strings (e.g., `🥈 sonnet \033[35m…`) — not abstracted

#### What NOT to Test (Lines 779–791)

| Category | Skip | Test Instead |
|----------|------|--------------|
| CLI help text | Exact phrasing | Command parses, options work |
| Error messages | Exact wording | Error raised, exit code, error type |
| Log output | Format, phrasing | Logged events occur, data captured |
| Documentation | Generated content | Generation process works |

**Exception clause:** Regulatory requirements, complex generated content, machine-parsed output.

---

### 3. Prose Handling Directives in SKILL.md

#### Prose-Only Phases (General Phases, Lines 437–443)

- **Script Evaluation:** Classify task by size (small ≤25 lines inline, medium 25-100 prose, large >100 separate planning)
- **Prerequisite pattern:** `**Prerequisite:** Read [file:lines] — understand [behavior/flow]`
- **Step structure:** Objective, Implementation, Expected Outcome, Error Conditions, Validation

#### Common Context Section (Lines 856–869)

Runbooks include explicit "Common Context" section with:
- Requirements mapping (FR-N → implementation element)
- Scope boundaries (in/out)
- Key Constraints
- Project Paths
- Design reference

#### RED Phase Prose Format (Lines 483–497)

```markdown
**RED Phase:**
**Test:** [test function name]
**Assertions:**
- [Specific assertion 1 — behavioral, not structural]
**Expected failure:** [Error type or pattern]
**Why it fails:** [Missing implementation]
**Verify RED:** `pytest [file]::[test_function] -v`
```

**Rule:** Prose not code — saves ~80% planning tokens (per workflow-advanced.md line 215).

#### Artifact-Type Prose Override (Lines 49–65, Model Assignment)

**Skills, fragments, agents, workflow-*.md files require OPUS regardless of task complexity:**
- "These are prose instructions consumed by LLMs — wording directly determines downstream agent behavior"
- "Simple" edits to these files require nuanced understanding that haiku/sonnet cannot reliably provide
- Applies to Tier 2 delegation (model parameter), Tier 3 step assignment, and Execution Model in Weak Orchestrator Metadata

---

### 4. Self-Modification Directives

#### Bootstrapping Self-Referential Improvements (workflow-advanced.md, lines 319–327)

**Decision Date:** 2026-02-15

**Pattern:** When improving tools/agents, apply each improvement BEFORE using that tool in subsequent steps.

**Key insight:** "Unimproved agents reviewing their own improvements creates a bootstrapping problem."

**Example:** If runbook skill is being improved, apply the improvement in Phase 1, then use the improved skill in Phase 2+.

**Rationale:** Phase ordering follows tool-usage dependency graph, not logical grouping. Collapses design→plan→execute into design→apply for prose-edit work.

#### Domain Validation Skill Integration (Lines 455–463)

When writing vet checkpoint steps, check if domain validation skill exists at `agent-core/skills/<domain>-validation/SKILL.md`. If found, include domain validation in vet step:

```markdown
- **Domain validation:** Read and apply criteria from
  `agent-core/skills/<domain>-validation/SKILL.md`
  for artifact type: [skills|agents|hooks|commands|plugin-structure]
```

**This is infrastructure evolution:** The skill enables planning infrastructure to evolve by detecting new domain-validation skills and incorporating them into vet steps without changing the base runbook skill.

#### Prepare-Runbook.py Automation (Phase 4, lines 715–742)

- **Mandatory:** Must run prepare-runbook.py to create execution artifacts
- **Reason:** Context isolation for weak orchestrator
- **Creates:** .claude/agents/[plan-name]-task.md agent definition
- **Requires:** Sandbox bypass (dangerouslyDisableSandbox: true)
- **Next:** Tail-call /handoff --commit

**This is orchestration automation:** The script auto-detects phase structure from runbook (TDD vs general by header format), generates cycle/step divisions, and creates plan-specific agent.

---

### 5. Referenced Files and Pattern Documents

**Location:** Lines 891–899, References section

#### Core Pattern Documents

| File | Lines | Purpose |
|------|-------|---------|
| `references/patterns.md` | 1–100+ | TDD granularity criteria, numbering (X.Y), dependencies, stop conditions |
| `references/general-patterns.md` | 1–100+ | General-step granularity, prerequisite validation, step structure template |
| `references/anti-patterns.md` | (exists) | Patterns to avoid with corrections |
| `references/error-handling.md` | (exists) | Error catalog, edge cases, recovery protocols |
| `references/examples.md` | (exists) | Complete runbook examples (TDD and general) |

#### External References

- **agents/decisions/pipeline-contracts.md** — I/O contracts for pipeline transformations, artifact routing, vet scopes
- **agents/decisions/testing.md** — Testing conventions including "When Preferring E2E Over Mocked Subprocess" (line 166)
- **agents/decisions/workflow-advanced.md** — Advanced patterns including "When Bootstrapping Self-Referential Improvements" (line 319)

#### Model Assignment Override Pattern

Lines 49–65 document the artifact-type override: Skills, fragments, agents, and workflow-*.md files MUST be edited by opus regardless of task complexity. This override cascades through:
- Tier 2 delegation (Task model parameter)
- Tier 3 step assignment (Execution Model field)
- Weak Orchestrator Metadata

---

### 6. Testing Strategy From Referenced Decisions Files

#### When Preferring E2E Over Mocked Subprocess (testing.md, line 166–176)

**Decision Date:** 2026-02-12

- **Pattern:** E2E only with real git repos (tmp_path fixtures), mocking only for error injection
- **Rationale:** Git with tmp_path is fast (milliseconds), subprocess mocks are implementation-coupled, interesting bugs are state transitions mocks can't catch
- **Exception:** Mock subprocess for error injection only (lock files, permission errors)

**Implication for runbooks:** TDD phases should use e2e-style tests with real filesystem state rather than subprocess mocks when testing git-related behavior.

#### When Bootstrapping Self-Referential Improvements (workflow-advanced.md, line 319–327)

**Decision Date:** 2026-02-15

- **Pattern:** When improving tools/agents, apply each improvement BEFORE using that tool in subsequent steps
- **Root cause:** "Unimproved agents reviewing their own improvements creates a bootstrapping problem"
- **Solution:** Phase ordering follows tool-usage dependency graph

**Implication for runbooks:** If the runbook skill itself is being evolved (prose directives changed, new phases added), test those changes within a runbook that uses the improved version. Requires careful phase sequencing to avoid circular dependencies.

---

### 7. Prose Atomicity and Discipline Patterns

#### Red Phase Prose Atomicity (Lines 499–511)

Each RED assertion must be:
- Specific: exact values, patterns, or behaviors
- Behavioral: not structural checks (not just "method exists")
- Falsifiable: distinguishes correct from empty/default output
- Independent: testable in isolation

**Example strong assertion:** "output dict contains 'count' key with integer > 0"
**Example weak assertion:** "processes input correctly"

#### Green Phase Behavioral Specification (Lines 513–535)

GREEN does NOT prescribe code. Instead:

1. **What (Behavior):** What the code must DO
2. **Hint (Approach):** Brief hint about algorithm/strategy
3. **Location:** File path and location hint for changes

**CRITICAL directive:** "Do NOT include complete function implementations or code blocks that can be copied verbatim."

**Rationale:** TDD discipline requires executor to WRITE code satisfying tests, not transcribe prescribed code.

#### Conformance Exception (Lines 555–567, references testing.md)

For implementation with external reference (shell prototype, API spec, visual mockup, exact output format):

- Standard prose: "Assert output contains formatted model with emoji and color"
- Conformance prose: "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator"

**Key distinction:** Conformance prose includes exact expected strings from the reference. This is NOT full test code — it is precise prose that preserves specification fidelity while maintaining token efficiency.

---

### 8. Phase Boundaries and Checkpoints

#### Light Checkpoint (Lines 751–759)

**Placement:** Every phase boundary

1. **Fix:** Run `just dev`, sonnet quiet-task diagnoses and fixes, commit when passing
2. **Functional:** Sonnet reviews implementations against design (stubs vs real implementations)

#### Full Checkpoint (Lines 760–765)

**Placement:** Final phase boundary, or phases marked `checkpoint: full`

1. **Fix:** Run `just dev`, sonnet fixes, commit when passing
2. **Vet:** Sonnet reviews accumulated changes (presentation, clarity, alignment)
3. **Functional:** Same as light checkpoint

#### Integration Test Pattern (Lines 767–770)

For TDD composition tasks:
- **Phase start:** xfail integration test calling top-level entry point
- **Phase end:** Remove xfail, verify passes
- **Purpose:** Catches gaps unit tests miss (results consumed, not just functions called)

#### When to Mark `checkpoint: full` (Lines 772–775)

- Phase introduces new public API surface
- Phase crosses module boundaries (3+ packages)
- Runbook exceeds 20 items total

---

### 9. Model Selection Framework

#### Default Heuristic (Lines 51–54)

| Model | Use Case |
|-------|----------|
| Haiku | File operations, scripted tasks, mechanical edits |
| Sonnet | Semantic analysis, judgment, standard implementation |
| Opus | Architecture, complex design decisions |

#### Artifact-Type Override (Lines 56–62)

**Files requiring opus regardless of task complexity:**
- Skills (`agent-core/skills/`)
- Fragments (`agent-core/fragments/`)
- Agent definitions (`agent-core/agents/`)
- Workflow decisions (`agents/decisions/workflow-*.md`)

**Justification:** "These are prose instructions consumed by LLMs — wording directly determines downstream agent behavior."

#### Where Override Applies (Lines 64)

- Tier 2 delegation (model parameter in Task call)
- Tier 3 step assignment (Execution Model field in phase)
- Weak Orchestrator Metadata (Execution Model for general phases)

---

### 10. Critical Infrastructure Directives

#### Phase 0.5 Discovery Requirements (Lines 196–227)

**Mandatory before any runbook content:**

1. **Read documentation perimeter** (if present in design):
   - Read all files under "Required reading"
   - Note Context7 references
   - Invoke skill-loading directives if present
   - Factor into step design

2. **Discover relevant prior knowledge:**
   - Check loaded memory-index context (already in CLAUDE.md)
   - Read referenced files when relevant
   - Factor known constraints into step design

3. **Verify file locations via Glob/Grep:**
   - NEVER assume from conventions alone
   - Use Glob to find source files
   - Use Glob to find test files
   - Use Grep to find functions/classes
   - STOP if expected files not found

#### Phase 0.75 Outline Quality Verification (Lines 244–253)

Seven explicit quality checks before review:

1. All implementation choices resolved (no "choose between" language)
2. Inter-item dependencies declared
3. Code fix items enumerate affected sites
4. Later items reference post-phase state
5. Phases ≤8 items each
6. Cross-cutting issues scope-bounded
7. No vacuous items (every item produces functional outcome)

**Commit before review:** "Review agents operate on filesystem state — committed state prevents dirty-tree issues"

#### Phase 3.5 Mandatory Validation (Lines 684–712)

**Mandatory for all Tier 3 runbooks.**

Four validation subcommands via validate-runbook.py:
1. **model-tags:** Artifact-type files must have opus tag
2. **lifecycle:** Create→modify dependency graph (flags violations)
3. **test-counts:** Checkpoint "All N tests pass" vs actual test function count
4. **red-plausibility:** Prior GREENs vs RED expectations (flags already-passing states)

**Graceful degradation:** If validate-runbook.py doesn't exist, skip Phase 3.5 with warning (supports incremental adoption).

#### Phase 4 Mandatory Prepare-Runbook.py (Lines 715–742)

**CRITICAL: MANDATORY step.**

1. Run prepare-runbook.py (requires sandbox bypass)
2. Copy orchestrate command to clipboard
3. Tail-call `/handoff --commit`

**Why:** Context isolation for weak orchestrator. Each step gets fresh agent with ONLY common context and specific step — no accumulated transcript.

**Auto-detection:** prepare-runbook.py auto-detects phase structure from runbook (TDD vs general by header format).

---

### 11. Design Constraints Enforcement (Tier 2, Lines 145–151)

**Non-negotiable directive:**

When design specifies explicit classifications (tables, rules, decision lists):

1. Include them LITERALLY in delegation prompt
2. Delegated agents must NOT invent alternative heuristics
3. Agent "judgment" means applying design rules to specific cases, not creating new rules

**Handling escalations:** If delegated agent escalates "ambiguity":
1. Verify against design source
2. If design provides explicit rules: resolve using those rules
3. If genuinely ambiguous: use /opus-design-question or ask user
4. Re-delegate with clarification if agent misread design

---

## Patterns and Conventions

### Naming Conventions

| Item | Format | Example |
|------|--------|---------|
| TDD cycles | X.Y | 1.1, 1.2, 2.1 |
| General steps | N.M | 1.1, 2.5 |
| Phases | Phase N | Phase 1, Phase 2 |
| Plan directories | plans/{job-name}/ | plans/runbook-evolution/ |
| Phase files | runbook-phase-N.md | runbook-phase-1.md |
| Review reports | {type}-review{-N}.md | outline-review.md, phase-1-review.md |
| Outline file | runbook-outline.md | (single file per plan) |
| Final runbook | runbook.md | (single file per plan) |

### Phase Ordering (Tier 3)

```
0.5: Discover Codebase Structure (REQUIRED)
0.75: Generate Runbook Outline
0.85: Consolidation Gate — Outline
0.86: Simplification Pass (MANDATORY)
0.9: Complexity Check Before Expansion
0.95: Outline Sufficiency Check
1: Phase-by-Phase Expansion (conditional)
2: Assembly and Metadata
2.5: Consolidation Gate — Runbook
3: Final Holistic Review
3.5: Pre-Execution Validation (MANDATORY)
4: Prepare Artifacts and Handoff
```

**MANDATORY phases:** 0.5, 0.86, 3.5, 4

---

## Architecture and Data Flow

### Three-Tier Assessment Routing

```
Input: Design document
  ↓
Tier Assessment (Phase 0)
  ↓
  ├─ Tier 1: Files <6, scope <100 lines → Direct Implementation
  │   └─ Implement → Vet → Handoff
  ├─ Tier 2: Files 6-15, moderate scope → Lightweight Delegation
  │   └─ Task delegation → Vet → Handoff
  └─ Tier 3: Files >15, complex scope → Full Runbook
      └─ Planning (Phases 0.5-4) → Orchestration
```

### Per-Phase Type Model

| Phase Type | Expansion Format | Review Criteria | Assembly |
|-----------|------------------|-----------------|----------|
| TDD | RED/GREEN cycles (X.Y) | TDD discipline + LLM failure modes | Auto-detect by `## Cycle X.Y:` header |
| General | Task steps (N.M) | Step quality + LLM failure modes | Auto-detect by `## Step N.M:` header |

**Key:** prepare-runbook.py auto-detects from headers; type tag in outline is for planning/review context.

### Model Selection Cascade

```
Default heuristic (complexity-based)
  ├─ Haiku: mechanical tasks
  ├─ Sonnet: semantic analysis
  └─ Opus: architecture

OVERRIDE for artifact types:
  ├─ Skills → Opus
  ├─ Fragments → Opus
  ├─ Agents → Opus
  └─ Workflow decisions → Opus
```

Applied at three levels:
1. Tier 2 Task(model=...) parameter
2. Tier 3 "Execution Model" field in phase
3. Weak Orchestrator Metadata section

---

## Critical Gaps and Open Questions

### 1. Prose Atomicity Enforcement

**Issue:** The skill describes prose atomicity rules (specific assertions, conformance strings) but doesn't specify WHO verifies prose quality during phase expansion.

**Current state:** plan-reviewer applies per-phase type review (line 449–450), but unclear if plan-reviewer validates prose specificity against testing.md standards.

**Question:** Does plan-reviewer check "assertion quality" (specific vs vague) or only "presence of assertions"?

### 2. Self-Modification Bootstrap Protocol

**Issue:** workflow-advanced.md (line 319–327) states tool improvements must precede tool usage in subsequent phases, but SKILL.md doesn't specify the protocol for evolving the runbook skill itself.

**Current state:** Runbook skill improvements would need to be applied in Phase 0.75–0.9, then used in Phase 1+. No explicit guidance on phase ordering for skill-improvement runbooks.

**Question:** If the runbook skill evolves, what phase order prevents circular dependencies (Phase 1 expansion using improved skill vs Phase 0.75 outline generation)?

### 3. Domain Validation Skill Auto-Discovery

**Issue:** Phase 1 (line 455–463) references checking for domain-validation skills but doesn't specify the discovery mechanism.

**Current state:** "Check if domain validation skill exists at `agent-core/skills/<domain>-validation/SKILL.md`" — implies manual check, not automated Glob.

**Question:** Should this be automated via Phase 0.5 discovery (Glob for domain-validation skills) or left as planner judgment during Phase 1?

### 4. Validate-Runbook.py Dependency

**Issue:** Phase 3.5 (line 680–712) marks validation as MANDATORY but includes graceful degradation: "If validate-runbook.py doesn't exist, skip Phase 3.5 with warning."

**Current state:** The script may not exist yet. No guidance on interim runbooks before script exists.

**Question:** Should Phase 3.5 be conditional (run if script exists) or should script creation be a prerequisite before runbook skill is used for complex runbooks?

### 5. Conformance Prose Exception Scope

**Issue:** Testing.md and SKILL.md define conformance prose exception (include exact expected strings) but scope is unclear.

**Current state:** Triggered by design.Reference field, but undefined what counts as "external reference" (shell prototype, API spec, visual mockup all listed).

**Question:** Are structured specifications (e.g., RFC, JSON schema) also external references, or only visual/executable prototypes?

### 6. Artifact Override Scope

**Issue:** Lines 56–62 list skills, fragments, agents, workflow-*.md as requiring opus, but unclear if subdirectories count.

**Current state:** `agents/decisions/workflow-*.md` is explicit, but what about `agents/rules/*.md` or future subdirectories?

**Question:** Should the rule be "any file with 'workflow-' in name" or "any file in agents/decisions/ directory"?

---

## Glossary

| Term | Definition |
|------|-----------|
| **Phase Type** | `tdd` or `general` — determines expansion format and review criteria |
| **Cycle** | TDD unit of work (X.Y numbering) with RED/GREEN phases |
| **Step** | General unit of work (N.M numbering) with objective/implementation/validation |
| **RED Phase** | Test specification (prose assertions, expected failure) |
| **GREEN Phase** | Implementation specification (behavior + hints, not prescriptive code) |
| **Prerequisite** | Investigation gate before creation steps (read existing patterns, discover affected files) |
| **Artifact-type override** | Model selection rule that forces opus for skills/fragments/agents/workflow-*.md |
| **Conformance validation** | Verification that implementation matches external reference (exact strings required) |
| **Weak Orchestrator Metadata** | Runbook section with coordination info for orchestrator (model assignment, dependencies, error escalation) |
| **Prepare-runbook.py** | Script that auto-detects phase structure, generates agent definition, creates orchestration artifacts |
| **Plan-reviewer** | Agent that reviews runbooks with type-aware criteria (TDD discipline, step quality, LLM failure modes) |

---

## References

**Runbook SKILL.md sections:**
- Lines 49–65: Model Assignment with artifact-type override
- Lines 196–227: Phase 0.5 Discovery Requirements
- Lines 472–567: TDD Cycle Planning Guidance with prose rules
- Lines 655–677: Phase 3 Holistic Review scope
- Lines 684–712: Phase 3.5 Validation checks
- Lines 715–742: Phase 4 Prepare-runbook.py requirements
- Lines 779–791: What NOT to Test with exceptions

**External referenced files:**
- `agents/decisions/testing.md` — Testing conventions (line 166: E2E vs mocks)
- `agents/decisions/workflow-advanced.md` — Advanced patterns (line 319: bootstrapping self-referential improvements)
- `agent-core/skills/runbook/references/*.md` — Pattern documents (5 files)
- `agents/decisions/pipeline-contracts.md` — I/O contracts for pipeline

