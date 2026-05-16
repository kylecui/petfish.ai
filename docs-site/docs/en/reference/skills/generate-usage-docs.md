# generate-usage-docs

> Pack: **testdocs**

Generate grounded usage docs from the current repo: README, Quick Start, configuration, usage, API/CLI/SDK docs, troubleshooting, FAQ, deployment/operator guides, or to整理零散设计说明 into user-facing doc sets. Trigger for 根据代码与设计文档生成交付级文档；not for generic polishing/translation.

**Compatibility:** Designed for OpenCode and Agent Skills compatible clients. Prefer Python 3.11+ and uv for running bundled scripts.

---

# Generate Usage Docs

用这项技能时，你的目标是根据**当前项目的真实设计与代码**生成“给人用”的文档，而不是只把源码结构改写一遍。

## 何时使用

当用户提出以下意图时加载本技能：

-根据当前项目生成使用文档
-补README、Quick Start、配置说明、FAQ、排障文档
-根据API/CLI/SDK /配置文件生成文档
-根据代码和设计文档生成交付级使用说明
-把零散的设计说明整理成用户导向文档

若用户只是要润色一段文字、翻译文档或写纯创作型内容，不必强制加载本技能。

## 默认方法

先识别**读者与场景**，再识别**项目对外能力**，最后输出**文档集**。  
不要直接堆API细节或源码清单。

### Step 1：盘点项目事实

优先读取以下内容：

1. README、docs、设计说明、部署说明
2. OpenAPI/proto/route/controller
3. CLI帮助、命令入口、子命令
4. package manifest、构建文件、安装方式
5. 配置文件、环境变量、示例配置
6. 示例代码、测试、样例数据
7. 常见报错、日志、故障处理线索

需要快速盘点时，先运行：

```bash
uv run scripts/project_inventory.py .
```

### Step 2：识别文档受众

先判断主要读者是谁：

- end user
- operator
- developer
- integrator
- internal team
- evaluator/reviewer

没有明确受众时，默认按“**首次接触该项目的技术使用者**”写。

### Step 3：识别项目的对外能力

至少梳理这些问题：

-它是什么
-适合什么场景
-如何安装/启动/调用
-需要哪些配置
-核心工作流是什么
-用户最可能从哪里开始
-失败时如何排障
-有哪些限制、注意事项或风险

### Step 4：构建doc set

按需从以下文档集中选择：

- README.md
- docs/quickstart.md
- docs/configuration.md
- docs/usage.md
- docs/api.md
- docs/cli.md
- docs/troubleshooting.md
- docs/faq.md
- docs/deployment.md

优先生成**最少但完整**的文档集，不要把所有文档都一股脑写满。

*... (79 more lines in full SKILL.md)*
