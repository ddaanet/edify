# Item 1.10 / Slice 8 — GREEN report

Mode: GREEN. Scope: `scripts/check_line_limits.sh` only (test file already
correct per RED/test-review — no further edit needed).

## Approach

Each of the three `find` call sites read from a process substitution
(`< <(find ... -print0)`), which discards `find`'s own exit status —
`set -e` cannot see a subshell's failure through a process substitution.
Slices 3-7's code review (Finding 3) and this slice's RED test both
confirmed the resulting gate stays green (exit 0, no `oversized-file:`
line) when `find` hits an unreadable directory mid-walk.

Fix: one `walk()` helper wrapping `find "$@" -print0`, spooled into a
`mktemp` temp file (`WALK_LIST`) instead of piped through a subshell. The
redirection's own exit status is checked directly:

```bash
walk() {
    find "$@" -print0 >"$WALK_LIST" || {
        echo "check_line_limits: find failed under $1" >&2
        exit 2
    }
}
```

`find`'s own stderr (`Permission denied`) is not redirected, so it reaches
the caller unchanged — this is what the RED test's
`"docs/locked" in result.stderr` assertion checks. `WALK_LIST` is created
once near the top of the script body with `mktemp`, cleaned by
`trap 'rm -f "$WALK_LIST"' EXIT` so it is removed on every exit path
(success, overage, or a `walk` failure). All three call sites (`src`/`tests`
Python walk, `plugin`/`docs` markdown walk, root-level `*.md` walk) now call
`walk "$dir" ...` then `while IFS= read -r -d '' file; do ... done <"$WALK_LIST"`
in place of the process-substitution form — same NUL-delimited read loop,
same quoting, just reading from a file instead of a subshell's fd.

Partial output already printed for an earlier, successfully-walked
directory is left as-is on a later failure (the RED test deliberately does
not assert on it either way, per Finding S8-1 in the test review).

## Verification

`pytest tests/test_line_limits.py -v`:

```
Summary: 12/12 passed
```

Full suite `pytest -q`:

```
316/332 passed, 16 skipped
```

`shellcheck scripts/check_line_limits.sh`: no output (clean).

`just precommit` on the real tree (red, as expected — no allowlist yet,
Item 1.11):

```
oversized-file: plugin/agents/corrector.md: 605 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 412 lines > 400
oversized-file: plugin/agents/design-corrector.md: 413 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 213 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 310 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 221 lines > 200
oversized-file: docs/design.md: 1213 lines > 400
```

`just precommit` exit code: 1 (overage) — confirmed via a bare exit-code
check after the recipe, not truncated `tail` output. Not 2, so the walk
itself completes cleanly on the real tree; the seven lines above are a
genuine overage report awaiting Item 1.11's allowlist.

## Commit

Subject: `fix: Item 1.10/8 — a failed walk is a failure, not a clean gate`
