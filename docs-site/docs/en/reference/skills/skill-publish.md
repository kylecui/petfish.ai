# skill-publish

> Pack: **toolchain**

>

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


*... (146 more lines in full SKILL.md)*
