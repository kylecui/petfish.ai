# /// script
# requires-python = ">=3.10"
# ///
"""Simulate companion-gateway.ts logic to preview system prompt injection."""
import re

SKILL_TRIGGERS = {
    "deploy": ["deploy", "docker", "container", "systemd", "nginx", "ci/cd", "rollback", "ops"],
    "course": ["course", "curriculum", "syllabus", "lab", "learner", "instructor"],
    "ppt": ["ppt", "slide", "presentation", "keynote"],
    "writing": ["rewrite", "polish", "style", "de-ai"],
    "research": ["research", "study", "literature", "evidence", "survey"],
    "topic": ["topic", "context", "contamination", "fish-trail"],
    "review": ["review", "critique", "calibration", "sycophancy"],
    "testdocs": ["test case", "usage doc"],
    "petfish": ["petfish", "skill", "companion", "pack", "install"],
}

EVALUATIVE = ["好吗", "对吗", "是不是", "right?", "is this correct", "what do you think"]

FAILURE_SIGNALS = [
    (r"无法.*(打开|读取|解析).*(PDF|PPTX|PPT|幻灯片)", "ppt"),
    (r"(deploy|部署|Docker).*(fail|失败|error|错误)", "deploy"),
    (r"(上下文|context).*(混乱|污染|冲突|drift)", "context"),
]


def simulate_gateway(user_msg, assistant_msg, retry_count=0):
    sections = ["\n--- Simulated Companion Gateway Output ---\n"]
    sections.append("Mode: depth=balanced, rigor=false")

    # Failure signal
    for pattern, pack in FAILURE_SIGNALS:
        if re.search(pattern, assistant_msg, re.IGNORECASE):
            sections.append("WARNING Failure Signal: pack=" + pack + " recommended")
            break

    # Skill sense
    lower = user_msg.lower()
    matches = []
    for domain, keywords in SKILL_TRIGGERS.items():
        if any(kw in lower for kw in keywords):
            matches.append(domain)
    if matches:
        sections.append("Skill Sense: detected domains: " + ", ".join(matches))

    # Anti-sycophancy
    if any(p in user_msg.lower() for p in EVALUATIVE):
        sections.append("WARNING Anti-Sycophancy: evaluative question detected. Define rubric BEFORE concluding.")

    # Retry guard
    if retry_count >= 3:
        sections.append("BLOCKED Retry Guard: " + str(retry_count) + " failures. AUTHORIZATION REQUIRED.")
    elif retry_count >= 2:
        sections.append("WARNING Retry Guard: " + str(retry_count) + " failures. RETRY before workaround.")
    elif retry_count == 1:
        sections.append("INFO Retry Guard: 1 failure. May be transient.")

    # Web-grounding (always)
    sections.append("Web-Grounding: use context7/web-search-prime for library/API questions. Cite sources.")

    return "\n".join(sections)


tests = [
    ("TEST 1: Deploy request", "帮我把这个服务部署到Docker", "", 0),
    ("TEST 2: Evaluative question", "这个方案对吗？", "", 0),
    ("TEST 3: Retry guard (2 failures)", "重试一下", "", 2),
    ("TEST 4: Failure signal from prev turn", "换个思路", "无法读取这个PDF文件", 0),
    ("TEST 5: Normal coding (no triggers)", "帮我写一个Python函数计算斐波那契数列", "", 0),
]

for title, user, assistant, retry in tests:
    print("=" * 70)
    print(title)
    print("  User: " + user)
    if assistant:
        print("  Prev assistant: " + assistant)
    if retry:
        print("  Retry count: " + str(retry))
    print("=" * 70)
    print(simulate_gateway(user, assistant, retry))
    print()
