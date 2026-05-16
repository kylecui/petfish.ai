---
title: 部署与运维指南
description: 使用 PEtFiSh 部署技能包进行仓库部署的完整指南。
---

# 部署与运维指南 (Deploy & Ops Guide)

**deploy** 包提供了一套完整的技能，用于读取代码仓库、将其部署到目标主机、验证其功能，并进行持续维护。

该技能包并没有假设一种放之四海而皆准的部署策略，而是充当一个智能的 DevOps 工程师。它会分析你的代码库以了解其*应该*如何运行，检查你的基础设施以确保其*可以*运行，制定明确的计划，通过安全检查执行部署，并在宣布任务完成前严格验证结果。

这个包弥合了本地开发与生产现实之间的差距。无论你是在笔记本电脑上快速启动一个 Docker Compose 技术栈，还是在远程 Ubuntu 服务器上执行零宕机的蓝绿部署（Blue/Green deployment），deploy 包都能确保一致性、安全性与运维的严谨性。

```bash
# 安装 deploy 包 (macOS / Linux)
curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack deploy

# 安装 deploy 包 (Windows PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack deploy
```

---

## 概览 (Overview)

deploy 包专为各种任务设计，从“在本地启动这个项目”到“将这个 GitHub 仓库部署到我的 staging 服务器”。它在智能发现、安全执行、真实的 smoke test 以及 Day-2 运维方面表现出色。

### 包内包含什么

deploy 包是模块化的。虽然由编排器（orchestrator）将一切联系在一起，但每个技能都是一个独立的工具，能够在其特定领域内执行深度操作。

| 技能 (Skill) | 目的 (Purpose) | 在流水线中的角色 |
|---|---|---|
| **`repo-service-lifecycle`** | 端到端编排器，将所有其他技能串联起来。它了解完整的生命周期，并在各个步骤之间无缝传递上下文（如发现的技术栈和目标主机）。 | **Orchestrator（编排器）** |
| **`repo-runtime-discovery`** | 扫描代码库，检测技术栈，识别构建步骤，定位数据库需求，并梳理出所需的环境变量。它构建了基础的“部署简报（Deployment Brief）”。 | **步骤 1: Discover（发现）** |
| **`target-host-readiness`** | 检查目标服务器的操作系统架构、可用的 CPU/内存、磁盘空间、端口冲突，以及所需的运行时（如 Docker、Node、Python）。它作为一个安全检查门禁。 | **步骤 2: Check（检查）** |
| **`deployment-executor`** | 执行实际的发布。它安全地应用变更、注入 secrets、管理 systemd 或 docker-compose 进程，并在执行任何破坏性操作前创建严格的 rollback point（回滚点）。 | **步骤 3: Execute（执行）** |
| **`deployment-verifier`** | 证明服务正常运行。它执行 HTTP health check、核心 API smoke test、检查日志中的启动错误，并验证数据库连接。 | **步骤 4: Verify（验证）** |
| **`service-operations`** | 充当你的 Day-2 SRE。它处理日常维护、日志轮转（log rotation）、资源性能分析、依赖升级，以及在零宕机下更新 SSL/TLS 证书。 | **步骤 5: Maintain（维护）** |
| **`incident-rollback`** | 应对故障，稳定崩溃的服务，并在发生严重的 SEV-1 级宕机时执行硬回滚到最后一个已知的安全状态。 | **故障处理** |

### 何时使用此包 vs. 何时不应使用

**在以下情况使用此包：**

- **部署到 VM 或裸机 (Bare Metal)：** 你有一个传统的代码仓库（Node、Python、Go、Java、Rust）并需要将其运行在虚拟专用服务器（AWS EC2、DigitalOcean Droplet、本地 Proxmox VM）或本地 Docker 环境中。
- **从零开始配置：** 你正在设置一台新的 staging 或生产服务器，需要一个智能 Agent 在尝试复制代码前，确保所有前置条件（如特定的 Node 版本、Docker daemon 或 Nginx）均已满足。
- **需要可验证的部署：** 你需要一个结构化的部署流程，在宣布任务“完成”前，能保证服务实际上正在响应请求（通过 HTTP smoke test 和日志跟踪）。
- **管理生产事故：** 你正在响应一次生产宕机（例如 502 Bad Gateway），需要安全地分类、稳定服务，或将部署回滚到最后一个已知正常的 Git commit。
- **执行日常 Day-2 维护：** 你希望对服务进行长期维护。这包括检查应用日志以发现慢查询、准备依赖升级、更新 SSL 证书，以及管理磁盘空间。

**在以下情况不要使用此包：**

- **使用全托管的 PaaS：** 你完全依赖托管的平台即服务 (PaaS)，如 Vercel、Heroku、Render 或 Netlify。这些平台内部已经处理了运行时发现、构建执行和流量切换。
- **开发功能：** 你想要编写或调试应用代码。此包严格处理 DevOps、基础设施和运维工作。如果你需要编写功能代码，请使用默认的 OpenCode 开发技能。
- **绕过安全检查：** 你想在不验证成功与否的情况下盲目运行破坏性脚本。此包强制执行安全检查、回滚点和验证步骤。如果你想绕过这些，请直接使用基本的 `bash` 工具。

---

## 部署执行链 (The Deployment Chain)

该包通过一个严格的确定性流水线运行，旨在消除部署中的盲目猜测。如果你使用 `repo-service-lifecycle` 编排器，它会自动按顺序将上下文和状态通过这些步骤传递。如果你手动请求特定操作（例如，“仅验证此 endpoint”），Agent 将绕过编排器并直接加载相应的单个技能。

```text
User Request ("Deploy this to production")
    │
    ▼
[ repo-service-lifecycle ] (Central Orchestrator)
    │
    ├─ Step 1: repo-runtime-discovery (Analyze the codebase)
    │          ↳ Output: Deployment Brief (Tech stack, Env vars, Build steps)
    │
    ├─ Step 2: target-host-readiness  (Check the target server)
    │          ↳ Output: Readiness Report (CPU, Port conflicts, Runtimes)
    │          ↳ Blocks if prerequisites are missing.
    │
    ├─ Step 3: deployment-executor    (Run the actual deployment)
    │          ↳ Output: Execution Log & Rollback Point
    │          ↳ Backs up previous state, injects secrets, restarts processes.
    │
    ├─ Step 4: deployment-verifier    (Prove the service is running)
    │          ↳ Output: Verification Report (Smoke tests, Log checks)
    │          ↳ Ensures HTTP 200 OK and database connectivity.
    │
    └─ Step 5: service-operations     (Record state & ongoing maintenance)
               ↳ Output: Ops Baseline (Version tracking, Resource profiling)
               │
          (If Step 3 or 4 fails critically)
               │
               └─ incident-rollback   (Revert & stabilize)
                  ↳ Output: Incident Record
                  ↳ Restores the backup created in Step 3.
```

### 上下文传递 (Context Passing)
链中的每个技能都会将其输出传递给下一个技能。例如，`target-host-readiness` 不仅仅检查通用的指标；它还会特别检查上一步 `repo-runtime-discovery` 所确定的确切 Node.js 版本和数据库端口。这种紧密的耦合确保了部署高度贴合你的确切代码仓库。

---

## 生命周期编排器 (Lifecycle Orchestrator)

`repo-service-lifecycle` 技能是一个“让它搞定一切”的入口点。当你提出一个宽泛的部署或运维请求时，Agent 会加载这个编排器来管理从发现到验证的整个流水线。

### 它是如何串联各个步骤的

编排器本身并不执行部署。相反，它充当一个管理者，按顺序委托给专门的技能：

1. 它触发 `repo-runtime-discovery` 以构建部署简报。
2. 它将该简报传递给 `target-host-readiness` 以验证环境。
3. 它将验证通过的计划交给 `deployment-executor`。
4. 它命令 `deployment-verifier` 去证明服务正在运行。
5. 它会根据验证结果使用 `service-operations` 或 `incident-rollback`。

### 示例提示词 (Example Prompts)

=== "部署与验证"

    ```text
    Please deploy this repository to my local machine and verify that it's working.
    ```

=== "远程配置与部署"

    ```text
    Help me deploy this GitHub repo to ubuntu@10.0.0.5. Make sure the server has what it needs first, then get it online and verified.
    ```

=== "持续维护"

    ```text
    Take ownership of the service running on port 8080. Verify its health, check the recent logs, and establish a baseline for continuous operations.
    ```

---

## 快速上手 (Quick Start)

### 示例 1: 本地 Docker 部署

如果你只是想利用现有的 Docker 配置在本地运行项目，以进行测试或开发：

=== "Prompt"

    ```text
    Deploy the current repository to my local Docker environment and verify it works.
    ```

=== "Expected Behavior"

    1. Agent 加载 `repo-service-lifecycle`。
    2. 它扫描你的代码仓库以找到 `Dockerfile` 或 `docker-compose.yml`。
    3. 它检查本地 Docker 是否正在运行，并确保你的主机 OS 没有被占用 80/443（或目标端口）。
    4. 它构建容器镜像（`docker build -t myapp .`）并启动容器（`docker run -d`）。
    5. 它积极地 curl 本地 endpoint（`http://localhost:8080/health`）直到应用不再返回 `502` 并且返回 `200 OK`。
    6. 它提供一个结构化的部署总结，包括映射的端口以及用于跟踪日志的命令（例如 `docker logs -f myapp`）。

### 示例 4: 部署后验证 (Post-Deploy Verification)

有时你手动部署了代码，但希望 Agent 来处理严格的验证阶段。

=== "Prompt"

    ```text
    I just deployed the new backend to production. Run a deep verification on https://api.example.com to ensure everything is stable.
    ```

=== "Expected Behavior"

    1. Agent 直接加载 `deployment-verifier`（绕过发现和执行阶段）。
    2. 它在提供的 URL 上执行 HTTP 检查，验证 SSL 证书的有效性。
    3. 它运行一些基础 API 调用（例如 `GET /api/v1/status`）以检查 JSON 响应结构。
    4. 它通过 SSH 连接到主机（如果在上下文中提供了凭据），以检查应用日志中是否有隐性错误。
    5. 它汇总一份“验证报告 (Verification Report)”以确认系统已完全恢复运行。

### 示例 2: 远程 SSH 部署

部署到远程服务器时，你必须提供目标主机和用户。Agent 使用你本地机器上现有的 SSH 配置（如 `~/.ssh/config` 或加载在 `ssh-agent` 中的身份）来安全地进行连接。

=== "Prompt"

    ```text
    Deploy this repository to staging-user@192.168.1.50. You can use my local SSH keys. We need it running on port 3000.
    ```

=== "Expected Behavior"

    1. Agent 通过 SSH 连接到 `192.168.1.50`。
    2. 它验证远程主机上是否安装了 Node.js 或 Docker。
    3. 它检查 `3000` 端口是否可用。
    4. 它通过 `rsync` 复制代码或通过 `git` 克隆。
    5. 它安装依赖，构建项目，并启动服务。
    6. 它运行远程验证脚本以确保端口正在响应。

### 示例 3: 蓝绿部署 / 零宕机部署

对于生产系统，通常即使进程重启几秒钟的宕机也是无法承受的。Agent 可以编排零宕机发布。

=== "Prompt"

    ```text
    Execute a zero-downtime deployment for this Python API. Start the new version on a temporary port, wait for it to be healthy, and then hot-swap the Nginx upstream to point to the new port before stopping the old version.
    ```

=== "Expected Behavior"

    1. Agent 读取当前 Nginx 配置以找到活动的端口（例如 `8001`）。
    2. 它部署新的代码库并在辅助端口（例如 `8002`）上启动新进程。
    3. 它不断轮询 `localhost:8002/health` 直到返回 200 OK。
    4. 在健康后，它修改 `/etc/nginx/sites-available/api` 使其指向 `:8002`。
    5. 它执行 `nginx -t` 以验证语法，然后执行 `systemctl reload nginx` 进行无缝的流量切换。
    6. 它安全地终止运行在 `8001` 上的旧进程。

??? example "刚才发生了什么？(The Chain Explained)"
    当你发出命令时，Agent 并不只是运行 `docker compose up`。它遵循该包要求的严格纪律：
    
    - 它运行了 **Discovery（发现）** 以确保它知道*如何*构建应用。
    - 它运行了 **Readiness（就绪性）** 以确保远程主机拥有正确的架构并且磁盘没有满。
    - 它运行了 **Executor（执行器）** 来应用变更，并确保记录其部署的 git commit hash。
    - 它运行了 **Verifier（验证器）** 以确认应用程序实际上正在响应 HTTP 请求，而不是仅仅检查进程 ID 是否存在。

!!! tip "明确指定目标"
    Agent 无法魔法般地知道你的服务器凭证。如果在远程部署，请提供 SSH 主机并确保你的环境已经配置了必要的 SSH 密钥。
    示例：`Deploy this to user@10.0.0.5`

---

## 步骤 1: 发现你的仓库 (Discover Your Repo)

在触碰任何服务器之前，Agent 必须了解它正在部署什么。这是由 **`repo-runtime-discovery`** 处理的。

它会扫描本地或远程仓库，以识别技术栈、入口点、配置需求、数据库依赖以及健康检查端点。如果在项目中缺失了必要的环境变量，它会发出警告。

### 将会被检测到什么

当 `repo-runtime-discovery` 运行时，它会寻找特定的文件和模式，来确定应用程序该如何构建和执行。以下是 Agent 在发现阶段确切要寻找的内容：

- **`Dockerfile` / `.dockerignore`**: 表明该项目已容器化。Agent 会检查基础镜像、暴露端口以及 entrypoint 命令。它还会寻找多阶段构建以优化最终镜像大小。
- **`docker-compose.yml` / `compose.yaml`**: 暗示多容器技术栈。Agent 会解析它以了解服务依赖（例如需要 Redis 或 PostgreSQL）、持久化命名卷以及自定义网络桥接。
- **`package.json` / `yarn.lock` / `pnpm-lock.yaml`**: 识别出 Node.js 项目。Agent 会读取 `scripts` 块以找到 `build`、`start` 和 `test` 命令。它会检查 Next.js、NestJS 或 Express 等框架以确定运行时要求。
- **`requirements.txt` / `pyproject.toml` / `Pipfile`**: 识别出 Python 应用。Agent 检查 Django、Flask 或 FastAPI 等框架以确定最佳的 WSGI/ASGI 服务器（如 gunicorn、uvicorn）。
- **`go.mod` / `go.sum`**: 识别出 Go 项目。Agent 寻找用于编译的 `main` 包位置，并检查是否需要 CGO。
- **`build.gradle` / `pom.xml`**: 识别出 Java/Kotlin 项目。Agent 寻找 Spring Boot 或 Quarkus 签名以定义 Maven/Gradle 构建命令以及最终 `.jar` 制品位置。
- **`Makefile`**: 一个通用的任务运行器。如果存在，Agent 将寻找标准的目标任务如 `make build`、`make run` 和 `make clean`。
- **Systemd Units (`*.service`)**: 如果 `.service` 文件被提交到了仓库中，Agent 会假定你希望直接使用 Systemd 部署到主机 OS，并解析 `ExecStart` 和 `EnvironmentFile` 指令。
- **Kubernetes Manifests (`k8s/`, `helm/`, `*.yaml`)**: 表明使用了 Kubernetes 部署策略。Agent 会读取 Deployments、Services 和 Ingresses 以映射集群拓扑。
- **`Procfile`**: 经常被 Heroku 或 PM2 使用，用来定义进程类型（例如 `web`, `worker`）。

!!! info "自定义配置文件"
    发现阶段也会扫描常见的配置文件，如 `.env.example`、`config.yml`、`nginx.conf` 和 `prometheus.yml`。它会将这些与应用代码进行交叉引用，以识别所需的环境变量，并在部署开始前就向你警告缺失的 secrets。

### 处理特定框架

发现技能为现代框架应用了定制的逻辑，以确保实现最佳的部署：

- **Next.js / Nuxt.js**: 检测应用是否配置了静态导出（`next export`）或是否需要 Node.js 服务器。它会确保在部署前调用了 `npm run build`。
- **Django / Flask**: 寻找 `wsgi.py` 或 `asgi.py`，并建议使用 Gunicorn 或 Uvicorn，而不是内置的开发服务器。它还会检查 `manage.py migrate` 的需求。
- **Spring Boot**: 识别 `.jar` 的位置，并确保 `java -jar` 命令包含了标准的生产环境标志（如内存限制 `-Xmx`）。
- **React / Vue / Vite**: 如果检测到了纯前端项目，它会建议使用静态服务策略（例如通过 Nginx 部署）而不是运行一个 Node.js 进程。

### 示例提示词

=== "本地分析"

    ```text
    Analyze this repository and tell me what we need to deploy it.
    ```

=== "远程 GitHub 分析"

    ```text
    Look at the repository https://github.com/example/api-service. What is required to run it in production?
    ```

=== "查找配置缺口"

    ```text
    Review our current codebase. What environment variables or configuration files are missing before we can deploy this?
    ```

??? example "示例输出"

    ```markdown
    ## 部署简报 (Deployment Brief): `api-service`
    
    ### Tech Stack
    - **Language:** TypeScript / Node.js (v18+)
    - **Framework:** Express
    - **Database:** PostgreSQL
    
    ### Entry Points
    - **Build:** `npm run build` (compiles to `./dist`)
    - **Run:** `npm start` (executes `node dist/index.js`)
    - **Dev:** `npm run dev`
    
    ### Dependencies & Configuration
    - **Database:** Requires a PostgreSQL instance.
    - **Environment Variables Required:**
      - `DATABASE_URL` (Missing)
      - `JWT_SECRET` (Missing)
      - `PORT` (Defaults to 3000)
    
    ### Health Endpoints
    - `/api/health` returns `{"status": "ok"}`
    
    ### Proposed Deployment Strategy
    The repository contains a `docker-compose.yml` that defines both the API and a PostgreSQL database. The recommended approach is to deploy using Docker Compose.
    ```

!!! tip "提供文档"
    如果你的仓库有 `DEPLOY.md` 或架构图，在发现阶段将其指向 Agent。它会将你的自定义指令合并到“部署简报”中。

---

## 步骤 2: 检查主机就绪性 (Check Host Readiness)

在明确部署策略后，Agent 借助 **`target-host-readiness`** 检查目标服务器是否实际上有能力运行代码。

它会验证 OS 架构、CPU/内存/磁盘空间、端口冲突、所需的运行时（Docker、Node、Python、Systemd）以及写权限。

### 将会被检查的内容

当 `target-host-readiness` 运行时，它的行为就像一位经验丰富的系统管理员，确保服务器不会在部署下崩溃。以下是具体执行的检查：

- **系统资源 (System Resources)**:
    - **CPU 与负载平均值**: 检查 `uptime` 和 `top`。如果服务器的 CPU 利用率已经达到了 99%，Agent 会警告你，添加新进程可能会使主机崩溃。
    - **内存 (RAM)**: 运行 `free -m`。它会计算可用内存是否能轻松支持新的应用程序，特别是对于基准开销很高的 Java 或 Node.js 应用。
    - **磁盘空间**: 运行 `df -h`。如果一个部署需要解压 2GB 的 Docker 镜像，但只有 1GB 可用空间，就会失败。Agent 会阻止部署以防止损坏服务器的根文件系统。
- **端口可用性**: 使用 `ss -tulpn` 或 `lsof -i` 以验证目标端口（例如 `80`、`443`、`3000`）确实是空闲的。它能识别出冲突的进程（比如旧的 Nginx 进程占据了 80 端口）。
- **运行时与依赖**:
    - **Docker**: 验证 `docker version` 和 `docker compose version`。检查当前用户是否有权连接到 Docker daemon (`docker ps`)。
    - **语言运行时**: 运行 `node -v`、`python3 --version` 或 `go version`。它会严格将这些版本与部署简报中要求的版本进行比对。
    - **服务管理器**: 检查是否安装并运行了 `systemd` 或 `pm2`。
- **权限**: 验证部署用户拥有对目标部署目录（例如 `/opt/myapp`）的写访问权限，以及通过 `sudo` 重启服务或重载代理的权限。

!!! warning "严谨模式就绪性"
    deploy 包在 fail-safe（失效安全）模式下运行。如果检测到了关键前置条件缺失（如缺少运行时或存在端口冲突），Agent 将 **阻止 (block)** 部署。除非收到明确指示，否则它不会尝试随机猜测如何安装依赖。

### 示例提示词

=== "检查远程需求"

    ```text
    Check if 192.168.1.100 is ready for our Node.js deployment. We need port 3000 and Node v18.
    ```

=== "Docker 起飞前检查"

    ```text
    Verify the local machine can run our docker-compose stack. Make sure ports 80 and 443 are free.
    ```

=== "容量规划"

    ```text
    Assess the production server at user@prod.internal. Do we have enough disk space and memory to deploy a new Java Spring Boot container?
    ```

??? example "示例输出"

    ```markdown
    ## Host Readiness Report: `192.168.1.100`
    
    ### System Resources
    - **OS:** Ubuntu 22.04 LTS (x86_64)
    - **CPU:** 4 Cores (Load average: 0.45) - **PASS**
    - **Memory:** 8GB total, 4.2GB available - **PASS**
    - **Disk Space:** 50GB total, 4.1GB available - **WARNING** (Low disk space)
    
    ### Runtimes & Dependencies
    - **Node.js:** v14.19.0 installed - **BLOCKER** (v18+ required by codebase)
    - **NPM:** v6.14.16 installed - **BLOCKER**
    - **Docker:** v24.0.5 installed - **PASS**
    
    ### Network & Ports
    - **Port 3000:** IN USE by PID 1452 (node) - **BLOCKER**
    
    ### Conclusion
    The host is **NOT READY** for deployment.
    
    **Required Actions Before Execution:**
    1. Upgrade Node.js to v18.
    2. Free up or reassign port 3000 (currently used by another Node process).
    3. Monitor disk space.
    
    Would you like me to attempt fixing these blockers?
    ```

!!! warning "不要忽略阻碍项 (Blockers)"
    如果 Agent 标记了一个阻碍项，不要强迫它继续。在转移到执行阶段前，让 Agent 解决该阻碍（例如，“Kill the process on port 3000 and install Node 18”）。

---

## 步骤 3: 执行部署 (Execute Deployment)

有了计划并且主机就绪后，**`deployment-executor`** 将执行实际的上线。

它遵循严格的 `Plan → Validate → Execute` (计划 → 验证 → 执行) 循环。它会记录当前状态、创建一个 rollback point（回滚点）、推送代码、注入配置并启动服务。

### 回滚点和状态记录

在执行任何破坏性命令之前，Agent 会创建一个回滚点。通常包括：

- 将现有的二进制文件或 release 目录复制到备份文件夹（例如 `release_backup_20260515/`）。
- 如果计划进行数据库迁移，则导出当前的数据库 schema 状态。
- 保存*上一次*部署的确切 Git commit hash。
- 记录使用过的确切命令，以便可以反向执行。

### 部署策略

Agent 会根据发现阶段自动选择最佳的部署策略，但你也可以明确指定使用某种特定方法。每种策略都附带其自己的验证检查和回滚程序。

=== "Docker Compose"
    多容器技术栈的首选方法。
    
    ```text
    Execute the deployment using docker-compose. Rebuild the images and recreate the containers without dropping the database volume.
    ```
    
    ```markdown
    **Agent Action:**
    1. Validates the `docker-compose.yml` syntax using `docker compose config`.
    2. Runs `docker compose pull` to fetch any updated base images from registries.
    3. Runs `docker compose build --pull` to compile the application image.
    4. Runs `docker compose up -d --remove-orphans` to start the new containers.
    5. Verifies container health states using `docker compose ps`.
    
    *Rollback Strategy:* The agent tags the previous image and can instantly revert by running `docker compose up -d` with the old tag.
    ```

=== "Systemd Service"
    裸机二进制文件（如 Go、Rust）或直接进行主机部署（没有容器开销）的最佳方法。
    
    ```text
    Deploy the compiled binary to /opt/myapp and set it up as a systemd service named myapp.service. Make sure it runs as a non-root user.
    ```
    
    ```markdown
    **Agent Action:**
    1. Creates a dedicated service user: `useradd -r -s /bin/false myapp_user`.
    2. Copies the compiled binary to `/opt/myapp/myapp` and sets ownership.
    3. Generates `/etc/systemd/system/myapp.service` with `User=myapp_user` and `Restart=always`.
    4. Runs `systemctl daemon-reload` to register the service.
    5. Runs `systemctl restart myapp` to apply changes.
    6. Runs `systemctl enable myapp` to ensure it starts on boot.
    
    *Rollback Strategy:* The agent moves the old binary to `/opt/myapp/backups/myapp_old` before copying the new one, allowing a simple file swap and restart if the new binary fails.
    ```

=== "PM2 / Process Manager"
    常用于直接运行在主机上的 Node.js 应用，提供集群功能和自动重启。
    
    ```text
    Use PM2 to deploy the Node.js app. Make sure it runs in cluster mode with 4 instances to utilize all CPU cores.
    ```
    
    ```markdown
    **Agent Action:**
    1. Verifies PM2 is installed globally (`pm2 -v`).
    2. Runs `npm ci` to cleanly install dependencies without modifying the lockfile.
    3. Runs `npm run build` to compile TypeScript or bundle assets.
    4. Executes `pm2 start ecosystem.config.js --env production -i 4` or `pm2 start dist/index.js -i 4 --name "api"`.
    5. Runs `pm2 save` to persist the process list across system reboots.
    
    *Rollback Strategy:* The agent can issue a `pm2 reload api` to perform a zero-downtime reload, or revert to a previous Git commit and run the build steps again.
    ```

=== "手动 / 自定义脚本"
    如果你的仓库有一个高度指定的部署脚本（例如 Ansible、Capistrano 或 Bash），指示 Agent 使用它。
    
    ```text
    Deploy using the ./scripts/deploy-prod.sh script. Pass the `--force` flag.
    ```
    
    ```markdown
    **Agent Action:**
    1. Grants execute permissions: `chmod +x ./scripts/deploy-prod.sh`.
    2. Analyzes the script to understand its side effects before running.
    3. Executes `./scripts/deploy-prod.sh --force`.
    4. Captures `stdout` and `stderr`, tracking the exit code.
    
    *Rollback Strategy:* Depends entirely on the custom script. The agent will ask you for a rollback script (e.g., `./scripts/rollback-prod.sh`) before proceeding.
    ```

### 权限与身份验证

执行器需要足够的权限来修改主机系统。根据你的部署策略，Agent 会自动处理权限：

- **Sudo 权限**: 当修改 `/etc/systemd/system/` 或 `/etc/nginx/` 时，Agent 会在命令前加 `sudo`。你必须确保连接的用户具有无需密码提示的 `sudo` 权限，否则部署将陷入停滞。
- **Docker 用户组**: 如果通过 Docker 进行部署，连接用户应该是 `docker` 组的成员，以避免每个 `docker` 命令都需要加 `sudo`。
- **远程镜像仓库**: 如果从私有仓库（如 AWS ECR 或 GitHub Container Registry）拉取镜像，Agent 可以执行所需的 `docker login` 步骤，前提是你在初始提示词中安全地传递了凭据。
- **SSH 转发**: 如果 Agent 需要在远程服务器上直接克隆一个私有 Git 仓库，它默认会使用你本地的 `ssh-agent` 转发，从而消除了将私钥复制到服务器的需要。

### 示例提示词

=== "执行 Docker Compose"

    ```text
    Execute the deployment to the staging server using docker-compose. Use the existing config.
    ```

=== "零宕机上线"

    ```text
    Deploy the latest master branch to the production VM. Use a blue-green strategy with Nginx so we don't drop traffic.
    ```

=== "注入 Secrets"

    ```text
    Deploy the worker service. Inject the secrets from the local `.env.prod` file into the target host before starting the systemd service.
    ```

??? example "示例输出"

    ```markdown
    ## Execution Plan
    
    1. **Rollback Point:** Create a tarball of `/opt/api-service/current` to `/opt/api-service/backups/release_20260515.tar.gz`.
    2. **Transfer:** Rsync local `./dist` to remote `/opt/api-service/new`.
    3. **Config:** Write injected `DATABASE_URL` to `/opt/api-service/new/.env`.
    4. **Execute:** Stop current service, swap symlinks, restart systemd service `api-service`.
    
    *Executing...*
    
    ## Execution Result
    
    - **Status:** SUCCESS
    - **Deployed Version:** Git commit `a1b2c3d4`
    - **Rollback Point:** `/opt/api-service/backups/release_20260515.tar.gz`
    - **Commands run:** `systemctl restart api-service`
    
    The service has been started. Proceeding to verification.
    ```

!!! tip "检查执行计划"
    当使用 `deployment-executor` 时，Agent 通常会在运行命令之前输出一个计划。在确认“放手去干”之前，花点时间阅读一下它，特别是在生产环境中。

---

## 步骤 4: 验证 (Verify)

进程没有立刻崩溃，并不代表部署就完成了。**`deployment-verifier`** 会证明该服务实际上是可用的。

它执行 health/readiness 检查、核心 API smoke test、日志审查以及依赖验证（检查它是否成功连接到了 Redis/DB）。

### 将会被验证的内容

验证不仅仅是检查进程 ID 是否存在。`deployment-verifier` 技能执行多层检查以确保真实的可用性：

- **进程与服务状态**: 检查 `systemctl status`、`pm2 list` 或 `docker ps` 以确保进程正在运行，没有持续重启，也没有以错误码退出。
- **端口绑定**: 运行 `netstat`、`ss` 或 `lsof` 来确认应用成功绑定到了预期的端口（如 `3000`）。
- **HTTP Smoke Tests**: 向 health endpoint（`/health`、`/ping`、`/api/status`）发起 `curl` 或 `wget` 请求。它会检查 `200 OK` 状态码，并解析 JSON 响应来确认深层次的健康状况（例如 `{"database": "connected"}`）。
- **日志检查**: 读取应用日志的结尾（通过 `journalctl`、`docker logs` 或是对文件进行 tail）。它使用模式匹配寻找在启动期间出现的致命错误、缺失的模块或未处理的异常。
- **依赖握手**: 检查日志或运行特定命令以确保应用成功连接到了它的数据库（PostgreSQL、MySQL）、缓存（Redis、Memcached）或消息队列（RabbitMQ、Kafka）。
- **反向代理路由**: 如果涉及到 Nginx 或 Traefik，它会验证代理正在成功地将外部请求路由给新部署的应用，并且没有返回 `502 Bad Gateway`。

### 示例提示词

=== "标准验证"

    ```text
    Verify the deployment we just did.
    ```

=== "自定义 Smoke Test"

    ```text
    Run a smoke test on the new deployment. Check the `/api/health` endpoint and verify that the `/api/users` endpoint returns a 200 OK.
    ```

=== "日志验证"

    ```text
    Verify the service started cleanly by checking the systemd logs. Make sure there are no database connection errors.
    ```

=== "深度依赖检查"

    ```text
    Perform a deep verification. Ensure the API returns 200, check the last 100 lines of logs for any memory warnings, and confirm the Redis connection is established by running `redis-cli ping` inside the cache container.
    ```

??? example "示例输出"

    ```markdown
    ## Verification Report
    
    ### Process Health
    - **Systemd Service:** `api-service.service` is **ACTIVE (running)**.
    - **PID:** 4512
    
    ### Network & API Smoke Test
    - **Port Check:** Port 3000 is listening.
    - **Health Endpoint:** `GET http://localhost:3000/api/health` returned `200 OK`.
      - Response body: `{"status":"healthy","db":"connected"}`
    
    ### Log Verification
    - Scanned last 50 lines of journalctl for `api-service`.
    - Found expected startup line: `Server listening on port 3000`.
    - **No ERROR or FATAL log entries found.**
    - Database connection verified in logs: `Connected to PostgreSQL pool`.
    
    ### Conclusion
    The deployment is **VERIFIED AND SUCCESSFUL**. Service is fully operational.
    ```

!!! warning "不要跳过验证"
    如果在步骤 3 之后你手动打断了 Agent，那你就是在盲目飞行。总是让 Agent 运行 verifier 来确保一个干净的交接，并及早捕捉配置错误。

---

## 步骤 5: 日常运维 (Ongoing Operations)

对于 Day-2 任务，**`service-operations`** 就充当你的 Site Reliability Engineer (SRE)。

它负责持续的维护工作、追踪版本历史、检查健康状况、管理证书以及为将来的升级做准备。

### Day-2 职责

- **日志审阅**: 扫描应用日志以发现异常、内存泄漏或慢查询。
- **升级准备**: 在尝试打补丁前验证当前版本和依赖。
- **证书检查**: 确保 SSL/TLS 证书（例如 Let's Encrypt）有效并在快过期时续期。
- **资源性能分析**: 检查服务的内存使用量是否正在爬升或正耗尽文件描述符。

### 常见的运维食谱 (Common Operations Recipes)

一旦服务在生产环境中变得稳定，你将例行进行维护。可以使用这些“食谱”指导 Agent 完成 Day-2 操作，以确保高可用性和系统健康。

??? example "食谱：日志轮转与清理磁盘"
    服务器经常因为应用日志填满磁盘而崩溃。你可以主动指示 Agent 安全地腾出空间。
    
    **Prompt:**
    ```text
    The server disk space is at 85%. Please find old application logs in /var/log/myapp, compress them, delete anything older than 30 days, and run `docker system prune -a --volumes` to clear unused Docker images.
    ```
    
    **Agent Behavior:**
    Agent 会定位日志位置，执行压缩（`tar -czf`），安全删除旧文件（`find /var/log/myapp -name "*.log" -mtime +30 -delete`），并清理 Docker 缓存。之后它会报告回收的磁盘空间。
    
    **Sample Output:**
    ```markdown
    - Compressed 14 log files into `archive-2026-05.tar.gz`.
    - Deleted 28 files older than 30 days.
    - Cleared 3.4GB of dangling Docker images and stopped containers.
    - **Result:** Disk usage reduced from 85% to 62%.
    ```

??? example "食谱：无中断依赖更新"
    当发布了一个安全补丁时，你需要更新依赖而不让系统宕机。
    
    **Prompt:**
    ```text
    We need to update the `express` package to v4.21.0 due to a CVE. Review the package.json, perform the update locally, run the unit tests, and if they pass, draft a plan to deploy the updated container to production without downtime.
    ```
    
    **Agent Behavior:**
    Agent 扮演了一个开发-SRE混合的角色。它修改 `package.json`，重新安装依赖，执行 `npm test`，并且利用 Docker Compose 或 Nginx upstream 切换，构建一份零宕机的部署计划。它会确保新容器变得健康之后才终止旧容器。

??? example "食谱：备份验证与数据恢复"
    如果不能恢复，那么备份就毫无用处。定期的验证是关键的运维任务。
    
    **Prompt:**
    ```text
    Test our database backup strategy. Download the latest PostgreSQL dump from AWS S3, spin up a temporary local PostgreSQL container, restore the dump, and verify that the `users` table has data.
    ```
    
    **Agent Behavior:**
    1. 使用 AWS CLI 下载 `.sql.gz` 文件。
    2. 启动 `docker run -d --name test-db -e POSTGRES_PASSWORD=test postgres:15`。
    3. 使用 `gunzip -c dump.sql.gz | docker exec -i test-db psql -U postgres` 将备份流式写入容器。
    4. 运行 `SELECT count(*) FROM users` 查询证明备份是可用的。
    5. 销毁临时的容器。

??? example "食谱：容量扩展与负载均衡"
    随着流量激增，服务需要更多的资源。
    
    **Prompt:**
    ```text
    Traffic is spiking. Scale the `api_worker` service in docker-compose from 2 replicas to 6 replicas. Verify that the Nginx load balancer recognizes the new instances.
    ```
    
    **Agent Behavior:**
    Agent 执行 `docker compose up -d --scale api_worker=6`。接着它检查 Nginx 或 Traefik 日志以确认新的 upstream target 已经被注册且正在接收 HTTP 请求。它监控扩展后的 CPU 和内存使用率，以确保主机没有过载。

??? example "食谱：续期 SSL/TLS 证书"
    证书过期会导致立即宕机以及浏览器的安全警告。
    
    **Prompt:**
    ```text
    Check the Let's Encrypt certificates managed by Certbot. If any expire in the next 15 days, force a renewal and reload the Nginx service.
    ```
    
    **Agent Behavior:**
    Agent 运行 `certbot certificates` 来解析过期日期。如果需要续约，它运行 `certbot renew`。最后，它执行 `systemctl reload nginx` 在不丢弃活跃连接的情况下应用新的证书。

### 示例提示词

=== "常规 SRE 检查"

    ```text
    Do a routine check on the production service. Grab the latest logs and check resource usage.
    ```

=== "升级准备"

    ```text
    We need to upgrade the database next week. Review the current operations state, check the exact versions running, and give me an upgrade prep report.
    ```

=== "证书与配置检查"

    ```text
    Check the SSL certificates for the Nginx proxy. Are they expiring soon? Also verify the configuration syntax is valid.
    ```

??? example "示例输出"

    ```markdown
    ## Operations Inspection Report
    
    ### Service State
    - **Target:** `api-service` (Docker container)
    - **Uptime:** 14 days, 3 hours
    - **Current Version:** `v1.2.4` (Commit `f8e9d0c`)
    
    ### Resource Utilization
    - **CPU:** Normal (0.2%)
    - **Memory:** 450MB / 1GB Limit - **Stable**
    - **Disk I/O:** Normal
    
    ### Log Anomalies
    - Scanned last 24 hours of logs.
    - **Notice:** Found 14 occurrences of `WARN: API rate limit exceeded for IP`. This is normal traffic behavior but might warrant adjusting rate limits.
    - No critical crashes or restarts detected.
    
    ### Certificate Status
    - **Domain:** `api.example.com`
    - **Issuer:** Let's Encrypt
    - **Expires In:** 45 days (Renewal not yet required).
    
    ### Recommendations
    Service is healthy. No immediate operational actions required.
    ```

!!! tip "安排常规检查"
    养成让 Agent 对你的关键服务每周“进行一次例行运维检查”的习惯。它往往会在内存泄漏或磁盘空间不足导致宕机前提前发现问题。

---

## 故障处理 (Handling Failures)

如果一次部署失败，或者某个服务在生产环境崩溃，**`incident-rollback`** 技能就会接管。它强调“优先稳定，后深挖调试”。

### 严重性等级和分类流程 (Severity Levels and Triage Flow)

当被调用时，Agent 根据严重性对问题进行分类。它使用结构化的决策树来确定是应该就地调试问题，还是立即执行硬回滚。

1. **严重宕机 (SEV-1):** 
    - **症状:** 服务完全无响应，返回 502/503/504 错误，容器陷入快速崩溃循环，或主机内存耗尽。
    - **Agent 行动:** 立即回滚到先前的稳定状态。Agent 将恢复服务置于寻找根本原因之前。一旦服务在旧版本上恢复稳定，Agent 将下载出错的日志以供离线分析。
2. **性能降级 (SEV-2):** 
    - **症状:** 服务运行中但响应缓慢，某些 API 路由返回 500，或数据库连接池耗尽。
    - **Agent 行动:** 在进行完整回滚之前尝试快速稳定。Agent 可能会重启服务、清理膨胀的缓存、扩容实例或者恢复某个特定的配置文件（如 Nginx 路由规则）。如果在 2 分钟内未能稳定，则升级至 SEV-1 级别并进行回滚。
3. **轻微问题 (SEV-3):** 
    - **症状:** 非致命 Bug，轻微的 UI 错位，或日志中不会影响主干路径的孤立警告。
    - **Agent 行动:** 标准的调试。Agent 将读取日志、提出补丁建议并在不中止当前运行状态下执行一次 hotfix（热修复）部署。

### 自动 vs. 手动回滚

如果编排器正在执行部署而且步骤 4（Verifier）彻底失败了（如 health check 返回了 500），Agent 将会自动触发回滚程序。如果你在几个小时之后才发现问题，你也可以手动调用它。

### 诊断常见故障

当部署失败时，Agent 会试图诊断该问题。以下是 `incident-rollback` 技能所处理的最常见的失败模式以及你该如何指引它。

| 错误模式 | 可能原因 | 建议的 Agent 动作 |
|---|---|---|
| **`502 Bad Gateway`** on health check | 应用进程在启动后立即崩溃，或者反向代理配置错误。 | *"Check the application container logs for immediate crashes. If none, check the Nginx error logs for upstream connection issues."* |
| **`Connection Refused`** to database | 数据库容器尚未就绪，凭据有误，或缺失了网桥网络。 | *"Verify the database host is resolvable from the app container. Check if the database migration ran successfully, and ensure the DB port is exposed."* |
| **`ENOSPC: no space left on device`** | 主机磁盘已 100% 满，阻止了新日志写入、构建或生成新容器。 | *"Abort deployment. Run `df -h` and `docker system prune -a --volumes` to clear space. Check `/var/log` for bloated log files, then retry."* |
| **`EADDRINUSE: port is already allocated`** | 旧版本的应用仍在运行中，或者另一个服务抢占了该端口。 | *"Find the PID using port 3000 (`lsof -i :3000`), kill it gracefully (`kill -15`), and restart the service."* |
| **`Invalid signature` / `Unauthorized`** | 缺失或错误的环境变量（例如缺少 API 密钥或错误的 JWT secret）。 | *"Check if the `.env` file was successfully injected. Compare the remote `.env` keys with the local template to identify missing secrets."* |
| **`OOMKilled` (Out of Memory)** | 应用程序消耗的内存超过了容器或主机允许的范围。 | *"Check `dmesg -T \| grep -i oom`. If confirmed, increase the memory limit in `docker-compose.yml` or allocate swap space on the host."* |
| **`Error: ENOTFOUND`** | DNS 解析失败，通常由于配置错误的 Docker 网桥或缺失的 `/etc/hosts` 条目。 | *"Ping the target hostname from within the container. Verify the Docker network configuration and custom DNS settings."* |

### 事故后回顾 (Post-Incident Review, PIR)

在一次成功的系统维稳或回滚后，Agent 不仅仅会停下来。它将自动生成一份“事故记录”，总结出现了什么差错、采取了什么措施以及在下一次尝试部署之前需要修复什么。这份记录为你团队的事故后回顾（PIR）打下了基础。

它还会指出失败到底是由于基础设施（例如内存耗尽）还是应用逻辑（例如缺失了一个环境变量）导致的。

### 示例提示词

=== "手动回滚"

    ```text
    The site is returning 502s after the last deploy. Fix it or roll it back.
    ```

=== "对生产事故进行分级"

    ```text
    Users are reporting the login API is timing out. Investigate the incident and stabilize the service immediately.
    ```

=== "恢复配置"

    ```text
    The new Nginx config we applied is dropping traffic. Roll back to the previous configuration backup immediately.
    ```

??? example "示例输出 (Incident Record)"

    ```markdown
    ## Incident Record & Rollback
    
    ### Incident Triage
    - **Issue:** Health check on `/api/health` failing with `502 Bad Gateway`.
    - **Logs:** App container is in a crash loop. Error: `Missing environment variable: STRIPE_API_KEY`.
    - **Severity:** CRITICAL (Service Down).
    
    ### Actions Taken (Stabilization)
    - Attempted to inject missing key, but key was not available in context.
    - **Decision:** Executing rollback to previous stable state to restore service.
    
    ### Rollback Execution
    1. Stopped failing container `api-service-v1.3.0`.
    2. Restored previous container `api-service-v1.2.9` from backup image.
    3. Reverted Nginx routing.
    
    ### Current State
    - **Status:** RESTORED
    - Service is back online running previous version (`v1.2.9`). 
    - Smoke tests pass.
    
    ### Follow-up Required
    The deployment failed due to a missing `STRIPE_API_KEY` in the production environment. Please provide this key securely before attempting the deployment again.
    ```

---

## 提示与最佳实践 (Tips & Best Practices)

??? example "处理私有代码仓库"
    如果 Agent 需要将私有的 GitHub 仓库部署到一台远程服务器上，它就需要获得访问权限。你可以使用 ssh-agent 转发，或是直接告诉 Agent： 
    *"Use a Personal Access Token stored in the `$GITHUB_TOKEN` environment variable on the server to clone the repo."*

??? example "网络重试"
    网络操作偶尔会失败。deploy 包被指示在彻底放弃或改变部署策略之前，必须**重试临时的网络故障**（如 SSH 超时、`apt install` 卡住、`docker pull` 错误）至少两次。如果第一次 SSH 尝试超时了，请不要惊慌。

??? example "多服务部署"
    在处理微服务时，请给予 Agent 明确指示。
    *"Deploy the backend service first, verify its database connection, and only then deploy the frontend React application."* 
    编排器将依次处理这些依赖。

??? example "安全处理数据库迁移"
    绝不能让 Agent 在生产环境中盲目运行具有破坏性的迁移。
    *"Run the deployment, but pause before running Prisma migrations. I want to review the SQL output first. Once I approve, you can execute the migration and verify."*
    设定这条边界可以确保模式的修改不会在流量高峰期内无意间删除表、重命名重要列或是锁定数据库。你也可以指示 Agent 在迁移执行*前*去运行一次数据库备份。

??? example "环境变量管理"
    千万别把生产环境的 secrets 粘贴在聊天窗口中。这样做既不安全又会将 secrets 留存在你的聊天历史里。
    *"The secrets are located in `/etc/secrets/.env.prod` on the remote host. Inject them during the deployment step."* 
    或者利用一个 secret manager: *"Fetch the database credentials from AWS Secrets Manager using the IAM role, and export them as environment variables before starting the Systemd service."*

??? example "结合 CI/CD"
    deploy 包并不能替代 GitHub Actions、GitLab CI 或者是 Jenkins；相反，它能够起到补充作用。你可以使用该技能包去设置初始的服务器、安装 Docker 环境、配置防火墙并注册 GitHub Actions runner。一旦底层的基础设施稳固之后，你就可以让你传统的 CI/CD 流水线接管日常的代码推送，把 deploy 包留给应对复杂的维护工作和生产事故诊断。

??? example "处理 Monorepos"
    如果你的仓库中包含多个服务（例如，在 `apps/web` 下的 React 前端，和在 `apps/api` 下的 Node.js 后端 API），请确切告诉 Agent 应该关注哪个目录以避免混淆。
    *"Deploy the backend service located in `apps/api`. Ignore the `apps/web` directory for now. Look for the `Dockerfile` inside `apps/api` and ensure the build context is the repository root."*

??? example "反向代理后方的部署"
    如果你部署的服务必须通过 Nginx、Traefik 或是 Caddy 向外网暴露，请让 Agent 在部署应用的同时一并处理路由的配置。
    *"Deploy the service to port 8080 locally. Then, create an Nginx server block in `/etc/nginx/sites-available/api` for `api.example.com` that proxies traffic to `127.0.0.1:8080`. Test the Nginx config, create the symlink, and reload Nginx."*

??? example "零宕机部署"
    对于关键的服务，请要求 Agent 使用零宕机部署策略而不是突然暂停并重新启动服务。
    *"Deploy the new Docker container on a new port (e.g., 8081). Wait for its health check to pass at `/api/health`. Once healthy, update the Nginx configuration to point to the new port, reload Nginx gracefully, and then stop the old container on port 8080."*
    这种清晰指令保证了 Agent 能在部署过程中避免中断你的应用程序的在线状态。

??? example "日志轮转和管理"
    如果日志任由其无限制积累，应用进程会很快耗尽磁盘空间。你可以在请求部署时一并包含对日志轮转的设置。
    *"Set up logrotate for the application logs located in `/var/log/myapp/`. Ensure logs are rotated daily, compressed, and kept for 14 days. Create the config file at `/etc/logrotate.d/myapp` and test it."*
    在部署期间处理此事可以防范日后深夜由于磁盘爆满引发的事故。

---

## 技能参考 (Skill Reference)

该包里的技能是模块化的。你可以通过 orchestrator 触发整条流水线，或者使用下面的触发词来单独调用特定的技能。

| 技能名称 (Skill Name) | 详细描述 (Detailed Description) | 常见的触发词汇 (Common Trigger Phrases) |
|---|---|---|
| **`repo-service-lifecycle`** | 处理完整部署流程的端到端编排器。它管理发现、主机检查、执行、验证和运维之间的上下文交接。使用这个来处理所有广义上的“让它运行起来”的请求。 | *"Deploy this repo"*<br>*"Spin this up and manage it"*<br>*"Get this online"*<br>*"Take this repo to production"* |
| **`repo-runtime-discovery`** | 预部署扫描。识别技术栈、构建命令、Dockerfile，以及推断部署的候选方式。不执行任何变更。 | *"Analyze this repo before we deploy"*<br>*"How should we run this?"*<br>*"What environment variables are missing?"* |
| **`target-host-readiness`** | 针对即将部署的系统执行安全预检，对 OS、运行时（Docker、Systemd 等）、可用内存以及端口冲突进行把关。 | *"Check the remote server before deploying"*<br>*"Does the production host have enough disk space?"* |
| **`deployment-executor`** | 真正的上线。以可控且带有日志记录的方式应用计划好的变更（Docker、Systemd、PM2）。总是会建立安全的回滚点。 | *"Run the deployment to staging"*<br>*"Update the production configuration and restart"* |
| **`deployment-verifier`** | 部署后的严谨检查。执行多层的深度验证，确保该服务不仅仅是没崩，而且完全处于能接受请求的状态。 | *"Verify the deployment we just made"*<br>*"Run a smoke test on the new backend"*<br>*"Check the logs to make sure it started cleanly"* |
| **`service-operations`** | 处理线上的日常运维，收集应用状态并且清理系统。 | *"Perform routine maintenance on the server"*<br>*"Check logs for anomalies"*<br>*"Renew SSL certificates"*<br>*"Clean up old Docker images"* |
| **`incident-rollback`** | 危机管理，用于解决健康检查失败、崩溃或是严重的线上故障（502/504）。实施稳定化方案或者是快速回滚。 | *"Roll back the deployment"*<br>*"The site is returning 502s, fix it"*<br>*"Revert to the previous version immediately"* |