# Item 2.9 — escalation-acceptance.md: committed fix escalates, one re-run

Target: `plugin/fragments/escalation-acceptance.md`. Requirements: M2, m14.

## Edits

### §Verification sequence, step 3 (m14)

Was: "If `DIRTY:`: commit the fix by name (`git commit -- <paths>`), re-run
until it exits 0".

Now:

```
   - If `DIRTY:`: commit the fix by name (`git commit -- <paths>`), subject
     `<type>: <job> Item N.M[/k] — <title>`, then re-run it once:
     - `CLEAN:` → step 4
     - `PRECOMMIT:` → step 2
     - a second `DIRTY:`, or exit 2 → escalate
```

The subject is D-94's item form. The unbounded loop is gone: one re-run, with
`PRECOMMIT:` routed back to step 2's precommit loop and a second `DIRTY:` or a
script failure (exit 2) escalating. The `CLEAN:` branch is stated so the
re-run's exit-0 outcome, which "until it exits 0" used to carry, is not left
implicit.

### §Rollback protocol, "Fix committed" (M2)

Was: revert every commit since the last clean commit, newest first, with
`git revert --no-commit <sha>`, then commit by name with the revert subject.

Now:

> Fix committed: escalate to the user with the commits since the last clean
> commit before the failed item and what the attempt found. Nothing reverts them
> by default. Only the commits the user decides to revert are reverted: newest
> first, each with `git revert --no-commit <sha>`, then the reverted paths
> committed by name (`git commit -- <paths>`), subject
> `<type>: <job> Item N.M[/k] — revert failed fix` (probed on git 2.47.3). Never
> `git reset`, which discards history

This matches the "Fix uncommitted" bullet below it and `escalation.md`
§Post-item remediation's "nothing reverts by default": the recipe survives, but
runs only on the user's decision. The text cites no outline decision label.

## Verification

- `just precommit`: `Precommit OK` (version consistency, tests cached, line
  limits, design links). No reflow beyond the edit; the file is 96 lines. The
  three `oversized-file` lines it prints (`corrector.md`,
  `outline-corrector.md`, `design-corrector.md`) are files this item does not
  touch.

## Surfaces outside scope

- `docs/references/build-run-state.md` D-92 still covers uncommitted dirt only;
  the committed case is Item 3.1's.
- A search of `plugin/`, `docs/`, `README.md` and `CLAUDE.md` for "until it
  exits 0", "revert every commit", "revert failed fix" and `revert --no-commit`
  finds no other copy.
