---
description: 审计当前课程项目结构、资料归属和质量状态，生成整理建议
agent: directory-curator
subtask: true
---
请审计当前课程项目的目录结构、命名、资料归属与交付边界。

用户补充说明：
$ARGUMENTS

如果项目存在以下目录，请重点审查：
!`find . -maxdepth 3 \( -path './.git' -o -path './node_modules' \) -prune -o -type d | sed 's#^./##' | sort | head -200`

输出要求：
-当前结构判断
-缺失目录
-混放问题
-建议移动/重命名/归档的内容
-整理优先级
-是否建议执行初始化脚本或结构审计脚本
