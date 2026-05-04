# PEtFiSh v0.5 实施方案

> 仓库更名 + fish-* 命名体系 + fish-trail 话题轨迹管理器

---

## 0. 优先级判断

| 序号 | 工作项 | 优先级 | 理由 |
|---:|---|---|---|
| 1 | 仓库更名 SKILL_builder → petfish.ai | **P0 — 必须先做** | 所有安装脚本、文档、URL 硬编码旧仓库名。后续改动越多，迁移成本越高。 |
| 2 | fish-* 命名体系 Phase 1（双命名） | **P1 — 紧随其后** | 新别名系统是 fish-trail 和品牌升级的前置条件。Phase 1 只加新 alias，不破坏旧用户。 |
| 3 | fish-trail MVP | **P2 — 核心产品** | 胖鱼从"skill installer"升级为"AI 协作环境管理器"的关键转折。依赖命名体系就绪。 |

依赖关系：

```
[P0] 仓库更名
  ↓ (所有 URL/脚本指向新仓库)
[P1] fish-* 命名 Phase 1
  ↓ (pack alias + skill 目录就绪)
[P2] fish-trail MVP
  ↓ (上下文治理能力上线)
[P3] fish-* 命名 Phase 2-3 + fish-trail 高级功能
```

---

## 1. P0 — 仓库更名

### 1.1 影响面

| 影响位置 | 变更内容 |
|---|---|
| GitHub 仓库名 | `kylecui/SKILL_builder` → `kylecui/petfish.ai` |
| 安装脚本 (4个) | 所有 raw.githubusercontent.com URL |
| README.md | 仓库链接、安装命令 |
| web/*.html | GitHub 链接 |
| AGENTS.md | 仓库引用 |
| pack-manifest.json | repository 字段 |
| 所有引用旧仓库名的文档 | grep 全量替换 |

### 1.2 关键风险

- **GitHub 自动重定向**：GitHub rename 后旧 URL 自动 301 到新 URL，不会立即破坏。但重定向会在其他人 fork 或创建同名仓库时失效。
- **用户已安装脚本缓存**：用户如果保存了旧 URL 的脚本，重定向期间仍能用。
- **域名**：petfish.ai 域名已有，仓库名与域名一致有利于品牌。

### 1.3 执行步骤

```
1. grep 全量扫描 SKILL_builder 和 kylecui/SKILL_builder 所有出现位置
2. 批量替换为 petfish.ai 和 kylecui/petfish.ai
3. 本地验证安装脚本语法
4. 运行测试
5. commit 到 dev
6. 在 GitHub Settings → General → Repository name 执行 rename
7. 立即 push dev（此时 remote URL 已变）
8. PR → master → release v0.5.0 (major: 仓库 URL 变更是破坏性的)
9. 部署 web
```

### 1.4 版本号

仓库更名是**破坏性变更**（旧 URL 最终会失效），应升级 major 版本：**v0.5.0**。

> 注：之前说过 "no v0.5, we are not ready for v0.5"。但仓库更名 + 命名体系重构正是 v0.5 的合理时机。如果你仍希望保持 v0.4.x，我会在 v0.4.16 中做。请确认。

### 1.5 退出标准

- [ ] `grep -r "SKILL_builder"` 除 dev_reference/ 和 CHANGELOG 外零结果
- [ ] 所有安装脚本语法验证通过
- [ ] 278 tests pass
- [ ] GitHub 仓库已 rename
- [ ] web 已 redeploy
- [ ] README 安装命令可用

---

## 2. P1 — fish-* 命名体系 Phase 1

### 2.1 范围（Phase 1 只做双命名）

- 安装脚本支持新 alias（fish-init, fish-core, fish-trail 等）
- 旧 alias（init, companion, context 等）保持完全可用
- pack 目录暂不重命名（避免大量文件移动）
- README 和 web 中新增 fish-* 命名说明

### 2.2 具体变更

| 文件 | 变更 |
|---|---|
| install.ps1 / install.sh | alias 映射表新增 fish-* 别名 |
| remote-install.ps1 / remote-install.sh | 同上 |
| README.md | 新增 fish-* 命名说明，旧别名标为 legacy |
| web/index.html | 更新命令示例 |
| platforms.json | 无变更（alias 在安装脚本中处理） |

### 2.3 安装升级中的 legacy name 处理（关键约束）

用户可能已经用旧名安装了 pack（如 `context-router-skill`），现在用新名升级（如 `fish-trail`）。安装脚本必须：

1. **pack-manifest.json 新增 `legacy_names` 字段**：声明该 pack 的旧名
2. **registry 查询时双向查找**：用新名查不到时，用 `legacy_names` 列表查旧名 registry entry
3. **版本比较跨名称**：旧名 v0.5.0 已安装 → 新名 v0.5.1 来了 → 识别为升级
4. **registry 更新为新名**：升级完成后，registry 中旧名 entry 删除，新名 entry 写入
5. **旧 skill 目录清理**：如果 skill 目录名也变了（如 `context-router/` → `fish-trail/`），升级时需要：
   - 删除旧目录
   - 安装新目录
   - AGENTS.md 中旧 marker 替换为新 marker

实现方案：

```bash
# pack-manifest.json 示例
{
  "name": "fish-trail",
  "version": "0.5.0",
  "legacy_names": ["context-router-skill"]
}

# check_pack_version 函数增强：
#   1. 先用当前 pack_name 查 registry
#   2. 查不到 → 遍历 manifest.legacy_names 查 registry
#   3. 找到旧名 entry → 比较版本 → 返回 "newer" + 标记需要 legacy cleanup
#
# install 循环增强：
#   1. 如果检测到 legacy name upgrade：
#      - 删除旧 skill 目录
#      - 删除旧 agent 目录
#      - 在 AGENTS.md 中替换旧 marker（BEGIN/END pack: old-name → BEGIN/END pack: new-name）
#      - 删除 registry 中旧名 entry
#   2. 然后正常安装新 pack
```

### 2.4 alias 映射

```bash
# 新 alias → 实际 pack 目录（Phase 1 不改目录）
fish-init       → project-initializer-skill
fish-core       → petfish-companion-skill
fish-course     → opencode-course-skills-pack
fish-testdocs   → opencode-skill-pack-testcases-usage-docs
fish-deploy     → repo-deploy-ops-skill-pack
fish-style      → petfish-style-skill
fish-slides     → opencode-ppt-skills
fish-calibrate  → anti-sycophancy-calibration-pack
fish-trail      → context-router-skill
```

### 2.4 命令体系

新增 `/fish` 命令作为 `/petfish` 的短别名。两者等价，`/petfish` 保持完全兼容。

### 2.5 退出标准

- [ ] `--pack fish-trail` 等价于 `--pack context`
- [ ] 所有旧 alias 仍可用
- [ ] README 主推 fish-* 命名
- [ ] 测试通过

---

## 3. P2 — fish-trail MVP

### 3.1 与 context-router 的关系

当前 context-router 已有：
- topic_store.py（topic CRUD + graph）
- topic_detector.py（规则检测 relation）
- contamination_scorer.py（污染评分）
- context_builder.py（context package 生成）
- session_store.py（会话管理）
- server.py（MCP server，28 个 tools）

fish-trail 是 context-router 的**产品升级**，不是重写。实施路径：

```
context-router-skill/ 目录 rename → fish-trail/
内部模块保持稳定
新增：topic_graph.json schema、topic card、active_context.md、decision log
```

### 3.2 MVP 范围（Phase 1 of fish-trail）

| 功能 | 来源 | 状态 |
|---|---|---|
| topic graph JSON schema | 新增 | 待实现 |
| topic card 模板 + 生成 | 新增 | 待实现 |
| active_context.md 生成 | context_builder.py 升级 | 改造 |
| context firewall (must/may/must_not) | 新增 | 待实现 |
| topic_detect (识别当前 topic) | topic_detector.py 已有 | 增强 |
| topic_update (任务后更新) | topic_store.py 已有 | 增强 |
| topic_report (全局报告) | 新增 | 待实现 |
| topic_validate (schema 校验) | 新增 | 待实现 |
| SKILL.md + SECURITY.md | 已有，需更新 | 改造 |
| MCP server 保持兼容 | server.py 已有 | 保持 |

### 3.3 状态目录迁移

```
当前：.ai-context/          (context-router 数据目录)
目标：.petfish/fish-trail/   (fish-trail 新目录)
```

兼容策略：如果检测到 `.ai-context/` 存在但 `.petfish/fish-trail/` 不存在，自动迁移。

### 3.4 开发阶段

**Phase 2a — Schema + Templates (1-2 天)**
- topic_graph.json schema 定义
- topic card markdown 模板
- active_context.md 模板
- config.yaml 模板
- references/ 文档

**Phase 2b — 脚本实现 (3-5 天)**
- topic_detect.py 升级（关键词 + topic card 摘要匹配）
- topic_route.py 新增（生成 active_context.md）
- topic_update.py 升级（更新 card + graph + decisions）
- topic_report.py 新增（生成 TOPIC_REPORT.md）
- topic_validate.py 新增（schema 校验）

**Phase 2c — Skill 化 + 测试 (1-2 天)**
- 更新 SKILL.md（fish-trail 工作流）
- 更新 SECURITY.md
- evals.json 测试用例
- 集成测试

### 3.5 退出标准

- [ ] 在 petfish.ai 自身 repo 中能管理 5+ topics
- [ ] 能生成有效 active_context.md（含 must/may/must_not）
- [ ] topic card 可从对话记录生成和更新
- [ ] MCP server 仍兼容 opencode
- [ ] 278+ tests pass

---

## 4. 时间估算

| 阶段 | 预估工期 | 产出 |
|---|---|---|
| P0 仓库更名 | 0.5 天 | v0.5.0 release |
| P1 fish-* 双命名 | 1 天 | v0.5.1 release |
| P2a fish-trail schema | 1-2 天 | schema + templates |
| P2b fish-trail 脚本 | 3-5 天 | MVP 功能 |
| P2c fish-trail skill化 | 1-2 天 | v0.5.2 release |

总计约 **7-10 个工作日**。

---

## 5. 决策点（需你确认）

| # | 问题 | 选项 | 推荐 |
|---|---|---|---|
| 1 | 版本号 | v0.5.0 (major) 还是 v0.4.16 (patch)? | v0.5.0 — 仓库更名 + 体系重构是合理的 major 升级 |
| 2 | 仓库 rename 时机 | 现在做（与命名体系一起）还是 fish-trail 完成后? | 现在做 — 越晚成本越高 |
| 3 | context-router → fish-trail 是 rename 还是新 pack? | rename（保留 legacy alias）还是全新目录? | rename + legacy alias — 代码复用，用户无感 |
| 4 | `.ai-context/` → `.petfish/fish-trail/` 自动迁移? | 自动迁移 / 并存 / 手动? | 自动迁移 + 兼容检测 |
| 5 | `/fish` 命令是否在 Phase 1 就加? | Phase 1 加 / 延后到 fish-trail 完成后? | Phase 1 加 — 成本低，品牌效果好 |

---

## 6. 风险登记

| 风险 | 影响 | 缓解 |
|---|---|---|
| 仓库 rename 后旧 URL 失效 | 用户安装失败 | GitHub 301 重定向至少持续数月；README 和 web 立即更新 |
| fish-* alias 与旧 alias 冲突 | 安装混乱 | alias 映射表严格测试 |
| context-router → fish-trail 迁移丢数据 | 用户 topic 数据丢失 | 自动迁移 + 备份提示 |
| fish-trail MVP scope creep | 工期膨胀 | 严格限制 MVP 只做 detect/route/update/report/validate |
| v0.5.0 破坏性变更吓退用户 | 用户不升级 | release notes 说明自动迁移，旧 alias 长期保留 |
