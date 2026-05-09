# Issue #91 修正方案：跨Pack触发关键词覆盖修复

## 问题背景

GitHub Issue #91 报告：用户输入"帮我仔细研究一下XXX"时，research-router skill未被触发。

根本原因：agent匹配skill时只读frontmatter `description`字段，而body中的`触发场景`section对匹配不可见。research-router的description中缺少"研究"这个最基本的中文关键词。

经全量审计发现，这不是research pack的孤立问题，而是跨所有7个pack的系统性问题：

- **54个skills**的body触发关键词未出现在frontmatter description中
- **0个pack**的AGENTS.md使用MUST级别路由规则
- **0个pack**有description与body对齐的自动化检查

## 修复目标

1. 修复所有skill的description ↔ body触发关键词缺口
2. 强化所有pack AGENTS.md的路由规则为MUST级别
3. 增加自动化防护，防止问题再次发生

---

## Phase 1: 紧急修复 (P0) — research pack核心路由

### 1.1 修复 research-router description

**文件**: `packs/research-skill-pack/.opencode/skills/research-router/SKILL.md`

**动作**: 在frontmatter description中添加缺失的高频触发词：
- "研究", "帮我研究", "仔细研究"
- "调研", "文献", "综述"
- 确保中英文核心触发词全覆盖

**验收标准**: 用户输入"帮我仔细研究一下XXX"时，research-router能被匹配

**QA场景**:
1. 修改description后，创建`core-trigger-evals-router-only.json`（从现有`core-trigger-evals.json`中提取research-router条目，转换为evaluate_triggers.py支持的格式）：
   ```json
   {
     "should_trigger": [
       "帮我研究一下AI安全的现状",
       "帮我仔细研究一下竞品的技术架构",
       "研究一下这个领域的最新进展",
       "帮我调研一下市场趋势",
       "I need to do a literature review on XDP",
       "做个竞品分析"
     ],
     "should_not_trigger": [
       "帮我写个函数",
       "fix the bug in auth.py",
       "deploy this to production",
       "create a new skill"
     ]
   }
   ```
2. 运行evaluate_triggers.py对research-router单独验证：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path packs/research-skill-pack/.opencode/skills/research-router --test-file packs/research-skill-pack/evals/trigger/core-trigger-evals-router-only.json --json --verbose
   ```
3. **预期结果**: verdict为`PASS`，所有should_trigger用例triggered=true（特别是包含"研究"的中文用例）

### 1.2 强化 research pack AGENTS.md 路由规则

**文件**: `packs/research-skill-pack/AGENTS.md`

**动作**: 将现有"推荐skill"措辞改为MUST级别规则：
- "涉及研究、调研、文献、证据收集类任务时，**必须**首先路由到 research-router"
- 添加明确的冲突解决规则（research意图 vs 普通搜索意图）

**验收标准**: AGENTS.md中包含至少3条MUST级别路由规则

**QA场景**:
1. 修改完成后验证（PowerShell）：
   ```powershell
   (Select-String -Path "packs/research-skill-pack/AGENTS.md" -Pattern "必须|MUST" -AllMatches).Matches.Count
   ```
2. **预期结果**: 返回值 ≥ 3

### 1.3 检查其他router/entry skills

**文件**: 
- `packs/research-skill-pack/.opencode/skills/experience-brief-framer/SKILL.md`
- `packs/research-skill-pack/.opencode/skills/decision-brief-framer/SKILL.md`
- `packs/research-skill-pack/.opencode/skills/research-brief-framer/SKILL.md`
- `packs/research-skill-pack/.opencode/skills/risk-research-brief/SKILL.md`
- `packs/research-skill-pack/.opencode/skills/learning-goal-framer/SKILL.md`
- `packs/research-skill-pack/.opencode/skills/learning-prerequisite-mapper/SKILL.md`

**动作**: 对每个router/entry skill，提取body中的触发场景关键词，与frontmatter description对比，补齐缺失项

**验收标准**: 所有router/entry类skill的description覆盖body中列出的触发场景关键词

**QA场景**:
1. 对每个修改后的skill，运行evaluate_triggers.py单独验证（以experience-brief-framer为例）：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path packs/research-skill-pack/.opencode/skills/experience-brief-framer --json
   ```
   （不带`--test-file`时脚本自动从description生成测试用例）
2. **预期结果**: 每个skill的verdict为`PASS`（trigger_pass_rate ≥ 0.80）

---

## Phase 2: 全Pack Description修复 (P1) — 批量修复

### 2.1 Research pack skills批量修复

**范围**: research pack下全部54个SKILL.md（排除Phase 1已修复的router/entry skills）

**方法**:
1. 对每个SKILL.md，提取body中的触发场景/触发词（从`触发场景`、`Trigger`、`Use this skill when`等section）
2. 与frontmatter description对比
3. 将缺失的关键词补入description
4. 保持description长度合理（不超过500字符），优先保留高频/高区分度词

**验收标准**: 每个skill的description覆盖body触发词的≥90%

**QA场景**:
1. 修改前，对5个代表性skill运行evaluate_triggers.py记录baseline trigger_pass_rate：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path packs/research-skill-pack/.opencode/skills/research-synthesis --json
   ```
2. 修改后，对同样5个skill重新运行，确认trigger_pass_rate不低于修改前
3. 对全部54个skill逐一运行auto-generate模式验证（无需手写test-file，脚本自动从description生成用例）：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path packs/research-skill-pack/.opencode/skills/<skill-name> --json --siblings packs/research-skill-pack/.opencode/skills
   ```
4. **预期结果**: 所有skill verdict为`PASS`，无新增cross-trigger冲突

### 2.2 其他6个pack的skills修复

**范围**: 
- `packs/petfish-companion-skill/` — companion、marketplace-connector等
- `packs/anti-sycophancy-calibration-pack/` — anti-sycophancy-calibration
- `packs/petfish-style-skill/` — petfish-style-rewriter
- `packs/opencode-course-skills-pack/` — 全部课程skills
- `packs/repo-deploy-ops-skill-pack/` — 全部部署运维skills
- `packs/fish-trail/` — fish-trail

**方法**: 同2.1

**验收标准**: 所有pack的所有skill description覆盖body触发词的≥90%

**QA场景**:
1. 对每个pack中的每个skill运行evaluate_triggers.py auto-generate模式：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/skill-trigger-evaluator/scripts/evaluate_triggers.py --path <pack>/.opencode/skills/<skill-name> --json
   ```
2. **预期结果**: 所有skill verdict为`PASS`（trigger_pass_rate ≥ 0.80）

### 2.3 强化全部7个pack的AGENTS.md

**范围**: 7个pack的AGENTS.md

**动作**:
- 将"推荐"/"建议"措辞升级为"必须"/"MUST"
- 添加明确的意图分类 → skill路由映射表
- 添加冲突解决规则（当多个skill可能匹配时的优先级）

**验收标准**: 每个AGENTS.md包含≥3条MUST级别路由规则和冲突解决指引

**QA场景**:
1. 修改完成后，对每个pack的AGENTS.md执行（PowerShell）：
   ```powershell
   (Select-String -Path "packs/<pack-name>/AGENTS.md" -Pattern "必须|MUST" -AllMatches).Matches.Count
   ```
2. **预期结果**: 每个pack返回值 ≥ 3

---

## Phase 3: 防护网 (P2) — 自动化检查防止复发

### 3.1 skill-lint 增加 description-body 覆盖检查

**文件**: `packs/petfish-companion-skill/.opencode/skills/skill-lint/scripts/lint_skill.py`

**动作**: 新增lint规则：
- 提取SKILL.md body中的触发关键词（从`触发场景`、`Trigger`、`Use this skill when`等section）
- 与frontmatter description对比
- 覆盖率<80%时报warning级别finding，<50%时报error级别finding
- 在`--json`输出中，findings数组增加type为`trigger-coverage`的条目，包含`coverage_pct`字段

**验收标准**: 对一个已知有缺口的skill运行lint，能检出覆盖率不足

**QA场景**:
1. 准备一个测试用的SKILL.md：将research-router的SKILL.md复制到临时目录，故意从description中删除"research"和"研究"关键词
2. 运行lint（PowerShell，使用$env:TEMP代替/tmp）：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/skill-lint/scripts/lint_skill.py --path $env:TEMP/test-skill --json
   ```
3. **预期结果**: JSON输出的findings数组中包含severity为`WARNING`或`ERROR`的条目，message包含"trigger"或"coverage"字样，且lint score因此降低
4. 对一个description已完善的skill（如修复后的research-router）运行同一命令：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/skill-lint/scripts/lint_skill.py --path packs/research-skill-pack/.opencode/skills/research-router --json
   ```
5. **预期结果**: 无trigger-coverage相关的warning或error finding

### 3.2 quality-gate 集成覆盖检查

**文件**: `packs/petfish-companion-skill/.opencode/skills/quality-gate/scripts/run_gate.py`

**动作**: 
- gate已通过调用lint_skill.py间接获取lint结果；3.1中lint新增的trigger-coverage findings会自动流入gate的lint阶段
- 在`make_decision()`函数中，当lint findings包含trigger-coverage类型的ERROR级别finding时，将decision从`PASS`降级为`CONDITIONAL`
- 不引入新的output字段，复用现有`decision`枚举（大写`PASS`/`CONDITIONAL`/`FAIL`）和`lint.findings`结构

**验收标准**: 对一个覆盖率不足的skill运行gate，decision输出为`CONDITIONAL`

**QA场景**:
1. 使用3.1中准备的低覆盖率测试SKILL.md
2. 运行gate（PowerShell）：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/quality-gate/scripts/run_gate.py --path $env:TEMP/test-skill --json
   ```
3. **预期结果**: JSON输出中`decision`字段为`"CONDITIONAL"`（大写），`lint.finding_count` > 0
4. 对一个覆盖率正常的skill运行gate：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/quality-gate/scripts/run_gate.py --path packs/research-skill-pack/.opencode/skills/research-router --json
   ```
5. **预期结果**: trigger-coverage规则不影响原有decision判定（若其他指标均通过，decision仍为`"PASS"`）

### 3.3 根AGENTS.md添加对齐纪律

**文件**: `AGENTS.md` (root)

**动作**: 在"Schema与SKILL.md对齐纪律"section之后添加"Description与Body触发词对齐纪律"section：
- 规则：修改SKILL.md body触发词时，同步更新description
- 规则：新建skill时，description必须覆盖body触发词的≥80%
- 引用Issue #91作为教训来源

**验收标准**: AGENTS.md中存在该section

**QA场景**:
1. 修改完成后验证（PowerShell）：
   ```powershell
   Select-String -Path "AGENTS.md" -Pattern "Description与Body触发词对齐"
   ```
2. **预期结果**: 返回匹配行，确认section存在

---

## Phase 4: 架构改进 (P3, Optional)

### 4.1 Companion Gateway Skill Sense增强

**文件**: `packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py`

**动作**: 在TRIGGERS字典中，为research pack补充缺失的中文高频关键词（如"研究"、"帮我研究"），作为Companion Gateway Tier 1白名单的补充保护层。

**优先级**: 低。Phase 1-3已解决根本问题，Phase 4是额外保险。

**QA场景**:
1. 修改TRIGGERS后，运行catalog_query.py验证：
   ```powershell
   uv run packs/petfish-companion-skill/.opencode/skills/petfish-companion/scripts/catalog_query.py --query "帮我研究一下这个问题"
   ```
2. **预期结果**: 输出中包含research pack的推荐

---

## 执行顺序与依赖

```
Phase 1 (P0, 紧急) ─→ Phase 2 (P1, 批量) ─→ Phase 3 (P2, 防护) ─→ Phase 4 (P3, 可选)
     │                      │                      │
     └─ 无依赖              └─ 依赖Phase 1完成      └─ 依赖Phase 2完成
```

- Phase 2依赖Phase 1：Phase 1建立修复模式和trigger eval baseline，Phase 2按同一模式批量执行
- Phase 3依赖Phase 2：lint/gate检查需要在description已修复后验证检测逻辑的准确性（用修复前后的对比来确认检测有效）
- Phase 4独立于Phase 3：可选执行

## 版本与发布

- 所有修复在`dev`分支进行
- Phase 1+2完成后可发布一个patch release（v0.10.9）
- Phase 3完成后可发布另一个patch release（v0.10.10）
- 遵循"每次合并master = 一次release"原则

## 风险

1. **Description长度膨胀**: 补入过多关键词可能导致description过长、语义模糊。缓解：设置500字符上限，优先高区分度词。
2. **误触发增加**: 扩大触发词覆盖可能增加false positive。缓解：每个修改后的skill运行evaluate_triggers.py验证，关注cross-trigger冲突。
3. **批量修改引入错误**: 54个文件批量修改可能引入笔误。缓解：逐个检查diff，修改后运行lint验证SKILL.md格式完整性。
