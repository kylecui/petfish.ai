# Petfish Style Guide

## 1. Core Writing Identity

The style is based on engineering problem analysis.

It does not try to impress the reader. It tries to help the reader understand:

- what the issue is
- why it matters
- how it can be decomposed
- what conclusion follows

## 2. Macro Structure

Most formal documents should follow a total-part-total structure.

### Opening

The opening should introduce only necessary background.

Good opening pattern:

```text
随着 X 的发展，Y 面临了新的约束。该问题在 Z 场景中更加明显。
```

Avoid generic openings:

```text
在当今高度复杂的时代背景下，X 已经成为不可忽视的重要问题。
```

### Body

The body should decompose the issue into 2–4 dimensions.

Common dimensions:

-技术约束
-管理约束
-执行路径
-风险影响
-现有方案局限
-可行改进方向

### Closing

The closing should converge.

Good closing forms:

```text
因此，有必要在现有方案基础上引入 X，以提升 Y 的能力。
```

```text
从这个角度看，下一步工作应集中在 X 和 Y 两个方面。
```

Bad closing forms:

```text
让我们携手共建更加美好的未来。
```

## 3. Micro Structure

Each paragraph should follow one of these patterns:

### Pattern A: Problem paragraph

```text
[现象]。这带来了 [问题]。其核心原因在于 [原因]。
```

### Pattern B: Analysis paragraph

```text
一方面，[因素 A]；另一方面，[因素 B]。二者共同导致 [结果]。
```

### Pattern C: Method paragraph

```text
为了解决这一问题，可以从 [方向] 入手。具体来说，需要 [动作 1] 和 [动作 2]。
```

### Pattern D: Cautious judgment paragraph

```text
在当前条件下，该方案可以解决 [问题]，但仍然受到 [限制] 的影响。因此，它更适合作为 [定位]，而不是 [定位]。
```

## 4. Language Rules

Use direct and restrained language.

Prefer:

-需要
-可以
-应当
-有必要
-面临
-受到限制
-具备条件
-形成闭环
-进行验证

Avoid:

-极大赋能
-全面升级
-颠覆式改变
-打造标杆
-形成强大抓手
-实现质的飞跃

## 5. Evidence Rules

Do not make unsupported claims.

Weak:

```text
该方案具有很高的可行性。
```

Better:

```text
该方案不依赖终端改造，且能够复用现有网络节点。因此，在部署复杂度上具备一定优势。
```

## 6. Negative Statements

Negative statements should be objective.

Weak:

```text
这个设计很糟糕。
```

Better:

```text
该设计没有区分控制逻辑和执行逻辑，后续扩展时容易出现耦合过重的问题。
```

## 7. English Style

English writing should be clear and operational.

Preferred patterns:

```text
Here are the key findings.
```

```text
Based on the trace, the issue appears to be caused by ...
```

```text
A potential workaround is to ...
```

Avoid dramatic writing:

```text
This revolutionary architecture will completely transform ...
```

## 8. Common Document Types

### Technical analysis

Use:

- background
- problem
- analysis
- conclusion

### Proposal

Use:

- customer need
- current limitation
- proposed approach
- delivery plan
- expected result

### Course material

Use:

- concept clarification
- example
- analysis
- hands-on task
- feedback and improvement

### Email

Use:

- acknowledgement
- key points
- evidence
- action or conclusion
- concise closing

## 9. Register Switching Rules

The same underlying message must wear different clothes for different audiences. Switch register deliberately.

| From register | To register | What changes |
|---|---|---|
| Academic paper | Executive summary | Drop hedges and jargon; lead with cost/risk/benefit; use bullets |
| Technical report | Support email | Add acknowledgement and explicit next action; remove background unless requested |
| Academic paper | Blog post | Use shorter sentences, direct address, and one concrete example early |
| Engineering memo | Patent draft | Use formal claim language; avoid evaluative adjectives; define terms precisely |
| Course material | Slide deck | Convert paragraphs to one idea per slide; favor examples over definitions |
| Incident postmortem | Customer update | Emphasize impact window, root-cause category, and preventive action; omit blame |

Rule: do not translate content word-for-word across registers. Rebuild the structure for the new reader.

## 10. Terminology Consistency Table

Consistent terminology reduces cognitive load. Track key terms across a document or project.

| Concept | Preferred term | Avoided variants | Notes |
|---|---|---|---|
| AI writing signal | AI腔 | AI味, machine flavor | Use in Chinese context |
| Style rewrite | de-AI rewrite | humanize, polish | Use when the goal is to remove AI flavor |
| Custom style file | `.petfish/style-profile.md` | style profile, profile | Capitalize as a proper file reference |
| Detection report | de-ai-detector report | detector output | Use the tool name as adjective |
| Sentence-length variance | burstiness | variability | Academic term of art |
| Connector density | connector stacking | transition spam | Stacking implies excess |
| Parallel structure | 排比 | parallelism (in Chinese) | Use the Chinese term for Chinese text |

When a user provides a style profile, let the profile's terminology table override this default table.

## 11. Tone Calibration by Audience

Adjust tone without changing factual claims.

| Audience | Tone | Sentence length | Hedging | Examples |
|---|---|---|---|---|
| Internal engineer | Direct, minimal | Short to medium | Rare | "The fix is in PR #234." |
| Cross-functional team | Neutral, structured | Medium | Moderate | "Three blockers remain; see below." |
| Customer / executive | Reserved, outcome-focused | Medium | Low | "Deployment will reduce P99 latency by 40%." |
| Academic reviewer | Formal, defensible | Varied (burstiness) | Load-bearing | "This suggests, though it does not prove, that …" |
| Public blog | Conversational but precise | Short | Occasional | "We tried X. It didn't work. Here's why." |
| Legal / compliance | Cautious, explicit | Medium to long | Frequent | "Subject to the limitations described in Section 4…" |

Never mix two registers in the same paragraph. If the audience shifts, insert a section break.

## 12. Micro-Editing Checklist

Before finalizing any paragraph, run this quick check:

1. Is the first sentence doing work, or only setting the scene?
2. Does every sentence add information a reader would not already know?
3. Are there two or more consecutive sentences with the same structure?
4. Are all connectors load-bearing, or are some doing the reader's work?
5. Is the closing sentence a real conclusion, or a restatement?
6. Are Chinese-English technical terms compact (e.g., `API接口`, not `API 接口`)?

If any answer is unsatisfactory, revise the paragraph before moving on.
