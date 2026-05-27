# TrustSkills 安全扫描分析报告

> 扫描时间：2026-05-01  
> 扫描范围：`.opencode/skills/` 全部 27 个 skill  
> 引擎版本：trustskills 0.1.0（4 条红线规则 · 12 个风险指标 · 6 维度加权评分）

---

## 1. 总览

| 治理等级 | 符号 | 数量 | 占比 | 含义 |
|---|---|---|---|---|
| allow | ✅ | 18 | 67% | 无风险，直接放行 |
| allow_with_ask | ⚠️ | 6 | 22% | 中风险，需用户确认后执行 |
| sandbox_required | 🔶 | 2 | 7% | 高风险，需沙箱隔离执行 |
| deny | 🚫 | 1 | 4% | 触犯红线规则，拒绝执行 |

---

## 2. 全量扫描结果

| Skill | 分数 | 等级 | 红线违规 | 风险指标 | 风险维度 |
|---|---|---|---|---|---|
| course-content-authoring | 0.00 | ✅ allow | 0 | 0 | — |
| course-development-orchestrator | 0.00 | ✅ allow | 0 | 0 | — |
| course-directory-structure | 0.09 | ✅ allow | 0 | 2 | file_write, script_risk |
| course-lab-design | 0.00 | ✅ allow | 0 | 0 | — |
| course-methodology-playbook | 0.00 | ✅ allow | 0 | 0 | — |
| course-outline-design | 0.00 | ✅ allow | 0 | 0 | — |
| course-quality-assurance | 0.09 | ✅ allow | 0 | 2 | file_write, script_risk |
| course-quality-control-reporting | 0.09 | ✅ allow | 0 | 2 | file_write, script_risk |
| **deployment-executor** | **0.25** | **⚠️ allow_with_ask** | 0 | 3 | shell |
| **deployment-verifier** | **0.40** | **🔶 sandbox_required** | 0 | 5 | shell, file_write, script_risk |
| development-plan-governance | 0.00 | ✅ allow | 0 | 0 | — |
| drawio-course-diagrams | 0.12 | ✅ allow | 0 | 1 | network |
| generate-test-cases | 0.09 | ✅ allow | 0 | 2 | file_write, script_risk |
| generate-usage-docs | 0.09 | ✅ allow | 0 | 2 | file_write, script_risk |
| **incident-rollback** | **0.25** | **⚠️ allow_with_ask** | 0 | 3 | shell |
| instructor-reference-materials | 0.00 | ✅ allow | 0 | 0 | — |
| learner-materials | 0.00 | ✅ allow | 0 | 0 | — |
| markdown-course-writing | 0.00 | ✅ allow | 0 | 0 | — |
| petfish-style-rewriter | 0.09 | ✅ allow | 0 | 2 | file_write, script_risk |
| **ppt-reader** | **1.00** | **🚫 deny** | **1** | 0 | — (红线直接拒绝) |
| **ppt-writer** | **0.24** | **⚠️ allow_with_ask** | 0 | 3 | shell, file_write, script_risk |
| reference-document-review | 0.00 | ✅ allow | 0 | 0 | — |
| **repo-runtime-discovery** | **0.34** | **⚠️ allow_with_ask** | 0 | 4 | shell, file_write, script_risk |
| **repo-service-lifecycle** | **0.25** | **⚠️ allow_with_ask** | 0 | 3 | shell |
| **service-operations** | **0.34** | **⚠️ allow_with_ask** | 0 | 4 | shell, file_write, script_risk |
| skill-reference-discovery | 0.00 | ✅ allow | 0 | 0 | — |
| **target-host-readiness** | **0.41** | **🔶 sandbox_required** | 0 | 6 | shell, file_write, script_risk |

---

## 3. 高风险 Skill 逐项分析

### 3.1 🚫 ppt-reader — DENY (score=1.00)

**红线违规**: `[subprocess-os-combo]` — `scripts/render_slides.py` 同时存在 subprocess 和 os 级操作。

**脚本实际行为分析**:

| 脚本 | 用途 | imports | subprocess | os_ops | network | file_io |
|---|---|---|---|---|---|---|
| `pptx_extract.py` | 解析PPTX XML结构 | zipfile, xml, json, pathlib | ❌ | ❌ | ❌ | ✅ |
| `render_slides.py` | 调用soffice/pdftoppm转换 | subprocess, shutil, tempfile, json | ✅ | ✅ | ❌ | ✅ |

**触发机制详解**:

`render_slides.py` 的 imports 包含 `subprocess`（命中 `SUBPROCESS_IMPORT_MARKERS`）和 `shutil` + `tempfile`（命中 `OS_IMPORT_MARKERS = {"os", "shutil", "tempfile", "signal"}`）。引擎红线规则 `subprocess-os-combo` 检测到同一脚本 `has_subprocess=True` 且 `has_os_operations=True`，立即判定 DENY。

**实际风险评估**:

- `shutil` 的使用仅限于 `shutil.which("soffice")` — 这是一个**只读的PATH查询**，不涉及文件复制、删除、移动。
- `tempfile` 的使用是 `tempfile.TemporaryDirectory()` — 这是标准的临时目录管理，系统自动清理，不是持久化文件操作。
- `subprocess.run()` 调用的是 `soffice --headless --convert-to pdf` 和 `pdftoppm` — 都是确定性命令，不接受用户拼接的shell字符串，使用列表形式调用（非 `shell=True`）。

**结论**: 这是一个**误判**。`shutil.which` 和 `tempfile.TemporaryDirectory` 不应等同于"os级危险操作"。当前引擎将 `import shutil` 整体视为 os 操作，粒度过粗。

---

### 3.2 🔶 target-host-readiness — SANDBOX_REQUIRED (score=0.41)

**触发的风险指标 (6个)**:

| 指标 | 维度 | 原因 |
|---|---|---|
| shell-execution | shell | SKILL.md 声明了 docker/systemctl/ssh 等工具 |
| high-privilege-tools | shell | docker, ssh, systemctl, nginx 均为高权限工具 |
| many-tools | shell | 声明工具数 ≥ 5 (docker, journalctl, nginx, ssh, systemctl) |
| file-writes | file_write | 脚本有 file_io（写出JSON结果） |
| script-file-io | script_risk | `host_probe.py` 导入 pathlib, json |
| script-subprocess | script_risk | `host_probe.py` 导入 subprocess |

**维度得分**: shell=1.00, file_write=0.40, script_risk=1.00

**脚本实际行为分析**:

`host_probe.py` 是一个**系统信息只读采集器**：

- 执行的命令全部是查询类：`cat /etc/os-release`, `uname -a`, `hostname`, `nproc`, `df -hP`, `ss -ltn`, `command -v <tool>`
- 唯一写操作是将JSON结果输出到文件（`Path(args.output).write_text()`）
- 不修改任何系统状态、不安装任何软件、不创建任何服务

**但存在真实风险点**:

1. **`shell=True` + 字符串拼接**: `subprocess.run(actual, shell=True, ...)` — 如果 `ssh_target` 来自不可信输入，存在命令注入风险（虽然使用了 `shlex.quote`）
2. **`sudo -n true` 检测**: 脚本会尝试执行 `sudo -n true` 来检测免密sudo权限 — 这本身不危险，但暴露了权限信息
3. **SSH远程执行**: 支持 `--ssh user@server` 模式远程探测 — 相当于在目标主机执行任意 shell 命令

**结论**: 评分偏高但方向正确。脚本确实有subprocess，但全部是只读查询。`shell=True` 是真实风险点，不过使用了 `shlex.quote` 缓解。合理等级应为 ALLOW_WITH_ASK。

---

### 3.3 🔶 deployment-verifier — SANDBOX_REQUIRED (score=0.40)

**触发的风险指标 (5个)**:

| 指标 | 维度 | 原因 |
|---|---|---|
| shell-execution | shell | SKILL.md 声明了 curl, docker, journalctl, jq |
| high-privilege-tools | shell | docker 为高权限工具 |
| file-writes | file_write | 脚本写出JSON结果 |
| script-file-io | script_risk | `verify_http.py` 导入 pathlib, json |
| script-network | script_risk | `verify_http.py` 导入 urllib |

**维度得分**: shell=1.00, file_write=0.40, script_risk=0.90

**脚本实际行为分析**:

`verify_http.py` 是一个纯HTTP smoke test工具：

- 使用 `urllib.request.urlopen()` 发送 GET/HEAD 请求
- 检查返回状态码和响应内容
- 写出JSON结果文件
- **无subprocess，无文件系统修改，无shell调用**

**风险来源拆解**:

脚本本身的真实风险很低（只是HTTP检查器）。0.40的分数主要来自SKILL.md文本中声明的 `curl`, `docker`, `journalctl`, `jq` — 这些工具是**Agent在执行skill时可能调用的CLI工具**，不是脚本自身的行为。当前引擎对"SKILL.md文本声明"和"脚本AST分析"结果同等信任，导致分数虚高。

**结论**: 评分偏高。脚本行为仅是HTTP GET，真实风险远低于shell=1.00所暗示的程度。合理等级应为 ALLOW_WITH_ASK。

---

### 3.4 ⚠️ deployment-executor — ALLOW_WITH_ASK (score=0.25)

**触发的风险指标**: shell-execution, high-privilege-tools, many-tools

**声明工具**: docker, git, helm, rsync, ssh, systemctl (6个)

**脚本**: **无** — 这个skill没有任何捆绑脚本。

**分析**: 所有风险信号100%来自SKILL.md文本中提到的工具名。skill本身是一份指导Agent如何执行部署的指令文档，不包含任何可执行代码。真实风险取决于Agent运行时是否实际调用这些工具，而非文档中是否提到了它们。

**结论**: 评分方向正确，但信号来源单一（仅文本声明）。当前等级 ALLOW_WITH_ASK 合理。

---

### 3.5 ⚠️ incident-rollback — ALLOW_WITH_ASK (score=0.25)

**触发的风险指标**: shell-execution, high-privilege-tools, many-tools

**声明工具**: curl, docker, journalctl, ssh, systemctl (5个)

**脚本**: **无**

**分析**: 与 deployment-executor 情况相同。纯指令文档，无可执行脚本。所有风险信号来自文本声明。

**结论**: 等级 ALLOW_WITH_ASK 合理。

---

### 3.6 ⚠️ repo-service-lifecycle — ALLOW_WITH_ASK (score=0.25)

**触发的风险指标**: shell-execution, high-privilege-tools, many-tools

**声明工具**: curl, docker, git, helm, jq, kubectl, rsync, ssh, systemctl (9个 — 全场最多)

**脚本**: **无**

**分析**: 工具声明最多的skill，但同样没有任何脚本。作为端到端部署编排的指令文档，声明大量工具符合预期。当前 ALLOW_WITH_ASK (0.25) 与 deployment-executor 相同，但其声明了9个工具而后者仅6个 — 这说明 `many-tools` 指标的区分度不足，≥5 个工具一律给同样的 0.2 分，无法区分"刚过线"和"远超线"。

**结论**: 等级合理，但评分精度不足。

---

### 3.7 ⚠️ repo-runtime-discovery — ALLOW_WITH_ASK (score=0.34)

**触发的风险指标**: shell-execution, high-privilege-tools, file-writes, script-file-io

**声明工具**: docker, git, helm (3个)

**脚本**: `scripts/repo_inventory.py` — 导入 pathlib, json, re, tomllib, argparse。**无subprocess，无网络，无os操作**。

**分析**: 脚本完全安全（只读取本地文件解析 pyproject.toml 等配置文件），但因为SKILL.md提到了 docker/helm，shell 维度被拉到1.00。0.34的分数是 shell(1.0×0.25) + file_write(0.4×0.15) + script_risk(0.3×0.10) 的加权结果。

**结论**: 脚本本身无风险，分数主要由文本声明驱动。当前等级偏高。

---

### 3.8 ⚠️ service-operations — ALLOW_WITH_ASK (score=0.34)

**触发的风险指标**: shell-execution, high-privilege-tools, file-writes, script-file-io

**声明工具**: curl, docker, journalctl, systemctl (4个)

**脚本**: `scripts/release_state.py` — 导入 argparse, datetime, json, pathlib。**纯JSON读写，无subprocess，无网络，无os操作**。

**分析**: 与 repo-runtime-discovery 情况一致。脚本完全安全，分数由SKILL.md文本声明驱动。

**结论**: 等级偏高。

---

### 3.9 ⚠️ ppt-writer — ALLOW_WITH_ASK (score=0.24)

**触发的风险指标**: shell-execution, file-writes, script-file-io

**声明工具**: node (1个，从SKILL.md文本匹配)

**脚本**:

| 脚本 | imports | subprocess | os_ops | network | file_io |
|---|---|---|---|---|---|
| `build_deck.py` | pptx, json, pathlib, re | ❌ | ❌ | ❌ | ✅ |
| `qa_deck.py` | zipfile, xml, json, pathlib | ❌ | ❌ | ❌ | ✅ |

**分析**: 两个脚本都是纯文件处理（生成PPTX、解析ZIP/XML），没有任何subprocess或网络行为。`shell_execution=True` 是因为 SKILL.md 文本中提到了 `node`（被 `_extract_tools` 从正文匹配到）。

**结论**: 等级偏高。脚本行为非常安全，node 声明来自文本中对 PptxGenJS 工具链的提及，并非脚本实际调用。

---

## 4. 引擎缺陷分析

### 4.1 P0 — `OS_IMPORT_MARKERS` 粒度过粗（误判根因）

**现状**: `OS_IMPORT_MARKERS = {"os", "shutil", "tempfile", "signal"}`。只要脚本 `import shutil`，就标记 `has_os_operations=True`。

**问题**: `shutil.which()` 是只读PATH查询，`tempfile.TemporaryDirectory()` 是系统管理的临时目录。它们与 `shutil.rmtree()`, `os.remove()`, `os.system()` 的风险等级完全不同。

**影响**: ppt-reader 被误判为 DENY。

**建议**: 将 os 操作检测从"模块级"细化到"函数级"。具体做法：

```python
# 当前（粗粒度）
has_os_operations = bool(top_level_names & OS_IMPORT_MARKERS)

# 建议（函数级）
SAFE_OS_USAGE = {
    "shutil": {"which", "get_terminal_size"},
    "tempfile": {"TemporaryDirectory", "NamedTemporaryFile", "mkdtemp", "gettempdir"},
    "os": {"path", "getcwd", "getenv", "environ", "sep", "linesep"},
}
DANGEROUS_OS_USAGE = {
    "shutil": {"rmtree", "copytree", "move", "copy2"},
    "os": {"system", "popen", "exec", "execvp", "remove", "unlink", "rename", "chmod"},
}
```

通过AST遍历 `ast.Attribute` 节点，检查实际调用的函数名而非仅检查 import 的模块名。

---

### 4.2 P1 — "声明工具"与"脚本行为"权重未分离

**现状**: 引擎对两类信号同等对待：

- **声明信号**: 从SKILL.md文本中正则匹配到的工具名（如文档提到 `docker`）
- **行为信号**: 从脚本AST中分析出的实际调用（如脚本执行了 `subprocess.run(["docker", ...])`)

**问题**: 6个 ALLOW_WITH_ASK skill 中，有 4 个的分数完全由声明信号驱动，脚本本身无风险或不存在脚本。deployment-executor、incident-rollback、repo-service-lifecycle **没有任何脚本**，它们的 shell 维度却得了满分 1.00。

**影响**: 文档类skill（只有指令，无可执行代码）的风险被高估。

**建议**: 引入信号来源权重：

```
declared_tools 来自 SKILL.md 文本 → 声明权重 = 0.4
script AST 分析出的实际行为      → 行为权重 = 1.0
```

即：仅由文本声明驱动的 shell 维度分数应打折。如果一个skill声明了 docker 但没有任何脚本调用 docker，实际风险远低于有脚本直接 `subprocess.run(["docker", ...])` 的skill。

---

### 4.3 P2 — 只读 subprocess 与读写 subprocess 未区分

**现状**: 脚本中只要 `import subprocess`，就标记 `has_subprocess=True`，所有subprocess一视同仁。

**问题**: `target-host-readiness` 的 `host_probe.py` 执行的全部是只读查询命令（`uname -a`, `cat /proc/meminfo`, `hostname -I`, `ss -ltn`），不修改系统状态。但引擎将其与"下载并执行远程脚本"的subprocess视为同等风险。

**建议**: 对subprocess调用做命令分类：

```python
READONLY_COMMANDS = {"cat", "grep", "uname", "hostname", "nproc", "df", "ss", "whoami",
                     "command", "test", "id", "uptime", "free", "lsb_release", "arch"}
WRITE_COMMANDS = {"rm", "mv", "cp", "chmod", "chown", "kill", "systemctl start",
                  "docker run", "apt install", "yum install"}
```

如果脚本中所有subprocess调用的目标命令都属于 `READONLY_COMMANDS`，降低 `script_risk` 维度得分。

实现方式：在AST分析中，查找 `subprocess.run([...])` 或 `subprocess.run("...")` 的参数列表，提取第一个元素作为命令名。

---

### 4.4 P3 — `many-tools` 指标区分度不足

**现状**: `len(m.declared_tools) >= 5` → 触发，给 0.2 分。

**问题**: 声明5个工具和声明9个工具得到相同分数。repo-service-lifecycle（9个工具）与 deployment-executor（6个工具）的 shell 维度得分完全相同（均为 1.00）。

**建议**: 改为分级或连续评分：

```python
# 分级方案
RiskIndicator("many-tools-tier1", "shell", 0.1, lambda m: 3 <= len(m.declared_tools) < 6),
RiskIndicator("many-tools-tier2", "shell", 0.2, lambda m: 6 <= len(m.declared_tools) < 10),
RiskIndicator("many-tools-tier3", "shell", 0.4, lambda m: len(m.declared_tools) >= 10),

# 或连续方案
score = min(1.0, len(m.declared_tools) * 0.05)
```

---

### 4.5 P3 — `shell_execution` 判定条件过宽

**现状** (parser.py 第173-177行):

```python
shell_execution = (
    len(declared_tools) > 0
    or any(s.has_subprocess for s in scripts)
    or _has_shell_indicators(body)
)
```

**问题**: 只要SKILL.md中提到了**任何一个** CLI工具（包括 `git`、`jq`、`node`），就标记 `shell_execution=True`。这意味着几乎所有提到工具名的skill都会触发 shell-execution 指标。

ppt-writer 的 `shell_execution=True` 仅因为文本提到了 `node`（用于描述PptxGenJS工具链），但脚本中完全没有shell调用。

**建议**: 区分"工具声明"和"shell执行"：

```python
# declared_tools > 0 不应直接等同于 shell_execution
# 应该仅在以下情况标记 shell_execution=True:
shell_execution = (
    any(s.has_subprocess for s in scripts)
    or _has_shell_indicators(body)
    or len(high_privilege_tools) > 0   # 只有高权限工具才等同于shell执行
)
```

---

## 5. Skill 侧改进建议

以下建议不需要修改引擎，仅通过调整skill自身即可降低风险评分。

### 5.1 ppt-reader — 拆分 render_slides.py

将 `render_slides.py` 拆为两个脚本：

1. `check_render_deps.py` — 仅调用 `shutil.which("soffice")` 和 `shutil.which("pdftoppm")` 检查依赖
2. `render_slides.py` — 仅保留 subprocess 调用，移除 shutil/tempfile 导入（改用 `pathlib.Path` + `os.makedirs`）

拆分后任何一个脚本都不会同时命中 subprocess + os_operations 红线。

### 5.2 target-host-readiness — 声明 approval_required

在 SKILL.md frontmatter 中添加：

```yaml
approval_required: true
```

这会避免触发 `sudo-without-approval` 红线（虽然当前未触发，但 `host_probe.py` 中确实执行了 `sudo -n true`），并向引擎传达"该skill已考虑到权限问题"的信号。

### 5.3 target-host-readiness — 消除 shell=True

`host_probe.py` 中 `subprocess.run(actual, shell=True, ...)` 是真实风险点。建议改为列表调用：

```python
# 当前（存在注入面）
proc = subprocess.run(actual, shell=True, text=True, capture_output=True)

# 建议（消除注入面）
if ssh_target:
    cmd_list = ["ssh", ssh_target, cmd]
else:
    cmd_list = ["sh", "-c", cmd]
proc = subprocess.run(cmd_list, text=True, capture_output=True)
```

### 5.4 运维类 skill — 声明工具分层

建议在SKILL.md中区分必需工具和可选工具：

```markdown
## Required Tools
- `git` — 版本管理

## Optional Tools (场景相关)
- `docker` — 仅容器化部署时需要
- `kubectl` — 仅k8s环境时需要
```

当前引擎无法利用这个信息，但为未来引擎支持 `required_tools` / `optional_tools` 分层评估做准备。

值得注意的是，repo-service-lifecycle 的 SKILL.md frontmatter 中**已经采用了这种分层**：

```
compatibility: ... Typical tools: git, ssh, rsync, curl, jq ... Optional: docker, docker compose, systemctl, kubectl, helm.
```

这说明 skill 作者已经意识到工具优先级的区别，只是引擎尚未解析和利用 `Typical` / `Optional` / `Helpful` / `Common` 这些前缀词。

---

## 6. 改进优先级汇总

| 优先级 | 类型 | 改进项 | 影响范围 | 预期效果 |
|---|---|---|---|---|
| **P0** | 引擎 | `OS_IMPORT_MARKERS` 细化到函数级 | ppt-reader | DENY → ALLOW_WITH_ASK |
| **P1** | 引擎 | 声明信号 vs 行为信号分权重 | 全部9个高风险skill | 平均降分0.05-0.15 |
| **P2** | 引擎 | 只读subprocess降分 | target-host-readiness | SANDBOX → ALLOW_WITH_ASK |
| **P3** | 引擎 | `many-tools` 分级评分 | 工具数≥5的skill | 提升区分度 |
| **P3** | 引擎 | `shell_execution` 判定条件收窄 | ppt-writer 等4个skill | 消除文本声明驱动的虚高 |
| **P1** | Skill | ppt-reader 拆分脚本 | ppt-reader | 绕过红线，立即生效 |
| **P2** | Skill | target-host-readiness 声明 approval_required | target-host-readiness | 防御性改善 |
| **P2** | Skill | target-host-readiness 消除 shell=True | target-host-readiness | 消除真实注入风险 |
| **P3** | Skill | 运维类skill工具声明分层 | 6个运维skill | 为未来引擎升级做准备 |

---

## 7. 扫描结果可信度评估

| 评估维度 | 评价 |
|---|---|
| ✅ 零风险skill识别准确 | 18个纯内容skill全部正确判定为 ALLOW |
| ✅ 风险方向正确 | 运维/部署类skill确实比内容类skill风险更高 |
| ✅ 红线规则设计合理 | subprocess+network combo 和 sudo-without-approval 抓住了真实高危模式 |
| ⚠️ 一个误判（ppt-reader） | shutil.which 被等同于 os 危险操作，导致误触红线 |
| ⚠️ 声明信号权重过高 | 4个无脚本skill因文本声明被标为 ALLOW_WITH_ASK |
| ⚠️ 只读行为未区分 | target-host-readiness 的只读探测被视为与写操作同等风险 |

**整体评价**: 引擎在**方向判断**上表现良好（哪些skill更危险的排序基本正确），但在**绝对分数**和**阈值判定**上存在虚高问题。主要原因是信号粒度不足——模块级 vs 函数级、声明 vs 行为、只读 vs 读写的区分尚未实现。
