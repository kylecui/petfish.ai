# AGENTS.md

## Skill路由（强制）

### 必须遵守的路由规则

1. 用户说"润色"、"说人话"、"用我的语言习惯表达"、"按我的风格写"时，**必须**路由到 `petfish-style-rewriter` skill
2. 用户要求进行"去AI味检测"、"AI味检测"、"检测AI写作"或类似AI写作检测时，**必须**先路由到 `de-ai-detector` skill；检测完成后如需改写，再调用 `petfish-style-rewriter`
3. 用户要求"提炼我的风格"、"提取我的风格"、"风格画像"、"style extraction"、"extract my voice"时，**必须**路由到 `style-extractor` skill
4. 涉及中英文技术写作风格改写时，**必须**使用本skill而非通用写作行为
5. 输出**必须**符合以下标准：结构清晰、问题驱动、简洁语言、证据支撑、无修辞夸张、无网络口号
6. 中英混排术语**必须**紧凑：用`Webhook挂载`而非`Webhook 挂载`

### 冲突解决

- 当用户说"去AI味"且意图不明确时，优先使用 `de-ai-detector` 检测，再视结果调用 `petfish-style-rewriter`
- 当润色意图与评审意图并存时，同时加载 `petfish-style-rewriter` 和 `anti-sycophancy-calibration`
- 当用户请求"帮我改一下"但上下文是代码而非文本时，不启用本skill

## Project Writing Policy

When the user asks to rewrite, polish, humanize, formalize, simplify, or detect AI-like writing, use the appropriate local skill:

- `.opencode/skills/petfish-style-rewriter/SKILL.md` — rewrite and polish
- `.opencode/skills/de-ai-detector/SKILL.md` — AI-writing detection
- `.opencode/skills/style-extractor/SKILL.md` — extract a writing style profile

Default mode is `strict` when the user says:

-用我的语言习惯表达
-按我的风格写
-说人话
-去AI味
-让我们润色一下

## Priority

For writing and rewriting tasks, prefer this skill over generic writing behavior.

## Default Output Expectations

- Clear structure
- Problem-driven analysis
- Concise language
- Evidence-based claims
- No rhetorical exaggeration
- No internet-style slogans
- No unnecessary conclusion
- Chinese-English mixed technical terms must be compact: use `Webhook挂载`, `Git提交`, `API接口`, not `Webhook挂载`, `Git提交`, `API接口`

## Important Distinction

Thinking can be exploratory, but final writing must be structured. The agent should first analyze the problem, then express the result using a clear total-part-total structure.

## Suggested User Prompts

-用我的语言习惯表达：...
-让我们润色一下：...
-说人话：...
-按petfish风格重写：...
-去掉AI味并保持工程化表达：...
