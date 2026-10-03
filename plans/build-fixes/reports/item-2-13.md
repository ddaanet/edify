# Item 2.13 — `/build` commit subjects in the agent files (KD-8)

Requirements: KD-8.

## Search

`rg -n 'Item N\.M|<type>:'` and `rg -n 'commit -m|subject'` over `plugin/`,
with `plugin/skills/build/` excluded because Items 2.1–2.7 own it. I also
checked `artisan.md` and `corrector.md` for any commit-subject prescription.

- **Prescribes a `/build` commit subject:** `plugin/agents/test-driver.md:95`
  (GREEN) and `plugin/agents/refactor.md:184` (the refactor commit). These are
  the only two.
- **Already in KD-8's form:** `plugin/agents/tdd-auditor.md:86, :96` (Item
  2.10).
- **Not a subject:** these hits are the runbook item syntax `Item N.M:` used as
  a content marker, not a commit subject:
  - `plugin/skills/proof/references/item-review.md:17`
  - `plugin/skills/runbook/references/runbook-format.md:16`
  - `plugin/agents/design-corrector.md:68, :77`
  - `plugin/agents/corrector.md:153`
- **Describes, does not prescribe:** `runbook-format.md:38-39` says `N.M/k` "is
  the id `/build` uses in dispatch names and slice commit subjects". That is
  still true under KD-8, so I left it.
- **No subject prescribed:** `artisan.md` (only "HEREDOC format for commit
  messages") and `corrector.md` (commits nothing).

## Changes

- **`test-driver.md` GREEN Mode step 6.** "subject `<type>: Item N.M/k —
  <title>`, the title from the prompt" became "subject `<type>: <job> Item N.M/k
  — <title>`, the job and title from the prompt". This matches `tdd-slice.md`
  (c) and `dispatch-composition.md` §Prompt contents item 4.
- **`refactor.md` Step 6.** The example commit became
  `git commit -m "refactor: <job> Item N.M/k — <what changed>"`. `<job>` is
  already bound in the same block (`plans/<job>/reports/...`). The paragraph
  after it ("`refactor:` is a suggested subject, not a checked one … nothing
  keys on the type") is still true and is unchanged.

## Contract across its surfaces

I read the subject contract across its three surfaces, as
`audit-a-contract-across-its-surfaces` asks:

- **Rule.** KD-8 is stated in `dispatch-composition.md` §Prompt contents item
  4: the prompt gives the subject, and `<job> Item N.M[/k]` is a label only.
- **Enforcer.** `.git/hooks/gitmoji.sh` matches
  `^([a-z]+)(\(…\))?(!)?: (.+)$` and rewrites only the type. A
  `<type>: <job> Item N.M/k — <title>` subject matches it, and `refactor` and
  `docs` are mapped in `gitmoji.cfg`. Nothing checks the rest of the subject,
  which KD-8 intends.
- **Consumer.** `tdd-auditor.md` reads `<job> Item N.M/k` as a label. It
  resolves every slice commit from its report's adding commit. Since Item 2.10
  it also expects the refactor commit and the list-revision commit to carry
  the marker. The refactor subject now does, so the auditor's count and the
  agent that produces the commit agree.
- **Seam.** The refactor prompt composed by `dispatch-composition.md` item 4
  carries a slice subject. `refactor.md`'s own example has the same
  `<job> Item N.M/k` shape, so the two no longer differ on the label. They
  differ only in the type and title, which are free.

## Judgement calls for review

- **test-driver's "nothing downstream keys on it"** refers to the type, and is
  left as written. KD-8's broader "nothing mechanical keys on the subject" is
  stated once, in `dispatch-composition.md` item 4. Repeating it in each agent
  would be a second copy.

## Cross-references left for later items

- `docs/design.md:233-240` still records `<type>: Item N.M/k — <title>`. It
  also says the marker "is the only thing `tdd-auditor` may match in a subject"
  (flagged in `item-2-6.md` and `item-2-10.md`). No item names `docs/design.md`.
  Item 2.14 records KD-8 in `pipeline-contracts.md` and `decisions.md`, and the
  hub paragraph needs the `<job>` form with it, since a hub conclusion and its
  node change together.

## Verification

- `just format`, then `just precommit` green: version consistency, cached
  tests, line limits (only the three allowlisted correctors reported), design
  links.
- Self-review of the uncommitted diff against KD-8 and Item 2.13, and against
  `tdd-slice.md` (c) and §After the slice, `dispatch-composition.md` item 4,
  and `tdd-auditor.md` check 2 as Item 2.10 left it.
- Line counts unchanged: `test-driver.md` 144 before and after (rumdl
  reflowed step 6), `refactor.md` 225 before and after.
