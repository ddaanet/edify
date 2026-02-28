# Defense-in-Depth Pattern

## When Designing Quality Gates

**Decision Date:** 2026-02-08

**Decision:** Quality gates should be layered with multiple independent checks to prevent single-point failures. No single gate should be trusted as the sole enforcement mechanism.

**Rationale:**

The statusline-parity RCA documented a cascade of failures where each quality gate—in isolation—passed successfully, yet the combined system failed to catch conformance issues (RC1), test scope limitations (RC2), and file size violations (RC3). This pattern reveals a fundamental design principle: single-layer validation is insufficient for complex work. Multiple, independent defense layers operating on different failure modes are required.

The parity iterations demonstrated:
- **Unit tests passed** (385/385) yet 8 visual parity issues remained undetected because tests verified data flow, not presentation against specification
- **Vet agent reviewed code quality** yet missed systemic conformance gaps because the review mandate did not include external reference comparison
- **File size constraint existed** (400-line limit) yet was either skipped or ignored before commit, requiring retroactive file splits

Each layer failed independently and only by combining them do we achieve adequate coverage.

**Pattern layers (from outer to inner):**

1. **Layer 1 — Outer defense (Execution Flow):** D+B hybrid (merge prose gates with adjacent action steps, anchor with tool call) ensures precommit appears in execution path and is actually executed
   - Prevents: Prose-only validation steps getting optimized/skipped in execution mode
   - Example: Commit skill Step 1 now opens with Read(session.md), not a prose judgment

2. **Layer 2 — Middle defense (Automated Checks):** Precommit catches line limits, lint, test failures via hard validation at commit time
   - Prevents: Oversized files, style violations, broken tests from being committed
   - Mechanism: `just precommit` runs `check_line_limits.sh`, linters, and test suite
   - Execution: Runs always unless in WIP-only modes (see Inner defense)

3. **Layer 3 — Inner defense (Quality Review):** Vet-fix-agent catches quality, alignment, and implementation issues through semantic review before commit
   - Prevents: Logic errors, integration problems, deviations from design
   - Scope: Full alignment verification (output matches design/requirements/acceptance criteria)
   - Note: Only as good as acceptance criteria specification — requires precise test descriptions for conformance work

4. **Layer 4 — Deepest defense (Conformance):** Conformance tests and reference validation catch spec-to-implementation drift
   - Prevents: Implementation that passes all automated checks yet diverges from specification
   - Mechanism: For work with external references (shell scripts, visual mockups, API specs), compare rendered output/behavior directly
   - Example: Conformance validation comparing Python statusline output to shell reference at `scratch/home/claude/statusline-command.sh` would have caught all 8 parity issues immediately

**Gap 3 + Gap 5 interaction:**

These two gaps interact to create a vulnerability:

- **Gap 3 (Prose gates skipping):** Without D+B hybrid fix, prose-only steps (like "run precommit as a judgment") get optimized past in execution mode, leading to the check not running at all.

- **Gap 5 (WIP-only bypass):** The commit skill supports `--test` and `--lint` modes which provide legitimate within-path bypasses of line limits, intended for TDD WIP commits. WIP-only means TDD GREEN phase commits only, before lint/complexity fixes. All other commits must use full `just precommit`. Without this scope restriction, these modes could be misused to bypass validation on final commits.

**Defense-in-depth closes this interaction:**

- **D+B (Outer defense)** ensures precommit runs (fixes Gap 3)
- **WIP-only restriction (Inner defense)** ensures `--test`/`--lint` modes are limited to work-in-progress commits, not final commits (fixes Gap 5)
- **Together:** Even if one layer is partially weak, the others compensate

Example scenario: If an agent were to use `--test` mode on what it perceives as "test-only" work, the outer D+B gate ensures the file size check still runs (because `just precommit` is invoked as a tool call, not skipped as prose). If D+B were not in place, the check could be skipped entirely.

**Example application:**

The statusline-parity failure cascade demonstrates each layer's necessity:

1. **Without outer defense (D+B):** Iteration 3 (aca8371) exceeded line limits and bypassed the precommit check via `--test` mode or prose skipping. The commit succeeded despite violation.

2. **Without middle defense (precommit):** Even with proper execution, files could be committed at any size.

3. **Without inner defense (vet alignment):** The Phase 4 checkpoint found one real issue (duplicate call) but missed the 8 parity issues because acceptance criteria were behavioral prose rather than exact expected strings. With stricter acceptance criteria (exact string matching from shell reference), alignment verification would catch output deviations.

4. **Without deepest defense (conformance):** Even with all three upstream layers perfect, the system could pass all tests and reviews yet still diverge from specification. The original statusline-wiring (Iteration 0) had 100% TDD compliance (28/28 RED-GREEN cycles), clean code, and passing tests—yet lacked all 13 visual indicators.

**Applicability:**

This pattern applies beyond parity tests—use for any quality gate design:
- When adding new quality mechanisms, consider which layer they belong to
- Multiple layers compensate for individual gate weaknesses (e.g., tests can pass but miss visual conformance; vet can review code but miss specification drift)
- No single layer is sufficient
- Each layer has a specific failure mode it prevents

**Related decisions:**

- **DD-1: Conformance tests mandatory for external references** — Deepest defense layer
- **DD-3: WIP-only restriction on `--test`/`--lint`** — Inner defense layer
- **DD-5: Vet alignment verification** — Inner defense layer
- **DD-6: Defense-in-depth pattern** — This decision (all four layers together)
- **Fix (Phase 1 Step 1): Commit skill WIP-only restriction** — Implements inner defense scoping
- **Fix (Phase 1 Step 2): D+B hybrid validation** — Implements outer defense execution flow

## When Placing Quality Gates

**Decision Date:** 2026-02-18

**Anti-pattern:** Ambient rules in always-loaded fragments telling agents to review artifacts. Unenforceable — agents rationalize skipping under momentum. Sub-agents don't see CLAUDE.md fragments at all.

**Correct pattern:** Gate at the chokepoint (commit). Scripted check (file classification + report existence) blocks mechanically. No judgment needed at the gate. Orchestrator handles mid-pipeline vet delegation separately.

**Rationale:** Ambient rules without enforcement are aspirational. Gating at commit captures all work. ~100 lines of always-loaded context eliminated for no behavioral loss.

## When Splitting Validation Into Mechanical And Semantic

**Decision Date:** 2026-02-18

**Anti-pattern:** Bundling deterministic checks (file path → model mapping) with judgment-based checks (task complexity assessment) in a single agent pass.

**Correct pattern:** Script handles deterministic checks (blocking, zero false positives). Agent enriches existing review for semantic checks (advisory). Different enforcement layers for different failure modes — defense-in-depth.

**Evidence:** FR-2 model review split. File path matching (agent-core/skills/ → opus) is scriptable with zero false positives. Semantic complexity ("is this synthesis?") requires runbook-corrector judgment during existing Phase 1 per-phase review.

## When Reviewing Quality Gate Coverage

When designing a new quality gate or quality process:

- [ ] Is there an outer execution-flow defense (gate runs via tool call, not prose)?
- [ ] Is there a middle automated-check defense (hard validation at commit/publish time)?
- [ ] Is there an inner semantic-review defense (expert review of alignment and quality)?
- [ ] For external reference work: Is there a deepest conformance defense (explicit comparison to reference)?
- [ ] Do layers have different failure modes (not redundant)?
- [ ] Can any single layer failure cause total system failure? (If yes, add another layer)

## When Fixing Behavioral Deviations Identified By RCA

**Decision Date:** 2026-02-25

**Anti-pattern:** Strengthening language ("no exceptions", "MUST", scenario-specific warnings) in rules the agent already saw and rationalized past. If the rule was clear and the agent overrode it, clarity wasn't the problem — the environment allowed the override.

**Correct pattern:** Structural fixes — resolve conflicting directives, anchor gates with tool calls (D+B), add environmental enforcement (hooks/scripts) with guidance, ensure sufficient context loaded at decision point. Fix the environment, not the prose.

**Evidence:** /reflect prescribed "no exceptions" language for design skill Simple gate after agent rationalized past existing clear behavioral-code rule. Same anti-pattern class as ambient rules without enforcement.

## .When Implementing Enforcement Gates

### When Anchoring Gates With Tool Calls

**Decision Date:** 2026-02-25

**Anti-pattern:** "Read X (skip if already in context)" as a gate. Agent rationalizes the skip condition without verifying — substitutes related activity for the required Read. The escape hatch IS the failure mode.

**Correct pattern:** Anchor with a tool call that proves work happened. `when-resolve.py` is the canonical gate anchor: it's a Bash call (unskippable), requires trigger knowledge (forces prior Read of memory-index), and produces output (proves resolution). One tool-call anchor is sufficient — passphrase/proof-of-Read mechanisms are redundant when the resolution tool proves both.

### When Selecting Gate Anchor Tools

**Decision Date:** 2026-02-26

**Anti-pattern:** Using a tool because it's "related" to the gate's domain without checking its preconditions match the gate's execution context. `_recall diff` uses `git log --since=mtime` — requires intervening commits. At a post-explore gate, exploration reports are uncommitted; the script finds nothing.

**Correct pattern:** Verify the tool's mechanism matches the gate's runtime state. The right anchor is the tool called on the positive path (`when-resolve.py`). Null mode (`when-resolve.py null`) provides the negative path at equal cost — silent exit 0, no output, proves gate was reached.

### When Gates Bypass Downstream Pipeline Stages

**Decision Date:** 2026-02-26

**Anti-pattern:** Direct execution gate checks coordination complexity but not capacity. Gate bypasses `/runbook` entirely — large-scope work routes to inline execution because it has "no coordination complexity."

**Correct pattern:** Gates that bypass downstream stages must union the criteria of all bypassed stages. Design's direct execution gate bypasses runbook tier assessment, so it must assess both coordination complexity (structurally simple?) and capacity (fits inline?).

### When Choosing Hook Enforcement Over Permission Deny

**Decision Date:** 2026-02-25

**Anti-pattern:** `"Bash(rm:*/index.lock)"` in permissions deny list. Never fires — rm runs within the sandbox without needing explicit permission, so the deny list is bypassed entirely.

**Correct pattern:** PreToolUse hook on Bash matcher with script that inspects `tool_input.command`. Hook fires unconditionally before execution, independent of sandbox/permission state.

### When Implementing Pre-Delegation Gates

**Decision Date:** 2026-02-26

**Anti-pattern:** PreToolUse hook on Task tool with exit 0 + additionalContext advisory. No model re-run between PreToolUse hook and tool execution for exit 0. Task dispatches, runs, completes before agent reads the advisory — the gate is post-delegation.

**Correct pattern:** Block with `permissionDecision:deny`. Gate by `subagent_type` discriminator (execution agents: artisan, test-driver, corrector, runbook-corrector, design-corrector, outline-corrector, runbook-outline-corrector, tdd-auditor, refactor). Fragments don't load in sub-agents; recall-artifact is the only project context transport.

