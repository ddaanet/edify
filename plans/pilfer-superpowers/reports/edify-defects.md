# edify pipeline defects surfaced by the 2026-08-13 comparison read

Observed in the text of `plugin/skills|agents|docs|bin` during the
pilfer-superpowers analysis. Repair backlog, independent of pilfering.

## Stale references / dangling names

1. `scripts/create-plan-agent.sh` resolves `agents/task-execute.md`, which no
   longer exists (renamed to `artisan.md`) — the script fails on every
   invocation. `docs/pattern-plan-specific-agent.md` and
   `docs/pattern-weak-orchestrator.md` still document it as the automation
   path, one with a machine-specific absolute path. Nothing calls it;
   prepare-runbook.py does the job better. Candidate for deletion.
2. `skill-reviewer` and `agent-creator` agents exist only in the plugin-dev
   marketplace plugin, not in edify, yet are load-bearing in
   `fragments/review-requirement.md`, `/inline` Phase 4a routing,
   `runbook/references/general-patterns.md`, and two worked examples. An
   `/inline` run whose changed files are skills/agents has no reviewer to
   dispatch unless plugin-dev is installed.
3. Agent frontmatter declares `skills: ["project-conventions"]` (8 agents) and
   `["error-handling"]` (2 agents); neither exists as a skill.
4. `Bash: recall diff <job-name>` prescribed in `write-design.md`,
   `research-protocol.md`, `write-outline.md`, `tier3-planning-process.md`; no
   such command exists.
5. `/plan` referenced as caller five times in `review-plan/SKILL.md`;
   `runbook-outline-corrector.md` triggers on "plan-adhoc Point 0.75 or
   plan-tdd Phase 1.5" — none of these skills exist (now `/runbook`).
6. `docs/tdd-workflow.md` routes Stage 5 to `/review-analysis` (×3); the
   actual agent is `tdd-auditor`.
7. `docs/general-workflow.md` has duplicate `### /design` entries and lists
   `.claude/handoff-task.md` twice with different descriptions; both docs'
   change logs stop at 2026-01-31.

## Contradictions

8. Orchestrator model tier: `/orchestrate` says Sonnet (twice); both pattern
   docs and `general-workflow.md` say Haiku, and the weak-orchestrator
   rationale depends on Haiku. No `model:` frontmatter to settle it.
9. `runbook/references/examples.md` Cycle 1.1 demonstrates the
   ImportError-as-RED anti-pattern that `anti-patterns.md`,
   `tdd-cycle-planning.md`, review-plan §11.1, and
   `validate-runbook.py red-plausibility` all prohibit. It also contains a
   corrupted find-and-replace string ("Use Read/Write/Edit/`rg` (Bash)s (not
   Bash for file ops)") — the same string is baked into prepare-runbook.py's
   `DEFAULT_TDD_COMMON_CONTEXT` and injected into every TDD agent lacking a
   Common Context.
10. `/orchestrate` §3.2 dispatches `<name>-test-corrector` and
    `<name>-impl-corrector`, but the §1 preflight artifact list never checks
    for them.

## Verification gaps

11. Execution bounds absent and known-absent: `max_turns` emitted into every
    manifest (`_DEFAULT_MAX_TURNS = 30`) but inert — the Agent tool has no
    such parameter; spinning/hanging guards recorded as platform gaps. A
    runaway agent has no in-band stop.
12. `validate-runbook.py verify-green-paths` exists but is missing from the
    Phase 3.5 invocation list — review-plan §3.5's rule has a deterministic
    checker that never runs.
13. Every validator subcommand has a `--skip-*` flag with no stated
    legitimacy conditions; a SKIPPED report file looks like a run.
14. `check_model_tags`/`check_lifecycle`/`check_red_plausibility` operate on
    TDD cycles only — general/inline runbooks pass all validators vacuously
    while Phase 3.5 is called "mandatory for all Tier 3 runbooks".
15. `/orchestrate` §3.0 inline-phase review threshold ("few net lines across
    few files → self-review") is left entirely to the executing model, in the
    one path where the orchestrator reviews its own edits.
16. `/requirements` has no failure path: no STOP conditions, no error
    handling, no corrector; sole gate is `/proof`.
17. `triage-feedback.sh` detects behavioral code via
    `grep -E "^\+[^#]*(def |class |function )"` — Python/JS only; silently
    weakens the under-classification verdict for other languages.

## Redundancy / verbosity

18. Runbook review report template appears three times verbatim
    (review-plan §Phase 5, `references/report-template.md`,
    `runbook-corrector.md`). `/review` is ~half template.
19. Recall protocol restated near-verbatim in ~8 places; the "do not Read
    memory/MEMORY.md" caveat in ~10 files.
20. Continuation block duplicated verbatim in `/design`, `/runbook`,
    `/inline`, and `orchestrate/references/continuation.md` — despite
    `fragments/continuation-passing.md` existing.
21. Four correctors total ~10,100 words sharing the same skeleton;
    differentiating criteria are ~20% of each file.
22. `/inline`'s Delegation Protocol Summary table restates seven rules from
    the section immediately above it.

## Brittleness

23. Phase 0.95 "lightweight orchestration exit" is discriminated by the mere
    presence of a `## Execution Model` heading — a rename silently reroutes
    the pipeline.
24. Many thresholds ungrounded; some self-flagged ("6-15 files (ungrounded —
    needs calibration)"), others carry no caveat (>8 items/phase, 40% phase
    share, 350-line growth threshold, >15 messages resume cutoff, 150k
    context refresh).
25. Recall-artifact `(phase N)` tagging couples LLM prose to a Python regex;
    the null sentinel is matched by `startswith("null")`.
26. `just green`/`just dev` hardcoded but absent from `plugin/portable.just`
    (host-repo-only); `verify-red.sh` hardcodes pytest.
27. `/orchestrate` remediation says "skip resume if agent exchanged >15
    messages" — the orchestrator has no way to observe an agent's message
    count.
28. Pattern docs mark all hypotheses ✅ and declare "READY for broader
    adoption" from a single 3-step execution; the "94% token reduction"
    figure derives from invented per-step estimates with the author's
    mid-calculation self-correction still in the file.

## Unclear triggers / routing

29. Plugin `/review` collides with Claude Code's built-in `/review`;
    `docs/shortcuts.md` lists it without the distinction.
30. `/review` is user-invocable with AskUserQuestion yet calls itself "the
    protocol used by review/correction agents", while `corrector.md` states a
    delegated reviewer cannot use AskUserQuestion — incompatible interaction
    models for the same protocol.
31. `review-plan` is `user-invocable: false`, reached only via
    runbook-corrector's `skills:` frontmatter, but its description is written
    as if a user or `/plan` triggers it.
32. `/design` Simple routing chains to `/inline`, which re-runs a full recall
    pass unless the easy-to-omit `execute` token is passed.
33. `/design` Phase 0 has two overlapping decompositions (Composite Task vs
    Companion Tasks) distinguished by a judgment call, not a detectable
    signal.
