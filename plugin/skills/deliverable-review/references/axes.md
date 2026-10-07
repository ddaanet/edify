# Review axes and severity

What a reviewer applies when judging a deliverable. Classify each deliverable
into exactly one type; the type selects its axes on top of the universal ones.

## Types

Code, test, agentic prose, human documentation, configuration.

## Universal axes

Applied to every type.

- **Conformance** — satisfies the conditions in the design spec (IEEE 1012).
- **Functional correctness** — behaves as the spec says (ISO 25010).
- **Functional completeness** — covers every specified function (ISO 25010).
- **Vacuity** — does real work rather than ceremony.
- **Excess** — anything unspecified.

## Per-type axes

**Code**

- Robustness
- Modularity
- Testability
- Idempotency
- Error signaling

**Test**

- Specificity — fails for the right reason and only that.
- Coverage
- Independence — verifies behavior, not implementation.

**Agentic prose**

- Actionability — every step maps to a tool call or state change.
- Constraint precision — measurable criteria, not "relevant" or "appropriate".
- Determinism
- Scope boundaries

**Human documentation**

- Accuracy
- Consistency
- Completeness
- Usability

**Configuration** — universal axes only.

## Severity

- **Critical** — incorrect behavior, data loss, security.
- **Major** — missing functionality, broken references, vacuous artifact.
- **Minor** — style, clarity, naming.

## Sources

[ISO/IEC 25010:2023](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010),
[IEEE 1012](https://standards.ieee.org/ieee/1012/5609/),
[ISO/IEC 26514](https://www.iso.org/standard/43073.html),
[AGENTIF benchmark](https://keg.cs.tsinghua.edu.cn/persons/xubin/papers/AgentIF.pdf),
[arXiv 2601.03359](https://arxiv.org/abs/2601.03359),
[Anthropic: Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
