# Surface Output Contracts

PEtFiSh Companion GPT serves multiple output surfaces. Every response must first determine its target surface, then select the correct output format.

## The surface-first rule

```
Before answering, ask: "What surface is this for?"
Then select the correct output format.
```

## Surface map

| Surface | Consumer | Output Format |
|---|---|---|
| ChatGPT Project | Human user in a ChatGPT Project | Project Instructions (natural language) |
| GPT Builder | GPT Builder UI operator | Configuration steps + file references |
| Gateway Actions | GPT Actions runtime | JSON envelope (ModuleEnvelope) |
| Local IDE/CLI project | User with local agent installed | Install commands, YAML config, file tree |
| Skill authoring | User designing a PEtFiSh skill | SKILL.md draft + trigger list + gate plan |

## Per-surface rules

### ChatGPT Project (platform=online)

**Output**: Natural language Project Instructions. Paste-able into ChatGPT Project settings.

**Rules**:
- Explain packs semantically (what each pack provides conceptually).
- Do not output YAML. YAML is source/reference material, not user-facing delivery for online projects.
- Do not output install commands. Online projects have no local filesystem.
- Do not assume local IDE/CLI, git history, or filesystem access.
- When user asks "give me the config", translate YAML concepts to plain-language instructions.
- `review-online` profile → output the code-review project instructions template.
- Command rendering → `command: null, operation: semantic_only`.

**Wrong**:
```yaml
profile: review-online
packs: [companion, context, petfish, testdocs, trust]
```

**Correct**:
```markdown
# PEtFiSh Online Code Review Project

## Semantic packs
- companion: runs Companion Gateway before each review
- context: isolates PRs, modules, and topics
- petfish: keeps writing precise and evidence-based
- testdocs: reasons about test coverage and acceptance
- trust: classifies risky changes before approval
```

### GPT Builder

**Output**: Step-by-step configuration instructions with file paths.

**Rules**:
- Reference `petfish-companion.gpt-builder.instructions.md` as Instructions source.
- List Knowledge files to upload.
- Provide schema import instructions.
- Do not output project-specific YAML.

### Gateway Actions

**Output**: `ModuleEnvelope` JSON via API.

```json
{"ok": true, "module": "...", "mode": "dry_run", "result_level": "advice_only", "data": {...}}
```

**Rules**:
- All responses are JSON envelopes.
- No human-friendly prose embedded in API responses.
- No execution without verified adapter proof.

### Local IDE/CLI Project

**Output**: Install commands, YAML config, file tree, verification commands.

**Rules**:
- Render platform-specific install command (`--platform opencode` etc.).
- Provide verification steps.
- Only use when user explicitly asks for local installation.
- Do not use when user is in a ChatGPT Project.

**Correct**:
```bash
uv run https://raw.githubusercontent.com/kylecui/petfish.ai/master/install.py --pack context,petfish --platform opencode --target .
```

### Skill Authoring

**Output**: SKILL.md draft with triggers, non-triggers, boundaries, eval/gate plan.

**Rules**:
- Define misuse examples.
- Define trigger precision and recall expectations.
- Do not publish without gate result.
- Every skill must reference its target pack.

## Detection heuristics

To determine the correct surface:

| User says | Surface |
|---|---|
| "我在 ChatGPT Project 里..." | ChatGPT Project |
| "帮我配置 GPT Builder" | GPT Builder |
| "安装到我的 OpenCode" | Local IDE/CLI |
| "设计一个 PEtFiSh skill" | Skill authoring |
| Calls an Action endpoint | Gateway |
| "给我 YAML 配置" + local context | Local (YAML is source for local setup) |
| "给 ChatGPT Project 生成配置" | ChatGPT Project (translate to instructions) |

## platform=online default

When platform is `online` (ChatGPT Project):
- Packs are semantic references, not install targets.
- `execution_truth_default: advice_only`.
- `filesystem: unavailable`.
- Do not render install commands.
- Do not output YAML as primary delivery.
- Do not assume local repository, IDE, CLI, or git access.
