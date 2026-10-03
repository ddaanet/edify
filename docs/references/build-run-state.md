# Build run state

Decisions governing how `/build` keeps and reads a run's state in git: when a
run is resumed, where its bases come from, which files are its changes, what
counts as a clean tree, what happens to dirt, how the review gate groups files,
and what a commit subject is for. Read this before changing `/build`'s entry
gate, resume, phase boundary, review gate or any of its scripts.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`. Every decision here rests on D-86
(`docs/references/pipeline-contracts.md`): a report rides the commit whose work
it reports, so report history is a structural record of what landed.

**D-88 — A `/build` run is resumed when it holds an item report, and report
history gives its base.** Any `plans/<job>/reports/item-*.md` on disk means the
run is resumed (`/build` §1); none means fresh. Only `item-*` counts, because
planning reports — `outline-review.md`, `runbook-review.md`, `explore-*` — share
the directory. The test holds because every item leaves a report and its first
commit carries it (D-86), which is why `/build` §4.1 reviews the uncommitted
diff and writes or takes `item-N-M.md` before the item's one commit. The run's
base is the parent of the earliest commit adding an item report:

```bash
git log --no-renames --diff-filter=A --reverse --format=%H \
    -- ':(glob)plans/<job>/reports/item-*'
```

first line, then its parent. The `:(glob)` magic keeps `*` inside one path
component — git's default `*` also matches `/`, so `reports/item-x/notes.md`
would count — and `--no-renames` counts a report renamed into place as added.
`changed-files.sh` re-derives the base wherever it is needed (D-90), and nothing
needs it before the first item commit, so there is no baseline file, no capture
step and nothing to delete. A finished job re-invoked reads as resumed: its
inventory finds every item landed and goes to finishing.

**D-89 — A phase boundary has landed when the run holds a commit touching its
corrector report.** Phase P has landed when

```bash
git log -1 --format=%H <run base>..HEAD \
    -- plans/<job>/reports/phase-<P>-corrector.md
```

prints a hash. The key is the report's path, never the commit subject: a
boundary always commits its corrector report, so the path is structural and the
subject a label (D-94). The range excludes an earlier run's commits; leaving out
`--diff-filter=A` counts a report the run modified as well as one it added; `-1`
resolves a report committed twice to the later commit, which carries the later
fix. `changed-files.sh <job> --phase` implements the rule: its base is the
latest commit in `<run base>..HEAD` touching
`:(glob)plans/<job>/reports/phase-*-corrector.md`, or the run base when no
boundary has landed. `--phase` falls back to an earlier base when a boundary
commit was skipped, which would widen phase P's review over phase P-1's work, so
at P>1 `phase-boundary.md` runs the landed query for P-1 first and STOPs when it
is empty or prints a hash other than `--phase`'s `BASE:`. An empty base is never
substituted: `git diff --name-only HEAD` is a working-tree diff that passes an
empty-field check with the wrong list. On resume the inventory covers boundaries
as well as items (`escalation.md` §Resuming); a boundary report present but
uncommitted is finished when complete and rerun when partial, because the
corrector writes its report before it applies any fix.

**D-90 — A changed-files list is the committed diff since the base, minus the
exempt paths and the job's own record, and one script produces it.**
`plugin/skills/build/scripts/changed-files.sh <job>` derives the run base
(D-88), prints `BASE: <sha>`, then the `<base> HEAD` diff with the D-91 exempt
paths and `plans/<job>/` removed; with no committed item report it exits 1 with
`NO-BASE:`, and `--phase` takes the phase base instead (D-89). The `HEAD` form
keeps uncommitted exempt dirt out, but not the exempt paths a `/handoff` or
memory-pointer commit lands during the run; those are not the run's work, so the
list drops them by name, as `verify-step.sh` does. `plans/<job>/` goes too: the
run's reports and `runbook.md` list revisions are its record, not its
implementation. The exempt alternation lives in one sourced file,
`exempt-paths.sh`, which both scripts read. Every site that needs the list or
the base calls the script: the phase boundary, the review gate, and triage,
whose two diffs take the same `<base> HEAD` form. The working-tree form,
`git diff --name-only <base>`, stays for uncommitted work — `/review`, and the
`/build` §4.1 corrector that reviews an item before its one commit.

**D-91 — Any change is dirt, except three paths dirty by convention.**
`verify-step.sh` is `/build`'s one definition of a clean tree, at the entry gate
and after every committed step. A file a dispatch created and forgot to stage
shows only as untracked, so untracked counts, and the status runs with
`--untracked-files=all` so an untracked `inbox/` lists its files rather than one
directory line the exemption cannot judge. Three paths are exempt in any
porcelain state but a rename or copy: `memory` (the gitlore submodule),
`.claude/handoff-*.md` (`/handoff` and `/precompact` leave it modified or
staged) and `inbox/*.md` (briefs dropped or updated uncommitted on purpose, so
sessions need not coordinate), each `*` a single path component. All three are
ddaanet workflow conventions shared by every repo that runs the plugin, so the
list is hardcoded, in `exempt-paths.sh`. Exempting them is safe because every
committing step, dispatch or orchestrator, stages its paths by name, never
`git add -A`, and commits with `git commit -- <paths>`, so exempt dirt never
enters a commit even when already staged. A rename or copy line fails closed as
DIRTY even when both sides are exempt, since `old -> new` is two paths that one
match cannot judge. A listing the `sandbox-lies` hook annotates as sandbox masks
is re-run once, not remediated: masks reach an unsandboxed reader while a
sandboxed Bash call runs concurrently.

**D-92 — Dirt is unfinished work to examine and finish; nothing reverts by
default.** The gate held the tree clean before an item, so non-exempt dirt after
it is that item's own work, unless someone touched the tree in between. The
named agent is resumed to finish its work and commit it by name; with no owner
or no progress, a fresh dispatch composed from the item carries the dirt as a
prior attempt's work to examine and finish; that failing, it escalates with the
listing and the dispatch's findings (`escalation.md` §Post-item remediation).
After a kill no agent owns the dirt, so the orchestrator examines each dirty
path's diff for relevance to the first remaining item and for quality: what is
relevant and sound joins that item's dispatch as prior work, the rest escalates.
A tdd slice's implementation-side dirt escalates unless its RED and test-review
reports are on disk, because RED's proof needs unchanged code. My human partner
decides escalated dirt path by path, and a path decided for revert is reverted
in session by one call,
`git restore --source=HEAD --staged --worktree -- <paths> && rm -- <untracked paths>`;
the orchestrator never cleans up on its own judgement.

**D-93 — Review-gate groups are four fixed rows, with fixed slugs.** The
`/build` review gate routes implementation files only; planning artifacts route
by artifact (D-26). Its groups, which are also its dispatch names, are
`review-code` (code and tests, and the default for any file kind no row names),
`review-skill` (skill definitions and the agent-instruction prose they load: a
skill's `references/` nodes and any shared instruction file kept outside a
skill), `review-agent` (agent definitions) and `review-design` (the living
design graph under `docs/`). A file kind is always classed into an existing row,
never a new group, by the one rule in `dispatch-composition.md` §Naming and
resumption. `review-design` goes to `edify:corrector` with
`craft:design-doc-writing` named as its criteria source, as the agent row names
`plugin-dev:agent-development`, and the report notes the fallback when `craft`
is absent. *Grounding:* a free one-word slug per routed group did not determine
the names; one run produced `review-code`, `review-skill`, `review-agents` and
`review-fragments`, mixing singular and plural and minting a group the routing
table does not have.

**D-94 — `/build` commit subjects name the job, and are labels only.** Every
`/build` commit takes one of four subjects:
`<type>: <job> Item N.M[/k] — <title>` for items and slices, the code-review and
list-revision commits included; `<type>: <job> Phase P boundary`;
`<type>: <job> Review gate`; `<type>: <job> Finish`. `<type>` is the executor's
choice, and the gitmoji `commit-msg` hook rewrites only that prefix. The subject
serves a human reading `git log` and keeps two jobs' commits apart. Nothing
mechanical keys on it: resume, inventory and base read report history (D-88,
D-89), and `tdd-auditor` resolves each slice commit as the commit adding its
report (D-86), reading the label only to account for a slice's other commits.

## Rejected alternatives

**A baseline file, `tmp/build-baseline-<job>`, for the run's base** — lost with
a worktree, a clone or `just clean`, and then silently recaptured at the wrong
commit (D-88).

**Commit subjects as the resume or boundary key** — a typo breaks a convention,
where a committed report is structural (D-88, D-89, D-94).

**A committed start marker** — a commit to say what the log already says (D-88).

**A stored phase base, or `HEAD~N`** — a `tmp/build-phase-base` file is one more
piece of state a resumed run must trust, and a phase's commit count varies with
slices and review commits (D-89).

**The changed-files query and the exempt regex spelled out in prose at each
site** — four sites, and a prose copy of a script's regex drifts (D-90).

**Filtering or gitignoring the sandbox-mask names** — a filter hides real files
sharing the masked names, and those `.claude/` names are legitimately versioned
in other repos, whose `.gitignore` the plugin cannot rely on (D-91).

**Reverting dirt by default** — it discards work the run already paid for
(D-92).

**A `verify-step.sh --revert` mode** — a tested wrapper around two commands, on
a path reached only by explicit decision (D-92).

**A listing token guarding the revert** — it guards only against a concurrent
session on the same tree (D-92).

**A mechanical item scope for dirt** — every plan would have to declare one
(D-92).

**A new review group per file kind** — free slugs did not determine the names
(D-93's grounding), and the text `/build` ships names the class of shared
instruction file, never one repo's directory such as edify's `plugin/fragments/`
(D-93).

**`edify:design-corrector` as the design-graph reviewer** — it reviews
`plans/<job>/design.md`, a planning artifact (D-93).
