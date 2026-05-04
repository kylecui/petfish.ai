

## 一、重新定义目标

新的目标是：

1. **开发Skills**

   * 从GitHub高星仓库、官方Skills示例、已有工程经验中抽取可复用工作流。
   * 输出符合OpenCode目录规范的Skills。

2. **治理Skills**

   * 检查Skill是否安全、可维护、可组合、可评估。
   * 避免恶意脚本、过宽权限、工具滥用、提示词注入和secret泄露。

3. **评估Skills**

   * 测试Skill是否能正确触发。
   * 测试Skill是否真正改善Agent输出质量。
   * 测试Skill是否引入额外风险或过高上下文成本。

4. **运营Skills仓库**

   * 建立Skill注册表、版本管理、依赖关系、兼容性说明和发布流程。
   * 支持项目级Skills与全局Skills两种部署方式。

OpenCode的Skill本质上就是通过`SKILL.md`定义可复用行为，并可放在`.opencode/skills/<name>/SKILL.md`或全局`~/.config/opencode/skills/<name>/SKILL.md`等路径下被发现。同时，AgentSkills规范也明确了Skill目录至少包含`SKILL.md`，可选包含`scripts/`、`references/`、`assets/`等内容。

---

## 二、SkillsTeam的工作域

新的Skill开发计划应分成六个工作域。

| 工作域             | 目标             | 代表Skills                                                                    |
| --------------- | -------------- | --------------------------------------------------------------------------- |
| SkillAuthoring  | 生成和改写Skills    | `skill-author`、`skill-refactor`、`skill-description-optimizer`               |
| SkillSecurity   | 审查Skill安全性     | `skill-security-auditor`、`mcp-risk-reviewer`、`script-safety-checker`        |
| SkillEvaluation | 测试触发率和输出质量     | `skill-trigger-evaluator`、`skill-output-evaluator`、`skill-benchmark-runner` |
| SkillMining     | 从开源项目中抽取Skills | `repo-skill-miner`、`awesome-list-analyzer`、`workflow-extractor`             |
| SkillPackaging  | 打包、发布、安装、升级    | `skill-packager`、`skill-installer`、`skill-registry-manager`                 |
| SkillOps        | 维护Skills生命周期   | `skill-version-manager`、`skill-dependency-mapper`、`skill-quality-gate`      |

这样，我们就不再把LangChain、LangGraph、Qdrant、Ollama这些项目理解为“课程内容”，而是理解为：

> 它们是Skill开发素材库、工作流样本库、工具能力来源和安全评估对象。

---

## 三、核心Skills清单

### 1. `skill-author`

用途：根据用户需求生成新的OpenCodeSkill。

输入：

```text
- 用户目标
- 适用场景
- 需要调用的工具
- 输入/输出格式
- 风险约束
- 参考项目或参考文档
```

输出：

```text
skill-name/
  SKILL.md
  references/
  scripts/
  assets/
  evals/
```

职责：

* 生成合法frontmatter。
* 控制`description`长度和触发边界。
* 将核心流程写入`SKILL.md`。
* 将长文档拆到`references/`。
* 将可复用自动化逻辑放入`scripts/`。
* 自动生成最小eval样例。

这是SkillsTeam的第一核心Skill。

---

### 2. `repo-skill-miner`

用途：阅读一个GitHub仓库，判断它能否沉淀为Skill。

它不负责“解释这个仓库怎么教学”，而是回答：

```text
这个仓库中是否存在可复用工作流？
这个工作流是否适合Agent执行？
是否需要脚本支持？
是否有明确输入/输出？
是否有安全边界？
是否值得做成Skill？
```

输出格式：

```markdown
# Repo Skill Mining Report

## Repository
## Candidate Skills
## Reusable Workflows
## Required Tools
## Security Risks
## Suggested Skill Boundaries
## Not Suitable for Skillization
## Priority
```

文档中提到的awesome-llm-apps、LangChain、LangGraph、CrewAI、Ollama、awesome-mcp-servers、Qdrant、system-design-primer、awesome-claude-code等项目，都应首先进入这个Skill的分析流程。原分析文档也明确把这些仓库划分为AI应用、Agent、MCP、RAG、系统设计、本地模型与AI辅助开发等不同价值域。

---

### 3. `skill-security-auditor`

用途：审查一个Skill是否安全。

检查对象：

```text
SKILL.md
scripts/
references/
assets/
opencode.json
MCP配置
外部下载命令
文件系统访问范围
网络访问行为
```

重点检查：

```text
[ ] 是否请求过宽文件权限
[ ] 是否读取.env、ssh key、token、浏览器profile
[ ] 是否自动上传项目代码或文档
[ ] 是否存在curl | bash、远程执行、动态eval
[ ] 是否存在rm -rf、覆盖写、递归删除等危险操作
[ ] 是否默认修改用户系统
[ ] 是否缺少dry-run
[ ] 是否缺少人工确认
[ ] 是否把MCP工具权限交给Agent无限调用
[ ] 是否可能被prompt injection驱动执行高危动作
```

这个Skill是整个SkillsTeam的安全门禁。

---

### 4. `skill-description-optimizer`

用途：优化`description`，让Skill该触发时触发，不该触发时不触发。

AgentSkills文档强调，Skill是否被激活主要依赖`description`字段；描述太窄会漏触发，太宽会误触发，因此需要专门评估和优化。

输入：

```text
- 当前description
- Skill能力范围
- 应触发样例
- 不应触发样例
- 相邻Skills列表
```

输出：

```text
- 新description
- 触发边界说明
- 正例/反例测试集
```

---

### 5. `skill-trigger-evaluator`

用途：测试Skill是否能被正确触发。

评估方法：

```text
每个Skill准备约20条query：
- 8-10条should_trigger
- 8-10条should_not_trigger
```

输出：

```json
{
  "skill": "skill-author",
  "trigger_pass_rate": 0.85,
  "false_positive_rate": 0.10,
  "false_negative_rate": 0.15,
  "failed_cases": []
}
```

---

### 6. `skill-output-evaluator`

用途：测试Skill是否真的提升输出质量。

AgentSkills评估文档建议将每个测试分为withskill和withoutskill，比较通过率、耗时、token成本和输出质量。

输出：

```json
{
  "skill": "repo-skill-miner",
  "with_skill_pass_rate": 0.82,
  "without_skill_pass_rate": 0.46,
  "quality_delta": 0.36,
  "token_delta": 1200,
  "recommendation": "keep"
}
```

---

### 7. `skill-packager`

用途：将一组Skills整理成可发布包。

输出：

```text
skills-pack/
  .opencode/
    skills/
  AGENTS.md
  opencode.json
  skills-registry.yaml
  README.md
  CHANGELOG.md
  LICENSE
  install.sh
  install.ps1
```

---

### 8. `skill-registry-manager`

用途：维护Skill清单、版本、依赖和状态。

`skills-registry.yaml`示例：

```yaml
skills:
  - name: skill-author
    version: 0.1.0
    status: stable
    category: authoring
    depends_on: []
    security_level: medium
    owner: skills-team

  - name: skill-security-auditor
    version: 0.1.0
    status: stable
    category: security
    depends_on: []
    security_level: high
    owner: skills-team
```

---

## 四、开源项目如何进入SkillsTeam流程

| 开源项目                    | 对SkillsTeam的价值                        |
| ----------------------- | ------------------------------------- |
| awesome-llm-apps        | 候选工作流池，用于挖掘RAG、Agent、多模态、MCP类Skills   |
| LangChain               | 工具调用、RAG、链式应用的Skill素材                 |
| LangGraph               | 可控Agent、状态机、HITL、恢复机制的Skill素材         |
| CrewAI                  | 多Agent角色分工Skill素材                     |
| Ollama                  | 本地模型运行、本地评估、本地隐私实验Skill素材             |
| awesome-mcp-servers     | MCP工具接入与安全审查Skill素材                   |
| Qdrant                  | 向量库、RAG、payload过滤、检索评估Skill素材         |
| AI-Agents-for-Beginners | Agent概念拆解与基础工作流Skill素材                |
| system-design-primer    | 生产级系统设计审查Skill素材                      |
| awesome-claude-code     | Skills、hooks、commands、subagents组织方式参考 |

尤其是awesome-claude-code和Anthropic官方Skills示例，不应该被当成课程内容，而应当作为我们设计`skill-author`、`skill-packager`、`skill-quality-gate`的参考材料。Anthropic官方仓库中有Creative&Design、Development&Technical、Enterprise&Communication、DocumentSkills等示例，可用于参考Skill组织方式。

---

## 五、实施方案

### Phase0：SkillsTeam工程仓库初始化

建立目录：

```text
skills-team/
  AGENTS.md
  README.md
  opencode.json
  skills-registry.yaml

  .opencode/
    skills/
      skill-author/
      repo-skill-miner/
      skill-security-auditor/
      skill-description-optimizer/
      skill-trigger-evaluator/
      skill-output-evaluator/
      skill-packager/
      skill-registry-manager/

  templates/
    skill-template/
    eval-template/
    registry-template/

  scripts/
    validate_skill.py
    package_skills.py
    scan_skill_security.py

  evals/
    trigger/
    output/
    security/

  references/
    opencode-skill-spec.md
    agent-skills-spec.md
    skill-security-model.md
```

---

### Phase1：先做SkillsTeam的“自举Skills”

第一批必须是这8个：

```text
skill-author
repo-skill-miner
skill-security-auditor
skill-description-optimizer
skill-trigger-evaluator
skill-output-evaluator
skill-packager
skill-registry-manager
```

原因很简单：它们让我们具备“开发Skills的Skills”。

---

### Phase2：用开源项目验证SkillMining流程

选5个仓库做样本：

```text
LangChain
LangGraph
Qdrant
awesome-mcp-servers
awesome-claude-code
```

每个仓库产出：

```text
1.repo-skill-mining-report.md
2.candidate-skills.yaml
3.security-risk-notes.md
4.是否进入下一阶段的决策
```

示例候选Skill：

```yaml
repo: LangGraph
candidate_skills:
  - name: langgraph-workflow-designer
    purpose: Design stateful, controllable agent workflows.
    priority: high
  - name: langgraph-human-approval-gate
    purpose: Add human-in-the-loop approval before dangerous actions.
    priority: high
```

---

### Phase3：开发领域型Skills

等自举Skills稳定后，再开发领域Skills，例如：

```text
langgraph-workflow-designer
langchain-rag-builder
qdrant-rag-index-manager
ollama-local-model-runner
mcp-server-integrator
mcp-security-reviewer
crewai-role-workflow-builder
system-design-reviewer
```

这些不是课程Skills，而是工程Skills。

---

### Phase4：建立质量门禁

每个Skill合并前必须通过：

```text
1.格式检查
2.安全检查
3.触发评估
4.输出评估
5.人工review
6.版本登记
```

最小门禁标准：

```text
[ ] name合法
[ ] description合法且不超过1024字符
[ ] SKILL.md不超过建议长度
[ ] references拆分合理
[ ] scripts非交互
[ ] scripts支持--help
[ ] 默认不破坏用户文件
[ ] 无secret读取
[ ] 无远程任意代码执行
[ ] 有trigger eval
[ ] 有output eval
[ ] registry已登记
```
