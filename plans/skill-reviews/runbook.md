# plugin-dev:skill-reviewer on plugin/skills/runbook (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). Line cites are the
reviewer's and are unverified here. **Partial — parts 2 to 4 pending.**

Scope: `SKILL.md`, `references/runbook-format.md`, `fragments/continuation-passing.md`
(the only fragment routed to), plus the named consumers: `agents/runbook-corrector.md`,
`agents/runbook-simplifier.md`, `skills/orchestrate/SKILL.md`,
`orchestrate/references/dispatch-composition.md`, `skills/design/SKILL.md`,
`docs/design.md`.

Measured: `SKILL.md` 151 lines / 916 words; `references/runbook-format.md` 121 / 763.
SKILL.md body after frontmatter is 6071 characters. The description parses to 212
characters, 33 words, and carries 3 embedded newlines.

## Critical

**C1. `runbook-format.md` never specifies the item format for `general` and `inline`
items, and two documents route there for exactly that.** SKILL.md:39-41 says "general
→ concrete action against a named target; inline → same, executed by the orchestrator
itself. All per `references/runbook-format.md`", and D-30 (`docs/design.md:492-494`)
routes the same way. In `runbook-format.md` the words `general` and `inline` occur
exactly once, inside the phase-header token at :14. Every content section is
tdd-shaped: Slices (:28-35), Interfaces (:37-43), the worked example (:45-64, a tdd
phase), Ordering (:84-94), and six of the eight item-level rules (:104-121). `general`
is the default type, so the format reference has no template for the most common item.

**C2. `type: inline` has no consumer in the skill that is supposed to execute it.**
SKILL.md:44-45 promises "inline → no dispatch" and `docs/design.md:497-498` says the
orchestrator executes inline items itself. A grep across `skills/orchestrate/` finds
no occurrence of `type:` in either SKILL.md or `dispatch-composition.md`, and the two
hits for "inline" are unrelated (`orchestrate/SKILL.md:17` means inline item text;
`dispatch-composition.md:4` names the `/inline` skill). Orchestrate separates tdd from
general by the presence of a slice list (`orchestrate/SKILL.md:58`, :113), not by the
phase type token, so an inline phase gets dispatched like a general phase. The repair
belongs in orchestrate, but the runbook skill states the contract nothing honours and
the runbook carries the unread token.

## Major

**M3. The prerequisites gate is labelled an anchor but prescribes no tool call, and
the tool it would need is not permitted.** SKILL.md:29-32 says "Prerequisites check
(D+B anchor): Check the plan directory for a design-stage artifact: `outline.md` or
`design.md`" with no call named, unlike :56 and :71, which carry "tool call required"
and name `Skill(edify:recall)`. D-48 (`docs/design.md:665-673`) says an unanchored
gate gets rationalised past; D-52 (:699-704) requires every step to open with a
concrete tool call. Compounding it, `allowed-tools` (SKILL.md:7) is `Bash(rg:*, git:*)`,
so there is no directory listing and a Read of a missing file errors rather than
returning a verdict. Name the call, e.g. `rg --files plans/<job>`, and branch on it.

**M4. The Self-Check list restates seven rules `runbook-format.md` already owns, and
the two copies have drifted.** SKILL.md:83-118 duplicates the reference (:92-93 vs
format:21-22; :94-96 vs :37-43; :97-99 vs :28-35; :100-101 vs :66-70; :110-111 vs
:105-106; :112-113 vs :93-94; :114 vs :114-116). Two already use different names for
the same rule: "No vacuous items" vs "No setup-only items", and "Prose atomicity" vs
"No split prose edits". The drift runs both ways: the self-check omits the
assertion-quality table (format:73-82), integration-first (:85-89), wire-then-isolate
(:90-92), conformance validation (:96-102) and four item-level rules (:107-121). A
planner treating the self-check as the checklist misses all of those.

**M5. The phase-size threshold is stated without the ungrounded caveat its siblings
carry.** SKILL.md:106-107 ("a phase over 8 items is a split signal"), repeated at
`agents/runbook-corrector.md:74`. The identical threshold is marked unvalidated at
`design/references/design-content-rules.md:26` ("both thresholds ungrounded — need
calibration"), and the corrector marks its other two thresholds that way
(runbook-corrector.md:77, :99) but not this one.

**M6. The skill never says how to choose a phase type, only what each type causes.**
SKILL.md:34-45 lists consequences — item format, review criteria, dispatch count —
and gives no assignment criterion. The only criterion in the repo is
`docs/design.md:509-511`: a phase qualifies as `inline` when its outcome is fully
determined by instruction plus target file state, with no runtime feedback loop and
all decisions pre-resolved in design. SKILL.md:24-27 points at §6.4 for pipeline
context only. The runbook skill is the sole party making this choice, and the rule
lives in a document it never tells the planner to read for that purpose.

**M7. The commit step cannot run the repository's precommit gate, and names no commit
path.** SKILL.md:120-123 says "Commit `runbook.md` before review", while
`allowed-tools` (:7) permits `Bash(rg:*, git:*)`, so `just precommit` is unreachable.
The shared conventions require running the precommit gate before committing, and
CLAUDE.md routes commits through the commit-commands plugin — which the skill's own
`default-exit` (:16) already names. Compare `/inline`, which gates on tree state and
`just precommit` explicitly (`inline/SKILL.md:35-47`). Either widen `allowed-tools`
or route step 4 through the commit skill.

**M8. The usage line disagrees with how the upstream skill invokes this one.**
SKILL.md:21 gives `/runbook plans/<job-name>/design.md`, a file path, while
`design/SKILL.md:151` and :184 both use the directory form `/runbook plans/<job>`.
The prerequisites check at :29 speaks of "the plan directory" and every later step
composes `plans/<job>/...`. The gate at :30 accepts `outline.md` too, so the
file-path usage line is the outlier.

**M9. The bare `/proof` invocation is ambiguous across three installed skills.**
SKILL.md:142 says "Invoke `/proof plans/<job>/runbook.md`", and `edify:proof`,
`ddaa:proof` and `plugin:proof` all answer to that name in this environment. Step 1
of the same skill uses the unambiguous `Skill(skill: "edify:recall", ...)` form at
:57. Systemic rather than unique (`design/SKILL.md:144`, :150 do the same), but it
lands hardest here, since step 7 is the human gate on the artifact execution reads.

## Minor

**m10. The description uses a literal block scalar, so it carries embedded newlines**
(SKILL.md:3-6 opens with `|`). The parsed value is 212 characters containing 3
newlines. All eleven other skills use `>-` or a plain scalar, and the newlines survive
into the rendered listing, where this entry is the only one breaking across lines.

**m11. The description covers few trigger synonyms and carries no negative trigger**
(SKILL.md:4-6). It omits "implementation plan", "break the design into steps", "task
decomposition", "plan the work", and has no boundary clause, though a sibling covers
the adjacent case: execution-ready work with no runbook belongs to `/inline`. At 33
words there is room for both.

**m12. `requires:` and `outputs:` frontmatter keys appear on no other skill**
(SKILL.md:8-12). They are documentation rather than loader keys, so they cost nothing
at runtime, but they diverge from the house shape and duplicate what :21-27 states in
prose.

**m13. "D+B" is never expanded and no reference routes to its definition**
(SKILL.md:29, :56, :71). It is repo-wide jargon in seven other skill and agent files,
recoverable only from D-52 (`docs/design.md:699-704`).

**m14. Two numbering schemes collide inside the Process section**: SKILL.md:47-75
numbers seven stages `### 1.` to `### 7.`, while substeps inside stage 1 run 0, 1, 2,
3, 4 (:51, :56, :61, :67, :71), so "1." denotes both the discovery stage and a substep
within it. The substep list also opens at 0.

**m15. The H1 duplicates a step heading**: SKILL.md:19 "# Write the Runbook" and :76
"### 2. Write the Runbook", so a cross-reference to that name is unresolvable.

**m16. The Self-Check step opens with no tool call**: SKILL.md:83-118 is twelve
bullets of prose judgement, the exact shape D-52 rules out, and the same rule the
skill invokes by name at :29, :56, :71. Merge into the Write step (:76-81) or anchor
with a Read of the written runbook.

**m17. The format reference contradicts itself on field placement**:
`runbook-format.md:16-18` puts `Depends on:` and `Model:` each on its own line, while
the worked example at :62-63 inlines them. The corrector validates against this file
(`runbook-corrector.md:121`).

## What holds up

Imperative style is clean in both files: no second-person forms, and only two modal
verbs across 272 lines, both legitimate. Progressive disclosure is genuinely two-tier,
with format rules in the reference and process in the body. `allowed-tools` is scoped
rather than a wildcard. The continuation section (SKILL.md:145-151) does what
`continuation-passing.md:36-38` asks, stating only its site-specific prepend rule and
pointing at the protocol, with the no-prepend justification stated rather than
asserted. Both cited design anchors resolve (§6.4 at `docs/design.md:396`, D-39 at
:581). The four-dispatch claim (SKILL.md:44-45) matches `orchestrate/SKILL.md:58`, and
the slice identifier `N.M/k` (`runbook-format.md:34-35`) matches
`dispatch-composition.md:20`, :25.

## Priority

C1 (missing general and inline item format) and M6 (missing type-selection criterion)
are the same wound and should be repaired together, since both leave the planner
unable to use two of the three types correctly. C2 needs a decision about whether
inline phases are still real, and that decision belongs to the orchestrate skill.
