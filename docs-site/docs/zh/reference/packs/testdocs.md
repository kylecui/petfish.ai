# testdocs

**测试用例与使用文档生成 — test case、覆盖率矩阵、README、API docs**

| 字段 | 值 |
|---|---|
| 包名 | `opencode-skill-pack-testcases-usage-docs` |
| 别名 | `testdocs` |
| 版本 | 1.0.1 |
| 技能数 | 2 |
| 命令数 | 0 |
| 代理数 | 0 |
| 兼容性 | opencode |

## 技能列表

- [`generate-test-cases`](../skills/generate-test-cases.md) — Generate test cases/test matrix for the current repo: API/CLI/UI/SDK/service, smoke/regression/acceptance/negative/bound...
- [`generate-usage-docs`](../skills/generate-usage-docs.md) — Generate grounded usage docs from the current repo: README, Quick Start, configuration, usage, API/CLI/SDK docs, trouble...

## 安装

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "testdocs"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack testdocs
    ```
