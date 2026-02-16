# Safety and Security Review Gate: Grounded Framework

**Grounding quality: Moderate**
- Internal brainstorm: Strong (incident-grounded, code-referenced, 6 LLM-specific failure modes)
- External frameworks: Moderate (DO-178C/FMEA/FTA adapted from adjacent domains; AI code quality research emerging but security-focused)
- LLM-specific safety: Thin externally (no established framework), strong internally (observed incidents)

## Research Foundation

### External Frameworks

**Software safety engineering** (DO-178C, IEC 61508, NASA Power of 10):
- **Design Assurance Levels (DALs):** Consequence severity determines review rigor. Maps to internal hazard tiers.
- **FMEA (bottom-up):** Component-level failure mode analysis. Maps to per-step safety scan.
- **FTA (top-down):** System-level fault tree from undesirable event backward. Maps to post-orchestration chain analysis.
- **"Shall not" requirements:** Safety requirements specify what must never happen, not just what should happen.

**AI code quality** (Turkovic 2026, Veracode 2025):
- Five evaluation dimensions: correctness, fitness, security, performance, maintainability.
- AI-generated code: 1.7× more total issues, 1.75× more logic/correctness errors vs human-written.
- 25-35% gap between functionally correct and simultaneously secure code.
- Trend toward specialized review agents per concern (correctness, security, performance).

**HITL patterns** (Skywork, industry):
- Gate destructive or high-impact actions with human/elevated approval.
- Rule: "If a mistaken action would be expensive or hard to reverse, require approval."

**Software security for LLM-generated code** (OWASP, CWEval, SafeGenBench):
- **OWASP LLM Top 10 (2025):** LLM01 Prompt Injection, LLM03 Supply Chain, LLM05 Improper Output Handling, LLM06 Excessive Agency — all applicable to code generation pipelines.
- **CWEval benchmark:** 25-35% absolute gap between functionally correct and simultaneously secure code. GPT-4o: func@10 = 90.7%, func-sec@10 = 65.3%.
- **SafeGenBench:** 558 prompts, 12 languages, dual-judge consensus. Zero-shot security accuracy averages 37.4%; safety prompting raises by 20-25%.
- **45% of AI-generated code** introduced risky security flaws (Veracode 2025, 100+ LLMs tested).

**Safety and security: distinct but co-equal:**
- Safety: protecting against accidental harm from correct-but-wrong code (data loss, state corruption)
- Security: protecting against adversarial exploitation (injection, unauthorized access, secret exposure)
- Overlap: OWASP LLM05 (Improper Output Handling) is the security analog of S-3 (Output-as-instruction). Same mitigation, different threat model.
- Both warrant review: current incident is safety-class, but the pipeline gap affects both. Security criteria prevent different failures through the same review gate.

### Internal Brainstorm (Opus)

Nine sections covering hazard classification, vet-vs-safety gap analysis, pipeline placement, LLM failure modes, generation vs review interventions, concrete checklists, and the observed failure chain. Full document: `tmp/ground-internal-safety-review.md`.

Key insight no external source surfaces: **existing review gates validate state; safety review validates dynamics** — what happens when state transitions fail, especially silent failures (exit 0 + wrong result).

## Adapted Methodology

### Framework Mapping

| External Concept | Internal Adaptation |
|-----------------|---------------------|
| DO-178C DAL (consequence → rigor) | 4-tier hazard classification (Tier 1: irreversible destruction → Tier 4: propagation amplifiers) |
| FMEA (bottom-up component analysis) | Per-step safety scan: S-1 through S-6 criteria applied when step touches destructive patterns |
| FTA (top-down fault tree) | Post-orchestration chain analysis: C-1 through C-3 tracing from data loss backward through operation chains |
| HITL (gating destructive actions) | Model tier elevation: minimum sonnet for steps modifying Tier 1 operations |
| Specialized review agents | Safety criteria injected into vet-fix-agent when triggered (not separate agent) |
| Turkovic 5-dimension checklist | Safety as 6th evaluation dimension alongside correctness/security/fitness/performance/maintainability |

### Hazard Tiers

Adapted from DO-178C DAL concept. Tier determines review rigor and generation model floor.

| Tier | Class | Examples | Generation Floor | Review |
|------|-------|----------|-----------------|--------|
| 1 | Irreversible destruction | `rmtree`, `branch -D`, `clean -fd`, `reset --hard` | sonnet | S-1 through S-6 |
| 2 | State corruption | Single-parent merge, force-remove worktree, overwrite without read | sonnet | S-1, S-2, S-6 |
| 3 | Semantic data loss | CLI suggesting destructive commands, exit 0 on failure, post-failure validation | haiku (standard) | S-3 only (output review) |
| 4 | Propagation amplifiers | Pipeline operations, agent-follows-CLI chains | N/A (cross-cutting) | C-1 through C-3 |

### LLM-Specific Failure Modes

Six modes grounded in observed incidents. No external framework covers these — they are specific to LLM-as-code-generator with LLM-as-consumer.

| Mode | Description | Safety Criterion |
|------|-------------|-----------------|
| Instruction-following from output | CLI prints command, agent executes it | S-3: No destructive commands in output |
| Exit code optimism | `returncode == 0` assumed semantic success | S-1: Verify semantically, not syntactically |
| Happy-path completion bias | Log-and-continue instead of stop on error | S-2: Guards must stop, not warn |
| Pattern matching without semantics | `_git()` returns string, used as bool | S-2: Guard data type verification |
| Cleanup-path destruction | Teardown runs all steps regardless of prior failure | S-4: Cleanup checks preconditions |
| Confident incorrectness | Structurally valid, semantically wrong | S-5/S-6: Semantic verification via tests |

### Per-Step Safety Criteria (S-1 through S-6)

Adapted from FMEA bottom-up analysis. Injected into vet-fix-agent prompt when step touches Tier 1/2 patterns.

**Trigger (mechanical grep):**
```
shutil.rmtree | os.remove | os.unlink
git branch -D | git branch -d
git clean -f | git reset --hard | git checkout .
git worktree remove --force
subprocess.run.*rm\b
```

**S-1: Exit code fidelity.** For every function returning exit code: list callers, verify caller can distinguish success from silent failure, verify test for silent-failure path.

**S-2: Guard-before-destroy ordering.** For every Tier 1 operation: guard exists before destructive call, guard stops execution (not warns), guard's return value is semantically correct (type check).

**S-3: Output-as-instruction.** For every error/warning message: no command strings that cause data loss if executed. Report problem state, not destructive fix.

**S-4: Cleanup path preconditions.** For every teardown function: step N+1 checks step N succeeded, partial-cleanup tested (step N fails → step N+1 does not execute).

**S-5: Merge/commit ancestry.** For code creating commits: expected parent count, source branch is ancestor of result, expected files present in result tree.

**S-6: Silent failure propagation.** For pipeline operations: trace what runs if this fails silently, verify downstream validates inputs independently.

### Per-Step Security Criteria (Sec-1 through Sec-4)

Adapted from OWASP LLM Top 10 and Turkovic security dimension. Applied alongside safety criteria — same trigger mechanism, separate checklist.

**Trigger (mechanical grep):**
```
subprocess.run | os.system | os.popen
open(.*w) | Write(
environ | getenv | secret | token | key | password
input( | click.prompt | sys.stdin
```

**Sec-1: Input validation.** For every external input (CLI args, file content, git output parsed as data): validated before use, no injection path through string interpolation into subprocess calls.

**Sec-2: Secret exposure.** For every string written to stdout/stderr/file: no credentials, tokens, or keys in output. Grep for `token`, `key`, `secret`, `password` in echo/print/write paths.

**Sec-3: Command injection.** For every `subprocess.run` with string interpolation: verify shell=False (list args), no unsanitized user input in command construction.

**Sec-4: Excessive agency.** For CLI commands that agents invoke: does the command do more than the agent needs? Can the scope be narrowed? (OWASP LLM06 adaptation.)

### Post-Orchestration Chain Analysis (C-1 through C-3)

Adapted from FTA top-down analysis. Applied after all steps implemented.

**C-1: Destructive operation inventory.** List all Tier 1 operations, their guards, exit codes, consumers.

**C-2: Error propagation trace.** From each destructive operation, trace backward: what conditions must hold, are they checked or assumed from upstream exit codes, does defense-in-depth exist?

**C-3: Agent-in-the-loop analysis.** For each CLI command an agent invokes: what does agent do with exit 0/1/stderr? Is there a path where agent causes data loss by following CLI guidance?

### Pipeline Integration

Two interventions, not one:

**Generation constraint:** Steps modifying Tier 1/2 operations → minimum sonnet (not haiku).

**Review augmentation (Option C from brainstorm):**
1. Mechanical grep scan after step execution → detects Tier 1/2 patterns
2. If triggered → vet-fix-agent delegation includes S-1 through S-6 criteria
3. Post-orchestration → C-1 through C-3 chain analysis (as part of deliverable review or separate)

No new agent. No new pipeline stage. Grep trigger + augmented vet prompt (safety S-1–S-6 + security Sec-1–Sec-4) + expanded deliverable review.

## Grounding Assessment

**Strong grounding:**
- Hazard tiering (DO-178C DAL adaptation)
- FMEA/FTA mapping to per-step/post-orchestration split
- Concrete checklist criteria (each grounded in observed failure)

**Moderate grounding:**
- Pipeline placement (Option C) — supported by cost analysis but not externally validated
- Model tier elevation — HITL pattern adapted but no direct precedent for LLM-generates-LLM-consumed-code

**Thin grounding:**
- LLM-specific failure modes — no external framework; internal evidence strong but N=1 incident
- Agent-in-the-loop analysis (C-3) — novel concept, no established methodology

## Sources

### External
- [DO-178C Safety Standard](https://en.wikipedia.org/wiki/DO-178C) — Design Assurance Levels, verification process
- [NASA Power of 10](https://www.perforce.com/blog/kw/NASA-rules-for-developing-safety-critical-code) — Safety-critical code rules (Holzmann/JPL)
- [FMEA vs FTA Comparison](https://creately.com/guides/fta-vs-fmea/) — Bottom-up vs top-down safety analysis
- [Evaluation Checklists: Quality Gate for AI Code](https://www.ivanturkovic.com/2026/02/10/evaluation-checklists-quality-gate/) — 5-dimension checklist, specialized review agents
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/) — LLM05 Improper Output Handling
- [AI Agent Safety FAQ](https://skywork.ai/blog/ai-agent/ai-agent-safety-faq) — HITL gating for destructive actions
- [Veracode GenAI Code Security Report 2025](https://www.veracode.com/blog/genai-code-security-report/) — 1.7× issue rate in AI-generated code
- [AI Code Quality Metrics 2026](https://www.secondtalent.com/resources/ai-generated-code-quality-metrics-and-statistics-for-2026/) — 1.75× logic error rate
- [CWEval: Security of LLM-Generated Code](https://arxiv.org/html/2504.20612v1) — func-sec@k metrics, 25-35% security gap
- [SafeGenBench: Security Benchmarking](https://beta.ai-plans.com/file_storage/2cdf7405-ac56-40b0-8e97-e97f3e47fbb9_2506.05692v1.pdf) — 558 prompts, dual-judge, 37.4% zero-shot
- [OWASP Gen AI Security Project](https://genai.owasp.org/llm-top-10/) — Full LLM risk taxonomy
- [AI Agent Security Checklist](https://ardor.cloud/blog/ai-agent-security-implementation-checklist) — HITL for destructive agent actions

### Internal
- `tmp/ground-internal-safety-review.md` — Opus brainstorm (9 sections, incident-grounded)
- `plans/worktree-merge-data-loss/reports/diagnostic-comparative-analysis.md` — 3-way review diagnostic
- `plans/worktree-merge-data-loss/design.md` — D-3 defect analysis (output-as-instruction)
