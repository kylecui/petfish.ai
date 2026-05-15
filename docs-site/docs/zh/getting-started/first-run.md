# 首次运行

[安装](installation.md)PEtFiSh并重启AI助手后，以下是你会遇到的情况。

## 1. 初始化项目

在AI助手中运行`/initproject`命令：

```
/initproject
```

向导会询问你的项目类型，并安装匹配的技能包。例如选择`code`会安装`deploy`、`petfish`和`testdocs`。

## 2. Companion Gateway已激活

你不需要做任何操作来启用它。Companion Gateway在每条消息前自动运行。它在后台完成以下工作：

1. **读取项目模式** — 检查`depth`（urgent/balanced/thorough）和`rigor`（on/off）设置
2. **检查话题上下文** — 检测你的消息是否偏离当前话题
3. **扫描失败信号** — 查找上一轮的错误
4. **感知能力缺口** — 如果你的请求需要未安装的技能，主动推荐
5. **反迎合检查** — 面对评价性问题时先暂停，不急于附和

Gateway只在有有用信息时才输出（中/高风险或有推荐）。要查看每次决策过程，启用[调试模式](../guides/companion-gateway/index.md#debug-mode)。

## 3. 试试`/petfish`

`/petfish`命令是你的主要入口：

| 命令 | 作用 |
|---|---|
| `/petfish` | 显示已安装的包和技能状态 |
| `/petfish catalog` | 浏览所有可用的包和技能 |
| `/petfish suggest` | 根据项目特征推荐技能包 |
| `/petfish search <关键词>` | 跨外部市场搜索技能 |

## 4. 正常工作

直接像平常一样工作。PEtFiSh在后台运作：

- 如果你提到"部署"但没有`deploy`包 → PEtFiSh会推荐安装
- 如果你问"这个架构设计合理吗？" → 反迎合检查会在agent附和前介入
- 如果上一轮读取PDF失败 → PEtFiSh建议安装`ppt`包
- 如果你在对话中切换话题 → PEtFiSh标记上下文漂移

## 5. 可选：配置项目模式

创建`.opencode/project-mode.yaml`来调整PEtFiSh的行为：

```yaml
depth: balanced       # urgent | balanced | thorough
rigor: false          # true | false
```

- **`depth: urgent`** — 快速修复，允许临时方案，最少搜索
- **`depth: balanced`** — 正常工作流（默认）
- **`depth: thorough`** — 根因分析，多源交叉验证，自动启用`rigor: true`
- **`rigor: true`** — 复杂任务需要正式计划，实施前须通过审查

你也可以在会话中直接说"紧急"、"仔细"或"严谨"来切换模式，无需修改文件。

## 接下来

- [Companion Gateway指南](../guides/companion-gateway/index.md) — 深入了解Gateway的每个步骤
- [/petfish命令参考](../guides/petfish-commands/index.md) — 完整命令参考
- [技能包参考](../reference/packs/index.md) — 浏览全部12个包和96个技能
