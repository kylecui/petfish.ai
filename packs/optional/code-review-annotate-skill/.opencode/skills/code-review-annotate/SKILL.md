---
name: code-review-annotate
description: 全量代码审查与文档注释流水线：为每个函数声明/定义写 用途/调用/返回 注释头，就地 //bugbug 标注安全问题，且保证代码 0 删改。用于逐行code review、函数注释、加注释、全量审查、全量审查注释、长程review、只加注释、修注释不改代码、bugbug标注。适配大代码库（50K-200K行）与子代理并行平台，含批次划分/并发槽纪律与平台故障恢复。Use when annotate every function, line-by-line review。不处理小范围单文件review或功能开发。
metadata:
  version: 1.0.0
  author: PEtFiSh
---

# Code Review Annotate — 全量审查注释流水线

目标：对整个代码库（或指定范围）做逐行审查，为**每一个**函数声明/定义写文档注释，安全问题就地 `//bugbug` 标注，**绝不修改任何代码行、绝不删除任何既有注释**。适配大代码库（50K-200K 行）与子代理并行执行平台。

## 触发场景

触发短语：逐行code review、函数注释、加注释、全量审查、全量审查注释、长程review、只加注释、修注释不改代码、bugbug标注、annotate every function、line-by-line review

边界：不处理小范围单文件review或功能开发——那是普通代码任务的职责。

## 0. 硬约束（每次都必须重复给子代理）

1. **只加注释行**。diff 中 deletions 必须 = 0；每批完成后审计。
2. **不删任何既有注释**——包括"扩写"式替换（原句必须原样保留，扩展文本作为续行追加在后面）。
3. 已有 `用途/调用/返回` 格式注释的函数：跳过，不重复。
4. 续作任务必须先读 diff 前沿，从断点继续，靠"skip 已注解"天然幂等。

## 1. 注释格式

```c
// 用途: <一行：这个函数做什么>
// 调用: <参数含义; 调用时机/调用方（REST路由/定时器/IPC/启动序列/事件循环）>
// 返回: <精确语义：0=成功 / -1=错误 / NULL / 指针所有权 / bool>
```

- 三行起；trivial 一行函数可合并为单行 `// <用途>；返回: <值>`
- 头文件原型：非平凡函数写全三行；简单原型单行即可
- 重要的 map/结构体/宏定义：加单行说明（尤其 wire struct、共享 ABI、字节序字段）
- 时间紧张时：给必须跳过的函数留下 `// TODO-ANNOTATE` 标记（可见缺口优于静默缺口），最终 sweep 收口
- 其他语言的格式变体见 `references/language-adaptations.md`

## 2. //bugbug 分类清单（按项目类型裁剪）

**安全类（任何 C 服务通用）**：`system()`（注入面）；`strcpy/strcat/sprintf` 用于外部输入；无宽度限制的 `sscanf`；SQL 字符串拼接；format string 注入；constant-time 比较缺失（口令/HMAC 用 memcmp）；弱随机源做 token；TLS 证书/主机名校验关闭；TOCTOU（access+open、check+use）
**内存类**：malloc 不查 NULL；error path 缺 free/close/finalize；double free；use-after-free；fd 泄漏
**逻辑类**：条件取反、off-by-one、switch 缺 break、注释与代码矛盾、静默截断、last-writer-wins 双写路径、错误码折叠进成功码
**领域类（按项目注入）**：网络字节序位运算前缺 `ntohl()`；BPF map lookup NULL 不查；spin_lock 无 unlock 路径；packed 缺失的 wire struct；CSV/公式注入；syslog 注入；分页参数无界；重连后状态未重注册
**非C语言**：见 `references/language-adaptations.md` 逐语言清单（Go/Rust/Python/Java/TS）

标注位置：贴在冒犯行上方或行尾，格式 `//bugbug: <一句问题描述>`。

## 3. 批次划分（先测平台，再定流水线）

开工前用小批次探测平台约束，然后按探测结果定参：

1. **单任务上限**：平台若有任务时长硬上限 T（如 30min），批次规模 ≤ 0.6T 的工作量。按经验速率（~80-100 行/分钟注解）折算行数，宁小勿大。
2. **并发槽**：探测并发度（启动 N 个小任务看几个真正运行）。**在飞任务数 = 并发槽**，绝不排队——排队超时是批量死亡的头号原因。
3. **批次划分**：>2.5K 行的大文件单独成批或纵向切片（切片必须显式声明行号边界 + "函数定义落在界内才归你"规则，防止相邻批次重复注解同一函数）。
4. **同文件不并行**：同一文件的两个切片串行执行（part1 完成通知后再发 part2），避免编辑冲突。

## 4. 子代理 Prompt 模板（每批必带 6 段）

```
TASK: 审查注释以下文件（附精确路径+行数）：<列表>
EXPECTED OUTCOME: 每个函数有文档注释；git diff 每文件 deletions=0；可疑代码有 //bugbug
REQUIRED TOOLS: read, edit, bash（仅限 git diff --numstat）；禁 make/构建/测试；禁触碰清单外文件
MUST DO:
  1. 时间预算 ~X 分钟（平台上限 × 0.6）；分块读、边读边注
  2. 注释格式（贴 §1 模板）
  3. TIME-SAFETY：超时风险时留 // TODO-ANNOTATE 而非静默跳过
  4. bugbug 清单（贴 §2，按本项目裁剪，附项目专属契约如 ARCH/SEC 编号语境）
  5. 每注 ~10 个函数跑一次 git diff --numstat，deletions>0 立即修复
  6. 既有 用途/调用/返回 注释：跳过
MUST NOT DO: 改码/删注释/触碰清单外文件/跑构建/sed 批量编辑
CONTEXT: 项目是什么、该模块职责、项目级硬规则（如禁止 system()、日志规范、已知债务编号）
SUCCESS CRITERIA: 全覆盖 + 仅注释新增 + 结尾报告（注解数/bugbug 数/TODO 标记数）
```

## 5. 验证门禁

一键验证（跨平台，推荐）：

```bash
uv run verify_annotations.py --paths <files...>   # 或不带 --paths 检查全部变更
```

输出：每文件 numstat（deletions 必须 0）、行注释内嵌 `/*` 的 `-Werror=comment` 风险行、剩余 `TODO-ANNOTATE` 计数；有违规退出码 1。

手动等价检查：

- **每批**：`git diff --numstat <files>` deletion 列必须为 0；>0 立即定位修复（常见根因：扩写替换了原注释行）
- **全量**：`git diff | grep '^-' | grep -v '^---'` 必须为空；`grep -rn "TODO-ANNOTATE"` 收口到 0（或转为情报性 caveat 并在报告中说明）
- **编译**：`make`（或等价构建）+ lint 全绿。注释也能炸构建：块注释内嵌 `/*`（如写 `bpf/*.bpf.c`）触发 `-Werror=comment`；务必全树扫描 `git diff | grep '^+' | awk -F'/\*' 'NF>2'`
- **报告**：发现结构化落盘（严重级/类别/模块矩阵 + 全量表格），人工复核的结论性发现单独成节

## 6. 平台故障恢复（实测经验）

| 故障 | 症状 | 处置 |
|---|---|---|
| 任务时长硬超时 | 工作中被杀，工作树保留部分成果 | 发续作任务（读 diff 前沿 → skip 已注解 → 继续）；**不**整批重来 |
| 排队超时 | 任务 0s 死亡、从未运行 | 取消排队；改为在飞=并发槽，完成通知驱动补位 |
| 0 秒空跑 flake | completed 但 duration=0s、无 session 内容 | `git diff` 核实无产出后原样重发 |
| 会话不可恢复 | timeout 后 task_id/session 查无 | 不依赖 session 续作；成果在工作树，天然可续 |

## 7. 交付物清单

1. 注释后的工作树（未提交，供人工 diff 复核）
2. 发现报告 markdown：总览矩阵 → 人工复核结论 → 各级全量表（file:line 可检索）
3. 一句话可用性：`grep -rn "bugbug" <dirs>` 定位全部原文
