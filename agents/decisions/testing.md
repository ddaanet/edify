# Test Strategy

Testing conventions and patterns for claudeutils codebase.

## .Test Organization

### How to Split Test Modules

**Decision:** Split test files to mirror source module structure + separate CLI test modules by subcommand

**Structure:**
```
tests/
├── test_models.py          # Pydantic validation
├── test_paths.py           # Path encoding
├── test_parsing.py         # Content extraction, filtering
├── test_discovery.py       # Session listing
├── test_agent_files.py     # Agent file discovery
├── test_extraction.py      # Recursive extraction
├── test_cli_list.py        # List command
├── test_cli_extract_basic.py   # Extract command, session matching
└── test_cli_extract_output.py  # JSON output, integration
```

**Rationale:** Maintain 400-line limit while keeping related tests together

## .Mock Patching

### How to Apply Mock Patches Correctly

**Decision:** Patch where object is **used**, not where it's **defined**

**Example:**
```python
# If module A defines foo(), and module B imports and uses it:
# Patch at usage location:
monkeypatch.setattr("pkg.b.foo", mock)  # ✅ Correct
monkeypatch.setattr("pkg.a.foo", mock)  # ❌ Won't work
```

**Rationale:** Python imports create references in the importing module's namespace

**Applied:** Mock patches target `claudeutils.discovery.*` and `claudeutils.extraction.*` for functions used in those modules

## .TDD Approach

### How to Test Markdown Cleanup

**TDD approach:**
- Red test → minimal code → green test
- Each feature: 4-6 test cycles
- Integration tests verify no conflicts
- Edge cases documented and tested

**Test coverage:**
- Valid patterns (should convert)
- Invalid patterns (should skip or error)
- Edge cases (empty blocks, unclosed fences, etc.)
- Integration (multiple fixes together)

### When Evaluating Test Success Metrics

- All new tests pass
- All existing tests pass (no regressions)
- Code follows existing patterns
- Clear error messages for invalid input
- Documentation complete and accurate

## When Writing Red Phase Assertions

**TDD RED behavioral:**

**Decision Date:** 2026-01-31

**Decision:** RED phase tests must verify behavior, not just structure.

**Anti-pattern:** Tests checking only structure (AttributeError, exit_code == 0, key existence)

**Problem:** Minimal GREEN implementations pass structure tests without implementing actual functionality.

**Examples of structural tests (insufficient):**
- `assert result.exit_code == 0` → implementation returns 0 with hardcoded data
- `assert "KEY" in dict` → implementation returns `{"KEY": ""}` (empty string)
- Test checks class/method exists → implementation returns stub that does nothing

**Correct pattern:** RED tests verify behavior with mocking/fixtures
- Mock file I/O and verify reads/writes to actual paths
- Mock external calls (subprocess, API) and verify correct invocation
- Assert on output content, not just success/failure
- Use fixtures (tmp_path) to simulate real filesystem state

**Rationale:** TDD principle "write minimal code to pass test" works only if test requires real behavior.

**Example:** Test should mock ~/.claude/account-mode file and verify CLI reads it, not just check exit code.

**Impact:** Prevents trivial implementations that satisfy tests without implementing functionality.

## When Testing Presentation Vs Behavior

**Decision Date:** 2026-01-31

**Decision:** Test behavior, defer presentation quality to vet checkpoints.

**Anti-pattern:** Writing RED-GREEN cycles for help text wording, error message phrasing.

**Rationale:** Presentation tests are brittle and self-evident.

**Impact:** Focus TDD cycles on functionality, handle presentation in batch during vet checkpoints.

## When Writing Integration Test Assertions

**Decision Date:** 2026-02-05

**Decision:** Add integration test requirement at phase boundaries for CLI/composition tasks.

**Anti-pattern:** Unit tests verify function calls (mock.assert_called) but not behavioral outcomes.

**Root cause:** Tests checked execution (function invoked) not integration (results consumed).

**Correct pattern:** For CLI/composition tasks, assert on critical content presence in output, not just structure.

**Example:** Cycle 5.4 test verified two-line output exists but didn't check usage data present.

**Implementation:** xfail integration test at phase start, pass at phase end.

**Impact:** Ensures behavioral outcomes are tested, not just execution paths.

## How to Validate Migration Conformance

**Decision Date:** 2026-02-05

**Decision:** Compare Python implementation against original shell spec at completion.

When migrating from external references (shell prototypes, API specs, visual mockups), tests must bake the expected behavior from the reference directly into assertions. The reference is consumed at test authoring time, and tests become permanent executable contracts that validate conformance throughout development.

### .Tests as Executable Contracts

When design includes external reference (shell prototype, API spec, visual mockup), tests bake expected behavior into assertions. The reference is consumed at authoring time, and tests become permanent living documentation. For example, statusline-parity tests should assert exact expected strings from the shell reference (e.g., `🥈 sonnet \033[35m…`), not just structure such as "contains emoji".

### .Exact Expected Strings Requirement

For conformance work, test assertions must include exact expected output from the reference. This eliminates translation loss between specification and implementation. It also addresses root cause RC5: "Visual Parity Validated" false completion claims become detectable when tests include exact expected strings from the reference.

### .Conformance Exception to Prose Descriptions

Standard TDD uses prose descriptions instead of full test code (per workflow-advanced.md). Conformance work is an exception: prose descriptions MUST include exact expected strings from the reference. This is not full test code — it is precise prose.

**Example contrast:**

| Standard prose | Conformance prose (with exact strings) |
|---|---|
| "Assert output contains formatted model with emoji and color" | "Assert output contains `🥈` emoji followed by `\033[35msonnet\033[0m` escape sequence with double-space separator" |

### .Conformance Pattern

**Pattern:** Delegated to exploration agent, writes detailed conformance matrix.

**Benefits:** Catches presentation/visual gaps that unit tests miss.

**Example:** statusline-wiring found all 5 requirements met but missing emojis/bars/colors.

**Impact:** Behavioral equivalence verification beyond functional testing, with exact specifications preventing translation loss.

**See also:** TDD RED Phase: Behavioral Verification (line 69) for assertion quality requirements that complement conformance testing.

## When Preferring E2E Over Mocked Subprocess

**Decision Date:** 2026-02-12

**Decision:** E2E only with real git repos (tmp_path fixtures), mocking only for error injection.

**Anti-pattern:** Dual test suite — e2e for behavior + mocked subprocess for speed.

**Rationale:** Git with tmp_path is fast (milliseconds), subprocess mocks are implementation-coupled (command strings not outcomes), interesting bugs are state transitions that mocks can't catch.

**Exception:** Mock subprocess for error injection only (lock files, permission errors).

## When Asserting Pipeline Idempotency

**Decision Date:** 2026-02-12

**Decision:** Assert full pipeline idempotency — `(preprocessor → remark)²` produces same result.

**Anti-pattern:** Pipeline test asserting remark output matches preprocessor expected fixtures.

**Rationale:** Remark legitimately reformats (table padding, blank lines) — exact match conflates preprocessor correctness with formatter style.

## When Detecting Vacuous Assertions From Skipped RED

**Decision Date:** 2026-02-12

**Decision:** When RED passes unexpectedly, verify assertions would catch the defect class.

**Anti-pattern:** Committing a test that never went RED without evaluating assertion strength.

**Example:** `assert isinstance(relevant, list)` passes on empty list — pipeline silently returns no matches.

**Detection:** Check if key assertions distinguish "correct output" from "empty/default output".
