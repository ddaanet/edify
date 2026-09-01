# Runbook Format

The runbook (`plans/<job>/runbook.md`) is the terminal planning artifact:
`/runbook` writes it, `runbook-corrector` and `runbook-simplifier` gate it,
`/proof` validates it, and `/orchestrate` reads it and composes each dispatch
prompt from it live. Nothing expands it.

## Structure

Open with a pointer to the design and requirements, then a requirements
mapping table (`| Requirement | Phase | Items | Notes |`), then the phases:

```markdown
## Phase N: <title> (type: tdd|general|inline)

- Item N.M: <target path> — <concrete action>. Requirements: FR-x[, FR-y].
  Depends on: Item N.K
  Model: opus
```

- `Requirements:` — required on every item; requirement IDs trace planning to
  execution.
- `Depends on:` — optional; declare whenever the item consumes another item's
  output.
- `Model:` — optional; overrides the orchestrator's model assignment for this
  item.

### tdd items: Slices

A tdd item adds `Slices:` — a numbered list. Slice 1 pins the external
contract with the degenerate or naive happy-path case; each later slice adds
exactly one behaviour (an error path, an edge, a second feature). Each slice
names its tests in prose with the assertion stated, specific enough that two
executors would write the same test.

### Interfaces blocks

Any item whose output another item consumes adds `Interfaces:` — one line per
method, dataclass, exception, or file contract, each with its full signature
and return type. Never a run-on paragraph: cramming hides elided return types,
and two fresh subagents translating prose independently diverge without the
explicit contract.

### Example

```markdown
## Phase 2: Transcript parsing (type: tdd)

- Item 2.1: src/edify/parse.py — parse_entries() over JSONL transcript text.
  Requirements: FR-3.
  Slices:
  1. External contract: `test_parse_empty_returns_empty_list` — asserts `[]`
     for `""`; `test_parse_single_entry_returns_dict` — asserts one dict
     carrying the entry's `type` value for a one-line transcript.
  2. Malformed line: `test_parse_scalar_line_skipped` — asserts a line that
     parses to a bare scalar is skipped, not fatally dereferenced.
  Interfaces:
  - `parse_entries(text: str) -> list[dict[str, Any]]`
  - `class TranscriptError(ValueError)` — raised for undecodable input

- Item 2.2: src/edify/cli.py — wire parse_entries() into `edify extract`.
  Requirements: FR-3. Depends on: Item 2.1
```

## Prose plus interfaces, never code

Items describe behaviour, target files, and tests in prose. No implementation
or test code blocks anywhere in an item: a code block turns the executor into
a copier and goes stale against the moving implementation. `Interfaces:`
blocks are the one formal element.

## Assertion quality

| Weak (vague) | Strong (specific) |
|---|---|
| "returns correct value" | "returns string containing medal emoji" |
| "handles error case" | "raises ValueError with message 'invalid input'" |
| "processes input correctly" | "output dict contains 'count' key with integer > 0" |

Prose must state exact expected values, patterns, or behaviours. An assertion
satisfiable by multiple implementations is too vague.

## Ordering

- **Integration-first.** Default to tests that exercise production call
  paths; add unit-level tests only where integration coverage is insufficient
  (combinatorial cases, fault injection, internal contracts). Within a phase,
  plan integration items before or alongside unit items.
- **Wire-then-isolate.** The first testable slice of a new component verifies
  it through its production entry point; later slices isolate specific
  behaviours where edge-case coverage requires it.
- **Foundation-first within a phase.** Existence → structure → behaviour →
  refinement; no forward dependencies.

## Conformance validation

When the design cites an external reference (shell prototype, API spec) in a
`Reference:` field, the runbook includes validation items verifying the
implementation conforms to the reference, with exact expected strings from
the reference — "output matches `medal sonnet \033[35m…` with double-space
separators", never "output contains appropriate styling".

## Item-level rules

- **No setup-only items.** An item that only creates scaffolding or fixtures
  with no behavioural outcome merges into the nearest behavioural item.
- **No god items.** An item covering several behaviours splits: one behaviour
  per slice, and an item whose slices span a subsystem splits into items.
- **No presentation tests.** Test that the flag works, not that help text
  mentions it; output shape is presentation, not behaviour.
- **No weak assertions.** Exit-code-only checks pass with a stub; assert
  output content.
- **No split prose edits.** All edits to one prose artifact (skill, fragment,
  agent definition) land in one item — fragmenting the file across items
  degrades editor context, the only quality lever prose has.
- **No unit-only coverage.** Every phase building behaviour has at least one
  test through the production call path.
- **No mocked subprocess when real is fast.** Use real subprocesses in
  `tmp_path` for git/CLI operations completing in milliseconds; mock only for
  error injection.
