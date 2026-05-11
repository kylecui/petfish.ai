# Phase 2 A/B Test Guide — Topic-Aware Compaction

## Overview

本测试对比 OpenCode 默认 compaction（baseline）与 fish-trail topic-structured compaction（plugin）在 token 用量和上下文召回质量上的差异。

测试脚本自动向两个 OpenCode Server 实例发送相同的多话题对话序列，触发 compaction 后发送 recall 问题，最终输出量化对比报告。

---

## 前置条件

| 依赖 | 用途 |
|------|------|
| `opencode` CLI | 启动 Server 实例 |
| `uv` | 运行测试脚本（自动处理 httpx 依赖） |
| 两个可用端口 | 默认 3100（baseline）和 3200（plugin） |

---

## 测试环境结构

```
<test-root>/
├── test-baseline/                          # 无插件，OpenCode 默认 compaction
│   ├── opencode.json                       # model 配置
│   ├── .opencode/
│   │   └── plugin/                         # 空目录（无插件）
│   └── .petfish/fish-trail/
│       ├── topic-registry.json             # 3 个 synthetic topics
│       └── topics/
│           ├── topic_ab_python.json        # active topic
│           ├── topic_ab_database.json
│           └── topic_ab_cicd.json
│
├── test-plugin/                            # Phase 2 插件启用
│   ├── opencode.json
│   ├── .opencode/
│   │   └── plugin/
│   │       └── fish-trail-compaction.ts    # Phase 2 compaction 插件
│   └── .petfish/fish-trail/
│       ├── topic-registry.json             # 相同的 3 个 topics
│       └── topics/
│           ├── topic_ab_python.json
│           ├── topic_ab_database.json
│           └── topic_ab_cicd.json
│
└── ab_test_harness.py                      # 测试脚本
```

两个目录使用完全相同的 topic 数据，唯一区别是 `test-plugin/` 包含 compaction 插件。

---

## 快速开始

### 1. 准备测试目录

从项目根目录复制文件到独立测试位置（可选，也可直接在项目内运行）：

```powershell
# Windows PowerShell
$TestRoot = "D:\test-compaction"
New-Item -ItemType Directory -Path $TestRoot -Force
Copy-Item -Recurse test-baseline $TestRoot\test-baseline
Copy-Item -Recurse test-plugin $TestRoot\test-plugin
Copy-Item research\topic-aware-compaction\06_outputs\ab_test_harness.py $TestRoot\
```

```bash
# macOS / Linux
TEST_ROOT=~/test-compaction
mkdir -p "$TEST_ROOT"
cp -r test-baseline "$TEST_ROOT/"
cp -r test-plugin "$TEST_ROOT/"
cp research/topic-aware-compaction/06_outputs/ab_test_harness.py "$TEST_ROOT/"
```

### 2. 启动两个 OpenCode Server

打开**两个独立终端**，分别在 `test-baseline/` 和 `test-plugin/` 目录下启动 server。

**终端 1 — Baseline（端口 3100）：**

```powershell
# Windows PowerShell
cd D:\test-compaction\test-baseline
$env:OPENCODE_SERVER_PASSWORD='test'
opencode serve --port 3100
```

```bash
# macOS / Linux
cd ~/test-compaction/test-baseline
OPENCODE_SERVER_PASSWORD=test opencode serve --port 3100
```

**终端 2 — Plugin（端口 3200）：**

```powershell
# Windows PowerShell
cd D:\test-compaction\test-plugin
$env:OPENCODE_SERVER_PASSWORD='test'
opencode serve --port 3200
```

```bash
# macOS / Linux
cd ~/test-compaction/test-plugin
OPENCODE_SERVER_PASSWORD=test opencode serve --port 3200
```

确认两个 server 均输出 `listening on :3100` / `:3200` 后继续。

### 3. 运行测试

在**第三个终端**：

```powershell
# Windows PowerShell
cd D:\test-compaction
uv run ab_test_harness.py
```

```bash
# macOS / Linux
cd ~/test-compaction
uv run ab_test_harness.py
```

---

## 测试流程

脚本自动执行以下步骤：

1. **健康检查** — 等待两个 server 就绪（30s 超时）
2. **创建 session** — 各 server 创建一个新会话
3. **发送 10 条对话消息** — 交替覆盖 3 个话题：
   - `python-setup`：Python 项目结构、pyproject.toml、CLI 开发
   - `database`：PostgreSQL schema、审计日志、RLS、连接池
   - `cicd`：GitHub Actions、Docker、K8s 部署、Slack 通知
4. **触发 compaction** — 消息量设计为超过 context limit，迫使 compaction 发生
5. **发送 3 个 recall 问题** — 每个话题 1 个，测试压缩后的上下文保留质量
6. **收集数据** — 提取每条 assistant 消息的 token 统计和 compaction 计数
7. **输出报告** — 终端打印对比表格，完整数据写入 JSON

---

## 配置

通过环境变量自定义测试参数：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AB_BASELINE_PORT` | `3100` | Baseline server 端口 |
| `AB_PLUGIN_PORT` | `3200` | Plugin server 端口 |
| `AB_PASSWORD` | `test` | Server 认证密码 |
| `AB_MODEL` | `anthropic/claude-sonnet-4-20250514` | 使用的模型 |

示例：使用不同端口和模型：

```powershell
$env:AB_BASELINE_PORT='4100'
$env:AB_PLUGIN_PORT='4200'
$env:AB_MODEL='anthropic/claude-sonnet-4-20250514'
uv run ab_test_harness.py
```

---

## 输出

### 终端报告

```
Token Usage Comparison:
Metric                       Baseline       Plugin        Delta        %
-----------------------------------------------------------------------
Input Tokens                  120,000       48,000      -72,000   -60.0%
Output Tokens                  30,000       28,000       -2,000    -6.7%
...

Metric                       Baseline       Plugin
-------------------------------------------------
Messages                           13           13
Compactions                         2            2
Wall Time (s)                   180.5        175.2
```

### JSON 报告

完整结果自动保存到脚本同目录的 `ab_test_results.json`，包含：

- 各维度 token 统计（input / output / reasoning / cache read / cache write）
- compaction 触发次数
- wall time
- 每个 recall 问题的回复文本（截断至 500 字符）
- 错误记录

---

## 预期结果

| 指标 | Baseline | Plugin（预期） |
|------|----------|----------------|
| Input tokens（compaction 后） | 基准 | 降低 ~60% |
| Recall 质量 | 基准 | 持平或更好 |
| Topic 分离度 | 混合在一段摘要里 | 按 topic 结构化组织 |
| Compaction 次数 | N | ≥ N（相同或更多） |

---

## 故障排查

| 症状 | 原因 | 解决方案 |
|------|------|----------|
| `Server not ready within 30s` | server 未启动或端口不对 | 检查 server 终端输出，确认端口 |
| `httpx.ConnectError` | server 进程崩溃或被防火墙拦截 | 检查 server 日志，确认 localhost 可访问 |
| compaction 未触发 | 消息量不足以超过 context limit | 检查 `opencode.json` 中的 model context 配置 |
| 两组 token 数差异很小 | 插件未加载 | 确认 `test-plugin/.opencode/plugin/fish-trail-compaction.ts` 存在 |
| recall 回复为空 | model 配置错误或 API key 无效 | 检查 `opencode.json` 和环境中的 API key |

---

## 测试完成后清理

```powershell
# 停止两个 server（Ctrl+C）
# 删除测试目录（如使用独立位置）
Remove-Item -Recurse D:\test-compaction
```

```bash
rm -rf ~/test-compaction
```

项目内的 `test-baseline/` 和 `test-plugin/` 已在 `.gitignore` 中，不会被提交。
