# Credential Safety Policy

## Core Rule

**Never store plaintext secrets in the research workspace, git repository, or chat history.**

## Allowed Storage References

| Reference Type | Format | Example |
|---|---|---|
| OS Keychain | `os-keychain:<name>` | `os-keychain:university-library` |
| Environment Variable | `env:<VAR_NAME>` | `env:LIBRARY_API_KEY` |
| Manual Login | `manual-login` | User logs in manually |
| Config File (gitignored) | `file:<path>` | `file:~/.config/research/creds.json` |

## Forbidden

- Plaintext passwords in any file
- Session tokens in chat messages
- Cookies in JSONL data files
- API keys in SKILL.md or AGENTS.md
- Credentials in source-index or evidence-ledger
- Secrets in git history

## Interaction Template

When credentials are needed:
```
请不要直接把密码发给我。你可以选择：
- 手动登录后上传PDF
- 告诉我使用哪种机构访问方式
- 配置本机secret store或环境变量后让我读取凭据引用
```

## `literature-access.json` Rules

- `store_raw_secret` must always be `false`
- `secret_ref` must be a reference, not a value
- Provider credentials are never logged to access-attempts.jsonl
