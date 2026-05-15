# Reflection Card Template

每次反思的最小记录单元，4个字段，不允许膨胀。

## 格式

```
trigger: [发生了什么，1行]
root_cause: [为什么发生，1-2行]
prevention_rule: [防止再犯的具体规则，1-2行]
scope: [file | project | universal]
```

## 字段编写指南

### trigger 字段

描述**可观察的事件**，而非内心感受。好的 trigger 读起来像 git commit message——简短、客观、可追溯。

| 质量 | 写法 |
|------|------|
| 差 | "出了问题" |
| 中 | "部署失败了" |
| 好 | "install.sh 第47行 rstrip 调用在 Ubuntu 22.04 原生 bash 下抛出 SyntaxError" |

### root_cause 字段

指向**机制或流程缺陷**，回答"哪个环节的什么机制坏了"。常见的 root cause 类别：

- **信息遗漏**：某处有约束/数据但执行时未检索到
- **假设未验证**：把推测当事实使用
- **心智模型偏差**：对系统行为的理解与实际不符
- **流程跳步**：省略了检查清单中的某个步骤
- **环境差异**：开发环境与生产环境的行为不一致

禁止使用的归因模板（这些都是伪根因）：
- ❌ "考虑不够周全"
- ❌ "遗漏了某些情况"
- ❌ "对X的了解不够深入"
- ❌ "时间紧张导致疏忽"

### prevention_rule 字段

可执行性自检清单——如果以下任一条回答为"否"，规则需要重写：

1. 一个新手读到这条规则，能否照着做？
2. 完成后能否客观验证是否做到了？
3. 规则中是否包含具体工具、命令或检查点？

### scope 字段

- `file`：仅与当前文件/模块相关的局部经验
- `project`：与本项目的约定、架构、工具链相关
- `universal`：可迁移到任何项目的通用经验

**保守原则**：初次记录时标 `project`，经过3+次跨项目验证后再升级为 `universal`。

## 示例库

### 示例1：Shell转义陷阱

```
trigger: install.sh中反斜杠转义在用户bash环境下被吞掉，PowerShell SSH测试未暴露
root_cause: Python代码嵌入bash双引号字符串时，反斜杠经过bash和Python两层解释；通过PowerShell SSH测试时，PowerShell额外的转义层掩盖了问题
prevention_rule: bash内嵌Python用chr()代替转义字面量；bash脚本必须在真实bash环境中测试，不通过代理shell
scope: universal
```

### 示例2：安装器集成遗漏

```
trigger: research pack在v0.9.0完成开发，直到v0.10.7才发现未接入远程安装器
root_cause: 本地安装器动态扫描packs/目录（自动可见），远程安装器使用硬编码静态数组（需手动添加），开发时只用本地安装器测试
prevention_rule: 新pack引入必须完成9触点检查清单；本地和远程安装器都要测试
scope: universal
```

### 示例3：Schema与文档字段名分裂

```
trigger: 用户按SKILL.md填写字段后schema校验失败
root_cause: schema中字段名为search_queries，SKILL.md中写成queries，两处独立维护未交叉校验
prevention_rule: 修改schema时同步检查SKILL.md；修改SKILL.md字段描述时同步检查schema
scope: project
```

### 示例4：并发编辑冲突

```
trigger: 两个subagent同时修改同一配置文件，后写入者覆盖前者的变更
root_cause: 并行delegation未考虑文件锁定，两个task对README.md的不同section做了独立编辑
prevention_rule: 并行delegation时列出每个task会修改的文件清单，确保无重叠；有重叠则改为串行
scope: universal
```

### 示例5：测试环境与生产环境差异

```
trigger: pytest在CI通过但用户本地执行报ImportError: cannot import name 'TypeAlias' from 'typing'
root_cause: CI使用Python 3.12，用户环境为Python 3.10；TypeAlias在3.10中需要从typing_extensions导入
prevention_rule: pyproject.toml的requires-python必须反映实际最低版本；CI矩阵必须覆盖声明的最低Python版本
scope: universal
```

## 质量评估棋盘

| 维度 | 不合格（0分） | 及格（1分） | 优秀（2分） |
|------|-------------|-----------|-----------|
| trigger | "出了问题" | "部署失败" | "deploy.sh L47 curl返回HTTP 403因为GitHub token过期" |
| root_cause | "不够仔细" | "没检查token有效期" | "部署脚本未在curl前验证GITHUB_TOKEN有效性，token过期后静默返回403而非明确报错" |
| prevention_rule | "下次注意" | "部署前检查token" | "deploy.sh添加preflight阶段：curl -sS -H Authorization HEAD api.github.com，非200则abort并打印诊断信息" |
| scope | 随意标注 | 基于直觉判断 | 有跨项目验证证据支撑 |

总分6+为合格反思卡片，4-5分需要修订，3分以下重写。
