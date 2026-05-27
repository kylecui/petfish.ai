---
name: target-host-readiness
description: 检查目标Linux主机部署就绪性：OS/架构/CPU/内存/磁盘，网络与端口冲突，docker/systemd/nginx/python/node等运行时，可写目录与sudo/服务管理权限，并区分阻塞项与建议项。Trigger for首次部署前检查、升级前核对、环境漂移巡检与rollout前置验证。
compatibility: Best for Linux hosts with ssh access. Requires Python 3.11+; uv recommended. Helpful commands: ssh, df, ss, systemctl, journalctl, docker.
license: Internal use
---

# 目标

在真正部署之前，确认“目标主机是否具备部署与运行条件”。

## 何时使用

-用户指定了一台或多台Linux主机
-要做首次部署
-要做升级前检查
-要做巡检或排查环境漂移
-不确定docker/systemd/runtime /端口/路径/权限 是否具备

## 核心原则

-先探测，再部署
-尽量结构化输出，不要只贴零散命令结果
-对权限不足、命令缺失、目录不存在要明确标记
-把“阻塞项”与“建议项”区分开

## 推荐脚本

```bash
uv run scripts/host_probe.py --ssh user@host --output -
```

如果当前shell就在目标机上，也可：

```bash
uv run scripts/host_probe.py --local --output -
```

## 至少检查这些项

### 系统与资源
- hostname
- OS发行版
- kernel
- arch
- CPU
- memory
- disk

### 运行时与工具
- `git`
- `curl`
- `jq`
- `python3`
- `uv`
- `node` / `npm` / `pnpm`
- `go`
- `java` / `mvn` / `gradle`
- `docker`
- `docker compose`
- `systemctl`
- `journalctl`
- `nginx`
- `kubectl`
- `helm`

### 权限与目录
-是否能写入部署目录
-是否能写入日志目录
-是否能创建/切换软链
-是否有sudo
-是否能管理systemd/docker

### 网络与端口
-核心端口是否被占用
-出站连通性是否满足依赖下载/镜像拉取
-监听端口与预期部署端口是否冲突
-反向代理端口是否已被nginx/Caddy/已有服务占用

## 输出结构

```markdown
## Host summary
## Runtime availability
## Permission/path checks
## Port/network checks
## Blocking issues
## Non-blocking suggestions
```

## 判定逻辑

### 可直接部署
当以下条件基本满足时：
-所需运行时齐备
-目录可用
-关键端口不冲突
-有足够权限
-网络条件满足

### 需先补环境
当以下任一成立：
-缺少核心运行时
-无法管理服务
-关键端口冲突
-部署目录不可写
-证书/反代/挂载目录等依赖未准备

## gotchas

- `python3` 存在不代表可直接跑项目，可能仍缺 `uv`、venv或编译依赖
- `docker` 存在不代表当前用户有权限使用
- `systemctl` 存在不代表该环境启用了systemd
-端口空闲不代表外部网络可达，还要看防火墙/安全组/反向代理
-临时手工修环境时，要记录成可复现步骤

## 何时读取参考文件

-需要判断“端口冲突是否可接受”时，读取：
  `references/port-and-proxy-notes.md`
-需要区分“阻塞项/建议项”时，读取：
  `references/readiness-decision-rules.md`
