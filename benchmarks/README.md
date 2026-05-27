# PEtFiSh Evaluation Framework

Regression test suite for PEtFiSh's Companion Gateway classification logic.
Uses simulated keyword-based classifiers — no LLM calls, no MCP servers, no network.

## Quick Start

```bash
cd benchmarks/scripts

# Gateway Topic Drift (multi-class)
python run_eval.py --dataset ../datasets/gateway-topic-drift.jsonl --module gateway

# Skill Sense Detection (binary)
python run_eval.py --dataset ../datasets/skill-sense.jsonl --module skill_sense

# Failure Signal Detection (binary)
python run_eval.py --dataset ../datasets/failure-signal.jsonl --module failure_signal

# Cost Routing (multi-class)
python run_eval.py --dataset ../datasets/cost-routing.jsonl --module cost_routing
```

**Options:**
- `--no-table` — skip per-entry pass/fail table
- `--json` — output results as JSON (for CI pipelines)

## Datasets

| Dataset | Entries | Task | Classes |
|---------|---------|------|---------|
| `gateway-topic-drift.jsonl` | 20 | Topic relation classification | continue, fork, switch, archive, reset |
| `skill-sense.jsonl` | 20 | Skill detection (binary) | detected, not_detected |
| `failure-signal.jsonl` | 15 | Failure signal detection (binary) | signal_detected, no_signal |
| `cost-routing.jsonl` | 20 | Task tier classification | gateway, worker, deep_coding, critic |

### gateway-topic-drift.jsonl

Tests Companion Gateway's `topic_detect` classification. Each entry has a `user_message`
and expected `relation` + `risk_level`.

**Test coverage:**
- **continue** (6 entries): Same-topic continuity — "继续上次的数据库迁移", "OK继续", "接着上面的代码写"
- **fork** (4 entries): Related but diverging — "在这个基础上做监控dashboard", "从API设计延伸出去"
- **switch** (6 entries): Different topic — "换个话题", "不说这个了", "Let's switch to..."
- **archive/reset** (4 entries): Context cleanup — "归档吧", "清空上下文重新开始"

### skill-sense.jsonl

Tests Companion Gateway's Tier 1 skill gap detection against known TRIGGERS keywords.

**Test coverage:**
- **deploy** (4 entries): 部署/上线/Docker/CI-CD keywords
- **course** (4 entries): 课程/教学/大纲/课时 keywords
- **research** (4 entries): 研究/调研/文献/市场分析 keywords
- **no-skill** (4 entries): General coding tasks that should NOT trigger skill detection
- **negative** (4 entries): Keywords used in non-action contexts — e.g. "部署这个变量是什么意思"

### failure-signal.jsonl

Tests Companion Gateway's Tier 0 failure signal detection (FAILURE_SIGNALS regex patterns).

**Test coverage:**
- **ppt** (4 entries): PDF/PPTX read failures
- **deploy** (4 entries): Deploy/Docker failure messages
- **testdocs** (3 entries): Test case generation failures
- **no-failure** (4 entries): Normal, successful responses

### cost-routing.jsonl

Tests task routing into cost tiers by complexity.

**Test coverage:**
- **gateway** (6 entries): Trivial queries — "what does git status do?", "add comment"
- **worker** (5 entries): Single-file edits — "fix the typo in auth.ts line 42"
- **deep_coding** (5 entries): Multi-file/complex — "implement JWT auth across the API", "refactor the entire error handling"
- **critic** (4 entries): Review/judgment — "review this PR for security issues", "is this architecture sound?"

## Eval Modules

Each module lives in `scripts/modules/<name>_eval.py` and exposes a single function:

```python
def classify(entry: dict) -> dict:
    """Return a dict with prediction keys matching the dataset's expected keys."""
```

| Module | Prediction Keys | Approach |
|--------|----------------|----------|
| `gateway_eval` | `predicted_relation`, `predicted_risk` | Topic continuity keywords |
| `skill_sense_eval` | `predicted_skill`, `predicted_detect` | TRIGGERS keyword matching + context filtering |
| `failure_signal_eval` | `predicted_signal`, `predicted_detect` | FAILURE_SIGNALS regex patterns |
| `cost_routing_eval` | `predicted_tier` | Complexity keywords + word count fallback |

## Metric Targets

| Dataset | Target Accuracy | Description |
|---------|----------------|-------------|
| `gateway-topic-drift` | ≥ 85% | Topic relation classification should be reliable for medium/high risk cases |
| `skill-sense` | ≥ 80% | Skill detection should have low false negatives; false positives are tolerable |
| `failure-signal` | ≥ 80% | Failure signals should be caught; false positives less critical |
| `cost-routing` | ≥ 75% | Tier routing is heuristic; expect some boundary cases to misclassify |

## Design Notes

- **Simulated, not integrated**: These evals use keyword-based simulation rather than calling
  actual MCP servers or APIs. This is intentional — they are regression tests for the
  classification heuristics, not integration tests.
- **Stdlib only**: No `pip install` required. All modules use only Python standard library.
- **Portable**: Works on any OS with Python 3.9+. No network, no file system dependencies
  beyond the datasets themselves.
- **CI-ready**: Exit code 0 on all-pass, 1 on any failure. Use `--json` for machine-readable output.

## Adding a New Eval

1. Create a JSONL dataset in `benchmarks/datasets/`
2. Create a module in `benchmarks/scripts/modules/<name>_eval.py` with a `classify(entry) -> dict` function
3. Run: `python run_eval.py --dataset ../datasets/<name>.jsonl --module <name>`

The harness auto-detects binary vs. multi-class by inspecting the dataset schema.
