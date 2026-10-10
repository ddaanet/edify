## Brief: the corrector's integration review reads a contract's surfaces against each other

2026-09-25

Arrived from the `craft` repo, while retiring a neighbouring ddaanet memory fact
into a craft skill. This note ends craft's involvement; nothing is tracked
there. Sections are named, not line-numbered.

### The gap

`plugin/agents/corrector.md`, "Analyze Changes", **Integration Review (for
multi-file or accumulated changes)**, ends with "Identify integration issues
between components". That names the goal and gives no method, and the method is
where the misses live.

### The increment

A contract specified in one file, enforced by an agent or hook in a second and
consumed in a third is reviewed by reading the three against each other.
Verifying each site on its own terms confirms every fix and checks no seam. Name
the three surfaces before reading anything, then ask of each pair:

- Does the enforcer check what the rule actually says?
- Can the enforcer repair what it detects without destroying what it just
  verified?
- Does the consumer depend on a clause nothing checks at the consumer's end?

The productive question is *what does this surface assume the other one did*.
"Is this surface defensible on its own" is what a per-site review already
answers. The same holds when the review is driven by a finding list: confirming
each finding at its own site is per-site verification.

### The instance

A deliverable review of a provenance contract: one rule file, two reviewing
agents enforcing it, one skill consuming it. Nine findings, two delegated
reviews and a first pass down the finding list all confirmed every fix at its
own site. Reading the three surfaces against one another found four majors none
of them reached: the enforcers' repair directive overwrote the one field it had
been told to trust, the same directive barred the one repair that was not the
thing being banned, and the consumer never checked the rule at all.

### Constraints

- `corrector.md` is already past a 400-line cap, so the increment should
  replace the "Identify integration issues between components" bullet rather
  than add beside it.
- The fact currently lives as the ddaanet memory
  `audit-a-contract-across-its-surfaces`. Once the corrector carries it, retire
  that memory file and its index line in the same change, and restate inline
  any inbound link that carried meaning.
- `outline-corrector.md`'s cross-component interface check is the design-time
  analogue over planned components. It is not the target: the defects above
  live in written text across files, which an outline does not have yet.
- A brief's recommendation is input, not a decision; placement and wording are
  edify's call.
