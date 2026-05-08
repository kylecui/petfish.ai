# Literature Matrix Template

> 使用说明：每行对应一篇已纳入全文复核的文献。不要只粘贴摘要；每列都应基于正文、方法或实验部分填写。`Evidence IDs` 列用于关联证据账本条目。

| Paper ID | Citation | Research Problem | Method | Dataset/Object | Metrics | Main Findings | Limitations | Relation to Our Work | Evidence IDs |
|---|---|---|---|---|---|---|---|---|---|
| P-001 | Author, Year, Venue, DOI/URL | 该文解决什么问题；边界是什么 | 核心方法与关键机制 | 使用的数据集、系统对象或实验场景 | 指标定义与计算口径 | 主要结果（含条件） | 作者承认或可观察到的局限 | 支持/反驳/补充我们哪部分问题 | EV-000001, EV-000002 |
| P-002 |  |  |  |  |  |  |  |  |  |
| P-003 |  |  |  |  |  |  |  |  |  |

## 补充字段建议（可选扩展）

当研究复杂度较高时，可在主表后补充子表：

### Method Assumptions Table

| Paper ID | Key Assumptions | Failure Conditions | Deployment Constraints |
|---|---|---|---|
| P-001 |  |  |  |

### Evaluation Comparability Table

| Paper ID | Baseline Type | Dataset Comparability | Metric Comparability | Reproducibility Notes |
|---|---|---|---|---|
| P-001 |  |  |  |  |

## 填写检查清单

- `Research Problem` 不得写成泛化主题，需写明确任务与边界。
- `Method` 至少包含一条可区分于其他论文的方法特征。
- `Dataset/Object` 与 `Metrics` 必须可支持横向比较，口径不一致要注明。
- `Main Findings` 需要条件上下文，避免绝对化表述。
- `Limitations` 不能留空；没有显式限制时也要写“未报告但可观察风险”。
- `Relation to Our Work` 必须具体到研究问题，不写“相关”。
- `Evidence IDs` 至少关联一条证据账本条目，便于后续citation audit。
