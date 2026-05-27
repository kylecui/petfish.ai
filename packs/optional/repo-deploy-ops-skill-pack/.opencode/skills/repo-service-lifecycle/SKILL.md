---
name: repo-service-lifecycle
description: 端到端总控skill：读取repo/GitHub→主机就绪检查→部署计划→执行部署→功能验证→持续运维→故障回滚。Trigger for“帮我把这个仓库部署到主机并验收/持续运维/安全升级”。用于跨阶段DevOps/SRE任务，并按需路由到repo-runtime-discovery、target-host-readiness、deployment-executor、deployment-verifier、service-operations、incident-rollback。
compatibility: Requires OpenCode skills support. Typical tools: git, ssh, rsync, curl, jq, Python 3.11+, uv. Optional: docker, docker compose, systemctl, kubectl, helm.
license: Internal use
---

# 作用

这是总控技能，适合宽泛且跨阶段的请求，例如：

- “把这个GitHub repo部署到指定主机”
- “读取当前项目并上线”
- “帮我跑起来并验证是否正常工作”
- “之后继续帮我运维”
- “升级这个服务，失败就回滚”

当任务横跨多个阶段时，使用本技能统一调度。

## 阶段划分

### 阶段1：识别repo与运行模型
优先完成以下事项：

1. 判断repo来源：
   -当前本地工作区
   -用户给出的GitHub URL
   -目标主机上的现有目录
2. 识别技术栈、构建方式、运行入口、测试入口
3. 识别部署信号：
   - `Dockerfile`
   - `compose.yaml` / `docker-compose.yml`
   - `k8s/`, `helm/`, `chart/`
   - `systemd` unit
   - `Makefile`
   - `Procfile`
   - `package.json`, `pyproject.toml`, `go.mod`, `pom.xml`, `Cargo.toml`
4. 识别运行依赖：
   -数据库
   - Redis/MQ
   -文件存储/挂载目录
   -反向代理/ TLS
   -必需环境变量/密钥/配置文件
5. 输出一份部署简报。模板见：
   `assets/deployment-brief-template.md`

如任务收缩为“先读懂repo的运行与部署方式”，转而使用 **`repo-runtime-discovery`** 这个技能。

## 阶段2：检查目标主机是否可部署

至少核对：

- OS /架构/磁盘/内存
-网络连通性
-端口占用
-运行时是否已安装
- Docker/systemd/nginx/kubectl等是否可用
-目标路径是否存在、是否可写
-服务用户、sudo、systemctl、journalctl等权限是否可用

如任务收缩为“只检查目标主机是否具备部署条件”，转而使用 **`target-host-readiness`** 这个技能。

## 阶段3：形成部署计划，先计划再变更

部署前必须明确：

1. **部署方式**
   - Docker单容器
   - docker compose
   - systemd + 虚拟环境/二进制
   - k8s/helm
   - repo自带脚本
2. **目录布局**
   -代码目录
   -配置目录
   -日志目录
   -数据目录
   -发布目录/ current软链
3. **配置与密钥**
   - `.env`
   - config yaml/json/toml
   -证书、token、API key
4. **构建与启动顺序**
5. **回滚点**
6. **验证矩阵**
   -健康检查
   - smoke API
   -页面可访问性
   -日志关键字
   -进程/端口

涉及升级、替换、重启、迁移、删除时，不要直接动手；先写出最小可执行计划。

## 阶段4：执行部署

执行时遵守以下原则：

-先备份/记录现状，再变更
-优先使用repo自带且可信的构建/启动方式
-没有明确证据时，不要擅自发明生产启动参数
-先dry-run或低风险探测，再正式执行
-尽量让部署具备幂等性
-输出完整的执行摘要：命令、路径、结果、异常、下一步

如任务已明确进入执行部署阶段，转而使用 **`deployment-executor`**。

## 阶段5：做功能验证

部署完成后不要仅以“进程已启动”作为成功标准。至少做以下验证中的两类，优先覆盖用户关键路径：

- `/health` 或 `/ready`
-核心API
- Web页面
-关键日志
-端口监听
-后台作业状态
-数据库连接
-反向代理转发

验证失败时，不要宣称部署成功。要么修复再验证，要么进入回滚流程。

如任务已明确进入功能性验证阶段，转而使用 **`deployment-verifier`**。

## 阶段6：持续运维

当用户要求“持续运维/升级/巡检/保持可用”时，继续：

-记录版本与当前状态
-记录配置漂移风险
-记录健康检查入口
-记录常见故障点
-记录升级与回滚命令
-记录证书、磁盘、日志、队列积压、CPU/内存等观察项

如任务已明确进入持续运维阶段，转而使用 **`service-operations`**。

## 阶段7：故障与回滚

出现以下情况时，优先止血：

-健康检查失败
-核心接口失败
-大量错误日志
-启动正常但功能异常
-依赖连接失败
-性能或资源异常

此时转而使用 **`incident-rollback`**。

## 输出结构

默认采用以下结构输出：

```markdown
# 部署与运维报告

## 1. 识别结果
## 2. 目标主机检查
## 3. 部署计划
## 4. 执行结果
## 5. 验证结果
## 6. 回滚点
## 7. 后续运维建议
```

## 关键约束

-不要把“未知”写成“已确认”
-缺少密钥、变量、域名、端口、挂载点时，明确标记为阻塞项
-不要把测试环境假装成生产环境
-不要默认用户有root；需要权限时应明确说明
-不要跳过验证
-不要在没有回滚点的情况下做高风险覆盖式变更

## 轻量检查清单

- [ ] repo已识别
- [ ] 目标主机已探测
- [ ] 部署计划已形成
- [ ] 回滚点已确定
- [ ] 执行已留痕
- [ ] 验证已完成
- [ ] 运维说明已输出
