# Recall Artifact Lifecycle: External Research

Research into established frameworks for managing shared artifacts that are progressively refined across pipeline stages.

---

## 1. W3C PROV-DM (Provenance Data Model)

**Source:** https://www.w3.org/TR/prov-dm/

### Core Concepts

W3C PROV-DM is a standard for representing provenance information in heterogeneous environments. Core entity types:

- **Entity**: a thing (physical, digital, or conceptual) with fixed aspects — the artifact being tracked
- **Activity**: something that occurs over time and acts upon entities (produces, transforms, consumes)
- **Agent**: a responsible party bearing responsibility for an activity or entity

### Lifecycle State Transitions

PROV-DM models lifecycle via instantaneous event transitions:

- **Generation**: entity becomes available after production by an activity
- **Usage**: beginning of an entity being consumed by an activity
- **Derivation**: resulting entity is a revised version of some original (connects transformed versions)
- **Invalidation**: entity becomes unavailable — no further use or invalidation permitted afterward

Temporal constraint: generation and usage must precede invalidation. Activities are bounded by start/end events.

### Applicability to Recall Artifacts

Strong fit. PROV-DM provides the conceptual vocabulary for exactly the problem recall artifacts face:
- Derivation captures when a recall artifact is updated from a memory-index entry (entity → derived entity)
- Usage captures when a pipeline stage loads and applies recall context
- Invalidation captures when an artifact is superseded by a newer version
- The model makes staleness explicit: an artifact that is generated, used by stage N, then replaced (invalidated) by stage N+1, has a precise provenance graph

**Gap:** PROV-DM is a data model, not a convention system. It defines vocabulary but not lifecycle policy (when to invalidate, what triggers derivation). Policy must be layered on top.

---

## 2. OpenLineage

**Source:** https://openlineage.io/docs/ | https://github.com/OpenLineage/OpenLineage

### Core Concepts

OpenLineage is an open standard for lineage metadata collection. Core entities: **Job**, **Dataset**, **Run**. A Job consumes and produces Datasets; a Run is an execution of a Job.

Key extensibility mechanism: **Facets**. A facet is an atomic piece of metadata attached to any core entity. Emitting a new facet with the same name for the same entity replaces the previous instance entirely. Facets can capture schema, column distributions, query plans, source code — or arbitrary custom metadata.

### Metadata Enrichment Across Stages

OpenLineage models progressive enrichment via run events with a defined lifecycle:
- `START` event: run begins, initial metadata emitted
- Intermediate events: additional facets attached as processing proceeds
- `COMPLETE`/`FAIL`/`ABORT` event: run concludes, final metadata state captured

Each stage in a pipeline emits events. The lineage backend accumulates the full history. Downstream consumers can query the lineage backend to understand what happened upstream before they act.

### Applicability to Recall Artifacts

Partial fit. OpenLineage's facet model maps cleanly onto recall artifact enrichment: each pipeline stage could emit a facet representing what recall entries it loaded and applied. The run event lifecycle (START → processing → COMPLETE) maps onto skill execution.

**Gap:** OpenLineage targets observability of existing pipelines — it is a metadata collection standard, not a lifecycle enforcement mechanism. It does not define conventions for when artifacts should be invalidated, updated, or retired.

---

## 3. Artifact Promotion Pipeline (CI/CD DevOps)

**Sources:**
- https://www.harness.io/harness-devops-academy/artifact-lifecycle-management-strategies
- https://www.withcoherence.com/articles/artifact-management-in-cicd-pipelines-guide

### Core Concepts

CI/CD artifact lifecycle follows a promotion model: artifacts move through repository tiers, and promotion is a gated transition requiring validation at each stage.

Standard lifecycle stages:
1. **Creation/Build**: artifact produced with version tag and initial metadata
2. **Testing/Validation**: artifact validated against quality gates
3. **Storage/Publication**: artifact stored in registry with consistent naming
4. **Promotion**: identical binary promoted across environments (dev → staging → production)
5. **Maintenance**: monitored for vulnerabilities, patched as needed
6. **Archival/Deletion**: retired per retention policy (version-based, time-based, or usage-based)

**Immutability principle**: what is promoted is identical to what was tested. Promotion does not modify the artifact; it changes its classification.

**Retention policies**:
- Version-based: keep last N versions
- Time-based: retain for defined duration
- Usage-based: prune artifacts not accessed within a period

### Applicability to Recall Artifacts

Partial fit with important limitations. The promotion model's immutability principle is a useful constraint — a recall artifact loaded at /design should not be silently modified mid-execution; a new version should be generated. The retention policy vocabulary (version-based, time-based, usage-based) is applicable to recall artifact pruning.

**Gap:** CI/CD artifact lifecycle assumes binary artifacts — the artifact is the deployable unit, and promotion is about environment context. Recall artifacts are knowledge artifacts whose content is progressively enriched (not promoted unchanged). The binary immutability principle does not map directly; recall artifacts are expected to accumulate content across pipeline stages.

---

## 4. HL7 FHIR / CRMI Knowledge Artifact Lifecycle

**Source:** https://build.fhir.org/ig/HL7/crmi-ig/artifact-lifecycle.html

### Core Concepts

The HL7 Canonical Resource Management Infrastructure (CRMI) defines a lifecycle for knowledge artifacts (clinical guidelines, value sets, measures) that persist and are consumed across healthcare systems. This is the closest analog to knowledge artifacts (vs. binary artifacts).

**Lifecycle states:**
- **Draft**: under development, not ready for normal use
- **Active**: ready for use in production
- **Retired**: withdrawn or superseded; should no longer be used

**Critical constraint**: `Active → Draft` is **forbidden**. An active artifact that needs revision requires a new version, not a rollback. Retired artifacts similarly cannot revert. This enforces forward-only progression.

**Versioning convention**: semantic versioning (`major.minor.patch[-label]`):
- Major: breaking changes or materially new capabilities
- Minor: non-breaking additions or refinements
- Patch: non-substantive corrections
- Labels (e.g., `-draft`, `-ballot`) for pre-release identification

**Two versioning policies**:
- **Metadata policy**: non-substantive metadata changes permitted without version increment (date must update)
- **Strict policy**: all modifications require version increment

**Canonical identity**: artifacts have version-independent canonical URLs and versioned references (via `url|version` notation). Collections share versions; dependency manifests enable stable resolution.

### Applicability to Recall Artifacts

Strong fit — the strongest of all frameworks found. Key mappings:

- The Draft/Active/Retired state machine directly models recall artifact lifecycle: a recall artifact in construction (draft), in active use across pipeline stages (active), and eventually superseded by a regenerated artifact (retired)
- The `Active → Draft` prohibition maps onto the problem of "stale recall artifact": you don't roll back a recall artifact to un-loaded state; you generate a new version
- Semantic versioning provides a naming convention for recall artifact versions that makes staleness detectable
- Canonical URL + versioned reference maps onto the recall artifact file path + a version marker that pipeline stages can check

**Gap:** CRMI is designed for long-lived clinical knowledge artifacts with formal governance. The overhead of full semantic versioning may exceed what recall artifacts require. The framework assumes formal review gates between states; recall artifact transitions would need to be automated.

---

## 5. Rational Unified Process (RUP) — Artifact Refinement Across Phases

**Source:** https://en.wikipedia.org/wiki/Rational_unified_process

### Core Concepts

RUP organizes software development into four phases (Inception, Elaboration, Construction, Transition), each containing multiple iterations. Artifacts are defined per discipline (Requirements, Analysis and Design, Implementation, Test, etc.) and are **progressively refined** across phases — not created once.

Key principle: **each discipline is addressed in every iteration, but emphasis shifts**. Requirements artifacts are heavily worked in Inception/Elaboration, lightly refined in Construction. Implementation artifacts dominate Construction.

Artifacts in RUP are first-class process outputs: every discipline has named artifacts, and workflows specify which activities produce and consume which artifacts. The RUP content framework tracks ownership (which role creates/maintains) and lifecycle (which phases create, refine, finalize an artifact).

Milestone gates at phase boundaries enforce that certain artifacts meet completion criteria before the next phase begins.

### Applicability to Recall Artifacts

Partial fit as a structural model. RUP's multi-phase refinement pattern maps onto the recall artifact lifecycle: an artifact produced in /requirements is refined in /design, further refined in /runbook, and finally consumed in /orchestrate. RUP's discipline-ownership model could inform which pipeline stage "owns" (has write authority over) a recall artifact at each stage.

**Gap:** RUP artifacts are human-readable deliverables (use case models, architecture documents) maintained by human roles. The automation of recall artifact updates differs from manual authoring. RUP also has no mechanism for artifacts that are auto-generated from other sources (memory-index → recall artifact).

---

## 6. TOGAF ADM — Architecture Repository

**Source:** https://togaf.visual-paradigm.com/2023/10/10/architectural-artifacts-in-togaf-adm-a-comprehensive-overview/

### Core Concepts

TOGAF's Architecture Development Method (ADM) produces artifacts across eight phases (Preliminary through Technology Architecture). The **Architecture Repository** is a centralized store where all artifacts are held, versioned, and referenced.

Key concepts:
- **Deliverables**: formally reviewed, approved work products at phase milestones
- **Artifacts**: work products within deliverables (catalogs, matrices, diagrams)
- **Architecture Building Blocks (ABBs)**: reusable components that artifacts describe

Artifacts in TOGAF are progressively augmented: the Business Architecture phase produces a foundation that Information Systems and Technology Architecture phases build upon. Later phases reference and refine earlier artifacts rather than replacing them.

**Requirements Management** is a continuous phase that feeds into all other phases — requirements artifacts are persistent, updated throughout the lifecycle.

### Applicability to Recall Artifacts

Limited direct applicability — TOGAF is a heavyweight enterprise architecture framework with human governance. However, two concepts are useful:

- The **Architecture Repository** pattern: a single canonical store for all artifacts that all phases read from and write to, with versioning. This directly maps onto a centralized recall artifact store rather than file-per-plan approach.
- The **continuous requirements phase**: requirements artifacts persist throughout and are updated by all phases — not a waterfall of one-time production. This models how recall artifacts should work across pipeline stages.

**Gap:** TOGAF assumes human architects reviewing and approving artifact updates at each milestone. No automated lifecycle.

---

## 7. Google ADK — Artifact Service

**Source:** https://google.github.io/adk-docs/artifacts/

### Core Concepts

Google's Agent Development Kit (ADK) treats artifacts as named, versioned binary data associated with either a session or a user. The framework provides:

- **Automatic versioning**: `save_artifact()` automatically increments version numbers
- **Explicit version retrieval**: `load_artifact(version=N)` for historical access; default fetches latest
- **Scope model**: session-scoped (ephemeral, tied to one interaction) vs. user-scoped (persistent across sessions, via `"user:"` prefix)
- **Storage backends**: InMemoryArtifactService (development) vs. GcsArtifactService (production)

Context compaction: ADK addresses context growth through asynchronous compaction — older events summarized into condensed form, with pruning of source data. Sessions serve as durable ground truth; working contexts are ephemeral computed projections optimized per invocation.

**Handle pattern**: large data objects stored externally, lightweight references in working context. Artifacts are offloaded from working context after model call completes.

### Applicability to Recall Artifacts

High applicability for implementation design. ADK's artifact service models exactly the infrastructure needed for recall artifacts:

- Session-scoped vs. user-scoped maps onto plan-scoped (per-execution) vs. project-scoped (persistent across sessions) recall artifacts
- Automatic versioning removes manual version bookkeeping
- The handle pattern maps onto recall artifact references in agent prompts — agents reference the artifact by name rather than inlining its full content

**Gap:** ADK is a runtime framework, not a lifecycle convention system. It handles storage and retrieval but not the semantic lifecycle (when is a recall artifact stale? when should it be retired?).

---

## 8. LangGraph — Shared State Across Agent Nodes

**Source:** https://docs.langchain.com/oss/python/langgraph/workflows-agents | https://blog.langchain.com/langgraph-multi-agent-workflows/

### Core Concepts

LangGraph models multi-agent workflows as directed graphs where each node is an agent. A single **StateGraph** object holds shared state that all nodes read from and write to. Updates are merged via **reducer logic** — nodes don't replace state, they contribute updates that are merged into the shared object.

Key properties:
- **Cyclical graphs**: enables loops and conditional branching — revisiting nodes is a first-class pattern
- **Reducer-based merging**: prevents write conflicts between parallel agents
- **Orchestrator access**: orchestrator node reads all worker outputs from shared state and synthesizes final output

Communication pattern: each worker maintains its own context; all worker outputs write to shared state keys accessible to the orchestrator.

### Applicability to Recall Artifacts

Useful as an implementation model for pipeline-stage shared state. The StateGraph pattern maps onto recall artifacts as shared state: each pipeline stage reads the current recall artifact, potentially adds to it, and the reducer ensures non-destructive accumulation. The cyclical graph property models iterative pipeline stages (e.g., /runbook outline → review → revision) without requiring new artifact instances per cycle.

**Gap:** LangGraph manages runtime state within a single orchestrated execution. It does not address cross-session persistence (what happens to state between pipeline runs) or artifact retirement across multiple executions over time.

---

## 9. Requirements Traceability Matrix (RTM)

**Sources:**
- https://www.testrail.com/blog/requirements-traceability-matrix/
- https://www.perforce.com/resources/alm/requirements-traceability-matrix

### Core Concepts

The RTM is a document/tool that maps relationships between requirements and other artifacts (design specs, test cases, source code, defects). It supports both:

- **Forward traceability**: requirement → design → implementation → test
- **Backward traceability**: defect → test result → requirement

RTM lifecycle follows the project: created at requirements phase, updated through design, implementation, and testing. Status fields track current state of each requirement's lifecycle. Bidirectional traceability ensures no requirement is lost and no implementation lacks a requirement.

### Applicability to Recall Artifacts

Limited direct applicability, but the **bidirectionality concept** is relevant. Recall artifacts today are forward-only: memory-index entries flow into pipeline stages. A bidirectional model would also trace which decisions were loaded and applied at which stage — enabling backward queries ("which pipeline executions loaded this decision entry?"). This would directly address the staleness detection problem.

**Gap:** RTMs are human-maintained matrices. The automation overhead is high. The RTM structure (spreadsheet-style mapping) does not map onto the recall artifact format (markdown text with embedded context).

---

## 10. SLSA (Supply-chain Levels for Software Artifacts)

**Source:** https://slsa.dev/ | https://slsa.dev/spec/v1.0/levels

### Core Concepts

SLSA is a security framework defining levels of artifact integrity assurance. The core concept for lifecycle purposes is **provenance**: a machine-readable attestation of how, where, and by whom an artifact was built.

SLSA levels build on each other:
- Level 1: provenance exists describing build process
- Level 2: provenance generated by CI/CD pipeline with cryptographic signatures
- Level 3: build system resistant to tampering, strong access controls

The build track separates concerns: source integrity, build integrity, and dependency integrity are tracked independently.

### Applicability to Recall Artifacts

Limited but useful for one specific sub-problem: **provenance attestation**. If recall artifacts are generated from memory-index entries, a SLSA-inspired provenance record would capture: which memory-index entries were included, when, by what process, and from what source files. This enables staleness detection (if source files changed since provenance was generated, artifact may be stale).

**Gap:** SLSA is a security framework for supply chain integrity, not a lifecycle management framework. It does not address consumption, augmentation, or retirement conventions.

---

## Synthesis: Applicable Patterns for Recall Artifact Lifecycle

### Pattern 1: Forward-Only State Transitions (HL7 CRMI)

The strongest applicable constraint: active artifacts do not regress to draft. Applied to recall artifacts: once a recall artifact is in active use by a pipeline stage, it is not modified in place. Refinement creates a new version. Staleness triggers new version generation, not artifact mutation.

**Convention**: recall artifacts carry a `status` field (draft / active / retired) and a `version` marker. Pipeline stages check status before consuming.

### Pattern 2: Facet-Based Progressive Enrichment (OpenLineage)

Each pipeline stage emits metadata about what it consumed and what it added. Rather than one monolithic artifact being mutated, the artifact accumulates facets — atomic metadata contributions from each stage. A facet for /design loads, a facet for /runbook loads, etc. Consuming stages can inspect facets to understand what prior stages did.

**Convention**: recall artifact sections tagged with the pipeline stage that added them.

### Pattern 3: Canonical Identity + Versioned References (HL7 CRMI)

Artifacts have a stable path-based identity (canonical URL equivalent) and version-specific references. Pipeline stages reference the specific version they loaded, not just "the current artifact." This enables staleness detection: if a later stage loads a different version than an earlier stage, the artifact changed mid-pipeline.

**Convention**: artifact file includes `generated_at` timestamp and `from_index_version` marker. Skills compare their loaded version to the current version before writing outputs.

### Pattern 4: Scope Tiering (Google ADK)

Session-scoped vs. user-scoped maps onto plan-scoped vs. project-scoped recall artifacts. Short-lived plan recall artifacts (specific to one execution run) vs. persistent project recall artifacts (the `recall-artifact.md` that persists across sessions).

**Convention**: two artifact tiers — `plans/<name>/recall-artifact.md` (plan-scoped, updated per design session) and `agents/recall-artifact.md` (project-scoped, updated by /codify).

### Pattern 5: Provenance Attestation (W3C PROV + SLSA)

Each artifact includes a provenance record: which source entries generated it, when, and from what source version. Staleness check: compare provenance generation time to memory-index modification time. If memory-index is newer, artifact is stale.

**Convention**: recall artifact frontmatter includes `generated_from: [list of source files]` and `generated_at: <timestamp>`. Staleness gate compares these timestamps.

### Pattern 6: Shared Accumulating State (LangGraph)

Pipeline stages contribute to a shared state object rather than overwriting it. Reducer logic ensures non-destructive accumulation. Applied to recall artifacts: each pipeline stage appends its loaded entries to a "loaded this session" log rather than regenerating the artifact.

**Convention**: recall artifact `## Session Log` section accumulates what was loaded per stage during current execution. Read-only from consuming stages; append-only for stages that resolve new entries.

---

## Gaps Across All Frameworks

None of the surveyed frameworks fully addresses the specific combination required by recall artifacts:

1. **Knowledge artifact (not binary)**: most CI/CD artifact lifecycle frameworks assume immutable binary artifacts. Knowledge artifacts are expected to be enriched.
2. **Autonomous consumption**: frameworks assume human review gates at state transitions. Recall artifact lifecycle must be fully automated.
3. **Staleness detection across sessions**: frameworks address within-pipeline lineage. Cross-session staleness (artifact generated last week, memory-index updated since) requires additional mechanisms.
4. **Null/empty state handling**: no framework addresses the case where an artifact does not yet exist or is intentionally empty — the "null mode" problem is specific to the recall artifact use case.

The closest framework is HL7 CRMI for lifecycle state conventions and W3C PROV-DM for provenance vocabulary. The most actionable implementation guidance comes from Google ADK's artifact service and LangGraph's shared state model.

---

## Sources

- [W3C PROV-DM: The PROV Data Model](https://www.w3.org/TR/prov-dm/)
- [OpenLineage Documentation](https://openlineage.io/docs/)
- [OpenLineage GitHub Specification](https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md)
- [HL7 CRMI Artifact Lifecycle](https://build.fhir.org/ig/HL7/crmi-ig/artifact-lifecycle.html)
- [SLSA: Supply-chain Levels for Software Artifacts](https://slsa.dev/)
- [SLSA Security Levels](https://slsa.dev/spec/v1.0/levels)
- [Harness: Artifact Lifecycle Management Strategies](https://www.harness.io/harness-devops-academy/artifact-lifecycle-management-strategies)
- [Google ADK Artifacts](https://google.github.io/adk-docs/artifacts/)
- [Google Developers Blog: Context-Aware Multi-Agent Framework](https://developers.googleblog.com/architecting-efficient-context-aware-multi-agent-framework-for-production/)
- [LangGraph Multi-Agent Workflows](https://blog.langchain.com/langgraph-multi-agent-workflows/)
- [LangGraph State Management](https://medium.com/@bharatraj1918/langgraph-state-management-part-1-how-langgraph-manages-state-for-multi-agent-workflows-da64d352c43b)
- [TOGAF Architectural Artifacts in ADM](https://togaf.visual-paradigm.com/2023/10/10/architectural-artifacts-in-togaf-adm-a-comprehensive-overview/)
- [Rational Unified Process - Wikipedia](https://en.wikipedia.org/wiki/Rational_unified_process)
- [Requirements Traceability Matrix - TestRail](https://www.testrail.com/blog/requirements-traceability-matrix/)
- [Requirements Traceability Matrix - Perforce](https://www.perforce.com/resources/alm/requirements-traceability-matrix)
- [dbt Artifacts Guide](https://www.elementary-data.com/post/dbt-artifacts-a-full-guide)
- [ISO/IEC/IEEE 12207 Software Life Cycle Processes](https://quality.arc42.org/standards/iso12207)
