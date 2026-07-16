# Plugin Transition — Evaluation

Status: **evaluation only, nothing executed.** Written 2026-07-15.

Scope: the five directives — retire hooks, sort out fragments, adopt
`claude-plugin-dev` for release, evaluate merging the `plugin` submodule into the
parent, and reassess `token-efficient-bash`.

## Summary

Merging is feasible and both original rationales for the submodule are dead. The
release directive, as stated, cannot be carried out: `claude-plugin-dev` names
edify an explicit non-goal and lacks PyPI, submodule, dry-run and rollback
support. Hooks and `token-efficient-bash` are safe to delete. Fragments are
mostly duplicated in memory already, but the memory file that would receive them
is itself stale.

## 1. Merge the submodule into the parent

### Both rationales are gone

- **"Shared across repos"** — only edify's own `.gitmodules` references
  `ddaanet/edify-plugin`. No other repo on the machine consumes it.
- **"Marketplace needs a standalone repo"** — edify has **no entry** in
  `claude-plugins/.claude-plugin/marketplace.json` (12 plugins listed; edify is
  not among them). `docs/marketplace.md` still advertises
  `/plugin install edify@ddaanet` and is stale.

Even if edify were published, a subdirectory would suffice: the marketplace
already uses `"source": "git-subdir"` for four plugins (`ddaa` is
`url: ddaanet/skills, path: plugins/ddaa`). A merged `plugin/` could be published
that way against `ddaanet/edify`.

### What a merge must rewrite

Real code coupling is small and confined to the justfile:

| Site | What it does | Merge impact |
|---|---|---|
| `justfile:6` | `import 'plugin/portable.just'` | Path only; `portable.just` supplies `bash_prolog` + `precommit`/`test`/`format`/`lint`/`check`/`claude` |
| `justfile:148` | `plugin/bin/bump-plugin-version.py` | Path only |
| `justfile:149` | `plugin/bin/check-version-consistency.py` | **Breaks** — see below |
| `justfile:150` | `git add ... plugin/.claude-plugin/plugin.json` | **Currently broken; a merge FIXES it** |
| `justfile:270` | test sentinel hashes `git ls-files src/ tests/ plugin/hooks/ plugin/bin/` | Today contributes nothing (`git ls-files` cannot see into a submodule); after merge it starts working — intended |

`check-version-consistency.py` computes
`repo_root = Path(__file__).parent.parent.parent`, climbing out of the submodule,
and hard-codes the directory name `plugin`. It depends on being exactly three
levels below the repo root and needs a path rewrite on merge.
`bump-plugin-version.py` uses `parent.parent`, stays inside, and is
location-independent.

`pyproject.toml`, `src/`, and `.claude/` have **no** references into `plugin/`.
Test references are nominal (string fixtures, a synthetic tmpdir). The rest is
prose in `CLAUDE.md`, `README.md`, `agents/`, and `docs/superpowers/`.

### The merge fixes the release blocker

`just release` cannot complete today. `git add plugin/.claude-plugin/plugin.json`
fails with `fatal: Pathspec 'plugin/.claude-plugin/plugin.json' is in submodule
'plugin'` — a parent repo cannot stage a path inside a submodule. Verified by
executing `just release --dry-run` on 2026-07-15. Merging removes the submodule
boundary and the `git add` becomes valid, with no submodule commit/push/pointer
dance and no two-repo release ordering.

Related defects found in the same dry-run:

- `cleanup_release` reverts the parent with `git reset --hard`, which by design
  leaves submodule *contents* alone — so rollback left `plugin.json` bumped while
  `pyproject.toml` reverted, a dirty tree that blocks the next run. A merge makes
  this class of bug impossible.
- `trap ... ERR EXIT` fires `cleanup_release` twice.

### Verdict

Merge is low-risk and net-negative in complexity. The only real work is rewriting
`check-version-consistency.py`'s path computation and ~5 justfile paths. Two
repos, two histories, and a gitlink currently buy nothing.

Open question for the owner: does `ddaanet/edify-plugin` get archived, and does
the version-consistency invariant survive a merge at all? If `plugin.json` and
`pyproject.toml` live in one repo, the two-file lockstep and the scripts that
enforce it may be replaceable by a single generated value.

## 2. Release mechanism — the directive conflicts with the toolkit

`claude-plugin-dev` **excludes edify by design**:

> Don't add hybrid Python+plugin support to `release.just`. Repos like `edify`
> are deliberately out of scope. — `CLAUDE.md:91-94`

> **Hybrid Python+plugin repos (e.g. edify)** are out of scope. … Edify keeps its
> bespoke recipe. — `DESIGN.md:320-325`

Concrete gaps against edify's needs:

| Need | `claude-plugin-dev` |
|---|---|
| PyPI build/publish | **Absent** — no `uv build`/`uv publish`/`pyproject.toml` awareness anywhere |
| Submodule handling | **Absent** |
| Dry-run | **Absent** |
| Rollback | **Absent** |
| Two versions in lockstep | **Absent** — single-manifest model, `manifest=".claude-plugin/plugin.json"` hardcoded root-relative (`release.just:28`) |
| plugin.json bump | Present (jq) |
| marketplace.json bump | Present, via `$MARKETPLACE_DIR` |
| tag + push + `gh release` | Present |

Two further frictions:

- **Path.** `release.just` looks for `.claude-plugin/plugin.json` at the repo
  root. Post-merge, edify's sits at `plugin/.claude-plugin/plugin.json`. No
  search, no configuration.
- **Marketplace side effect.** `release.just` requires `MARKETPLACE_DIR` and
  synthesizes a marketplace entry from plugin.json if none exists
  (`release.just:88-104`). Since edify has no entry, adopting the toolkit would
  start publishing edify to the `ddaanet` marketplace.

Integration is git-subtree vendoring (`install.sh:63`,
`git subtree add --prefix=plugin-dev`) plus `import 'plugin-dev/release.just'`,
and it installs a PreToolUse `version-guard.sh` hook that **denies** any
Write/Edit changing plugin.json's `.version` — worth noting given the parallel
directive to remove hooks.

### Options

1. **Extend `claude-plugin-dev`** to support hybrid repos — reverses its
   documented decision and, by its own reasoning, obscures its main path.
2. **Keep edify's bespoke recipe** (now hardened by the pytest-md port) and adopt
   nothing. Matches the existing decision.
3. **Split the difference** — only viable if edify stops being a hybrid, e.g. the
   plugin becomes a separate published thing again, which contradicts the merge.
4. **Reconsider the exclusion** — the decision predates the merge; a merged edify
   is a different shape than the one that was ruled out.

Not actionable without the owner's call.

## 3. Hooks — retire

Two hooks in `plugin/hooks/`, both registered in `hooks/hooks.json` (Claude Code
auto-discovers this at a plugin root; `plugin.json` correctly does not reference
them):

- `pretooluse-block-tmp.sh` — denies Write/Edit under `/tmp/`. Enforces
  `tmp-directory.md`.
- `posttooluse-autoformat.sh` — runs `ruff format` + `docformatter` on `.py`.

They are **not vestigial in the sense of being dead code** — they fire, but only
via `just claude` (`plugin/portable.just`'s `claude` recipe runs
`claude --plugin-dir ./plugin`). `edify` appears in **no** `enabledPlugins`:
neither `.claude/settings.json:12-18` nor `~/.claude/settings.json`. Under a plain
`claude` launch, nothing from this plugin loads.

Overlap differs per hook, and the difference matters:

- `posttooluse-autoformat.sh` — genuinely redundant. `just format` / `just
  precommit` already run ruff + docformatter. Delete freely.
- `pretooluse-block-tmp.sh` — **not redundant.** `tmp-directory.md:7` claims
  "Permission enforcement: `Write(/tmp/*)` is denied in settings.json". **This is
  false.** `.claude/settings.json` denies exactly `["NotebookEdit",
  "WebFetch(domain:http-intake.logs.*.datadoghq.com)"]` — verified 2026-07-15. No
  `/tmp` entry exists. This hook is the *only* mechanical enforcement of the tmp
  rule.

So deleting `pretooluse-block-tmp.sh` leaves the tmp policy as prose only — and
that prose is itself false (above) and contradicts the current harness, which
assigns a scratchpad under `/tmp/claude-1000/…` and instructs agents to use it.
Deleting the hook is defensible, but do it knowing the rule then has zero
enforcement and a broken rationale. Decide the tmp policy (§4) and the hook
together, not separately.

### Live defect found while investigating

`plugin/.claude/agents -> ../agents/` (tracked symlink, committed Jan 27) is
**dangling**: it resolves to `plugin/agents`, deleted in `99920f4`. The loader
appears to resolve it relative to the plugin root, so it picks up the *parent's*
`agents/` directory and registers its prose documentation as spawnable agents.
Observed live: a session launched via `just claude` exposes `edify:README`,
`edify:ROADMAP`, `edify:learnings`, `edify:decisions:*`, and
`edify:guides:IMPLEMENTATION_STATUS` — a 1:1 match with `agents/*.md`, none of
which have agent frontmatter. Delete the symlink regardless of the hooks decision.

## 4. Fragments

All 8 are referenced exactly once each, all from `CLAUDE.md` (`:5`–`:21`), via
`@plugin/fragments/x.md`. Zero orphans.

The owner's position — they don't belong in a plugin, they belong in native
memory — runs into a complication: **`memory/operational-rules.md` already
mirrors most of them**, as one-liners:

| Fragment | Mirror in `memory/operational-rules.md` |
|---|---|
| `source-not-generated.md` | "Edit source, not generated output" |
| `code-removal.md` | "Delete obsolete code — no archiving, no commenting out" |
| `error-handling.md` | "Errors never pass silently — no `\|\| true`, no `2>/dev/null`" + "No sed escape" |
| `no-estimates.md` | "No estimates unless requested" |
| `no-confabulation.md` | "No confabulation — invented heuristics flagged as 'ungrounded'" |
| `communication.md` | "Report observable state", "No hedging or preamble", "Reference, never recap" |

Fragments carry the detail and rationale; memory carries the summary. So this is
not a migration into empty space — it is a **merge into an existing, partly
conflicting record**.

### What would be LOST, not relocated

Content that exists nowhere else, ranked by whether losing it costs anything:

**Worth not losing — live, general, no dead dependencies:**

1. `no-estimates.md:5` — "**Reuse is not measurement.** Citing numbers from a
   prior document does not satisfy 'measured data.'"
2. `no-confabulation.md:9` — the operational-thresholds extension: "Deriving
   thresholds from reasoning … or replacing one confabulated metric with a
   'cleaner' confabulated metric is still confabulation." The sharpest content in
   the directory; memory has none of it.
3. `project-tooling.md:3-15` — the recipe-before-ad-hoc rule *itself*. Memory
   holds only two gotchas derived from it, never the rule.
4. `project-tooling.md:45-51` — "Rule Suppression by Procedure": specific
   instructions must not suppress general operational rules.
5. `code-removal.md:32` — the ADR exception.

**Lost, but needs rewriting anyway:** `tmp-directory.md` entire. Memory has **no**
tmp policy, so dropping fragments deletes the project's tmp policy outright — but
as written it contains a false settings.json claim (§3) and contradicts the
harness scratchpad, so it cannot be relocated as-is.

**Lost, no loss:** `communication.md:9-13` (its remediation is already applied —
no output-style plugin is enabled); `project-tooling.md:35-43` (built entirely on
the deleted `_worktree` CLI); `error-handling.md:15`'s sed rationale (the rule
survives in memory; only the argument goes).

### Obsolete content that should not be migrated anywhere

- `tmp-directory.md:7` — false claim about settings.json (§3); `:8` cites the
  deleted runbook pipeline; `:5` ("never in `/tmp/` or `/tmp/claude/`") is the
  inverse of what the harness now instructs.
- `source-not-generated.md:3` names `prepare-runbook.py` — deleted. Memory's
  mirror names "agent-core" — the pre-rename name of `plugin/`. Both stale.
  Compounding: `agents/README.md:11,15` claims CLAUDE.md is "generated from
  fragments" by `agents/compose.sh` — **that script does not exist**, and there is
  no `compose` command in `src/edify/cli.py`. CLAUDE.md is hand-written.
- `project-tooling.md:25` — cites `execution-routing.md`, deleted in `99920f4`.
- `project-tooling.md:31` — "Anthropic ships 28 official plugins", an undated hard
  count. Exactly what `no-confabulation.md` targets.
- `communication.md:9-13` — remediation already applied.

### Prior art — this directory was already triaged once

`memory/strategic-pivot.md:12` records a prior pass applying a
system-prompt-duplication test to this exact directory: "`error-handling` /
`project-tooling` kept as fragments, `token-economy` / `pushback` /
`tool-batching` cut (system-prompt duplicates)." The two fragments with the most
unique content are the two someone already decided to keep on purpose.
`fragments/` has not been touched since `99920f4` (2026-05-23).

That is a reason to be careful with a second "these are redundant" pass: the
redundancy that remains is the redundancy that survived the last one.

**`memory/operational-rules.md` is itself stale** and should not be treated as the
good copy. It still cites the torn-down pipeline: "/inline or /orchestrate
required for corrector gates", "agent-core generates agents/skills", "Plan-backed
tasks mandatory — every pending task references `plans/<slug>/`",
"Worktree-tasks-only on main", "Max 5 concurrent worktrees", "Handoff captures
conclusions". Per `strategic-pivot`, that machinery is deleted.

### The mechanism question

`@plugin/fragments/x.md` includes are **deterministic** — CLAUDE.md loads them
every session, verbatim. Memory recall is **retrieval-based** and surfaces inside
`<system-reminder>` blocks as background context. Moving an always-on behavioral
rule from a guaranteed include to a recalled memory is a change in enforcement
strength, not just location. Worth deciding deliberately: which of these rules
must be present every session (→ CLAUDE.md prose, inline), and which are
situational (→ memory)?

A third option exists and may be the real answer: fragments were a *sharing*
mechanism for a multi-repo plugin. With the merge, they can simply be **inlined
into CLAUDE.md** — no plugin, no memory, no include indirection.

## 5. `token-efficient-bash` — retire

The owner's suspicion is substantially correct.

- **Nothing depends on it.** The only `set -xeuo pipefail` / `exec 2>&1` hits
  outside the skill's own directory are `justfile:187` and `plugin/README.md`.
  The three real scripts — `plugin/hooks/posttooluse-autoformat.sh:2`,
  `plugin/hooks/pretooluse-block-tmp.sh:5`, `scripts/check_line_limits.sh:4` —
  all use plain `set -euo pipefail`.
- **The repo's own bash contradicts its central claim.** `justfile:186-199` makes
  `-x` opt-in behind `trace`, then defines `show`/`visible` — the explicit echo
  helpers the skill says tracing makes unnecessary.
- **The headline is unsourced.** "40-60% token reduction" (`SKILL.md:3`,
  `plugin/README.md:133`) has no citation. Per no-confabulation, it should not
  stand.
- **It ships a defect.** `SKILL.md:187` and `references/examples.md:68`:

  ```bash
  if grep -q "pattern" config.yaml || true; then
  ```

  `|| true` makes the condition always true; the `else` at `SKILL.md:189` is dead
  code. Verified by execution 2026-07-15: with the pattern absent, the if-branch
  still runs. The skill contradicts itself at `SKILL.md:196` ("No `|| true` needed
  in if condition") without retracting the broken example, and `examples.md:84-86`
  ships fabricated output presenting the bug as correct.
- **It is an outlier.** The other five skills are gated, artifact-producing
  protocols aimed at the requirements mission; this is a style guide for a syntax
  fragment. It alone lacks `allowed-tools:` and `user-invocable: true` — so
  `CLAUDE.md:33`'s claim that it is "invoked via slash command" is wrong.

### What must not be waved through

1. **The `|| true` exception must be reworded, not relocated.** Two sites define
   it *by deferring to the skill*, so both break on deletion regardless of what is
   decided about fragments:
   - `plugin/fragments/error-handling.md:11` — "In bash scripts using
     token-efficient pattern, `|| true` is used to handle expected non-zero exits
     (grep no-match, diff differences). See `/token-efficient-bash` skill."
   - `memory/operational-rules.md:16` — "(except token-efficient bash expected
     exits)" — launders the skill's name in as the justification.

   The exception's *authority* is the skill, but its *content* is a property of
   the tools: `grep` exits 1 on no-match, `diff` exits 1 on differences. Those
   non-zero exits encode a **result**, not a failure — so `|| true` there isn't
   suppression, it's correct. That fact holds whether or not any skill exists.
   Reword both to name the **condition** instead of the skill: *commands whose
   non-zero exit encodes a result rather than a failure*. The exception is live —
   the justfile relies on it (`justfile:70-75`).
2. **Two pieces of real knowledge** should be confirmed as covered elsewhere
   before deletion, not assumed: the `((count++))`-under-`set -e` trap
   (`SKILL.md:144-175`) and the `trap "cd $(printf %q "$PWD")" EXIT` pattern
   (`directory-changes.md:12-26`). Both plausibly sit inside the installed
   `shell-scripting:shell-gotchas` skill, and cwd-drift is now enforced by the
   `cwd-safety` hook — but that should be verified.

## 6. Incidental staleness found

Independent of any decision above:

- `docs/marketplace.md` — advertises `/plugin install edify@ddaanet`; no such
  marketplace entry exists.
- `plugin/README.md` — describes "18 skills, 14 sub-agents, 23 fragments, 4
  hooks", the deleted `/design → /runbook → /orchestrate` pipeline, `templates/`,
  `configs/`, seven `bin/` validators, and an install step `just sync-to-parent`
  that is not a recipe. Lists `/reflect`, `/worktree`, `/release-prep`,
  `/handoff-haiku`, `/plugin-dev-validation`, `/gitmoji` — none exist.
- `bump-plugin-version.py` — rewrites `EDIFY_VERSION` in
  `hooks/sessionstart-health.sh`, deleted in the teardown. Guarded by
  `if health_sh.exists()`, so the block silently no-ops and its `sys.exit(1)` is
  unreachable.
- `plugin/bin/deliverable-inventory.py` — referenced nowhere outside `plans/`.
- `agents/decisions/deliverable-review.md:107` — points at
  `plugin/fragments/review-requirement.md`, which no longer exists.
- `agents/README.md:11,15` — claims CLAUDE.md is generated from fragments by
  `agents/compose.sh`. No such script; no `compose` command in `cli.py`. CLAUDE.md
  is hand-written. (Note this one interacts with the `source-not-generated` rule:
  the docs assert a generator that doesn't exist, which is precisely the confusion
  that rule exists to prevent.)
- `agents/learnings.md:5` — routes rules *into* `plugin/fragments/*.md` via
  `/codify`, a deleted skill. The only place naming fragments as a destination.
- `plugin/README.md:35` — includes `@plugin/fragments/execution-routing.md`,
  deleted.
- `plugin/bin/deliverable-inventory.py:36` — classifies any `.md` under
  `fragments/` as "Agentic prose" by path substring; would silently reclassify to
  "Human docs" if the directory moved.
- `skills/requirements` — body still says output is consumed by `/design` and
  `/runbook`, both deleted.
- `plugin/.claude/settings.json` sets `"plansDirectory": "plans/"`; the parent
  sets `"plans/claude/"`.
- `memory/operational-rules.md` — stale pipeline references (see §4).
- `refs/remotes/origin/HEAD` pointed at a nonexistent `origin/tmp`, making the
  release recipe compute the main branch as `tmp`. Fixed 2026-07-15 with
  `git remote set-head origin --auto` (local ref state only).
- `dist/` holds `claudeutils-0.0.1`/`0.0.2` artifacts from before the rename —
  which the old bare `uv publish` would have re-uploaded. `just clean` clears them.

## Recommended sequence

Ordering matters; the merge changes the ground the others stand on.

1. **Decide the release question** (§2) — it is the only true blocker and it needs
   the owner.
2. **Merge the submodule** (§1) — fixes the release `git add`, unblocks
   everything, and makes the fragment question simpler (inlining beats migrating).
3. **Delete the dangling `.claude/agents` symlink** (§3) — independent,
   unambiguous, no decision needed.
4. **Delete `posttooluse-autoformat.sh`** (§3) — genuinely redundant with
   `just format`.
5. **Decide the tmp policy, then `pretooluse-block-tmp.sh`** (§3 + §4) — coupled.
   The hook is the only enforcement; the prose is false and fights the harness.
   Either fix the rule and keep the hook, or drop both deliberately.
6. **Delete `token-efficient-bash`** (§5), *after* rewording the `|| true`
   exception at both sites to name the condition, and confirming shell-gotchas
   coverage.
7. **Sort fragments** (§4) — last, because post-merge "inline into CLAUDE.md" may
   be the answer, because `memory/operational-rules.md` needs its own de-staling
   first, and because the surviving redundancy already survived one triage pass.
