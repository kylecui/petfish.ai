# 胖鱼 PEtFiSh — 安装指南 / Install Guide

---

## 一句话安装（推荐） / One-Line Install (Recommended)

把下面这句话粘贴到你的AI编程助手里，它会自己完成安装：

Paste this into any AI coding assistant — it handles the rest:

```
Install PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-install.md
```

中文版 / Chinese version：

```
请按照这个文档安装胖鱼PEtFiSh：https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-install.md
```

**工作原理 / How it works**：AI助手读取那个URL里的安装指令，自动检测你的操作系统和AI平台，问你几个问题，然后跑对应的安装命令。全程对话式，你只管回答。

The AI assistant reads the install doc from that URL, auto-detects your OS and AI platform, asks a few questions, then runs the right install commands. Conversational — just answer the prompts.

**适用范围 / Works with**：所有能跑终端命令的AI编程助手 / Any AI coding assistant that can run terminal commands — OpenCode, Claude Code, Cursor, Copilot, Windsurf, Codex, Antigravity.

---

## 命令行安装 / Command-Line Install

更习惯直接跑命令？没问题。

Prefer running commands directly? Here you go.

**Bash (macOS / Linux / WSL):**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack init,companion --detect
```

**PowerShell (Windows):**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "init,companion" -Detect
```

装完输入 `/initproject`，胖鱼会问你项目类型，然后自动装上匹配的能力包。

After install, type `/initproject` — PEtFiSh asks your project type and auto-installs matching packs.

---

## 装全套 / Install Everything

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack all --detect
```

---

## 升级 / Upgrade

已经装了？重跑一遍加 `--force` 就行。

Already installed? Re-run with `--force` to upgrade.

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh \
  | bash -s -- --pack all --force
```

或者让AI帮你升级 / Or let your AI handle it：

```
Upgrade PEtFiSh by following: https://raw.githubusercontent.com/kylecui/petfish.ai/master/docs/agent-upgrade.md
```

---

## 几点说明 / Notes

- 安装脚本**自动获取最新稳定release**，不用手动指定版本号。The installer auto-resolves the latest stable release — no version pinning needed.
- `--detect` 自动检测AI平台，把skill装到正确的目录。Auto-detects your AI platform and installs to the right path.
- `--pack init,companion` 先装初始化器和伙伴命令，其他pack后续按需装。Installs the initializer and companion first — add more packs later as needed.
- 要指定平台？`--platform cursor` / `--platform claude` / `--platform copilot`。Need a specific platform? Use `--platform`.
- 要指定版本？`--branch v0.6.3`（Bash）或 `-Branch v0.6.3`（PowerShell）。Need a specific version? Use `--branch`.

---

*><(((^> 胖鱼 PEtFiSh — Your AI Companion*
