# Item 2.4 slice 1 — GREEN

Added `--no-show-signature` right after `git log`/`-1`/`--diff-filter=A`/`--reverse` flags and before `--format=%H`, as `finishing.md` does. No other wording changed; no reason sentence added.

## Order made to pass (one file at a time)

1. `phase-boundary.md` §Base and changed files (`git log -1 ...`)
2. `tdd-slice.md` GREEN-commit query
3. `escalation.md` §Resuming step 1 (inline span; `just format` reflowed the list item, no rewording)
4. `tdd-auditor.md` check 2
5. `build-run-state.md` D-88 block, then D-89 block

`finishing.md` untouched (already flagged). `plugin/skills/build/SKILL.md` and `dist/` untouched.

## Results

- `.venv/bin/pytest -p no:markdown_report tests/test_build_prose_git_log.py`: 9 passed (was 6 failed, 3 passed).
- Full suite via precommit: 430/431 passed, 1 xfail (pre-existing).
- `just format` reflowed only `escalation.md`; the diff beyond the flag is line re-wrapping.

## Gate verdict

`Precommit OK`; recap: version consistency (0.3.0), tests cached, line limits, design links (94 decisions indexed, defined once, conclusions match, 9 nodes present).
`tmp/.test-sentinel`: `1358766492 698630`

## Precommit warnings (not acted on)

oversized-file: plugin/agents/corrector.md 682 > 400; outline-corrector.md 450 > 400; design-corrector.md 460 > 400.
