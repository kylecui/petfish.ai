# PEtFiSh 贡献指南 (Contributing to PEtFiSh)

了解如何为 PEtFiSh 项目贡献技能 (skills)、技能包 (packs) 以及其他改进。

---

## 开发环境设置 (Development Setup)

### 前置依赖

- **Git** — 用于版本控制
- **uv** — Python 环境管理器（所有 Python 脚本必用）
- **Python 3.11+** — 用于 skill 脚本和 MCP 服务器

### 克隆与分支

```bash
git clone https://github.com/kylecui/petfish.ai.git
cd petfish.ai
git checkout dev
```

所有的开发都在 `dev` 分支上进行。永远不要直接向 `master` 提交代码。

---

## 分支策略 (Branching Strategy)

```text
master ← dev ← feature branches (功能分支)
  │
  └── 每一次向 master 的合并 = 一次 GitHub 发布 (vX.Y.Z)
```

- **`dev`**：活跃的开发分支
- **`master`**：稳定的发布分支 — 每次合并都会打上发布标签 (release tag)
- **功能分支 (Feature branches)**：从 `dev` 分支切出，提交 PR 返回到 `dev`

### 版本号 (Version Numbers)

| 变更类型 | 版本提升 | 示例 |
|---|---|---|
| 破坏性变更 (Breaking changes) | 主版本号 (Major, X) | Pack 结构变更，安装器 API 变更 |
| 新功能 | 次版本号 (Minor, Y) | 新的 pack，新的 skill，新的平台支持 |
| Bug 修复 | 修订号 (Patch, Z) | 修复问题，文档修正，微小优化 |

---

## 添加新的 Skill

1. 在合适的 pack 下创建 skill 目录
2. 编写带有正确前置元数据 (frontmatter) 的 `SKILL.md`
3. 根据需要添加脚本 (scripts)、参考文件 (references) 和模式 (schemas)
4. 添加触发器评估 (trigger evaluation) 测试
5. 运行质量门禁：`/petfish gate path/to/skill/`
6. 修复所有的 FAIL（失败）或 CONDITIONAL（有条件通过）问题

详细的指令请参见 [Skill 创作指南 (Skill Authoring Guide)](skill-authoring.md)。

---

## 添加新的 Pack

引入一个新的 pack 需要更新 **9 个触点 (touchpoints)**。遗漏任何一项都会导致用户的静默安装失败。

### 9 触点检查清单 (The 9-Touchpoint Checklist)

| 序号 | 触点 | 文件 | 处理方法 |
|---|---|---|---|
| 1 | 统一安装器别名 | `install.py` | 在 `ALIASES` 映射表中注册 pack 的别名 |
| 2 | 本地安装器别名 | `install.ps1`, `install.sh` | 在本地 pack 映射表中注册别名（遗留） |
| 3 | Companion 目录 | `catalog_query.py` PROFILES 字典 | 添加到相关的配置文件 (至少包括 `comprehensive`) |
| 4 | 项目初始化器 | `project-initializer/SKILL.md` + `init_project.py` | 关联到具体的配置或添加新配置 |
| 5 | README | `README.md` | 更新 Pack 列表和 Profile → Auto-Install 映射表 |
| 6 | 网站 | `website/index.html`, `pitch.html`, `blog.html` | 更新 pack 卡片、表格、数量统计 |
| 7 | 安装/升级文档 | `docs/agent-install.md`, `docs/agent-upgrade.md` | 更新示例以及 pack 列表 |
| 8 | 中文翻译 | `docs/zh/README.md` | 同步中文版本 |
| 9 | 归档文档 | `docs/archive/` | 更新 pack 数量统计和列表 |

!!! danger "统一 Python 安装器 vs 遗留 Shell 安装器"
    **统一 Python 安装器**（`install.py`，首选）：使用 PEP 723 内联元数据，通过 `uv run` 自动引导，内置镜像回退，并通过 petfish-market 动态解析可选 pack。新 pack 必须在 `ALIASES` 字典中注册别名。

    **遗留 Shell 安装器**（`install.ps1`, `install.sh`）：动态扫描 `packs/` 目录 — 新的 packs 会被自动发现，但别名仍需注册。保留用于向后兼容。

    **遗留远程安装器**（`remote-install.ps1`, `remote-install.sh`）：使用**硬编码的静态数组**。如果不手动添加 pack 名称，`--pack all` 将会静默跳过它。可选包通过 petfish-market 解析，但核心包名仍需在数组中。

    请务必测试统一安装器路径。遗留安装器仅用于向后兼容。

### 验证

添加新 pack 之后：

1. 在所有 9 个触点文件中搜索该 pack 的名称
2. 使用本地和远程安装器分别测试 `--pack all`
3. 验证 `/petfish catalog` 会列出新的 pack
4. 验证 `/initproject` 配置选择中包含该 pack

---

## 4 个安装器 (The 4 Installers)

PEtFiSh 拥有 5 个安装器脚本。统一 Python 安装器（`install.py`）是首选；Shell 脚本为遗留兼容。

| 脚本 | 类型 | 架构 | 状态 |
|---|---|---|---|
| `install.py` | 统一, Python (PEP 723) | 动态别名 + 市场解析 | **首选** |
| `install.ps1` | 本地 (Local), PowerShell | 动态扫描 `packs/` | 遗留 |
| `install.sh` | 本地 (Local), Shell | 动态扫描 `packs/` | 遗留 |
| `remote-install.ps1` | 远程 (Remote), PowerShell | 静态数组 (Static array) | 遗留 |
| `remote-install.sh` | 远程 (Remote), Shell | 静态数组 (Static array) | 遗留 |

任何逻辑上的变更都必须在所有脚本中进行评估。优先级：先确保 `install.py` 正确，再同步到遗留脚本。

---

## 测试 (Testing)

### 冒烟测试 (Smoke Tests)

Pack 级别的冒烟测试位于每个 pack 的 `tests/` 目录中：

```bash
uv run pytest packs/my-pack/tests/ -v
```

### 触发评估 (Trigger Evaluation)

测试 skill 触发的准确率：

```bash
uv run python .opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py \
  --path packs/my-pack/.opencode/skills/my-skill/evals/trigger/my-skill.json
```

### 质量门禁 (Quality Gate)

在提交任何 PR 之前，请运行完整的发布门禁：

```bash
uv run python .opencode/skills/quality-gate/scripts/run_gate.py \
  --path packs/my-pack/.opencode/skills/ --recursive
```

---

## 提交 PR (Pull Request Process)

1. 从 `dev` 分支切出新分支
2. 进行修改
3. 在受影响的 skills 上运行质量门禁
4. 运行冒烟测试（如适用）
5. 更新 CHANGELOG（如果该 pack 拥有对应的日志）
6. 向 `dev` 提交 PR
7. 在合并到 `dev` 且测试通过后，创建一个从 `dev` 合并到 `master` 的 PR
8. 合并到 `master` 后，**立即创建一个 GitHub 发布 (GitHub Release)**：

```bash
gh release create vX.Y.Z --target master \
  --title "vX.Y.Z - Brief description" \
  --notes "Changelog summary"
```

---

## 代码约定 (Code Conventions)

### Python

- 使用 `uv` 进行所有的虚拟环境管理 — 禁止使用 `pip install`
- 具有外部依赖的脚本必须使用 PEP 723 内联元数据 (inline metadata)
- MCP 服务器通过 `["uv", "run", "python", "server.py"]` 启动
- 仅限标准库的内联代码 (`python3 -c`) 可以在不使用 uv 的情况下运行

### SKILL.md

- 前置元数据的 `description` 必须覆盖 ≥80% 的主体触发关键词
- 包含中文和英文的触发短语
- 将描述控制在 500 个字符以内
- Schema 字段名必须与 SKILL.md 字段描述完全一致

### 命名 (Naming)

- 目录和文件：仅使用小写的短横线命名法 (`kebab-case`)
- Skill 名称必须与其目录名匹配
- 避免在名称中使用 `final`、`new`、`v2` 等词汇

### 脚本中的 Bash

在 bash 字符串中嵌入 Python 代码时 (`python3 -c "..."`)，请使用 `chr()` 而不是转义字面量：

```python
# 推荐 — 对 shell 转义层免疫
sep = chr(47)  # 正斜杠 (forward slash)
bs = chr(92)   # 反斜杠 (backslash)

# 不推荐 — 在 SSH、PowerShell 以及其他代理 shell 中会出错
sep = "/"
bs = "\\"
```

---

## 绝对禁止的事项 (What Not to Do)

- 不要直接向 `master` 分支提交代码
- 合并到 `master` 后绝不能忘记打发布标签 (release tag)
- 任何地方都不要使用 `pip install`
- 不要直接修改其他仓库的代码 — 请提交 issue 代替
- 不要删除已发布的 release（除非存在安全漏洞）
- 不要跳过在提 PR 之前的质量门禁检查