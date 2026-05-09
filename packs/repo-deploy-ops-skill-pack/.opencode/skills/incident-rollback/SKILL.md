---
name: incident-rollback
description: 处理部署失败与线上故障：health check失败、核心API错误、502/504、重启循环、依赖异常等。先定级与止血，再判断修复或回滚，执行回滚并输出incident/rollback记录（影响、证据、动作、当前状态、后续修复）。Use when rollout fails or service needs rapid stabilization.
compatibility: Requires access to the target environment and prior deployment context. Helpful tools: systemctl, journalctl, docker logs, curl, ssh.
license: Internal use
---

# 目标

当部署或运行出现异常时，快速回答三件事：

1. **问题是否真实影响可用性**
2. **应修复还是应立即回滚**
3. **如何安全止血并留下记录**

## 何时使用

-部署后health check失败
-核心API报错
-页面502/504
-容器/进程持续重启
-数据库/缓存/密钥错误导致服务异常
-用户明确要求回滚

## 处置顺序

### 1. 先定级
至少判断：

-是否影响核心用户路径
-是否影响所有流量还是部分流量
-是否仅是观测噪声
-是否可在短时间内修复
-是否存在清晰可执行的回滚点

### 2. 先止血
优先选择低风险动作：

-切回前一版本
-停止错误实例
-恢复上一份配置
-恢复上一份容器/ image tag/symlink
-暂时从反向代理摘流
-仅在必要时重启

### 3. 再分析
排查时围绕：

-最近变更
-配置差异
- migration
-依赖连接
-证书/域名
-端口/反向代理
-权限/路径
-环境漂移

### 4. 输出结论
明确写出：

-症状
-初步原因
-已采取动作
-当前状态
-是否已回滚
-后续修复建议

## 回滚原则

-有清晰回滚点时，优先回滚恢复可用性
-没有清晰回滚点时，优先最小化影响范围
-数据库迁移不可逆时，必须单独说明风险
-不要为了“查明原因”而长时间保持故障状态

## 默认输出

```markdown
## Incident summary
## User-visible impact
## Triage evidence
## Immediate actions
## Rollback decision
## Current status
## Follow-up fixes
```

## gotchas

-不要在生产故障期间追求“完美修复”而延误恢复
- “我觉得快好了”不是不回滚的理由
-回滚后仍要做验证，不能默认恢复成功
-配置错误与代码错误常常表现相似，要看最近变更
-日志量大时，先找第一条关键错误和重复模式

## 何时读取参考文件

-需要判断“修复还是回滚”时，读取：
  `references/rollback-decision.md`
-需要事后记录模板时，读取：
  `assets/incident-template.md`
