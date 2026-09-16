# plugin-dev:skill-reviewer on plugin/skills/formalize (2026-09-16)

Saved by the calling session (the reviewer has no Write tool). The reviewer ran
`edify check` to test its own claims. Findings below are its words in substance;
line cites are unverified by the calling session.

Scope: `plugin/skills/formalize/SKILL.md` alone — no `references/`, no fragment
imports — checked against the shipped `edify check`,
`docs/superpowers/design/invariant-guided-verify-loop.md`, and `docs/design.md`.

Measured: 77 lines, 471 words, 3233 bytes.

## Critical

1. **The `error` interpretation is wrong, and it is the skill's only defense
   against a false `verified`** (SKILL.md:58-59). The skill says a target with no
   contract surfaces as `error` and to add a contract in response. Tested against
   the shipped CLI with a contract-free function, it returns `verified` at exit 0:

   ```
   $ .venv/bin/edify check tmp/fz/nocontract.py --json
   {"status": "verified", "target": "tmp/fz/nocontract.py", "findings": [], "detail": "", "budget": null, "vacuity_warning": true}
   exit=0
   ```

   An agent following step 4 accepts a contract-free or contract-stripped target
   as verified. The available signal is `vacuity_warning: true`, which the skill
   never mentions. The defect originates upstream: L1 in the living design carries
   the same wrong premise ("Deferred to `formalize` discipline (add a contract on
   `error`)"), so fixing the skill alone lets it regress.

2. **The documented invocation form is not the one the skill prints** (SKILL.md:42
   runs a bare `edify check`). The binary is not on PATH for installed users;
   `plugin/bin/bootstrap-venv.sh:75` links the venv to `${CLAUDE_PLUGIN_DATA}/current`
   and `docs/design.md:201-203` (D-12 at :293) says skills reach it as
   `${CLAUDE_PLUGIN_DATA}/current/bin/edify` by content substitution. A grep across
   plugin markdown finds zero uses of either placeholder. The bare form works only
   in the edify dev checkout, which is what hides it.

3. **`AskUserQuestion` is prohibited by the always-in-context tier.** Declared at
   SKILL.md:15 and instructed at :32, against `memory/ddaanet/shared-claude.md:22`
   ("Never call `AskUserQuestion`. Ask inline in numbered plain prose, each
   question carrying a stated default"). Load-bearing here, since asking on
   ambiguity is the skill's reason for existing. Same conflict in
   `plugin/skills/requirements/SKILL.md:4` and `plugin/skills/proof/SKILL.md:8`,
   so the fix is a sweep. FR9 in the living design pins the behaviour and needs
   rewording alongside.

## Major

4. **The budget and vacuity discipline assigned to this skill was never written
   into it.** `docs/superpowers/specs/2026-06-15-l7-vacuity-warning-design.md:31`
   rejects an auto-probe inside the CLI because it "belongs in the `formalize`
   discipline, not the `check` primitive" (repeated at :97 under out-of-scope);
   :65 says the JSON fields exist so the formalize loop and a future eval harness
   could read the vacuity flag programmatically instead of scraping stderr. The
   skill reads neither `budget` nor `vacuity_warning`, never mentions `--timeout`,
   and its verified branch (SKILL.md:48-50) just reports and stops. The design's
   worked example (D10) is a planted bug that passed at the default budget and was
   refuted only at a 30s per-condition timeout. The verified branch should require
   a re-run at a non-default budget, or report the verdict as vacuity-flagged.

5. **Nonzero exit codes are undisclosed** (SKILL.md:39-45). Refuted exits 1 and
   error exits 2 per `src/edify/check_cli.py:15-19`. The agent's Bash tool reports
   both as command failures on a normal loop outcome. This is the narrow case the
   project's error-handling rule carves out, where a nonzero exit encodes a result;
   the skill should say so rather than leaving the agent to reach for suppression.

6. **The Backend section points at a superseded frozen spec** (SKILL.md:76-77
   links the 2026-06-08 frozen spec). `docs/superpowers/design/invariant-guided-verify-loop.md:3-4`
   declares itself living and superseding where they diverge, and they diverge on
   four points this skill's reader cares about: D3 on command shape, D4 on the
   four-state output, D5 on the seed function, D7 on CrossHair verbose reporting.
   Link the living design instead.

7. **The iteration cap is not a cap** (SKILL.md:61-62): "at most a small fixed
   number" with five as an example, so the agent has no binding limit. The number
   is also an ungrounded operational threshold, which `CLAUDE.md` treats as
   confabulation. Either state a number and label it arbitrary, or derive one.

8. **No progressive disclosure, where the missing content needs it.** Nine of the
   eleven sibling skills have a `references/` directory; formalize does not, and at
   77 lines it is the smallest body, so moving current content out would be wrong.
   The budget discipline from finding 4, a worked triage example for each of the
   three branches (SKILL.md:52-56), and an icontract usage reference belong in a
   reference file that steps 2 and 4 route to. They are absent rather than misplaced.

## Minor

9. **The contract example omits the import** (SKILL.md:35-37): decorator forms
   without the import that defines them, so step 2 followed literally writes an
   undefined name. Working usage imports it at `src/edify/check.py:7`.
10. **Descriptive second person where imperative is the house form**
    (SKILL.md:22-25 "You own *intent*", "That judgment is yours"; :45 "The result
    status is one of"). The numbered steps are correctly imperative; the drift is
    the preamble and the last sentence of step 3.
11. **The self-trigger condition is not detectable**: the description (SKILL.md:8)
    ends "or after writing a function whose correctness matters". Shared ddaanet
    conventions reserve self-triggering for mechanical, detectable conditions; this
    is a judgement about the agent's own prior output, so it fires arbitrarily or
    never. The three explicit phrase triggers suffice.
12. **`Write` is declared but unused** (SKILL.md:13); Read, Edit and Bash cover the
    procedure.
13. **The Backend heading is a bare "See" link** (SKILL.md:73-77) with no statement
    of when to read it or what it holds. Compare `orchestrate/SKILL.md:201-202`,
    which labels each reference by what it governs.

## Not a problem

The triage rubric (SKILL.md:52-56) and the Disciplines list (:68-71) are sound and
map onto FR10, FR11, NFR4 and NFR5 in the living design. The honest-guarantee
language at :71 is correct as written.
