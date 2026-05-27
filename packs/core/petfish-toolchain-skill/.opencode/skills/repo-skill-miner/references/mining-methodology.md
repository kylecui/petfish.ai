# Repo Skill Mining Methodology

## Purpose

`repo-skill-miner` exists to answer one question: which workflows inside a repo
are worth extracting into reusable PEtFiSh skills?

The answer is rarely "all of them". A good mining pass separates:

- durable workflows
- repo-specific glue
- unsafe automation
- reference-only content

## Evaluation flow

1. **Read the repo framing**
   - README
   - top-level directories
   - package manifests
   - CI, Docker, Makefile, scripts, workflow files
2. **Locate repeatable workflow signals**
   - setup
   - build
   - test
   - deploy
   - lint
   - release
   - debug
   - generate
   - audit
3. **Map each workflow to skill boundaries**
   - trigger phrase
   - expected inputs
   - expected outputs
   - tool requirements
   - likely risks
4. **Score the candidate**
5. **Reject weak candidates early**
6. **Write a mining report, not a repo summary**

## Value domains

These domains usually contain reusable skill material, but each one has a
different mining lens.

| Domain | What to look for | Typical candidate skills |
|---|---|---|
| AI apps | app bootstrapping, eval loops, prompt assets, smoke tests | app-runtime-bootstrap, prompt-regression-runner |
| Agent frameworks | graph definitions, orchestration flows, agent tests | agent-workflow-mapper, agent-debug-runner |
| MCP | server layout, tool registration, transport config, safety checks | mcp-server-tester, mcp-risk-reviewer |
| RAG | ingestion, indexing, retrieval eval, vector DB config | rag-pipeline-debugger, retrieval-benchmark-runner |
| System design | architecture docs, diagrams, scenario decomposition | usually reference-heavy; only skillize if there is a repeatable analysis workflow |
| Dev tools | CLI tasks, Makefile targets, CI/CD, codegen, lint/test automation | repo-task-runner, ci-workflow-triager |
| Local model stacks | model runtime setup, pull/run scripts, quantization, benchmarking | local-model-bootstrap, ollama-workflow-runner |

## Candidate scoring

Score each dimension from 1-5.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Reusability | one-off, repo-locked | reusable within a niche | reusable across teams/repos |
| Automation-friendliness | mostly judgment/manual | mixed manual + automation | agent can drive end-to-end |
| Safety | high blast radius or secret-heavy | manageable with guardrails | low-risk and easy to sandbox |
| Demand | rare edge case | common in one domain | broadly useful and repeatedly requested |

Recommended weighting:

- Reusability: 35%
- Automation-friendliness: 30%
- Safety: 20%
- Demand: 15%

Interpretation:

- **4.0-5.0**: high-priority skill candidate
- **3.2-3.9**: medium-priority candidate
- **below 3.2**: usually document only or keep as a low-priority idea

## Anti-patterns

These usually should **not** become skills:

1. **One maintainer's personal release ritual**
   - depends on local credentials
   - relies on tribal knowledge
   - mutates production without guardrails
2. **Thin wrappers around a single command**
   - little reasoning value
   - easier as raw docs or shell alias
3. **Reference-only repos**
   - theory, examples, or reading lists without executable workflows
4. **Generated or vendored content**
   - build output, caches, lockfile churn, copied upstream code
5. **Unsafe admin automation**
   - mass deletion
   - broad secret access
   - unattended deployment to sensitive systems
6. **Too-vague ideas**
   - "understand this project"
   - "do the DevOps"
   - "work on the codebase"

## Security review prompts

For every candidate, ask:

- Does it require secrets, tokens, or production credentials?
- Does it modify infrastructure, registries, or external services?
- Can it expose code, logs, or internal docs externally?
- Does it execute arbitrary scripts or unreviewed Make targets?
- Can the workflow run in a dry-run or read-only mode first?

If the workflow is valuable but risky, keep it as a candidate and record the
guardrails. If the guardrails are unclear, downgrade or reject it.

## Repo-category reference set

Use the following repo families as mining calibration examples:

- `awesome-llm-apps` → AI app patterns, demos, prompt flows
- `LangChain` → chain/tool orchestration, agent helpers, integrations
- `LangGraph` → graph-based agent workflows, stateful orchestration
- `CrewAI` → multi-agent task coordination patterns
- `Ollama` → local model runtime, model pull/run workflows
- `awesome-mcp-servers` → MCP server categories, capability discovery
- `Qdrant` → vector DB operations, retrieval workflows, RAG support
- `system-design-primer` → mostly reference material; skillize only repeatable
  analysis workflows
- `awesome-claude-code` → skill inspiration, agent workflow patterns,
  packaging ideas

## Output expectations

A useful mining report should make the next step obvious:

- which skill to create first
- which workflows need scripts
- which workflows need security review
- which repo areas are not worth skillization

If the report cannot support `skill-author`, it is still too vague.
