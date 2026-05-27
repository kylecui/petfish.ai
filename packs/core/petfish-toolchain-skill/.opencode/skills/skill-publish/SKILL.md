---
name: skill-publish
description: >
  Publish validated skill packs to PEtFiSh Market. Generates registry JSON
  entries from pack-manifest.json for optional packs. Trigger on 'publish
  skill', 'publish pack', 'release to market', '发布到市场'. Runs after
  quality-gate PASS. Outputs registry JSON files ready for commit to
  petfish-market.
metadata:
  author: petfish-team
  version: 0.1.0
  short-description: Bridge quality-gate PASS → marketplace registry JSON
---

# Skill Publish — 发布到市场

> quality-gate通过之后，skill-publish是将pack真正推送到市场的最后一步。

## 1. 角色定位

你是胖鱼的**市场发布桥接器**。你的职责是把一个已通过quality-gate的optional pack，转化为petfish-market注册表所需的JSON条目。

你不做skill的创建、修改或质量评审——你只做**格式转换和输出**。

## 2. 激活条件

以下情况触发本skill：

- 用户说"publish skill"、"publish pack"、"release to market"、"发布到市场"
- 用户说"generate registry entry"、"market publish"、"注册到市场"
- quality-gate返回PASS，且用户随后要求发布
- 用户说"/petfish publish"或"/petfish gate"完成后要求下一步

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
  └─⑥ 写入 <output-dir>/<pack-name>.json
      （默认：../petfish-market/registry/official/）
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
```

## 4. 输出格式

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

字段说明：
- `name`：pack目录名（即 packs/optional/ 下的目录名）
- `alias`：来自PACK_ALIASES映射 + pack-manifest.json中的legacy_names
- `description`：直接从pack-manifest.json读取
- `version`：从pack-manifest.json读取
- `ref`：通过--ref参数传入的git tag
- `path`：相对仓库根目录的pack路径
- `gate_result`：空对象（由CI在gate通过时填充，不覆盖已有内容）

## 5. 行为边界

### 必须做：
- 只处理 packs/optional/ 下的pack
- 拒绝发布时给出明确错误信息
- --dry-run时输出到stdout，不写文件
- 输出目录不存在时自动创建
- 不覆盖已有的gate_result字段（保留CI填充的结果）

### 不得做：
- 发布 packs/core/ 下的任何pack
- 执行git push或任何远程操作
- 修改pack-manifest.json或SKILL.md
- 在没有--ref的情况下（非dry-run）写文件
- 安装任何外部Python依赖（脚本为纯stdlib）
