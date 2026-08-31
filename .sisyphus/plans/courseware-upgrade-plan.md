# 计划：Courseware能力升级——借鉴OpenMAIC（项目2）

> 状态：草案 → Council已审 → **Momus ACCEPT（2026-08-31，引用全量复核通过）**
> 依据：
> - 基线：course pack盘点（15 skills/10 commands/8 agents；流程治理强、内容质量杠杆弱，12项缺口）
> - 借鉴源：OpenMAIC v1.0.0解剖（THU-MAIC；REVIEW文档+代码库探查）——五层质量执行体系：DSL校验器→JSON修复→outline-constraints.json机器约束→技能内过程门→eval harness（LLM-as-judge+exit-code门禁）
> - 不抄清单（REVIEW §3教训）：默认串行、非流式长生成、JSON-in-text+repair循环、全量历史重放、压缩死配置、30KB提示词+字节级重复、静态/动态混排毁缓存

## 1. 基线诊断（一句话）

**流程治理强（8段目录/QA-QC门禁/师生分离4层机制），内容质量杠杆弱**——最致命缺口：教学法浅（teaching-flow-patterns.md仅3条一行模式）、测评种类近零（大纲模板仅一行"评估方式"）、QA是正则不是语义（qa_scan无法判内容质量，"满是含糊填充物的课程只要文件名对就能过QA"）、无evals、无反馈闭环。

## 2. 借鉴映射（OpenMAIC资产 → 缺口 → 移植方式 → 分期）

| # | OpenMAIC模式（证据） | 我们的缺口 | 移植方式 | 分期 |
|---|---|---|---|---|
| C1 | outline-constraints.json机器可检约束（skills.ts `checkScenesAgainstSkill`；违规作为diagnostics返回agent自纠而非硬失败） | QA无机器约束 | 约束schema+课程类型预设；qa_scan新检查项 | P0 |
| C2 | curriculum-planner双门（Gate1澄清2-3轮+Gate2显式sign-off才开工） | orchestrator无确认门 | 移植进course-development-orchestrator | P0 |
| C3 | stage-design构建序列+完成清单（plan→roster→逐页生成→list验证；"未persist不算完成"） | 内容质量靠LLM自觉 | course-content-authoring增done-checklist+qa_scan结构完备性检查 | P0 |
| C4 | 教学法内嵌模板（requirements-to-outlines/system.md含教学设计原则+语言推断规则，386行结构化教学法） | 无教学科学参考层 | pedagogy-compact.md等references层（按需读，不进SKILL.md正文——避开30KB教训） | P1 |
| C5 | 题型系统（quiz单选/多选/短答+AI评分；PBL里程碑+可交付物） | 测评种类近零 | 新skill：course-assessment-design | P1 |
| C6 | 23个教学技能（deep-research/PBL/职业教学/K12素养） | 教学法深度不足 | 经项目1挖掘链挖curriculum-planner/stage-design改编；roadmap已列的course-eval-design落地 | P1-P3 |
| C7 | eval harness（scenarios+judge+exit-code门禁；orchestration回归/E2E率门禁） | 无evals（roadmap Phase3未做） | evals/目录+judge.py+runner.py+CI接入 | P2 |
| C8 | golden基线（eval scenarios含ground truth） | 无质量度量锚点 | 2门golden courses回归fixture | P2 |
| C9 | Deep Interactive五类交互件（3D/仿真/游戏/思维导图/在线编程） | labs纯文本 | 交互教学件作为lab资产类型（远期，概念借鉴） | P3 |
| C10 | 素材管线（PDF/音视频→提取→内容，AliDocMind/MinerU/ffmpeg+ASR） | reference-document-review弱 | doc-reader pack深度集成 | P3 |
| C11 | 授课后迭代（无直接对应，属我们自补） | 无反馈闭环 | course-delivery-review skill：反馈→QC循环 | P3 |

## 3. 目标与成功标准

- **目标**：课程产出从"结构合规"升级到"教学有效"——约束机器可检、教学法有据可依、测评成体系、质量可度量可回归。
- **成功标准**：
  1. 构造反例课程（无测评/模块数越界/课时超带宽）→ qa_scan必报（约束违规可复现）
  2. golden course回归：judge五维（目标对齐/教学法覆盖/测评有效性/师生分离/结构完整）均值≥4.0/5；故意破坏教学法规则的变体判分显著下降（≥1.0分差）
  3. 端到端效率：3模块课程（大纲+内容+labs+双pack+QA/QC）较基线人工计时降≥30%
  4. 新增内容全部过skill-lint（trigger-coverage≥80%）+ pack过quality-gate

## 4. 分阶段任务

### P0 快赢（2-3天，无新skill，纯pack内增强）

**C1 outline-constraints机器检查**
- 新增：`.opencode/skills/course-quality-assurance/references/outline-constraints/`
  - `schema.json`：约束字段定义——`module_count{min,max}`、`lab_ratio{min,max}`、`required_assessment_types[]`、`total_hours{min,max}`、`lessons_per_module_max`、`first_module_type`（学OpenMAIC的OutlineConstraints字段风格：范围+必含，不是等值硬约束）
  - 预设**先做1个**：`standard-training.json`（跑通全链路）→ 再扩workshop/k12/vocational
- `docs/00-project/course-type.yaml`：课程类型声明（orchestrator在Gate2前引导用户确认时落盘）
- `qa_scan.py`新增check#9：读course-type→加载约束→校验`docs/01-outline/`实际→violation映射severity（module_count越界=blocker；lab_ratio=major；其余=minor）
- `course-outline-design/SKILL.md`：产出大纲时自检约束（生成侧预防优于检测侧发现）

**C2 双门禁**
- `course-development-orchestrator/SKILL.md`：
  - **Gate1=执行帧澄清**：最多3轮，每轮单问（用question工具），问题从**澄清问题库**选（新增references/clarification-bank.md，按课程类型分组的8-12个高价值问题：受众基线/成功行为定义/课时约束/测评偏好/素材存量等）
  - **Gate2=大纲sign-off**：大纲完成后显式用户确认（"确认开始内容创作"），未确认不得路由content-authoring
  - 与现有5个review gates整合：Gate1/2置于Gate 1(requirements)与Gate 2(architecture)之间细化

**C3 authoring完成清单**
- `course-content-authoring/SKILL.md`新增Done-Checklist节：目标可测（动词+可观察行为）/前置明示/≥1个worked example/≥1个misconception暴露/练习带评分标准/小结回扣目标/时长预算对齐；**"未写入docs/02-content = 未完成"**（OpenMAIC"未persist不算完成"规则移植）
- `qa_scan.py`新增check#10：逐lesson正则查结构要素标记存在性（目标/示例/练习/时长四要素的显式section标记）→缺失=major；**诚实命名：结构完备性检查，不号称语义质量评估**

### P1 质量层（1周）

**C4 教学法参考层**（references，按需读）
- `course-content-authoring/references/pedagogy-compact.md`：Bloom动词表（六层×可测动词）/认知负荷三原则（内在/外在/关联，各≤10行+应用示例）/样例-练习配比（worked example→completion→faded→independent渐退）/误解前置策略/检索练习间隔
- `course-outline-design/references/assessment-planning.md`：形成性/总结性配比框架、题型-目标匹配矩阵（记忆→MCQ；理解→短答；应用→lab；分析→project）

**C5 course-assessment-design新skill**
- 9字段测评设计模式（复用lab-design结构风格）：目标绑定（每题挂Bloom层）/题型（MCQ/多选/短答/rubric评分项/项目里程碑）/题干规范（单一考点/无歧义干扰项）/答案与评分标准（→instructor-pack）/题面（→learner-pack，师生分离机制复用）/难度分布/时限/抽样复测题
- 命令`/course-assessment`；agent无需（qa-auditor可扩检查）
- **9触点核对**：pack manifest（skill_count/contents）+ README pack表 + docs/agent-install示例 + website计数 + zh README（新增skill属pack内容变更，非新pack，触点#2/#10不适用）
- skill-lint + trigger-coverage（description须含"测评/assessment/quiz/题库/考试"等触发词）+ quality-gate

**C6 ppt集成桥**
- 新命令`/course-slides`（course pack commands/）：lesson.md→slide outline JSON（每lesson一节：标题/要点/图示建议/讲者备注）→调用ppt-writer build_deck→qa_deck→产出`docs/02-content/<module>/slides/<lesson>.pptx`
- 能力检测优雅降级：ppt pack未装→提示`/petfish install ppt`命令，不硬失败

### P2 度量层（1周）

**C7 evals harness**
- `evals/`目录（pack内）：`scenarios/*.json`（课程brief+课程类型+期望约束+教学法规则清单）、`judge.py`（LLM-as-judge：五维rubric 1-5分+总体判定；judge模型可配置；**温度0+judge prompt版本固定**；**无LLM环境降级**：仅跑静态约束检查+结构检查，judge项标skip）、`runner.py`（跑outline+首模块生成→judge→report.md+exit code：阈值不达=1）
- CI接入：repo workflow在course pack路径变更时触发（复用现有CI结构）

**C8 golden courses**
- 2门基准：1门standard-training（如"Git入门3模块"）+1门workshop；含期望大纲结构、约束期望值、教学法检查点——作为回归fixture与C7场景种子

### P3 远期（独立排期）

- C9交互教学件：mindmap/quiz-HTML/code-playground三类先做（借鉴OpenMAIC widget概念，产出为`docs/03-labs`资产+learner-pack引用）
- C10素材管线：doc-reader集成（参考资料→结构化课程输入流水线）
- C11反馈闭环：course-delivery-review skill（授课反馈/测验成绩分布→QC循环迭代内容）
- C6补充：OpenMAIC course skills经项目1挖掘链引入改编

## 5. 风险与缓解

| 风险 | 缓解 |
|---|---|
| C1约束过严扼杀课程形态灵活性 | 约束是范围+必含非等值；允许`deferred`项记录（QC状态模型复用）；预设文件可被项目级override |
| C7 LLM-judge方差损害回归可信度 | 温度0+prompt版本钉死+双评仲裁机制（分歧>1分时第三次仲裁；借鉴calibrate pack rubric-first）+ 无LLM降级模式保底 |
| C5新skill触发词与其他skill冲突（如与course-lab-design） | skill-trigger-evaluator跑sibling冲突检测；description聚焦"测评/考试/题库"独占域 |
| C6依赖ppt pack形成跨pack耦合 | 桥接命令做能力检测+降级提示；不修改ppt pack本身；接口=slide outline JSON文件（松耦合） |
| pack体积膨胀（references堆积） | 参考层按需读设计（SKILL.md只留一行索引）；年度清点references使用率（skill-usage-tracker） |
| 双门禁增加交互摩擦惹恼老用户 | Gate1允许"跳过澄清"显式选项（记录skipped状态）；Gate2一次性确认非逐模块 |

## 6. 边界（不做）

- 不自建幻灯片渲染引擎（C6桥接ppt pack，不重复造）
- 不做视频/音频/TTS管线（OpenMAIC媒体栈工程量大且非core，远期再议）
- 不做多agent课堂编排（OpenMAIC director-graph属运行时产品形态，我们是内容生产工具链）
- 不改QA/QC既有severity/status模型（只增检查项，不动模型）

## 7. Council审查记录（5+1，2026-08-31）

工作流依据：本仓库`agents-rules/anti-sycophancy.md`的council-thinking规范。

| 顾问 | 判断 | 裁决 |
|---|---|---|
| 反对者 | C3的qa_scan正则查"结构要素"仍是正则——别包装成语义质量；命名与文档必须诚实 | **采纳**：check#10命名"结构完备性检查"，SKILL.md明示其边界；成功标准1/2的措辞已对应（约束可复现≠语义质量） |
| 本质思考者 | 课程质量的真瓶颈在**输入质量**——执行帧（受众/目标）质量决定下游一切；Gate1的澄清问题库才是最高杠杆资产 | **采纳**：C2新增clarification-bank.md为P0交付物（原计划无），Gate1从"流程"升格为"资产" |
| 机会挖掘者 | outline-constraints机制可反哺所有pack（研究pack的brief质量约束等） | **删除**（超本计划范围；模式备忘记入本节即可，不立项） |
| 局外人 | evals的judge模型成本谁付？本地无API key时CI怎么办？ | **采纳**：C7补无LLM降级模式（静态检查保底）+judge模型可配置；已写入 |
| 执行者 | C1别一次写4个课程类型预设——先1个跑通qa_scan全链路再扩 | **采纳**：C1明确"先standard-training后扩"；已写入 |
| 仲裁结论 | 删1条、采纳4条；最高杠杆变更：clarification-bank成为P0交付物、C3诚实化命名、C7降级模式、C1渐进扩展 | 已整合 |

## 8. 待Momus裁决项

1. C2双门禁与现有5 review gates的整合深度（替换or细化插入）——计划选"细化插入"，是否造成双轨混乱
2. C7 judge的评分锚定：五维rubric的1-5分锚点定义是否足够客观（需Momus判断rubric文本是否进入P0先行评审）
3. C5新skill vs 扩展现有course-lab-design（测评与lab边界：项目型测评归谁）——计划选新skill
4. P0三件（C1/C2/C3）是否真正可在2-3天完成（工作量估计的现实性）

## 9. 我不知道的部分

- golden course的judge基线分数分布（首跑后才能定回归阈值，P2中期校准）
- ppt-writer对"lesson→slide outline"输入格式的实际接受度（C6实施前需一次手动链路验证）
- K12/vocational约束预设的合理默认值（无历史课程数据，需领域专家一轮校准——实施时找用户确认）
