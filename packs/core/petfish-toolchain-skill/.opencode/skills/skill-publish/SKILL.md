---
name: skill-publish
description: >
  Publish validated skill packs to PEtFiSh Market. Generates registry JSON
  entries from pack-manifest.json for optional packs. Trigger on 'publish
  skill', 'publish pack', 'release to market', '发布到市场'. Runs after
  quality-gate PASS. Outputs registry JSON files ready for commit to
  petfish-market. Supports --generate-index to regenerate index.json and
  --push to auto-commit and push to petfish-market via gh CLI.
metadata:
  author: petfish-team
  version: 0.2.0
  short-description: Bridge quality-gate PASS → marketplace registry JSON, index, and git push
---

# Skill Publish — 发布到市场

> quality-gate通过之后，skill-publish是将pack真正推送到市场的最后一步。

## 1. 角色定位

你是胖鱼的**市场发布桥接器**。你的职责是把一个已通过quality-gate的optional pack，转化为petfish-market注册表所需的JSON条目，并可选地自动更新index.json、提交并推送到petfish-market。

你不做skill的创建、修改或质量评审——你只做**格式转换、聚合和输出**。

## 2. 激活条件

以下情况触发本skill：

- 用户说"publish skill"、"publish pack"、"release to market"、"发布到市场"
- 用户说"generate registry entry"、"market publish"、"注册到市场"
- 用户说"regenerate index.json"、"update market index"
- quality-gate返回PASS，且用户随后要求发布
- 用户说"/petfish publish"或"/petfish gate"完成后要求下一步

## 2.5 发布前验证（强制，#249教训）

发布前**必须**验证以下条件，任一失败则阻止发布：

1. **git tag存在**：`--ref`指定的tag必须在目标仓库中实际存在
   ```bash
   gh api repos/kylecui/petfish.ai/git/refs/tags/<ref> --silent
   ```
   如果404 → 提示用户先创建tag：`git tag <ref> && git push origin <ref>`

2. **pack-manifest.json完整**：包含 `skills` 数组和 `contents` 列表（installer依赖这些字段复制文件）

3. **目录结构正确**：skill文件必须在 `.opencode/skills/<name>/` 下（不是直接放在pack根目录）
   - ✅ 正确：`packs/optional/<pack>/.opencode/skills/<skill>/SKILL.md`
   - ❌ 错误：`packs/optional/<pack>/SKILL.md`（installer找不到）

4. **不手动编辑registry JSON**：所有registry条目必须通过 `publish_pack.py` 生成，不得手写
   - 手写条目容易遗漏字段、猜错ref、用错path — 这是#249的根本原因

## 3. 工作流程

### 3.1 完整流程

```
用户请求发布 pack-name
  │
  ├─① 验证pack位于 packs/optional/（拒绝core packs）
  │
  ├─② 读取 pack-manifest.json
  │
  ├─③ （可选）确认已通过quality-gate
  │
  ├─④ 生成registry JSON条目（petfish-market schema）
  │
  ├─⑤ 验证JSON结构
  │
  ├─⑥ 写入 <output-dir>/<pack-name>.json
  │   （默认：../petfish-market/registry/official/）
  │
  ├─⑦ [--generate-index] 从 registry/official/*.json 重新生成 index.json
  │
  └─⑧ [--push] git add + git commit + git push origin main
      （需要先运行 gh auth login）
```

### 3.2 执行命令

```bash
# 发布单个pack（需指定--ref）
uv run packs/core/petfish-toolchain-skill/.opencode/skills/skill-publish/scripts/publish_pack.py \
  --pack research-skill-pack --ref v1.4.0

# 发布所有optional packs
uv run packs/core/petfish-toolchain-skill/.opencode/skills/skill-publish/scripts/publish_pack.py \
  --all --ref v1.4.0

# 预览输出（不写文件）
uv run packs/core/petfish-toolchain-skill/.opencode/skills/skill-publish/scripts/publish_pack.py \
  --pack research-skill-pack --dry-run

# 指定输出目录
uv run packs/core/petfish-toolchain-skill/.opencode/skills/skill-publish/scripts/publish_pack.py \
  --pack research-skill-pack --ref v1.4.0 --output ./registry/official/

# 发布 + 重新生成 index.json
uv run packs/core/petfish-toolchain-skill/.opencode/skills/skill-publish/scripts/publish_pack.py \
  --all --ref v1.4.0 --generate-index

# 发布 + 重新生成 index.json + 自动提交并推送到 petfish-market
uv run packs/core/petfish-toolchain-skill/.opencode/skills/skill-publish/scripts/publish_pack.py \
  --all --ref v1.4.0 --generate-index --push

# 预览完整流程（不写文件、不推送）
uv run packs/core/petfish-toolchain-skill/.opencode/skills/skill-publish/scripts/publish_pack.py \
  --all --ref v1.4.0 --generate-index --push --dry-run
```

## 4. 新增参数

### `--generate-index`

写入registry JSON文件后，从 `registry/official/` 下所有 `*.json` 文件重新生成 `index.json`。

- 聚合格式：`{version: 2, generated_at, skill_count: 0, pack_count, skills: [], packs: [...]}`
- packs按name字母顺序排列
- 保留现有 `index.json` 中的 `skills[]` 条目（不覆盖）
- 写入 market repo根目录（`output_dir` 的上两级）
- 与 `--dry-run` 兼容：dry-run时输出到stdout，不写文件

### `--push`

写入registry文件（以及可选的index.json）后，通过git + gh CLI自动提交并推送到petfish-market。

**前置条件：**
```bash
gh auth login   # 必须先完成认证
```

执行步骤：
1. `gh auth status` — 检查认证状态，未认证时快速失败并给出清晰提示
2. `git add registry/official/ index.json` — 暂存变更
3. `git commit -m "publish: <pack-names>"` — 提交
4. `git push origin main` — 推送到远端

与 `--dry-run` 兼容：dry-run时打印git命令到stderr，不实际执行。

## 5. 输出格式

每个pack生成一个JSON文件，路径为 `<output-dir>/<pack-name>.json`：

```json
{
  "namespace": "official",
  "name": "pack-directory-name",
  "alias": ["short-alias"],
  "description": "Bilingual description / English description",
  "version": "X.Y.Z",
  "repo": "kylecui/petfish.ai",
  "ref": "vX.Y.Z",
  "path": "packs/optional/<pack-name>",
  "skill_count": 0,
  "command_count": 0,
  "agent_count": 0,
  "license": "Apache-2.0",
  "author": "petfish-team",
  "platforms": ["opencode"],
  "gate_result": {}
}
```

`index.json` 格式：

```json
{
  "version": 2,
  "generated_at": "2026-05-29T10:00:00Z",
  "skill_count": 0,
  "pack_count": 9,
  "skills": [],
  "packs": [...]
}
```

字段说明：
- `name`：pack目录名（即 packs/optional/ 下的目录名）
- `alias`：来自PACK_ALIASES映射 + pack-manifest.json中的legacy_names
- `description`：直接从pack-manifest.json读取
- `version`：从pack-manifest.json读取
- `ref`：通过--ref参数传入的git tag
- `path`：相对仓库根目录的pack路径
- `gate_result`：空对象（由CI在gate通过时填充，不覆盖已有内容）

## 6. 行为边界

### 必须做：
- 只处理 packs/optional/ 下的pack
- 拒绝发布时给出明确错误信息（stderr）
- --dry-run时输出到stdout，不写文件
- 输出目录不存在时自动创建
- 不覆盖已有的gate_result字段（保留CI填充的结果）
- 所有错误信息输出到stderr，不混入stdout
- --push前检查gh auth状态，未认证时给出明确提示

### 不得做：
- 发布 packs/core/ 下的任何pack
- 修改pack-manifest.json或SKILL.md
- 在没有--ref的情况下（非dry-run）写文件
- 安装任何外部Python依赖（脚本为纯stdlib）
- 未指定--push时执行任何git push操作
- 向stdout输出非JSON内容（干扰管道）
