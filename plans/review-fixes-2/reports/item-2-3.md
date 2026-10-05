# Item 2.3 — escalation.md: mask-branch dependency, remediation agents, resume verdicts

Target: `plugin/skills/build/references/escalation.md` (150 lines after
`just format`; cap 400). Requirements: m9, m12, m17.

## Edits

### §Post-item remediation, exit-1 bullet (m9)

Added after the mask-re-run sentence: the annotation comes from the
`phantom-untracked` detector of the optional `sandbox-lies` plugin's Bash
hook; without that plugin no listing is annotated, so the branch never fires,
and a masked listing reads as dirt. The rest of the bullet is unchanged
(reflowed by `just format`).

### §Post-item remediation, step 2 (m17)

Added: after a tdd slice's step, the step names the agent — after its GREEN,
`edify:test-driver` in GREEN mode; after its code-review, refactor or
list-revision commit, `edify:artisan`. Either dispatch carries the slice's
entry and the dirt. No outline label is cited: the living design has no
D-number for this rule (D-92 covers the remediation ladder, not the agent
type), so the text states the rule itself.

### §Resuming, step 2 (m12)

Replaced "every other verdict is taken as §2 takes it" with the named verdicts:

- `CLEAN:` → proceed;
- `DIRTY:` → examined, as the step already says;
- `PRECOMMIT:` over a clean tree, and exit 2 → STOP, as `/build` §2 does.

Then the bound: `verify-step.sh` exits on `DIRTY:` before it runs
`just precommit`, so a dirty resume reaches no precommit at the gate;
precommit first runs at the first remaining item's `SKILL.md` §4.4
verification, over the adopted prior work too.

## Verified

- **verify-step.sh verdict order** (`plugin/skills/build/scripts/verify-step.sh`):
  exempt-paths load failure → exit 2 `ERROR:`; `git status` failure or grep
  exit ≥ 2 → exit 2 `ERROR:`; non-empty filtered status → `DIRTY:` with the
  listing, exit 1, before any precommit; `just` missing → exit 2 `ERROR:`;
  `just precommit` failing → `PRECOMMIT:`, exit 1; else `CLEAN: tree clean,
  just precommit passed`, exit 0. So a dirty tree skips precommit, and
  `PRECOMMIT:` only ever occurs over a clean tree.
- **Hook name.** `sandbox-lies` is not installed on this machine: no entry in
  `~/.claude/plugins/installed_plugins.json` and nothing under
  `~/.claude/plugins/cache/`. Its source is at `/Users/david/code/sandbox-lies`
  (`.claude-plugin/plugin.json` name `sandbox-lies`). The plugin ships one
  Bash hook, `hooks/annotate.sh`, on `PostToolUse` and `PostToolUseFailure`
  (`hooks/hooks.json`); `phantom-untracked` is a *detector* that hook runs
  (`docs/references/detectors.md` §phantom-untracked), not a hook of its own.
  The text therefore says "the `phantom-untracked` detector of the optional
  `sandbox-lies` plugin's Bash hook" rather than the outline's "`phantom-untracked`
  hook".
- **Neighbours.** `SKILL.md` §2 (exit 1 `DIRTY:` mask branch, `PRECOMMIT:` STOP,
  exit 2 STOP) and §4.4 (refactor and list-revision commits listed) agree with
  the new text; `tdd-slice.md` §After the slice names the code-review,
  refactor and list-revision commits the remediation sentence lists;
  `dispatch-composition.md` uses "the slice's own numbered entry", matching
  "the slice's entry".

## Observation, not acted on

`docs/references/detectors.md` gives `phantom-untracked`'s matcher a threshold
of at least two distinct masked names on status-shaped lines. A `DIRTY:`
listing carrying a single masked name is not annotated even with the plugin
installed, so it too reads as dirt. The item did not ask for this bound; it is
recorded here for whoever owns Items 2.11 and 3.1's `sandbox-lies` wording.
