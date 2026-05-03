# Prompt Patterns for Anti-Sycophancy Calibration

## 1. Input neutralization patterns

把带预设答案的问题改写成可评估问题。

### Pattern A

```text
Leading:
我这个方案是不是明显最优？

Neutralized:
请从目标匹配度、成本、风险、替代方案四个维度评估该方案是否适合作为默认方案。
```

### Pattern B

```text
Leading:
你也觉得微服务一定比单体好吗？

Neutralized:
请比较微服务与单体在当前约束下的收益、代价、适用边界与迁移风险。
```

### Pattern C

```text
Leading:
我这样理解应该没问题吧？

Neutralized:
请判断这个理解成立的前提、可能错误点，以及需要补充的关键条件。
```

### Pattern D

```text
Leading:
这个设计不是已经很完整了吗？

Neutralized:
请检查该设计在接口边界、可测试性、风险控制和缺失假设上的完整度。
```

### Pattern E

```text
Leading:
客户都这么要求了，我们只能这么做，对吧？

Neutralized:
请区分客户诉求、现实约束与可替代实现，评估当前做法是否真的是唯一可行路径。
```

### Pattern F

```text
Leading:
你同意这个章节写得已经很好了吗？

Neutralized:
请按中心论点、结构、证据、推理、语言五个维度评估该章节的完成度与主要缺口。
```

## 2. Contrastive prompting patterns

用于固定“支持理由 vs 反对理由”的输出结构。

```text
请先列评价维度，再分别给出：
1. 支持该方案的最强理由
2. 反对该方案的最强理由
3. 更稳妥的替代方案
4. 当前结论与置信度
```

```text
Evaluate this proposal with a scorecard first, then provide the strongest case for it and the strongest case against it.
```

```text
不要只说优点。请给出支持理由、主要问题、替代路径，并说明在哪些条件下你的结论会改变。
```

## 3. Devil's advocate patterns

用于构造真正相关的 opposing case，而不是表演式反对。

```text
如果你必须从反方角度反驳这个方案，最有力的三点会是什么？要求基于真实约束，不要凭空挑刺。
```

```text
Assume the preferred approach fails in production. What is the most plausible failure chain, and which hidden assumption caused it?
```

```text
请从成本、复杂度、时间窗口、维护压力四个角度，为反对该方案构造最强论证。
```

```text
如果必须推荐一个替代路线，哪个路线最稳妥？它比原方案牺牲了什么，又换来了什么？
```

## 4. Evidence ladder patterns

把判断按证据强度分层表达。

```text
请把你的关键说法分别标记为：观察事实 / 合理推断 / 推测性判断 / 无依据猜测。
只有前两类可以支撑强结论。
```

```text
Claim: 当前接口设计边界不清。
Evidence type: 观察事实。
Support: 三个模块同时修改同一DTO，且没有单一owner。
```

```text
Claim: 这个方案上线后会拖慢团队速度。
Evidence type: 推测性判断。
Why: 目前没有迁移期数据，只能基于类似项目经验保守估计。
```

```text
Claim: 用户一定会喜欢这个方案。
Evidence type: 无依据猜测。
Why: 没有用户访谈、实验或历史数据支撑。
```

## 5. Confidence calibration patterns

把结论与确定性拆开。

```text
结论：我倾向于选择B方案。
置信度：Medium。
原因：目标匹配度和实现路径较清楚，但性能影响仍缺基准测试。
改变条件：如果压测结果显示延迟增加超过20%，则优先级需要下调。
```

```text
Conclusion: The direction is reasonable.
Confidence: Low.
What would change my mind: verified cost model, production constraints, and rollback plan.
```

```text
不要说“我觉得大概率没问题”就结束。必须补一句：什么事实出现后，你会改变这个判断。
```

## 6. Consecutive confirmation breaker

用于识别并打断 yes-loop。

触发信号：

- 连续3轮及以上出现“对吗/是不是/right?/correct?”
- 用户不断把问题改写成同一个确认句
- 回答已经给过边界，但用户仍追求单纯肯定

打断模板：

```text
我注意到连续多轮确认性提问，让我重新独立评估一下这个方向。
```

后续动作：

1. 回退到中性问题定义
2. 重建评分维度
3. 给出支持理由与反对理由
4. 单独输出结论与置信度
