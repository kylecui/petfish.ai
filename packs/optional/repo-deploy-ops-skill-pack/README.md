# Repo Deploy & Ops Skill Pack for OpenCode

这是一套面向 **“读取repo → 部署到指定主机 → 功能验证 → 持续运维”** 的OpenCode skills。

## 设计目标

它不假设所有项目都能用同一种方式部署。相反，这套技能包要求代理先识别：

- repo来自本地工作区还是GitHub
-技术栈、构建方式、运行入口、配置文件与密钥需求
-部署方式是Docker/docker compose/systemd /直接二进制/ k8s /其它
-目标主机是否具备运行条件
-功能验证如何定义，如何留出回滚点，如何形成运维交接

## 技能清单

- `repo-service-lifecycle`：端到端总控。适合“帮我把这个repo部署起来并运维”这类宽泛请求。
- `repo-runtime-discovery`：读取本地repo或GitHub仓库，识别部署需求与运行约束。
- `target-host-readiness`：检查目标主机是否满足部署前提。
- `deployment-executor`：按计划执行部署、升级、回滚前准备。
- `deployment-verifier`：做健康检查、接口smoke test、日志核验、端口/页面验证。
- `service-operations`：进行日常运维、版本管理、巡检、变更记录。
- `incident-rollback`：处理故障、回滚、止血、形成事后记录。

## 推荐使用方式

### 放到项目内
将整个 `.opencode/skills/` 目录复制到你的项目根目录。

### 或放到全局
将这些skill放到：
`~/.config/opencode/skills/`

## 建议的项目规则文件

根目录自带了一个 `AGENTS.md` 示例。你可以直接使用，或将其中“部署与运维工作流”段落并入你现有的 `AGENTS.md`。

## 前置工具

建议环境具备以下能力：

- `git`
- `ssh`
- `rsync`
- `curl`
- `jq`
- `python3`
- `uv`

视项目情况可能还需要：

- `docker` / `docker compose`
- `systemctl`
- `nginx`
- `node`, `pnpm`, `npm`
- `go`, `java`, `mvn`, `gradle`
- `kubectl`, `helm`

## 关键原则

1. **先识别再部署**：先做repo与主机分析，再决定执行路径。
2. **先计划再变更**：任何改动前先形成部署计划和回滚点。
3. **验证必须可复现**：健康检查、接口验证、日志验证应尽量脚本化。
4. **运维要留痕**：版本、配置、路径、端口、变更时间、验证结果应被记录。
5. **默认保守**：不凭空假设环境；缺少关键事实时先探测、再执行。

## 内含脚本

- `repo-runtime-discovery/scripts/repo_inventory.py`
- `target-host-readiness/scripts/host_probe.py`
- `deployment-verifier/scripts/verify_http.py`
- `service-operations/scripts/release_state.py`

这些脚本都尽量做到：

-非交互式
- `--help` 清晰
- stdout输出结构化结果
-错误信息可供代理继续决策
