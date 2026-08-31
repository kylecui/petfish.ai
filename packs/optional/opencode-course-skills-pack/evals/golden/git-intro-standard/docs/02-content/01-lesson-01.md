# 第 1 课：版本控制与第一个仓库

## 目标

完成本课后，学员能够解释版本控制的价值，并独立创建第一个本地 Git 仓库。本课目标对应模块一目标。

## 示例

以"论文草稿 v1/v2/final/final2"的混乱命名引入版本控制问题，随后演示：

```bash
git init demo-repo
cd demo-repo
git config user.name "Learner"
git config user.email "learner@example.com"
echo "# demo" > README.md
git add README.md
git commit -m "initial commit"
```

## 练习

1. 初始化一个名为 `practice` 的仓库。
2. 创建两个文件并分别提交，观察 `git log` 输出。
3. 用 `git status` 解释工作区与暂存区的状态变化。

## 时长

45 分钟（讲授 20 分钟 + 演示 10 分钟 + 练习 15 分钟）。
