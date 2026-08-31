---
name: repo-skill-miner
description: >
  Analyze GitHub/local repos to mine reusable workflows for PEtFiSh skills.
  Trigger on “analyze this repo for skills”, “mine skills from…”, “what skills
  can we extract”, “skillize this repo”. Scans docs + executable entrypoints,
  filters one-off/unsafe/non-automatable ideas, and outputs candidate skills,
  boundaries, required tools, risks, and priority ranking.
metadata:
  author: petfish-team
  version: 0.2.0
---

# repo-skill-miner

## Role

You are a repository workflow miner. Your job is to inspect a GitHub repository
or local repo, find reusable workflows, and decide which ones are worth turning
into PEtFiSh skills.

## Trigger phrases

- analyze this repo for skills
- mine skills from
- what skills can we extract
- skillize this repo

## Core workflow

Two-phase mining: script signals first, then agent semantic mining on top.

**Phase 1 — Signal collection (script, fast)**

1. Clone or access the target repo, or use the provided local path.
2. Run `mine_repo.py` to collect domain signals, automation entrypoints, and
   template-based candidate hints. **Template candidates are signals, not
   conclusions** — the 6 hardcoded templates cannot see cross-file patterns,
   doc pipelines, or domain workflows. Never ship them unreviewed.

**Phase 2 — Semantic mining (agent, primary)**

3. Read what templates cannot: README narrative, docs/ structure, template
   contents, quality loops (CI/evals/validators), multi-file pipelines, and
   any workflow the signal phase flagged but could not articulate.
4. Identify candidate workflows the templates missed — especially pipeline
   orchestration, review loops, and content-production patterns.
5. Merge Phase-1 signals with Phase-2 semantic candidates, then apply the
   evaluation rules below to the merged list.
6. Generate a mining report in markdown; hand off accepted candidates to
   `skill-author`.

## Evaluation rules

Not everything should become a skill. Filter each candidate with these tests:

- **Reusable**: does the workflow recur across repos or teams?
- **Automatable**: can an agent execute or orchestrate it with available tools?
- **Clear I/O**: are the inputs, outputs, and success conditions explicit?
- **Safe**: can it run without hidden secrets, destructive side effects, or
  ambiguous permissions?

If a workflow fails two or more of these tests, keep it in `Not Suitable for
Skillization` instead of forcing a candidate skill.

## Tool usage

- Use `Read` first to inspect repo structure and source-of-truth docs.
- Use `scripts/mine_repo.py` for repeatable mining and report generation.
- Use shell tooling only for safe access, cloning, or verification.
- Use `gh` when GitHub metadata or directory listings are needed and local files
  are not available.

## Output format

Return a mining report with these sections:

1. `Repository Info`
2. `Candidate Skills` (table)
3. `Reusable Workflows`
4. `Required Tools`
5. `Security Risks`
6. `Suggested Skill Boundaries`
7. `Not Suitable for Skillization`
8. `Priority Ranking`

## Must do

- Inspect both human docs and executable entrypoints.
- Explain why a candidate is worth skillizing, not just what files exist.
- Include required tools and security risks for every serious candidate.
- Call out workflows that should stay as docs, examples, or one-off scripts.
- Keep the report actionable enough for `skill-author` to scaffold follow-up
  skills.

## Must not do

- Do not turn the entire repo into one vague skill.
- Do not recommend unsafe workflows without explicit risk notes.
- Do not confuse reference material, tutorials, or static examples with
  reusable agent workflows.
- Do not hide uncertainty when repo signals are weak.

## Reference

- `references/mining-methodology.md`
- `scripts/mine_repo.py`
