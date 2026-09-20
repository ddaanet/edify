# Item 1.11 — rumdl in the dev group, the 80-column reflow, the allowlist

Three commits: tooling, the reflow alone, the allowlist. The line-limit gate
is red between the first and the third by design.

## Commit A — tooling

### rumdl

`uv add --group dev rumdl` resolved **rumdl 0.2.74**.

### Config keys verified against `rumdl config --defaults`

Not guessed — every key below appears in `rumdl config --defaults` and is
echoed back by `rumdl config --no-defaults` as `[from .rumdl.toml]`:

- `global.enable`, `global.include`, `global.exclude` — all three exist.
- `MD013.line-length`, `.reflow`, `.reflow-mode`, `.headings`,
  `.code-blocks`, `.tables` — all six exist. `tables` already defaults to
  `false`; it is set explicitly anyway, so the file states the whole
  contract.
- `rumdl config file` prints `/Users/david/code/edify/.rumdl.toml`, so the
  filename is picked up.

### Include globs are not path-anchored — measured

`include = ["*.md"]` does **not** mean root-level markdown: rumdl's `*`
crosses `/`, so that pattern matched `.claude/rules/*.md`, `agents/*.md`,
`memory/**` and `plans/**` — 377 files, and a `Permission denied` on
`.claude/loop.md` that made the run incomplete. `include = ["/*.md"]` is
anchored and matches exactly `CLAUDE.md` and `README.md`. The shipped
include is `["plugin/**/*.md", "docs/**/*.md", "/*.md"]`.

Scope then matches `scripts/check_line_limits.sh` exactly: the file set
rumdl walks and the file set the line-limit gate walks are the same 57
paths (`find plugin docs -name '*.md'` minus the two frozen
`docs/superpowers/` trees, plus root-level `*.md`), diffed and identical.

### The non-fixing precommit check — probe results

Candidates measured on throwaway files under `$TMPDIR` and on the repo:

| invocation | clean file | would-change file | unreflowable over-column line |
| --- | --- | --- | --- |
| `rumdl check --no-cache` | exit 0, prints `Success:` summary | exit 1 | **exit 1, permanently** |
| `rumdl fmt --check -q --no-cache` | exit 0, **prints nothing** | exit 1, prints a unified diff | exit 0 |

The third column is what decides it. Two lines in scope cannot be reflowed
by any `fmt` pass — `plugin/skills/design/SKILL.md:51` (107 chars) and
`plugin/agents/design-corrector.md:96` (102 chars); rumdl itself reports
`1082 of 1084` issues as auto-fixable. `rumdl check` reports those two
forever, so wiring it would leave the gate red with no action that clears
it. `rumdl fmt --check` is documented as "Exit with code 1 if any
formatting changes would be made (for CI)" and measures that way.

`-q` ("print diagnostics, but suppress summary lines") is what makes it fit
the `report` helper, which prints a header whenever the command produced
any output: without `-q` a clean run still prints `Success: No issues found
in 57 files` and the header would show on every green precommit.

Long URLs are a non-issue: `MD013.ignore-link-urls` defaults to `true`, and
a lone 120-char URL was clean under both invocations.

### Recipes (`plugin/portable.just` — the source; the root `justfile`
imports it and neither is generated)

- `precommit`: `report "rumdl" rumdl fmt --check -q --no-cache`, placed
  after `run-pytest` and immediately ahead of `run-line-limits` (KD-8).
- `format`: `rumdl fmt -q --no-cache` piped through
  `sed -Ene '/\[fixed\]$/s/^([^:]+):.*$/\1/p'` into `$tmpfile`, so the
  existing "Reformatted files" listing names the markdown files too. `-q`
  leaves one `path:line:col: … [fixed]` diagnostic per fix and drops the
  summary; repeated paths collapse in the existing `sort --unique`.

The root `justfile` carries its own copy of `bash_prolog` that overrides
the portable one, but `report` and `set-tmpfile` are identical in both, so
no prolog change was needed.
