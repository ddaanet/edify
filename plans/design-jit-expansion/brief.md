# Design JIT Expansion

## 2026-03-07: Discussion conclusion from active-recall Phase B

Multi-phase outlines (like active-recall's 12-sub-problem outline) should NOT expand to full design.md. JIT expansion instead: each sub-problem gets `/design` or `/runbook` when it enters its execution window. The outline IS the cross-problem coordination artifact. Readiness summary already routes each sub-problem to its pipeline.

Requires `/design` skill update — when the skill encounters an outlined multi-sub-problem plan, it should validate the outline sufficiency, then the caller dispatches individual sub-problems through their readiness-appropriate pipeline. Not attempt full design expansion.

Related: `plans/design-context-gate/` — context budget check at /design exit points (orthogonal concern).
