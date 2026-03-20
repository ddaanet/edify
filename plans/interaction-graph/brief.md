## Render agentic-prose interaction graph

### Origin

During /proof of outline-proofing design (session 83b685c4). The discussion kept cycling on whether agentic-prose edits are "simple" — the interaction graph would make the answer visually obvious.

### What to build

Render a graph showing:
- **Nodes:** skill/fragment/agent files touched by a set of requirements
- **Edges:** behavioral dependencies between them (output format contracts, not code imports)
- **Color coding:** edge types (format coupling, review dependency, execution ordering)

For a bounded agentic-prose requirement (e.g., "add /proof gate to /design Moderate"), the graph should expose triviality: few nodes, zero non-trivial edges. For a cross-pipeline requirement (e.g., "track requirements to all artifacts"), the graph should expose the directed dependency chain.

### Purpose

Classification aid. The proof session showed repeated confusion about whether work is "simple" based on edit size vs behavioral impact. The graph makes the distinction concrete: zero-edge graphs → inline-plan.md eligible. Non-trivial edge graphs → need design ceremony regardless of prose-only nature.

### Implementation direction

Prototype in plans/prototypes/. Input: a set of affected files. Output: DOT or HTML visualization. Could parse SKILL.md cross-references and corrector dispatch tables to infer edges automatically.
