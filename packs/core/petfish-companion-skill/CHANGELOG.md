# CHANGELOG — petfish-companion-skill

所有重要变更记录在此。版本号遵循语义化版本（仅pack内部版本，独立于PEtFiSh项目版本）。

## [1.3.0] — 2026-06-18

### Added
- **Gateway Step 2.6: Reading-Notes Check** — agent读文件前先查笔记，避免重复阅读
- **Staleness检测** — file_mtime + file_size stat比对（1次stat调用，不读内容）
- **Gateway Trace可观测性** — 每轮回复开头输出结构化trace行 + 追加JSONL
- **verify_trace.py** — trace验证脚本（纯stdlib）
- **reading_notes_lint.py** — 阅读笔记JSONL验证器（纯stdlib）
- **SKILL.md Section 10** — 阅读笔记完整行为规范（何时记/不记/检索/staleness/格式）

### Changed
- Gateway Trace格式增加 `step2.6=notes:hit/total` 字段
- pack AGENTS.md增加阅读笔记行为指令 + staleness检测说明

### QA
- verify_trace.py: 2/2 trace entries PASS
- reading_notes_lint.py: 3/3 valid entries PASS, 4/4 invalid entries rejected

## [1.2.0] — 2026-06-18

### Added
- **Contract-Driven Gateway Atoms** — 5个Gateway步骤形式化为机制原子
  - step0-mode-read: depth/rigor schema校验
  - step1-topic-check: topic relation分类
  - step1.5-failure-signal: 失败信号regex检测
  - step2-skill-sense: skill缺口关键词检测
  - step2.5-anti-sycophancy: 评价性问题检测（detection级）
  - gateway-macro: 跨步骤carried obligations
- **6个契约文件**（contracts/）+ **6个fixture文件**（fixtures/）+ **6个验证器**（validators/）
- **references/contract-methodology.md** — 完整方法论 + claim boundary
- **实施纪律（最小代码原则）** — 先读后写 + 六问，编码到AGENTS.md（用户侧强制）

### Changed
- `fish-calibrate` TRIGGERS扩展：新增"好吗"、"合理"、"你觉得"等评价性关键词
- 根AGENTS.md + pack AGENTS.md增加实施纪律 + 契约驱动行为章节

### Fixed
- **修复循环实证**：Phase 3验证器捕获calibrate TRIGGERS缺失中文评价性问句模式 → 修复 → 回归通过

### QA
- 42/42 contract validator checks PASS
- skill-sense eval回归: 20/20 PASS (accuracy 1.0000)
- failure-signal eval回归: 15/15 PASS (accuracy 1.0000)
- install管线验证: shutil.copytree递归分发contracts/fixtures/validators

## [1.1.0] — 2026-06-10

### Changed
- 随v1.7.0项目release发布，companion pack初始版本记录
