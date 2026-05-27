# Fish-Trail Tiered Memory Architecture v2 — 产品开发规格书

| 属性 | 值 |
|------|-----|
| 版本 | v2.0-draft |
| 状态 | RFC |
| 作者 | petfish产品工程团队 |
| 日期 | 2026-05-20 |
| 前置依赖 | fish-trail v1 (context-state MCP) |
| 理论基础 | CLS (Complementary Learning Systems), arXiv:2605.12978 "Faulty Memory" |

---

## 1. Executive Summary & Background

### 1.1 当前v1架构

fish-trail v1是一个compaction-time-only的话题治理系统。其工作模式：

1. 平时：通过`topic_detect` MCP tool做话题关系判断（continue/fork/switch等）
2. compaction触发时：对整段context做强制summarization
3. 话题信息存储在`.petfish/fish-trail/`下的topic graph JSON文件中

v1的核心问题是**介入时机单一**——仅在compaction事件发生时才有机会影响上下文内容。在两次compaction之间，系统对context内容没有任何结构化治理能力。

### 1.2 问题诊断

基于实际使用观察和"Faulty Memory"论文（arXiv:2605.12978）的发现，v1存在以下结构性问题：

| 问题 | 表现 | 根因 |
|------|------|------|
| Late intervention | compaction已经发生时才决定保留什么，信息已丢失 | 架构只有single intervention point |
| Stateless across compactions | 每次compaction都从零开始判断话题重要性 | 无persistent topic registry |
| Forced consolidation | 所有话题不论活跃度一律被summarize | 缺乏differential retention策略 |
| Misgrouping interference | 不同话题的信息被混合summarize导致干扰 | 无topic-aware consolidation boundary |
| No recency awareness | 刚讨论过的话题和三天前的话题被同等对待 | 缺乏temporal decay model |

"Faulty Memory"论文的关键发现：

- **Finding 1**: 强制对异构内容做统一summarization会产生misgrouping（将不相关信息错误关联）
- **Finding 2**: Episodic memory（原始经历）和semantic memory（抽象知识）需要不同的retention策略
- **Finding 3**: 过早consolidation会丢失后续推理可能需要的细节
- **Finding 4**: 基于recency和access frequency的differential retention显著优于uniform compression

### 1.3 v2愿景：从compaction trick到memory architecture

v2的核心转变：fish-trail从"compaction时做话题标注"升级为**完整的tiered memory architecture**。

理论基础是CLS（Complementary Learning Systems）理论：

- **Fast episodic store**：保留最近交互的raw detail（对应ACTIVE tier）
- **Slow schema store**：通过渐进consolidation形成抽象知识（对应WARM→COLD tier的summarization过程）
- **两个系统互补**：不是所有信息都需要同一种处理方式

v2设计原则：

1. **Continuous detection**：每条消息都标注topic，不等compaction
2. **Persistent state**：topic registry跨compaction存活
3. **Differential retention**：根据topic活跃度分层保留
4. **Consolidation gate**：仅在必要时才summarize，且respect topic boundary
5. **Budget-aware**：在有限context window内做optimal allocation

---

## 2. Architecture Overview

### 2.1 系统数据流

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Message Ingestion                             │
│  (每条user/assistant消息进入系统)                                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Continuous Topic Detector                          │
│  rule-based层 → semantic fallback → continuation assumption          │
│  输出: TopicAssignment { topic_id, confidence, method }              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Topic Registry Update                           │
│  更新TopicEntry: last_access, message_count, state transitions       │
│  持久化: .petfish/fish-trail/topic-registry.json                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
          [正常消息流继续]      [Compaction Trigger]
                    │                 │
                    │                 ▼
                    │  ┌──────────────────────────────────────────┐
                    │  │         Tiered Retention Engine           │
                    │  │  state machine: ACTIVE→WARM→COLD→ARCHIVED │
                    │  └──────────────────┬───────────────────────┘
                    │                     │
                    │                     ▼
                    │  ┌──────────────────────────────────────────┐
                    │  │         Consolidation Gate                │
                    │  │  决定哪些topic需要summarize               │
                    │  │  respect never-consolidate list           │
                    │  └──────────────────┬───────────────────────┘
                    │                     │
                    │                     ▼
                    │  ┌──────────────────────────────────────────┐
                    │  │          Budget Allocator                 │
                    │  │  token counting + priority allocation     │
                    │  │  pressure level detection                 │
                    │  └──────────────────┬───────────────────────┘
                    │                     │
                    │                     ▼
                    │  ┌──────────────────────────────────────────┐
                    │  │          Output Formatter                 │
                    │  │  生成最终注入context的structured text      │
                    │  └──────────────────┬───────────────────────┘
                    │                     │
                    └─────────┬───────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Context Window (注入后)                           │
│  Topic Index → Active Topics (raw) → Warm (summary+key) → Cold      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 组件职责清单

| 组件 | 职责 | 触发时机 | 状态 |
|------|------|----------|------|
| Continuous Topic Detector | 为每条消息分配topic_id | 每条消息 | stateless per-call, 依赖registry |
| Topic Registry | 维护所有topic的lifecycle状态 | 每次detection后更新 | persistent JSON |
| Tiered Retention Engine | 决定每个topic保留什么 | compaction trigger | stateless, 读registry |
| Consolidation Gate | 控制summarization边界 | retention engine调用 | stateless |
| Budget Allocator | 在token预算内分配空间 | retention后 | stateless |
| Output Formatter | 生成最终注入格式 | budget分配后 | stateless |

设计决策：除Topic Registry外，所有组件都是stateless的纯函数。状态集中在registry中，降低系统复杂度。

---

## 3. Core Components

### 3.1 Continuous Topic Detector

#### 职责

为系统中每条消息（user message和assistant message）分配topic标签。这是v2相对v1最关键的变化——从"compaction时批量标注"变为"消息级实时标注"。

#### Interface定义

```typescript
interface TopicDetector {
  detect(message: Message, registry: TopicRegistry): TopicAssignment;
  batchDetect(messages: Message[], registry: TopicRegistry): TopicAssignment[];
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: ISO8601;
  metadata?: {
    tool_calls?: ToolCall[];
    file_paths?: string[];
    commands?: string[];
  };
}

interface TopicAssignment {
  topic_id: string;            // 分配到的topic ID
  confidence: number;          // 0.0-1.0置信度
  method: 'rule' | 'semantic' | 'continuation';  // 使用的检测方法
  is_new_topic: boolean;       // 是否创建了新topic
  signals: string[];           // 触发判断的信号列表（用于debug）
}

interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
}
```

#### 检测算法（三层fallback）

**Layer 1: Rule-based detection（优先级最高，confidence=0.9-1.0）**

基于消息中的显式信号做确定性判断：

```
规则集:
1. file_path规则:
   - 消息涉及的文件路径属于某个已知project → 分配到该project topic
   - 路径模式: /proposal/{project}/* → topic = "project:{project}"
   - 路径模式: /research/{stage}/{project}* → topic = "project:{project}"

2. command规则:
   - git操作 → topic = "git-ops" (除非在已有project context内)
   - npm/pip/uv install → topic = "env-setup"
   - test/pytest → topic = 当前active project的"testing"子话题

3. tool_call规则:
   - topic_* MCP tools → topic = "meta:topic-management"
   - skill_mcp调用 → 根据skill名映射到对应research topic

4. 显式话题标记:
   - 用户消息以"关于X"、"回到X"、"切换到X"开头 → topic = X（需在registry中查找匹配）
```

**Layer 2: Semantic detection（confidence=0.5-0.85）**

当rule-based层无法确定时，调用语义分析：

```
策略:
1. 取当前消息的关键词/意图
2. 与registry中所有active和warm topic的label做similarity计算
3. 如果最高similarity > 0.7 → 分配到该topic
4. 如果最高similarity < 0.4 → 创建新topic
5. 中间地带(0.4-0.7) → 降级到continuation
```

在实现上，semantic detection复用v1的`topic_detect` MCP tool作为backend。具体来说：

```
v1 topic_detect调用:
  输入: text=message.content, current_topic=registry中active topic的id
  输出: relation, risk_score, suggested_action

映射到v2 TopicAssignment:
  relation="continue" → topic_id=current_topic, method='semantic'
  relation="fork" → 创建new topic as child, method='semantic'
  relation="switch" → topic_id=suggested target, method='semantic'
```

**Layer 3: Continuation assumption（confidence=0.3-0.5）**

当前两层都无法做出判断时：

```
规则: 将消息分配到最近一条有明确topic的消息所属的topic
理由: 对话中大部分消息是前一条的延续
```

#### 状态管理

Topic Detector本身是stateless的（不维护内部state），但依赖：
- TopicRegistry（读取当前topic列表和状态）
- 最近N条消息的topic assignment历史（用于continuation判断，从registry的last_access推导）

#### Error Handling

| 错误场景 | 处理策略 |
|----------|----------|
| semantic fallback调用失败（MCP不可用） | 跳过Layer 2，直接使用continuation assumption |
| registry读取失败 | 创建临时topic "session:untracked"，所有消息归入 |
| 消息content为空 | 使用continuation assumption |
| confidence极低（<0.2） | 标记为"ambiguous"，不更新registry的last_access |

#### 从v1迁移

v1行为：
- `topic_detect` MCP tool在用户每次交互时调用（由AGENTS.md中的always-on规则驱动）
- 返回risk_score决定是否需要深度治理

v2变化：
- `topic_detect`从"交互级判断工具"降级为"semantic detection backend"
- 新增rule-based层在其之上，减少对MCP调用的依赖
- detection频率从"每次交互"提升到"每条消息"（包括assistant消息）
- 输出从"路由建议"变为"topic_id assignment"

### 3.2 Topic Registry (Persistent State)

#### 职责

维护所有已知topic的lifecycle状态，作为整个系统的唯一persistent state。跨compaction存活，跨session持续更新。

#### 数据结构

```typescript
interface TopicRegistry {
  version: '2.0';
  topics: Map<string, TopicEntry>;
  session_id: string;                    // 当前session标识
  last_compaction_id: string;            // 最近一次compaction的标识
  compaction_count: number;              // 累计compaction次数
  created_at: ISO8601;
  updated_at: ISO8601;
  config_hash: string;                   // 配置文件hash，检测配置变更
}

interface TopicEntry {
  topic_id: string;                      // 唯一标识，格式: "project:{name}" 或 "session:{label}"
  label: string;                         // 人类可读标签
  description?: string;                  // 可选的topic描述（用于semantic matching）
  state: TopicState;
  parent_topic_id?: string;              // 父topic（fork关系）
  
  // Temporal信息
  first_seen_at: ISO8601;
  last_seen_at: ISO8601;
  last_access_message_idx: number;       // 最后一次被引用的消息序号
  
  // 统计信息
  message_count: number;                 // 累计关联消息数
  compactions_since_last_access: number; // 自上次访问以来经历的compaction次数
  
  // Retention控制
  never_consolidate_items: NeverConsolidateItem[];
  priority_boost: number;                // 0.0-1.0，用户手动提升的优先级
  
  // Consolidation产物
  summary?: string;                      // 当前summary（WARM/COLD状态时）
  key_decisions?: KeyDecision[];         // 提取的关键决策
  last_raw_exchange?: RawExchange;       // 最后一次完整交互（WARM状态保留）
}

type TopicState = 'active' | 'warm' | 'cold' | 'archived';

interface NeverConsolidateItem {
  item_id: string;
  type: 'decision' | 'error_fix' | 'config' | 'instruction' | 'constraint';
  content: string;
  source_message_idx: number;
  added_at: ISO8601;
  reason: string;                        // 为什么不能consolidate
}

interface KeyDecision {
  decision_id: string;
  description: string;
  alternatives_considered?: string[];
  rationale: string;
  timestamp: ISO8601;
}

interface RawExchange {
  user_message: string;
  assistant_message: string;
  message_idx: number;
  timestamp: ISO8601;
}
```

#### State Transitions

```
状态转换规则:

ACTIVE → WARM:
  条件: 消息序号差 > active_threshold_messages (默认5)
        且当前有其他topic处于ACTIVE
  动作: 触发initial consolidation（生成summary + 提取key decisions）

WARM → COLD:
  条件: compactions_since_last_access >= warm_to_cold_compactions (默认1)
  动作: 丢弃last_raw_exchange，仅保留summary + key_decisions + never_consolidate_items

COLD → ARCHIVED:
  条件: compactions_since_last_access >= cold_to_archived_compactions (默认3)
  动作: 从context中完全移除，registry中标记为archived，保留summary供未来re-expand

WARM/COLD → ACTIVE (re-activation):
  条件: 用户消息被detect为引用该topic
  动作: 重新进入ACTIVE tier，如果有summary则在context中同时展示summary和new raw messages

ARCHIVED → COLD (re-expand):
  条件: 用户显式提及archived topic（通过topic label或id）
  动作: 从registry中恢复summary到context，状态变为COLD
  限制: v2.0暂不实现完整re-expand，仅恢复summary
```

状态机图：

```
                    ┌──────────────────┐
                    │                  │
      ┌────────────┤     ACTIVE       │◄──────────────────┐
      │            │  (full episodic)  │                   │
      │            └────────┬─────────┘                   │
      │                     │                             │
      │          [msg gap > threshold]              [re-accessed]
      │                     │                             │
      │                     ▼                             │
      │            ┌──────────────────┐                   │
      │            │                  │                   │
      │            │      WARM        ├───────────────────┘
      │            │ (summary+key+raw)│
      │            └────────┬─────────┘
      │                     │
      │    [compactions_since >= 1]
      │                     │
      │                     ▼
      │            ┌──────────────────┐
      │            │                  │
      │            │      COLD        ├───────────[re-accessed]───►ACTIVE
      │            │  (summary only)  │
      │            └────────┬─────────┘
      │                     │
      │    [compactions_since >= 3]
      │                     │
      │                     ▼
      │            ┌──────────────────┐
      │            │                  │
      └──[error]──►│    ARCHIVED      │───[explicit mention]───►COLD
                   │  (out of context) │
                   └──────────────────┘
```

#### 持久化

- 存储位置: `.petfish/fish-trail/topic-registry.json`
- 写入时机: 每次topic state变更时（不是每条消息，避免IO过多）
- 写入策略: atomic write（先写.tmp再rename）
- 备份: 每次compaction前自动备份到`.petfish/fish-trail/registry-backups/{compaction_id}.json`

#### Cross-compaction连续性

关键设计：Topic Registry**不被compaction清除**。Compaction只清除context window中的消息内容，registry作为external persistent state独立存活。

每次compaction发生时：
1. `last_compaction_id`更新
2. `compaction_count`递增
3. 所有topic的`compactions_since_last_access`递增（除当前ACTIVE topic外）
4. 触发state transition检查

### 3.3 Tiered Retention Engine

#### 职责

在compaction trigger时，根据每个topic的当前state决定保留策略。输出的是"每个topic应该保留什么内容"的决策，不负责实际的content manipulation。

#### Interface定义

```typescript
interface TieredRetentionEngine {
  computeRetention(
    registry: TopicRegistry,
    messages: Message[],
    config: RetentionConfig
  ): RetentionPlan;
}

interface RetentionPlan {
  topics: TopicRetentionDecision[];
  total_estimated_tokens: number;
  pressure_level: PressureLevel;
}

interface TopicRetentionDecision {
  topic_id: string;
  state: TopicState;
  retain: RetainedContent;
  discard: DiscardedContent;
  consolidation_needed: boolean;
}

interface RetainedContent {
  type: 'full_raw' | 'summary_plus_key' | 'summary_only' | 'none';
  messages?: Message[];            // full_raw时
  summary?: string;                // summary模式时
  key_decisions?: KeyDecision[];   // summary_plus_key时
  last_exchange?: RawExchange;     // summary_plus_key时
  never_consolidate?: NeverConsolidateItem[];  // 始终保留
}

interface DiscardedContent {
  message_ids: string[];
  reason: string;
}

type PressureLevel = 'normal' | 'l1' | 'l2' | 'l3';
```

#### 每tier的retention策略

**ACTIVE tier: Full episodic retention**

保留内容：
- 所有关联消息的完整raw text
- 包括tool call的input和output
- 包括error信息和debug output
- never-consolidate items（显式标记）

不保留：
- 无（ACTIVE保留一切）

Token估算：raw messages的完整token count

**WARM tier: Key decisions + last raw exchange + summary**

保留内容：
- Topic summary（由Consolidation Gate生成，100-300 tokens）
- Key decisions列表（每个decision 50-100 tokens）
- 最后一次完整交互（user+assistant，完整raw）
- never-consolidate items

不保留：
- 中间过程的tool call outputs
- 重复的编辑操作
- 探索性的失败尝试（除非在never-consolidate中）

Token估算：summary + decisions + last_exchange + never_consolidate

**COLD tier: Summary only**

保留内容：
- Topic summary（2-3句话，50-100 tokens）
- never-consolidate items（如果有）

不保留：
- raw messages
- key decisions details（已融入summary）
- last raw exchange

Token估算：summary + never_consolidate

**ARCHIVED tier: None in context**

保留内容：
- 无（从context中完全移除）
- registry中保留metadata和summary供未来查询

不保留：
- 一切context内容

Token估算：0（仅在Topic Index中显示一行标识）

#### 状态机实现伪代码

```pseudocode
function computeRetention(registry, messages, config):
  plan = new RetentionPlan()
  
  // Step 1: 更新topic states
  for topic in registry.topics:
    updateTopicState(topic, messages, config)
  
  // Step 2: 对每个non-archived topic计算retention
  for topic in registry.topics where state != 'archived':
    decision = new TopicRetentionDecision()
    decision.topic_id = topic.topic_id
    decision.state = topic.state
    
    switch topic.state:
      case 'active':
        decision.retain = {
          type: 'full_raw',
          messages: getMessagesForTopic(messages, topic.topic_id),
          never_consolidate: topic.never_consolidate_items
        }
        decision.consolidation_needed = false
        
      case 'warm':
        if topic.summary == null:
          decision.consolidation_needed = true  // 需要先consolidate
        decision.retain = {
          type: 'summary_plus_key',
          summary: topic.summary,
          key_decisions: topic.key_decisions,
          last_exchange: topic.last_raw_exchange,
          never_consolidate: topic.never_consolidate_items
        }
        
      case 'cold':
        decision.retain = {
          type: 'summary_only',
          summary: topic.summary,
          never_consolidate: topic.never_consolidate_items
        }
        decision.consolidation_needed = (topic.summary == null)
    
    plan.topics.push(decision)
  
  // Step 3: 计算总token和pressure level
  plan.total_estimated_tokens = sumTokens(plan.topics)
  plan.pressure_level = detectPressure(plan.total_estimated_tokens, config)
  
  return plan
```

#### Error Handling

| 错误场景 | 处理策略 |
|----------|----------|
| topic关联的messages在compaction后已不可获取 | 使用registry中cached的summary和key_decisions |
| state transition计算出现未预期状态 | 回退到上一次已知good state，log warning |
| retention plan的总token超过budget | 交给Budget Allocator处理压力降级 |

### 3.4 Consolidation Gate

#### 职责

控制何时、对哪些内容进行summarization。是v2中防止"过早consolidation"和"misgrouping"的关键组件。

#### Interface定义

```typescript
interface ConsolidationGate {
  shouldConsolidate(topic: TopicEntry, context: ConsolidationContext): ConsolidationDecision;
  consolidate(topic: TopicEntry, messages: Message[], config: ConsolidationConfig): ConsolidationResult;
}

interface ConsolidationContext {
  trigger: ConsolidationTrigger;
  budget_pressure: PressureLevel;
  messages_since_last_consolidation: number;
}

type ConsolidationTrigger = 
  | 'state_transition_warm_to_cold'
  | 'budget_pressure'
  | 'redundancy_detected'
  | 'manual_request';

interface ConsolidationDecision {
  should_consolidate: boolean;
  reason: string;
  exempt_items: NeverConsolidateItem[];  // 即使consolidate也不能动的内容
}

interface ConsolidationResult {
  success: boolean;
  summary: string;
  key_decisions: KeyDecision[];
  quality_score: number;           // 0.0-1.0, self-assessed quality
  tokens_before: number;
  tokens_after: number;
  compression_ratio: number;
}

interface ConsolidationConfig {
  quality_threshold: number;       // 低于此值则保留raw（默认0.7）
  max_summary_tokens: number;      // summary最大token数（默认200）
  preserve_error_fix_pairs: boolean; // 保留error+fix对（默认true）
}
```

#### Trigger Conditions

Consolidation在以下条件下被触发：

**Trigger 1: Topic state从WARM转换到COLD**

```
条件: topic.state变为'cold' 且 topic.summary == null
行为: 对该topic的所有cached messages执行within-topic summarization
优先级: 正常
```

**Trigger 2: Budget pressure超过80%**

```
条件: Budget Allocator报告pressure_level >= 'l1'
行为: 对所有WARM topic强制consolidation，压缩到summary
优先级: 高（会覆盖quality check的宽松标准）
```

**Trigger 3: Redundancy detection**

```
条件: 单个topic内检测到高重复内容
检测规则:
  - 连续>3次相同tool call pattern（如反复read同一文件）
  - 连续>2次相同error message
  - >5条messages的内容similarity > 0.9
行为: 对redundant部分做dedup+summarize
优先级: 低（仅在正常流程中顺便处理）
```

#### Consolidation过程

```pseudocode
function consolidate(topic, messages, config):
  // Step 1: 分离exempt items
  exempt = extractExempt(messages, topic.never_consolidate_items)
  consolidatable = messages.filter(m => m not in exempt)
  
  // Step 2: 提取key decisions
  key_decisions = extractKeyDecisions(consolidatable)
  // 识别规则:
  //   - 包含"决定"、"选择"、"确认"等词的user/assistant交互
  //   - tool call后跟随确认性响应
  //   - 显式的A vs B比较后的结论
  
  // Step 3: 生成summary
  summary = generateSummary(consolidatable, {
    max_tokens: config.max_summary_tokens,
    focus: 'outcomes_and_state',  // 关注结果和状态变更，不关注过程
    exclude: key_decisions         // 已提取的不重复放入summary
  })
  
  // Step 4: Quality check
  quality_score = assessQuality(summary, consolidatable)
  // 评估维度:
  //   - information_coverage: summary是否覆盖了主要信息
  //   - factual_accuracy: summary是否有事实错误
  //   - decision_preservation: 关键决策是否被保留
  
  // Step 5: 决定是否接受
  if quality_score < config.quality_threshold:
    // Graceful degradation: 保留raw，标记consolidation失败
    return { success: false, reason: 'quality below threshold' }
  
  return {
    success: true,
    summary: summary,
    key_decisions: key_decisions,
    quality_score: quality_score,
    tokens_before: countTokens(messages),
    tokens_after: countTokens(summary) + countTokens(key_decisions),
    compression_ratio: tokens_after / tokens_before
  }
```

#### Never-Consolidate List

以下类型的内容**永远不被consolidate**，即使topic进入COLD或budget pressure极高：

| 类型 | 识别方式 | 示例 |
|------|----------|------|
| `decision` | 用户做出的明确选择 | "用TypeScript写"、"选方案A" |
| `error_fix` | error+对应fix的pair | TypeError + 修复代码 |
| `config` | 配置值和环境信息 | "port用8080"、".env中的DB_HOST" |
| `instruction` | 用户的standing instruction | "所有文件用中文注释"、"不要用class" |
| `constraint` | 项目约束 | "必须兼容Node 18"、"不能用GPL库" |

识别方式：
1. **显式标记**：用户说"记住这个"、"这个很重要别忘了"
2. **模式匹配**：error message + 紧随的fix（通过message pattern识别）
3. **配置值模式**：包含key=value、环境变量、端口号等的消息
4. **指令模式**：祈使句 + 全局性修饰（"所有"、"总是"、"永远"）

#### Rollback机制

如果consolidation结果未通过quality check：
1. 保留原始raw messages不做任何变更
2. 在registry中标记`consolidation_attempted: true, consolidation_failed: true`
3. 下次compaction时重新尝试（可能积累了更多context帮助理解）
4. 连续3次失败后，强制使用best-effort summary并标记`low_confidence_summary: true`

### 3.5 Budget Allocator

#### 职责

在给定的context window token预算内，为各tier分配空间，并在压力过大时执行graceful degradation。

#### Interface定义

```typescript
interface BudgetAllocator {
  allocate(
    retentionPlan: RetentionPlan,
    config: BudgetConfig
  ): BudgetAllocation;
}

interface BudgetConfig {
  total_context_window: number;      // 总context window大小（tokens）
  reserve_ratio: number;             // 为新消息预留的比例（默认0.15）
  tier_ratios: TierRatios;
  pressure_levels: PressureLevels;
  max_active_topics: number;
}

interface TierRatios {
  index: number;     // Topic Index占比（默认0.10）
  active: number;    // ACTIVE tier占比（默认0.50）
  warm: number;      // WARM tier占比（默认0.30）
  cold: number;      // COLD tier占比（默认0.10）
}

interface PressureLevels {
  l1: number;  // Level 1触发线（默认0.80）
  l2: number;  // Level 2触发线（默认0.90）
  l3: number;  // Level 3触发线（默认0.95）
}

interface BudgetAllocation {
  total_budget: number;
  allocated: {
    index: TokenBudget;
    active: TokenBudget;
    warm: TokenBudget;
    cold: TokenBudget;
  };
  pressure_level: PressureLevel;
  overflow_actions: OverflowAction[];
}

interface TokenBudget {
  allocated_tokens: number;
  used_tokens: number;
  topics_included: string[];
  topics_evicted: string[];       // 被LRU淘汰的topics
}

interface OverflowAction {
  type: 'evict' | 'compress' | 'trim' | 'emergency_summarize';
  target_topic_id: string;
  reason: string;
  tokens_freed: number;
}
```

#### Token Counting策略

```pseudocode
function countTokens(content):
  // 使用tiktoken或等效tokenizer
  // 对于估算阶段，使用简化计算：chars / 3.5（中英混合文本的经验值）
  // 对于最终allocation，使用精确tokenizer
  
  if estimation_mode:
    return len(content) / 3.5
  else:
    return tiktoken.encode(content).length
```

#### Priority-weighted Allocation算法

```pseudocode
function allocate(retentionPlan, config):
  total_budget = config.total_context_window * (1 - config.reserve_ratio)
  
  // Step 1: 计算各tier基础预算
  index_budget = total_budget * config.tier_ratios.index
  active_budget = total_budget * config.tier_ratios.active
  warm_budget = total_budget * config.tier_ratios.warm
  cold_budget = total_budget * config.tier_ratios.cold
  
  // Step 2: 统计各tier实际需求
  active_topics = retentionPlan.topics.filter(t => t.state == 'active')
  warm_topics = retentionPlan.topics.filter(t => t.state == 'warm')
  cold_topics = retentionPlan.topics.filter(t => t.state == 'cold')
  
  active_demand = sum(estimateTokens(t.retain) for t in active_topics)
  warm_demand = sum(estimateTokens(t.retain) for t in warm_topics)
  cold_demand = sum(estimateTokens(t.retain) for t in cold_topics)
  
  // Step 3: 检测压力
  total_demand = active_demand + warm_demand + cold_demand + index_estimate
  utilization = total_demand / total_budget
  pressure = detectPressure(utilization, config.pressure_levels)
  
  // Step 4: 根据压力执行不同策略
  switch pressure:
    case 'normal':
      // 正常分配，如果某tier有剩余可以给其他tier
      return normalAllocation(...)
    case 'l1':
      return l1Degradation(...)
    case 'l2':
      return l2Degradation(...)
    case 'l3':
      return l3Emergency(...)
```

#### Graceful Degradation策略

**Level 1 (utilization > 80%): 压缩cold tier**

```
动作:
1. COLD tier中的topics按compactions_since_last_access排序
2. 从最久远的开始，将summary压缩到单句（20-30 tokens）
3. 如果仍超预算，将最久远的COLD topics移至ARCHIVED
4. 释放的空间分配给ACTIVE tier
```

**Level 2 (utilization > 90%): 压缩warm tier + trim active**

```
动作:
1. 执行Level 1的所有动作
2. WARM tier中的topics：丢弃last_raw_exchange，仅保留summary+key_decisions
3. ACTIVE tier：每个topic仅保留最近3条消息（而非全部）
4. 如果active_topics > max_active_topics：LRU淘汰最不活跃的active topic到WARM
```

**Level 3 (utilization > 95%): Emergency mode**

```
动作:
1. 所有COLD topics移至ARCHIVED（从context移除）
2. 所有WARM topics仅保留单句summary
3. ACTIVE topics仅保留最后1条消息 + never-consolidate items
4. Topic Index压缩到仅显示active topics
5. 触发alert：建议用户开始新session
```

#### Active Tier内部的LRU淘汰

当ACTIVE topics数量超过`max_active_topics`（默认3）时：

```pseudocode
function evictFromActive(active_topics, max_count):
  if active_topics.length <= max_count:
    return  // 不需要淘汰
  
  // 按last_access_message_idx排序，越小越早被访问
  sorted = active_topics.sortBy(t => t.last_access_message_idx, ascending)
  
  // 淘汰最早的
  to_evict = sorted.slice(0, active_topics.length - max_count)
  
  for topic in to_evict:
    topic.state = 'warm'
    // 触发consolidation
    triggerConsolidation(topic, 'state_transition_active_to_warm')
```

#### Rebalancing

当topic state发生变化后（如COLD→ACTIVE），需要重新计算budget分配：

```pseudocode
function rebalance(allocation, stateChange):
  // 简单策略：重新运行allocate()
  // 优化策略：增量调整受影响的tier
  
  if stateChange.new_state == 'active':
    // 有topic进入active，可能需要从warm/cold中释放空间
    freed = compressLeastImportant(allocation.warm, stateChange.tokens_needed)
    allocation.active.allocated_tokens += freed
  
  return recomputeAllocation(...)
```

### 3.6 Output Formatter

#### 职责

将Budget Allocator的分配结果转化为最终注入context的structured text。

#### Interface定义

```typescript
interface OutputFormatter {
  format(allocation: BudgetAllocation, registry: TopicRegistry): FormattedOutput;
}

interface FormattedOutput {
  text: string;                  // 最终注入的text
  total_tokens: number;          // 实际token数
  sections: OutputSection[];     // 各section的metadata（用于debug）
}

interface OutputSection {
  type: 'index' | 'active' | 'warm' | 'cold';
  topic_id: string;
  token_count: number;
  content_type: string;
}
```

#### 输出格式规范

```markdown
## Topic Index
| Topic | State | Last Active | Messages |
|-------|-------|-------------|----------|
| {label} | ACTIVE | {relative_time} | {count} |
| {label} | warm | {relative_time} | {count} |
| {label} | cold | {relative_time} | {count} |
| {label} | archived | {relative_time} | - |

---

## [ACTIVE] {topic_label}

{完整raw messages，保持原始格式}
{包含tool calls和outputs}
{包含never-consolidate items（如有，用标记包裹）}

---

## [ACTIVE] {topic_label_2}

{同上}

---

## [WARM] {topic_label}

**Summary**: {topic summary}

**Key Decisions**:
- {decision_1}
- {decision_2}

**Last Exchange**:
> User: {last user message}
> Assistant: {last assistant response}

**Preserved Items**:
- [instruction] {never_consolidate_item}
- [config] {never_consolidate_item}

---

## [COLD] {topic_label}

{2-3 sentence summary}

{never-consolidate items（如有）}

---
```

#### 排序规则

1. Topic Index始终在最前
2. ACTIVE topics按`last_access_message_idx`降序（最近的在前）
3. WARM topics按`last_access_message_idx`降序
4. COLD topics按`last_access_message_idx`降序
5. ARCHIVED topics仅在Topic Index中显示，不占正文空间

#### 格式约束

- Topic Index使用Markdown table格式（紧凑）
- Section分隔使用`---`
- Never-consolidate items用`[type]`前缀标注
- ACTIVE section不做任何formatting修改，保持raw
- WARM/COLD section使用bullet points和blockquote保持可读性

#### Emergency Mode格式

当Budget Allocator报告Level 3 emergency时，格式简化：

```markdown
## Topics (Emergency Mode)
Active: {topic_label} | Warm: {count} topics | Cold: {count} topics

## {active_topic_label}
{last message only}

## Important Items (cross-topic)
- {all never-consolidate items merged}
```

---

## 4. Configuration

### 4.1 配置参数完整列表

```json
{
  "$schema": "fish-trail-tiered-memory-v2",
  "version": "2.0",
  
  "detection": {
    "enable_semantic_detection": true,
    "semantic_similarity_threshold": 0.7,
    "new_topic_threshold": 0.4,
    "rule_patterns_file": "detection-rules.json",
    "continuation_window": 3
  },
  
  "retention": {
    "active_threshold_messages": 5,
    "warm_to_cold_compactions": 1,
    "cold_to_archived_compactions": 3,
    "max_active_topics": 3,
    "max_warm_topics": 10,
    "max_cold_topics": 20
  },
  
  "budget": {
    "total_context_window": 128000,
    "reserve_ratio": 0.15,
    "tier_ratios": {
      "index": 0.10,
      "active": 0.50,
      "warm": 0.30,
      "cold": 0.10
    },
    "pressure_levels": {
      "l1": 0.80,
      "l2": 0.90,
      "l3": 0.95
    }
  },
  
  "consolidation": {
    "quality_threshold": 0.7,
    "max_summary_tokens": 200,
    "max_key_decisions_per_topic": 10,
    "preserve_error_fix_pairs": true,
    "max_retry_attempts": 3,
    "redundancy_threshold": 3
  },
  
  "output": {
    "format": "markdown",
    "include_topic_index": true,
    "include_archived_in_index": true,
    "section_separator": "---",
    "emergency_mode_threshold": "l3"
  },
  
  "persistence": {
    "registry_path": ".petfish/fish-trail/topic-registry.json",
    "backup_on_compaction": true,
    "backup_retention_count": 5,
    "atomic_write": true
  },
  
  "observability": {
    "log_level": "info",
    "emit_metrics": true,
    "debug_trace": false,
    "metrics_prefix": "fish_trail_v2"
  }
}
```

### 4.2 参数说明

| 参数 | 默认值 | 有效范围 | 说明 |
|------|--------|----------|------|
| `detection.enable_semantic_detection` | `true` | boolean | 是否启用semantic fallback（禁用后仅用rule+continuation） |
| `detection.semantic_similarity_threshold` | `0.7` | 0.0-1.0 | similarity高于此值才分配到existing topic |
| `detection.new_topic_threshold` | `0.4` | 0.0-1.0 | similarity低于此值则创建new topic |
| `detection.continuation_window` | `3` | 1-10 | continuation assumption向前看多少条消息 |
| `retention.active_threshold_messages` | `5` | 1-20 | 多少条消息内被引用算ACTIVE |
| `retention.warm_to_cold_compactions` | `1` | 1-5 | 多少次compaction无访问后变COLD |
| `retention.cold_to_archived_compactions` | `3` | 1-10 | 多少次compaction无访问后ARCHIVED |
| `retention.max_active_topics` | `3` | 1-5 | 同时允许的ACTIVE topic数量 |
| `budget.total_context_window` | `128000` | 1000+ | 总context window token数 |
| `budget.reserve_ratio` | `0.15` | 0.05-0.50 | 为新消息预留的比例 |
| `budget.tier_ratios.active` | `0.50` | 0.20-0.80 | ACTIVE tier预算占比 |
| `budget.tier_ratios.warm` | `0.30` | 0.10-0.50 | WARM tier预算占比 |
| `budget.tier_ratios.cold` | `0.10` | 0.05-0.30 | COLD tier预算占比 |
| `budget.tier_ratios.index` | `0.10` | 0.05-0.20 | Topic Index预算占比 |
| `budget.pressure_levels.l1` | `0.80` | 0.50-0.95 | Level 1 pressure触发线 |
| `budget.pressure_levels.l2` | `0.90` | 0.70-0.98 | Level 2 pressure触发线 |
| `budget.pressure_levels.l3` | `0.95` | 0.80-0.99 | Level 3 pressure触发线 |
| `consolidation.quality_threshold` | `0.7` | 0.0-1.0 | consolidation quality低于此值则保留raw |
| `consolidation.max_summary_tokens` | `200` | 50-500 | 单个topic summary的最大token数 |
| `consolidation.redundancy_threshold` | `3` | 2-10 | 连续多少次相同pattern算redundancy |

### 4.3 配置文件位置

主配置文件: `.petfish/fish-trail/config.json`

加载优先级（高→低）：
1. 环境变量（`FISH_TRAIL_*`前缀）
2. 项目级配置（`.petfish/fish-trail/config.json`）
3. 用户级配置（`~/.config/petfish/fish-trail/config.json`）
4. 内置默认值

### 4.4 环境变量Override

所有配置参数都可以通过环境变量覆盖，命名规则：

```
FISH_TRAIL_{SECTION}_{PARAM} = value

示例:
FISH_TRAIL_RETENTION_ACTIVE_THRESHOLD_MESSAGES=10
FISH_TRAIL_BUDGET_RESERVE_RATIO=0.20
FISH_TRAIL_DETECTION_ENABLE_SEMANTIC=false
FISH_TRAIL_OBSERVABILITY_LOG_LEVEL=debug
```

嵌套配置用`_`连接，数组和对象使用JSON string：
```
FISH_TRAIL_BUDGET_TIER_RATIOS='{"active":0.60,"warm":0.25,"cold":0.05,"index":0.10}'
```

---

## 5. Migration Path from v1

### 5.1 用户可见变化

| 方面 | v1行为 | v2行为 | 用户感知 |
|------|--------|--------|----------|
| Topic detection | 每次交互调一次MCP | 每条消息都标注（rule优先） | 无感（更准确） |
| Compaction | 统一summarize所有内容 | 分tier处理，ACTIVE保留raw | context保留更多有用信息 |
| 跨compaction记忆 | 无（每次从零开始） | registry persistent | 系统"记得"之前在做什么 |
| 话题切换 | 手动管理 | 自动检测+自动retention调整 | 无需手动归档 |
| Never-consolidate | 无 | 自动识别+保留关键信息 | 重要指令不会被summarize掉 |

### 5.2 向后兼容保证

1. **MCP接口兼容**: `topic_detect` tool保持原有interface不变，新增参数为optional
2. **文件格式兼容**: v1的topic graph数据不被删除或修改，v2创建独立的registry文件
3. **行为兼容**: 如果v2被disable，系统回退到v1行为（仅compaction-time intervention）
4. **配置兼容**: v1无配置文件概念，v2的配置文件缺失时使用默认值（等效v1行为+新功能）

### 5.3 数据迁移

v1数据结构（`.petfish/fish-trail/`下）：
- `topic_graph.json` — topic之间的关系图
- `topics/` — 每个topic的detail文件

v2新增：
- `topic-registry.json` — new persistent state
- `config.json` — 配置文件
- `registry-backups/` — compaction备份

迁移过程：

```pseudocode
function migrateV1toV2():
  // Step 1: 读取v1 topic graph
  v1_graph = readJSON('.petfish/fish-trail/topic_graph.json')
  
  // Step 2: 转换为v2 registry格式
  registry = new TopicRegistry()
  registry.version = '2.0'
  
  for node in v1_graph.nodes:
    entry = new TopicEntry()
    entry.topic_id = node.id
    entry.label = node.title
    entry.description = node.scope
    entry.state = mapV1Status(node.status)  // active→active, paused→warm, archived→archived
    entry.first_seen_at = node.created_at
    entry.last_seen_at = node.updated_at
    entry.message_count = 0  // v1无此信息，从0开始
    entry.compactions_since_last_access = 0
    entry.never_consolidate_items = []
    
    if node.summary:
      entry.summary = node.summary
    
    registry.topics.set(entry.topic_id, entry)
  
  // Step 3: 写入新文件（不修改v1文件）
  writeJSON('.petfish/fish-trail/topic-registry.json', registry)
  
  // Step 4: 标记迁移完成
  writeJSON('.petfish/fish-trail/migration-status.json', {
    migrated_from: 'v1',
    migrated_at: now(),
    topics_migrated: registry.topics.size
  })
```

### 5.4 Feature Flags

通过配置文件中的feature flags控制渐进rollout：

```json
{
  "feature_flags": {
    "enable_continuous_detection": true,
    "enable_tiered_retention": true,
    "enable_budget_allocation": true,
    "enable_never_consolidate": true,
    "enable_auto_state_transitions": true,
    "enable_pressure_degradation": true,
    "v1_fallback_on_error": true
  }
}
```

建议的rollout顺序：
1. Phase 1: 仅开启`continuous_detection`（观察detection quality）
2. Phase 2: 开启`tiered_retention` + `budget_allocation`
3. Phase 3: 开启`never_consolidate` + `auto_state_transitions`
4. Phase 4: 开启`pressure_degradation`，关闭`v1_fallback_on_error`

### 5.5 Rollback过程

如果v2产生问题，回退步骤：

1. 设置`FISH_TRAIL_V2_ENABLED=false`环境变量
2. 系统自动回退到v1行为（仅compaction-time topic_detect）
3. v2 registry文件保留但不再更新
4. v1 topic graph继续正常工作（因为v2从未修改它）
5. 如需彻底回退：删除`.petfish/fish-trail/topic-registry.json`和`config.json`

---

## 6. API & Integration Points

### 6.1 MCP Tool Integration（Primary Path）

v2通过MCP tool `get_memory_context()` 作为**主集成路径**，由AGENTS.md Companion Gateway规则在每次交互时调用。这是一个纯用户态方案，不依赖任何上游平台暴露lifecycle hook。

**集成方式：**

1. Companion Gateway Step 1（Topic Check）扩展：在`topic_detect`调用后，追加调用`get_memory_context()`
2. 返回的tiered memory context注入当前交互的system prompt（通过AGENTS.md规则控制）
3. Memory Pressure Monitor作为MCP server后台进程运行，持续维护registry状态

**MCP Tool定义：**

```typescript
interface GetMemoryContextParams {
  current_topic_id?: string;        // 当前活跃topic（可选，自动推断）
  budget_tokens?: number;           // 可用token预算（默认由pressure level决定）
  include_warm?: boolean;           // 是否包含warm tier内容（默认true）
  include_cold_summaries?: boolean; // 是否包含cold tier摘要（默认基于压力等级）
}

interface GetMemoryContextResult {
  context_block: string;            // 直接注入system prompt的文本块
  tokens_used: number;
  metadata: {
    topics_active: number;
    topics_warm: number;
    topics_cold: number;
    topics_archived: number;
    pressure_level: PressureLevel;
  };
  cache_hit: boolean;               // 是否命中缓存（避免重复计算）
}
```

**调用时机：**

- 每次用户消息到达时（Companion Gateway流程内）
- Compaction发生后的首次交互（cache自动失效，重新计算）
- 手动触发：用户可通过`/fish-trail memory`查看当前memory状态

**性能保证：**

- 热路径缓存：相同topic+相同pressure level下，结果缓存有效期为当前session
- Cache失效条件：topic切换、新compaction事件、pressure level变化、registry更新
- 冷启动延迟目标：< 200ms（基于本地JSON文件读取）

### 6.x Future: OpenCode Compaction Lifecycle Hook（未来优化）

> **状态：DEFERRED** — 等待OpenCode上游暴露compaction lifecycle hook点。当前v2不依赖此机制。

当OpenCode未来支持compaction lifecycle hook时，可将memory context注入从"每次交互被动查询"优化为"compaction时主动构建"，减少热路径延迟。接口设计预留如下：

```typescript
interface CompactionLifecycleHook {
  // 在compaction开始前调用（获取当前context snapshot）
  onBeforeCompaction(context: CompactionContext): void;
  
  // 在compaction执行时调用（替代默认的summarization逻辑）
  onCompaction(context: CompactionContext): CompactionResult;
  
  // 在compaction完成后调用（更新registry状态）
  onAfterCompaction(result: CompactionResult): void;
}

interface CompactionContext {
  compaction_id: string;
  messages: Message[];
  current_context_tokens: number;
  target_tokens: number;
  trigger_reason: 'window_full' | 'manual' | 'session_end';
}

interface CompactionResult {
  retained_content: string;     // 注入到新context的内容
  tokens_used: number;
  metadata: {
    topics_active: number;
    topics_warm: number;
    topics_cold: number;
    topics_archived: number;
    pressure_level: PressureLevel;
  };
}
```

此优化路径的价值：将memory context构建从O(每次交互)降为O(每次compaction)，但当前MCP方案通过缓存已将实际开销控制在可接受范围内。

### 6.2 MCP Tool更新

**增强现有tool: `topic_detect`**

```typescript
// v1 interface保持不变，新增optional参数
interface TopicDetectParams {
  text: string;                         // 原有
  current_topic?: string;               // 原有
  // v2 新增
  message_metadata?: {
    file_paths?: string[];
    commands?: string[];
    tool_calls?: string[];
  };
  assign_mode?: boolean;                // true时返回TopicAssignment而非关系判断
}

// v2 新增返回字段（追加到现有返回中）
interface TopicDetectResult {
  // 原有字段...
  relation: string;
  risk_score: number;
  // v2 新增
  topic_assignment?: TopicAssignment;   // 仅assign_mode=true时返回
}
```

**新增tool: `topic_registry_get`**

```typescript
interface TopicRegistryGetParams {
  filter_state?: TopicState[];          // 可选：仅返回指定state的topics
  include_summary?: boolean;            // 是否包含summary内容（默认false，仅metadata）
}

interface TopicRegistryGetResult {
  topics: TopicEntry[];
  compaction_count: number;
  last_updated: ISO8601;
}
```

**新增tool: `budget_status`**

```typescript
interface BudgetStatusParams {}

interface BudgetStatusResult {
  total_budget: number;
  used_tokens: number;
  utilization: number;
  pressure_level: PressureLevel;
  tier_usage: {
    index: { allocated: number; used: number };
    active: { allocated: number; used: number };
    warm: { allocated: number; used: number };
    cold: { allocated: number; used: number };
  };
  topics_by_tier: {
    active: string[];
    warm: string[];
    cold: string[];
    archived: string[];
  };
}
```

**新增tool: `never_consolidate_add`**

```typescript
interface NeverConsolidateAddParams {
  topic_id: string;
  content: string;
  type: 'decision' | 'error_fix' | 'config' | 'instruction' | 'constraint';
  reason?: string;
}

interface NeverConsolidateAddResult {
  item_id: string;
  success: boolean;
}
```

### 6.3 Event Emissions

系统通过structured events记录所有重要操作，供observability和debug使用：

```typescript
type FishTrailEvent = 
  | { type: 'topic_detected'; topic_id: string; method: string; confidence: number }
  | { type: 'topic_created'; topic_id: string; label: string }
  | { type: 'state_transition'; topic_id: string; from: TopicState; to: TopicState; reason: string }
  | { type: 'consolidation_triggered'; topic_id: string; trigger: ConsolidationTrigger }
  | { type: 'consolidation_completed'; topic_id: string; compression_ratio: number; quality: number }
  | { type: 'consolidation_failed'; topic_id: string; reason: string }
  | { type: 'budget_pressure'; level: PressureLevel; utilization: number }
  | { type: 'overflow_action'; action: OverflowAction }
  | { type: 'compaction_hook'; compaction_id: string; topics_affected: number }
  | { type: 'registry_updated'; changes: string[] }
  | { type: 'migration_completed'; topics_migrated: number };
```

Event sink配置：
- 默认：写入`.petfish/fish-trail/events.jsonl`（append-only）
- 可选：emit到MCP event channel（如果平台支持）
- Debug模式：同时写入console log

### 6.4 Plugin Interface Contract — DEFERRED TO v3

> **v2 scope decision**: Plugin/extension architecture deferred to v3. v2 hardcodes all 6 components with no third-party extension points. Rationale: zero users exist to inform API surface design; prove value first, extract extension points from real usage patterns later.
>
> When v3 introduces plugins, consider: custom detection rules, custom consolidation strategies, custom output formatters, event listeners. Load from `.petfish/fish-trail/plugins/`.

---

## 7. Error Handling & Edge Cases

### 7.1 错误处理矩阵

| 错误场景 | 检测方式 | 处理策略 | 降级行为 |
|----------|----------|----------|----------|
| Topic detection失败 | detect()抛异常或返回null | Continuation fallback | 消息归入last active topic |
| Registry文件损坏 | JSON parse失败 | 从备份恢复；如无备份，rebuild | 从消息历史重建空registry |
| Registry文件不可写 | Write操作抛IO error | 内存中维护state，retry写入 | 本次session内有效，重启后丢失 |
| Budget计算溢出 | total > window或分配为负 | 强制进入emergency mode | 所有topic仅summary |
| Semantic MCP不可用 | 调用timeout或connection refused | 跳过Layer 2 | 仅rule + continuation |
| Consolidation质量过低 | quality_score < threshold | 保留raw，标记失败 | 不做summarize |
| 零topics检测到 | registry.topics.size == 0 | 创建单一"session"topic | 整个session作为单topic |
| 单topic消息极多 | 单topic消息数>100 | Internal sub-segmentation hint | 在topic内部按时间段分块 |
| 并发访问registry | 多agent实例同时写入 | File lock + last-write-wins | 最后写入者覆盖（可接受） |
| Compaction hook未注册 | Hook点不存在 | 使用替代方案（MCP tool injection） | 功能完整但触发时机延迟 |

### 7.2 Registry Corruption Recovery

```pseudocode
function recoverRegistry():
  // Strategy 1: 从备份恢复
  backups = listDir('.petfish/fish-trail/registry-backups/')
  if backups.length > 0:
    latest = backups.sortByDate().last()
    registry = readJSON(latest)
    if validateRegistry(registry):
      return registry
  
  // Strategy 2: 从v1 topic graph重建
  if exists('.petfish/fish-trail/topic_graph.json'):
    return migrateV1toV2()
  
  // Strategy 3: 创建空registry
  return createEmptyRegistry()
```

### 7.3 Extremely Long Single Topic

当单个topic的消息数超过100条时，系统不做强制分割（避免人为制造topic boundary），但提供sub-segmentation hint：

```
策略:
1. 在该topic的raw messages中插入时间段分隔标记
2. 在budget pressure时，优先trim该topic的早期消息
3. 在summary中标注"此topic内容跨度较长，可能包含多个子阶段"
4. 不创建sub-topic（除非用户显式请求）
```

### 7.4 Concurrent Access

多agent实例（如background agent + foreground agent）可能同时操作registry：

```
保护措施:
1. 文件级锁（advisory lock）：写入前acquire，写入后release
2. 乐观并发：读取时记录updated_at，写入时check是否被修改
3. 冲突解决：last-write-wins（简单策略，对于topic registry可接受）
4. 严重冲突：如果检测到state不一致，merge两个版本的state transitions

为什么last-write-wins可接受：
- Topic state transitions是单调的（active→warm→cold→archived）
- 最坏情况是某个topic的state transition被延迟一个cycle
- Registry的message_count等统计字段误差在可接受范围内
```

---

## 8. Observability & Metrics

### 8.1 Metrics定义

系统emit以下metrics：

| Metric名称 | 类型 | 说明 |
|------------|------|------|
| `fish_trail_v2.topic_count` | gauge | 各state的topic数量 |
| `fish_trail_v2.tier_distribution` | histogram | topic在各tier的分布 |
| `fish_trail_v2.budget_utilization` | gauge | 当前budget使用率(0-1) |
| `fish_trail_v2.pressure_level` | gauge | 当前pressure level(0-3) |
| `fish_trail_v2.consolidation_events` | counter | consolidation触发次数 |
| `fish_trail_v2.consolidation_quality` | histogram | consolidation质量分数分布 |
| `fish_trail_v2.consolidation_failures` | counter | consolidation失败次数 |
| `fish_trail_v2.detection_confidence` | histogram | detection置信度分布 |
| `fish_trail_v2.detection_method` | counter | 各detection method使用次数 |
| `fish_trail_v2.overflow_actions` | counter | overflow处理动作次数（by type） |
| `fish_trail_v2.compaction_duration_ms` | histogram | compaction hook执行耗时 |
| `fish_trail_v2.registry_size_bytes` | gauge | registry文件大小 |
| `fish_trail_v2.state_transitions` | counter | state transition次数（by from→to） |

### 8.2 Logging规范

| Log Level | 内容 |
|-----------|------|
| ERROR | Registry corruption, compaction hook failure, unrecoverable state |
| WARN | Consolidation failure, pressure level升级, detection confidence极低, concurrent write conflict |
| INFO | State transitions, compaction events, migration完成, configuration变更 |
| DEBUG | 每条消息的detection结果, budget计算detail, consolidation过程 |
| TRACE | 完整decision trace（仅debug mode） |

Log格式：

```json
{
  "ts": "2026-05-20T10:30:00.000Z",
  "level": "info",
  "component": "tiered-retention",
  "event": "state_transition",
  "topic_id": "project:rswitch",
  "from": "active",
  "to": "warm",
  "reason": "message_gap_exceeded",
  "details": { "gap": 8, "threshold": 5 }
}
```

### 8.3 Debug Mode

开启方式：配置`observability.debug_trace = true`或环境变量`FISH_TRAIL_DEBUG=true`

Debug模式下额外输出：

1. **Detection trace**: 每条消息经过的三层detection的完整推理过程
2. **Budget trace**: allocation计算的每一步数值
3. **Consolidation trace**: summary生成的input/output/quality评估
4. **State machine trace**: 每个topic的state变更原因链

Debug输出位置：`.petfish/fish-trail/debug-trace.jsonl`

---

## 9. Open Questions & Future Work

### 9.1 Re-expand机制

当前v2设计中，COLD→ACTIVE的re-activation仅恢复summary。未来可考虑：

- **Full re-expand**: 从外部存储（如MCP topic graph的detail files）重新加载完整历史
- **Selective re-expand**: 仅恢复与当前query相关的历史片段（需semantic search）
- **On-demand re-expand**: 用户显式请求"展开这个topic的完整历史"时触发

设计考量：
- Re-expand会消耗大量budget，需要相应压缩其他topic
- 需要外部存储层配合（当前registry不存储full messages）
- 可能需要与OpenCode的session history对接

### 9.2 Cross-session Topic Persistence

当前：registry在单个project内跨compaction持续。
未来：利用现有的context-state MCP topic graph实现跨session持续。

```
设想:
- Session结束时将registry snapshot同步到topic graph
- 新session开始时从topic graph恢复registry
- 解决问题：用户跨session回到相同project时，系统仍记得topic结构
```

与现有fish-trail MCP的集成点：
- `topic_create` → 对应v2中新topic创建
- `topic_update` → 对应state transition
- `topic_archive` → 对应ARCHIVED状态
- `context_build` → 可用于re-expand时获取topic full context

### 9.3 Multi-agent Topic Sharing

当前v2假设单agent场景。多agent场景的挑战：

- 多个agent可能同时在不同topic上工作
- 每个agent的context window独立，但topic registry共享
- 需要agent-aware的budget allocation

可能的设计：
```
每个agent维护独立的"视角"（view），共享registry但有独立的:
- active topic选择
- budget allocation
- state awareness

registry增加agent_views字段：
interface AgentView {
  agent_id: string;
  active_topics: string[];
  last_seen_message_idx: number;
}
```

### 9.4 Adaptive Threshold Tuning

当前：所有threshold是静态配置值。
未来：基于用户行为模式自适应调整。

可能的适应维度：
- 如果用户频繁在topics之间切换 → 降低warm_to_cold_compactions（更快归档不活跃topic）
- 如果用户session通常很短 → 提高active_threshold_messages（更宽松的active判定）
- 如果用户倾向于回溯旧topic → 延长cold_to_archived_compactions（保留更多在context中）
- 如果context window较小 → 自动调低budget ratios中的warm/cold占比

实现方式：
- 收集usage pattern metrics
- 定期（每N次compaction）评估当前threshold效果
- 生成建议调整（不自动生效，需用户确认）

### 9.5 Quality-of-Consolidation评估

当前consolidation quality assessment是self-assessed（由生成summary的同一个LLM评估质量）。未来可考虑：

- **Cross-reference check**: 对比summary和原文的信息覆盖率
- **User feedback loop**: 如果用户在summary topic上反复ask for detail → 标记quality不足
- **A/B testing**: 对同一topic生成多个summary版本，评估哪个更好

---

## 10. Appendix

### 10.1 Decision Matrix: TAC vs EPIS评估结果 → 设计影响

本节记录从"Faulty Memory"论文评估中得出的设计决策。

| 评估维度 | 发现 | 对v2设计的影响 |
|----------|------|----------------|
| TAC (Topic-Aware Consolidation) | 按topic边界做consolidation显著减少misgrouping | → v2的Consolidation Gate严格遵守topic boundary |
| EPIS (Episodic-Preferential Retention) | 近期episodic memory的完整保留优于uniform summarization | → ACTIVE tier保留full raw messages |
| Recency效应 | 最近5条消息内的topic几乎一定需要full retention | → `active_threshold_messages=5`的默认值来源 |
| Interference距离 | 超过1次compaction未访问的topic与active topic混合会产生interference | → `warm_to_cold_compactions=1`的默认值来源 |
| Schema formation | 重复接触+time gap是形成稳定schema的条件 | → WARM→COLD的transition正是模拟slow consolidation过程 |
| Never-forget items | 某些信息不适合consolidation（如约束、配置、决策） | → never-consolidate list设计 |
| Budget pressure下的优先级 | 放弃远期信息优于损害近期信息 | → Pressure degradation从COLD开始压缩 |
| Over-consolidation风险 | 过早summarize会不可逆地丢失后续推理需要的detail | → Consolidation Gate的quality check + rollback机制 |

### 10.2 "Faulty Memory"论文发现 → v2设计映射

| 论文发现 | 引用 | v2对应设计 |
|----------|------|-----------|
| "Forced consolidation of heterogeneous content produces misgrouping errors" | Section 4.2 | Topic-aware consolidation boundary: 永远不跨topic做summarize |
| "Recency-based differential retention outperforms uniform compression by 34%" | Table 3 | Tiered retention: ACTIVE保留raw, COLD仅summary |
| "Items accessed within last 5 interactions require full episodic access for correct recall" | Section 5.1 | `active_threshold_messages = 5` |
| "Single compaction without access is sufficient indicator for transition to schema memory" | Section 5.3 | `warm_to_cold_compactions = 1` |
| "Error-correction pairs and explicit decisions are disproportionately important for task continuity" | Section 6.1 | Never-consolidate list (error_fix, decision types) |
| "Budget pressure should degrade gracefully starting from least-accessed content" | Section 6.4 | Three-level pressure degradation (COLD first) |
| "Quality-gated consolidation prevents catastrophic information loss" | Section 7.2 | Consolidation Gate with quality threshold + rollback |
| "CLS-inspired dual-store (fast episodic + slow schema) is the optimal memory architecture for LLM agents" | Section 8, Conclusion | 整个v2 tiered architecture设计基础 |

### 10.3 术语表

| 术语 | 定义 |
|------|------|
| CLS | Complementary Learning Systems，互补学习系统理论。大脑中hippocampus（快速episodic）和neocortex（慢速schema）的互补模型 |
| Compaction | OpenCode中context window满时触发的压缩操作，将历史消息summarize以释放空间 |
| Compaction trigger | 触发compaction的事件（window满、手动触发、session结束） |
| Consolidation | 将raw messages转化为summary的过程，类似记忆巩固 |
| Context window | LLM可用的总输入token空间 |
| Episodic memory | 保留完整原始经历的记忆类型（对应ACTIVE tier） |
| Misgrouping | 将不相关信息错误关联到一起的现象（强制跨topic summarize时常发生） |
| Never-consolidate | 标记为不可被summarize的重要信息项 |
| Pressure level | Budget使用率超过阈值时的系统状态（l1/l2/l3） |
| Re-expand | 将已summarize的topic重新展开为详细内容 |
| Registry | Topic Registry，持久化存储所有topic状态的JSON文件 |
| Retention | 决定保留什么内容的策略 |
| Schema memory | 通过consolidation形成的抽象知识（对应COLD tier的summary） |
| Semantic detection | 基于语义相似度的topic分配方法 |
| Tier | 分层级别（ACTIVE/WARM/COLD/ARCHIVED） |
| Topic | 一个连贯的工作主题，由多条相关消息组成 |
| Topic boundary | Topic之间的分界线，consolidation不应跨越此边界 |

### 10.4 相关文档

| 文档 | 位置 | 关系 |
|------|------|------|
| fish-trail v1 SKILL.md | `.opencode/skills/fish-trail/SKILL.md` | 现有实现的skill定义 |
| context-state MCP | `.opencode/skills/fish-trail/`下的MCP配置 | v1的backend |
| AGENTS.md fish-trail规则 | `agents-rules/fish-trail.md` | v1的always-on行为定义 |
| Faulty Memory论文 | arXiv:2605.12978 | 理论基础 |
| Tiered Memory评估memo | `research/06_outputs/` | 前置评估文档 |

---

## 变更日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-05-20 | v2.0-draft | 初版产品规格书 |
