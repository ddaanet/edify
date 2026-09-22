# Preflight — edify release readiness

**Date:** 2026-09-22
**Repo:** `/Users/david/code/edify`
**Branch:** `main`
**Current version:** 0.2.0 (`plugin/.claude-plugin/plugin.json`, source of truth)
**Last release tag:** `v0.2.0` (2026-09-02)
**Commits since tag:** 68

---

## Verdict: NO-GO as the tree stands

One blocker, and it is the one the task already anticipated: a tracked
modification to `.claude/handoff-todo.md`. `scripts/release.sh` refuses any
tracked diff. Commit that file and the verdict flips to **GO** — every other
precondition the release script enforces is already satisfied, the quality
gate is green, and the changelog covers the release window.

Do not use `git add -A` or `git add .claude/` to make that commit. Five
untracked paths under `.claude/` are character devices and git refuses them
outright. See warning W1. Add the single file by path.

| Check | Status |
|---|---|
| Branch is `main` | pass |
| Working tree clean (tracked) | **FAIL** — `.claude/handoff-todo.md` |
| Remote sync | pass — 68 ahead, 0 behind; the release pushes them |
| Submodule `memory` clean | pass — working tree clean, gitlink drift only |
| Quality gate (`just precommit`) | pass |
| Version consistency | pass — plugin.json and pyproject.toml both 0.2.0 |
| plugin.json matches last tag | pass — required by `release_preflight` |
| Marketplace entry and repo | pass |
| GitHub auth | pass |
| PyPI token | pass |
| Required tools | pass |
| Changelog coverage | pass |
| Pending task markers | pass — zero |
| Documentation | warn — two stale README claims (W2) |

---

## Blockers

### B1 — Tracked modification blocks the release script

`scripts/release.sh` `common_preflight` runs:

```
git diff --quiet HEAD -- . ':(exclude)memory' || die "uncommitted changes"
```

Verified against the current tree:

```
$ git diff --quiet HEAD -- . ':(exclude)memory'; echo "EXIT=$?"
EXIT=1

$ git diff --name-only HEAD -- . ':(exclude)memory'
.claude/handoff-todo.md
```

The diff is one deleted line:

```
$ git diff --stat .claude/handoff-todo.md
 .claude/handoff-todo.md | 1 -
 1 file changed, 1 deletion(-)
```

This is the file the task said would be committed before release. Commit it
and the gate clears. Nothing else in the tree is tracked-dirty.

---

## Warnings

### W1 — Five untracked `.claude/` paths are character devices, not files

```
$ git status --porcelain
 M .claude/handoff-todo.md
 M memory
?? .claude/launch.json
?? .claude/loop.md
?? .claude/output-styles
?? .claude/routines
?? .claude/workflows

$ ls -la .claude/launch.json .claude/output-styles
crw-rw-rw- 1 nobody nogroup 1, 3 Jul 23 21:28 .claude/launch.json
crw-rw-rw- 1 nobody nogroup 1, 3 Jul 23 21:28 .claude/output-styles
```

All five are device `1, 3`, which is `/dev/null`, owned by `nobody:nogroup`
and stamped with the same mount time. They are Claude Code sandbox bind
mounts, the same class as the paths already listed under the
`# Claude Code sandboxing artifacts` heading in `.gitignore`. They are not
covered by any existing pattern:

```
$ git check-ignore -v .claude/launch.json
NOT IGNORED
```

They do not block the release. `release.sh` only inspects tracked diffs, so
untracked paths are invisible to its gate.

They do break a bulk add, which matters because B1 needs a commit:

```
$ git add --dry-run .claude/launch.json .claude/loop.md .claude/output-styles \
    .claude/routines .claude/workflows
error: .claude/launch.json: can only add regular files, symbolic links or git-directories
fatal: adding files failed
```

Commit `.claude/handoff-todo.md` by explicit path. Separately, consider
extending the `.gitignore` sandbox-artifact block to cover these five so they
stop appearing in `git status`. That is a repo change, not a release
prerequisite, and I made no edit.

### W2 — Two stale claims in README.md

Neither blocks the release. Both mislead a reader arriving at the repo today.

**Markdown formatting points at dprint.** README lines 30 and 68 tell the
reader to pair `edify markdown` with dprint. The gate now formats markdown
with rumdl at 80 columns:

```
$ grep -rn 'dprint' justfile plugin/portable.just package.json
not invoked by any recipe
```

`.dprint.json` still exists in the tree, so dprint is configured but
unreferenced by any recipe. Either the README pointer or the leftover config
is wrong; deciding which is a repo call, not a preflight call.

**Design is described as a single file.** README's Development section says
"Design is recorded in `docs/design.md`". The design was split on 2026-09-20
into a hub, a decision index and eight nodes. `docs/design.md` is now the hub,
not the whole record.

Everything else in the README audits clean. The CLI section claims six
commands in four groups, and `edify --help` lists exactly six: `check`,
`collect`, `extract`, `list`, `markdown`, `tokens`. The plugin section names
five pipeline and five standalone skills, and `plugin/skills/` holds exactly
those ten.

### W3 — The release cannot run from a sandboxed Bash call

`common_preflight` calls `check_marketplace_writable`, which mktemps a probe
inside `$MARKETPLACE_DIR/.claude-plugin/`. This session's sandbox write
allowlist covers the repo directory and not `/Users/david/code/claude-plugins`,
so a sandboxed invocation dies there. The script anticipates this and says so
in its own `die` message, which names `dangerouslyDisableSandbox` and
`/add-dir` as the two ways out.

Run `just release` from a terminal outside the sandbox and the point is moot.
I did not run the probe, to honour the read-only constraint on the
marketplace repo; this warning is grounded in the sandbox allowlist and the
script's text, not in an observed failure.

---

## Informational

### I1 — `M memory` is the resting state, and memory itself is clean

```
$ git submodule status
+a20e6898d776900ac71022a3f2589d15ccffabec memory (heads/live)

$ git -C memory status --porcelain
(no output)
```

The `+` is gitlink drift: the parent records `7ab21b1a`, the submodule is
checked out at `a20e6898`. The parent's pre-commit hook records memory into
the next parent commit. `release.sh` excludes the path from both of its
cleanliness checks (`':(exclude)memory'`), so this cannot block the release.

The submodule HEAD is detached, but at the tip of `live`, and `live` is level
with `origin/live`:

```
$ git -C memory branch --contains HEAD
* (HEAD detached from 8f51421)
  live

$ git -C memory rev-parse live
a20e6898d776900ac71022a3f2589d15ccffabec

$ git -C memory log --oneline 'live@{u}..live'
(no output)
```

Nothing unpublished, nothing to lose.

### I2 — Quality gate is green, in full

```
$ PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit
# version consistency
Version consistent: 0.2.0
Tests cached (inputs unchanged)
# line limits
oversized-file: plugin/agents/corrector.md: 682 lines > 400
oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
# design links
design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
EXIT=0
```

The three `oversized-file:` lines are the allowlist reporting itself, not
failures. `scripts/check_line_limits.allow` records a ceiling for each, and
the script exits 0:

```
plugin/agents/corrector.md        682  pilfer defect 21 (corrector-family dedup)
plugin/agents/design-corrector.md 460  pilfer defect 21 (corrector-family dedup)
plugin/agents/outline-corrector.md 450 pilfer defect 21 (corrector-family dedup)

$ ./scripts/check_line_limits.sh; echo "EXIT=$?"
EXIT=0
```

Each ceiling equals the file's current count exactly, so any growth in the
three corrector agents turns the gate red. That is the ratchet working as
designed, and it is worth knowing before someone edits those files.

`Tests cached (inputs unchanged)` means the test sentinel short-circuited
pytest. The only tracked change since the last full run is a one-line
deletion in `.claude/handoff-todo.md`, which is not a test input.

### I3 — The version is correctly *not* bumped; `just release` bumps it

`release_preflight` requires plugin.json to hold the **last released**
version and refuses a pre-bumped manifest:

```
$ jq -r .version plugin/.claude-plugin/plugin.json
0.2.0
$ git describe --tags --abbrev=0
v0.2.0
$ plugin/bin/check-version-consistency.py
Version consistent: 0.2.0
```

Manifest equals tag, so the guard passes. `just release` defaults to a patch
bump and will produce `0.2.1` / `v0.2.1`. `just release minor` gives `0.3.0`.
No tag `v0.2.1` exists locally, and PyPI has no `edify-cli` 0.2.1:

```
$ curl -s -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/edify-cli/0.2.1/json
404
```

The previous release landed completely: PyPI has 0.2.0 (HTTP 200) and the
GitHub release `v0.2.0` was published 2026-09-02.

Given 68 commits carrying a design-graph split, a `/build` merge that retired
three skills, and a new markdown line gate, a **minor** bump is the better
fit than the default patch. That is my human partner's call, not mine.

### I4 — Every other release precondition verified against the tree

| `release.sh` precondition | Result |
|---|---|
| Manifest exists | `plugin/.claude-plugin/plugin.json` present |
| On `origin/HEAD` branch | `origin/main`, checked out `main` |
| `MARKETPLACE_DIR` set | `/Users/david/code/claude-plugins` via `.envrc` |
| marketplace.json exists | present |
| Entry points at `plugin/` subdir | `git-subdir` / `ddaanet/edify` / `plugin` |
| Marketplace repo clean | `git status --porcelain` empty |
| GitHub authenticated | logged in as `ddaanet`, scopes include `repo` |
| `UV_PUBLISH_TOKEN` set | set |
| Tools present | `jq`, `gh`, `uv`, `curl`, `bash`, `git`, `python3` |

The marketplace entry's `description` differs from plugin.json's, but
`bump_marketplace` overwrites it from the manifest on every release, so it
needs no action.

The `dev` prerequisite on the `release` recipe (`release BUMP="patch": dev`,
and `dev: format precommit`) runs `format` before `release.sh`. Since
precommit's `ruff format --check` and `rumdl fmt --check` both pass, that
format pass is a no-op and will not re-dirty the tree under the script's own
gate.

### I5 — Changelog covers the release window

`docs/changelog.md` carries twelve entries dated after the `v0.2.0` tag
(2026-09-02), each backed by a file in `docs/changelog/`: the release
mechanism as a decision, the pipeline hub splits, `/proof` verdicts, the
mechanical crosslink check, the TDD audit outcomes, recall resolving skills,
`ruff format --check` joining the gate, the design split into hub and nodes,
routing by need for a runbook, one routing node in `/design`, the
`/inline`+`/orchestrate` merge into `/build`, and the runbook dropping model
names.

Only two commits in the 68 predate the earliest post-tag entry:

```
$ git log v0.2.0..HEAD --oneline --reverse --until=2026-09-16
30ec9082 🐛 derive the marketplace subdirectory in the release script
8f325ed3 📝 review every edify skill and record the subagent reply cut
```

Both are covered — the first by the release-mechanism entry, the second by
the pipeline-hubs-split entry. No design-significant change is unlogged.

---

## To clear the blocker and release

```
cd /Users/david/code/edify
git add .claude/handoff-todo.md
git commit -m "🔧 snapshot the task frame before release"
git diff --quiet HEAD -- . ':(exclude)memory' && echo "release gate clear"
```

The last line must print `release gate clear`. Then, from a terminal outside
the Claude Code sandbox (see W3):

```
cd /Users/david/code/edify
just release minor    # or: just release    (patch → 0.2.1)
```

If it dies partway, `just resume-release` completes it. Each external step
probes what already landed before acting.

I made no commits, no pushes, no tags, no version changes, no branches, and
no edits to any file other than this report.
