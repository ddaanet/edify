# Review: corrector Provenance criteria

**Scope:** `plugin/agents/outline-corrector.md`, `plugin/agents/design-corrector.md`
**Baseline:** `a533a842573459032e7816271b3b55849fe37890`
**Requirement:** R2 — design artifacts record the review they derive from and the
initial commit base
**Spec:** `plugin/skills/design/references/design-content-rules.md` §Provenance Section
**Date:** 2026-09-17

## Summary

Both correctors gained a Provenance criterion. As written at baseline the two
criteria agreed with each other but diverged from the spec in one substantive
way and left the most dangerous act — repairing a missing base — unnamed inside
two agents whose standing policy is to fix everything. Four issues fixed in
each file; three pre-existing findings reported, not acted on.

**Assessment:** Ready after fixes.

## Issues found and fixed

### Critical

**1. The fix-all policy would have manufactured the exact failure the criterion forbids.**

- Location: `outline-corrector.md` §3 Provenance × §5 Apply Fixes;
  `design-corrector.md` §3.5 × §Fix Policy
- Problem: both agents fix ALL issues, and `design-corrector.md:38` lists
  "Missing sections (add with placeholder content)" as a thing to fix. The
  criterion flagged a missing `## Provenance` as Major and stopped there. An
  agent holding `Bash`, told to fix a missing base, reaches for
  `git rev-parse HEAD` — which is precisely the recomputation the adjacent
  Critical bullet names, and it fails silently: pass 2's range starts after
  pass 1's work and the narrow diff reads as a clean review. The criterion
  created the hazard it was added to prevent.
- Fix: a fifth bullet in each file, **"Never fill in `Base:` yourself"** —
  repair with a `TODO` placeholder in both fields and name in the report what
  the author must supply. Grounded: `git diff --numstat TODO..HEAD` exits
  non-zero with `fatal: bad revision 'TODO..HEAD'` (run in this repo), so the
  placeholder is a loud stop rather than a silent wrong range. The
  corresponding prohibition was also added where each agent grants the tool
  (`outline-corrector.md` §Critical Constraints Tool Usage,
  `design-corrector.md` same section), so an agent reading only the tool list
  still meets it.
- Status: FIXED

### Major

**2. `Derived from:` was not checked for naming the superseded artifact.**

- Location: both files, the second Provenance bullet
- Problem: the criterion said only "`Derived from:` names a prior artifact".
  The spec is explicit that it names *two* things — the review report that
  motivated the design **and** the artifact it supersedes — and states why:
  "Naming both is what makes the base copyable — a second pass in a new job
  directory has no other route to it"
  (`design-content-rules.md:109`). An artifact naming only the review report
  passed the criterion and left the next pass with no path to inherit `Base:`
  from, which is the inheritance rule's whole mechanism.
- Fix: bullet rewritten to require `none` or **both**, with naming only the
  report classified Major and the reason stated.
- Status: FIXED

**3. The verbatim check named an input without naming the act or the empty case.**

- Location: both files, the inheritance bullet
- Problem: "`Base:` must match that artifact's `Base:` verbatim" asserts a
  comparison against a file the agent was never told to open, and gives no
  verdict when the path does not resolve — a live case, since `Derived from:`
  points into *another* job directory. An unresolvable path would fall through
  as a pass. This is the failure mode in
  `memory/ddaanet/instruction-names-absent-data.md`: an instruction naming an
  absent input reads as the agent ignoring it.
- Fix: "Read that artifact and check `Base:` matches it verbatim", plus "A
  `Derived from:` path that does not resolve → Major; report it rather than
  accept the base unchecked".
- Status: FIXED

### Minor

**4. "full sha reachable from HEAD" conflated two properties; the named command checks one.**

- Location: both files, the `none` bullet
- Problem: `git merge-base --is-ancestor` verifies reachability only. Verified
  in this repo: the outline's own base at full length exits 0, and its first
  8 characters also exit 0 — an abbreviated sha passes the check the criterion
  offered as proof of a full one. (A sha absent from the repo exits 128 with
  `fatal: Not a valid commit name`, so "exit 0" remains the right pass test.)
- Fix: "a full 40-character sha reachable from HEAD (… via Bash, exit 0)" —
  length and reachability stated as two checks.
- Status: FIXED

**5. Provenance was unreachable from each agent's own checklist.**

- Location: `outline-corrector.md` §Response Protocol item 4;
  `design-corrector.md` §Response Protocol item 6
- Problem: both protocols enumerate the dimensions reviewed and neither listed
  provenance, so an agent working the protocol never reaches the criterion.
- Fix: `provenance` added to outline-corrector's dimension list;
  design-corrector's item 6 now reads "**Check provenance** (Step 3.5) and
  **plugin topics** …" — folded into the existing item rather than added as a
  new one, to avoid growing a file already over the line cap.
- Status: FIXED

**6. `outline-corrector` sanctioned Bash for `rg` only.**

- Location: `outline-corrector.md` §Critical Constraints, Tool Usage
- Problem: the list enumerated `rg` and `rg --files`; the new criterion
  requires `git`. `design-corrector.md` already granted git generically.
- Fix: git line added, carrying the `rev-parse` prohibition.
- Status: FIXED

## Checks that passed

- **Frontmatter completeness:** both carry `name`, `description`, `model`,
  `color`, `tools`. Names match filenames and the `plugin-dev` format rules.
- **`Bash` granted:** `outline-corrector` `["Read","Write","Edit","Bash","Skill"]`,
  `design-corrector` `["Read","Edit","Write","Bash","Skill"]`. The criterion's
  `git merge-base` call is within tools in both.
- **Second-person system prompt:** both open with "You are a … agent".
- **Severity coherence across the two agents:** missing section → Major,
  recomputed base → Critical, in both. Defensible: a missing section degrades a
  downstream review's range (recoverable, and now loudly), while a recomputed
  base silently inverts it. The two new Major cases added here (report-only
  `Derived from:`, unresolvable path) sit at the same level in both files.
- **House style preserved:** `outline-corrector` keeps the flat `**Name:**`
  bullet block under §3; `design-corrector` keeps the numbered
  `### 3.5. Check …` form matching its §1.5 and §4.5.
- **Cross-references resolve:** `/edify:deliverable-review` matches the form
  used in `docs/changelog.md:36`, `docs/design.md:549` and
  `design-content-rules.md:100`. `design-corrector` §3.5's internal pointer
  from §Response Protocol item 6 resolves. `§Fix Policy`, `§5 Apply Fixes` and
  the Tool Usage sections referenced here all exist.
- **Criterion matches the spec** on all four clauses after the fixes: both
  fields required; `Derived from:` names both artifacts or `none`; verbatim
  inheritance on a second pass with recomputation prohibited; a full,
  reachable sha on a first pass.
- **Line-limit gate:** `scripts/check_line_limits.sh` covers `src`,
  `tests` and `agents/decisions/` — not `plugin/agents/`. Neither file breaks
  the build.

## Findings reported, not acted on

**F1 — `design-corrector.md` is 403 lines against the 400 soft cap** (401 at
the start of this review; +2 from the Provenance bullets, with the Response
Protocol edit deliberately kept line-neutral). Per `memory/line-caps.md` no
prose was shaved. The clearest redundancy, if a split or trim is wanted: §4.5
Validate Requirements Alignment states four checks as a bullet list
(`:180-184`) and then restates the same four as a table (`:197-203`), adding
only one row — roughly 9 lines of pure duplication. §Fix Policy (`:18-46`) and
§Critical Constraints Scope/Tone also overlap. The split-or-accept call is
yours.

**F2 — `design-corrector.md` frontmatter `color: purple`** is outside the
palette `plugin-dev:agent-development` documents (`blue`, `cyan`, `green`,
`yellow`, `magenta`, `red`). It is the only one of the repo's eleven agents
outside that set. Pre-existing, unrelated to R2, untouched.

**F3 — `design-corrector.md`'s description is descriptive, not a trigger.** It
describes what the agent does but carries no "Use this agent when …" clause and
no trigger examples, unlike its sibling `outline-corrector` and
`runbook-corrector`. Pre-existing; affects dispatch reliability, not this
requirement.

**F4 — out-of-scope consumer gap, for whoever reviews
`plugin/skills/deliverable-review/SKILL.md`.** That skill's fallback keys on
the *absence* of a Provenance section: "Ask the user for the range only when
the artifact carries no Provenance section" (`:31`). A section present but
carrying an unusable `Base:` — the placeholder case this review introduces, and
equally any typo'd sha — therefore does not reach the fallback; it reaches
`git diff` and fails. That is the intended behaviour here (loud beats silent)
and the wording in both correctors now says so, but the skill's own fallback
condition would read better as "no Provenance section, or a `Base:` `git` will
not resolve". Not edited — outside this group's scope.

**F5 — deviation from the outline, judged correct.** `outline.md` §Item B
prescribed "a **conditional** criterion in the pattern each already uses for
optional sections". The implementation made it unconditional. That is right:
the spec says every `/design` artifact carries a Provenance section, so an
"if present" framing would have made the required section optional and voided
the criterion. Recording it so the divergence is not read later as drift.
