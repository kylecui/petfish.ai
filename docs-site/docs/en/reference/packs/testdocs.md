# testdocs

**测试用例与使用文档生成 — test case、覆盖率矩阵、README、API docs**

| Field | Value |
|---|---|
| Pack name | `opencode-skill-pack-testcases-usage-docs` |
| Alias | `testdocs` |
| Version | 1.0.1 |
| Skills | 2 |
| Commands | 0 |
| Agents | 0 |
| Compatibility | opencode |

## Skills

- [`generate-test-cases`](../skills/generate-test-cases.md) — Generate test cases/test matrix for the current repo: API/CLI/UI/SDK/service, smoke/regression/acceptance/negative/bound...
- [`generate-usage-docs`](../skills/generate-usage-docs.md) — Generate grounded usage docs from the current repo: README, Quick Start, configuration, usage, API/CLI/SDK docs, trouble...

## Install

=== "PowerShell"

    ```powershell
    & ([scriptblock]::Create((irm https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.ps1))) -Pack "testdocs"
    ```

=== "Bash"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/kylecui/petfish.ai/master/remote-install.sh | bash -s -- --pack testdocs
    ```
