# git-intro-violations fixture 说明

`git-intro-standard` 的破坏版，用于 runner `--selftest` 的必挂断言。

故意引入的违规：

1. **模块数 15**：超出 standard-training 预设上限 12 → qa_scan blocker
2. **实验配比 0/15 = 0**：低于 lab_ratio 下限 0.2 → qa_scan major
3. **lesson 缺 3 个结构标记**：`01-lesson-01.md` 仅有"目标"，缺 示例/练习/时长 → qa_scan check#10 major
4. **模块 15 无目标**：触发 pedagogy rule `module-objectives` 校验失败

其余维度（首模块导论、课时声明、测评类型、kebab 命名、H1）保持合规，确保失败可归因于上述定点违规。
