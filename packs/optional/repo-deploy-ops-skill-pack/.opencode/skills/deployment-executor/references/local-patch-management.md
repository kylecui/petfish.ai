# Local Patch Management for Multi-Service Co-location

## 场景

多个服务共享一台服务器。每个项目的 `docker-compose.yml` 或配置文件需要服务器特有的修改（端口重映射、环境变量补充、healthcheck修复），这些修改不在上游仓库中。

## Patch Lifecycle

```
部署 → 发现问题 → 应用最小本地补丁 → 记录到README
→ 向上游提issue → 上游修复 → git pull → 确认上游已包含修复
→ 退役本地补丁（从"Deployment-Specific"移到"Upstreamed"）
→ 验证服务健康
```

## git pull with Local Patches

```bash
git stash
git pull  # （私有仓库需走token注入流程）

# 交叉检查README中"Deployment Fixes Applied"段落
# 已被上游合并的补丁 → 移到"Upstreamed Fixes"，不再重新apply

# 使用python3重新apply剩余补丁（不要用sed）
python3 -c "
with open('docker-compose.yml', 'r') as f:
    content = f.read()
content = content.replace('\"1883:1883\"', '\"11883:1883\"')
# ... more replacements
with open('docker-compose.yml', 'w') as f:
    f.write(content)
"

docker compose config   # 验证YAML语法
docker compose up -d --build
```

## Patch记录格式（README.md中）

### Upstreamed Fixes
| 修复内容 | Issue链接 | Upstream Commit | 日期 |
|---------|----------|-----------------|------|
| healthcheck端点修正 | org/repo#42 | abc1234 | 2026-04-15 |

### Deployment-Specific Patches
| 修改内容 | 原因 | 影响文件 | 必须在每次git pull后重新apply |
|---------|------|---------|---------------------------|
| 端口1883→11883 | 与其他服务冲突 | docker-compose.yml | 是 |

## 硬性规则

1. **每个本地补丁必须有对应记录**——未记录的修改是"野修改"
2. **使用python3修改YAML**，永远不要用 `sed`（YAML对空白敏感，sed会破坏缩进）
3. **本地补丁与上游更新冲突时**，先读上游changelog，再决定保留/调整/删除
4. **每次git pull后验证服务健康**，确认补丁正确重新apply
5. **补丁退役**：上游修复后，本地补丁必须显式移除，不能留着"以防万一"

## 与deployment-verifier的关系

部署验证时加入检查：

- [ ] README中记录的所有deployment-specific patches是否已在运行配置中体现？
- [ ] 是否有未记录的本地修改？(`git diff` 应该只显示已记录的补丁)

## 何时读取本文件

- 执行升级（git pull）时，需要处理本地修改冲突
- 发现新的需要本地补丁的问题时
- 验证部署完整性时
