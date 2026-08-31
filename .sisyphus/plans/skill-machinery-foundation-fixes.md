# 计划：技能机制地基修复（两项目共享前置）

> 状态：草案 → Council已审 → **Momus ACCEPT（2026-08-31，引用全量复核通过）**
> 依据：2026-08-31四路并行研究（PEtFiSh技能机制盘点/OpenCode平台能力/OpenMAIC解剖/course pack基线）
> 上游文档：`.sisyphus/plans/dynamic-skill-loading-plan.md`（本计划是其P0的前置展开，独立可发布）

## 1. 背景与证据

动态技能加载（项目1）与courseware升级（项目2）都依赖技能生命周期机制。盘点发现6处地基缺陷，不修复则上层建筑的自动化链条必然断裂：

| # | 缺陷 | 证据位置 | 对上层的影响 |
|---|------|---------|------------|
| F1 | 市场索引键错位：`publish_pack.py`写`packs`键，`marketplace_search.py`读`skills`键（L156），且publish只保留不填充`skills`（L196-204）→ 新发布pack对搜索不可见 | 两文件 | 自动挖掘链的"搜索"环节失明 |
| F2 | 无skill粒度安装：`install.py`仅pack粒度（build_parser L2671-2754无`--skill`），单技能无安装路径 | install.py | 挖掘产物（单skill）无法落地 |
| F3 | 触发词表双份drift：`companion-gateway.ts`硬编码`SKILL_TRIGGERS`（L60-70）与`catalog_query.py TRIGGERS`（L73-241）已分叉（TS多`writing`域，关键词集不同） | 两文件 | 索引注入层的匹配质量无保障 |
| F4 | 文档矛盾：`agent-install.md` L155-169说必须重启；`fish-init/SKILL.md` L585-596与`fish-brain/SKILL.md` L140说无需重启；fish-init §11引用不存在的`skill-registry` MCP工具和已退役的remote-install命令 | 三处文档 | 动态加载的session边界语义混乱 |
| F5 | `/petfish suggest`名不副实：文档称"基于项目结构"，实现是"列出所有未装"（`suggest_packs` L829-854） | catalog_query.py | 任务感知推荐的入口失效 |
| F6 | pack版本冻结惯性：companion自6/18停在1.3.0期间内容多次变更（v3.2.0已修当前值，但流程上缺 bump习惯） | 新发布门禁第6项 | 不bump则非--force升级与check-updates失明 |

## 2. 目标与成功标准

- **目标**：搜索命中全量市场pack；单skill可安装可卸载；触发词单一事实源；文档口径统一；suggest具备项目感知；全部随一个patch release（v3.2.1）发布。
- **成功标准**：
  1. `uv run marketplace_search.py --query <任一market pack名> --json` 能命中该pack
  2. 干净目录`install.py --pack companion --skill fish-market`后仅`fish-market` skill落地，registry记录部分安装，卸载对称
  3. 删除gateway硬编码表后，`step2`推荐行为不回退（对照现有gateway契约测试）
  4. 三处重启文档口径一致（"需重启，skill于session启动时加载"）
  5. 在含`pyproject.toml`的空项目跑`/petfish suggest`，research/code类pack排名高于course
  6. `pre_release_check.py` 6/6 PASS（含新版本漂移门禁）

## 3. 依赖关系

```
F3(单一事实源) ──┬──> 项目1-P1.2(发现块注入)
F2(--skill安装) ──┴──> 项目1-P2.3(vault→持久安装)
F1(索引键) ────────> 项目1-P2.1(自动搜索)
F4/F5/F6 ──────────> 独立，无下游依赖
```
建议实施顺序：F3 → F2 → F1 → F5 → F4 → F6（F3/F2解锁后续项目，优先）。

## 4. 任务分解

### F3 触发词单一事实源（最高优先）
- `scripts/generate_skill_index.py`：
  - 新增合并源：`catalog_query.py`的TRIGGERS（import或读JSON导出）+ market index `packs`键的skill清单 + community注册表
  - schema扩展：每skill条目`{name, description, triggers[], parallel_safe, source: installed|market|community|vault}`
  - 保持向后兼容：旧字段不删，新增可选字段
- `companion-gateway.ts`（同步改`lib/plugin/`副本）：
  - 删除`SKILL_TRIGGERS`硬编码（L60-70），改为读`.opencode/skill-index.json`的`triggers`聚合匹配
  - 兼容旧格式：index缺失时静默降级为无关键词匹配（仅description包含匹配）
- `catalog_query.py`：TRIGGERS保留为唯一写侧来源，加注释声明
- 验证：gateway契约测试`test_skill_sense.py`新增fixture（新index格式+旧格式）

### F2 skill粒度安装
- `install.py`：
  - `build_parser`：`--skill <name>`（action=append，可多次）
  - skill→pack解析：优先本地packs manifests，fallback market index
  - `install_single_pack`：skills过滤模式——只复制目标skill目录；L1规则/插件/AGENTS.md照常（pack级基础设施一次到位）
  - registry：`installed-packs.json`的pack条目新增`installed_skills`（list）；**向后兼容**：无该键视为全装
  - uninstall：识别`installed_skills`，仅删除列出的skill
- 验证：干净目录端到端install/uninstall + 旧格式registry读取测试

### F1 市场索引键修复（双侧）
- `marketplace_search.py` `search_petfish_market`：读`packs`键（与installer对齐）∪`skills`键（历史兼容），按name去重
- `publish_pack.py` `generate_index_json`：同步填充`skills`摘要条目（从各pack的skills字段生成，保持双键完整）
- 注：`petfish-market`是独立仓库，publish侧改动只影响后续发布；搜索侧改动立即生效

### F5 suggest项目感知
- `catalog_query.py` `suggest_packs`：
  - 项目信号扫描（纯标准库，~60行）：`pyproject.toml/package.json/go.mod/Cargo.toml`→code；`Dockerfile/.github/workflows`→deploy；`docs/01-outline`等课程目录特征→course；`.petfish/notes`→research/petfish；等8-10个信号
  - 信号→pack权重表（新增模块级常量`PROJECT_SIGNALS`）
  - 排序：信号命中×缺失状态；无信号时保持现状行为
- 同步修正`fish-brain SKILL.md` §4.3描述与实现一致

### F4 文档口径统一
- `fish-init/SKILL.md`：L585-596改为需重启表述；§11的`skill-registry list_available_packs`引用改为skill-index.json读取并注明"该MCP仅dev工作区可用，用户项目不保证部署"（Momus核实：MCP在dev仓库存在，但fish-init面向用户项目分发，引用无可用性保证）；remote-install命令（L453/459，Momus核实仓库中已无此文件）→`install.py`统一命令
- `fish-brain/SKILL.md` L140：同口径修正
- 变更属pack内容→计入F6版本bump

### F6 版本bump与发布
- companion（F3/F4/F5改其SKILL.md与catalog_query/marketplace_search）+1 minor；**toolchain必bump**（Momus指出：F1改publish_pack.py属toolchain pack内容，原计划遗漏）；按新漂移门禁逐pack核对兜底
- 走dev→PR→pre_release_check→master→release v3.2.1标准流程

## 5. 风险与缓解

| 风险 | 缓解 |
|---|---|
| F2 registry格式变更破坏旧安装 | 无`installed_skills`键=全装的向后兼容语义；uninstall对旧格式全删 |
| F3 gateway改读文件引入每轮IO | index只在session启动读一次缓存（复用gateway现有GATEWAY_STATE_DIR模式） |
| F1 改publish影响已发布索引 | 搜索侧∪读取立即兼容存量；发布侧只影响增量 |
| F5 信号误判（如pyproject但实为文档项目） | 信号仅影响排序权重不影响安装；输出中展示判定依据供用户否决 |

## 6. 边界（不做）

- 不做MCP server/plugin新组件（属项目1-P1）
- 不做community注册表播种（属项目1-P3）
- 不做mine_repo语义化（属项目1-P3）
- 不重构install.py整体结构（只做最小增量）

## 7. Council审查记录（5+1，2026-08-31）

工作流依据：本仓库`agents-rules/anti-sycophancy.md`的council-thinking规范（skill本体未装于本工作区，规则文件已注入）。

| 顾问 | 判断 | 裁决 |
|---|---|---|
| 反对者 | F3把TRIGGERS合并进skill-index.json后，market/community的skill没有触发词数据（TRIGGERS只覆盖本地pack）——合并是假单一源 | **采纳**：F3范围收窄为"本地pack触发词单一源"；market条目的triggers允许为空，匹配退化为description匹配，P1再补市场侧触发词生成 |
| 本质思考者 | 真瓶颈是"发现质量"而非"数据源"——gateway最终只吃top-N，匹配排序算法（关键词命中数？加权？）未定义 | **采纳**：F3补充匹配规格：`score = 精确关键词命中×3 + 子串命中×1`，同分按description长度升序（短优先，省token） |
| 机会挖掘者 | F2的`installed_skills`可顺势记录安装时间/来源，为P3的usage统计铺路 | **删除**（有价值但超范围，记入项目1-P3备忘） |
| 局外人 | 三个修复(F1/F3跨repo、F2改注册表格式)各自可独立回滚吗？ | **采纳**：明确每个F项独立commit独立可revert；F2的registry兼容逻辑单独测试用例 |
| 执行者 | F5的信号扫描别手写——init_project.py已有项目特征探测逻辑可复用 | **采纳**：F5先查init_project.py可复用函数，避免二造 |
| 仲裁结论 | 删1条、采纳4条；计划范围收窄（F3本地源）、补匹配规格、补回滚单元、补复用检查 | 已整合进上文 |

## 8. 待Momus裁决项

1. F2的pack级基础设施（L1规则/插件）在`--skill`模式下是否照装——计划选择"照装"（一次到位），是否引入过重副作用？
2. F1双侧修复的发布顺序（搜索侧先行 or 同release）。
3. F3匹配规格的score权重是否需要先做小样本评测再定。

## 9. 我不知道的部分

- OpenCode未来版本是否会原生支持skill热加载（若支持，F3/F4的session边界语义需重写）——watch `anomalyco/opencode`的skill watcher issue
- market索引中历史`skills`键的存量数据规模（需发布侧一次全量重生成确认）
