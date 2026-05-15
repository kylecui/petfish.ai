# fish-trail

> Pack: **context**

topic_detect is high risk, users ask to 整理/切换/合并/归档话题 or 清空上下文, or mention topic governance/上下文污染/继承隔离/session resume. It routes continue/fork/switch/merge/archive/reset/bridge, applies context policy, builds context packages, logs decisions, and manages session boundaries via context-state MCP.

---

# Fish Trail — 话题治理器

## 触发条件

以下情况自动加载本skill：

- `topic_detect`返回风险等级**high**（分数61-100）
- 用户主动要求话题管理（关键词：整理话题、切换话题、合并话题、归档、清空上下文等）
- 用户提及fish-trail相关概念（topic、话题治理、上下文污染、继承策略等）

## 前置条件

- context-state MCP server已启动（通过SKILL.md frontmatter自动发现，或手动在opencode.json中配置）
- `.petfish/fish-trail/`目录已存在（首次使用时由`topic_create`自动创建）

## Optional: Semantic Embedding (v0.7.0+)

Fish-trail supports ONNX-based sentence embedding as a Tier 2 fallback for semantic drift detection. This is **fully optional** — without it, keyword-based detection works identically to v0.6.x.

**Install (optional):**
```bash
pip install onnxruntime>=1.23 tokenizers>=0.13 huggingface_hub numpy
```

**Platform support:** Linux x86_64/ARM64, macOS ARM64, Windows x64/ARM64. macOS Intel (x86_64) is not supported by onnxruntime >=1.24 and will fall back to keyword-only.

**Python requirement:** >=3.11 (onnxruntime 1.25.x requirement).

**Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (ONNX int8, ~118MB, downloads on first use).

**Configuration:** Add to `.petfish/fish-trail/config.json`:
```json
{
  "embedding": {
    "enabled": true,
    "preload": false,
    "timeout_ms": 2000
  }
}
```

See `docs/embedding-setup.md` for offline/air-gapped setup and troubleshooting.

## 核心概念

### Topic

话题单元。每个topic有独立的scope、summary、status和Context Package。详见`references/topic-model.md`。

### 关系类型（7种）

| 关系 | 含义 | 检测可靠性 | 自动执行 |
|------|------|-----------|---------|
| continue | 继续当前话题 | 高 | 是 |
| fork | 从当前分叉 | 高 | 是 |
| switch | 切换到已有话题 | 高 | 是 |
| reset | 清空上下文重新开始 | 高 | 是 |
| merge | 合并两个话题 | 中 | 否，需确认 |
| archive | 归档完成话题 | 中 | 否，需确认 |
| bridge | 建立桥接关系 | 低 | 否，需确认 |

### 污染风险评分

5维度评分（0-100），详见`references/contamination-scoring.md`。

| 等级 | 分段 | 行为 |
|------|------|------|
| low | 0-30 | 静默继续 |
| medium | 31-60 | 简要提示上下文范围 |
| high | 61-100 | 触发本skill完整工作流 |

### Context Package

为topic生成的Markdown上下文文件，详见`references/context-package-spec.md`。三种变体：标准包、桥接包、导出包。

### Session

会话单元。session绑定外部会话ID（如OpenCode session_id）或自动推断创建。每个session记录话题切换时间线、topic引用和工作摘要。存储在`.petfish/fish-trail/sessions/`。

- `external` session: 由外部平台提供session_id，ID格式 `oc_<external_id>`

*... (285 more lines in full SKILL.md)*
