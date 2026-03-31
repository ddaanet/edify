# Codebase Quality Sweep — Requirements

## Context

Grounded code density principles identified during quality infrastructure analysis. Extracted from quality-infrastructure FR-4 — independent of infrastructure renaming/restructuring work.

Grounding report: `plans/reports/code-density-grounding.md`
User feedback: annotated `src/edify/cli.py` (12 anti-pattern markers)

## Implementation Targets

- Add `_git_ok(*args) -> bool` to `src/edify/worktree/utils.py`
- Add `_fail(msg, code=1) -> Never` to `src/edify/worktree/utils.py`
- Replace 13 raw `subprocess.run(["git", ...])` calls with `_git_ok` across cli.py, merge.py, utils.py
- Replace 18 `click.echo(err=True) + raise SystemExit` patterns with `_fail` across cli.py, merge.py
- Replace exception-as-control-flow patterns (3 sites) with `_git_ok` boolean checks
- Custom exception classes for domain errors in `src/edify/cli.py` (SessionNotFoundError, etc.)

## Non-Requirements

- No changes to exit code semantics (1=error, 2=safety gate)
- No changes to `_git()` helper signature
- Click exception hierarchy (`ClickException`, `UsageError`) evaluated and rejected — `_fail()` is simpler for this project's exit code semantics
