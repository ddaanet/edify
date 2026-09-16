# plugin-dev:skill-reviewer on plugin/skills/deliverable-review (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — remainder requested; report was
cut inside C3.**

The harness flagged this reply as containing instruction-shaped text (a settings
file pattern) and neutralized it. Nothing in the report was treated as an
instruction.

Scope: `skills/deliverable-review/SKILL.md`, `references/example-report.md`;
`docs/design.md` §6.8 cited but not shipped; fragments consulted:
`escalation-acceptance.md`, `delegation.md`, `continuation-passing.md`,
`token-economy.md`.

## Measurements

| File | Lines | Words | Bytes |
|---|---|---|---|
| `SKILL.md` | 143 | 739 | 5515 |
| `references/example-report.md` | 197 | 1207 | 8949 |

Frontmatter description: 36 words, 304 characters.

## Critical

**C1. `run_in_background=true` is not an `Agent` parameter, and a fragment in this
plugin says so.** SKILL.md:73 instructs "Use `run_in_background=true` for parallel
agents". `fragments/escalation-acceptance.md:50` records the verified correction:
the spawn tool is `Agent` with `description`, `prompt`, `subagent_type`, `name`,
`model`, `isolation` (plus `mode`/`team_name` where exposed); no `max_turns`, no
`run_in_background`, no `resume`. An agent following line 73 passes an unknown key
and gets an input-validation error exactly where Layer 1 launches. The string
appears in `plugin/` only twice: this line and the fragment refuting it. Fix:
delete the line; parallelism comes from issuing the Agent calls in one message,
which line 67 already implies.

**C2. The methodology reference does not exist for any installed copy.** SKILL.md:44,
:109 (inside the report template, so every generated report hardcodes it) and :142
point at `docs/design.md` §6.8. The plugin ships from `plugin/`, which contains no
`docs/`; `scripts/release.sh:36` derives the subdir from the manifest and :76-78
enforce a `git-subdir` marketplace entry at `path: plugin`. §6.8 holds the operative
content — axis definitions, severity rubric, the ISO/IEEE citations the description
advertises — while SKILL.md:36-42 gives only axis names. Line 109 writes a dangling
citation into every consumer's report, which the skill's own "broken references →
Major" rule would flag. Fix: move §6.8's content to
`references/methodology.md` and cite it via `${CLAUDE_PLUGIN_ROOT}`.

**C3. SKILL.md contradicts the two design decisions it cites as its methodology.**
SKILL.md:136-138 says to report severity counts only, no merge-readiness language,
and that "the skill does not queue follow-up work or record lifecycle state".
`docs/design.md:761-764` (D-58) says every finding resolves to a fix or a tracked
task, with no third option, and that "noted in report" is not a resolution.
`docs/design.md:772-774` (D-60) says to route findings unconditionally to `/design`.
Only D-59 survives in the skill; D-58 and D-60 are negated by the closing clause of
:138. The reviewer could not tell which side is current: CLAUDE.md calls
`docs/design.md` current truth, so the skill contradicting it is the anomaly, but
either could be stale. Decide, then make the other match.

## Major

**M1. Phase 4 never says to read the Layer 1 sub-reports, and Phase 3 arguably
forbids it.** SKILL.md:101 says "Write consolidated report" but nothing reads the
Layer 1 outputs at `plans/<plan>/reports/deliverable-review-<type>.md` (:71), while
:97 says "Layer 2 reads deliverables directly against the design spec, not
delegation reports. The two layers are independent." Read literally, Layer 1's
reports are abandoned. The example report attributes findings to the sub-reviews
(`references/example-report.md:34, 41, 48, 55, 62, 70, 77`, list at :194-197), so it
demonstrates a merge step the process omits. Fix: add a Phase 4 step that reads and
merges each Layer 1 report, deduplicating against Layer 2's own, and reword :97 to
scope the prohibition to judgement independence.

**M2. The Layer 1 gate is ungrounded, and CLAUDE.md names this exact failure mode.**
SKILL.md:59-65 gates on total lines: under 500 skip Layer 1, 500-2000 two opus
agents, over 2000 three. Nothing in `docs/design.md` §6.8 (D-55 to D-60) mentions a
line threshold, agent count or partitioning rule. A skill whose job is to catch
ungrounded methodology carries three round numbers in its own control flow. Fix:
cite a measurement, or mark the table as an ungrounded starting point in the style
`docs/design.md:809-811` already uses for the 20/60/20 split (L-3).

**M3. "Total lines" is ambiguous between churn and file size, and the two gate
differently.** SKILL.md:31 counts via `git diff --numstat <range>` (churn); :59 gates
on "total deliverable lines from Phase 1 inventory". The example report's inventory
reads as file length (`references/example-report.md:12-19`: `cli.py` 370, `merge.py`
290, `__init__.py` 1). A plan making small edits across a large codebase skips
Layer 1 under churn and gets three agents under file size. The reviewer would pick
churn and fix the example, since `--numstat` is the prescribed instrument.

**M4. The Phase 1 pathspec excludes `.claude`, which holds tracked production
artifacts.** SKILL.md:31 runs `git diff --numstat <range> -- . ':!plans' ':!tmp'
':!.claude'`. The reviewer ran it verbatim against `HEAD~3..HEAD`: it works and
surfaces the memory submodule pointer move. But `git ls-files .claude` shows tracked
production content: `.claude/rules/cli-work.md`, `design-work.md`, `planning-work.md`,
`test-work.md`, `workflow-work.md`, and `.claude/settings.json`. Under D-55
(`docs/design.md:718-720`) a path-triggered rule file is a deliverable, and D-54
(:790-794) makes `.claude/rules/` one of four discovery layers. A plan shipping a new
rule file is silently dropped from the inventory. Fix: narrow to `':!.claude/handoff-*'`
and add rows for `.claude/rules/*.md` and `.claude/settings.json`.

**M5. "Fragment convention compliance" names no conventions and points at no file**
(SKILL.md:90, a mandatory cross-cutting check). The only file containing the phrase
is SKILL.md itself; `plugin/fragments/` has ten files with no README, index or schema
statement. By the skill's own constraint-precision axis (`docs/design.md:743-744`) it
is unactionable. Give it a referent or cut it.

**M6. The skill dispatches sub-agents without referencing the delegation contract.**
SKILL.md:67-71 specifies what each Layer 1 agent receives but never routes through
`plugin/fragments/delegation.md`, unlike `orchestrate/SKILL.md:201`,
`inline/SKILL.md:108`, `design/references/design-content-rules.md:121`. Omitted:
quiet execution and the return contract (`delegation.md:31-38`), so an agent may dump
its report into the parent's context; search capability (:62-73), since SKILL.md
never says which tools the sub-agents get; the recall artifact hand-off (:81-85).

**M7. No prerequisite validation, despite a rule file pointing at the pattern.**
SKILL.md:20-24 is headed "Prerequisites" but states no check and no failure
behaviour. With `plans/<plan>/design.md` absent, Phase 1 reads a Scope section that
does not exist and the conformance baseline is silently empty.
`.claude/rules/planning-work.md:11` routes to `prerequisite-validation.md`;
`runbook/SKILL.md:29` implements it; `orchestrate/SKILL.md:28` deliberately declines
and says so. D-52 (`docs/design.md:700-704`) requires a Read or Bash anchor.

## Minor

**m1. Severity definitions drift from D-56 without saying they extend it**
(SKILL.md:131-134 vs `docs/design.md:757-759`). SKILL.md adds "unimplemented design
requirement" to Critical, "test gap" to Major, "robustness edge case" to Minor. The
example files C4 and C5 (test gaps) as Critical, exceeding even SKILL.md's rubric:
two documents, three rubrics.

**m2. Layer 1 type values are undefined and the example uses a third naming.**
SKILL.md:71 writes `deliverable-review-<type>.md`; partitions at :64-65 imply
`code-test` / `prose-config`; the example (`example-report.md:195-197`) uses `-code`,
`-tests`, `-prose`.

**m3. The report template omits the sub-report list the example ends with**
(SKILL.md:105-129 defines six sections; `example-report.md:194-197` adds a seventh).

**m4. The template's Gap Analysis has a column the example does not** (SKILL.md:125
specifies requirement/status/reference; `example-report.md:161` has two columns).

**m5. The example uses approximate line counts** (`example-report.md:19-20`: "roughly
200", "roughly 20") while `--numstat` returns exact integers; the No Estimates rule
applies and the example is what agents imitate.

**m6. The example's Gap Analysis uses check and cross emoji**
(`example-report.md:163-176`). Style call rather than defect.

**m7. The report template gives no way to obtain the date** (SKILL.md:107 placeholder
with no `date -I` instruction).

**m8. The living design record has no row in the type table**, though Phase 1 will
surface it: the pathspec does not exclude `docs/`, and the reviewer's test run
returned `docs/design.md` and `docs/changelog.md`.

**m9. Three soft qualifiers in a skill that enforces constraint precision**:
SKILL.md:51 "acceptable if justified" (weakest, no test), :55 "Layer 1 is optional",
:84 "issues delegation cannot catch". The latter two are defensible because concrete
material follows immediately.

## What is working

No second person anywhere across 143 lines. The description triggers well (36 words,
three literal phrases plus a state trigger). The two-layer rationale at :97 names a
structural limit of delegation and matches D-57. Layer 2 mandatory with Layer 1
optional is the right way round. The submodule sentence at :31 fires in practice,
confirmed by the reviewer's run. Line 138's refusal of merge-readiness language
implements D-59 exactly. The example report is a good model: every finding carries
file, line, axis and impact, attributed to its source review.

## Suggested order of work

1. Delete SKILL.md:73 (C1) — one line, removes a guaranteed runtime error.
2. Resolve the D-58/D-60 contradiction (C3) — a decision, and it may change Phase 4.
3. Relocate the methodology into the plugin (C2) — larger, touches the template.
4. M1, M3, M4 — one-to-three-line corrections with real behavioural consequence.
5. The rest.
