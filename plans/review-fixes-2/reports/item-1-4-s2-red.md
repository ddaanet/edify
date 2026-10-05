# Item 1.4 slice 2 RED — exempt-paths.sh load guard in verify-step.sh

Test: `tests/test_verify_step.py::test_unloadable_exempt_paths_is_an_error_not_dirty`,
parametrised `[absent]` (exempt-paths.sh missing) and `[defines-nothing]`
(present, `# defines nothing`). Module 134 lines (cap 400). Helper change:
`tests/verify_step_helpers.py::_run_script` gained a `script: Path = SCRIPT`
keyword (invoked via `[str(script)]`). The test copies `SCRIPT` (the repo's
`verify-step.sh`) to `tmp_path/scripts/` beside the doctored file, so a
mutation of the real script reaches the copy. The repo carries an untracked
`dirt.txt`, so a script that carried on would print `DIRTY:` (exit 1). The
test asserts exit 2, the ERROR line, no `DIRTY:`, and that the stub `just`
was never invoked.

## Against the unchanged script (guard present)

Module 5/5 passed; with the exemption module 11/11. Both cases pass: the guard
already exists.

## Mutation proof

Mutation, one run per case (`-k "not_dirty and <case>"`): in
`plugin/skills/build/scripts/verify-step.sh` replace the once-occurring block

    if ! source "$script_dir/exempt-paths.sh" || [[ -z ${EXEMPT_PATHS_ALTERNATION:-} ]]; then
        echo "ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh"
        exit 2
    fi

with `source "$script_dir/exempt-paths.sh"`. Both reds are on the
`returncode == 2` assertion:

- `[absent]`: `verify-step.sh: line 18: .../scripts/exempt-paths.sh: No such file or directory` / `assert 1 == 2`
- `[defines-nothing]`: `verify-step.sh: line 36: EXEMPT_PATHS_ALTERNATION: unbound variable` / `assert 1 == 2`

Restore: swapped replacement. Proof: grep `^source "$script_dir` no hit;
`git diff --exit-code -- plugin/skills/build/scripts/verify-step.sh` exit 0;
module 5/5 green; `just lint` OK.

## Fixtures tried and rejected

None.
