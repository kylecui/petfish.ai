# 胖鱼 PEtFiSh — 安装提示词

---

## 一句话安装（推荐）

将以下一句话粘贴到任意AI编程助手的对话框中，AI会自动完成安装：

```
Install PEtFiSh by following: https://raw.githubusercontent.com/kylecui/SKILL_builder/master/docs/agent-install.md
```

中文版：

```
请按照这个文档安装胖鱼PEtFiSh：https://raw.githubusercontent.com/kylecui/SKILL_builder/master/docs/agent-install.md
```

**工作原理**：AI助手读取该URL中的安装指令文档，自动检测操作系统和AI平台，询问项目类型，然后执行对应的安装命令。整个过程是对话式的，你只需要回答几个问题。

**适用范围**：所有能执行终端命令的AI编程助手——OpenCode、Claude Code、Cursor、Copilot、Windsurf、Codex、Antigravity等。

---

## 传统命令行安装

如果你更习惯直接跑命令：

**Bash (macOS/Linux/WSL):**
```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack init,companion --detect
```

**PowerShell (Windows):**
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.ps1))) -Pack init,companion -Detect
```

装完后输入`/initproject`，胖鱼会引导你选择项目类型并自动安装匹配的skill pack。

---

## 安装全部pack

```bash
curl -fsSL https://raw.githubusercontent.com/kylecui/SKILL_builder/master/remote-install.sh | bash -s -- --pack all --detect
```

---

## 说明

- 安装脚本会**自动获取最新稳定release版本**（当前v0.2.0），无需手动指定版本号
- `--detect` 自动检测当前AI平台，将skill安装到正确路径
- `--pack init,companion` 一次安装初始化器和`/petfish`伙伴命令，后续通过`/initproject`按需装其他pack
- 如需指定平台：`--platform cursor` / `--platform claude` / `--platform copilot` 等
- 如需指定版本：`--branch v0.2.0`（bash）或 `-Branch v0.2.0`（PowerShell）

---

*><(((^> 胖鱼 PEtFiSh — AI Worker's Companion*
