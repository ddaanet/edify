# Memory Index

Active knowledge retrieval. Invoke `/when` or `/how` to recall decisions.

**Invocation:**
/when <trigger>        # behavioral knowledge (when to do X)
/how <trigger>         # procedural knowledge (how to do X)

**Navigation:**
/when .Section Title   # section content by heading name
/when ..file.md        # entire decision file (relative to agents/decisions/)

**Consumption:** This index is loaded via CLAUDE.md @-reference. Do NOT re-read this file. Scan entries, invoke `/when` or `/how` for details.

**Append-only.** Do not index content already loaded via CLAUDE.md fragments.









## agents/decisions/cli.md

/when getting current working directory
/how output errors to stderr
/when cli commands are llm-native | internal stdout markdown exit-code no-stderr
/how configure script entry points
/when writing CLI output | no destructive suggestions agents follow instructions
/when choosing feedback output format
/how format token count output
/when checking expected program state | boolean return not exception EAFP state-query
/when writing error exit code | consolidate display exit single call Click
/when call site expands under formatter | 5+ lines Black kwargs extract helper
/when raising exceptions for expected conditions | custom types not ValueError broad masking
/when adding error handling to call chain | layer separation context site display top
/when designing cli tools for llm callers | stdin stdout markdown no quoting structured
/when cli error messages are llm-consumed | facts only no suggestions STOP directive recovery

## agents/decisions/data-processing.md

/how write init files
/when placing helper functions
/when splitting large modules
/how encode file paths
/how resolve history directories
/how extract session titles
/how format session titles
/how detect trivial messages | filter noise skip short
/how order feedback extraction | layer feedback filter priority
/how validate session uuid files
/when sorting glob results
/how parse first line metadata
/how resolve agent ids to sessions
/how extract agent ids from sessions
/when handling malformed session data
/how handle optional field defaults

## agents/decisions/defense-in-depth.md

/when designing quality gates | layered defense multiple independent checks
/when placing quality gates | commit chokepoint scripted mechanical enforcement
/when splitting validation into mechanical and semantic | script deterministic agent judgment advisory
/when reviewing quality gate coverage | defense layer checklist
/when fixing behavioral deviations identified by RCA | structural fix environment prose

## agents/decisions/deliverable-review.md

/when identifying deliverable artifacts | classify artifact types review axes agentic prose code test
/when orchestrator handles review delegation | sub-agents lack Task all reviews post-commit
/when deliverable review catches drift | inter-file consistency holistic not per-step

## agents/decisions/execution-strategy.md

/when choosing execution tier | inline delegate orchestrate context window capacity three-tier
/when tier boundary is capacity vs orchestration complexity | Tier 1 Tier 2 Tier 3 prompt generation ad-hoc runbook
/when tier thresholds are ungrounded | file count cycle count calibration empirical measurement
/when relating execution tiers to complexity routing | design ceremony work type quality obligations execution mechanics

## agents/decisions/implementation-notes.md

/when using at-sign references
/when placing DO NOT rules in skills | skill constraint rules negative constraints
/when using session start hooks
/how filter user prompt submit hooks
/when using hooks in subagents
/when needing mcp tools in subagents
/when skill is already loaded
/when hook fragment alignment needed | recency primacy contradict reinforce
/when prompt caching differs from file caching | read appends API prefix
/when sub-agent rules not injected | rules fire main only domain context
/when treating commits as sync points
/when deciding to commit interactively
/when git branch rename writes config | sandbox config write failure
/when reading design classification tables
/how format runbook phase headers
/how prevent skill steps from being skipped | prose gates no tool call D+B hybrid
/when choosing hard or soft limits
/when hitting file line limits | code quality first not compression
/when lint rule requires code change | fix design problem not mechanical circumvention
/how format batch edits efficiently
/when precommit fails | fix before committing broken gate worse than none
/when editing runbook step or agent files | edit source phase files not generated
/when removing stale learnings on commit
/when edit tool reports stale success | Write after Bash dropped sandbox git-mv
/when custom agents not discoverable as subagent types | built-in Task frontmatter restart
/when phase files contain h2 headers in code blocks | extract_sections code fence boundary

## agents/decisions/markdown-tooling.md

/how pass model as cli argument
/how handle model alias resolution
/how integrate with anthropic api
/when counting tokens in empty files
/when expanding file glob patterns
/when fixing consecutive emoji lines
/how clean markdown before formatting
/when extending vs creating cleanup functions
/when handling invalid markdown patterns
/how order markdown processing steps
/how detect markdown line prefixes
/how indent nested markdown lists
/when evolving markdown processing
/when choosing markdown formatter tool

## agents/decisions/operational-practices.md

/when placing deliverable artifacts | plans vs tmp referenced later
/when requiring per-artifact vet coverage | corrector review batch momentum
/when launching task agents in parallel | single message batch
/when background agents crash | check output files recovery
/when refactoring agents need quality directives | deslop factorization
/when triaging external diagnostic suggestions | routing superseded annotate inline
/when relaunching similar task | resume prior agent id preserve context
/when exploration agents report false findings | verify file existence
/when scrubbing learnings before design input | validate against evidence
/when diagnosing review agent quality gaps | 2x2 experiment model tier input content controlled test
/when running multi-reviewer diagnostics | parallel independent cross-reference false positive
/when performing root cause analysis | multi-layer stop between layers
/when searching adjacent domains | correction not exclusion adjacent research
/when temporal validation required for analysis | git history correlation
/when inlining reference file subsets for optimization | knowledge ceiling partial subset full-Read
/when merging worktree with consolidated learnings | delta only post-consolidation
/when batch review routing overrides per-artifact judgment | single reviewer fabricates proportionality
/when discovery decomposes by data point | parametrized operation spot-check variation-table
/when verifying delivered plan artifacts | content line-counts signatures not file-existence
/when assessing fragment demotion | behavioral procedural workflow-specific dead-weight
/when evaluating recall system effectiveness | recognition retrieval metacognitive forced injection
/when loading context before skill edits | plugin-dev skill-development description frontmatter
/when reusable components reference project paths | hardcoding config pyproject
/when validate-runbook flags pre-existing files | lifecycle false-positive modify-before-create
/when execution routing preempts skill scanning | skill matching gate hook injection
/when skill sections cross-reference context | back-reference inline criteria framing
/when recovering broken submodule worktree refs | git worktree repair core.worktree

## agents/decisions/operational-tooling.md

/when git operation fails | read actual error confabulation license stop
/when no-op merge orphans branch | always create merge commit
/when naming tasks for worktrees | branch-suitable alphanumeric constraint
/when requiring clean git tree | no stash fragile merge rebase
/when failed merge leaves debris | abort untracked files clean
/when git lock error occurs | never delete lock report wait
/when tracking worktree tasks in session.md | inline marker filesystem query
/when comparing file versions across branches | diff content not line count
/when validating worktree merges | session.md merge autostrategy remerge
/when cli command fails and raw commands are denied | routing signal wrapper force retry
/when classifyHandoffIfNeeded bug occurs | foreground Task calls fail background works
/when sub-agents cannot spawn sub-agents | Task MCP hooks unavailable
/when resolving session.md conflicts during merge | checkout discard branch tasks verify
/when removing worktrees with submodules | core.worktree restore submodule merge check
/when importing artifacts from worktrees | git show branch transport scope ownership
/when workaround requires creating dependencies | two-step limit stop report
/when recovering agent outputs | task output files json extraction
/when extracting git helper functions | _git pattern subprocess reduction
/when fixture shadowing creates dead code | pytest fixture vs local function
/when test corpus defines correct behavior | fixtures are spec not workaround
/when DP matrix has zero-ambiguity | -inf initialization impossible states
/when phase numbering is flexible | 0-based or 1-based detect from first
/when checking self-referential modification | exclude plan own directory
/when avoiding CLI skill name collision | check built-ins before naming
/when choosing name | public handles discovery recall over cleverness
/when constraining task names for slug validity | layers dont share constraints

## agents/decisions/orchestration-execution.md

/when delegation requires commit instruction | agents leave tree dirty
/when limiting agent scope | context defines scope boundary relevant files structural
/when deduplicating delegation prompts | shared file reference
/when managing orchestration context | handoff not delegatable
/when partitioning work for parallel agents | no post-dispatch communication fire-and-forget
/when task agents skip submodule pointer | parent repo status check
/when commit precedes review delegation | uncommitted dirty tree agents
/when step agents leave uncommitted files | clean tree report commit invariant
/when running post-step verification | git status UNFIXABLE grep
/when planning is parallelizable | phase expansion concurrent agents
/when assuming interactive context | orchestration unattended timeout real
/when designing timeout mechanisms | independent guards spinning hanging
/when item-level escalation blocks execution | UNFIXABLE grep mechanical stop
/when local recovery suffices | refactor within design no global replan
/when global replanning is needed | design flaw scope creep runbook broken
/when stabilizing orchestrator model | sonnet before haiku optimization
/when using opus for RCA delegation | primary source verification
/when sonnet inadequate for synthesis | opus for multi-turn extraction
/when no model tier introspection available | no API ask or use hook
/when haiku rationalizes test failures | regression green phase bugs
/when haiku GREEN phase skips lint | tdd green verification lint check
/when classifying errors by tier | tier-aware self-classify report
/when choosing script vs agent judgment | scripting non-cognitive deterministic
/when script should generate metadata | validates not just validate
/when bootstrapping around broken tools | design as execution plan
/when resuming interrupted orchestration | checkpoint recovery recipe enforcement
/when vet flags unused code | test callers infrastructure design-intent not dead
/when delegating with corrections to prior analysis | exclude wrong item conflicting signals recency
/when ordering post-orchestration tasks | diagnostic fixes improvements sequence
/when assessing RED pass blast radius | over-implementation test-flaw correct
/when shared code is bifurcated | unifying over patching root cause
/when agent context has conflicting signals | common context competes phase-neutral
/when capturing requirements from conversation | capture over interview
/when measuring agent durations | sleep inflation tool use rate
/when analyzing sub-agent token costs | total_tokens cache decomposition
/when submodule commits diverge during orchestration | linear history pointer verify phase-boundary
/when selecting agent type for orchestrated steps | plan-specific mandatory restart

## agents/decisions/pipeline-contracts.md

/when choosing review gate | transformation table artifact type T1-T6.5 pipeline stages
/when routing artifact review | reviewer per artifact type skill-reviewer agent-creator corrector orchestrator delegation
/how review delegation scope template | scope IN OUT changed files requirements
/when UNFIXABLE escalation | fix-all pattern grep UNFIXABLE stop escalate
/when declaring phase type | tdd general inline per-phase typing model expansion review orchestration
/when phase qualifies as inline | outcome determined instruction prose config pre-resolved
/when vet escalation calibration | over-escalate UNFIXABLE pattern-matching uncertainty
/when vet flags out-of-scope items | DEFERRED vs UNFIXABLE blocking scope
/when vet receives execution context | filesystem state explicit IN OUT changed-files
/when corrector rejects planning artifacts | runbook-corrector routing
/when reviewing expanded phases | expansion reintroduces defects regression LLM failure modes
/when outline review produces ungrounded corrections | confabulated operation sequence fabricated fix-all sonnet opus
/when simplifying runbook outlines | pattern consolidation identical-pattern batching
/when selecting model for prose artifact edits | opus skills fragments agents design
/when selecting model for TDD execution | complexity type pattern state-machine synthesis
/when reviewing skill deliverable | cross-project context skill-reviewer interactive
/when concluding reviews | severity counts pending task no merge-readiness
/when routing implementation findings | unconditional design triage proportionality
/when selecting review model | match model to correctness property
/when holistic review applies fixes | grep all references fix-all occurrences
/when scoping vet for cross-cutting invariants | verification scope call-graph grep
/when reviewing final orchestration checkpoint | lifecycle audit stateful objects
/when adding verification scope to vet context | cross-cutting invariant indicators grep
/when review gates feel redundant | non-negotiable checkpoint completeness consistency
/when recall-artifact is absent during review | lightweight recall fallback
/when corrector agents lack recall mechanism | design-corrector outline-corrector recall loading
/when treating recall-artifact summary as recall pass | batch-resolve full content when-resolve
/when batch changes span multiple artifact types | proportionality per-file routing artifact-type
/when using inline execution lifecycle | Tier 1 Tier 2 entry gate corrector triage feedback
/how dispatch corrector from inline skill | standardized template baseline diff recall report
/when triage feedback shows divergence | classification comparison heuristics calibration log

## agents/decisions/project-config.md

/how inject context with rule files
/when naming model capability tiers
/how make skills discoverable | surface discovery layers agents miss
/when writing agent yaml frontmatter
/when verifying symlinks after operations
/when using heredocs in sandbox
/when parsing cli flags as tokens
/when finding project root in scripts
/how compose agents via skills | frontmatter inject prompt
/how recall sub-agent memory | bash transport when-resolve
/how augment agent context | always-inject on-demand two-tier
/when agent-creator reviews agents | plugin-dev write read fix
/when custom agents need session restart for discoverability | subagent_type agent lifecycle

## agents/decisions/prompt-structure-research.md

/when ordering fragments in CLAUDE.md | position bias fragment where to put
/when formatting rules for adherence
/when writing rules for different models
/when too many rules in context | managing rule count budget length
/when loading context for llm processing

## agents/decisions/testing.md

/how split test modules
/how apply mock patches correctly
/how test markdown cleanup
/when evaluating test success metrics
/when writing red phase assertions
/when testing presentation vs behavior
/when writing integration test assertions
/how validate migration conformance
/when preferring e2e over mocked subprocess | real git repos tmp_path
/when asserting pipeline idempotency | preprocessor remark roundtrip
/when detecting vacuous assertions from skipped RED | assertion strength
/when test setup steps fail | subprocess stderr swallowed self-diagnosing
/when testing CLI tools | click CliRunner in-process isolated filesystem
/when tests simulate merge workflows | branch as merged parent amend preserves
/when safety checks fail in tests | understand why fix scenario not suppress
/when green phase verification includes lint | just check test lint commit gate

## agents/decisions/validation-quality.md

/when choosing pydantic for validation
/how define feedback type enum
/when docstring formatting conflicts
/how manage cyclomatic complexity
/when tempted to suppress linting
/when adding strict type annotations
/how architect feedback pipeline
/how build reusable filtering module
/how detect noise in command output
/how categorize feedback by keywords
/how deduplicate feedback entries
/when filtering for rule extraction

## agents/decisions/workflow-advanced.md

/when seeding indexes before generation
/when adding entries without documentation
/when writing memory-index trigger phrases | articles heading alignment exact
/how merge templates safely
/when requirements change during execution
/when naming memory index triggers | activity at decision point not outcome
/when embedding knowledge in context
/when memory-index amplifies thin user input | sparse query recall cross-reference
/when analyzing task insertion patterns | origin segment priority position
/how name session tasks | prose keys task naming
/when compressing session tasks | classify sub-items contextual vs artifact
/when committing rca fixes
/when running precommit validation
/when tracking worktree tasks in session | inline marker pending slug filesystem-state

## agents/decisions/workflow-core.md

/when using oneshot workflow
/how integrate tdd workflow
/when optimizing design phase output
/how document three stream planning
/when setting orchestrator execution mode
/when assessing orchestration tier
/how checkpoint runbook execution
/how structure phase grouped runbooks
/when cycle numbering has gaps
/when refactoring needs escalation
/how verify commits defense in depth
/when delegating without plan

## agents/decisions/workflow-execution.md

/how design with outline first approach
/when selecting model for design guidance
/when choosing model for design review
/when using conceptual explore | always opus generative divergence brainstorm
/when research required before outline | external prior art ground
/when design references need verification | glob disk verify names
/when review catches structural issues
/when reviewing agent definitions
/when agent ignores injected directive | template context contradicts rules
/when step agent uses wrong model | orchestrator model differs
/when ordering tdd test cases
/how format runbook outlines
/how chain multiple skills together | continuation passing tail calls
/when using hook based parsing

## agents/decisions/workflow-optimization.md

/how end workflow with handoff and commit | chain handoff tail calls
/when handoff includes commit flag
/when context already loaded for delegation
/when complexity assessed twice | assessing routing layer efficiency double assessment
/when reusing review agent context
/when delegating well-specified prose edits | opus delegation ceremony cost pre-resolved
/when designing context preloading mechanisms | @ref duplication skill invocation prime
/when design ceremony continues after uncertainty resolves | two gates entry mid-stream re-check
/when design resolves to simple execution | execution readiness gate exit ramp prose inline
/when writing methodology | ground skill diverge converge external research general-first framing parallel agents

## agents/decisions/workflow-planning.md

/how expand outlines into phases | review phases iteratively expansion
/when assembling runbooks manually
/how use review agent fix all pattern
/how transmit recommendations inline
/how name review reports
/when writing test descriptions in prose | RED phase runbook test description
/when checking complexity before expansion
/when merging trivial cycles with adjacent work | consolidation gates
/when requirements mention agent or skill creation | scanning requirements
/when crossing phase boundaries
/when bootstrapping self-referential improvements | dependency graph ordering
/when requirements added after review | re-check traceability FRs
/when deleting agent artifacts | audit trail value vs redundant restate
/how write green phase descriptions
/when verifying model analysis results
/how implement domain validation
/when adding a new variant to an enumerated system | grep downstream enumeration sites
/when tdd cycles grow shared test file | line-limit split conditional 400 refactor
/when step file inventory misses codebase references | discovery grep propagation rename
/when triaging behavioral code changes as simple | structural criteria functions logic-paths moderate
