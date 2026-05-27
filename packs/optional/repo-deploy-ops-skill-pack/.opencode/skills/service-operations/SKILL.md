---
name: service-operations
description: 对已上线服务做持续运维：版本/commit/image记录，健康与状态巡检，日志与资源(CPU/内存/磁盘/队列)观察，依赖与证书风险检查，升级前核对，变更留痕与runbook交接。Trigger for日常SRE巡检、上线后保活、运维交接、升级准备和操作卫生治理。
compatibility: Requires access to the running environment. Python 3.11+ and uv recommended. Helpful tools: systemctl, journalctl, docker, df, free, ss, curl.
license: Internal use
---

# 目标

让代理不仅能“部署一次”，还知道如何“持续维护”。

## 何时使用

-服务已经上线
-用户要求持续运维、日常巡检
-需要升级前核对
-需要记录版本、路径、端口、依赖、日志入口
-需要交接runbook

## 运维基线

至少记录：

-当前版本/ commit/image tag
-当前部署路径
-当前配置路径
-当前日志路径
-服务管理方式（docker/compose/systemd/k8s）
-健康检查入口
-核心端口
-外部依赖
-最近一次变更时间
-上一次成功验证结果

## 推荐脚本

用下面的脚本维护一个轻量发布状态文件：

```bash
uv run scripts/release_state.py init --state .deploy/releases.json
uv run scripts/release_state.py add --state .deploy/releases.json --release-id 20260423-210500 --version v1.2.3 --commit abcdef1 --path /opt/myapp/releases/20260423-210500
uv run scripts/release_state.py promote --state .deploy/releases.json --release-id 20260423-210500
```

## 巡检项

### 服务状态
-进程/容器是否存活
-最近是否频繁重启
-健康检查是否稳定

### 日志状态
-是否持续出现error/exception
-是否有连接失败、认证失败、上游失败
-是否存在明显告警前兆

### 资源状态
- CPU/memory
-磁盘空间
- inode（如有需要）
-连接数/端口占用
-队列积压/ worker backlog（如有）

### 依赖状态
- DB/Redis/MQ /存储
-反向代理/ TLS
- DNS /域名/证书到期风险

## 变更管理

每次升级或重要运维动作后，至少补充：

-时间
-操作人/执行者
-版本
-路径或镜像
-关键命令
-验证结果
-是否存在后续观察项

## 默认输出

```markdown
## Current release state
## Service/runtime status
## Logs and resources
## Risks / watchpoints
## Upgrade readiness
## Ops handover notes
```

## gotchas

- “现在没报错”不代表“运维工作完成”
-没有版本记录，后续升级和回滚会很痛苦
-不要只记录镜像tag；最好同时记录commit、配置版本、路径
-巡检最好固定入口，否则每次都靠临场发挥
-长期运维应识别“观察项”，而不只是“当前是否宕机”

## 何时读取参考文件

-需要整理runbook时，读取：
  `assets/ops-runbook-template.md`
-需要区分“立即处理”和“持续观察”时，读取：
  `references/watchpoints.md`
