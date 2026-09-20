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

## Commit B — the reflow

### Survey: nothing line-greps markdown in scope

`rg` over `tests/`, `plugin/bin/`, `plugin/skills/build/scripts/`,
`plugin/hooks/`, `justfile`, `plugin/portable.just` and `scripts/` for
`grep`/`rg`/`sed`/`awk` touching a `.md` path:

| hit | disposition |
| --- | --- |
| `plugin/bin/triage-feedback.sh:44` greps `**Classification:**` | reads `plans/<job>/classification.md` — outside the reflow scope |
| `plugin/bin/edify-review-range.sh:90,141` grep `**Base:**` / `**Derived from:**` | reads design/outline artifacts under `plans/` — outside the scope; and already joins `- **Field:**` bullets with their continuation lines (Item 1.9), so wrap-safe regardless |
| `plugin/bin/bootstrap-venv.sh:32` | reads `plugin.json`, not markdown |
| `plugin/skills/build/scripts/verify-step.sh:9` | greps `git status --porcelain`, not markdown |
| `plugin/portable.just:66,127,135` | parses tool output, not markdown |
| `tests/fixtures/markdown/05-*.md:12` | a `grep "*.md"` *inside* a fixture's code block, under `tests/` — outside the scope |

No hit reads a file the reflow touches. Nothing needed changing.

### Renderer

`cmark-gfm` is not installed and is not packaged for this box, so the render
is **markdown-it-py 4.2.0** in a throwaway venv (`/tmp/item-1-11/render`),
configured `MarkdownIt("commonmark").enable(["table", "strikethrough"])` so
tables render as tables and `~~del~~` as `<del>`. Each of the 57 in-scope
files was rendered to `tmp/item-1-11/{before,after}/<path>.html` and the two
compared after `re.sub(r"\s+", " ", …)` on both sides.

### Source fix the render diff demanded

First pass: **1 of 57 files changed rendering** —
`plugin/skills/build/references/dispatch-composition.md`. The change was a
*repair*, not a regression, and it exposed a real pre-existing defect.

The line was hand-wrapped as:

```text
   subject is `<type>: Item N.M/k —
   <title>`; `<type>` is the executor's choice — `feat`, …
```

`title` is one of CommonMark's block-level tag names, so `<title>` at the
start of a line opens an **HTML block**, which interrupts the paragraph and
cuts the code span in half. Every backtick from there to the end of the
paragraph then rendered as a literal backtick instead of `<code>`. Minimal
probe, confirming the mechanism rather than guessing it:

```text
a `x\n<title>` b   ->  <p>a `x</p> <title>` b      # broken
a `x\n<zzz>` b     ->  <p>a <code>x <zzz></code> b</p>  # fine
```

Fix: move the em dash down a line so `<title>` is no longer line-initial
(`` `<type>: Item N.M/k\n   — <title>` ``). The before rendering then
carries `<code>&lt;type&gt;: Item …</code>` as intended, and the reflow — which
re-joins both onto one line — leaves the rendering untouched. The fix is
invisible in the committed diff because the reflow subsumes it; its purpose
was to make the before rendering correct so the comparison could prove the
reflow changes nothing.

### Render diff, second pass

**57 files compared, 0 with a rendering change.** Every pair diffs empty
with whitespace collapsed.

### Reflow outcome

54 files rewritten (50 with a changed line count), **+1139 lines** total;
`git diff --stat` reports 54 files changed, 3186 insertions, 2047
deletions. Files touched:

| file | before | after | render diff empty |
| --- | ---: | ---: | :---: |
| `CLAUDE.md` | 218 | 296 | y |
| `README.md` | 73 | 72 | y |
| `docs/changelog.md` | 293 | 294 | y |
| `docs/design.md` | 1213 | 1221 | y |
| `docs/marketplace.md` | 30 | 38 | y |
| `docs/superpowers/design/invariant-guided-verify-loop.md` | 110 | 110 | y |
| `docs/superpowers/design/plugin-transition-evaluation.md` | 395 | 403 | y |
| `plugin/README.md` | 81 | 82 | y |
| `plugin/agents/artisan.md` | 122 | 132 | y |
| `plugin/agents/brainstorm-name.md` | 65 | 66 | y |
| `plugin/agents/corrector.md` | 605 | 682 | y |
| `plugin/agents/design-corrector.md` | 413 | 460 | y |
| `plugin/agents/outline-corrector.md` | 412 | 450 | y |
| `plugin/agents/refactor.md` | 203 | 221 | y |
| `plugin/agents/runbook-corrector.md` | 214 | 264 | y |
| `plugin/agents/runbook-simplifier.md` | 165 | 186 | y |
| `plugin/agents/scout.md` | 109 | 121 | y |
| `plugin/agents/tdd-auditor.md` | 194 | 194 | y |
| `plugin/agents/test-driver.md` | 112 | 111 | y |
| `plugin/fragments/claude-config-layout.md` | 102 | 109 | y |
| `plugin/fragments/delegation.md` | 94 | 122 | y |
| `plugin/fragments/error-classification.md` | 179 | 205 | y |
| `plugin/fragments/escalation-acceptance.md` | 57 | 81 | y |
| `plugin/fragments/execution-routing.md` | 41 | 54 | y |
| `plugin/fragments/prerequisite-validation.md` | 260 | 270 | y |
| `plugin/fragments/review-requirement.md` | 176 | 253 | y |
| `plugin/fragments/token-economy.md` | 5 | 7 | y |
| `plugin/fragments/workflows-terminology.md` | 28 | 35 | y |
| `plugin/skills/build/SKILL.md` | 221 | 218 | y |
| `plugin/skills/build/references/dispatch-composition.md` | 93 | 93 | y |
| `plugin/skills/build/references/finishing.md` | 77 | 73 | y |
| `plugin/skills/build/references/phase-boundary.md` | 23 | 22 | y |
| `plugin/skills/build/references/resuming.md` | 13 | 13 | y |
| `plugin/skills/build/references/review-dispatch-template.md` | 110 | 136 | y |
| `plugin/skills/build/references/tdd-slice.md` | 56 | 55 | y |
| `plugin/skills/deliverable-review/SKILL.md` | 152 | 175 | y |
| `plugin/skills/deliverable-review/references/example-report.md` | 197 | 231 | y |
| `plugin/skills/design/SKILL.md` | 176 | 285 | y |
| `plugin/skills/design/references/design-content-rules.md` | 170 | 224 | y |
| `plugin/skills/design/references/research-protocol.md` | 43 | 64 | y |
| `plugin/skills/design/references/route-to-execution.md` | 67 | 66 | y |
| `plugin/skills/design/references/write-design.md` | 77 | 101 | y |
| `plugin/skills/design/references/write-outline.md` | 215 | 301 | y |
| `plugin/skills/formalize/SKILL.md` | 94 | 95 | y |
| `plugin/skills/ground/SKILL.md` | 81 | 107 | y |
| `plugin/skills/ground/references/grounding-criteria.md` | 126 | 160 | y |
| `plugin/skills/proof/SKILL.md` | 158 | 203 | y |
| `plugin/skills/proof/references/item-review.md` | 78 | 100 | y |
| `plugin/skills/recall/SKILL.md` | 80 | 79 | y |
| `plugin/skills/requirements/SKILL.md` | 310 | 357 | y |
| `plugin/skills/requirements/references/empirical-grounding.md` | 63 | 71 | y |
| `plugin/skills/review/SKILL.md` | 213 | 231 | y |
| `plugin/skills/review/references/common-scenarios.md` | 27 | 27 | y |
| `plugin/skills/review/references/example-execution.md` | 52 | 52 | y |
| `plugin/skills/review/references/review-axes.md` | 65 | 71 | y |
| `plugin/skills/runbook/SKILL.md` | 150 | 146 | y |
| `plugin/skills/runbook/references/runbook-format.md` | 138 | 138 | y |

## Commit C — the allowlist

`scripts/check_line_limits.sh` reported ten files over their path-picked cap
after the reflow. `scripts/check_line_limits.allow` records each with its
**measured** post-reflow count as the ceiling, TAB-separated, under a header
restating the format and the ratchet-down maintenance rule:

| path | ceiling (measured) | cap | note |
| --- | ---: | ---: | --- |
| `docs/design.md` | 1221 | 400 | no job yet |
| `docs/superpowers/design/plugin-transition-evaluation.md` | 403 | 400 | no job yet |
| `plugin/agents/corrector.md` | 682 | 400 | pilfer defect 21 (corrector-family dedup) |
| `plugin/agents/design-corrector.md` | 460 | 400 | pilfer defect 21 (corrector-family dedup) |
| `plugin/agents/outline-corrector.md` | 450 | 400 | pilfer defect 21 (corrector-family dedup) |
| `plugin/skills/build/SKILL.md` | 218 | 200 | no job yet |
| `plugin/skills/design/SKILL.md` | 285 | 200 | no job yet |
| `plugin/skills/proof/SKILL.md` | 203 | 200 | no job yet |
| `plugin/skills/requirements/SKILL.md` | 357 | 200 | no job yet |
| `plugin/skills/review/SKILL.md` | 231 | 200 | no job yet |

`plugin/skills/design/SKILL.md`, `plugin/skills/proof/SKILL.md` and
`docs/superpowers/design/plugin-transition-evaluation.md` are the three the
reflow itself pushed over — `design/SKILL.md` and `proof/SKILL.md` past the
200-line `SKILL.md` cap, `plugin-transition-evaluation.md` past 400 by three
lines. The other seven were already over before it.

### `just precommit` — green

```text
# version consistency
Version consistent: 0.2.0
# Test Report

**Summary:** 331/332 passed, 1 xfail
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
oversized-file: plugin/skills/review/SKILL.md: 231 lines > 200
oversized-file: plugin/skills/requirements/SKILL.md: 357 lines > 200
oversized-file: plugin/skills/design/SKILL.md: 285 lines > 200
oversized-file: plugin/skills/build/SKILL.md: 218 lines > 200
oversized-file: plugin/skills/proof/SKILL.md: 203 lines > 200
oversized-file: docs/design.md: 1221 lines > 400
oversized-file: docs/superpowers/design/plugin-transition-evaluation.md: 403 lines > 400
✓ Precommit OK
```

Exit 0. The `oversized-file:` lines are the allowlist working as designed —
reported, not failing. The `rumdl` check printed nothing, which is the whole
point of `-q`: a clean formatter check is silent and the `report` helper
prints no header for it.

## Commits

1. `build: Item 1.11 — rumdl in the dev group, format and precommit recipes`
   (committed as `📦️ Item 1.11 — …`; the `commit-msg` hook rewrites the type
   prefix to an emoji)
2. `style: Item 1.11 — reflow markdown at 80 columns` (`🎨 Item 1.11 — …`)
3. `chore: Item 1.11 — allowlist the files over cap after the reflow`
