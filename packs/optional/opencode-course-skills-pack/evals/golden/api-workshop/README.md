# api-workshop golden fixture 说明

本 fixture 内容为 workshop（工作坊）风格课程，但 `docs/00-project/course-type.yaml` 声明为 `standard-training`。

**原因**：course pack 当前仅提供 `standard-training` 一个 outline-constraints 预设（P0 阶段决策：先跑通一个预设再扩展）。若声明 `type: workshop`，qa_scan 会报"preset 缺失" minor 问题，干扰 golden 基准的全绿语义。

workshop 类型预设属后续 phase 工作；本 fixture 暂以 standard-training 约束验证评测链路，待预设扩展后再切换。
