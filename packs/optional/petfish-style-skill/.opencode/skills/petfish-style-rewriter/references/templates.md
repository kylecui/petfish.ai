# Templates

## 1. Technical Analysis

```markdown
# [Title]

## 1. Background

[Brief context. Do not over-expand.]

## 2. Problem

[Define the actual problem.]

## 3. Analysis

### 3.1 [Dimension 1]

[Condition → limitation → implication.]

### 3.2 [Dimension 2]

[Condition → limitation → implication.]

### 3.3 [Dimension 3]

[Condition → limitation → implication.]

## 4. Conclusion

[Converge to necessity or next step.]
```

## 2. Course Material

```markdown
# [Topic]

## 1. Concept

[Clarify the concept.]

## 2. Example

[Give a concrete example.]

## 3. Analysis

[Explain why the example matters.]

## 4. Hands-on Task

[Define what learners should do.]

## 5. Feedback and Improvement

[Explain how to evaluate and improve.]
```

## 3. Proposal Section

```markdown
## [Section Title]

[State the customer need.]

Current limitations are mainly reflected in the following aspects:

1. [Limitation 1]
2. [Limitation 2]
3. [Limitation 3]

Based on these limitations, this project should focus on [direction]. The expected result is [concrete outcome].
```

## 4. English Technical Email

```text
Hi [Name],

Thanks for [context].

Here are the key points.

1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

Based on the above, [conclusion or recommended action].

Please feel free to let me know if you have any questions or concerns.

Regards,
[Name]
```

## 5. Chinese Formal Rewrite

```markdown
[背景句。只保留必要背景。]

该问题主要体现在以下几个方面：

1. [问题一]
2. [问题二]
3. [问题三]

因此，[必要性或下一步方向]。
```

## 6. Academic Paper — Abstract (humanized)

This template operationalizes the academic humanization framework from `academic-writing.md`. It deliberately breaks the symmetric "Background / Method / Result / Conclusion" shape.

```text
[Problem or gap, stated concretely in one sentence. Avoid "In recent years" openings.]

[Approach in one clause, with a natural qualifier such as "empirically" or "in a controlled setting" if accurate.]

[Main result with a number or a bounded claim.]

[One qualification or scope limit — a candid hedge, not a generic one.]

[Implication, hedged. Close on a bounded forward statement, not a slogan.]
```

Word budget: 150–250 words. Reorder when the result is the most interesting part.

## 7. Academic Paper — Introduction

```markdown
## 1. Introduction

[Paragraph 1: the problem, stated concretely. Do not over-expand background. Insert one authorial phrase such as "we observe" or "to our knowledge".]

[Paragraph 2: why existing approaches fall short. Name them. Break the template — start with the limitation, not the background.]

[Paragraph 3: what this work does, in one or two sentences, then the contribution list. Each contribution is a bounded claim, not a slogan.]

[Paragraph 4, optional: a roadmap only if the paper structure is non-standard. For IMRaD, drop the roadmap.]
```

## 8. Academic Paper — Related Work (grouped, not enumerated)

```markdown
## 2. Related Work

[Approach group A.] [One sentence on the approach.] [One sentence on the limitation relevant to this paper.]

[Approach group B.] [One sentence on the approach.] [One sentence on the limitation relevant to this paper.]

[Closing sentence: position this work relative to the closest prior approach. Do not list papers as a flattened enumeration — the grouping is an authorial choice.]
```

## 9. Academic Paper — Results (with candor)

```markdown
## 4. Results

[Main result first, with dispersion measure or interval.]

[Secondary results.]

[At least one negative, null, or surprising result. Use "we observe" for direct observations; reserve "this suggests" for interpreted claims.]

[Note any effect that was smaller or less consistent than expected.]
```

## 10. Academic Paper — Discussion and Conclusion

```markdown
## 5. Discussion

[Open with the most surprising or consequential result.]

[Contrast with the closest prior result.]

[Limitations, grouped by source: data, method, scope.]

## 6. Conclusion

[One paragraph. Restate the contribution in different words from the abstract. Add one scope limit not in the abstract. Close with a specific next step, not "future work is promising".]
```

## Template Selection Decision Tree

Use this tree to pick the right template quickly.

```text
Is the input a paper draft, thesis chapter, abstract, related work, or grant proposal?
  yes → Use templates 6–10 (academic) and load references/academic-writing.md
  no  → Continue

Is the primary goal to persuade a stakeholder or customer?
  yes → Use template 3 (proposal)
  no  → Continue

Is the output an email or short message?
  yes → Use template 4 (English email) or 5 (Chinese formal rewrite)
  no  → Continue

Is the output teaching material?
  yes → Use template 2 (course material)
  no  → Continue

Is the output a structured technical analysis?
  yes → Use template 1 (technical analysis)
  no  → Use the generic total-part-total structure in references/style-guide.md
```

## Fill-In Examples

These mini-drafts show how to populate each template.

### Technical analysis

```markdown
# 网关超时问题分析

## 1. Background

支付网关自上周起偶发 502 错误，集中在晚高峰。

## 2. Problem

上游服务降级时，网关没有熔断逻辑，导致请求堆积并拖垮自身。

## 3. Analysis

### 3.1 超时配置

当前超时设为 30 秒，远高于上游 P99 响应时间，无法及时释放连接。

### 3.2 重试策略

默认重试 3 次且幂等校验不足，放大了故障流量。

### 3.3 监控盲区

缺乏对连接池使用率的实时告警，问题发现滞后约 5 分钟。

## 4. Conclusion

应先缩短网关超时至 5 秒并引入熔断，再补齐连接池监控。
```

### Course material

```markdown
# 理解幂等性

## 1. Concept

同一操作执行多次与执行一次的效果相同，称为幂等。

## 2. Example

HTTP DELETE /orders/42 重复发送两次，结果仍是该订单被删除。

## 3. Analysis

幂等性通过唯一请求标识和去重表实现；非幂等操作（如 POST）需要额外设计。

## 4. Hands-on Task

为订单创建接口添加幂等键，并验证重复提交不会创建重复记录。

## 5. Feedback and Improvement

检查去重键的过期时间是否覆盖业务窗口；观察并发下的竞态条件。
```

### English technical email

```text
Hi Alex,

Thanks for sharing the latency report.

Here are the key findings.

1. P99 latency increased from 95 ms to 210 ms after the v2.3 rollout.
2. The regression is isolated to the /export endpoint.
3. CPU profiling shows 60% time spent in JSON serialization.

Based on the above, I recommend we switch to a streaming serializer and re-measure before the next release.

Please let me know if you want me to open a tracking issue.

Regards,
Lin
```

### Academic abstract (humanized)

```text
Existing API documentation tools either require manual maintenance or produce stale references. We built a pipeline that extracts endpoint contracts from source code and generated tests, then rewrites them into Markdown. In a repository with 340 endpoints, the pipeline kept 97% of documents synchronized across six release cycles. The approach assumes tests accurately reflect intended behavior; when tests are missing, the generated docs inherit their gaps. For teams already using contract tests, this reduces documentation drift without adding a separate maintenance step.
```

## Common Template Mistakes

1. **Filling every field equally**. Not every template slot deserves the same length. Put weight where the reader cares most.
2. **Copying the abstract into the conclusion**. The conclusion should restate the contribution in different words and add a new scope limit.
3. **Using academic templates for non-academic text**. The abstract template's hedges and authorial voice weaken engineering memos.
4. **Forcing a roadmap**. In standard IMRaD papers, the roadmap paragraph adds noise; drop it unless the structure is unusual.
5. **Preserving source order in Related Work**. Group by approach, not by citation sequence.
6. **Ending emails with empty pleasantries**. "Please feel free to let me know if you have any questions" is acceptable once; repeated in every email it becomes noise.
7. **Ignoring word budget in abstracts**. An abstract that is 80 words or 350 words both signal poor control; stay inside 150–250 words.

When a template feels wrong for the content, break it. Templates are starting points, not straitjackets.
