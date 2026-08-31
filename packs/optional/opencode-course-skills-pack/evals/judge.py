#!/usr/bin/env python3
"""LLM-as-judge for course outline evaluation.

Five-dimension rubric (1-5 each) + overall pass/fail by mean threshold.
OpenAI-compatible chat completions API. Stdlib + urllib only.

Config via environment:
  JUDGE_API_URL  - base URL (e.g. https://api.openai.com/v1) or full endpoint
  JUDGE_API_KEY  - bearer token
  JUDGE_MODEL    - model name

Determinism: temperature=0 and the judge prompt is pinned by
JUDGE_PROMPT_VERSION. Any prompt text change must bump the version.

Usage:
  python judge.py --brief brief.txt --outline outline.md [--rules rules.txt]
  python judge.py --check-config
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

JUDGE_PROMPT_VERSION = "1.0"
DEFAULT_THRESHOLD = 4.0

DIMENSIONS = [
    "goal_alignment",
    "pedagogy_coverage",
    "assessment_validity",
    "learner_instructor_separation",
    "structure_integrity",
]

RUBRIC_TEXT = """\
评分维度与锚点（每维 1-5 分，仅整数）：

1. goal_alignment（目标对齐）
   1=大纲与brief完全无关；2=仅标题相关；3=部分模块对齐brief目标；
   4=全部模块对齐brief且目标可测；5=目标可测且含受众/先修/收益闭环。

2. pedagogy_coverage（教学法覆盖）
   1=无任何教学法要素；2=仅罗列主题；3=有目标但缺实验或练习设计；
   4=目标/示例/练习/实验基本齐全；5=含渐退练习、形成性反馈与误解前置。

3. assessment_validity（测评有效性）
   1=无测评；2=测评与目标脱节；3=有quiz/assignment但未绑定目标；
   4=测评类型匹配目标层级；5=题型-目标矩阵清晰且含评分标准说明。

4. learner_instructor_separation（师生分离）
   1=学员材料混入答案/讲师提示；2=边界含糊；3=基本分离但有个别泄露风险；
   4=学员/教师材料边界清晰；5=分离机制显式且含泄露自检。

5. structure_integrity（结构完整）
   1=无结构；2=有模块但缺课时/评估声明；3=模块/课时/评估基本齐；
   4=结构齐全且命名一致；5=结构齐全且首模块导论、模块间递进清晰。
"""

SYSTEM_PROMPT = (
    "你是课程质量评审员。按给定rubric对课程大纲打分。"
    "只输出JSON，不要输出任何其他文字。"
)


def have_judge_config() -> bool:
    return bool(os.environ.get("JUDGE_API_KEY") and os.environ.get("JUDGE_API_URL"))


def build_user_prompt(brief: str, outline_text: str, pedagogy_rules: list[str]) -> str:
    rules_text = "\n".join(f"- {r}" for r in pedagogy_rules) or "- （无显式规则）"
    return (
        f"[judge-prompt-version: {JUDGE_PROMPT_VERSION}]\n\n"
        f"{RUBRIC_TEXT}\n"
        "教学法规则清单（大纲必须遵守）：\n"
        f"{rules_text}\n\n"
        "课程brief：\n"
        f"{brief}\n\n"
        "待评审大纲：\n"
        f"{outline_text}\n\n"
        '输出格式（严格JSON）：{"scores": {"goal_alignment": N, '
        '"pedagogy_coverage": N, "assessment_validity": N, '
        '"learner_instructor_separation": N, "structure_integrity": N}, '
        '"rationale": {"<dimension>": "<一句话理由>", ...}}'
    )


def _endpoint() -> str:
    base = os.environ["JUDGE_API_URL"].rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return base + "/chat/completions"


def call_judge(user_prompt: str) -> dict:
    """Call the judge model and return parsed scores dict."""
    payload = {
        "model": os.environ.get("JUDGE_MODEL", "gpt-4o-mini"),
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    req = urllib.request.Request(
        _endpoint(),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['JUDGE_API_KEY']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"judge API HTTP {exc.code}: {detail}") from exc
    content = body["choices"][0]["message"]["content"]
    return parse_judge_content(content)


def parse_judge_content(content: str) -> dict:
    """Extract and validate the scores JSON from model output."""
    text = content.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fence:
        text = fence.group(1)
    else:
        brace = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if brace:
            text = brace.group(0)
    parsed = json.loads(text)
    scores = parsed.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("judge output missing 'scores' object")
    for dim in DIMENSIONS:
        value = scores.get(dim)
        if not isinstance(value, int) or not 1 <= value <= 5:
            raise ValueError(f"judge score for '{dim}' is not an integer in 1-5: {value!r}")
    return {
        "scores": {dim: scores[dim] for dim in DIMENSIONS},
        "rationale": parsed.get("rationale", {}),
    }


def judge_outline(
    brief: str, outline_text: str, pedagogy_rules: list[str], threshold: float = DEFAULT_THRESHOLD
) -> dict:
    """Full judge pipeline: prompt -> call -> scores -> mean -> pass/fail."""
    prompt = build_user_prompt(brief, outline_text, pedagogy_rules)
    result = call_judge(prompt)
    mean = sum(result["scores"].values()) / len(DIMENSIONS)
    return {
        "prompt_version": JUDGE_PROMPT_VERSION,
        "model": os.environ.get("JUDGE_MODEL", "gpt-4o-mini"),
        "scores": result["scores"],
        "rationale": result["rationale"],
        "mean": round(mean, 2),
        "threshold": threshold,
        "pass": mean >= threshold,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM-as-judge for course outlines.")
    parser.add_argument("--brief", help="Path to course brief text file.")
    parser.add_argument("--outline", help="Path to outline markdown file.")
    parser.add_argument("--rules", help="Path to pedagogy rules file (one per line).")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Print whether judge env config is present, then exit.",
    )
    args = parser.parse_args()

    if args.check_config:
        configured = have_judge_config()
        print(json.dumps({"configured": configured, "prompt_version": JUDGE_PROMPT_VERSION}))
        return 0 if configured else 1

    if not args.brief or not args.outline:
        parser.error("--brief and --outline are required (or use --check-config)")
    if not have_judge_config():
        print("error: JUDGE_API_URL/JUDGE_API_KEY not set; use static mode instead", file=sys.stderr)
        return 2

    with open(args.brief, encoding="utf-8") as f:
        brief = f.read()
    with open(args.outline, encoding="utf-8") as f:
        outline = f.read()
    rules: list[str] = []
    if args.rules:
        with open(args.rules, encoding="utf-8") as f:
            rules = [line.strip() for line in f if line.strip()]

    result = judge_outline(brief, outline, rules, threshold=args.threshold)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
