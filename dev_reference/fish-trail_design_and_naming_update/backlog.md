# PEtFiSh v0.5 Backlog

> 从 implementation-plan.md 拆解的可执行 backlog

---

## Epic 1: 仓库更名 (P0)

### E1-1: 全量扫描旧仓库名引用
- **类型**: 调研
- **描述**: grep 扫描所有文件中 `SKILL_builder` 和 `kylecui/SKILL_builder` 的出现位置，输出影响清单
- **验收**: 输出文件路径 + 行号清单

### E1-2: 批量替换仓库名
- **类型**: 实现
- **描述**: 将所有 `kylecui/SKILL_builder` 替换为 `kylecui/petfish.ai`，将所有独立的 `SKILL_builder` 仓库引用替换为 `petfish.ai`
- **排除**: dev_reference/ 目录内的历史文档不改
- **验收**: grep 确认零残留（排除 dev_reference/）

### E1-3: 验证安装脚本语法
- **类型**: 验证
- **描述**: PowerShell 语法检查 + bash -n 语法检查 4 个安装脚本
- **验收**: 无语法错误

### E1-4: 运行测试套件
- **类型**: 验证
- **描述**: pytest tests/ -x -q 全量通过
- **验收**: 278+ pass

### E1-5: GitHub 仓库 rename
- **类型**: 运维
- **描述**: 在 GitHub Settings 执行 rename: SKILL_builder → petfish.ai
- **前置**: E1-2, E1-3, E1-4 全部通过
- **验收**: 新 URL https://github.com/kylecui/petfish.ai 可访问

### E1-6: 更新本地 remote URL
- **类型**: 运维
- **描述**: `git remote set-url origin https://github.com/kylecui/petfish.ai.git`
- **验收**: git push 成功

### E1-7: PR + Release v0.5.0
- **类型**: 发布
- **描述**: dev → master PR，merge，创建 release v0.5.0
- **验收**: release tag 存在，install 脚本可从新 URL 下载

### E1-8: 部署 web
- **类型**: 运维
- **描述**: scp web/*.html 到 38.55.160.238
- **验收**: petfish.ai 网站 GitHub 链接指向新仓库

---

## Epic 2: fish-* 命名体系 Phase 1 (P1)

### E2-1: 安装脚本添加 fish-* alias
- **类型**: 实现
- **描述**: 在 4 个安装脚本的 alias 映射表中新增 fish-init/fish-core/fish-course/fish-testdocs/fish-deploy/fish-style/fish-slides/fish-calibrate/fish-trail 别名，指向现有 pack 目录
- **验收**: `--pack fish-trail` 等价于 `--pack context`

### E2-2: 新增 /fish 命令
- **类型**: 实现
- **描述**: 在 petfish-companion-skill 的 commands 中新增 `/fish` 作为 `/petfish` 的等价短命令
- **验收**: `/fish` 和 `/petfish` 行为一致

### E2-3: 更新 README fish-* 命名
- **类型**: 文档
- **描述**: README.md 主表使用 fish-* 命名，旧别名标注为 legacy
- **验收**: README 中 fish-* 为主命名

### E2-4: 更新 web 页面
- **类型**: 文档
- **描述**: index.html / blog.html / pitch.html 中的 pack 名和命令示例更新为 fish-*
- **验收**: 网页内容与 README 一致

### E2-5: 测试 alias 兼容性
- **类型**: 验证
- **描述**: 测试所有旧 alias 仍正常工作，新 alias 正确映射
- **验收**: 所有 alias 正确解析

### E2-6: Release v0.5.1
- **类型**: 发布
- **描述**: PR + merge + release + deploy
- **验收**: release 发布，web 部署

---

## Epic 3: fish-trail MVP (P2)

### E3-1: 设计 topic_graph.json schema
- **类型**: 设计
- **描述**: 定义 topic node、relation edge、evidence level 的 JSON schema，写入 references/topic-schema.md
- **验收**: schema 可用于 validate 脚本

### E3-2: 创建模板文件
- **类型**: 实现
- **描述**: topic-card-template.md、active-context-template.md、config-template.yaml
- **验收**: 模板文件存在且格式正确

### E3-3: rename context-router → fish-trail (pack 目录)
- **类型**: 重构
- **描述**: `packs/context-router-skill/` → `packs/fish-trail/`，pack-manifest.json 添加 legacy_names，安装脚本 alias 指向新目录
- **验收**: `--pack fish-trail` 和 `--pack context` 都正常安装

### E3-4: 实现 topic_route.py
- **类型**: 实现
- **描述**: 基于 topic_detect 结果，生成 active_context.md（含 must_load / may_load / must_not_load）
- **验收**: 给定 topic graph 和 query，输出正确的 active_context.md

### E3-5: 升级 topic_detect.py
- **类型**: 增强
- **描述**: 增加 topic card 摘要匹配、recent route 加权、显式用户短语加权
- **验收**: routing accuracy >= 0.85 on eval set

### E3-6: 实现 topic_report.py
- **类型**: 实现
- **描述**: 扫描 topic graph，生成 TOPIC_REPORT.md（hub topics、stale topics、pollution risks）
- **验收**: 输出结构化报告

### E3-7: 实现 topic_validate.py
- **类型**: 实现
- **描述**: 校验 topic_graph.json 结构完整性（唯一 ID、edge 引用合法、evidence level 合法）
- **验收**: 能检测出故意注入的错误

### E3-8: 升级 topic_update.py
- **类型**: 增强
- **描述**: 支持从 task notes 提取新决策、新 relations、废弃旧结论
- **验收**: 更新后 graph 仍通过 validate

### E3-9: 状态目录迁移 .ai-context → .petfish/fish-trail
- **类型**: 实现
- **描述**: MCP server 启动时检测旧目录，自动迁移到新路径
- **验收**: 旧数据在新路径正常访问

### E3-10: 更新 SKILL.md
- **类型**: 文档
- **描述**: fish-trail SKILL.md 描述新工作流（detect → route → execute → update → validate）
- **验收**: OpenCode 能正确触发 fish-trail skill

### E3-11: 编写 evals
- **类型**: 测试
- **描述**: evals.json 包含 route-current-topic、detect-topic-split、avoid-context-pollution 3 个核心测试用例
- **验收**: eval 可运行

### E3-12: 集成测试
- **类型**: 验证
- **描述**: 在 petfish.ai 自身 repo 中初始化 fish-trail，管理 5+ topics，验证闭环
- **验收**: detect → route → active_context → update → report 全流程跑通

### E3-13: Release v0.5.2
- **类型**: 发布
- **描述**: PR + merge + release + deploy
- **验收**: fish-trail 作为可安装 pack 发布

---

## Epic 4: 后续 (P3, 不在本轮)

- E4-1: fish-* 命名 Phase 2 — README 全面切换，旧名降为 legacy
- E4-2: fish-* 命名 Phase 3 — pack 目录全部 rename
- E4-3: fish-trail Phase 2 — split/merge/stale/handoff
- E4-4: fish-trail Phase 3 — HTML topic map + Graphify adapter
- E4-5: fish-trust 新 pack — 供应链安全与可信度评估
- E4-6: /fish 子命令完整化（fish lint / fish audit / fish gate / fish trail）

---

## 执行顺序总览

```
Week 1:
  E1-1 → E1-2 → E1-3 → E1-4 → E1-5 → E1-6 → E1-7 → E1-8  (v0.5.0)
  E2-1 → E2-2 → E2-3 → E2-4 → E2-5 → E2-6                  (v0.5.1)

Week 2-3:
  E3-1 → E3-2 → E3-3                                          (schema + rename)
  E3-4 → E3-5 → E3-6 → E3-7 → E3-8                           (脚本实现)
  E3-9 → E3-10 → E3-11 → E3-12 → E3-13                       (v0.5.2)
```
