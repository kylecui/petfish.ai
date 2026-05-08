# Repo Deployment & Operations Rules

本项目包含一套用于 **repo部署、验证、运维、回滚** 的OpenCode skills。

## 工作原则

-当用户要求“读取repo/GitHub项目并部署到指定主机”时，优先走完整链路：
  1. `repo-runtime-discovery`
  2. `target-host-readiness`
  3. `deployment-executor`
  4. `deployment-verifier`
  5. 如需持续管理，再使用 `service-operations`
  6. 如遇异常，再使用 `incident-rollback`

-如果用户给的是宽泛任务，例如：
  - “帮我把这个仓库部署到10.0.0.5”
  - “把这个GitHub repo跑起来并验收”
  - “把这个服务上线后帮我持续运维”

  优先启用 `repo-service-lifecycle` 作为总控技能。

## 必须遵守

-先分析repo与目标主机，再选择部署方式。
-不得在未形成最小部署计划前直接执行高风险变更。
-不操作其它仓库的内容（即使有权限），只能通过issues反馈问题和建议。
-网络出现问题或可能是网络问题导致的中断（SSH无法连接、apt install失败、docker pull超时），不要急于改变当前方案，至少重试两次再行调整。
-涉及覆盖、替换、重启、删除、迁移时，必须先说明：
  -本次动作影响范围
  -回滚入口
  -验证办法
-部署完成后必须给出至少一份验证结果：
  -健康检查
  -功能smoke test
  -日志核验
  -端口/进程/页面/API结果
-任何长期运维动作都要记录版本、时间、路径、端口、依赖、观察点。

## 输出偏好

当任务涉及部署或运维时，默认输出以下结构：

1. **识别结果**
2. **部署计划**
3. **执行结果**
4. **验证结果**
5. **回滚点**
6. **后续运维建议**

## 懒加载参考文件

只在需要时读取skill中的 `references/*.md` 与 `assets/*` 文件，不要一次性全部加载。
