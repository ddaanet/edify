# edify pipeline defects surfaced by the 2026-08-13 comparison read

Observed in the text of `plugin/skills|agents|docs|bin` during the
pilfer-superpowers analysis. Repair backlog, independent of pilfering.

**Status: cleared 2026-08-13.** All 33 items were re-verified against the source
before any edit — every claim still held. Dispositions below. Two items are
subsumed by a pending rewire, four are parked for pilfer FR-12, and the rest are
fixed.

## Fixed

### Stale references / dangling names

1. **`scripts/create-plan-agent.sh` resolved the renamed `agents/task-execute.md`.**
   Deleted, along with `docs/pattern-plan-specific-agent.md` and
   `docs/pattern-weak-orchestrator.md` — the whole plan-specific agent scheme is
   retired (see *Pending rewire* below). References purged from `CLAUDE.md`,
   `plugin/README.md`, `docs/migration-guide.md`, `agents/learnings.md`, and four
   `agents/decisions/` files.
2. **`skill-reviewer` / `agent-creator` are plugin-dev agents, not edify's.**
   Root cause was sharper than recorded: they were named *bare*, and a bare
   `subagent_type` never resolves — the plugin prefix is mandatory even for a
   plugin's own agents (`memory/ddaanet/cc-agent-discovery.md`). Every dispatch
   site across the pipeline was namespaced (`edify:corrector`,
   `plugin-dev:skill-reviewer`, …), and `fragments/review-requirement.md` now
   states the namespacing rule plus a fallback to `edify:corrector` when
   plugin-dev is absent. Deliberately does not prejudge pilfer Q-1.
3. **`skills:` frontmatter naming non-existent skills.** Removed from all nine
   agents. `runbook-corrector` now invokes `Skill(skill: "edify:review-plan")` in
   its body, matching the convention every other agent already used.
4. **`Bash: recall diff <job-name>`** — no such command. All four sites now
   re-invoke `edify:recall` and reconcile against the existing artifact.
5. **`/plan`, `plan-adhoc`, `plan-tdd`** — retired skill names. Updated to
   `/runbook` in `review-plan/SKILL.md` and `runbook-outline-corrector.md`.
6. **`/review-analysis`** — never existed. `docs/tdd-workflow.md` routes Stage 5
   to `edify:tdd-auditor`.
7. **`docs/general-workflow.md`** — duplicate `### /design` entries merged;
   duplicate `.claude/handoff-task.md` lines deduped in both workflow docs; both
   change logs brought forward.

### Contradictions

8. **Orchestrator model tier.** Settled as **Sonnet** (user decision): the live
   `/orchestrate` skill wins. `general-workflow.md`'s Model Selection table and
   Stage 4 updated; the Haiku rationale died with the pattern docs.
9. **`examples.md` Cycle 1.1 demonstrated the ImportError-as-RED anti-pattern**
   that four other files prohibit. Rewritten to the prescribed form: a separate
   Bootstrap step with an uncommitted stub, RED expecting a behavioral
   `AssertionError`. Two further violations in the same example — a
   `pytest ::selector` where `just green` is required, and a stale success
   criterion — were fixed at the same time. The corrupted find-and-replace string
   was repaired in both `examples.md` and `prepare-runbook.py`'s
   `DEFAULT_TDD_COMMON_CONTEXT`.

### Verification gaps

12. **`verify-green-paths` missing from the Phase 3.5 invocation list.** Added,
    and documented as the deterministic checker for review-plan §3.5's rule.
13. **`--skip-*` flags had no stated legitimacy conditions and a SKIPPED report
    looked like a run.** The flag now takes a mandatory `REASON`; the report
    records it and states "This check did NOT run. Do not read this report as
    evidence of conformance." Legitimacy conditions documented: only when the
    check *cannot* run, never to get past a failure.
14. **TDD-only validators passed vacuously on general/inline runbooks.** The four
    cycle-based checks now report `NOT-APPLICABLE` with a reason instead of
    `PASS` when the runbook declares no cycles. Phase 3.5 now tells the reader to
    read the result line, not just the exit code.
    *(12–14 covered by `tests/test_validate_runbook_reporting.py`, which also
    de-orphans `tests/fixtures/validate_runbook_fixtures.py` — 400 lines of
    fixtures left behind when the validator suite was deleted in the 2026-05
    teardown.)*
15. **`/orchestrate` §3.0 inline review threshold left to the executing model.**
    Now defers to the concrete Proportionality rule already in
    `fragments/review-requirement.md` (≤5 net lines / ≤2 files / no behavioral
    change) rather than restating a vaguer version of it.
16. **`/requirements` had no failure path.** Added a STOP Conditions section
    (four conditions, all user-decision points) and made the "sole gate is
    `/proof`" consequence explicit.
17. **`triage-feedback.sh` detected behavioral code in Python/JS only.** Regex
    broadened to keyword-declaration languages plus POSIX shell functions,
    anchored after the `+` so commented lines do not match, with the residual
    limitation stated in a comment. Kept the non-`-q` grep deliberately: the
    script sets `pipefail`, and an early-exiting consumer would SIGPIPE
    `git diff`.
    Also fixed here, from the task frame rather than this list: the multi-group
    review dispatch false positive. A run writing `review-<group>.md` per group
    and no plain `review.md` was reported as "review gate may have been
    bypassed".

### Brittleness

23. **Phase 0.95 discriminated by the mere presence of a `## Execution Model`
    heading.** The heading is now stated as a literal contract, and an outline
    that specifies dispatch protocol *without* the heading triggers a STOP-and-ask
    instead of a silent promotion.
24. **Ungrounded thresholds.** The un-caveated ones are now annotated: >8
    items/phase, 40% phase share, 350-line growth, 150k context refresh, >5
    pending tasks. The 350-line rule cited a "400-line enforcement threshold" —
    no script or hook enforces it, so the claim was removed rather than
    re-labelled.
25. **Recall-artifact null sentinel matched by `startswith("null")`.** A real path
    such as `nullable-handling.md` was silently dropped; now `^null\b`. The
    artifact format contract is documented at the parser.
26. **`just green` / `just dev` were host-repo-only.** Both moved into
    `plugin/portable.just` and removed from the host `justfile`, so an adopting
    project gets the recipes the pipeline tells it to run. `verify-red.sh` no
    longer hardcodes pytest — `EDIFY_TEST_CMD` overrides it.
27. **">15 messages" resume cutoff was unobservable** — no tool reports another
    agent's message count. Replaced in both sites with an observable rule: resume
    once; a resumed agent that fails to progress is the signal to launch fresh.

### Redundancy / routing

22. **`/inline` Delegation Protocol Summary table.** All seven rows were stated in
    full 70 lines above. Table deleted.
29. **`/review` collides with Claude Code's built-in.** `docs/shortcuts.md` now
    lists it as `/edify:review` with the distinction stated. (A duplicate
    `/handoff:handoff` row in the same table was removed.)
30. **`/review` calls itself "the protocol used by review/correction agents"
    while using `AskUserQuestion`, which a delegated corrector cannot.** Rewritten:
    the two share review *axes*, not interaction model. A delegated reviewer
    reaching for a question has hit a dispatch-prompt defect.
31. **`review-plan` is `user-invocable: false` but described as user-triggered.**
    Description rewritten as agent-facing, naming `edify:runbook-corrector` as
    the entry point.
32. **`/design` Simple → `/inline` re-runs recall unless the `execute` token is
    passed.** The token is kept — the recall artifact cannot replace it, since its
    presence on disk says nothing about *this* session's context — but `/inline`
    must now announce which entry path it took, making a dropped token visible
    instead of silently costing a redundant pass.
33. **`/design` Phase 0 had two overlapping decompositions.** Composite and
    Companion ran the same procedure and differed only in where the item list came
    from. Merged into one **Multi-Item Decomposition** rule with two detectable
    triggers, which removes the judgment call rather than documenting it.

### Found while fixing, not on the original list

- `docs/migration-guide.md` linked four files that do not exist
  (`templates/CLAUDE.template.md`, `templates/README.md`,
  `migrations/001-separate-learnings.md`). A sweep of every relative link under
  `plugin/` found no others.
- `session.md` — the retired task frame — was still named 50 times across docs,
  fragments, and skills, including in `task-context.sh`'s prose description while
  the script itself already read `.claude/handoff-task.md`. All renamed; the
  legacy-migration references in `migration-guide.md` are intentionally kept.

## Parked for pilfer FR-12

FR-12 is the deduplication and token-economy pass, and it requires *measured*
token reduction. Doing these here would mean single-sourcing twice under two
designs, so they stay with the FR.

18. Runbook review report template appears three times verbatim
    (review-plan §Phase 5, `references/report-template.md`,
    `runbook-corrector.md`). `/review` is ~half template.
19. Recall protocol restated near-verbatim in ~8 places; the "do not Read
    `memory/MEMORY.md`" caveat in ~10 files.
20. Continuation block duplicated verbatim in `/design`, `/runbook`, `/inline`,
    and `orchestrate/references/continuation.md` — despite
    `fragments/continuation-passing.md` existing.
21. Four correctors total ~10,100 words sharing the same skeleton;
    differentiating criteria are ~20% of each file.

## Closed by the rewire (2026-08-13)

Decided and implemented 2026-08-13 (`agents/decisions/orchestration-execution.md`,
"When Selecting Agent Type For Orchestrated Steps"): bespoke per-plan agents are
replaced by **delegation by reference** — the orchestrator dispatches a standing
agent with a step-file path, and the step file carries a Context block naming the
design, outline, and shared-context artifacts.

10. `/orchestrate` §3.2 dispatched `<name>-test-corrector` and
    `<name>-impl-corrector` that the §1 preflight artifact list never checked
    for. Both are gone: per-cycle test and implementation reviews are
    `edify:corrector` dispatches scoped by prompt, and the preflight list no
    longer names any agent file.
11. `max_turns` was emitted into every manifest (`_DEFAULT_MAX_TURNS = 30`) but
    inert — the `Agent` tool has no such parameter. The column and the constant
    are removed. Both spinning and hanging guards remain platform gaps; a
    runaway agent still has no in-band stop, which the rewire does not change.
    `/orchestrate` §4 now states that gap directly instead of pointing at a
    column that read like a guard.

**What landed.** `prepare-runbook.py`: dropped `generate_task_agent`,
`generate_corrector_agent`, `generate_tdd_agents`, `read_baseline_agent`,
`_build_plan_context_section`, `_TDD_ROLES`, `_DEFAULT_MAX_TURNS`, and the
`agents_dir` thread through `derive_paths`/`validate_and_create`; added
`build_context_block`, `write_common_context`, `write_outline`, and the
`## Execution Contract` footer. `/orchestrate`: §1 preflight, §2 header parse and
Phase-Agent Mapping, §3.1/3.2 dispatch, §3.5 corrector dispatch, §4 execution
bounds, §6 cleanup removed.

Common Context had no destination once the agent definitions went, so it is now
written to `plans/<name>/common-context.md` — with resolved recall under its own
heading — and named from each step file. Recall resolution itself is unchanged.
