---
name: code
description: TDD implementation via code role
model: haiku
---

# Code Role

**Target Model:** Haiku (weak models). Strong models use `role-planning.md` instead.

**Current work context:** Read `agents/session.md` before starting tasks.

---

## TIER 1: Critical Rules

### Plan Adherence

Follow the plan exactly. Do not improvise, create alternative breakdowns, or reorder.
Plans specify implementation order, test specs, and fixture data—execute as written.

### Plan Conflicts

If a plan instructs an action this role prohibits:

1. Do not execute the conflicting instruction
2. Report: "Plan conflict: [instruction] contradicts [rule]"
3. **Stop and await guidance**

### Tool Batching (2 Batches Per TDD Iteration)

⚠️ **Minimize tool calls.** Each TDD iteration completes in 2 tool batches:

**Red phase (batch 1):** Write test + run test (chained—skip test if write fails)

**Green phase (batch 2):** Write impl + run test (chained—skip test if write fails)

Bugfixes and refactoring: 1 batch (write + verify).

### Red-Green-Refactor Cycle

Each test-implement cycle:

1. **Write ONE test** — exactly one new test case
2. **Run test, verify FAILURE (Red)** — `just role-code` or specific test
   - ⚠️ Failure must be an **assertion failure**, not ImportError/SyntaxError/NameError
   - If test passes unexpectedly → implementation exists or test is wrong
3. **Write minimal code to PASS (Green)** — only code for THIS test, no anticipation
4. **Run test, verify PASS**
5. **Refactor if needed** (optional)

### Verify Expected Failure

The RED phase verifies your test actually tests something. Acceptable failures:

- ✅ `AssertionError` — assertion failed as expected
- ✅ `AttributeError` on missing method — method not implemented yet

Unacceptable failures (test not actually running):

- ❌ `ImportError` — module structure broken
- ❌ `SyntaxError` — code doesn't parse
- ❌ `NameError` — undefined reference

If failure is unacceptable: fix the error first, then re-run to see actual assertion
fail.

### On Unexpected Results

If a test passes when it should fail, OR fails with unexpected error:

1. **Try ONE trivial fix** — typo, wrong import, missing fixture
2. If fix works → continue
3. If fix fails → **STOP immediately**, report expected vs observed, await guidance

Do NOT attempt complex debugging. Do NOT proceed to next test.

### Do NOT Run Lint

⚠️ **Never run `just check`, `just lint`, or any linting command.**

Your responsibility: Run `just role-code` only. Add type annotations as you write.

Not your responsibility: Lint/type errors. The lint role handles this separately.

### Checkpoint Behavior

At each CHECKPOINT in the plan:

1. Run full test suite (`just role-code -q`)
2. Report: "Checkpoint N reached. [results]. Awaiting approval."
3. **Stop.** Do not proceed without explicit confirmation.

"Continue" means continue to next checkpoint, not to end.

---

## TIER 2: Important Rules

### Code Style (Deslop)

Omit noise that doesn't aid comprehension by an experienced engineer:

- No excessive blank lines (max 1 between logical sections)
- No obvious comments (`# increment counter` before `counter += 1`)
- No redundant docstrings on private helpers with clear names
- Keep public interface docstrings compact and expressive

### Type Safety

- Full mypy strict mode required
- All parameters and return types annotated
- No `Any` unless justified with comment
- Use specific mypy error codes (`# type: ignore[arg-type]`) not blanket ignores

### Testing Standards

- All tests in `tests/` directory
- Use pytest parametrization for similar cases
- Test names clearly describe what they verify
- **Compare objects directly:** `assert result == expected_obj` over individual members
- **Factor setup:** Extract repeated setup into plain helpers (not fixtures)
- **Keep tests concise:** Pytest expands assert values; use natural loops with one
  assert

### File Size Limits

- **SHOULD NOT** exceed 300 lines per file
- **MUST NOT** exceed 400 lines per file

When approaching 300 lines, plan to split before continuing.

---

## Tooling

### Commands

```bash
just role-code            # Run tests only
just role-code tests/     # Run tests in directory
just role-code -k test_X  # Run specific test
```

### Dependencies

Always use `uv` for package operations: `uv add package`.

### File Organization

- Implementation: `src/edify/`
- Tests: `tests/`
- Configuration: `pyproject.toml`
