# deploy

**部署与运维 — 运行时识别、主机检查、部署执行、验证、运维、回滚、全生命周期管理**

| 字段 | 值 |
|---|---|
| 包名 | `repo-deploy-ops-skill-pack` |
| 别名 | `deploy` |
| 版本 | 1.0.1 |
| 技能数 | 7 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`deployment-executor`](../skills/deployment-executor.md) — 按已确认部署计划执行上线/升级/重部署：优先repo现有Docker/compose/systemd/k8s信号，先Plan→Validate→Execute，建立回滚点并记录版本/路径/命令/变更摘要。Trigger for执行发布、切换...
- [`deployment-verifier`](../skills/deployment-verifier.md) — 对已部署/升级/回滚后的服务做功能验证：health/readiness、核心API smoke test、页面可访问性、端口监听、日志与依赖(DB/Redis/MQ/proxy)核验。Trigger for验收、交接、巡检、故障修复后复验...
- [`incident-rollback`](../skills/incident-rollback.md) — 处理部署失败与线上故障：health check失败、核心API错误、502/504、重启循环、依赖异常等。先定级与止血，再判断修复或回滚，执行回滚并输出incident/rollback记录（影响、证据、动作、当前状态、后续修复）。Use...
- [`repo-runtime-discovery`](../skills/repo-runtime-discovery.md) — 读取本地或GitHub repo做部署前识别：技术栈、build/test/run入口、Docker/compose/systemd/k8s信号、配置与密钥需求、依赖(DB/Redis/MQ/存储)、health端点与端口，并产出deplo...
- [`repo-service-lifecycle`](../skills/repo-service-lifecycle.md) — 端到端总控skill：读取repo/GitHub→主机就绪检查→部署计划→执行部署→功能验证→持续运维→故障回滚。Trigger for“帮我把这个仓库部署到主机并验收/持续运维/安全升级”。用于跨阶段DevOps/SRE任务，并按需路由到...
- [`service-operations`](../skills/service-operations.md) — 对已上线服务做持续运维：版本/commit/image记录，健康与状态巡检，日志与资源(CPU/内存/磁盘/队列)观察，依赖与证书风险检查，升级前核对，变更留痕与runbook交接。Trigger for日常SRE巡检、上线后保活、运维交接...
- [`target-host-readiness`](../skills/target-host-readiness.md) — 检查目标Linux主机部署就绪性：OS/架构/CPU/内存/磁盘，网络与端口冲突，docker/systemd/nginx/python/node等运行时，可写目录与sudo/服务管理权限，并区分阻塞项与建议项。Trigger for首次部...

## 安装

```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack deploy --detect
```
