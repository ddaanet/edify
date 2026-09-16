# plugin-dev:skill-reviewer on plugin/skills/proof (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — parts 2 and 3 pending.**

Files: `SKILL.md` (158 lines, 1048 words), `references/item-review.md` (78 lines, 571
words). Neither references any file under `plugin/fragments/`; that absence is itself
a finding, in part 3.

## Critical

**C1. The corrector dispatch three callers depend on does not exist.** Terminal
"apply" (SKILL.md:137-141) lists four steps, none dispatching a corrector. Three
callers say it does: `design/references/write-outline.md:159` ("On terminal action
'apply', /proof dispatches outline-corrector automatically and presents findings
before returning control"), `design/references/write-design.md:60` (same for
design-corrector), and `design/SKILL.md:150` ("outline-corrector dispatched by /proof
on revise/kill") — which names a different trigger from the first. Neither is
implemented. A fourth caller, `design/references/write-inline-plan.md:31`, cites a
"/proof Corrector Dispatch table" that does not exist in the proof skill.
Corroboration that this is lost behaviour rather than stale caller prose: `Agent` is
in `allowed-tools` (SKILL.md:8) and the body never dispatches an agent. Either add
the table and the apply-time dispatch, or strip the claims from all four callers.

**C2. The state line advertises an action vocabulary the body does not implement.**
SKILL.md:47 and :56 show the entry action list as `feedback, proceed, learn, suspend,
sync`. The body defines: verdicts `approve, revise, kill, skip` (:102-106); terminal
`apply, discard` (:137, :145); loop `learn, pending, brief, revisit` (:125-127, :151);
discussion `sync` (:118). Of the five advertised, only `learn` and `sync` exist;
`feedback`, `proceed` and `suspend` appear nowhere, while `apply`, `discard`,
`revisit`, `pending` and `brief` are real and unadvertised. This is the primary
user-facing affordance list, emitted at entry before the first item. `suspend` is
especially misleading given that `skip` is the real deferral verb.

## Major

**M1. `/proof` is ambiguous across two installed plugins.** Both `edify:proof` and
`ddaa:proof` are enabled and both trigger on the bare "proof" plus "validate" and
"review". Every caller invokes the bare form (`design/SKILL.md:150`,
`requirements/SKILL.md:155`, `runbook/SKILL.md:142`, `write-outline.md:159`,
`write-design.md:60`). A misroute to `ddaa:proof` would run a text-proofreading loop
over a runbook and look plausible. Qualify every call site as `/edify:proof`.

**M2. The description is trigger-first, against the house shape** (SKILL.md:4-7, 278
characters, 39 words). Every other edify skill opens with what it does. The
description renders verbatim in the skill list.

**M3. The glob-expansion command is broken.** SKILL.md:74 says to expand a glob "via
`rg --files` (Bash)". The reviewer ran it:

```
$ rg --files 'section-*.md'
rg: section-*.md: IO error for operation on section-*.md: No such file or directory (os error 2)
$ rg --files -g 'section-*.md' <dir>
<dir>/section-a.md
```

Bare `rg --files` takes a path, not a pattern. The instruction needs `-g`.

**M4. Per-item recall discards half the recall contract.** SKILL.md:100 calls
`Skill(skill: "edify:recall", args: "<that item's topic>")`, but the contract at
`recall/SKILL.md:15` is `"<plan-dir> — <topic>"`, whose step 1 (`recall/SKILL.md:38-44`)
resolves `<plan-dir>/recall-artifact.md` and reads every file it lists. Omitting the
plan dir skips that silently. Proof always knows the plan directory.

**M5. The iteration guard forbids what the next paragraph permits.** SKILL.md:122
refuses "skill chains to other skills or external plugins"; :125-127 lists `learn`,
`pending` and `brief` as available throughout iteration, where `pending` is the
handoff plugin and `brief` is `ddaa:brief`. Restate the guard as forbidding
execution-oriented chains, naming those three as exceptions.

**M6. Revisit is described as both in-iteration and post-completion-only.**
SKILL.md:149 heads Loop Actions "Available during and after item iteration" with
revisit as its only entry; :158 states "Revisit is post-completion only";
`item-review.md:70` sides with post-completion. The anti-pattern's rationale is
sound, so :149 is the line to fix.

**M7. `AskUserQuestion` sits in `allowed-tools` against a standing convention**
(SKILL.md:8, vs `memory/ddaanet/shared-claude.md`). Proof's prompts are already
inline text (SKILL.md:97). Proof is where the pull toward the banned pattern is
strongest, being pure interaction.

**M8. `p:` semantics is cited twice and defined nowhere** (SKILL.md:126,
`item-review.md:65`). A grep across `plugin/` and `docs/` returns only those lines.
Define it or point at the handoff plugin's mechanism.

**M9. `agents/learnings.md` is a host-repo path shipped inside a plugin**
(SKILL.md:125, `item-review.md:64`). It exists in this checkout; nothing guarantees
it in a consuming repo and neither file says what to do when absent. Contrast
SKILL.md:100, which reaches memory through the recall skill.

## Minor

**m1. Dangling requirement reference**: SKILL.md:100 "Per-item recall (FR-3)" — no
`plans/proof` directory holds that requirements document. Authoring context leaking
into shipped text.

**m2. The state-line emission table is incomplete** (SKILL.md:45-51): no row for the
most frequent transition, after a per-item verdict is recorded. "Accumulate"
(SKILL.md:116) is a discussion-round concept, so the per-item case is unaddressed.

**m3. The sections that should emit the state line never mention it** — neither
Entry (SKILL.md:72-76) nor Orientation (:79-84) refers to it.

**m4. Redundant restatement**: SKILL.md:129-133 repeats the table's "After sync" row
inside Iteration Guards, where it does not belong topically.

**m5. Verdict semantics are duplicated across the split**: SKILL.md:102-106 defines
all four; `item-review.md:48-58` re-lists five verdict cases under batch-apply, while
`item-review.md:46` defers back to SKILL.md. The reference is meant to hold detection
and format detail per its own framing at :3.

**m6. Revisit is documented twice at similar depth** (SKILL.md:151,
`item-review.md:70-78`), with the same two points in both.

**Fragments:** neither proof file reads anything under `plugin/fragments/`.
Defensible, since none covers review-loop mechanics, but `token-economy.md` is
arguably relevant and its do-not-repeat rule is exactly what the duplication above
violates.

## What passed

Imperative form is clean: zero second-person instruction subjects across both files,
verified by grep. Progressive disclosure is well judged — the core loop in SKILL.md,
detection tables and accumulation format in the reference, routed at the point of
need (SKILL.md:76). The Anti-Patterns section (:153-158) states each with its
consequence. Frontmatter is structurally valid and consistent with siblings. The
design rationale at :16, on why this is a skill rather than a reference file, is what
stops a future session from flattening it.

## Suggested order of work

The two critical items first, since they are cross-file contracts that surface no
other way. Then the broken `rg` command, the only finding that fails at runtime with
certainty. Then the vocabulary and guard contradictions. Duplication items are
cleanup and can wait.
