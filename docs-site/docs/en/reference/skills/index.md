# Skills

PEtFiSh includes **104 skills** across all packs.

| Skill | Pack | Description |
|---|---|---|
| [`fish-trail`](fish-trail.md) | context | topic_detect is high risk, users ask to 整理/切换/合并/归档话题 or 清空上下文, or mention topic governance/上下文污染/继承... |
| [`fish-brain`](fish-brain.md) | companion | > |
| [`fish-market`](fish-market.md) | companion | > |
| [`quality-gate`](quality-gate.md) | toolchain | > |
| [`repo-skill-miner`](repo-skill-miner.md) | toolchain | > |
| [`skill-author`](skill-author.md) | toolchain | > |
| [`skill-description-optimizer`](skill-description-optimizer.md) | toolchain | > |
| [`skill-lint`](skill-lint.md) | toolchain | > |
| [`skill-publish`](skill-publish.md) | toolchain | > |
| [`skill-security-auditor`](skill-security-auditor.md) | toolchain | > |
| [`skill-trigger-evaluator`](skill-trigger-evaluator.md) | toolchain | > |
| [`skill-usage-tracker`](skill-usage-tracker.md) | toolchain | > |
| [`project-initializer`](project-initializer.md) | init | Initialize/scaffold/bootstrap AI-agent workspaces, generate AGENTS.md/README/.opencode/docs/tasks/qa... |
| [`doc-reader`](doc-reader.md) | doc-reader | Convert PDF/DOCX/XLSX/HTML/PPTX/EPUB to Markdown for reading, review, and extraction. Use when user ... |
| [`drawio-radar-chart`](drawio-radar-chart.md) | drawio | >- |
| [`fish-reflection`](fish-reflection.md) | reflect | 结构化反思与经验沉淀。Use when 反思, reflect, what went wrong, lessons learned, 复盘, 经验总结, 失败分析, root cause analys... |
| [`council-thinking`](council-thinking.md) | calibrate | 五人顾问团多视角对抗式判断，用于方案评估、战略判断、产品定位、技术路线、研究设计等复杂决策。5个logical subagents（反对者/本质思考/机会挖掘/局外人/执行者）+Arbiter删除弱观... |
| [`anti-sycophancy-calibration`](anti-sycophancy-calibration.md) | calibrate | For 评审, 评价, 批判, review, critique, feedback, judgment, decision, evaluation, calibration, sycophancy,... |
| [`course-content-authoring`](course-content-authoring.md) | course | Create, revise, expand, compress, or review course chapter content, including explanations, examples... |
| [`course-development-orchestrator`](course-development-orchestrator.md) | course | Drive course projects end to end — plans, outlines, content, labs, learner/instructor materials, QA,... |
| [`course-directory-structure`](course-directory-structure.md) | course | Create, reorganize, normalize, or audit a course project directory tree, |
| [`course-lab-design`](course-lab-design.md) | course | Create, modify, review, or operationalize course labs, exercises, demos, |
| [`course-methodology-playbook`](course-methodology-playbook.md) | course | Reusable course-development methods, review heuristics, historical conventions, |
| [`course-outline-design`](course-outline-design.md) | course | Create, modify, or review a course outline, syllabus, chapter tree, hour |
| [`course-quality-assurance`](course-quality-assurance.md) | course | Structured course QA: completeness checks, consistency review, pedagogical |
| [`course-quality-control-reporting`](course-quality-control-reporting.md) | course | Turn QA findings into concrete quality control actions, remediation plans, |
| [`development-plan-governance`](development-plan-governance.md) | course | Create, revise, or review a course development plan, including milestones, |
| [`drawio-course-diagrams`](drawio-course-diagrams.md) | course | Course-related diagrams in draw.io form, including architecture diagrams, |
| [`instructor-reference-materials`](instructor-reference-materials.md) | course | Instructor-only assets such as teaching notes, speaking points, timing |
| [`learner-materials`](learner-materials.md) | course | Learner-facing course assets such as handouts, reading packs, worksheets, |
| [`markdown-course-writing`](markdown-course-writing.md) | course | Polished Markdown artifacts for course plans, outlines, lesson notes, lab guides, learner handouts, ... |
| [`reference-document-review`](reference-document-review.md) | course | Read, normalize, compare, extract, or convert reference materials in PDF, |
| [`skill-reference-discovery`](skill-reference-discovery.md) | course | Search GitHub/public sources for high-quality agent skills, run skill reference scans, compare candi... |
| [`ppt-reader`](ppt-reader.md) | ppt | Read/inspect/summarize/audit/compare PPT/PPTX, extract slide inventory (titles, structure, notes, co... |
| [`ppt-writer`](ppt-writer.md) | ppt | Create/rewrite/restructure/update/validate/export PPT/PPTX decks (课件、提案、汇报、论文、技术方案). Trigger for 从Ma... |
| [`generate-test-cases`](generate-test-cases.md) | testdocs | Generate test cases/test matrix for the current repo: API/CLI/UI/SDK/service, smoke/regression/accep... |
| [`generate-usage-docs`](generate-usage-docs.md) | testdocs | Generate grounded usage docs from the current repo: README, Quick Start, configuration, usage, API/C... |
| [`de-ai-detector`](de-ai-detector.md) | petfish | Detect AI writing patterns in Chinese or English text. Use when the user asks to 检测AI味 / 检测AI痕迹 / 去A... |
| [`petfish-style-rewriter`](petfish-style-rewriter.md) | petfish | Rewrite, polish, humanize, de-AI, or formalize Chinese or English technical, academic, business, cou... |
| [`style-extractor`](style-extractor.md) | petfish | Extract personal writing style from samples to create a style profile. Analyzes sentence patterns, v... |
| [`deployment-executor`](deployment-executor.md) | deploy | 按已确认部署计划执行上线/升级/重部署：优先repo现有Docker/compose/systemd/k8s信号，先Plan→Validate→Execute，建立回滚点并记录版本/路径/命令/变更摘... |
| [`deployment-verifier`](deployment-verifier.md) | deploy | 对已部署/升级/回滚后的服务做功能验证：health/readiness、核心API smoke test、页面可访问性、端口监听、日志与依赖(DB/Redis/MQ/proxy)核验。Trigger... |
| [`incident-rollback`](incident-rollback.md) | deploy | 处理部署失败与线上故障：health check失败、核心API错误、502/504、重启循环、依赖异常等。先定级与止血，再判断修复或回滚，执行回滚并输出incident/rollback记录（影响、... |
| [`repo-runtime-discovery`](repo-runtime-discovery.md) | deploy | 读取本地或GitHub repo做部署前识别：技术栈、build/test/run入口、Docker/compose/systemd/k8s信号、配置与密钥需求、依赖(DB/Redis/MQ/存储)、... |
| [`repo-service-lifecycle`](repo-service-lifecycle.md) | deploy | 端到端总控skill：读取repo/GitHub→主机就绪检查→部署计划→执行部署→功能验证→持续运维→故障回滚。Trigger for“帮我把这个仓库部署到主机并验收/持续运维/安全升级”。用于跨阶... |
| [`service-operations`](service-operations.md) | deploy | 对已上线服务做持续运维：版本/commit/image记录，健康与状态巡检，日志与资源(CPU/内存/磁盘/队列)观察，依赖与证书风险检查，升级前核对，变更留痕与runbook交接。Trigger f... |
| [`target-host-readiness`](target-host-readiness.md) | deploy | 检查目标Linux主机部署就绪性：OS/架构/CPU/内存/磁盘，网络与端口冲突，docker/systemd/nginx/python/node等运行时，可写目录与sudo/服务管理权限，并区分阻塞... |
| [`adoption-recommendation`](adoption-recommendation.md) | research | 基于风险采购证据链给出最终采用建议，区分evidence sufficiency与verdict，并定义Adopt/Control/Pilot/Defer/Reject路径、缓解措施、复审与回滚。Us... |
| [`compliance-check`](compliance-check.md) | research | 对候选方案开展合规风险研究，覆盖隐私、数据驻留/跨境传输、许可证与合同条款、政策匹配与法务待确认项。Use when the user says "合规评估", "合规检查", "compliance... |
| [`conference-adapter`](conference-adapter.md) | research | 为会议/研讨会场景补充CFP截止、讲者管理、AV与直播录制、注册胸牌、赞助履约、并行议程与会后proceedings检查清单，不复制主流程。Use when the user says "会议筹备",... |
| [`content-selection-adapter`](content-selection-adapter.md) | research | 为内容选择场景补充偏好画像、可用性、分级限制、群体兼容、口碑聚合、实时场次票价核验与备选方案检查清单，不复制主流程。Use when the user says "内容推荐", "content se... |
| [`decision-brief-framer`](decision-brief-framer.md) | research | 将模糊决策请求转化为结构化决策简报，明确决策问题、备选项、决策人、约束、偏好、must-have、nice-to-have与一票否决项。Use when the user says "决策简报", "... |
| [`decision-criteria-builder`](decision-criteria-builder.md) | research | 构建带权重的决策标准与比较口径，明确must-have/nice-to-have/deal-breaker并定义评分与证据规则。Use when the user says "决策标准", "deci... |
| [`decision-recommendation`](decision-recommendation.md) | research | 基于decision brief、criteria与comparison matrix生成最终推荐，明确生效条件、备选/回退路径、风险、试点验证与决策日志。Use when the user says... |
| [`event-runbook-writer`](event-runbook-writer.md) | research | 将活动研究成果转为可执行runbook/run of show，覆盖before/during/after时间线、角色分工、检查清单、沟通升级链路、应急SOP与复盘模板。Use when the us... |
| [`experience-brief-framer`](experience-brief-framer.md) | research | 定义体验或活动目标、参与者、约束、偏好与成功标准，形成可执行的活动研究简报。Use when the user says "活动策划", "event planning", "旅行规划", "trip... |
| [`learning-goal-framer`](learning-goal-framer.md) | research | 将模糊学习愿望转化为结构化学习目标，明确目标能力、当前基线、应用场景、时间约束、产出要求与评估标准。Use when the user says "学习目标", "learning goal", "我... |
| [`learning-path-designer`](learning-path-designer.md) | research | 基于学习目标与资源清单设计分阶段学习路径，定义阶段目标、资源组合、练习任务、交付物与评估检查点。Use when the user says "学习路径", "learning path", "学习路... |
| [`learning-practice-planner`](learning-practice-planner.md) | research | 基于学习路径设计分层练习与实操任务，构建从概念巩固到项目迁移的练习闭环。Use when the user says "练习计划", "practice plan", "实操任务", "hands-o... |
| [`learning-prerequisite-mapper`](learning-prerequisite-mapper.md) | research | 为学习目标梳理前置知识与依赖关系，形成分层先修结构与补齐顺序，避免学习路径断层。Use when the user says "前置知识", "prerequisite", "先修要求", "学习依赖... |
| [`learning-progress-reviewer`](learning-progress-reviewer.md) | research | 对学习执行结果进行阶段化成效复盘，评估概念理解、操作能力、迁移表现与下一步纠偏方向。Use when the user says "学习进度", "learning progress", "阶段检查"... |
| [`learning-resource-discovery`](learning-resource-discovery.md) | research | 按学习目标发现、筛选并排序学习资源，覆盖官方文档、教材、论文、教程、课程、代码仓库、实验与基准。Use when the user says "学习资源", "learning resources",... |
| [`logistics-risk-planner`](logistics-risk-planner.md) | research | 规划活动物流与风险应对，覆盖交通/住宿/设备物资/许可、controllable vs uncontrollable风险、预算超支与取消应急路径。Use when the user says "后勤规... |
| [`option-comparison-matrix`](option-comparison-matrix.md) | research | 基于criteria对候选方案做矩阵比较，输出评分、证据链接、deal-breaker淘汰、证据缺口与敏感性检查。Use when the user says "方案对比", "comparison ... |
| [`participant-experience-designer`](participant-experience-designer.md) | research | 从参与者视角优化活动全流程体验，设计attendee journey触点、痛点缓解、互动机制与体验指标，覆盖Before到After阶段。Use when the user says "参与者体验",... |
| [`planning-environment-scanner`](planning-environment-scanner.md) | research | 环境扫描与外部趋势分析（PESTLE、趋势雷达、信号识别），将外部变量转化为战略研究输入。Use when the user says "环境扫描", "PESTLE", "趋势分析", "trend... |
| [`planning-policy-researcher`](planning-policy-researcher.md) | research | 政策与监管研究（法规版图、政策趋势、合规要求、政策影响评估），将制度约束转化为战略规划输入。Use when the user says "政策研究", "policy research", "pol... |
| [`planning-roadmap-developer`](planning-roadmap-developer.md) | research | 战略路线图开发与分阶段落地设计（里程碑、依赖关系、决策门、资源节奏），整合环境、利益相关方、情景、政策与技术评估输入。Use when the user says "战略路线图", "roadmap"... |
| [`planning-scenario-planner`](planning-scenario-planner.md) | research | 情景规划与替代未来构建（关键不确定性、情景矩阵、稳健策略），将环境与利益相关方输入转化为战略选项。Use when the user says "情景规划", "scenario planning",... |
| [`planning-stakeholder-analyst`](planning-stakeholder-analyst.md) | research | 利益相关方分析与参与策略设计（影响力-关注度映射、关系网络、诉求识别），为规划研究建立可执行协同路径。Use when the user says "利益相关方分析", "干系人分析", "stake... |
| [`planning-technology-assessor`](planning-technology-assessor.md) | research | 技术评估与采用准备度分析（TRL成熟度、落地可行性、集成复杂度、战略匹配），将技术变量纳入规划决策。Use when the user says "技术评估", "technology assessm... |
| [`product-competitor-analysis`](product-competitor-analysis.md) | research | 系统化执行竞品发现、功能矩阵、定位分析、SWOT与市场规模估算，提炼可执行差异化方向。Use when the user says "竞品分析", "competitor analysis", "竞品... |
| [`product-decision-brief`](product-decision-brief.md) | research | 将用户研究、竞品分析与验证结果综合为go/no-go/pivot决策简报，提供可追溯结论与风险说明。Use when the user says "产品决策", "产品建议", "product de... |
| [`product-opportunity-mapper`](product-opportunity-mapper.md) | research | 基于用户证据与竞争格局做问题空间映射，结合JTBD识别、评分并优先级排序产品机会。Use when the user says "机会分析", "opportunity mapping", "JTBD... |
| [`product-user-research`](product-user-research.md) | research | 设计并分析用户研究（访谈、问卷、可用性测试、用户画像、用户旅程图），将用户证据转化为产品决策输入。Use when the user says "用户研究", "user research", "访谈... |
| [`product-validation-planner`](product-validation-planner.md) | research | 设计产品验证计划，围绕假设清单、最小MVP、量化成功标准与决策树，降低投入前不确定性。Use when the user says "验证计划", "validation plan", "MVP", ... |
| [`research-brief-framer`](research-brief-framer.md) | research | 将模糊研究意图转化为结构化research brief，明确研究问题、范围边界、证据要求与验收标准。Use when the user says "研究目标", "研究问题", "research b... |
| [`research-citation-auditor`](research-citation-auditor.md) | research | 引用审计与source verification：逐条核对claim→evidence_id→source_id链路，识别unsupported claims、引用缺口、来源失效/过时、统计口径不一致... |
| [`research-evidence-ledger`](research-evidence-ledger.md) | research | 证据账本构建与claim映射：把摘录笔记提升为正式证据，分类EXTRACTED/INFERRED/AMBIGUOUS/PROPOSED，标注confidence、矛盾与不确定性，输出claim map... |
| [`research-insight-log`](research-insight-log.md) | research | 研究灵感日志：记录“我突然想到”“记一下这个想法”的hypothesis/analogy/research-question/method-idea/experiment-idea等，绑定触发来源(s... |
| [`research-literature-access`](research-literature-access.md) | research | 文献全文合法获取与访问审计：处理付费墙、版本差异（published/accepted/preprint/tech report）、全文缺失与授权访问确认，优先free-first并记录access-... |
| [`research-note-capture`](research-note-capture.md) | research | 阅读摘录与证据笔记捕获：从PDF/DOC/网页提取关键原文，记录出处位置(page/section/paragraph)、paraphrase与why_it_matters，支持“先摘录不要总结”“读... |
| [`research-quality-reviewer`](research-quality-reviewer.md) | research | 研究报告独立质审：检查证据覆盖、引用完整性、逻辑链、反面证据、方法匹配、可执行建议、风险披露与AI腔（AI slop），给出发布前评级。Use when users ask “报告审查/quality... |
| [`research-report-writer`](research-report-writer.md) | research | 基于research brief、evidence ledger与synthesis写正式研究报告/执行摘要，支持科学研究、产品研究、规划研究、白皮书与提案，确保每个claim可追溯evidence_... |
| [`research-router`](research-router.md) | research | 研究入口与任务路由器。判断研究类型（科学/产品/规划/学习/决策/风险采购/活动体验）、复杂度并推荐合适的路由链路。Use when user says "研究", "帮我研究", "仔细研究", "... |
| [`research-source-discovery`](research-source-discovery.md) | research | 研究资料发现与来源登记：查找论文、官方文档、竞品材料、政策文件、行业报告、数据集与用户反馈，建立/维护source index并记录search strategy，按authority/relevan... |
| [`research-synthesis`](research-synthesis.md) | research | 研究综合分析：将evidence ledger转为主题聚类、对比矩阵、缺口分析、矛盾分析与置信度分级，形成key findings与recommendation options。Use when us... |
| [`risk-research-brief`](risk-research-brief.md) | research | 明确评估对象、采用场景、风险边界与决策要求，形成可执行的风险采购研究简报。Use when the user says "风险评估", "risk assessment", "工具评估", "tool... |
| [`schedule-itinerary-planner`](schedule-itinerary-planner.md) | research | 基于activity brief与场地研究设计可执行日程/行程，平衡活动密度、转场缓冲、休息餐食与A/B备选方案。Use when the user says "行程安排", "行程规划", "iti... |
| [`scientific-experiment-planner`](scientific-experiment-planner.md) | research | 科学实验设计与验证规划：围绕可检验假设、变量、baseline、ablation、评价指标、统计检验与复现要求生成experiment plan，回答“如何评估贡献”。Use when users a... |
| [`scientific-gap-finder`](scientific-gap-finder.md) | research | 基于文献矩阵做research gap分析：识别真实gap vs 伪gap，绑定支撑与反例论文，评估novelty与可验证性，并产出贡献方向(contribution options)。Use whe... |
| [`scientific-literature-review`](scientific-literature-review.md) | research | 科学文献综述与systematic review：围绕RQ执行检索策略、纳入排除筛选、全文复核、文献矩阵构建与方法比较，输出研究现状、related work脉络、争议点与研究空白。Use when ... |
| [`scientific-methodology-designer`](scientific-methodology-designer.md) | research | 科学方法设计：把研究想法落成可证伪research design，定义研究对象、核心假设、I/O、差异化、验证路径与validity threats，明确可声称与不可声称边界。Use when use... |
| [`scientific-paper-writer`](scientific-paper-writer.md) | research | 科研论文写作与骨架生成：基于research brief、evidence ledger、synthesis和实验结果产出paper outline与paper draft，强化contributio... |
| [`scientific-review-rebuttal`](scientific-review-rebuttal.md) | research | 论文投稿前自查与审稿回复(rebuttal)：执行novelty/soundness/evaluation/presentation/reproducibility/ethics六维检查，分类revi... |
| [`security-risk-review`](security-risk-review.md) | research | 对候选方案执行安全风险评审，覆盖数据暴露、访问控制、密钥管理、供应链、执行越权、prompt injection与审计响应能力。Use when the user says "安全评审", "secu... |
| [`tco-operational-risk`](tco-operational-risk.md) | research | 评估候选方案的TCO与运维风险，覆盖直接/隐性成本、买建混合路径、锁定风险、退出可行性与情景敏感因子。Use when the user says "TCO", "TCO评估", "total cos... |
| [`training-event-adapter`](training-event-adapter.md) | research | 为培训与工作坊场景补充学习目标映射、学员前置条件、实验环境、讲师材料、考核认证、出勤追踪与反馈闭环检查清单，不复制主流程。Use when the user says "培训安排", "trainin... |
| [`travel-adapter`](travel-adapter.md) | research | 为旅行场景补充目的地类型、签证入境、天气季节、本地交通、货币语言、健康保险与跨城/跨国核验清单，不复制主流程。Use when the user says "旅行规划", "trip planning... |
| [`vendor-source-diligence`](vendor-source-diligence.md) | research | 对供应商、开源项目与数据来源做尽调，评估身份与治理、SLA与支持、许可证兼容、bus factor、锁定与退出条件。Use when the user says "供应商尽调", "vendor du... |
| [`venue-destination-research`](venue-destination-research.md) | research | 研究并评估城市/酒店/会场/景点候选，覆盖可达性、容量、成本、设施、安全、天气与法规许可，输出推荐/备选/淘汰清单。Use when the user says "场地调研", "venue rese... |
| [`series-style-governor`](series-style-governor.md) | style-governor | 系列文档风格一致性治理。跨文档统一术语、命名、排版和叙事结构。从参考文件提取风格画像，审计目标文档，检测术语漂移和排版漂移，生成保守改写草稿。Use when writing a series of ... |
| [`skill-trust-governance`](skill-trust-governance.md) | trust | Skill trust/governance requests: skill trust, skill安全, 治理, 可信度, trust scan, risk score, redline chec... |
| [`typst-pdf-builder`](typst-pdf-builder.md) | typst | > |
