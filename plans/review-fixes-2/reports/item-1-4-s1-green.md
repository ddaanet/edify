# Item 1.4 slice 1 — GREEN

No implementation change: the load guard already exists in
`plugin/skills/build/scripts/changed-files.sh` (proven by mutation in RED and
test review). This dispatch commits the slice's test, the reviewer's
`_run_script` helper change, and the reports.

## Tests run

Order made to pass (both already passing; no growth needed):

1. `test_unloadable_exempt_paths_is_an_error_not_no_base[absent]` — passed
2. `test_unloadable_exempt_paths_is_an_error_not_no_base[defines-nothing]` — passed

Run with `UV_CACHE_DIR=$TMPDIR/uvc uv run pytest tests/test_changed_files.py -k unloadable`: 2/2 passed
(default uv cache is read-only in the sandbox). `just lint`: Lint OK.

## Gate verdict

`just precommit` (foreground), full output:

```
# version consistency
Version consistent: 0.3.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 94 decisions indexed, defined once, conclusions match, 9 nodes present
✓ Precommit OK
```

`tmp/.test-sentinel`: `4029834635 650433`

Warnings (for code review, not acted on): the three oversized-file lines above,
all in files this slice does not touch.
