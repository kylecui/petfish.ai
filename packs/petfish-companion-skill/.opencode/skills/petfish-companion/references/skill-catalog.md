# 胖鱼PEtFiSh Skill Catalog — 详细能力参考

> 本文件是skill pack及内置skill的**能力矩阵**、**依赖关系**、**兼容性**指南。
> SKILL.md 已覆盖命令清单和感知规则，本文重点提供pack间的组合指南、限制范围、版本依赖。

---

## 1. 外置Pack能力矩阵

### init — Project Initializer

| 能力维度 | 详情 |
|---------|------|
| **支持的Profile** | minimal, course, code, ops, security, writing, skills-package, comprehensive |
| **兼容平台** | OpenCode, Claude, Cursor, Copilot, Windsurf, Antigravity, Codex |
| **常见失败点** | 目录已存在时覆盖行为；Python<3.9时uv安装失败；网络超时导致pack下载中断 |
| **与其他pack的关系** | 其他pack都依赖init创建的目录结构；init本身无运行时依赖 |
| **文件大小** | ~50MB（含wizard资源） |
| **典型运行时间** | 30-120s（取决于网络和profile复杂度） |

### course — Curriculum Development

| 能力维度 | 详情 |
|---------|------|
| **能做的事** | 提纲规划、正文编写、实验设计、学员资料、教师资料、QA/QC、方法论沉淀 |
| **不能做的事** | 授课录制、学员成绩管理、LMS集成、视频剪辑 |
| **最小项目规模** | ≥3章节、≥1个实验；单章节课程不建议用 |
| **典型工作流** | outline → content → labs → learner-pack → instructor-pack → QA → QC → release |
| **与deploy的关系** | 课程中涉及部署演示时，建议同时装deploy pack |
| **与testdocs的关系** | 课程实验需自动生成验收用例时，建议同时装testdocs pack |
| **存储占用** | 基础10MB；每10万字课程内容加3-5MB |
| **建议项目数上限** | 1个pack支持管理5-8个课程（目录分离） |

### deploy — Deployment & Ops

| 能力维度 | 详情 |
|---------|------|
| **支持的部署方式** | Docker、Docker Compose、systemd、K8s、Helm、Ansible、自定义脚本 |
| **支持的技术栈** | Node.js, Python, Java, Go, Ruby, .NET, PHP, Rust（通过Dockerfile识别） |
| **支持的CI/CD** | GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis（通过.yml自动识别） |
| **不能做的事** | 云账户管理、IAM权限配置、域名DNS管理、SSL证书申请 |
| **与course的关系** | course讲授部署时推荐并行使用 |
| **安全敏感** | 处理SSH密钥、API令牌、数据库密码——需要特殊权限提升 |
| **网络依赖** | 高：需拉取镜像、包管理器、在线health check |
| **典型失败恢复时间** | 5-30min（取决于故障根因）|

### petfish — Writing Style

| 能力维度 | 详情 |
|---------|------|
| **支持的语言** | 简体中文、English、中英混合 |
| **支持的文档类型** | Markdown、.md批量处理、DOCX（转Markdown后）、HTML（转Markdown后） |
| **不能做的事** | 语法纠错（建议用ChatGPT Grammar Checker）、SEO优化、翻译、音频转录 |
| **生效范围** | 单文件或目录批量；支持include/exclude过滤 |
| **改写强度** | strict（激进重写）、normal（中等调整）、gentle（轻微补充）——可配置 |
| **独立性** | 完全独立，不依赖其他pack |
| **批处理性能** | ~100KB/s；10MB文档约100s |

### ppt — Presentation Design

| 能力维度 | 详情 |
|---------|------|
| **支持的格式** | PPTX（LibreOffice兼容）、ODP（转PPTX）、PDF（展示，不编辑） |
| **依赖外部工具** | soffice（LibreOffice）、pdftoppm（Poppler）——需手动或包管理器安装 |
| **支持的操作系统** | Windows（WSL2推荐）、macOS、Linux |
| **不能做的事** | 动画脚本、高级特效、3D渲染、视频嵌入 |
| **常见缺陷** | 无soffice时自动转换失败；低分辨率渲染导致图片模糊 |
| **与course的关系** | 课程PPT化时常搭配使用；course提大纲，ppt生成slides |
| **生成速度** | ~200-500ms per slide |

### testdocs — Testing & Documentation

| 能力维度 | 详情 |
|---------|------|
| **自动生成物** | 测试矩阵、验收用例、API文档、README、Quick Start |
| **从哪些源生成** | Python/TypeScript源码、JSON/YAML配置、OpenAPI/GraphQL Schema |
| **不能做的事** | 集成测试执行、覆盖率测试、性能基准测试、UI自动化脚本 |
| **最低代码量** | ≥50行代码才能生成有意义的用例 |
| **测试框架兼容** | Jest、Pytest、Go testing、JUnit（自动检测） |
| **与course的关系** | 课程的实验需要验收用例时推荐搭配 |

### research — Research Workbench

| 能力维度 | 详情 |
|---------|------|
| **能做的事** | 研究简报框架、来源发现与索引、文献合法获取、摘录笔记、灵感日志、证据账本、综合分析、报告写作、质量审查 |
| **不能做的事** | 实验执行、数据采集、统计分析运行、论文投稿、学术数据库付费订阅管理 |
| **研究类型** | scientific（文献综述、gap分析）、product（用户研究、竞品分析）、planning（环境扫描、路线图） |
| **核心原则** | 证据优先：每个声明追溯到来源；生成与审查分离；事实、推断、提案不混合 |
| **与course的关系** | 课程设计前期的文献调研、参考资料整理可搭配使用 |
| **与petfish的关系** | 报告写作后可用petfish风格改写润色 |
| **安装命令** | `/petfish install research` |

---

## 2. 内置Skill详细能力表

### marketplace-connector

| 能力维度 | 详情 |
|---------|------|
| **数据源** | 胖鱼自有仓库、SkillKit、Smithery、Glama、anthropics/skills、GitHub |
| **搜索语义** | 模糊匹配skill名称、描述关键词、trigger短语；支持按语言/平台/分类过滤 |
| **搜索范围限制** | GitHub默认扫描Top 100星项目；可用`--deep`扩大到1000+ |
| **结果质量评分** | 综合考虑来源优先级、更新频率、security audit历史、下载量 |
| **缓存策略** | 24h本地缓存；可用`--no-cache`强制刷新 |
| **搜索失败恢复** | 自动降级至下一优先级数据源 |
| **API限制** | SkillKit 100req/min、Smithery 50req/min、GitHub 60req/min（匿名） |
| **输出格式** | table（人易读）、json（自动化）、csv（Excel导入） |

### skill-author

| 能力维度 | 详情 |
|---------|------|
| **生成物** | 标准目录结构、SKILL.md、references/目录、scripts/骨架、.gitignore |
| **模板类型** | automation（脚本工具）、workflow（多步流程）、knowledge（参考资料） |
| **命名验证** | 强制kebab-case，≤64 chars，不得重复 |
| **生成质量** | 符合CT002-CT010 lint规范；部分初始分数85-92/100 |
| **常见痛点** | 用户名称过长需截断；特殊字符自动转义；重名检测依赖本地扫描 |
| **生成速度** | ~1-2s（含校验） |

### skill-lint

| 能力维度 | 详情 |
|---------|------|
| **检查项** | SKILL.md结构、frontmatter、description长短适度、目录规范、脚本安全、重叠检测 |
| **评分维度** | 格式(30) + 规范(30) + 安全(20) + 重叠(20) = 100分 |
| **合格线** | ≥80/100；<70/100不建议发布 |
| **常见扣分** | description太长(-15)、脚本有危险命令(-25)、与兄弟skill重叠>40%(-20) |
| **自动修复范围** | 目录缺失、格式错误、引号不匹配；但不能修改逻辑错误 |
| **递归扫描开销** | ~100个skill约30s |
| **持续集成** | 可集成pre-commit、GitHub Actions（触发器：*.md, scripts/* 变化） |

### repo-skill-miner

| 能力维度 | 详情 |
|---------|------|
| **识别目标** | CI/CD配置、Docker构建、Bash/Python脚本、Terraform、Ansible、Agent框架、CLI工具 |
| **扫描深度** | quick(目录树) → standard(代码分析) → deep(完整AST + 安全审计) |
| **候选评估** | 复杂度、工具需求、安全风险、代码质量、文档完善度 |
| **常见挖掘** | Makefile → lint skill、Dockerfile → deploy skill、test/**/*.py → testdocs skill |
| **适用场景** | 大型开源项目（千+文件）、企业内部积累、遗产代码现代化 |
| **生成报告** | Markdown（人工审阅）、JSON（自动化处理） |

### skill-security-auditor

| 能力维度 | 详情 |
|---------|------|
| **检测规则** | 危险命令(rm -rf等)、secret泄露(.env、密钥文件)、远程执行(eval、curl\|bash)、权限过宽(777) |
| **风险分级** | CRITICAL(0.75-1.0) → HIGH(0.5-0.75) → MEDIUM(0.3-0.5) → LOW(<0.3) |
| **审计范围** | SKILL.md frontmatter、scripts/所有脚本、references/外链扫描 |
| **漏洞库** | OWASP Top 10、CWE Top 25、定制化胖鱼规则集 |
| **假正例处理** | 支持.auditignore白名单；支持注释标记`# audit: ignore-next-line UNSAFE_RM` |
| **通常耗时** | 单个skill ~2-5s；批量100个 ~3min |

### quality-gate

| 能力维度 | 详情 |
|---------|------|
| **门禁流程** | lint(评分) → audit(风险) → metadata验证 → 综合决策 |
| **决策规则** | PASS(lint≥80 + audit<0.5) → CONDITIONAL(需人工) → FAIL(不可发布) |
| **通过率统计** | 胖鱼自有pack 95%+、社区pack 60-70% |
| **pre-commit集成** | 可绑定git hook，commit前自动检查modified skill |
| **GitHub Actions集成** | 示例workflow见`quality-gate/assets/github-action-gate.yml` |
| **失败后恢复** | 给出具体扣分理由和改进步骤 |

### skill-description-optimizer

| 能力维度 | 详情 |
|---------|------|
| **分析维度** | 长度(100-300字最优)、触发短语密度(3-5个)、覆盖范围(不能过广) |
| **重叠检测** | 与同pack内其他skill的关键词重叠度；建议≤20% |
| **生成建议** | 重写方向、关键词调整、trigger短语补充、description精简指导 |
| **自动改进版** | 可选生成改进后的description示例 |
| **应用建议** | 单skill优化30min；全pack系统优化2-4h |

### skill-trigger-evaluator

| 能力维度 | 详情 |
|---------|------|
| **测试集** | 正向查询(应该触发)、反向查询(不应该触发)、边界查询(易混淆) |
| **评估指标** | 触发率(recall)、精度(precision)、F1 score |
| **跨检测** | 检测与兄弟skill的误触发冲突；建议冲突率<5% |
| **自定义测试** | 支持上传JSON测试集 |
| **典型阈值** | precision ≥ 0.85 算合格；recall ≥ 0.90 算优秀 |
| **常见改进** | trigger短语抽象化、反向短语添加、特异性关键词补强 |

### skill-usage-tracker

| 能力维度 | 详情 |
|---------|------|
| **追踪事件** | skill激活(何时/来自何用户)、用户反馈(满意/无用/需改进)、错误日志 |
| **存储方式** | 本地JSON（~/.opencode/petfish-stats/）；不上传云端 |
| **隐私保护** | 仅记录skill别名、激活时间、反馈标签；不记录prompt/response内容 |
| **报告类型** | 全局统计、按pack统计、按时间段统计、activation趋势图 |
| **推荐输入** | 满意率≥80% → 重点推荐；<50% → 标记待改进；>90天未激活 → 休眠skill |
| **保留期限** | 默认90天滚动；可配置 |

---

## 3. Pack间依赖与兼容性矩阵

| 组合 | 典型场景 | 风险/注意 |
|-----|--------|---------|
| course + petfish | 课程文档需要改写风格 | 兼容；无冲突 |
| course + testdocs | 课程实验需要自动生成验收用例 | 兼容；共享课程结构目录 |
| deploy + course | 课程讲述部署内容 | 兼容；部署脚本不要放在course/目录 |
| deploy + testdocs | 部署自动化测试 | 兼容；推荐testdocs生成用例供deploy验证 |
| ppt + course | 课程转PPT幻灯片 | 兼容；建议course outline → ppt slides流 |
| ppt + petfish | PPT文本改写 | 兼容性待验证；petfish主要处理Markdown，PPT需转文本 |

---

## 4. Profile→Pack映射原理

| Profile | 自动装 | 映射理由 |
|---------|-------|--------|
| **minimal** | petfish | 只需基础写作风格 |
| **course** | course, petfish | 课程开发+写作改进 |
| **code** | deploy, petfish, testdocs | 代码部署+测试文档+风格 |
| **ops** | deploy, petfish | 运维部署+文档改写 |
| **security** | deploy, petfish, testdocs | 安全代码审计+部署+测试覆盖 |
| **writing** | petfish, ppt | 写作优化+演示制作 |
| **skills-package** | petfish, testdocs | 开发skill时需文档和风格检查 |
| **comprehensive** | course, deploy, petfish, ppt, testdocs | 全能工作坊 |

---

## 5. 平台支持与限制

### 内置Skill支持范围

| Skill | OpenCode | Claude | Cursor | Copilot | Windsurf | Antigravity |
|-------|----------|--------|--------|---------|----------|-------------|
| marketplace-connector | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| skill-author | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ✅ |
| skill-lint | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| repo-skill-miner | ✅ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ |
| skill-security-auditor | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| quality-gate | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| skill-description-optimizer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| skill-trigger-evaluator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| skill-usage-tracker | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ |

**图例**：✅ 完全支持 | ⚠️ 部分功能 | ❌ 不支持

---

## 6. 版本兼容性

| Pack | 最低版本 | 推荐版本 | 已验证版本 |
|-----|---------|--------|----------|
| init | 0.1.0 | 0.2.0+ | 0.2.0, 0.2.1 |
| companion | 0.2.0 | 0.2.0+ | 0.2.0 |
| course | 0.1.0 | 0.2.0+ | 0.1.5, 0.2.0 |
| deploy | 0.1.0 | 0.2.0+ | 0.1.0, 0.1.5 |
| petfish | 3.0.0 | 3.1.0+ | 3.0.0, 3.1.0 |
| ppt | 0.1.0 | 0.2.0+ | 0.1.0 |
| testdocs | 0.1.0 | 0.2.0+ | 0.1.0, 0.1.5 |

---

## 7. 常见坑点与应对

| 坑点 | 症状 | 原因 | 解决 |
|-----|------|------|------|
| 初始化冲突 | init失败，提示"目录已存在" | 旧项目重初始化 | 用`--force`覆盖或手动清理 |
| 平台检测错误 | skill装错了平台目录 | 多平台混用，自动检测失败 | 用`--platform`显式指定 |
| Python版本低 | lint/audit报"ModuleNotFoundError" | Python<3.9 | 升级到3.9+或用uv |
| 网络超时 | marketplace搜索卡住 | 三方API不可达或网络慢 | 用`--local-only`仅搜胖鱼自有 |
| 重叠警告高 | lint警告"description重叠>50%" | skill设计重复 | 运行optimizer建议重新描述 |
| 触发冲突 | 两个skill误触发 | trigger短语过宽 | 运行evaluator检测，改进trigger |
| 权限拒绝 | 写文件失败"Permission denied" | 安装目录权限不足 | chmod或重装到有权目录 |

---

## 8. 三方市场优先级与特点

| 市场 | 优先级 | 更新频率 | 质量审核 | 特点 |
|------|-------|--------|--------|------|
| **胖鱼自有** | 1 | 周 | security audit + gate | 官方维护，最稳定 |
| **SkillKit** | 2 | 月 | 社区验证 | 跨平台skill聚合 |
| **Smithery** | 2 | 月 | 上传者负责 | MCP Server居多 |
| **Glama** | 2 | 月 | 上传者负责 | 多模态MCP |
| **anthropics/skills** | 3 | 不规律 | Anthropic维护 | Claude官方skills |
| **GitHub高星** | 4 | 每日 | 社区star评分 | 广泛使用但需审查 |

---

## 9. 资源占用与性能指标

| 操作 | CPU | 内存 | 磁盘 | 耗时 |
|-----|-----|------|------|------|
| init（full profile） | 低 | ~100MB | ~200MB | 60-120s |
| course skill setup | 低 | ~80MB | ~150MB | 30-60s |
| deploy skill + Docker | 中 | ~300MB | ~500MB(镜像) | 3-10min |
| lint单skill | 低 | ~50MB | - | 1-2s |
| lint全pack(100+ skill) | 中 | ~200MB | - | 30-60s |
| audit单skill | 低 | ~50MB | - | 2-5s |
| miner(deep on大repo) | 高 | ~500MB+ | - | 5-20min |
| marketplace搜索 | 低 | ~100MB | - | 5-15s |

---

## 10. 升级路径与向后兼容

- **0.1.x → 0.2.x**：完全兼容；新增特性自动启用
- **0.2.x → 1.0.0** (规划中)：API重构，需迁移脚本
- **跨major版本**：不保证兼容；需手动迁移或reinstall

---

## 11. 常用命令速查

| 目标 | 命令 |
|-----|------|
| 检查某pack能否发布 | `/petfish gate <pack-path>` |
| 找skill重叠问题 | `/petfish lint <pack-path> --check-overlap` |
| 测试skill触发准确性 | `/petfish eval <skill-path> --verbose` |
| 从开源repo挖掘新skill | `/petfish mine <repo> --depth deep` |
| 批量改进所有skill描述 | `/petfish optimize <pack-path> --recursive --apply` |
| 跨市场搜索skill | `/petfish search <keyword> --format json` |
| 本地仅搜胖鱼自有库 | `/petfish search <keyword> --local-only` |
