# Upstream Issues — anomalyco/opencode 问题簇映射

> **快照日期：2026-10-10。上游结论会漂移**——引用任何一条之前，先回查 issue 当前状态；本文件只保证快照日期的归属关系。

## 分类 → issue 簇

| 类 | 故障 | 关联 issue（快照 2026-10-10） |
|---|---|---|
| 2 | agent 身份解析失败 | #54256、#42507 |
| 3 | 存储层故障 | #33356 |
| L3 治理 | 配置 reload 窗口 | #54172 |
| 相邻簇 | 会话/消息生命周期 | #47158、#46111 |

## 各 issue 一句话覆盖范围

| Issue | 覆盖范围（快照 2026-10-10，上游结论会漂移） |
|---|---|
| #54256 | agent display name 与 registry key 不一致导致 `createUserMessage` 阶段 `UnknownError`，是类 2 的主根因 |
| #42507 | prompt 注入路径绕过别名归一化，使未镜像的 display name 进入消息创建流程，类 2 的旁路成因 |
| #33356 | event 表无界膨胀导致存储层压力与磁盘打满，类 3 的慢性根因 |
| #54172 | 配置/插件重写触发 reload 窗口，活跃后台任务在窗口内批量崩溃——L3 配置编辑保护的机制依据（启发式标注） |
| #47158 | 会话消息生命周期边界问题，与类 2 的 session 死亡判据相关 |
| #46111 | 消息/部件写入时序问题，与类 3 的锁竞争表现相关 |

## 复查清单（引用前执行）

1. `gh issue view <N> --repo anomalyco/opencode --json state,title,updatedAt` 核对状态
2. state=closed 且修复已进 release → 更新本文件归属说明，递增 pack 版本
3. 标题/讨论方向已变 → 标记为漂移，修订映射表
4. 新增同类 issue → 追加到对应簇，保持快照日期同步刷新

逐条复查命令（快照当日状态，仅为格式示例）：

```text
gh issue view 54256 --repo anomalyco/opencode --json state,title,updatedAt
gh issue view 42507 --repo anomalyco/opencode --json state,title,updatedAt
gh issue view 33356 --repo anomalyco/opencode --json state,title,updatedAt
gh issue view 54172 --repo anomalyco/opencode --json state,title,updatedAt
gh issue view 47158 --repo anomalyco/opencode --json state,title,updatedAt
gh issue view 46111 --repo anomalyco/opencode --json state,title,updatedAt
```

## 验证要点（逐 issue）

| Issue | 引用前验证什么 |
|---|---|
| #54256 | display name ≠ registry key 的归因是否仍被上游认可；是否已有归一化补丁合入 |
| #42507 | prompt 注入绕过路径是否被堵；旁路是否还有变体 |
| #33356 | event 表是否加了保留策略或分区；膨胀是否仍无界 |
| #54172 | reload 窗口机制是否被证实；启发式可否升级为确定规则 |
| #47158 | 生命周期边界修复是否影响死亡判据的两跳查询 |
| #46111 | 写入时序修复是否降低锁竞争频率 |

## 复查记录模板

| 复查日期 | 操作人 | 结论 | 动作 |
|---|---|---|---|
| 2026-10-10 | （建立快照） | 六条归属有效 | 建立本文件 |
| YYYY-MM-DD | （谁复查） | 无漂移 / #N 已修复 | 更新映射 / 刷新快照日期 |

## 不在本分类学范围内

- 上游功能请求类 issue（与本四类 crash 无关）
- 上游 UI/键绑定问题
- 其它发行版的专属缺陷（本表只映射 anomalyco/opencode）
- milestone、label、assignee 等 triage 元数据变化不算漂移，无需刷新快照

## 漂移处理

上游 issue 关闭/修复后，本表归属可能失效；发现漂移时：

- 更新本文件的归属说明与一句话覆盖范围
- 刷新快照日期为复查当日
- 递增 pack 的 patch 版本

## 使用规则

- 引用任何一行时必须带快照日期：`（上游 #54256，快照 2026-10-10）`
- 这些 issue 解释**根因层**，不替代本仓库的诊断签名——签名分类以 `crash-signatures.md` 为准
- 不要把 issue 讨论里的猜测当作已证实结论写入诊断报告
