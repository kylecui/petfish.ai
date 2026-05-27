# TrustSkills Governance Model / TrustSkills治理模型

## Overview / 概述

`trustskills` evaluates a skill by executable behavior, resource access scope, side effects, and persistence signals.

`trustskills` 不是按“文案看起来像不像安全”来判断，而是按可执行行为、资源访问范围、副作用和持久化风险来做治理决策。

---

## 1. Six Risk Dimensions / 六个风险维度

Default weighted dimensions:

| Dimension | Weight | Meaning |
|---|---:|---|
| `shell` | 0.25 | shell执行、子进程调用、高权限工具声明 |
| `network` | 0.25 | 网络访问、外部域名、远程通信范围 |
| `file_write` | 0.15 | 文件写入能力、批量写路径、宽范围写入 |
| `sensitive_data` | 0.15 | 接触密钥、凭证、敏感系统路径、隐私数据 |
| `script_risk` | 0.10 | 脚本内的file IO、subprocess、network等行为证据 |
| `persistence` | 0.10 | 持久化副作用，如服务安装、长期状态写入、配置驻留 |

These weights come from the default rules engine and are used to compute the overall risk score.

这些权重来自默认规则引擎，用于计算综合风险分。

---

## 2. Five Governance Levels / 五级治理动作

Default thresholds:

| Level | Threshold | Meaning |
|---|---:|---|
| `allow` | `>= 0.00` | 直接放行 |
| `allow_with_ask` | `>= 0.15` | 允许执行，但应先征得用户确认 |
| `sandbox_required` | `>= 0.35` | 需要沙箱隔离执行 |
| `manual_review_required` | `>= 0.55` | 必须进入人工复核 |
| `deny` | redlines only | 命中红线直接拒绝 |

Important: `deny` is not driven by score thresholds. It is triggered by hard redline violations.

重点：`deny` 不是普通阈值计算结果，而是红线命中后的硬拒绝。

---

## 3. Redline Rules / 红线规则

The default engine contains four hard DENY gates:

| Redline | Meaning |
|---|---|
| `subprocess-network-combo` | script同时具备 `subprocess` 与 `network`，可能形成 download-and-exec 路径 |
| `dangerous-system-paths` | 读写敏感路径，如 `/etc/passwd`、`/etc/shadow`、`/root/.ssh`、`~/.ssh/id_*` |
| `sudo-without-approval` | 声明 `sudo`/`su`，但没有显式 `approval_required` |
| `subprocess-os-combo` | script同时具备 `subprocess` 与 `os` 级操作，表明任意命令/高破坏面行为 |

In practical policy language, these map to the hard-stop cases described by the engine design:

- subprocess + network combo
- sensitive paths such as `/etc/passwd` and `~/.ssh`
- sudo without approval
- subprocess + os combo

命中任何一条红线，治理结果都会直接进入 `deny`。

---

## 4. Indicator Model / 风险指标模型

Below the redlines, the default engine adds indicator-based dimension scores. Typical built-in indicators include:

- `shell-execution-behavior`
- `shell-execution-declaration-only`
- `high-privilege-tools`
- `network-access`
- `network-unrestricted-domains`
- `file-writes`
- `file-broad-write-scope`
- `sensitive-data-contact`
- `script-file-io`
- `script-subprocess`
- `script-network`
- `many-tools`
- `persistence-behavior`

这些指标不会直接触发`deny`，但会推动维度分与综合风险分上升。

---

## 5. Custom Policy YAML / 自定义策略YAML

`trustskills` supports policy customization through a YAML or JSON file passed with `--policy`.

可通过 `--policy` 传入YAML或JSON文件，覆盖默认权重、阈值与规则开关。

Supported top-level keys:

- `weights`
- `thresholds`
- `disabled_redlines`
- `disabled_indicators`
- `extra_indicators`

Example:

```yaml
weights:
  shell: 0.20
  network: 0.20
  file_write: 0.20
  sensitive_data: 0.20
  script_risk: 0.10
  persistence: 0.10

thresholds:
  - score: 0.00
    level: allow
  - score: 0.10
    level: allow_with_ask
  - score: 0.30
    level: sandbox_required
  - score: 0.50
    level: manual_review_required

disabled_redlines:
  - sudo-without-approval

disabled_indicators:
  - many-tools

extra_indicators:
  - name: custom-persistence-flag
    dimension: persistence
    score: 0.4
    field: persistence_behavior
```

### Guidance / 使用建议

- Adjust `weights` when your environment treats one dimension as more dangerous than another.
- Adjust `thresholds` when your release process is stricter or more permissive.
- Disable redlines only with strong organizational justification.
- Add custom indicators for environment-specific signals.

- 当你的组织对某一类风险更敏感时，改 `weights`
- 当你的门禁标准更严格或更宽松时，改 `thresholds`
- `disabled_redlines` 应非常谨慎，通常只在受控环境中使用
- 用 `extra_indicators` 承载你自己的领域特有风险信号

---

## 6. Operational Interpretation / 结果解释

- `allow`: low-risk content or bounded automation
- `allow_with_ask`: can run, but human confirmation should be explicit
- `sandbox_required`: behavior surface is broad enough that isolation is recommended
- `manual_review_required`: risk is high enough that human gatekeeping is mandatory
- `deny`: the skill crosses a hard redline and should not proceed

治理分不是“绝对真理”，但它提供了一个稳定、可审计、可自动化接入的默认安全边界。
