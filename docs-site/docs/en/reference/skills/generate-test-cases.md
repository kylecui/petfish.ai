# generate-test-cases

> Pack: **testdocs**

Generate test cases/test matrix for the current repo: API/CLI/UI/SDK/service, smoke/regression/acceptance/negative/boundary tests, traceability mapping, coverage gap补齐, or automation scaffolds (pytest/Playwright/contract). Trigger for 根据项目/模块/设计文档生成测试用例；not for generic testing theory.

**Compatibility:** Designed for OpenCode and Agent Skills compatible clients. Prefer Python 3.11+ and uv for running bundled scripts.

---

# Generate Test Cases

用这项技能时，你的目标不是泛泛而谈“应该测试什么”，而是**基于当前项目的真实设计与代码**，生成可追溯、可执行、可迭代的测试产物。

## 何时使用

当用户提出以下意图时加载本技能：

-根据当前项目/模块/设计文档生成test cases
-为API、CLI、Web UI、SDK、库或服务生成测试矩阵
-生成冒烟测试、回归测试、负面测试、边界测试、验收测试
-根据设计和代码补齐测试覆盖思路
-为现有仓库提供自动化测试建议或测试文件骨架

若用户只是问“什么是单元测试”“测试有哪些类型”之类的通用问题，不必强制加载本技能。

## 默认方法

先做**项目盘点**，再做**追踪映射**，最后做**分层测试产物**。  
不要直接跳到“写若干条例子”。

### Step 1：盘点项目事实

优先读取以下材料：

1. README、docs、设计说明、架构说明
2. API规范、proto、route、controller、schema
3. 配置样例、环境变量、构建文件
4. 入口程序、CLI帮助、public API
5. 现有tests目录与测试框架
6. 关键状态机、权限、持久化、外部依赖

需要快速盘点时，先运行：

```bash
uv run scripts/project_inventory.py .
```

先根据盘点结果判断项目更接近哪一类：

- library/SDK
- CLI
- Web API
- Web UI
- daemon/service
- pipeline/job
- research prototype/demo

### Step 2：建立traceability map

把“设计目标/模块/接口/风险”映射到“应测点”。

至少覆盖这些维度：

-功能点
-正常路径
-异常路径
-边界条件
-状态迁移
-认证/授权
-幂等/重试/回滚
-并发/时序
-配置错误
-外部依赖失败
-兼容性/回归风险

输出traceability matrix时，优先使用 `assets/traceability-matrix-template.md` 的格式。

### Step 3：生成分层测试策略

从适用层中选择，而不是机械地全部输出：

- Unit tests
- Integration tests
- Contract/API tests
- CLI tests
- E2E/UI tests
- Smoke tests
- Regression tests
- Negative/abuse-adjacent tests

*... (80 more lines in full SKILL.md)*
