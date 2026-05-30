# skill-author V2优化方案

## 1. 背景与问题判断

`skill-author`当前已经能完成基础脚手架工作：生成合法的`SKILL.md`、`references/`、`scripts/`、`assets/`、`evals/`目录，并尝试约束名称、description和基础workflow。但从胖瘦写作法的产出来看，它的问题不是“不合规”，而是“只能写出合规骨架，不能稳定写出高质量skill”。

胖瘦写作法暴露出的典型问题包括：

1. 核心方法成立，但工程化不足。
2. 有主流程，但缺少执行模式。
3. 有触发描述，但边界不够精细。
4. 有参考文件，但没有真正形成可复用模板和评测闭环。
5. 有eval目录意识，但没有生成可用eval样例与断言。
6. 没有主动考虑与其它writing/research/style skills的边界和handoff。

因此，`skill-author`应从“脚手架生成器”升级为“skill产品经理+架构师+质检员”。

---

## 2. V2目标

### 2.1 定位升级

当前定位：

> Turn a user's idea into an installable valid skill directory.

建议升级为：

> Turn a user's intent, examples, domain rules, and expected outcomes into a production-grade skill package with precise activation, reusable workflow, progressive disclosure, templates, evals, and quality gates.

也就是说，V2不只负责“生成文件”，还要负责：

- 明确skill真正解决的问题。
- 抽取用户的专有经验。
- 识别agent缺失的知识。
- 设计触发条件与非触发边界。
- 规划主skill与references/assets/scripts/evals的分工。
- 生成可测试、可迭代、可维护的skill包。
- 联动lint、trigger evaluator、description optimizer、quality gate。

### 2.2 输出质量目标

一个合格的V2产物至少满足：

1. `SKILL.md`合规。
2. `description`包含what、when、边界、典型触发场景。
3. 主体内容不是泛泛建议，而是可执行流程。
4. 至少包含一个“判断/分流/模式选择”机制。
5. 至少包含一个输出模板。
6. 至少包含3-5个eval用例，其中包括should-trigger和should-not-trigger。
7. 有质量检查清单。
8. 明确与相邻skills的handoff边界。
9. 对不确定信息有`[assumption]`或`[needs-user-input]`标记。
10. 最终交付时包含创建文件清单和验证结果。

---

## 3. 当前skill-author的关键缺陷

### 3.1 Intake过窄

当前只问三个问题：

1. What does the skill do?
2. What user requests or trigger phrases should activate it?
3. What tools does it need?

这对于简单工具skill足够，但对写作、研究、课程、项目初始化、安全审计等复杂skill远远不够。

V2应改为分层intake：

```markdown
## Intake Ladder

### Minimum Intake
- skill目标：它解决什么问题？
- 用户触发：什么请求应该激活它？
- 交付物：它最终应该产出什么？

### Quality Intake
- 领域规则：agent不知道但必须遵守的规则是什么？
- 成功样例：有没有一份理想输出或已有优秀案例？
- 失败样例：过去agent哪里做错过？
- 相邻skill：哪些任务不归它管？
- 自动化程度：需要交互确认，还是允许自动推进？
- 证据要求：是否需要引用、文件依据、命令输出或日志？

### Production Intake
- 是否需要脚本？
- 是否需要模板？
- 是否需要eval？
- 是否需要安全边界？
- 是否需要与pack-manifest或远程安装机制集成？
```

### 3.2 skill类型过粗

当前只有：

- automation
- workflow
- knowledge

建议扩展为：

- `automation`：脚本/命令驱动。
- `workflow`：多阶段流程。
- `knowledge`：领域规则/知识。
- `writing`：写作、编辑、风格、结构治理。
- `review`：审查、评分、质检、反思。
- `research`：资料收集、摘录、引用、综合分析。
- `project`：项目初始化、仓库治理、任务规划。
- `hybrid`：需要多个类型组合。

也可以不改变脚本枚举，而是在`SKILL.md`中引入`capability profile`：

```yaml
metadata:
  skill_type: workflow
  capability_profile: writing,research,review
```

### 3.3 生成内容过泛

当前模板生成的Role、Workflow、Output都比较通用，容易出现“看起来像skill，但没有专用能力”的问题。

V2应强制生成以下几类专用内容：

```markdown
## Domain Rules
写入agent如果不知道就会做错的领域规则。

## Decision Points
写入流程中必须做判断的节点。

## Execution Modes
定义interactive/auto/review-only等模式，避免机械地反复问用户。

## Output Contracts
定义每种模式下必须交付的文件、字段或章节。

## Anti-patterns
列出典型失败方式。

## Handoff
说明什么时候交给其它skill。
```

### 3.4 evals为空

当前`generate_skill.py`会创建`evals/evals.json`，但内容是空数组。这会让“有eval结构”变成“没有eval能力”。

V2应要求至少生成：

- 3个should-trigger prompts。
- 2个should-not-trigger prompts。
- 每个prompt至少2条assertions。
- 至少1个边界场景。
- 如果是写作/研究类skill，应增加输出质量断言。

示例：

```json
{
  "skill_name": "fat-slim-writer",
  "evals": [
    {
      "id": "trigger-longform-outline",
      "prompt": "我有一个提纲，帮我写一篇长文，先扩展素材再收敛成稿。",
      "should_trigger": true,
      "expected_output": "Uses Fat then Slim workflow with draft and revision summary.",
      "assertions": [
        "Output includes a Fat phase or material expansion stage.",
        "Output includes a Slim phase or reduction/editing stage.",
        "Final draft does not contain unresolved placeholders."
      ]
    },
    {
      "id": "no-trigger-short-polish",
      "prompt": "帮我润色这句话。",
      "should_trigger": false,
      "expected_output": "Does not activate fat-slim long-form workflow.",
      "assertions": [
        "Response should not require outline expansion.",
        "Response should not create chapter-level files."
      ]
    }
  ]
}
```

### 3.5 缺少相邻skill边界

胖瘦写作法这类skill很容易和以下skills重叠：

- markdown writer
- personal writing style
- series style governor
- research note
- citation manager
- document reviewer

V2必须强制生成`Handoff & Boundaries`章节：

```markdown
## Handoff & Boundaries

This skill owns:
- 内容生产流程
- 阶段性扩写与删减
- 长文结构推进

This skill does not own:
- 系列文章风格统一 → handoff to series-style-governor
- 个人文风拟合 → handoff to personal-writing-style
- 文献摘录和引用管理 → handoff to research-note/citation-manager
- Markdown格式治理 → handoff to markdown-writer
```

### 3.6 缺少质量门禁

当前`skill-author`只说“run skill-lint if available”，但没有真正定义“写完以后怎么自检”。

V2应在每个skill交付前执行手工质量门禁：

```markdown
## Authoring Quality Gate

- [ ] name合法并与目录一致
- [ ] description小于1024字符
- [ ] description包含what/when/near-miss boundary
- [ ] SKILL.md小于500行
- [ ] 有明确Activation
- [ ] 有Execution Modes或Decision Points
- [ ] 有Output Contract
- [ ] 有Must Do/Must Not Do
- [ ] references不重复SKILL.md
- [ ] assets中至少有必要模板
- [ ] evals至少包含3个正例、2个反例
- [ ] 明确handoff边界
- [ ] 如果使用脚本，脚本有--help、错误处理、相对路径
```

---

## 4. V2建议目录结构

```text
skill-author/
├── SKILL.md
├── references/
│   ├── skill-spec.md
│   ├── authoring-methodology.md
│   ├── skill-type-taxonomy.md
│   ├── description-design.md
│   ├── eval-design.md
│   ├── handoff-boundary-design.md
│   └── quality-gate.md
├── assets/
│   ├── skill-md-template.md
│   ├── evals-template.json
│   ├── reference-template.md
│   ├── writing-skill-template.md
│   ├── workflow-skill-template.md
│   └── review-skill-template.md
├── scripts/
│   ├── generate_skill.py
│   └── validate_generated_skill.py
└── evals/
    ├── evals.json
    └── files/
        ├── simple-skill-request.md
        ├── writing-skill-request.md
        └── flawed-skill-example.md
```

---

## 5. SKILL.md V2主体建议

### 5.1 Role

```markdown
## Role

You are a production-grade skill author. Your job is not only to scaffold a valid skill, but to turn user intent, examples, domain rules, and prior failures into a reusable, testable, and maintainable skill package.

You must optimize for:
- precise activation
- clear boundaries
- executable workflow
- progressive disclosure
- concrete output contracts
- eval-driven improvement
- compatibility with the surrounding skill ecosystem
```

### 5.2 Activation

```markdown
## Activation

Use this skill when the user asks to:
- create, write, design, improve, refactor, package, or evaluate an Agent Skill/OpenCode skill/Claude skill
- turn a workflow, methodology, style guide, checklist, or repeated task into a skill
- improve a weak skill generated by another agent
- add evals, templates, references, scripts, or quality gates to an existing skill

Do not use this skill for:
- ordinary writing tasks where the user wants the final article rather than a reusable skill
- simple code generation unrelated to skill packaging
- running an existing skill without modifying or authoring it
```

### 5.3 Workflow

```markdown
## Workflow

1. Determine authoring mode:
   - new-skill
   - improve-existing-skill
   - extract-from-workflow
   - package-skill-pack
   - add-evals
   - refactor-boundaries

2. Collect minimum intake.
   If user input is incomplete, make the smallest safe assumption and mark it.

3. Extract domain-specific knowledge:
   - rules
   - examples
   - anti-patterns
   - user corrections
   - output expectations
   - edge cases

4. Design activation:
   - should-trigger prompts
   - should-not-trigger prompts
   - near-miss boundaries

5. Design skill structure:
   - SKILL.md core instructions
   - references for detailed rules
   - assets for reusable templates
   - scripts only when they reduce repeated fragile work
   - evals for trigger and output quality

6. Generate files.

7. Run validation:
   - name/frontmatter check
   - description check
   - structure check
   - reference duplication check
   - eval completeness check
   - script interface check

8. Return delivery summary:
   - files created/changed
   - assumptions
   - validation result
   - recommended next iteration
```

---

## 6. generate_skill.py优化方向

### 6.1 增加参数

建议新增：

```bash
--mode new-skill|improve-existing|add-evals|refactor
--profile automation|workflow|knowledge|writing|review|research|project|hybrid
--trigger "..."
--non-trigger "..."
--output-contract "..."
--handoff "..."
--with-assets
--with-evals
--with-quality-gate
--pack-root
```

### 6.2 eval不再为空

当前脚本生成：

```json
{
  "skill_name": "xxx",
  "version": "0.1.0",
  "evals": []
}
```

建议改为生成最小可用eval：

```json
{
  "skill_name": "xxx",
  "version": "0.1.0",
  "evals": [
    {
      "id": "trigger-primary-task",
      "prompt": "User asks for the primary task this skill is designed for.",
      "should_trigger": true,
      "expected_output": "The skill follows its defined workflow and returns the expected output contract.",
      "assertions": [
        "The response follows the workflow stages defined in SKILL.md.",
        "The response includes the required output sections."
      ]
    },
    {
      "id": "no-trigger-adjacent-task",
      "prompt": "User asks for an adjacent task that belongs to another skill.",
      "should_trigger": false,
      "expected_output": "The skill should not take over the adjacent task.",
      "assertions": [
        "The response does not follow this skill's main workflow.",
        "The response suggests the correct adjacent workflow if appropriate."
      ]
    }
  ]
}
```

### 6.3 自动生成handoff文件

新增：

```text
references/handoff-boundaries.md
```

内容包括：

```markdown
# Handoff Boundaries

## This skill owns

## This skill does not own

## Adjacent skills

## Escalation / composition rules
```

### 6.4 自动生成quality-gate文件

新增：

```text
references/quality-gate.md
```

用于每次修改后自检。

---

## 7. 与toolchain其它skills联动

`petfish-toolchain-skill`中已经包含：

- skill-author
- skill-lint
- repo-skill-miner
- skill-security-auditor
- quality-gate
- skill-description-optimizer
- skill-trigger-evaluator
- skill-usage-tracker
- skill-publish

V2的`skill-author`应该主动调用或提示调用这些能力，而不是孤立产出。

建议在`SKILL.md`增加：

```markdown
## Toolchain Handoff

After authoring:
1. Use `skill-lint` to check structural validity.
2. Use `skill-description-optimizer` if activation is broad or vague.
3. Use `skill-trigger-evaluator` when eval prompts are available.
4. Use `quality-gate` before publishing.
5. Use `skill-security-auditor` if scripts, shell commands, network access, credentials, or file mutation are involved.
6. Use `skill-publish` only after validation passes.
```

---

## 8. 胖瘦写作法案例对应的修复要求

用胖瘦写作法作为回归测试，V2生成的skill应比当前版本多出：

1. Execution Modes：interactive/auto/review-only。
2. Writing Contract：文档类型、读者、目标、篇幅、证据要求。
3. Material Ledger：素材账本。
4. Slim Action Taxonomy：DELETE/COMPRESS/MERGE/MOVE/REWRITE。
5. Handoff：series-style-governor、personal-writing-style、research-note、markdown-writer。
6. Evals：至少3个触发样例、2个非触发样例。
7. Assets：fat draft template、slim review template、source ledger template。
8. Quality Gate：最终稿不得残留`[待查]`、`[素材]`等占位符。

---

## 9. 实施路线

### Phase 1：改SKILL.md

目标：不动脚本，先提升agent作者行为。

改动：

- 扩展Role。
- 增加Authoring Modes。
- 增加Intake Ladder。
- 增加Domain Extraction。
- 增加Activation Design。
- 增加Handoff & Boundaries。
- 增加Authoring Quality Gate。
- 增加Toolchain Handoff。

### Phase 2：补references和assets

目标：让skill-author有可复用知识和模板。

新增：

- `references/authoring-methodology.md`
- `references/skill-type-taxonomy.md`
- `references/description-design.md`
- `references/eval-design.md`
- `references/handoff-boundary-design.md`
- `references/quality-gate.md`
- `assets/skill-md-template.md`
- `assets/evals-template.json`
- `assets/writing-skill-template.md`

### Phase 3：改generate_skill.py

目标：让脚本不再生成空泛骨架。

改动：

- 支持profile。
- 支持mode。
- 支持非触发边界。
- 生成最小可用evals。
- 生成handoff和quality-gate文件。
- 输出JSON包含validation warnings。

### Phase 4：建立回归eval

目标：避免V2继续产出胖瘦写作法这种“理念成立但工程化不足”的skill。

新增eval场景：

1. 生成一个写作skill。
2. 改进一个已有弱skill。
3. 从用户方法论抽取skill。
4. 给skill增加evals。
5. 判断某需求不应写成skill。

---

## 10. 推荐的最小可行改造

如果只做一次小步快跑，建议先做这四件事：

1. 修改`SKILL.md`，加入Authoring Modes、Intake Ladder、Quality Gate。
2. 新增`references/quality-gate.md`。
3. 新增`assets/evals-template.json`。
4. 修改`generate_skill.py`，让`evals/evals.json`不再是空数组。

这样就能明显改善下一次生成skill的质量。
