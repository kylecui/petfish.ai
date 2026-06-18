# Rewrite Examples

## Example 1: Chinese-English spacing normalization

### Input

接入层支持Webhook挂载。接入事件包括Git提交，Issue更新和PR合并。

### Output

接入层支持Webhook挂载。接入事件包括Git提交、Issue更新和PR合并。

## Example 2: remove AI-style expression

### Input

在当今高度复杂的网络对抗格局中，银弹式的单点防御理念早已失效。现代网络安全的核心挑战，已经从对单一威胁指标的被动响应，转变为对复杂攻击者战术、技术和程序的主动理解与体系化对抗。

### Output

随着网络环境和攻击路径的复杂化，单一防御手段已经难以覆盖全部风险。

一方面，攻击活动通常会跨越多个阶段，仅依赖单个告警或单项指标难以还原完整过程。另一方面，不同安全设备产生的数据存在视角差异，需要通过关联分析才能形成较稳定的判断。

因此，安全分析不能只关注单一指标，而需要围绕攻击过程建立跨数据源的分析方法。

## Example 3: formal Chinese technical writing

### Input

AI渗透测试智能体会让攻击门槛普惠化，也会极限拔高高级攻击能力。

### Output

AI渗透测试智能体会改变攻击能力的使用方式。

对于低能力攻击者而言，智能体可以将部分侦察、扫描和漏洞利用流程自动化，从而降低实施复杂攻击链的技术门槛。对于高能力攻击者而言，智能体可以承担重复性任务，使攻击者能够同时管理更多目标和更大的攻击面。

因此，防御方需要关注的不只是单个攻击工具的能力变化，而是攻击组织方式和执行效率的变化。

## Example 4: English technical email

### Input

The hotfix is not related. The capture shows packet loss. Network should check it.

### Output

Hi [Name],

Thanks for the update.

Based on the network trace, the hotfix does not appear to be related to this issue. The trace indicates that the missing data was not captured by the network adapter on the receiving server. This usually means the packets did not reach the server, rather than being modified by the operating system.

Therefore, the next step should be to review the network path between the two servers and identify whether any device is filtering or dropping the traffic.

Please feel free to let me know if you have any questions or concerns.

## Example 5: Academic abstract — de-AI a symmetric, low-burstiness draft

### Input (AI-like: uniform sentence length, symmetric template, no authorial voice)

In recent years, transformer-based models have achieved significant progress in code generation tasks. However, existing approaches face challenges in handling complex multi-file dependencies. We propose a novel framework that leverages graph-based dependency analysis to improve code generation accuracy. Our approach constructs a dependency graph from the repository context and incorporates it into the generation process. Experimental results demonstrate that our method achieves state-of-the-art performance on three benchmarks. Specifically, our method improves the pass rate by 12.3% on average. Furthermore, our approach shows robust generalization to unseen programming languages.

### Output (academic mode: burstiness, authorial voice, broken symmetry, candor)

Generating code that touches multiple files in a repository is still hard for current models. The core difficulty is dependency resolution: a function defined in one file may be called from another, with types and side effects that the model cannot see in the local context.

We propose a graph-based dependency analysis that constructs a repository-level dependency graph and feeds it into the generation process. On three standard benchmarks, the average pass rate improves by 12.3 percentage points. Somewhat to our surprise, the gain is concentrated in repositories with fewer than 50 files; on larger repositories, the improvement is smaller and noisier across seeds.

This suggests that graph-based context helps most when the dependency structure is tractable. For larger repositories, the graph itself may introduce noise that offsets the contextual gain.

### What changed

- **Burstiness**: the first paragraph has a short opening sentence, then a longer explanatory one.
- **Authorial voice**: "Somewhat to our surprise" and "This suggests" carry epistemic stance.
- **Candor**: the negative result on large repositories is kept, not hidden.
- **Broken symmetry**: the third paragraph opens with the implication, not with "Furthermore".
- **Removed**: "In recent years", "significant progress", "novel framework", "state-of-the-art", "robust generalization".

## Example 6: Academic paragraph — break syntactic over-symmetry

### Input (AI-like: four sentences, same template, same length)

The model achieves high accuracy on the classification task. The model handles edge cases gracefully. The model scales to large datasets without degradation. The model integrates with existing pipelines seamlessly.

### Output (broken template, varied length, hedged where appropriate)

The model achieves high accuracy on the standard classification benchmark. Edge cases require a fallback path, which we describe in Section 3.2. At scale, throughput degrades linearly rather than gracefully — this is the main practical limitation. Integration with existing pipelines is straightforward on the read path but requires a custom adapter for writes.

### What changed

- Each sentence now carries distinct information, not a parallel restatement.
- Sentence length varies (10, 13, 17, 15 words vs. the original uniform ~10).
- A limitation is stated candidly ("this is the main practical limitation").
- "Seamlessly" is removed and replaced with the specific integration condition.

## Example 7: Related work — grouped, not enumerated

### Input (AI-like: flattened enumeration, no grouping, symmetric)

Smith et al. proposed method A for X. Jones et al. extended this with method B. Lee et al. introduced method C which improves upon B. Wang et al. combined A and C into method D. Our work differs by proposing method E.

### Output (grouped by approach, positioned, non-symmetric)

Prior work on X falls roughly into two groups. The first group, following Smith et al. and extended by Jones et al., treats the problem as a sequence labeling task. The second group, initiated by Lee et al. and refined by Wang et al., frames it as a graph completion problem. Our approach borrows the graph representation from the second group but replaces the completion objective with a constrained generation objective, which we find more robust to noisy edges.

### What changed

- Papers are grouped by approach, not listed chronologically.
- The closing sentence positions this work relative to the closest prior approach.
- The grouping itself is an authorial choice that carries information.
- Symmetric "A did X. B did Y." template is broken by the two-group structure.
