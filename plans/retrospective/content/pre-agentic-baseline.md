# Pre-Agentic Baseline — Before Agent Instructions

Evidence of Claude-assisted development without agent instructions, establishing contrast with the agentic period.

## celebtwin (May–Jul 2025)

- **256 commits**, 2025-05-31 to 2025-07-22
- **Agent instruction files:** None (no AGENTS.md, no CLAUDE.md, no .claude/)
- **Gitmoji usage:** 40 of 256 commits (16%) — gitmoji predates agentic instructions
- **GitHub Actions:** Present (`a2e0110` "Try using github actions to validate commits")
- **Tooling:** make-based (Makefile), not just-based. `make lint`, `make format`, `make pip-compile`

### Commit style

Commits are structured with gitmoji prefixes where used, but many are informal:
- `👷‍♂️ Use uv sync to build venv`
- `🐛 Create venv using uv before installing requirements`
- `✨ add /detect/{model} endpoint for face detection`
- `♻️ Clarify why we use Facenet2018 preprocessing everywhere`

Mix of gitmoji and non-gitmoji. No commit message conventions enforced. No `just agent` or equivalent gate.

### What's present without agent instructions

- Gitmoji (partial adoption, ~16%)
- GitHub Actions CI
- Python typing (mypy)
- Linting (pycodestyle, ruff)
- Make-based build system
- UV package management

### What's absent

- Agent instruction files (AGENTS.md, CLAUDE.md)
- Session tracking (session.md)
- Design decisions documentation
- TDD workflow formalization
- Commit gates (`just agent`)
- Skills, hooks, or agent configuration
- Plans directory
- Orchestration or delegation patterns

## calendar-cli (Apr–Jul 2025)

- **11 commits**, 2025-04-18 to 2025-07-31
- **Agent instruction files:** None
- **Gitmoji usage:** 0 of 11 commits
- **Tooling:** Minimal — Python script, no build system

### Commit style

Fully informal, narrative-style commit messages:
- `the regex patterns for weekday + time parsing were capturing the minutes...`
- `Fix AppleScript escaping to handle URLs and special character`
- `add debug mode info`
- `update readme to reflect support for reminders...`

No gitmoji, no conventional commit format, no structured messages. Longest commit message is multi-sentence paragraph.

### What's present

- Basic Python script
- README documentation

### What's absent

Everything listed for celebtwin, plus:
- Gitmoji
- CI/CD
- Linting/typing
- Build system
- Package management structure

## Contrast Summary

| Aspect | calendar-cli (Apr 2025) | celebtwin (May-Jul 2025) | First agentic (rules, Sep 2025) |
|--------|------------------------|--------------------------|--------------------------------|
| Agent instructions | None | None | rules.md (14 rules) |
| Commit style | Narrative paragraphs | Mixed gitmoji/informal | Structured, "descriptive messages" rule |
| Tooling | None | make + uv | just recipes |
| Quality gates | None | GitHub Actions CI | `just test` before commit |
| TDD | None | None | TDD Red-Green-Refactor |
| Session tracking | None | None | None (appears Jan 2026) |

The gap between celebtwin (Jul 2025) and rules (Sep 2025) is ~2 months. In that window:
- Agent instructions go from nonexistent to 14-rule structured document
- Commit conventions go from ad-hoc to gitmoji + structured messages
- Development workflow goes from manual to `just agent` gated
- Quality enforcement goes from CI-only to pre-commit agent checks
