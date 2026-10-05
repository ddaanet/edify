# Item 1.4 slice 1 RED — exempt-paths.sh load guard

Test: `tests/test_changed_files.py::test_unloadable_exempt_paths_is_an_error_not_no_base`,
parametrised over two cases (`[None]` = exempt-paths.sh absent;
`[# defines nothing\n]` = present, defines nothing). Module now 318 lines.
The test copies `SCRIPT` (the repo's `changed-files.sh`, from
`tests/changed_files_helpers.py`) to `tmp_path/scripts/`, so a mutation of the
real script reaches it. Each repo holds a committed `item-1-1.md` report.

## Against the unchanged script (guard present)

Module: 8/8 passed — both cases pass, as expected: the guard already exists.

## Mutation proof

Mutation (one run, reds both named cases): in
`plugin/skills/build/scripts/changed-files.sh`, replace the exact once-occurring
block

    if ! source "$script_dir/exempt-paths.sh" || [[ -z ${EXEMPT_PATHS_ALTERNATION:-} ]]; then
        echo "ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh"
        exit 2
    fi

with the bare `source "$script_dir/exempt-paths.sh"`. Result: 6/8 passed, 2 failed,
each on the `returncode == 2` assertion (not an ERROR):

- `[None]`: `changed-files.sh: line 68: .../scripts/exempt-paths.sh: No such file or directory` / `assert 1 == 2`
- `[# defines nothing\n]`: `changed-files.sh: line 69: EXEMPT_PATHS_ALTERNATION: unbound variable` / `assert 1 == 2`

Restore: applied the swapped replacement. Proof: grep for the bare
`^source "$script_dir` line: no hit; `git diff --exit-code --
plugin/skills/build/scripts/changed-files.sh`: exit 0; module 8/8 green;
`just lint` OK.

## Fixtures tried and rejected

None. (Parametrising rather than two tests keeps one shared body; each case is
a separately named test id for mutation proof.)
