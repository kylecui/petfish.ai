# repo-service-lifecycle

> 所属包: **deploy**

端到端总控skill：读取repo/GitHub→主机就绪检查→部署计划→执行部署→功能验证→持续运维→故障回滚。Trigger for“帮我把这个仓库部署到主机并验收/持续运维/安全升级”。用于跨阶段DevOps/SRE任务，并按需路由到repo-runtime-discovery、target-host-readiness、deployment-executor、deployment-verifier、service-operations、incident-rollback。

**兼容性:** Requires OpenCode skills support. Typical tools: git, ssh, rsync, curl, jq, Python 3.11+, uv. Optional: docker, docker compose, systemctl, kubectl, helm.

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

*... (完整 SKILL.md 中还有 96 行)*
