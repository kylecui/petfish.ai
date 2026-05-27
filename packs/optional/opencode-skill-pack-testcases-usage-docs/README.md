# OpenCode Skills Pack：测试用例生成 + 使用文档生成

本包提供两套可直接放入项目的OpenCode/Agent Skills兼容技能：

- `generate-test-cases`：根据当前项目的设计文档、接口定义、代码结构与现有实现，生成测试策略、测试矩阵、测试用例和自动化建议。
- `generate-usage-docs`：根据当前项目的设计文档、接口定义、代码结构与现有实现，生成README、Quick Start、配置说明、API/CLI用法、FAQ与排障文档。

## 目录

```text
.opencode/
  skills/
    generate-test-cases/
      SKILL.md
      scripts/
      references/
      assets/
      evals/
    generate-usage-docs/
      SKILL.md
      scripts/
      references/
      assets/
      evals/
```

## 放置方法

将本包中的 `.opencode/` 目录复制到你的项目根目录。同时把 `pyproject.toml` 和 `.python-version` 复制到项目根目录。

然后运行：

```bash
uv sync
```

OpenCode会从项目路径向上搜索 `.opencode/skills/<name>/SKILL.md`，并根据 `name` / `description` 决定何时加载技能。

内置脚本通过 `uv run` 调用，详见 `UV-USAGE.md`。

## 设计原则

1. `SKILL.md` 保持精简，只放核心步骤、判断逻辑和输出要求。
2. 更长的说明放到 `references/`，避免主技能过长。
3. 需要重复执行或格式校验的工作，用 `scripts/` 承载。
4. 使用 `evals/` 维护触发测试与输出质量测试，便于迭代。

## 建议使用方式

### 测试用例技能
让代理读取当前项目后，直接提出：
- “根据当前仓库生成test cases”
- “根据这个模块代码补全测试矩阵”
- “为API设计回归测试和负面测试”
- “根据当前设计文档生成验收测试点”

### 使用文档技能
让代理读取当前项目后，直接提出：
- “根据当前项目生成使用文档”
- “补一份README和quick start”
- “为这个CLI生成使用说明”
- “根据代码和配置生成部署与排障文档”

## 与你的项目目标的对应关系

本包面向“创建各种skills”的项目用途，强调：
-输出符合OpenCode使用的目录结构
- skill内容可继续扩展、复用和打包
-可参考官方和公开高星skill仓库的组织方式
-预留 `evals/` 便于后续做持续改进
