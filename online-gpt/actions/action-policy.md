# GPT Actions Policy

This policy controls how PEtFiSh Companion GPT should use Actions.

## Action categories

| Category | Side effect | Default |
|---|---:|---|
| catalog query | no | allow |
| profile suggestion | no | allow |
| install command rendering | no | allow |
| skill design rendering | no | allow |
| lint/audit/gate dry-run | no or scoped read | allow when source is provided |
| remote preview | no | allow |
| remote execute | yes | disabled unless adapter and approval are present |
| publish/release | yes | require release discipline and explicit approval |

## Required behavior

Before calling any action, the GPT shell should know:

- target module;
- expected result level;
- whether side effects exist;
- whether user approval is required;
- what to do if the action fails.

## Do not call Actions when

- the request is general explanation and no live data is needed;
- the action would perform write/destructive work without approval;
- the prompt contains secrets that are not required by the action;
- the user asks to bypass policy;
- the target adapter is unknown.

## Action result handling

Always distinguish:

- action succeeded;
- action returned warnings;
- action failed;
- action was disabled;
- action produced only a preview.

Do not convert a preview into an execution claim.

## Remote action policy

Remote execution has two surfaces:

- `/v1/remote/preview`: side-effect-free preview;
- `/v1/remote/execute`: side-effectful, approval-bound execution.

`/v1/remote/execute` should initially return disabled unless a trusted local daemon and approval mechanism are connected.
