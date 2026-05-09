---
name: deployment-executor
description: 按已确认部署计划执行上线/升级/重部署：优先repo现有Docker/compose/systemd/k8s信号，先Plan→Validate→Execute，建立回滚点并记录版本/路径/命令/变更摘要。Trigger for执行发布、切换release目录、配置注入、迁移与启动；用于部署方式已明确且需要安全落地时。
compatibility: Requires deployment access to the target host. Common tools: ssh, rsync, git, docker or systemctl. Python 3.11+ and uv recommended for helper scripts.
license: Internal use
---

# 目标

把“已经分析清楚”的部署计划真正执行下去，但要安全、可回滚、可验证。

## 适用前提

只有在以下内容已基本清楚时才进入执行：

- repo来源与版本
-部署方式
-目标目录
-依赖配置与密钥
-启动方式
-验证方法
-回滚点

如果这些还不清楚，先回到识别或主机检查阶段。

## 执行策略

### 策略A：当前repo自带容器定义
优先使用：
- `docker compose up -d`
- `docker build` + `docker run`
- repo的已有deploy script

### 策略B：传统主机部署
适用于：
- Python/Node/Go/Java/Rust服务
-使用systemd管理
-需要显式目录布局和软链切换

推荐目录模型：

```text
/opt/<service>/
  releases/<release-id>/
  current -> releases/<release-id>
  shared/
    config/
    logs/
    data/
```

### 策略C：k8s/helm
仅在repo本身已提供相关材料，或用户明确要求使用k8s时采用。

## Plan → Validate → Execute

### 1. 计划
先写出：

-代码来源：branch/tag/commit
-构建命令
-分发方式：git pull/clone/rsync/artifact
-配置注入方式
-迁移命令（如有）
-启动/重启方式
-验证矩阵
-回滚命令或回滚路径

### 2. 预验证
在真正上线前做最小验证：

-目录是否存在/可写
-配置文件是否齐
-镜像/依赖能否获取
-端口是否可用
-启动命令在语义上是否正确
-必要时先dry-run或先拉起staging路径

### 3. 执行
执行顺序通常如下：

1. 记录当前版本/当前路径/当前容器/进程状态
2. 创建新发布目录或准备新镜像
3. 写入配置/环境变量
4. 安装依赖/构建
5. 做数据库迁移（如必须，且已确认顺序）
6. 启动新版本
7. 做验证
8. 验证通过后再切流或确认完成

## 默认输出

```markdown
## Deploy target
## Release id / commit
## Planned actions
## Commands executed
## Files / paths touched
## Runtime status
## Verification handoff
## Rollback entry
```

## gotchas

-不要把 `git pull` 当成万能升级方案；很多生产环境更适合版本化发布目录
-不要在未备份配置的情况下直接覆盖 `.env`、nginx配置、service unit
-数据库迁移可能不可逆，必须单独说明风险
-应用启动成功不代表反向代理、worker、cron、webhook都已恢复
- `docker compose up -d` 之后仍必须检查容器状态和日志

## 何时读取参考文件

-需要决定采用"发布目录 + current软链"时，读取：
  `references/release-layout.md`
-需要区分"就地升级"和"新发布切换"时，读取：
  `references/upgrade-strategy.md`
-部署私有仓库、目标服务器无GitHub凭据时，读取：
  `references/private-repo-access.md`
-多服务共享主机、存在本地补丁或执行git pull升级时，读取：
  `references/local-patch-management.md`
