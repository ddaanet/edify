# Code Density and Exception Handling — Grounded Reference

Date: 2026-02-18

## Research Foundation

**Internal branch:** Opus analysis of `src/claudeutils/worktree/` module — 19 raw subprocess calls, 18 SystemExit raises, 6 exception-as-control-flow sites. Full applicability audit across cli.py, merge.py, utils.py.

**External branch:** EAFP/LBYL principles (Real Python, Python glossary, mathspp), subprocess best practices (Python docs, sqlpey), Click exception hierarchy (Click docs), Black formatting mechanics (Black docs, trailing comma spec).

**User feedback:** Annotated `src/claudeutils/cli.py` with 12 anti-pattern markers across exception handling, Black density, and architecture.

## Adapted Methodology

### Principle 1: Expected State Checks Return Booleans

**General principle:** When a condition is a normal program state (not an exceptional event), check it with a boolean return, not an exception. EAFP is idiomatic for IO where failure is uncommon (Real Python, Python glossary), but expected states — existence checks, availability queries — are not exceptional (charlax/antipatterns: "Exception handling is for unexpected or exceptional events").

**Grounding:** Real Python EAFP/LBYL guide, Python glossary, charlax/antipatterns.

**Project instance:** Two inconsistent idioms for "does branch exist?" — raw subprocess LBYL (5-6 lines under Black) and EAFP try/except (treats expected condition as exceptional). Implemented as `_git_ok(*args) -> bool` — boolean wrapper returning `returncode == 0`. Covers 13 of 15 raw subprocess sites. Two outliers needing stderr remain as raw calls.

### Principle 2: Consolidate Display and Exit

**General principle:** Error termination should be a single call, not a display+exit sequence. CLI frameworks recognize this — Click's `ClickException` and `UsageError` consolidate display+exit into a single raise (Click docs). When display and exit are separate statements, they drift apart (different messages, forgotten exits, inconsistent stderr routing).

**Grounding:** Click exception hierarchy docs. Alternative considered: `ClickException` subclass — rejected for this project because hardcoded exit codes (UsageError→2, Abort→1) don't map to the project's exit code semantics.

**Project instance:** 18 instances of `click.echo(msg, err=True)` + `raise SystemExit(N)` across worktree module. Implemented as `_fail(msg, code=1) -> Never` in utils.py. `Never` return type informs type checkers that control flow terminates.

### Principle 3: Formatter Expansion Signals Abstraction Need

**General principle:** When a call site consistently takes 5+ lines after opinionated formatting, the call has too many parameters for inline use. Extract a helper whose defaults encode the common kwargs. Formatting tools expose complexity that manual formatting hides — a function that "looks fine" hand-formatted but explodes under Black has an API surface problem, not a formatting problem.

**Grounding:** Black's formatting algorithm tries to fit calls on one line, falling back to one-arg-per-line (Black docs). Keyword arguments expand aggressively. Wrapper functions that encode default kwargs as policy reduce expansion (Black trailing comma spec).

**Project instance:** Raw `subprocess.run()` with keyword args expands to 5-6 lines under Black. The `_git()` helper collapses stdout calls to 1 line, but callers bypass it when they need returncode. `_git_ok()` covers the returncode case.

### Principle 4: Exceptions for Exceptional Events Only

**General principle:** Exception handling is for unexpected or exceptional events (charlax/antipatterns, Medium anti-pattern article). If a condition is a normal program state, boolean returns or typed return values are cleaner than exceptions. Using broad exception types (`ValueError`) for expected conditions masks legitimate bugs under the same `except` clause.

**Grounding:** charlax/antipatterns error-handling guide, Medium exception-as-control-flow article, Real Python EAFP/LBYL.

**Project instance:** `try: _git("rev-parse"...) except CalledProcessError:` used to check branch existence → replaced with `_git_ok()` boolean. `ValueError` raised for expected conditions (no session found, multiple matches) → replaced with custom exception classes (`SessionNotFoundError`). Custom classes also properly satisfy lint rules about hardcoded exception messages — without the `msg` variable circumvention.

### Principle 5: Error Handling Layers Don't Overlap

**General principle:** Each layer in the error handling chain has one responsibility. Failure site: collect context, raise typed exception. Top level: display, exit. When both layers print, you get duplicate output or conflicting messages. The `raise from` chain preserves the causal chain without duplicating display logic.

**Grounding:** Single-responsibility principle applied to error handling. Standard pattern in well-structured CLI tools — framework-level exception handlers (Click, argparse) expect to own the display responsibility.

**Project instance:** Double error handling in cli.py — exceptions caught and messages printed at both the failure site and a top-level handler. Rule: context collection at the failure site, display at the top level, never both.

## Grounding Quality: Moderate

**Strong grounding:** EAFP/LBYL boundaries, subprocess patterns, Click exception hierarchy, Black expansion mechanics — all from authoritative sources with clear applicability.

**Thin grounding:** The `_git_ok()` pattern is a project-specific synthesis (no external source describes this exact helper design). But it follows directly from the grounded principle that state queries should return booleans when the condition is expected.

**Not grounded (standard practice):** Custom exception classes, `Never` return type, pydantic models vs ad-hoc casting. These are established Python patterns not requiring external validation.

## Sources

- [Real Python — LBYL vs EAFP](https://realpython.com/python-lbyl-vs-eafp/)
- [mathspp — EAFP and LBYL coding styles](https://mathspp.com/blog/pydonts/eafp-and-lbyl-coding-styles)
- [Medium — Exception as Control Flow Anti-Pattern](https://medium.com/@samanwayghatak/exception-as-control-flow-anti-pattern-e3b46b079cdd)
- [charlax/antipatterns — Error Handling](https://github.com/charlax/antipatterns/blob/master/error-handling-antipatterns.md)
- [Python subprocess docs](https://docs.python.org/3/library/subprocess.html)
- [sqlpey — subprocess best practices](https://www.sqlpey.com/python/python-subprocess-best-practices/)
- [Click docs — Exception Handling](https://click.palletsprojects.com/en/stable/exceptions/)
- [Black docs — The Black Code Style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
- [Black GitHub Issue #1288 — Magic Trailing Comma](https://github.com/psf/black/issues/1288)
