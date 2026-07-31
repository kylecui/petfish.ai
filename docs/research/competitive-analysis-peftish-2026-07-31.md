# Competitive Analysis: New-Generation AI Companions & Skill Ecosystems for PEtFiSh

**Date:** 2026-07-31  
**Scope:** WorkBuddy, Cursor / Windsurf (Devin Desktop) / Cline / Aider, Anthropic Agent Skills, Smithery / Glama MCP marketplaces, SkillKit, and 2025-2026 agentic-companion patterns.  
**Goal:** Identify architectural patterns and UX innovations that PEtFiSh can adopt for proactive assistance, skill discovery, context management, and companion behavior.

---

## 1. WorkBuddy (Tencent Cloud / CodeBuddy)

### What it is
WorkBuddy is Tencent Cloud's AI Agent office companion. It launched in China on March 9, 2026, released an international version on May 28, 2026, and shipped an enterprise edition on June 5, 2026. It is positioned as a "one-person command, multi-expert execution" workbench for non-technical and business users.

### Key features
- **One-sentence task → end-to-end delivery:** The user gives a natural-language instruction, and WorkBuddy autonomously plans, researches, and produces a finished artifact (report, PPT, data analysis, web app, image design).
- **100+ domain experts:** Pre-built "experts" cover operations, design, data, finance, legal, development, etc. They can work in parallel as a "virtual team."
- **Multi-Agent parallel execution:** Multiple agents run concurrently and assemble a final deliverable.
- **Skills + MCP ecosystem:** WorkBuddy supports custom Skills and MCP connectors for GitHub, GitLab, Jira, Confluence, Google Drive, Gmail, Notion, Slack, etc.
- **Remote / IM control:** Users can start tasks from mobile via WeChat, Slack, Telegram, or Discord; the agent runs on the desktop and returns results through the same channel.
- **Scheduled automation:** Auto-tasks and personal assistants run recurring workflows.
- **Cross-platform:** Desktop client, main IM apps, and a mini-program version.
- **Enterprise compliance:** Private deployment, multi-member management, role-based access, and full-chain operation auditing.

### What makes it "new generation"
WorkBuddy is not a chatbot or autocomplete; it is a **task-completion agent** embedded in the user's existing communication stack. Its architecture mixes:
1. **Multi-agent orchestration** for complex workflows.
2. **Pre-built domain experts** that lower the barrier for non-coders.
3. **Skills/MCP extensibility** so it can operate inside enterprise tools.
4. **Compliance-first enterprise packaging** (private deployment, audit logs).

### Sources
- WorkBuddy product site: https://www.workbuddy.cn/ and https://www.codebuddy.cn/work/
- International launch / Skills + MCP details: https://www.aixq.cc/35268.html
- Enterprise edition (private deployment, audit, multi-member): https://www.ai-indeed.com/encyclopedia/22710.html

---

## 2. AI Coding Assistants

### 2.1 Cursor

Cursor is now primarily an **AI coding agent** rather than a smarter autocomplete. Its design is built around an "agent harness" of instructions, tools, and model-specific tuning.

Key architectural/UX patterns:
- **Plan Mode (Shift+Tab):** The agent researches the codebase, asks clarifying questions, and writes a reviewable Markdown plan *before* editing. Plans are saved to `.cursor/plans/`.
- **Rules vs. Skills:**
  - **Rules** (`.cursor/rules/`) are static, always-on context (commands, style, workflow pointers).
  - **Skills** (`.cursor/skills/` or `.agents/skills/`) are dynamic, loaded only when relevant. Skills can contain `SKILL.md`, `scripts/`, `references/`, and `assets/`, and are triggered by YAML frontmatter `name`/`description`.
- **Context on demand:** Cursor's agent uses `grep` and semantic search, `@Branch`, and `@Past Chats` to pull context without the user manually tagging every file.
- **Long-running loops:** Skills can define hooks (e.g., `stop` hooks) that keep the agent iterating until tests pass or a `scratchpad.md` signals completion.
- **Built-in slash commands:** `/create-rule`, `/create-skill`, `/migrate-to-skills`, `/review`, `/babysit`, `/automate`, etc.
- **Marketplace:** MCP servers and integrations (Slack, Sentry, Figma, Datadog) are discoverable via the Cursor Marketplace.
- **Cloud agents:** Background agents run in remote sandboxes, open PRs, and can be triggered from Slack or mobile.
- **Bugbot:** Automated AI code review on pull requests.

### Source
- Cursor agent best-practices: https://cursor.com/blog/agent-best-practices
- Cursor Agent Skills docs: https://cursor.com/docs/context/skills

### 2.2 Windsurf → Devin Desktop (Cognition)

Windsurf was rebranded as **Devin Desktop** in June 2026. The product is being repositioned as an **Agent Command Center** where developers manage fleets of local and cloud agents.

Key patterns:
- **Agent Command Center:** A Kanban-style board for sessions, statuses, PRs, and agents.
- **Spaces:** Shared context and Git worktrees across multiple agents.
- **Devin Local:** The successor to the Cascade agent, with up to 30% better token efficiency, subagent support, and sandboxing.
- **Agent Client Protocol (ACP):** Lets multiple agents and models interoperate in the same workspace.
- **Fast Context:** Finds the exact files and lines an agent needs in milliseconds.
- **Supercomplete:** Predicts the developer's next thought, not just the next edit.
- **Cloud handoff:** Local work can be escalated to Devin Cloud agents with a single click.
- **Extensive integrations:** MCP servers and language-server extensions for Notion, Linear, Stripe, Datadog, Sentry, Vercel, Figma, etc.

### Source
- Devin Desktop / Windsurf site: https://windsurf.com/
- Devin Desktop FAQ (transition details, Spaces, Devin Local, rule paths): https://docs.devin.ai/desktop/devin-desktop-faq

### 2.3 Cline

Cline is an **open-source coding agent** (VS Code extension, CLI, SDK) that emphasizes portability and no vendor lock-in.

Key patterns:
- **Plan, then Act:** Toggle between plan and act modes; approve each step or enable auto-approve.
- **`.clinerules`:** Repo-specific rules that teach the agent standards, architecture, and deployment conventions.
- **MCP + plugins:** Custom tools and lifecycle hooks via SDK; plug in MCP servers for infrastructure.
- **Multi-agent teams and schedules:** Coordinator agents delegate to specialists; cron-based recurring automations.
- **Cross-channel:** Slack, Discord, Telegram, Linear, GitHub Actions, GitLab CI integration.
- **MCP Marketplace:** A dedicated marketplace for MCP servers.
- **Model agnostic:** Claude, GPT, Gemini, local Ollama/LM Studio, any OpenAI-compatible endpoint.

### Source
- Cline official site: https://cline.bot/

### 2.4 Aider

Aider is an open-source terminal-native pair-programming tool. It is more **reactive** than the others but still shows useful design patterns.

Key patterns:
- **Codebase map:** Builds a map of the entire repo to work better in larger projects.
- **Git-first workflow:** Automatically commits changes with sensible messages; easy diff/revert with familiar git tools.
- **Lint and test integration:** Runs linters/tests after edits and fixes failures.
- **Multi-modal context:** Images, web pages, voice input.
- **Model agnostic:** Claude, DeepSeek, OpenAI, local models.

### Source
- Aider official site: https://aider.chat/

---

## 3. Anthropic / Claude Agent Skills

### What it is
Anthropic's **Agent Skills** are an open standard for extending AI agents with specialized capabilities. A skill is a folder containing a `SKILL.md` file with YAML frontmatter, optional scripts, references, and assets.

### Key design patterns
- **Progressive disclosure (three levels):**
  1. **Metadata:** `name` and `description` from YAML frontmatter are always loaded in the system prompt (~100 tokens per skill). This is the trigger surface.
  2. **Instructions:** The `SKILL.md` body is read only when the skill is triggered (<5k tokens).
  3. **Resources/code:** Bundled files and scripts are loaded or executed only as needed. Scripts run via bash and only their output enters context.
- **Auto-triggering vs. manual invocation:** By default the agent matches skills by description. `disable-model-invocation: true` turns a skill into a manual `/skill-name` command.
- **Path scoping:** `paths` globs limit automatic loading to matching files, keeping unrelated guidance out of context.
- **Multiple storage scopes:** `~/.claude/skills/` (personal), `.claude/skills/` (project), enterprise managed settings, and plugins.
- **Security controls:** `allowed-tools` / `disallowed-tools`, trusted-source warnings, and audit of bundled scripts/resources.
- **Cross-platform open standard:** `agentskills.io` documents the format and lists adopters including Cursor, Claude Code, OpenCode, Goose, Gemini CLI, OpenAI Codex, GitHub Copilot, VS Code, and many others.
- **Distribution:** GitHub repo (`anthropics/skills`), Claude Code plugin marketplace (`/plugin marketplace add anthropics/skills`), Claude API `/v1/skills`, claude.ai settings, and enterprise managed deployment.

### Source
- Anthropic Skills announcement: https://www.anthropic.com/news/skills
- Engineering deep-dive: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Reference repo: https://github.com/anthropics/skills
- Agent Skills open standard: https://agentskills.io/
- Claude Code skills docs: https://code.claude.com/docs/en/skills
- API docs: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

---

## 4. MCP Marketplaces

### 4.1 Smithery
- **Registry + runtime integration:** Connects agents to thousands of tools and services.
- **Auth handled:** OAuth, credentials, and sessions are managed automatically via `agent.pw`.
- **CLI:** `npx smithery auth login`, `npx smithery mcp add <server>`, `npx smithery tool list`, `npx smithery tool call`.
- **Verified badge:** Servers can carry a verified badge and usage counts.
- **Publish once, run anywhere:** MCP server authors publish to Smithery and get install paths for multiple clients.
- **Skills marketplace:** Smithery also lists Skills, not just MCP servers.

### Source
- Smithery: https://smithery.ai/

### 4.2 Glama
- **Superset of the official MCP Registry:** 65,000+ servers, 10,000+ hosted connectors, 450,000+ tools (as of July 2026).
- **Tool-level search:** Search by *capability* (e.g., "query Postgres," "send email") rather than by server name.
- **In-browser MCP Inspector:** Test any server in an ephemeral sandbox without installing; share debug sessions as URLs.
- **Glama Gateway:** Hosted proxy with logging, per-tool access control, managed OAuth, and usage analytics.
- **Quality & safety scoring:** Scans tools, schemas, licenses, and security; annotates hints such as `readOnlyHint`, `destructiveHint`, `idempotentHint`.
- **One-click hosting:** Authors can run servers on Glama infrastructure.

### Source
- Glama: https://glama.ai/

---

## 5. SkillKit

SkillKit is a "universal skills bridge" for AI coding agents. It treats skills as packages that can be written once and translated across 44+ agents.

Key patterns:
- **Cross-agent translation:** `skillkit translate --to cursor,windsurf` converts a skill to another agent's format.
- **`.skills` manifest:** Git-based team skill stack, similar to a `package.json` for agent capabilities.
- **Primer:** Auto-generates agent instructions from the codebase for all supported agents.
- **Skill tree:** 15,000+ skills in a hierarchical taxonomy; AI recommends skills based on the codebase.
- **Security scanner:** Detects prompt injection, secrets, and malicious patterns on install.
- **Testing & CI/CD:** Built-in test framework, GitHub Actions / GitLab CI / pre-commit integration.
- **Runtime APIs:** REST server, MCP server, and Python client for skill discovery.
- **Compatibility matrix:** Publicly scores 16 agents across 10 capability categories (skill translation, hooks, MCP, context window, security, testing, frontend, backend, DevOps, documentation).

### Source
- SkillKit: https://agenstskills.com/

---

## 6. Agentic Companion Patterns (2025-2026)

The research literature distinguishes between **autonomy** (can act without supervision) and **proactivity** (decides when to act without a prompt). A useful framework is the three-level taxonomy from *Agentic Coding Needs Proactivity, Not Just Autonomy* (arXiv 2026):

1. **Reactive:** Agent runs only when the user asks.
2. **Scheduled:** Agent runs on predefined triggers (schedules, webhooks, GitHub events). It may filter, batch, or rank outputs, but does not learn a per-developer interruption policy.
3. **Situation-aware:** Agent continuously monitors context, computes expected utility vs. interruption cost, and chooses among four actions: **notify**, **question**, **draft**, or **stay silent**. It updates its policy from user feedback.

### Key UX/control patterns
- **Plan before act:** Cursor's Plan Mode, Cline's Plan/Act toggle, and Claude's plan recipes all separate "decide what to do" from "do it."
- **Progressive approval:** Auto-approve can be toggled, but risky or long-running actions default to explicit approval.
- **Skill-level permissions:** `allowed-tools` / `disallowed-tools`, `disable-model-invocation`, and `paths` scoping let a skill declare what it is allowed to do.
- **Interruption cost:** The best agents reason about when *not* to interrupt. Silence is an explicit action.
- **Context scoping:** Project vs. personal vs. enterprise skills, nested skills, and path globs keep guidance relevant and compact.
- **Feedback loops:** Skills/rules can be updated when the agent makes a mistake; the insight policy should learn from accept/dismiss/defer signals.
- **Verification before trust:** Marketplaces use verified badges, security scans, in-browser inspectors, and tool-level annotations to reduce hallucinated capability claims.

### Sources
- IBM agentic AI overview (proactive, goal-driven, guardrails): https://www.ibm.com/think/topics/agentic-ai
- ArXiv paper on proactive coding agents: https://arxiv.org/html/2605.06717v1

---

## 7. Design Decisions PEtFiSh Should Consider

### 7.1 Proactive assistance
1. **Move from reactive to insight-driven:** Build an "insight policy" that decides between notify/question/draft/silence based on context and interruption cost, not just explicit prompts.
2. **Plan/Act separation:** Add a reviewable plan step before autonomous execution, especially for multi-file or multi-step tasks.
3. **Auto-approve with per-skill guardrails:** Let users opt into autopilot, but gate it by skill trust level and tool risk.
4. **Background agents:** Allow agents to run scheduled/recurring tasks and return results asynchronously.

### 7.2 Skill/capability discovery
5. **Adopt the Agent Skills open standard (`agentskills.io`):** Use `SKILL.md` with `name`/`description` frontmatter so PEtFiSh skills are portable across Cursor, Claude Code, OpenCode, etc.
6. **Progressive disclosure:** Load only skill metadata at startup; pull full instructions and scripts only when triggered.
7. **Tool-level search:** In the marketplace, search by *what the user wants to do* ("lint Python," "deploy to Vercel") rather than only by pack name.
8. **Skill recommendation engine:** Analyze the current project/repo and suggest skills that match its stack, similar to SkillKit's Primer and recommendations.
9. **Compatibility matrix:** Publish which agents/clients a skill works with, and provide auto-translation where possible.
10. **MCP integration:** Treat MCP servers as first-class capabilities, and provide a gateway for auth, observability, and per-tool access control.

### 7.3 Context management
11. **Project/personal/enterprise skill scopes:** Let skills live at the repo, user, or org level, with enterprise overrides as the highest priority.
12. **Nested skills:** In monorepos, allow package-specific skills that activate only when working in that package.
13. **Path/glob scoping:** Use `paths` frontmatter to keep file-specific guidance out of unrelated conversations.
14. **Context persistence:** Carry memory across sessions (user preferences, project conventions, recent feedback) without dumping everything into the current prompt.
15. **Fast context retrieval:** Index the codebase so agents can find relevant files/lines in milliseconds, rather than relying on the user to tag files.

### 7.4 Companion behavior and trust
16. **Multi-agent / expert-team orchestration:** Like WorkBuddy, offer pre-defined experts that can work in parallel and assemble a deliverable.
17. **Remote/IM control:** Let users start and receive tasks from Slack/Teams/WeChat/Discord, so the companion lives where they already communicate.
18. **Trust scoring:** Combine security scans, provenance, user ratings, and verification badges for skills and MCP servers.
19. **Audit and compliance:** For enterprise use, provide private deployment, role-based access, operation logs, and mandatory human confirmation for high-risk actions.
20. **Avoid hallucinated capabilities:** Require each skill/MCP to declare a deterministic schema, provide an in-browser test environment, and surface `readOnly`/`destructive`/`idempotent` hints before execution.

### 7.5 Platform-specific lessons
- **From Cursor:** Invest in model-specific harness tuning, plan mode, and the Rules/Skills distinction.
- **From Devin Desktop:** Build an Agent Command Center with shared Spaces, worktrees, and cloud/local handoff.
- **From Cline:** Keep the runtime open-source, model-agnostic, and embeddable via CLI/SDK.
- **From Aider:** Keep git as the source of truth; use deterministic lint/test loops to verify changes.
- **From WorkBuddy:** Target non-coders with pre-built experts and end-to-end deliverables; integrate with enterprise IM and compliance.
- **From SkillKit:** Build a `.skills` manifest and cross-agent translation so users don't rewrite skills for every tool.

---

## 8. Confidence & Limitations

- Most product details come from vendor documentation, product pages, and official blogs (2026). Some marketing claims (e.g., "100+ experts") are reported as-stated.
- The academic source on proactivity (arXiv 2605.06717v1) is a research paper, not a product benchmark; it provides a conceptual framework rather than measured comparisons.
- WorkBuddy's enterprise features are described by third-party Chinese tech media and the vendor's own pages; independent audits were not available.
- The report focuses on **architectural patterns and UX decisions**, not pricing or commercial positioning.

---

## 9. Sources

- WorkBuddy: https://www.workbuddy.cn/, https://www.codebuddy.cn/work/
- WorkBuddy international launch / Skills + MCP: https://www.aixq.cc/35268.html
- WorkBuddy enterprise edition: https://www.ai-indeed.com/encyclopedia/22710.html
- Cursor agent best practices: https://cursor.com/blog/agent-best-practices
- Cursor Agent Skills: https://cursor.com/docs/context/skills
- Devin Desktop / Windsurf: https://windsurf.com/
- Devin Desktop FAQ: https://docs.devin.ai/desktop/devin-desktop-faq
- Cline: https://cline.bot/
- Aider: https://aider.chat/
- Anthropic Agent Skills announcement: https://www.anthropic.com/news/skills
- Anthropic Agent Skills engineering blog: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic skills repo: https://github.com/anthropics/skills
- Agent Skills open standard: https://agentskills.io/
- Claude Code skills docs: https://code.claude.com/docs/en/skills
- Claude API skills docs: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- Smithery: https://smithery.ai/
- Glama: https://glama.ai/
- SkillKit: https://agenstskills.com/
- IBM agentic AI overview: https://www.ibm.com/think/topics/agentic-ai
- Proactive coding agents paper: https://arxiv.org/html/2605.06717v1
