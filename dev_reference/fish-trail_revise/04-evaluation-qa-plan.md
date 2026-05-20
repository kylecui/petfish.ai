# Fish-Trail Tiered Memory v2 — 完整评估与QA方案

| 字段 | 值 |
|------|-----|
| For | 测试组 (QA/QC + 能力评估) |
| Cross-ref | [产品规格](03-product-spec-tiered-memory.md), [实验执行计划](01-experiment-execution-plan.md) |
| Status | Ready for planning |
| Version | 1.0 |
| Date | 2026-05-20 |

---

## 文档说明

本文档整合学术实验评估与产品QA两条线，为测试组提供完整的验证框架。学术实验部分基于已有P0-P3框架（见01-experiment-execution-plan.md），本文仅描述**新增与变更**内容；产品功能验证、性能基准、回归测试为全新内容。

**阅读前提**：测试组已持有01-experiment-execution-plan.md（P0-P3详细协议）和03-product-spec-tiered-memory.md（v2产品规格）。

---

## Part 1: 学术实验

本部分基于已有P0-P3框架，整合EPIS condition并新增P4 long-session验证。

### 1.1 实验矩阵 (Revised)

在原有P0-P3基础上，P1扩展为四臂设计，并新增P4阶段。完整矩阵如下：

| Phase | Conditions | Blocks | Runs | Purpose |
|-------|-----------|--------|------|---------|
| P0 | CF vs TAC | 5 paired | 10 | Core replication |
| P1-revised | CF vs TAC vs COMPR vs EPIS | 5 four-arm | 20 | Full ablation (segmentation vs summarization) |
| P1b | CF vs TAC (single-topic) | 5 paired | 10 | Topic-count control |
| P2 | CF vs TAC (GPT-4o) | 5 paired | 10 | Cross-model |
| P3 | CF vs TAC (5-topic) | 3 paired | 6 | Scaling |
| **P4-new** | CF vs TAC-Tiered vs TAC-Uniform (10+ compactions) | 3 three-arm | 9 | Long-session tiered validation |

**总计**：~65 runs，预估成本$60-80，预估机器时间50-70h。

**与01-experiment-execution-plan.md的差异**：
- P1从三臂(CF/TAC/COMPR)变为四臂(+EPIS)
- 新增P4阶段（需v2 tiered实现完成后执行）
- P0/P1b/P2/P3协议不变，直接沿用原计划

### 1.2 EPIS Condition详细规格

EPIS (Episodic Retention) 是一个ablation condition，用于隔离"话题分割"与"摘要压缩"各自的贡献。

**设计原则**：保留TAC的话题分割能力，但跳过摘要生成步骤。

| 参数 | 规格 |
|------|------|
| 话题提取 | 与TAC step 1完全相同（同一TopicDetector输出） |
| 摘要生成 | **跳过** — 保留每个话题的原始消息 |
| Token预算匹配 | 总token输出量与TAC相同（确保公平比较） |
| 截断策略 | LRU within each topic — 从最不活跃话题中删除最旧消息 |
| Topic index header | 保留（格式与TAC相同） |
| 实现方式 | 修改compaction plugin，跳过summarization step |

**EPIS vs 其他condition对比**：

| 特性 | CF | COMPR | EPIS | TAC |
|------|----|----|------|-----|
| 话题分割 | 无 | 无 | 有 | 有 |
| 摘要压缩 | 无 | 有(全局) | 无 | 有(per-topic) |
| Topic index | 无 | 无 | 有 | 有 |
| 截断方式 | 尾部截断 | 全局摘要 | LRU per-topic | 摘要per-topic |

**实现检查清单**：

- [ ] compaction plugin添加`mode: episodic`配置项
- [ ] episodic mode下topic extraction正常执行
- [ ] episodic mode下summarization step被跳过
- [ ] LRU截断逻辑实现并通过单元测试
- [ ] token输出量与TAC condition在±5%误差内匹配
- [ ] topic index header格式与TAC完全一致

### 1.3 P4 Long-Session Protocol (NEW)

P4是本次评估的核心新增实验，专门验证tiered retention在长会话中的效果。

#### 1.3.1 会话设计

**10-compaction session结构**：

```
Session总长: 50+ messages
话题数量: 3-5个交错话题
Compaction触发: 每5条消息触发一次compaction (共10次)
话题交错模式: progressive interleaving

消息分布示例(50 messages):
  Messages 1-5:   Topic A (初始化)     → compaction 1
  Messages 6-10:  Topic B (引入)       → compaction 2
  Messages 11-15: Topic A + C (交错)   → compaction 3
  Messages 16-20: Topic B + C          → compaction 4
  Messages 21-25: Topic A (回归)       → compaction 5
  Messages 26-30: Topic D (新话题)     → compaction 6
  Messages 31-35: Topic C + D          → compaction 7
  Messages 36-40: Topic A (再回归)     → compaction 8
  Messages 41-45: Topic B + D          → compaction 9
  Messages 46-50: Topic A + B + C + D  → compaction 10
```

**recall probe设计**：

每次compaction后，插入一组recall probe（引用早期话题中的specific detail），记录准确率。共10个测量点，形成degradation curve。

#### 1.3.2 三个条件

| Condition | 描述 | 预期行为 |
|-----------|------|---------|
| CF (Control) | 默认context window管理，无compaction | 直接截断，早期信息丢失 |
| TAC-Uniform | 当前v1实现，所有话题均等摘要 | 所有话题同等压缩，频繁回访话题也被压缩 |
| TAC-Tiered | v2 tiered retention，按活跃度分层保留 | 活跃话题保留更多细节，冷话题压缩更多 |

#### 1.3.3 指标体系

**Primary metric**: Recall accuracy degradation curve
- 横轴: compaction event number (1-10)
- 纵轴: recall accuracy (0-1)
- 每个condition一条曲线，比较形状和最终值

**Secondary metrics**:
- API efficiency trend: API calls per message across compaction events
- Token utilization: 实际使用token / 预算token比率
- Topic coverage: compaction后仍可召回的话题数量

**Expected outcomes**:
- CF: recall单调递减（早期信息被截断）
- TAC-Uniform: recall非单调递减（Faulty Memory prediction — 某些compaction可能意外丢失关键细节）
- TAC-Tiered: recall保持稳定（活跃话题始终保留足够细节）

#### 1.3.4 P4执行要求

| 要求 | 规格 |
|------|------|
| 前置依赖 | v2 tiered retention实现完成 |
| 会话模板数量 | 3个不同话题分布的模板 |
| 每模板runs | 3 (每condition 1 run) |
| 总runs | 9 |
| 预估耗时 | 每run约45-60min (含10次compaction) |
| 预估成本 | ~$15-20 (longer sessions cost more) |
| 评分方式 | 同P0-P3 frozen answer key protocol |

### 1.4 Decision Matrix

#### 1.4.1 P0-P3 Decision Matrix (沿用)

来源: evaluation-reassessment.md，此处引用以保持测试组文档完整性。

| P0 Outcome | Interpretation | Action |
|---|---|---|
| TAC > CF (significant) | Core hypothesis confirmed | Proceed to P1 |
| TAC ≈ CF | No advantage from TAC | Stop, investigate design |
| CF > TAC | TAC harmful | Stop, root cause analysis |
| High variance, no signal | Insufficient power | Increase sample size |

| P1 Outcome | Interpretation | Action |
|---|---|---|
| TAC > COMPR > EPIS > CF | Full pipeline validated, each component contributes | Ship TAC, document ablation |
| TAC > EPIS ≈ COMPR > CF | Summarization not key; segmentation sufficient | Simplify — EPIS mode may be sufficient |
| TAC ≈ COMPR > EPIS ≈ CF | Summarization matters, segmentation doesn't | Reconsider topic-aware approach |
| EPIS > TAC | Raw retention better than summarization | Challenge summarization quality |

#### 1.4.2 P4 Decision Matrix (NEW)

| P4 Outcome | Interpretation | Action |
|---|---|---|
| Tiered stable, Uniform degrades | Tiered retention validated | Ship tiered as default |
| Tiered ≈ Uniform, both stable | No benefit from tiering in 10 compactions | Tiered unnecessary for typical sessions |
| Both degrade similarly | Problem is not retention policy | Investigate other failure modes (summarization quality, topic detection drift) |
| Tiered degrades, Uniform stable | Tiered policy harmful | Root cause: tier assignment may be incorrect |
| All three similar | Long session is not a differentiating scenario | Focus value proposition elsewhere |

**P4与P0-P3的关系**：
- P4仅在P0确认TAC > CF后执行
- 若P1显示EPIS > TAC，P4可能需要调整condition为EPIS-Tiered vs EPIS-Uniform
- P4结果独立于P0-P3（即使P0-P3全部confirm，P4仍可能显示tiering无益）

### 1.5 统计分析计划

#### 1.5.1 两臂比较 (P0, P1b, P2, P3)

| 方法 | 用途 | 参数 |
|------|------|------|
| Exact paired permutation test | Primary hypothesis test | α=0.05, two-tailed |
| Bootstrap 95% CI | Effect size estimation | 10,000 resamples, BCa method |
| Rank-biserial correlation | Non-parametric effect size | — |
| Cohen's d_z | Parametric effect size (paired) | — |

#### 1.5.2 多臂比较 (P1-revised四臂, P4三臂)

| 方法 | 用途 | 参数 |
|------|------|------|
| Friedman test | Omnibus test | α=0.05 |
| Holm-corrected pairwise comparisons | Post-hoc | Family-wise α=0.05 |
| Bootstrap 95% CI per pair | Effect estimation | 10,000 resamples |

#### 1.5.3 P4特有分析

| 方法 | 用途 | 参数 |
|------|------|------|
| Linear mixed-effects model | Degradation curve analysis | Fixed: compaction_number × condition; Random: template |
| Interaction test | Condition对degradation rate的调节效应 | F-test on interaction term |
| Piecewise linear fit | 检测degradation inflection point | Breakpoint at compaction 5 |

**模型规格**：

```
recall ~ compaction_number * condition + (1|template)
```

若interaction term显著 (p<0.05)，则conditions间degradation rate不同。

#### 1.5.4 Recall评分协议

沿用01-experiment-execution-plan.md中的frozen answer key protocol：
- 每个recall probe有预先定义的correct answer
- 评分: exact match (1) vs partial match (0.5) vs miss (0)
- 评分者: automated matching + human review for ambiguous cases
- Inter-rater reliability: 若需人工评分，Cohen's κ ≥ 0.8

---

## Part 2: 产品功能验证

本部分定义v2各组件的功能测试方案。测试对象以03-product-spec-tiered-memory.md中的组件划分为准。

### 2.1 单元测试清单

#### 2.1.1 TopicDetector

| Test Case | Input | Expected Output | Priority |
|-----------|-------|-----------------|----------|
| Rule-based关键词检测 | 包含明确topic切换信号的消息 | 新topic ID | P0 |
| Semantic fallback触发 | 规则未命中但语义明显不同 | 触发LLM检测，返回新topic | P1 |
| Continuation分配 | 内容延续当前话题 | 返回当前active topic ID | P0 |
| 空消息处理 | `""` 或 `null` | Graceful return, no crash | P0 |
| Binary content | 包含非文本内容引用 | Fallback to continuation | P1 |
| 超长消息 (>10k tokens) | 10000+ token单条消息 | 正常检测，不超时 | P1 |
| 多话题混合消息 | 单条消息涉及2+话题 | 返回dominant topic或split信号 | P2 |
| 连续相同检测结果 | 100条同topic消息 | 稳定返回同一ID，无drift | P1 |

**覆盖目标**: 语句覆盖≥90%, 分支覆盖≥85%

#### 2.1.2 TopicRegistry

| Test Case | Input | Expected Output | Priority |
|-----------|-------|-----------------|----------|
| Create topic | 新topic metadata | Registry entry created, ID returned | P0 |
| Read topic | Valid topic ID | Correct metadata returned | P0 |
| Update topic state | topic ID + new state | State updated, timestamp recorded | P0 |
| Delete/archive topic | topic ID | Marked archived, not physically deleted | P0 |
| State transition: active→warm | Inactivity trigger | State changes, tier updated | P0 |
| State transition: warm→cold | Extended inactivity | State changes, consolidation eligible | P0 |
| State transition: cold→archived | Manual or policy trigger | State changes, frozen | P1 |
| Invalid state transition | cold→active without re-expansion | Rejected with error | P0 |
| Persistence: write+read | Create then restart | Data survives restart | P0 |
| Recovery from corruption | Truncated registry file | Rebuild from available data, log warning | P1 |
| Concurrent access | Simultaneous read+write | No data race, consistent state | P1 |
| 100-topic capacity | 100 topics in registry | Performance within bounds | P1 |

**覆盖目标**: 语句覆盖≥95%, 分支覆盖≥90%

#### 2.1.3 TieredRetentionEngine

| Test Case | Input | Expected Output | Priority |
|-----------|-------|-----------------|----------|
| Tier assignment: hot topic | 最近5条消息内活跃 | Tier=HOT, full retention | P0 |
| Tier assignment: warm topic | 5-15条消息前最后活跃 | Tier=WARM, partial retention | P0 |
| Tier assignment: cold topic | 15+条消息前最后活跃 | Tier=COLD, summary only | P0 |
| Budget allocation: normal | 3 topics, 均匀活跃 | Budget按tier比例分配 | P0 |
| Budget allocation: skewed | 1 hot + 5 cold | Hot获得多数budget | P0 |
| Overflow handling | Total demand > budget | Graceful degradation, cold first compressed | P0 |
| Never-consolidate items | 标记为pinned的消息 | 始终保留，不计入压缩池 | P1 |
| Tier boundary edge case | 恰好在tier边界的活跃度 | 确定性分配，无oscillation | P1 |
| Empty registry input | No topics | No-op, return empty allocation | P0 |
| Single topic input | Only one active topic | All budget to that topic | P0 |

**覆盖目标**: 语句覆盖≥95%, 分支覆盖≥90%

#### 2.1.4 ConsolidationGate

| Test Case | Input | Expected Output | Priority |
|-----------|-------|-----------------|----------|
| Trigger: cold topic eligible | Cold topic with enough content | Consolidation triggered | P0 |
| Trigger: warm topic not eligible | Warm topic | Consolidation NOT triggered | P0 |
| Exempt item filtering | Topic with pinned messages | Pinned items excluded from consolidation input | P0 |
| Quality check pass | Good summary output | Accept and store | P0 |
| Quality check fail | Summary missing key info | Reject, retry or retain raw | P1 |
| No content to consolidate | Cold topic with only 1 message | Skip consolidation | P1 |
| Rate limiting | Multiple topics eligible simultaneously | Process sequentially, respect rate limit | P1 |

**覆盖目标**: 语句覆盖≥90%, 分支覆盖≥85%

#### 2.1.5 BudgetAllocator

| Test Case | Input | Expected Output | Priority |
|-----------|-------|-----------------|----------|
| Pressure L0 (normal) | Total < 60% capacity | Standard allocation | P0 |
| Pressure L1 (elevated) | Total 60-80% capacity | Cold topics compressed more | P0 |
| Pressure L2 (high) | Total 80-95% capacity | Warm topics also compressed | P0 |
| Pressure L3 (emergency) | Total > 95% capacity | Minimal retention mode | P0 |
| Graceful degradation steps | Pressure L0→L3 progressive | Each step reduces proportionally | P0 |
| Rebalancing after topic state change | Topic goes from active to cold | Budget reallocated on next cycle | P1 |
| Zero-budget topic | Archived topic | Zero allocation, no error | P1 |
| Budget exactly at boundary | Exactly 60%/80%/95% | Deterministic behavior at boundary | P1 |

**覆盖目标**: 语句覆盖≥95%, 分支覆盖≥95% (核心算法组件)

#### 2.1.6 OutputFormatter

| Test Case | Input | Expected Output | Priority |
|-----------|-------|-----------------|----------|
| Correct ordering | Multiple topics with different tiers | HOT first, then WARM, then COLD | P0 |
| Format compliance | Standard output | Matches spec format exactly | P0 |
| Token count within budget | Large session | Output ≤ allocated token budget | P0 |
| Empty topic handling | Topic with no retained content | Omitted or minimal placeholder | P1 |
| Topic index header | Multiple topics | Correct topic index at top | P0 |
| Special characters | Unicode, code blocks, etc. | No corruption | P1 |

**覆盖目标**: 语句覆盖≥90%, 分支覆盖≥85%

### 2.2 集成测试场景

每个场景定义完整的输入→处理→输出链路，覆盖组件间交互。

#### Scenario 1: Normal 3-topic session

```yaml
Name: normal-3-topic
Input: 15 messages across 3 topics (5 each, interleaved)
Trigger: compaction at message 15
Expected:
  - TopicDetector identifies 3 distinct topics
  - TopicRegistry contains 3 active entries
  - TieredRetention assigns: most recent topic=HOT, others=WARM
  - Output contains all 3 topics with appropriate detail level
  - Total output within budget
Validation: topic assignments correct, tier states correct, output parseable
```

#### Scenario 2: Single-topic session

```yaml
Name: single-topic-deep
Input: 20 messages, all same topic
Trigger: compaction at message 20
Expected:
  - TopicDetector assigns all to one topic
  - TopicRegistry contains 1 active entry
  - TieredRetention assigns full budget to single topic
  - Output contains single comprehensive topic section
Validation: no spurious topic splits, full budget utilization
```

#### Scenario 3: Topic goes cold

```yaml
Name: topic-goes-cold
Input: 30 messages - Topic A (msg 1-10), Topic B (msg 11-30)
Trigger: compaction at message 30
Expected:
  - Topic A transitions to COLD (inactive for 20 messages)
  - Topic B remains HOT
  - ConsolidationGate triggers for Topic A
  - Topic A output is summary only
  - Topic B output is full detail
Validation: state transitions correct, consolidation triggered, output tiers correct
```

#### Scenario 4: User returns to cold topic

```yaml
Name: cold-topic-return
Input: 40 messages - Topic A (1-10), Topic B (11-35), Topic A again (36-40)
Trigger: compaction at message 40
Expected:
  - Topic A was COLD, now re-activated to HOT
  - Registry shows state transition history
  - Topic A output includes both original summary + new messages
Validation: re-activation works, no data loss from cold period
```

#### Scenario 5: Budget pressure L1

```yaml
Name: budget-pressure-l1
Input: 25 messages across 5 topics, total approaching 60% budget
Trigger: compaction with L1 pressure
Expected:
  - BudgetAllocator detects L1 condition
  - Cold topics receive reduced allocation
  - Hot/warm topics minimally affected
  - Total output stays within budget
Validation: allocation math correct, cold topics compressed, hot preserved
```

#### Scenario 6: Budget pressure L3 (emergency)

```yaml
Name: budget-pressure-l3
Input: 50+ messages across 8 topics, >95% budget
Trigger: compaction with L3 pressure
Expected:
  - BudgetAllocator enters emergency mode
  - All topics receive minimal retention
  - Only most recent topic retains significant detail
  - System remains functional (no crash, no infinite loop)
Validation: graceful degradation, no data corruption, output valid
```

#### Scenario 7: Topic detection failure

```yaml
Name: detection-failure-fallback
Input: Messages that confuse topic detector (adversarial edge case)
Trigger: detection returns error/timeout
Expected:
  - Graceful fallback to continuation (assign to current active topic)
  - Warning logged
  - No crash, session continues normally
  - Subsequent messages still processed
Validation: no crash, fallback behavior, warning in logs
```

#### Scenario 8: Registry corruption recovery

```yaml
Name: registry-corruption
Setup: Corrupt registry file (truncated JSON)
Input: New message arrives
Expected:
  - Corruption detected on read
  - Rebuild initiated from message history
  - Warning logged with details
  - Session continues with rebuilt registry
  - No permanent data loss
Validation: recovery successful, data consistent after rebuild
```

#### Scenario 9: 10-compaction session

```yaml
Name: ten-compactions
Input: 50 messages with compaction every 5 messages
Trigger: 10 sequential compaction events
Expected:
  - Registry persists correctly across all 10 events
  - Topic states evolve correctly over time
  - No registry drift or corruption
  - Final output reflects cumulative tiering decisions
  - Memory usage stays bounded
Validation: registry integrity at each step, final state correct
```

#### Scenario 10: Migration from v1

```yaml
Name: v1-migration
Setup: Existing v1 session data (compaction output without tiering)
Input: First compaction event after v2 upgrade
Expected:
  - v1 data correctly interpreted
  - TopicRegistry initialized from v1 state
  - Tier assignment applied retroactively
  - Output format upgraded to v2
  - No loss of v1 data
Validation: backward compatibility, data preservation, format upgrade
```

### 2.3 验收标准

#### 功能验收

| 标准 | 要求 | 验证方式 |
|------|------|---------|
| 单元测试 | 全部通过 | CI自动运行 |
| 集成测试 | 10个场景全部通过 | CI自动运行 |
| v1回归 | 无回归 | 回归套件通过 |
| Topic detection latency | <100ms per message (rule-based) | Performance benchmark |
| Registry file size | <1MB after 100 topics | Size test |
| Crash recovery | Zero data loss | Scenario 8通过 |
| Registry write | Atomic (write-then-rename) | Unit test验证 |

#### 非功能验收

| 标准 | 要求 | 验证方式 |
|------|------|---------|
| Code coverage | ≥85% overall, ≥90% core components | Coverage report |
| No known P0 bugs | Zero | Bug tracker query |
| Documentation | API docs + config guide complete | Review |
| Error handling | No unhandled exceptions in test suite | Exception monitoring |

#### 阻塞条件 (Release Blockers)

以下任一条件未满足则阻塞发布：
1. 任何P0 priority单元测试未通过
2. 集成场景1-6任一未通过
3. v1回归套件有failure
4. Crash recovery场景未通过 (data loss risk)
5. Latency target超过2x (>200ms for rule-based detection)

---

## Part 3: 性能基准

### 3.1 Latency Benchmarks

#### 3.1.1 测量方法

所有latency测量使用以下标准方法：
- 环境: 隔离测试环境，无其他负载
- 预热: 丢弃前10次测量
- 样本量: ≥1000次测量 (取p50/p99)
- 时钟: monotonic clock, microsecond精度
- 报告: p50, p95, p99, max

#### 3.1.2 目标值

| Operation | Target p50 | Target p99 | 测量方法 |
|-----------|-----------|-----------|---------|
| Topic detection (rule-based) | <10ms | <50ms | Microbenchmark, 1000 random messages |
| Topic detection (semantic/LLM) | <200ms | <500ms | With LLM API call (mock latency for CI) |
| Registry read | <2ms | <10ms | File I/O benchmark, warm cache |
| Registry update (single topic) | <5ms | <20ms | File I/O benchmark, fsync included |
| Tiered retention computation | <100ms | <300ms | Given 50-topic registry |
| Budget allocation | <10ms | <30ms | Pure computation benchmark |
| Full compaction pipeline | <2s | <5s | End-to-end, 100-message session (excl. LLM calls) |
| Output formatting | <50ms | <150ms | Token counting + assembly |
| ConsolidationGate evaluation | <5ms | <20ms | Per-topic evaluation |

#### 3.1.3 LLM调用延迟说明

涉及LLM的操作（semantic detection, summarization）的实际延迟取决于外部API。基准测试中：
- CI环境: 使用mock LLM (固定延迟50ms)
- Staging环境: 使用真实API，记录但不作为pass/fail判据
- 报告中分开列出: local computation latency vs total latency (incl. LLM)

### 3.2 Accuracy Benchmarks

#### 3.2.1 Topic Detection Accuracy

| Metric | Target | 测量方法 |
|--------|--------|---------|
| Precision | ≥85% | 200-message human-labeled corpus |
| Recall | ≥80% | Same corpus |
| F1 | ≥82% | Computed from P/R |
| Continuation accuracy | ≥90% | Messages correctly assigned to current topic |
| New-topic detection rate | ≥75% | True new topics correctly identified |

**评估语料库规格**：
- 200条消息，覆盖3-8个不同话题
- 人工标注ground truth topic assignment
- 包含edge cases: 模糊边界、混合话题、单消息话题
- 标注者: 2人独立标注，Cohen's κ ≥ 0.8
- 语言: 中英混合 (反映实际使用场景)

#### 3.2.2 Tier Assignment Accuracy

| Metric | Target | 测量方法 |
|--------|--------|---------|
| Tier assignment correctness | ≥95% | Deterministic given registry state |
| Boundary decision consistency | 100% | Same input → same tier (no randomness) |
| State transition correctness | 100% | All transitions follow state machine rules |

Tier assignment是确定性算法（给定registry state），correctness主要验证实现是否与规格一致。95%而非100%是因为edge case可能存在reasonable ambiguity。

#### 3.2.3 Budget Compliance

| Metric | Target | 测量方法 |
|--------|--------|---------|
| Budget compliance | 100% | Output never exceeds allocated token budget |
| Budget utilization | ≥80% | Allocated budget used efficiently (not wasting) |
| Over-allocation detection | 0 occurrences | No topic gets more than allocated |

#### 3.2.4 Recall Preservation (vs v1)

| Metric | Target | 测量方法 |
|--------|--------|---------|
| Recall accuracy | ≥ v1 scores on same task set | A/B comparison using P0 protocol |
| Hot topic recall | > v1 (expected improvement) | Focus on recently active topics |
| Cold topic recall | ≥ v1 × 0.9 (acceptable slight degradation) | Focus on inactive topics |

### 3.3 Resource Usage

#### 3.3.1 内存占用

| 指标 | 目标 | 测量条件 |
|------|------|---------|
| Registry in-memory size (10 topics) | <100KB | Normal session |
| Registry in-memory size (50 topics) | <500KB | Stress session |
| Registry in-memory size (100 topics) | <1MB | Maximum capacity |
| Per-compaction memory spike | <50MB | During compaction processing |
| Steady-state memory overhead vs v1 | <20% increase | Same session, v1 vs v2 |

#### 3.3.2 磁盘占用

| 指标 | 目标 | 测量条件 |
|------|------|---------|
| Registry file size (10 topics) | <50KB | After 10 compactions |
| Registry file size (50 topics) | <250KB | After 50 compactions |
| Growth rate | <5KB per compaction event | Amortized over 100 events |
| Temporary file cleanup | Zero orphaned temp files | After crash/restart |

#### 3.3.3 LLM Token开销

| 指标 | 目标 | 测量条件 |
|------|------|---------|
| Semantic detection overhead | <200 tokens per invocation | When triggered |
| Semantic detection trigger rate | <20% of messages | Rule-based handles 80%+ |
| Summarization efficiency | Summary < 30% of source length | Per-topic compression ratio |
| Total token overhead vs v1 | <15% increase | Same session content |

---

## Part 4: 回归测试

### 4.1 v1兼容性回归

#### 4.1.1 功能兼容性

| 回归项 | 验证方法 | 阻塞级别 |
|--------|---------|---------|
| fish-trail v1全部测试用例 | 运行existing test suite | 阻塞 |
| compaction output format | v2 disabled时输出与v1 identical | 阻塞 |
| MCP tool `topic_detect` schema | Extended (new fields), not breaking | 阻塞 |
| MCP tool `topic_update` schema | Extended, not breaking | 阻塞 |
| MCP tool `topic_list` schema | Extended, not breaking | 阻塞 |
| Configuration file format | Migration script + backward compat | 阻塞 |
| topic_graph.json format | Additive changes only | 阻塞 |

#### 4.1.2 行为兼容性

| 场景 | v1行为 | v2行为 (tiered disabled) | 要求 |
|------|--------|--------------------------|------|
| 单话题compaction | 全文摘要 | 全文摘要 (identical) | Byte-identical output |
| 多话题compaction | Per-topic摘要 | Per-topic摘要 (identical) | Byte-identical output |
| topic_detect low risk | 静默继续 | 静默继续 | 行为相同 |
| topic_detect high risk | 提示用户 | 提示用户 | 行为相同 |
| Registry persistence | JSON file | JSON file (extended schema) | 可读取v1 registry |

#### 4.1.3 配置迁移

```yaml
# v1 config (must still work)
fish-trail:
  enabled: true
  compaction: true

# v2 config (new options)
fish-trail:
  enabled: true
  compaction: true
  tiered-retention:
    enabled: true  # default: false (backward compat)
    tiers:
      hot-threshold: 5
      warm-threshold: 15
    budget:
      l1-pressure: 0.6
      l2-pressure: 0.8
      l3-pressure: 0.95
```

**迁移规则**：v1 config → v2 config时，所有新字段使用默认值，行为与v1相同。

### 4.2 标准场景回归套件

5个golden scenario，每个有frozen input和expected output。

#### Golden 1: Simple 3-topic coding session

```yaml
ID: golden-001
Source: P0 experiment template
Input: 15 messages (frozen JSON, see golden/golden-001-input.json)
Expected topic assignments:
  - msg 1-5: topic-a (python debugging)
  - msg 6-10: topic-b (git workflow)
  - msg 11-15: topic-c (deployment)
Expected tier states (after compaction):
  - topic-a: WARM
  - topic-b: WARM
  - topic-c: HOT
Expected output format: Matches golden/golden-001-output.json
Tolerance: Exact match on structure, fuzzy match on summary text (cosine sim > 0.9)
```

#### Golden 2: Single-topic deep session

```yaml
ID: golden-002
Source: P1b template
Input: 20 messages (all same topic: architecture design)
Expected topic assignments:
  - msg 1-20: topic-a
Expected tier states:
  - topic-a: HOT (only topic, always active)
Expected output format: Single topic section, full detail
Tolerance: Structure exact, content fuzzy (cosine sim > 0.9)
```

#### Golden 3: Rapid topic switching

```yaml
ID: golden-003
Source: Adversarial test case
Input: 10 messages, each about a different sub-topic
  - msg 1: React hooks
  - msg 2: Docker config
  - msg 3: SQL query
  - msg 4: CSS layout
  - msg 5: API design
  - msg 6: React hooks (回归)
  - msg 7: Docker config (回归)
  - msg 8: Testing
  - msg 9: React hooks (再回归)
  - msg 10: Deployment
Expected topic assignments:
  - Minimum 5 distinct topics detected
  - React hooks messages grouped together
  - Docker config messages grouped together
Expected tier states:
  - React hooks: HOT (3 messages, most recent)
  - Docker: WARM
  - Others: COLD or WARM depending on recency
Tolerance: Topic grouping correctness (not exact ID matching)
```

#### Golden 4: Very long single message

```yaml
ID: golden-004
Source: Edge case
Input: 1 message with >10,000 tokens (code review of large file)
Expected:
  - Topic detection completes within timeout
  - Single topic assigned
  - Compaction handles gracefully (may not trigger if under threshold)
  - No crash, no truncation of detection input
Tolerance: Behavior correctness (no crash, correct assignment)
```

#### Golden 5: Session with no compaction triggered

```yaml
ID: golden-005
Source: Short session
Input: 3 messages (below compaction threshold)
Expected:
  - TopicDetector processes all messages
  - TopicRegistry updated with topic info
  - No compaction triggered
  - No tiered retention applied (nothing to tier)
  - System in clean idle state
Tolerance: State correctness (registry exists, no compaction output)
```

#### Golden文件管理

```
tests/golden/
  golden-001-input.json
  golden-001-expected-topics.json
  golden-001-expected-tiers.json
  golden-001-expected-output.json
  golden-002-input.json
  golden-002-expected-topics.json
  ...
  golden-005-expected-state.json
```

所有golden文件版本控制，修改需经review approval。

### 4.3 回归自动化

#### 4.3.1 CI/CD集成

```yaml
# CI pipeline stages
stages:
  - lint
  - unit-test
  - integration-test
  - golden-regression
  - performance-check

golden-regression:
  script:
    - run golden scenarios 1-5
    - compare output with expected (structure + fuzzy content)
    - fail if any structural mismatch
    - warn if content similarity < 0.9
  trigger: every PR, every merge to main
  timeout: 5min

performance-check:
  script:
    - run latency benchmarks (subset: 100 iterations)
    - compare with baseline
    - fail if any target regressed >20%
  trigger: every PR
  timeout: 10min
```

#### 4.3.2 Snapshot Testing

对OutputFormatter的输出使用snapshot testing:
- 首次运行生成snapshot
- 后续运行比较snapshot
- Structural changes require explicit snapshot update (with review)
- Content changes (summarization wording) 使用fuzzy matching

#### 4.3.3 Performance Regression Detection

| 指标 | Regression阈值 | 行为 |
|------|---------------|------|
| p50 latency | >20% increase | CI fail |
| p99 latency | >30% increase | CI fail |
| Memory usage | >25% increase | CI warn |
| Token overhead | >20% increase | CI warn |

Baseline由上一个release tag的benchmark结果定义，存储在`tests/baselines/perf-baseline.json`中。

---

## Part 5: 测试执行时间线

### 5.1 总览

```
W1  W2  W3  W4  W5  W6  W7  W8  W9  W10  W11  W12
|---|---|---|---|---|---|---|---|---|----|----|-----|
 环境  单元  集成  性能  ----P0----  P1+P1b  P2   P3+P4 分析  签收
```

### 5.2 详细时间线

| Week | Activity | Deliverable | 前置依赖 |
|------|----------|-------------|---------|
| W1 | 测试环境搭建，v1回归baseline建立 | 环境ready，baseline metrics记录 | 无 |
| W2 | 全组件单元测试开发 | Unit test suite (目标: 100%组件覆盖) | W1环境 |
| W3 | 集成测试场景开发 | 10个场景自动化 | W2单元测试 |
| W4 | 性能基准测试开发 | Benchmark harness + 初始测量值 | W1环境 |
| W5-6 | 学术实验P0执行 | P0 raw data (10 runs) | 01-experiment-plan ready |
| W7-8 | P1-revised (4-arm) + P1b执行 | 30 runs raw data | P0完成且confirmed |
| W9 | P2 (GPT-4o cross-model) | 10 runs raw data | P0 confirmed |
| W10 | P3 (scaling) + P4 (if v2 ready) | 15 runs raw data | v2实现完成(P4) |
| W11 | 统计分析 + 报告撰写 | Analysis report with CIs and decision | 全部raw data |
| W12 | 最终QA签收 | QA report, known issues, release recommendation | 分析完成 |

### 5.3 并行执行说明

- W5-6的P0与W2-4的产品测试开发可并行（P0基于v1）
- W7-8的P1需要EPIS condition实现完成
- P4需要v2 tiered retention实现完成（最晚W9开始开发，W10可测）
- 统计分析(W11)可在每phase完成后增量进行，不必等全部数据

### 5.4 里程碑与Gate

| Gate | 时间 | 条件 | 不通过则 |
|------|------|------|---------|
| G1: P0 Decision | W6结束 | P0 confirms TAC > CF | 停止后续实验，root cause |
| G2: v2 Unit Test Pass | W2结束 | 全部P0 unit tests pass | 阻塞集成测试 |
| G3: Integration Pass | W3结束 | 10/10 scenarios pass | 阻塞性能测试 |
| G4: Performance Acceptable | W4结束 | All latency targets met | 优化后重测 |
| G5: P4 Decision | W10结束 | P4 outcome clear | 决定是否ship tiered |
| G6: Release Go/No-Go | W12结束 | 全部criteria met | 不发布，列出blocking issues |

---

## Part 6: 交付物清单

| # | Deliverable | Owner | Format | 位置 |
|---|---|---|---|---|
| 1 | Unit test suite + coverage report | 测试组 | Code + HTML report | `tests/unit/` + `reports/coverage/` |
| 2 | Integration test suite | 测试组 | Code + scenario YAML | `tests/integration/` |
| 3 | Performance benchmark results | 测试组 | JSON + summary table | `reports/benchmarks/` |
| 4 | Regression test golden files | 测试组 | Frozen JSON snapshots | `tests/golden/` |
| 5 | Academic experiment raw data (P0-P4) | 测试组 | JSON per run + metadata.json | `experiments/raw/` |
| 6 | Statistical analysis report | 研究组 | Markdown with figures | `research/06_outputs/` |
| 7 | QA sign-off report | 测试组 | Pass/Fail + known issues | `reports/qa-signoff.md` |
| 8 | Release recommendation | 测试组+研究组 | Go/No-Go with conditions | `reports/release-recommendation.md` |

### 交付物质量要求

| 交付物 | 质量要求 |
|--------|---------|
| Test code | Lint pass, 有docstring, 可独立运行 |
| Raw data | JSON schema validated, metadata完整 |
| Reports | Markdown well-formed, 数据可追溯 |
| Golden files | Version controlled, modification需review |
| Analysis report | 每个claim有evidence_id支撑 |

---

## Part 7: 风险与依赖

### 7.1 关键依赖

| 依赖 | 影响范围 | 缓解措施 |
|------|---------|---------|
| 产品组完成v2实现 | P4实验, 集成测试, 性能测试 | P0-P3可基于v1先行；单元测试可基于接口先写 |
| EPIS condition实现 | P1-revised实验 | 实现简单(跳过summarization)，可快速完成 |
| LLM API稳定性 | 学术实验全部phases | 预算包含retry成本；使用rate limiting |
| 人工标注语料库 | Topic detection accuracy benchmark | 提前安排标注(W1-W2并行) |
| Golden file初始化 | 回归测试 | W2与单元测试同步产出初始golden files |

### 7.2 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| P0 fails (TAC ≈ CF) | Low-Medium | 停止全部后续实验 | 先做pilot run检查信号 |
| v2实现延期 | Medium | P4无法按时执行 | P0-P3先行，P4可延后 |
| 预算超支 | Low | 减少runs | 65 runs × 优先级排序，先做P0/P1 |
| LLM API rate limiting | Medium | 实验速度下降 | 错峰执行，预留buffer时间 |
| Topic detection accuracy不达标 | Medium | 影响tiered retention质量 | 若<75% recall，切换到simpler heuristics |
| Golden test维护成本过高 | Low | 回归测试失效 | 使用fuzzy matching减少false positives |

### 7.3 预算分解

| 项目 | 预估成本 | 说明 |
|------|---------|------|
| P0 (10 runs) | $8-12 | 基础实验 |
| P1-revised (20 runs) | $16-24 | 四臂，每run成本略高 |
| P1b (10 runs) | $8-12 | 与P0相同结构 |
| P2 (10 runs, GPT-4o) | $12-18 | GPT-4o更贵 |
| P3 (6 runs) | $6-10 | 5-topic更长session |
| P4 (9 runs) | $15-20 | 10-compaction长session |
| Buffer (retries, failures) | $10-15 | — |
| **Total** | **$75-111** | 保守上限$111 |

### 7.4 通过/不通过判据汇总

**Release Go条件（全部满足）**：
1. P0 confirms TAC > CF (primary hypothesis)
2. 全部unit tests pass
3. 全部integration scenarios pass (10/10)
4. Performance targets met (all p99 within target)
5. v1 regression suite无failure
6. Zero known P0 bugs

**Release Go with conditions（可接受）**：
- P4未完成但P0-P2 confirmed → ship v1 improvements, tiered as experimental
- Performance某指标略超target但<2x → ship with monitoring
- 1-2个P2 integration scenarios需workaround → documented known limitations

**Release No-Go条件（任一触发）**：
- P0 fails (TAC ≤ CF)
- Data loss在任何测试中出现
- v1 regression failure
- Performance >3x target

---

## Appendix A: 术语表

| 术语 | 定义 |
|------|------|
| CF | Context Full — 默认context管理，无compaction |
| TAC | Topic-Aware Compaction — 话题感知压缩 |
| COMPR | Compression-only — 全局压缩，无话题分割 |
| EPIS | Episodic Retention — 话题分割但无摘要 |
| TAC-Uniform | v1版TAC，所有话题均等摘要 |
| TAC-Tiered | v2版TAC，按活跃度分层保留 |
| Golden scenario | 冻结输入+期望输出的回归测试用例 |
| Degradation curve | Recall accuracy随compaction次数的变化曲线 |
| Budget pressure | Token预算使用率，分L0-L3四级 |

## Appendix B: 相关文档索引

| 文档 | 位置 | 关系 |
|------|------|------|
| 实验执行计划 | `research/06_outputs/01-experiment-execution-plan.md` | P0-P3详细协议，本文引用 |
| 产品规格 | `research/06_outputs/03-product-spec-tiered-memory.md` | v2组件定义，测试对象 |
| 评估重评估 | `research/06_outputs/evaluation-reassessment.md` | Decision matrix来源 |
| Research brief | `research/00_brief/` | 研究问题定义 |

---

*End of document*
