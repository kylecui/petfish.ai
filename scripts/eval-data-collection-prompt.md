# Eval Data Collection Prompt

Send this to team members who use PEtFiSh skills regularly. Their real queries will improve our trigger evaluation datasets.

---

## For Team Members

We're building an evaluation dataset to measure how well PEtFiSh skill descriptions trigger on real user queries. We need **actual queries you've typed** that successfully activated a specific skill.

### What to do

1. Search your AI chat history (OpenCode, Claude, Cursor, etc.)
2. Find messages where a PEtFiSh skill was activated
3. For each, record:
   - **The query you typed** (exact wording)
   - **Which skill activated** (e.g. `course-outline-design`, `deployment-executor`)
   - **Was the activation correct?** (yes = you wanted that skill; no = wrong skill fired)

### Output format

One JSON file per person. Use this structure:

```json
{
  "contributor": "your-name",
  "date": "2026-05-11",
  "entries": [
    {
      "query": "帮我设计一个3天的课程大纲",
      "skill": "course-outline-design",
      "correct": true
    },
    {
      "query": "review this pull request for security issues",
      "skill": "anti-sycophancy-calibration",
      "correct": false,
      "intended_skill": "security-risk-review",
      "notes": "calibration skill fired instead of security review"
    },
    {
      "query": "帮我把这个repo部署到测试服务器",
      "skill": "repo-service-lifecycle",
      "correct": true
    }
  ]
}
```

### What counts as a good entry

- **Best**: Queries in your natural language (Chinese, English, or mixed)
- **Best**: Queries where the wrong skill fired (these expose weaknesses)
- **Good**: Queries that correctly triggered a skill
- **Skip**: Slash commands like `/petfish` (those are exact-match, not trigger-based)
- **Skip**: Queries where no skill was involved (plain coding tasks)

### Where to look

- OpenCode session history
- Claude/Cursor chat logs
- Any saved conversation where you interacted with PEtFiSh skills

### How to submit

Save your JSON file as `evals/human/<your-name>.json` and submit via PR, or send it directly to the eval maintainer.

---

## For the Eval Maintainer

### Processing collected data

Human-collected queries go into `evals/human/`. To merge them into the per-skill eval datasets:

```bash
# 1. Generate baseline eval datasets (auto-generated from SKILL.md)
uv run scripts/gen_trigger_evals.py --output-dir evals/trigger

# 2. Manually merge high-value human queries into evals/trigger/<pack>/<skill>.json
#    - correct=true entries → add to should_trigger
#    - correct=false entries → add to the WRONG skill's should_not_trigger

# 3. Run the full eval suite
uv run scripts/run_all_trigger_evals.py --eval-dir evals/trigger --json > evals/baseline.json
```

### Priority skills for collection

Focus on skills where auto-generated tests are weakest:

1. **course pack** (6 skills) — pilot target for description compression
2. **companion pack** (10 skills) — high-traffic, most exposure to diverse queries
3. **deploy pack** (5+ skills) — operational queries tend to be varied
4. **research pack** (54 skills) — already has eval data, but human queries add value

### Quality bar

- At least 5 human queries per skill to meaningfully supplement auto-generated tests
- Prioritize false-trigger reports (wrong skill fired) — these are the highest-signal data points
