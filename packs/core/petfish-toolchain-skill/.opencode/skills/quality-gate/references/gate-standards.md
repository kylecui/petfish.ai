# Quality Gate Standards Reference

## 1. 门禁层级

PEtFiSh采用三级门禁体系：

### Level 1: 格式门禁（skill-lint）
自动化检查，零人工干预：
- SKILL.md存在且frontmatter合法
- name: 小写kebab-case，≤64字符，无空格/大写/特殊字符
- description: 非空，≤1024字符
- 目录结构规范（SKILL.md在根目录，scripts/和references/可选）
- scripts有`--help`支持
- 无明显格式错误

### Level 2: 安全门禁（skill-security-auditor）
自动化静态分析：
- 无CRITICAL级危险命令（rm -rf, format, dd, curl|bash）
- 无secret读取（.env, .ssh, tokens, API keys）
- 无远程代码执行（eval远程内容, 动态import）
- 无过宽文件系统操作
- subprocess调用有适当约束
- 风险评分 ≤ 阈值

### Level 3: 人工审查
由skill maintainer执行：
- 业务逻辑合理性
- 与现有skill的重叠/冲突
- 触发描述的准确性
- 用户体验
- 文档完整性

## 2. 评分模型

### Lint评分（0-100）
```
100分起始
每个ERROR    -10分
每个WARNING  -5分
每个INFO     -2分
最低0分
```

通过阈值：≥ 80分

### 安全风险评分（0.0-1.0）
```
CRITICAL  权重 1.0
HIGH      权重 0.6
MEDIUM    权重 0.3
LOW       权重 0.1

风险分数 = min(1.0, sum(findings × weight) / 10)
```

通过阈值：≤ 0.5（PASS需≤ 0.3）

## 3. 发布决策矩阵

| Lint分数 | 安全分数 | CRITICAL数 | 决策 |
|----------|----------|-----------|------|
| ≥80 | ≤0.3 | 0 | PASS |
| ≥80 | 0.3-0.5 | 0 | CONDITIONAL |
| ≥80 | ≤0.5 | ≥1 | FAIL |
| <80 | any | any | FAIL |
| any | >0.5 | any | FAIL |

## 4. 常见FAIL原因及修复

### 格式类
| 问题 | 修复 |
|------|------|
| name含大写 | 改为kebab-case |
| description超长 | 精简到1024字符以内 |
| 缺少frontmatter | 添加`---`包裹的YAML头 |
| scripts无--help | 添加argparse + --help |

### 安全类
| 问题 | 修复 |
|------|------|
| shell=True | 改为shell=False + list args |
| rm -rf | 添加safeguard（确认/dry-run/范围限制） |
| 读取.env | 改为环境变量或参数传入 |
| curl\|bash | 下载后验证再执行 |
| eval() | 改为安全的替代方案 |

## 5. CI/CD集成

### GitHub Action用法
```yaml
- name: Run PEtFiSh Quality Gate
  run: |
    uv run .opencode/skills/quality-gate/scripts/run_gate.py \
      --path .opencode/skills/ \
      --recursive \
      --json \
      --fail-threshold 0.5
```

### Pre-commit Hook
```bash
#!/bin/bash
changed_skills=$(git diff --cached --name-only | grep '.opencode/skills/.*/SKILL.md' | xargs -I{} dirname {})
for skill_dir in $changed_skills; do
  uv run .opencode/skills/quality-gate/scripts/run_gate.py --path "$skill_dir"
  if [ $? -ne 0 ]; then
    echo "Quality gate FAILED for $skill_dir"
    exit 1
  fi
done
```
