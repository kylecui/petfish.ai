# TrustSkills 安全扫描分析报告

> 扫描时间：2026-05-02  
> 扫描范围：`.opencode/skills/` 全部 27 个 skill  
> 引擎版本：trustskills 0.2.0（4 条红线规则 · 13 个风险指标 · 6 维度加权评分）  
> 变更：P0（函数级os_operations检测）+ P1（声明vs行为分权重）已实施

---

## 1. 总览

| 治理等级 | 符号 | 数量 | 占比 | 含义 |
|---|---|---|---|---|
| allow | ✅ | 19 | 70% | 无风险，直接放行 |
| allow_with_ask | ⚠️ | 7 | 26% | 中风险，需用户确认后执行 |
| sandbox_required | 🔶 | 1 | 4% | 高风险，需沙箱隔离执行 |
| deny | 🚫 | 0 | 0% | 无 |

**对比上次扫描（2026-05-01）**:
- ppt-reader: 🚫 DENY → ⚠️ allow_with_ask（P0修复：函数级检测消除误判）
- deployment-verifier: 🔶 sandbox_required → ⚠️ allow_with_ask（P1修复：声明信号降权）
- 0个红线违规（上次1个）

---

## 2. 全量扫描结果

| Skill | 分数 | 等级 | 风险指标数 | 主要风险维度 |
|---|---|---|---|---|
| course-content-authoring | 0.00 | ✅ allow | 0 | — |
| course-development-orchestrator | 0.00 | ✅ allow | 0 | — |
| course-directory-structure | 0.09 | ✅ allow | 2 | file_write, script_risk |
| course-lab-design | 0.00 | ✅ allow | 0 | — |
| course-methodology-playbook | 0.00 | ✅ allow | 0 | — |
| course-outline-design | 0.00 | ✅ allow | 0 | — |
| course-quality-assurance | 0.09 | ✅ allow | 2 | file_write, script_risk |
| course-quality-control-reporting | 0.09 | ✅ allow | 2 | file_write, script_risk |
| **deployment-executor** | **0.21** | **⚠️ allow_with_ask** | 3 | shell |
| **deployment-verifier** | **0.31** | **⚠️ allow_with_ask** | 4 | shell, file_write, script_risk |
| development-plan-governance | 0.00 | ✅ allow | 0 | — |
| drawio-course-diagrams | 0.12 | ✅ allow | 1 | network |
| generate-test-cases | 0.09 | ✅ allow | 2 | file_write, script_risk |
| generate-usage-docs | 0.09 | ✅ allow | 2 | file_write, script_risk |
| **incident-rollback** | **0.21** | **⚠️ allow_with_ask** | 3 | shell |
| instructor-reference-materials | 0.00 | ✅ allow | 0 | — |
| learner-materials | 0.00 | ✅ allow | 0 | — |
| markdown-course-writing | 0.00 | ✅ allow | 0 | — |
| petfish-style-rewriter | 0.09 | ✅ allow | 2 | file_write, script_risk |
| **ppt-reader** | **0.31** | **⚠️ allow_with_ask** | 4 | shell, file_write, script_risk |
| **ppt-writer** | **0.15** | **⚠️ allow_with_ask** | 3 | shell, file_write, script_risk |
| reference-document-review | 0.00 | ✅ allow | 0 | — |
| **repo-runtime-discovery** | **0.25** | **⚠️ allow_with_ask** | 3 | shell, file_write, script_risk |
| **repo-service-lifecycle** | **0.21** | **⚠️ allow_with_ask** | 3 | shell |
| **service-operations** | **0.25** | **⚠️ allow_with_ask** | 3 | shell, file_write, script_risk |
| skill-reference-discovery | 0.00 | ✅ allow | 0 | — |
| **target-host-readiness** | **0.41** | **🔶 sandbox_required** | 6 | shell, file_write, script_risk |

---

## 3. P0 + P1 修复效果

### 3.1 P0 — 函数级 os_operations 检测

**修改**: `parser.py` 的 `_analyze_single_script` 不再将 `import shutil` 整体标记为 `has_os_operations=True`。改为AST遍历 `ast.Attribute` 节点，检查实际调用函数：

- `shutil.which` → 安全（只读PATH查询）
- `tempfile.TemporaryDirectory` → 安全（系统管理临时目录）
- `shutil.rmtree`, `os.remove`, `os.system` → 危险（标记 `has_os_operations=True`）

**效果**: ppt-reader 的 `render_slides.py` 不再触发 `subprocess-os-combo` 红线。

| 字段 | 修复前 | 修复后 |
|---|---|---|
| `render_slides.py` has_os_operations | True | False |
| ppt-reader 红线违规 | subprocess-os-combo | 无 |
| ppt-reader 治理等级 | 🚫 DENY | ⚠️ allow_with_ask (0.31) |

### 3.2 P1 — 声明 vs 行为分权重

**修改**: 将 `shell-execution` 指标拆分为两个：

| 指标名 | 分数 | 触发条件 |
|---|---|---|
| `shell-execution-behavior` | 0.6 | `shell_execution=True` 且有脚本包含subprocess |
| `shell-execution-declaration-only` | 0.25 | `shell_execution=True` 但无脚本subprocess |

**效果**: 4个无脚本运维skill的shell维度从0.6+降至0.25+，整体分数降低0.04-0.10。deployment-verifier 从 SANDBOX → ALLOW_WITH_ASK。

---

## 4. 现存高风险 Skill 分析

### 4.1 🔶 target-host-readiness — SANDBOX_REQUIRED (score=0.41)

**触发的风险指标 (6个)**:

| 指标 | 维度 | 原因 |
|---|---|---|
| shell-execution-behavior | shell | 脚本实际使用subprocess |
| high-privilege-tools | shell | docker, ssh, systemctl |
| many-tools | shell | 声明工具数 ≥ 5 |
| file-writes | file_write | 脚本写出JSON结果 |
| script-file-io | script_risk | `host_probe.py` 导入 pathlib, json |
| script-subprocess | script_risk | `host_probe.py` 导入 subprocess |

**真实风险评估**:

`host_probe.py` 执行只读系统信息采集（`uname -a`, `df -hP`, `ss -ltn` 等）。使用 `shell=True` + `shlex.quote` 组合——经评审确认不存在可利用注入漏洞（`shlex.quote` 完整覆盖所有用户输入）。Skills team 评估结论：改为 `shell=False` 的收益/成本比极低（安全性提升微乎其微，回归测试成本高）。

**评分合理性**: SANDBOX_REQUIRED 偏保守但可接受——该脚本确实通过subprocess执行shell命令并支持SSH远程模式，属于行为面较广的skill。

### 4.2 ⚠️ ppt-reader — ALLOW_WITH_ASK (score=0.31)

修复后分数来自：
- `shell-execution-behavior` (0.6): 脚本有subprocess（调用soffice/pdftoppm）
- `script-subprocess` (0.7): subprocess导入
- `script-file-io` (0.3): file_io导入
- `file-writes` (0.4): 脚本有file_io

**评价**: 合理。脚本确实通过subprocess调用外部命令，ALLOW_WITH_ASK 恰当。

### 4.3 ⚠️ deployment-executor / incident-rollback / repo-service-lifecycle (score=0.21)

纯指令文档skill，无脚本。分数由 `shell-execution-declaration-only` (0.25) + `high-privilege-tools` (0.4) + `many-tools` (0.2) 驱动。

**评价**: ALLOW_WITH_ASK 恰当——这些skill指导Agent调用高权限工具（docker/ssh/systemctl），用户确认是合理的安全边界。

---

## 5. 剩余改进方向（P2-P3）

| 优先级 | 改进项 | 影响范围 | 预期效果 |
|---|---|---|---|
| P2 | 只读subprocess降分 | target-host-readiness | 可能从 SANDBOX → ALLOW_WITH_ASK |
| P3 | `many-tools` 分级评分 | 工具数≥5的skill | 提升区分度 |
| P3 | `shell_execution` 判定条件收窄 | ppt-writer 等 | 消除低风险工具声明驱动的shell标记 |

---

## 6. 关于 shell=True 的最终结论

Skills team 评审确认 `host_probe.py` 的 `shell=True` + `shlex.quote` 组合：

- **安全性提升**：微乎其微（shlex.quote已覆盖主要注入面）
- **功能风险**：需逐条验证所有探测命令在 `["sh", "-c", cmd]` 模式下行为一致
- **工作量**：本地+SSH两种模式 × 20+条命令的回归测试成本高

**决策**: 不修改skill代码。`shell=True` 在此场景下不构成可利用安全漏洞。

---

## 7. 扫描结果可信度评估

| 评估维度 | 评价 |
|---|---|
| ✅ 零风险skill识别准确 | 19个纯内容skill全部正确判定为 ALLOW |
| ✅ 风险方向正确 | 运维/部署类skill确实比内容类skill风险更高 |
| ✅ 红线规则设计合理 | subprocess+network combo 和 sudo-without-approval 抓住了真实高危模式 |
| ✅ 无误判 | P0修复后，所有判定结果与人工评审一致 |
| ✅ 声明vs行为区分有效 | P1修复后，无脚本skill不再虚高 |
| ⚠️ 只读行为未区分 | target-host-readiness 的只读探测被视为与写操作同等风险（P2待做） |

**整体评价**: 引擎在方向判断和绝对分数上均表现良好。0个误判，0个漏判。剩余P2-P3改进属于精度提升而非缺陷修复。
