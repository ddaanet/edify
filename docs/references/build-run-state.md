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
diff and writes or takes `item-N-M.md` before the item's one commit. Work with
no `Item N.M` — the task an invocation names, or a design or outline without
items — is one item, Item 1.1, so every run leaves an item report: a design
without items carries general work only (D-83), which one item executes, at the
cost of resume granularity, since a kill mid-item re-runs the whole item. The
run's base is the parent of the earliest commit adding an item report:

```bash
git log --no-renames --diff-filter=A --reverse --no-show-signature --format=%H \
    -- ':(glob)plans/<job>/reports/item-*'
```

first line, then its parent. The `:(glob)` magic keeps `*` inside one path
component — git's default `*` also matches `/`, so `reports/item-x/notes.md`
would count. `--no-renames` is there for uniformity with the script's diff only:
a path-limited log pairs no rename source from outside its pathspec, so a report
renamed into place reads as added either way. `changed-files.sh` re-derives the
base wherever it is needed (D-90), and nothing needs it before the first item
commit, so there is no baseline file, no capture step and nothing to delete. A
finished job re-invoked reads as resumed: its inventory finds every item landed
and goes to finishing.

**D-89 — A phase boundary has landed when the run holds a commit touching its
corrector report.** Phase P has landed when

```bash
git log -1 --no-show-signature --format=%H <run base>..HEAD \
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
exempt paths and the pipeline's record, and one script produces it, for the
phase boundary, the review gate and triage alike.**
`plugin/skills/build/scripts/changed-files.sh <job>` derives the run base
(D-88), prints `BASE: <sha>`, then the `<base> HEAD` diff with the D-91 exempt
paths, `plans/<job>/` and the triage log,
`plans/reports/triage-feedback-log.md`, removed, and `--phase` takes the phase
base instead (D-89). In a repo with commits and no committed item report it
exits 1 with `NO-BASE:`. A usage error or a git failure exits 2 with `ERROR:`,
and an unborn `HEAD` is a git failure, so it exits 2 too, never `NO-BASE:`. The
`HEAD` form keeps uncommitted exempt dirt out, but not the exempt paths a
`/handoff` or memory-pointer commit lands during the run; those are not the
run's work, so the list drops them by name, as `verify-step.sh` does.
`plans/<job>/` goes too: the run's reports and the list revisions in the file
hosting its items — `runbook.md`, or the `outline.md` or `design.md` routed to
`/build` — are its record, not its implementation. The triage log goes for the
same reason: it is the pipeline's record across jobs, and a closing commit lands
it. It goes by name, not with the rest of `plans/reports/`, which is where an
Investigation's deliverable goes (`/design`'s artifact-destination table); D-82
routes Investigation to `/build`, so that deliverable stays on the list, under
review and counted. The exempt alternation lives in one sourced file,
`exempt-paths.sh`, which both scripts read. Every site that needs the list or
the base calls the script. Triage, `plugin/bin/triage-feedback.sh <job>`, takes
no base: it runs the script itself and counts its list, so its evidence is the
set the review gate reviewed. Files changed is the length of the list, and
behavioural code is read from the `<base> HEAD` diff of those paths only, given
as literal pathspecs. Its report count looks past the list, which drops the
job's record: it counts the reports `<base> HEAD` adds directly under
`plans/<job>/reports/`, excluding the `item-<N>-<M>.md` report every item leaves
and the review reports (`review.md`, `review-*.md`, `final-review.md`,
`tdd-audit.md`). Slice, refactor and phase-boundary reports count, and planning
reports committed before the base fall outside the range. Both drops keep a
re-run on the set the first run measured: a finished job re-invoked runs triage
again after its closing commit has landed the triage log and `tdd-audit.md`, so
with either in the evidence the re-run's row differs from the first, the log's
skip of a row equal past its date does not fire, and a second row is logged,
with a verdict that can flip. A `NO-BASE:` or `ERROR:` from the script, or a git
or grep failure of triage's own, stops triage with exit 2, no verdict and no log
row. The working-tree form, `git diff --name-only <base>`, stays for uncommitted
work — `/review`, and the `/build` §4.1 corrector that reviews an item before
its one commit.

**Limitation:** the base query and the `<base> HEAD` range read the job branch
as linear. A merge of `main` into the job branch, or another session committing
on the branch, puts commits that are not the run's into the range, and their
paths into the list. A report added only in a merge commit is invisible to the
base query, which then gives `NO-BASE:` (probed on git 2.47.3). How often either
happens is unmeasured.

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
match cannot judge. A listing annotated as sandbox masks is re-run once, not
remediated: masks reach an unsandboxed reader while a sandboxed Bash call runs
concurrently. The annotation comes from the `phantom-untracked` detector of the
optional `sandbox-lies` plugin's Bash hook. Without that plugin no listing is
annotated, so the re-run never fires, and a masked listing reads as dirt.

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
`git restore --source=HEAD --staged --worktree -- <tracked or indexed paths> && rm -- <untracked paths>`,
dropping either half that has no paths, since both commands error on an empty
operand list; the orchestrator never cleans up on its own judgement. A failed
fix already committed is not reverted by default either. It escalates to my
human partner with the commits since the last clean commit before the failed
item and what the attempt found. Only the commits they decide to revert are
reverted: newest first, each with `git revert --no-commit <sha>`, then the
reverted paths committed by name, subject
`<type>: <job> Item N.M[/k] — revert failed fix`; never `git reset`, which
discards history (`escalation-acceptance.md` §Rollback protocol).

**D-93 — Review-gate groups are four fixed rows, with fixed slugs.** The
`/build` review gate routes implementation files only; planning artifacts route
by artifact (D-26). Its groups, which are also its dispatch names, are
`review-code` (code and tests, and the default for any file kind no row names),
`review-skill` (skill definitions and the agent-instruction prose they load,
meaning their `references/` nodes and the shared instruction files a skill loads
from outside itself), `review-agent` (agent definitions) and `review-design`
(the living design graph under `docs/`). An instruction file no skill loads,
such as `CLAUDE.md` or `.claude/rules/*.md`, matches no row and takes the
`review-code` default. A file kind is always classed into an existing row, never
a new group, by the one rule in `dispatch-composition.md` §Naming and
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

**Triage keeping a base argument and filtering the raw diff itself** — a second
copy of the list's filters, which drifts from the script's as a prose copy does
(D-90).

**A landed check on triage keyed on the triage log** — the log is shared across
jobs, so another job's closing commit on the branch would skip this job's triage
(D-90).

**Triage dropping its own log path from the list** — a second copy of the list's
filters, as above (D-90).

**The list dropping all of `plans/reports/`** — an Investigation's deliverable
lands there, so the review gate would not review it and triage would not count
it; only the triage log, which a closing commit lands, is dropped (D-90).

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
