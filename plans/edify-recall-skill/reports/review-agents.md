# Review: 4 corrector agent recall rewires

**Baseline:** ce4d03d4109ac79cb306b326edc748061a5299cb
**Files:** plugin/agents/corrector.md, plugin/agents/design-corrector.md, plugin/agents/outline-corrector.md, plugin/agents/runbook-outline-corrector.md

## Verdict: PASS — no issues found

## Checks performed

1. **Fallback rewired to `edify:recall` invocation** — confirmed in all 4 files. Each replaces the old inlined "do lightweight recall... `memory/MEMORY.md`... `agents/decisions/*.md`" paragraph with `Skill(skill: "edify:recall", args: "<topic>")`.

2. **Preceding sentences intact** — `corrector.md`/`design-corrector.md`: "**Recall context:** Read `plans/<job-name>/recall-artifact.md`, then Read each file it lists" and the "When the artifact exists..." sentence are unchanged. `outline-corrector.md`/`runbook-outline-corrector.md`: item 4's lead-in ("Read `plans/<job>/recall-artifact.md`... when the artifact exists...") is unchanged; only the trailing absent-artifact clause was rewired.

3. **Topics match spec:**
   - `corrector.md` → `"<topic covering quality patterns, failure modes>"` ✓
   - `design-corrector.md` → `"<topic covering architectural conventions, quality patterns>"` ✓
   - `outline-corrector.md` → generic `"<topic>"` ✓
   - `runbook-outline-corrector.md` → generic `"<topic>"` ✓

4. **No remaining `agents/decisions/*.md` reference** in any of the 4 files (grep confirmed zero matches) — satisfies D6.

5. **Phrasing consistency** — `corrector.md`/`design-corrector.md` use a standalone sentence; `outline-corrector.md`/`runbook-outline-corrector.md` fold the same clause into their existing single numbered line, per the requested scope (these two files already carried the recall step inline in item 4, unlike the other two which use a separate bolded line).

6. **Agent structure / tool access** — diffs are single-line, scoped exactly to the fallback clause; no other content touched. None of the 4 agents declare `Skill` in `tools:` frontmatter, but per `memory/cc-subagent-context-capabilities.md` a declared `tools:` list is not a contract — `Skill` reaches subagents regardless of declaration — so this is not a defect.

No fixes were required.
