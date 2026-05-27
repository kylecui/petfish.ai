---
description: 初始化一个AI-agent友好的项目工作区，支持多种项目类型（code/course/ops/writing等）
---
请使用`project-initializer` skill来初始化当前项目。

用户补充说明：
$ARGUMENTS

执行要求：
1. 优先读取当前目录结构，判断是空项目还是已有项目
2. 根据用户意图推断最合适的profile（minimal/course/code/ops/security-research/writing/skills-package/comprehensive）
3. 如果用户没有明确指定profile，简要询问项目类型后再执行
4. 使用`tools/init_project.py`进行确定性初始化，默认`--no-overwrite`
5. 初始化完成后，按照SKILL.md第11节的profile→pack映射表，自动运行petfish远程安装器安装推荐的技能包
6. 技能包安装完成后，进入Post-Init Wizard（SKILL.md第12节），逐步引导用户完成AGENTS.md、README.md、任务规划、Git初始化、Python环境、MCP配置等后续设置，每步可跳过
7. 如果uv未安装且项目需要Python环境，提醒用户安装uv
