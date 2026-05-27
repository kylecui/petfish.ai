# Private Repo Access on Credential-Free Servers

## 场景

目标服务器没有存储GitHub凭据（安全最佳实践）。部署时需要clone/pull私有仓库。

## 标准流程

在**单条SSH命令链**中完成token注入和清除：

```bash
# 必须在同一个SSH命令中完成——不可拆分为两次执行
TOKEN=$(gh auth token)
git remote set-url origin https://x-access-token:${TOKEN}@github.com/<org>/<repo>.git
git pull
git remote set-url origin https://github.com/<org>/<repo>.git  # 立即清除token
```

## 硬性规则

1. **Token注入和清除必须在同一SSH命令/脚本中完成**——永远不要分开执行
2. **验证清除**：`git remote get-url origin` 输出中不可包含token
3. **不写入服务器文件**：永远不写 `~/.netrc`、`~/.git-credentials`、环境变量文件
4. **不记录含token的URL**：日志和输出中不可出现token

## 完整示例

```bash
ssh user@host 'bash -s' <<'EOF'
set -e
cd /opt/myservice/current
TOKEN=$(cat /dev/stdin)
git remote set-url origin "https://x-access-token:${TOKEN}@github.com/org/repo.git"
git pull origin main
git remote set-url origin "https://github.com/org/repo.git"
echo "✓ Pull complete, token cleared"
git remote get-url origin  # 验证
EOF
```

## 何时使用

- 部署前流程中检测到repo为私有仓库
- `git pull` 返回 `fatal: could not read Username`
- 首次clone私有仓库到目标服务器

## 与部署计划的关系

在 deployment-executor 的 Plan 阶段加入检查项：

- [ ] Repo是否为私有？
- [ ] 目标服务器是否已配置credentials？
- [ ] 如未配置，token注入流程是否已纳入部署脚本？
