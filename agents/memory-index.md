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
/how configure script entry points
/when choosing feedback output format
/how format token count output

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
/when reviewing quality gate coverage | defense layer checklist

## agents/decisions/deliverable-review.md

/when identifying deliverable artifacts | classify artifact types review axes agentic prose code test

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
/how format batch edits efficiently
/when removing stale learnings on commit

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
/when requiring per-artifact vet coverage | batch momentum skip prevention
/when launching task agents in parallel | single message batch
/when background agents crash | check output files recovery
/when refactoring agents need quality directives | deslop factorization
/when exploration agents report false findings | verify file existence
/when scrubbing learnings before design input | validate against evidence
/when diagnosing review agent quality gaps | 2x2 experiment model tier input content controlled test
/when temporal validation required for analysis | git history correlation
/when no-op merge orphans branch | always create merge commit
/when naming tasks for worktrees | branch-suitable alphanumeric constraint
/when requiring clean git tree | no stash fragile merge rebase
/when failed merge leaves debris | abort untracked files clean
/when git lock error occurs | never delete lock report wait
/when classifyHandoffIfNeeded bug occurs | foreground Task calls fail background works
/when sub-agents cannot spawn sub-agents | Task MCP hooks unavailable
/when extracting git helper functions | _git pattern subprocess reduction
/when fixture shadowing creates dead code | pytest fixture vs local function
/when test corpus defines correct behavior | fixtures are spec not workaround
/when DP matrix has zero-ambiguity | -inf initialization impossible states
/when phase numbering is flexible | 0-based or 1-based detect from first
/when checking self-referential modification | exclude plan own directory
/when avoiding CLI skill name collision | check built-ins before naming
/when choosing name | public handles discovery recall over cleverness

## agents/decisions/orchestration-execution.md

/when delegation requires commit instruction | agents leave tree dirty
/when limiting agent scope | context defines scope boundary relevant files structural
/when deduplicating delegation prompts | shared file reference
/when managing orchestration context | handoff not delegatable
/when partitioning work for parallel agents | no post-dispatch communication fire-and-forget
/when task agents skip submodule pointer | parent repo status check
/when commit precedes review delegation | uncommitted dirty tree agents
/when running post-step verification | git status UNFIXABLE grep
/when planning is parallelizable | phase expansion concurrent agents
/when item-level escalation blocks execution | UNFIXABLE grep mechanical stop
/when local recovery suffices | refactor within design no global replan
/when global replanning is needed | design flaw scope creep runbook broken
/when stabilizing orchestrator model | sonnet before haiku optimization
/when using opus for RCA delegation | primary source verification
/when sonnet inadequate for synthesis | opus for multi-turn extraction
/when no model tier introspection available | no API ask or use hook
/when choosing script vs agent judgment | scripting non-cognitive deterministic
/when script should generate metadata | validates not just validate
/when bootstrapping around broken tools | design as execution plan
/when assessing RED pass blast radius | over-implementation test-flaw correct
/when shared code is bifurcated | unifying over patching root cause
/when agent context has conflicting signals | common context competes phase-neutral
/when capturing requirements from conversation | capture over interview

## agents/decisions/pipeline-contracts.md

/when choosing review gate | transformation table artifact type T1-T6 pipeline stages
/when routing artifact review | reviewer per artifact type skill-reviewer agent-creator vet-fix orchestrator delegation
/how review delegation scope template | scope IN OUT changed files requirements
/when UNFIXABLE escalation | fix-all pattern grep UNFIXABLE stop escalate
/when declaring phase type | tdd or general per-phase typing model expansion review
/when vet escalation calibration | over-escalation pattern-matching not design
/when vet flags out-of-scope items | DEFERRED vs UNFIXABLE distinction
/when vet receives execution context | filesystem vs execution-time state
/when vet-fix-agent rejects planning artifacts | plan-reviewer routing
/when reviewing expanded phases | expansion reintroduces defects regression LLM failure modes
/when outline review produces ungrounded corrections | confabulated operation sequence fabricated fix-all sonnet opus
/when simplifying runbook outlines | pattern consolidation identical-pattern batching
/when validating runbook pre-execution | model-tags lifecycle test-counts red-plausibility structural

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

## agents/decisions/prompt-structure-research.md

/when ordering fragments in CLAUDE.md | position bias fragment where to put
/when formatting rules for adherence
/when writing rules for different models
/when too many rules in context | managing rule count budget length
/when loading context for llm processing

## agents/decisions/runbook-review.md

/when detecting vacuous items
/when ordering runbook dependencies
/when evaluating item density
/when spacing runbook checkpoints
/when planning for file growth

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
/how merge templates safely
/when requirements change during execution
/when embedding knowledge in context
/how name session tasks | prose keys task naming
/when committing rca fixes
/when running precommit validation
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
/how write green phase descriptions
/when verifying model analysis results
/how implement domain validation

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

## agents/decisions/workflow-optimization.md

/how end workflow with handoff and commit | chain handoff tail calls
/when handoff includes commit flag
/when context already loaded for delegation
/when complexity assessed twice | assessing routing layer efficiency double assessment
/when reusing vet agent context
/how design with outline first approach
/when selecting model for design guidance
/when choosing model for design review
/when brainstorming | always opus generative divergence
/when research required before outline | external prior art ground
/when design references need verification | glob disk verify names
/when vet catches structural issues
/when reviewing agent definitions
/when agent ignores injected directive | template context contradicts rules
/when step agent uses wrong model | orchestrator model differs
/when ordering tdd test cases
/how format runbook outlines
/how chain multiple skills together | continuation passing tail calls
/when using hook based parsing
