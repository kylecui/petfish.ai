#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""PEtFiSh 安装体检 — 可视化验证升级后的全部新能力是否真正参与运行。

用法（项目根目录）:
    uv run .opencode/skills/fish-brain/scripts/verify_install.py
    # 或免升级直接用最新版体检:
    uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/.opencode/skills/fish-brain/scripts/verify_install.py

检查项（互相独立，单项失败不影响其余）:
    1. 插件文件        5个TS插件是否齐（含 companion-gateway.ts）
    2. 插件注册        opencode.json 的 plugin 数组 ≥4
    3. MCP 注册        skill-vault（v3.3.0+）等 MCP server 注册
    4. vault 自检      skill-vault server.py --selftest 子进程实测
    5. 网关版本        companion-gateway.ts 含 domains+Skill Vault（防陈旧副本）
    6. 规则文件        petfish-companion.md 含 Gateway Trace；petfish-toolchain.md 独立存在
    7. 索引质量        skill-index 的 domains/pack归属/market 条目
    8. pack 版本       registry 关键版本清单 + 最新 release 提示
    9. 新命令         /petfish load（v3.4.0+）
   10. course 能力    （装了才查）outline-constraints/双门禁/测评skill/交互件

退出码: 全PASS=0，任何FAIL=1（WARN不影响）。
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path.cwd()
O = ROOT / ".opencode"

PASS, FAIL, WARN, SKIP = "PASS", "FAIL", "WARN", "SKIP"
ICONS = {PASS: "✓", FAIL: "✗", WARN: "⚠", SKIP: "–"}
results: list[tuple[str, str, str]] = []  # (status, name, detail)


def record(status: str, name: str, detail: str = "") -> None:
    results.append((status, name, detail))


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def head(msg: str) -> None:
    print(f"\n{msg}")


# ---------------------------------------------------------------- 1. 插件文件
head("🐟 PEtFiSh 安装体检 (verify_install)")
print("─" * 62)
EXPECTED_PLUGINS = [
    "companion-gateway.ts",
    "system-prompt-rules.ts",
    "system-prompt-context-inject.ts",
    "topic-context-filter.ts",
    "fish-trail-compaction.ts",
]
plugin_dir = O / "plugin"
if plugin_dir.is_dir():
    present = [p for p in EXPECTED_PLUGINS if (plugin_dir / p).is_file()]
    extra = [p.name for p in plugin_dir.glob("*.ts") if p.name not in EXPECTED_PLUGINS]
    if len(present) == len(EXPECTED_PLUGINS):
        record(PASS, "插件文件", f"{len(present)}/{len(EXPECTED_PLUGINS)} 齐" + (f"（额外: {', '.join(extra)}）" if extra else ""))
    else:
        missing = [p for p in EXPECTED_PLUGINS if p not in present]
        record(FAIL, "插件文件", f"缺 {', '.join(missing)} — 重跑升级 --force")
else:
    record(FAIL, "插件文件", ".opencode/plugin/ 目录不存在")
    del EXPECTED_PLUGINS[:]  # 后续插件检查会跳过

# ---------------------------------------------------------------- 2. 插件注册
cfg = read_json(ROOT / "opencode.json")
if cfg and isinstance(cfg.get("plugin"), list):
    n = len(cfg["plugin"])
    record(PASS if n >= 4 else FAIL, "插件注册", f"opencode.json 注册 {n} 项" + ("" if n >= 4 else " — 应≥4，重跑升级 --force"))
elif cfg:
    record(FAIL, "插件注册", "opencode.json 无 plugin 数组")
else:
    record(FAIL, "插件注册", "opencode.json 不存在或不可解析")

# ---------------------------------------------------------------- 3. MCP 注册
if cfg and isinstance(cfg.get("mcp"), dict):
    mcps = list(cfg["mcp"].keys())
    has_vault = "skill-vault" in mcps
    detail = f"{', '.join(mcps)}"
    if has_vault:
        record(PASS, "MCP 注册", detail)
    else:
        record(FAIL, "MCP 注册", f"缺 skill-vault（v3.3.0+核心），现有: {detail}")
else:
    record(FAIL, "MCP 注册", "opencode.json 无 mcp 配置")

# ---------------------------------------------------------------- 4. vault 自检
vault_server = O / "mcp" / "skill-vault" / "server.py"
if vault_server.is_file():
    try:
        r = subprocess.run(
            [sys.executable, str(vault_server), "--selftest"],
            capture_output=True, text=True, timeout=60,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if r.returncode == 0 and "all pass" in (r.stdout or ""):
            record(PASS, "vault 自检", "四工具/去重/白名单/容错 全过")
        else:
            record(FAIL, "vault 自检", ((r.stdout or "") + (r.stderr or "")).strip()[-160:])
    except Exception as exc:
        record(FAIL, "vault 自检", f"执行失败: {exc}")
else:
    record(FAIL, "vault 自检", ".opencode/mcp/skill-vault/server.py 不存在")

# ---------------------------------------------------------------- 5. 网关版本（防陈旧）
gw = plugin_dir / "companion-gateway.ts"
if gw.is_file():
    text = gw.read_text(encoding="utf-8", errors="replace")
    has_domains = "skill-index.json" in text and "domains" in text
    has_vault_blk = "Skill Vault" in text
    has_autosearch = "marketplace_search" in text
    marks = []
    if not has_domains:
        marks.append("domains匹配(缺失=旧版网关!)")
    if not has_vault_blk:
        marks.append("发现块注入")
    if not has_autosearch:
        marks.append("自动搜索提示")
    if marks:
        record(FAIL, "网关版本", f"旧副本，缺: {'; '.join(marks)} — 重跑升级 --force")
    else:
        record(PASS, "网关版本", "domains匹配+发现块+自动搜索（v3.4.x新网关）")
else:
    record(SKIP, "网关版本", "无 companion-gateway.ts（插件检查已FAIL）")

# ---------------------------------------------------------------- 6. 规则文件
rules = O / "agents-rules"
if rules.is_dir():
    companion_md = rules / "petfish-companion.md"
    toolchain_md = rules / "petfish-toolchain.md"
    n_rules = len(list(rules.glob("*.md")))
    gt = companion_md.is_file() and "Gateway Trace" in companion_md.read_text(encoding="utf-8", errors="replace")
    if gt and toolchain_md.is_file():
        record(PASS, "规则文件", f"Gateway Trace ✓ + petfish-toolchain.md 独立 ✓（共{n_rules}个规则文件）")
    else:
        misses = []
        if not gt:
            misses.append("petfish-companion.md 缺 Gateway Trace（L1冲突未修复态!）")
        if not toolchain_md.is_file():
            misses.append("petfish-toolchain.md 不存在（工具链规则未独立）")
        record(FAIL, "规则文件", "; ".join(misses) + " — 重跑升级 --force")
else:
    record(FAIL, "规则文件", ".opencode/agents-rules/ 不存在")

# ---------------------------------------------------------------- 7. 索引质量
idx = read_json(O / "skill-index.json")
if idx and isinstance(idx.get("skills"), list):
    n_skills = len(idx["skills"])
    domains = idx.get("domains") or {}
    attributed = sum(1 for s in idx["skills"] if isinstance(s, dict) and s.get("pack"))
    market = len(((idx.get("available_packs") or {}).get("market")) or [])
    notes = []
    status = PASS
    if n_skills == 0:
        record(FAIL, "索引质量", "0 skills"); idx = None
    else:
        if not domains:
            status = FAIL; notes.append("domains=0（域匹配全灭 — v3.4.1前的安装器）")
        if attributed == 0:
            status = FAIL if domains else WARN
            notes.append("pack归属=0（缺口判定退化）")
        if market == 0:
            if status == PASS: status = WARN
            notes.append("market=0（离线安装或旧索引）")
        record(status, "索引质量", f"{n_skills} skills / {len(domains)} domains / {attributed}归属 / market {market}"
                + ("；" + "；".join(notes) if notes else ""))
else:
    record(FAIL, "索引质量", ".opencode/skill-index.json 缺失或不可解析")

# ---------------------------------------------------------------- 8. pack 版本
reg = read_json(O / "installed-packs.json")
latest = ""
try:
    with urllib.request.urlopen(
        "https://api.github.com/repos/kylecui/petfish.ai/releases/latest", timeout=5
    ) as resp:
        latest = json.loads(resp.read().decode()).get("tag_name", "")
except Exception:
    pass
if reg and isinstance(reg.get("packs"), dict):
    key = ["petfish-companion-skill", "petfish-toolchain-skill", "opencode-course-skills-pack", "fish-trail"]
    vers = {k: (reg["packs"].get(k) or {}).get("version", "未装") for k in key}
    detail = " ".join(f"{k.split('-')[0]}={v}" for k, v in vers.items() if v != "未装")
    note = f"；最新release: {latest}（对照 /petfish upgrade）" if latest else "；（离线，未查最新release）"
    record(PASS, "pack 版本", detail + note)
else:
    record(FAIL, "pack 版本", "installed-packs.json 缺失")

# ---------------------------------------------------------------- 9. 新命令
pf = O / "commands" / "petfish.md"
if pf.is_file():
    t = pf.read_text(encoding="utf-8", errors="replace")
    if "/petfish load" in t or "petfish load" in t:
        record(PASS, "新命令", "/petfish load 已分发（v3.4.0+）")
    else:
        record(WARN, "新命令", "petfish.md 无 load 子命令（v3.4.0前版本）")
else:
    record(SKIP, "新命令", "未装 companion pack")

# ---------------------------------------------------------------- 10. course 能力（装了才查）
cs = O / "skills" / "course-quality-assurance"
if cs.is_dir():
    checks = {
        "outline-constraints": (cs / "references" / "outline-constraints" / "schema.json").is_file(),
        "测评skill": (O / "skills" / "course-assessment-design" / "SKILL.md").is_file(),
        "反馈skill": (O / "skills" / "course-delivery-review" / "SKILL.md").is_file(),
        "教学法参考": (O / "skills" / "course-content-authoring" / "references" / "pedagogy-compact.md").is_file(),
        "/course-slides": (O / "commands" / "course-slides.md").is_file(),
        "交互件参考": (O / "skills" / "course-lab-design" / "references" / "interactive-artifacts.md").is_file(),
    }
    missing = [k for k, v in checks.items() if not v]
    if missing:
        record(FAIL, "course 能力", f"缺: {', '.join(missing)} — course pack < 1.5.0，重跑升级 --force")
    else:
        record(PASS, "course 能力", "约束/测评/反馈/教学法/课件桥/交互件 6/6")
else:
    record(SKIP, "course 能力", "未装 course pack")

# ---------------------------------------------------------------- 汇总
print("─" * 62)
n_pass = sum(1 for s, _, _ in results if s == PASS)
n_fail = sum(1 for s, _, _ in results if s == FAIL)
n_warn = sum(1 for s, _, _ in results if s == WARN)
n_skip = sum(1 for s, _, _ in results if s == SKIP)
for status, name, detail in results:
    print(f"  [{ICONS[status]}{status:^4}] {name:<8} {detail}")
print("─" * 62)
verdict = "安装健康 — 全部新能力就位" if n_fail == 0 else f"{n_fail} 项失败 — 重跑升级: uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --force --platform <平台>"
print(f"结果: {n_pass} PASS / {n_warn} WARN / {n_fail} FAIL / {n_skip} SKIP — {verdict}")
print("提示: 升级后需重启AI编码工具，插件/技能在session启动时加载。")
sys.exit(0 if n_fail == 0 else 1)
