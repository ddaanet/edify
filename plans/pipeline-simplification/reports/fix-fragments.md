# Fix report — fragments, `/inline`, `/runbook`

Scope: the deliverable-review findings assigned to the fragments + `/inline` +
`/runbook` group. Eight files edited, no files added, renamed or deleted.

## Findings applied

| Finding | Site | Change |
|---|---|---|
| Critical 3 | `continuation-passing.md:1-15` | Dropped "hook-based system". §How It Works now states the two real sources — a `[CONTINUATION: ...]` suffix in the invoking prompt or Skill args, and the task frame `.claude/handoff-task.md` — and says explicitly that no hook parses input or injects continuation. The worked chain example now shows a user typing the suffix. |
| Critical 3 | `continuation-passing.md:38` (step 1) | "Read continuation from `additionalContext` (first skill in chain)" → read from the `[CONTINUATION: ...]` suffix in the invoking prompt or Skill args, or from the task frame. Steps 1–4 keep their numbering, so every skill's "step 2" prepend reference still resolves. |
| Critical 3 | `continuation-passing.md` §Transport Format | Removed the "First invocation (hook → skill): JSON `additionalContext` with `[CONTINUATION-PASSING]` marker" line. One format now, whatever the source. |
| Critical 3 | `continuation-passing.md` §Cooperative Skills note | "not enforced by hook" → implemented by the skill itself, nothing enforces it from outside. |
| Major 2 | `delegation.md` §Recall Artifacts For Sub-Agents | Was an anti-pattern rule against handing a grouped pipeline artifact to a sub-agent. Now states the one artifact model: the dispatch prompt hands `plans/<job>/recall-artifact.md` by path, the sub-agent Reads it and every file it lists, per `dispatch-composition.md` §Prompt contents (named as authoritative). Notes that the per-type flat artifacts the old rule assumed no longer exist, and keeps the reason selection is the parent's job. |
| Major 2 | `delegation.md` §Recall Content In Delegation Prompts | Unchanged — pass the path, never inline content, still true and now consistent with the section above. |
| Major 2 | `runbook/SKILL.md:127-130` | "include review-relevant entries from `recall-artifact.md` in the delegation prompt" → pass `plans/<job>/recall-artifact.md` by path, corrector Reads the artifact and its listed files, never inline recall content. |
| Major 7 | `inline/SKILL.md:123` | "Planning artifacts → runbook-corrector (not this gate)" → routes by artifact per `docs/design.md` §6.4 D-26: `design.md` → `edify:design-corrector`, `outline.md` → `edify:outline-corrector`, `runbook.md` → `edify:runbook-corrector`, with the note that `runbook-corrector` rejects anything else. |
| Major 7 | `review-dispatch-template.md:47` | Same three-way routing replaces "route to runbook-corrector per pipeline contracts". |
| Major 11 | `execution-routing.md:5` | Retired `Session.md` → the task frame `.claude/handoff-task.md`. |
| Major 12 | `execution-routing.md:17` | "multiple Task calls" → "multiple Agent calls". |
| Major 12 | `continuation-passing.md:89` | "Skills construct Task prompts explicitly" → Agent prompts. |
| Major 13 | `escalation-acceptance.md:24` | "(D-5)" dropped. `docs/design.md` D-5 is "One responsibility per error-handling layer"; the design record has no rollback-protocol decision at all (`grep -n 'rollback\|revert'` over `docs/design.md` returns nothing, and D-40's three escalation tiers do not state a rollback), so there is no correct D-number to point at. |
| Major 13 | `continuation-passing.md:111` | "(D-1)" dropped. D-1 is "Two output conventions, split by consumer"; `docs/design.md` has no continuation or chain-abort decision, so no substitute exists. |
| Minor (step→item) | `escalation-acceptance.md:3,8,20,26,28,31,35,37` | "step" → "item" throughout, except line 35's "post-step verification" → "post-dispatch verification", which is what that gate actually runs after. No occurrence of "step" remains in the file. |
| Minor (step→item) | `delegation.md:79` | "post-step verification" → "post-dispatch verification". |
| Minor (count) | `continuation-passing.md:107` | "Six cooperative skills" → "Four skills declare `cooperative: true`". Measured: `design`, `runbook`, `inline`, `orchestrate`. The §Cooperative Skills table's other three rows are terminal skills with `default-exit: []`, not cooperative ones. |
| Minor (agent review) | `review-requirement.md:41` | Agent-definition row rerouted from `plugin-dev:agent-creator` to `edify:corrector`, with the `plugin-dev:agent-development` skill named as the criteria source in the dispatch prompt. **No agent-definition reviewer exists in the enabled plugins** — the only agent directories under `~/.claude/plugins/cache/*/*/agents/` belong to edify itself (`artisan`, `corrector`, `design-corrector`, `outline-corrector`, `runbook-corrector`, `runbook-simplifier`, `refactor`, `scout`, `tdd-auditor`, `test-driver`, `brainstorm-name`, `hooks-tester`, and the stale `runbook-outline-corrector`), and plugin-dev ships only `agent-creator`, `plugin-validator` and `skill-reviewer`, none of which reviews agent definitions. |
| Minor (agent review) | `review-requirement.md:46` | Fallback note updated: with plugin-dev absent, only the skill-definition row falls back; the agent-definition row loses its criteria source and reviews against the existing `plugin/agents/` definitions. |
| Minor (frontmatter) | `runbook/SKILL.md:7` | `Bash(mkdir:*, rg:*, git:*, echo:*|pbcopy)` → `Bash(rg:*, git:*)`. Confirmed no `mkdir`, `echo` or `pbcopy` call site in the skill body or its references. |
| Minor (model rule) | `delegation.md:11-14` | Restated to match `dispatch-composition.md` §Model assignment verbatim in substance: type default (`artisan`/`test-driver` sonnet, `corrector` opus, D-32), artifact-type override for `plugin/skills/`, `plugin/fragments/`, `plugin/agents/`, `docs/design.md` (D-42), per-item `Model:` override. Names dispatch-composition as authoritative. |

## Consistency edit not in the finding list

`inline/SKILL.md:114` listed `agent-creator` among the fix-capable reviewers.
Removing it from the routing table (finding 7) would have left that line naming
a reviewer no route reaches, so the list now reads corrector,
design-corrector, outline-corrector, runbook-corrector.

## Skills whose §Continuation contradicts the rewritten fragment

None. All four cooperative skills (`design`, `runbook`, `inline`,
`orchestrate`) point at the fragment's §Consumption Protocol and refer to its
"step 2" prepend. The rewrite preserved the four-step numbering with prepend at
step 2, so every reference still resolves. No skill's §Continuation mentions a
hook or `additionalContext`.

## Left undone

Nothing in the assigned list. Two adjacent facts observed but not acted on,
both outside the owned files:

- `review-requirement.md`'s routing table still routes "plans" to
  `edify:corrector` and has no row for outlines or runbooks; the planning-artifact
  routing lives in `docs/design.md` §6.4 D-26, which line 48 already points at.
  Left as is — narrowing that row was not in the finding list.
- `~/.claude/plugins/cache/.../plugin/agents/runbook-outline-corrector.md` still
  exists in the installed plugin cache. That is a stale install artifact, not a
  repo file.

## Validation

```
$ PATH=.venv/bin:$PATH just precommit
# version consistency
Version consistent: 0.1.1
Tests cached (inputs unchanged)
✓ Precommit OK

$ PATH=.venv/bin:$PATH just check
✓ Checks OK
```

Not committed, per instruction. Files changed: 8, +51 / -42.
