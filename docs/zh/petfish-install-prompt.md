# 胖鱼 PEtFiSh — 安装指南

---

## 一句话安装（推荐）

把下面这句话粘贴到你的AI编程助手里，它会自己完成安装：

```
Install PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-install.md
```

中文版：

```
请按照这个文档安装胖鱼PEtFiSh：https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-install.md
```

**工作原理**：AI助手读取那个URL里的安装指令，自动检测你的操作系统和AI平台，问你几个问题，然后跑对应的安装命令。全程对话式，你只管回答。

**适用范围**：所有能跑终端命令的AI编程助手——OpenCode、Claude Code、Cursor、Copilot、Windsurf、Codex、Antigravity。

---

## 命令行安装

更习惯直接跑命令？没问题。

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack init,companion --detect
```

装完输入 `/initproject`，胖鱼会问你项目类型，然后自动装上匹配的能力包。

---

## 装全套

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --detect
```

---

## 升级

已经装了？重跑一遍加 `--force` 就行。

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack all --force
```

或者让AI帮你升级：

```
Upgrade PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-upgrade.md
```

---

## 几点说明

- 安装脚本**自动获取最新稳定release**，不用手动指定版本号。
- `--detect` 自动检测AI平台，把skill装到正确的目录。
- `--pack init,companion` 先装初始化器和伙伴命令，其他pack后续按需装。
- 要指定平台？`--platform cursor` / `--platform claude` / `--platform copilot`。
- 前置条件：[uv](https://docs.astral.sh/uv/getting-started/installation/) — 安装器通过PEP 723自动引导，无需手动配置Python。

---

*><(((^> 胖鱼 PEtFiSh — 你的AI伙伴*
