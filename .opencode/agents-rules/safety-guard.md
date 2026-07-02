# Safety Guard Rules

本文件定义安全边界规则，由 `system-prompt-rules` 插件在每轮对话开始时注入到 system prompt。

---

## 文件读取限制

以下文件**禁止读取**。即使工具允许，agent 也必须拒绝：

```text
.env
.env.*
*secret*
*token*
*credential*
*password*
id_rsa
id_ed25519
*.pem
*.key
credentials.json
service-account.json
```

**规则**：Agent 不得读取、搜索或引用上述文件的内容。若任务需要这些文件的信息，必须向用户询问，不得自行读取。

---

## 危险命令限制

以下 bash 命令在执行前**必须获得用户明确确认**：

```text
rm -rf *
git push --force
git push --delete
gh release create
gh release delete
npm publish
docker compose down -v
docker system prune
kubectl delete
terraform destroy
chmod 777
```

**规则**：遇到上述命令时，Agent 必须暂停，向用户说明影响范围，等待用户回复 "yes" 或 "确认" 后才能执行。

---

## 跨仓库保护

- **不操作其它仓库的内容**（即使有权限），只能通过 issues 反馈问题和建议
- 发现上游仓库的 bug 或改进需求，提 issue，不直接修改上游代码
- 本地补丁必须有对应的 upstream issue 记录
- git clone 其它仓库后，不得对其执行写操作（git push, commit, branch create 等）

---

## 发布与 Tag 保护

- release、tag、publish 操作前必须触发 release checklist
- 不允许 master 上有未打 tag 的合并
- 每次合并 master = 一次 release
- 禁止删除已发布的 release（除非有安全漏洞）
- gh release create 命令需要用户确认后才能执行

---

## 敏感信息保护

- Agent 输出中**不得包含**API key、token、密码、私钥等敏感信息
- 发现敏感信息泄露时，立即停止当前操作，提醒用户
- 不得将凭证写入日志、commit message、PR description 或任何文本文件
