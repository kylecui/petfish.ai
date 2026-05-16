# target-host-readiness

> 所属包: **deploy**

检查目标Linux主机部署就绪性：OS/架构/CPU/内存/磁盘，网络与端口冲突，docker/systemd/nginx/python/node等运行时，可写目录与sudo/服务管理权限，并区分阻塞项与建议项。Trigger for首次部署前检查、升级前核对、环境漂移巡检与rollout前置验证。

**兼容性:** Best for Linux hosts with ssh access. Requires Python 3.11+; uv recommended. Helpful commands: ssh, df, ss, systemctl, journalctl, docker.

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

*... (完整 SKILL.md 中还有 35 行)*
