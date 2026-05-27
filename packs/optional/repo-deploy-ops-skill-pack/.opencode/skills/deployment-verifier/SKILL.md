---
name: deployment-verifier
description: 对已部署/升级/回滚后的服务做功能验证：health/readiness、核心API smoke test、页面可访问性、端口监听、日志与依赖(DB/Redis/MQ/proxy)核验。Trigger for验收、交接、巡检、故障修复后复验；用于证明“服务可用”而非仅“进程已启动”。
compatibility: Requires network access to the service under test. Python 3.11+ and uv recommended. Helpful tools: curl, jq, grep, journalctl, docker logs.
license: Internal use
---

# 目标

验证“服务真的能用”，而不只是“进程活着”。

## 何时使用

-新部署完成后
-升级完成后
-回滚完成后
-做验收、交接、巡检
-故障修复后确认恢复

## 验证层次

### Level 1：健康与可达
-端口是否监听
- `/health`、`/ready`、`/metrics` 是否按预期返回
- Web首页或关键页面是否可打开

### Level 2：核心功能smoke test
-关键API返回正确状态码
-关键响应字段存在
-认证链路基本可用
- worker/queue/background job已恢复

### Level 3：日志与依赖
-启动日志无明显报错
-数据库连接正常
- Redis/MQ/存储等依赖无错误
-反向代理无502/504/连接拒绝

## 推荐脚本

当验证对象是HTTP/HTTPS接口时，优先使用：

```bash
uv run scripts/verify_http.py --spec assets/smoke-matrix.example.json --output -
```

你可以根据实际服务复制并修改 `assets/smoke-matrix.example.json`。

## 最低交付标准

部署完成后，至少提供：

1. 一条health/readiness结果
2. 一条核心功能smoke test结果
3. 一条日志或依赖核验结果

## 验证报告模板

见：
`assets/verification-report-template.md`

## 判定标准

### 可以宣称“验证通过”
仅当：
-核心检查全部通过
-没有阻塞级错误日志
-至少一条关键用户路径已验证

### 不能宣称“验证通过”
如果出现：
- health ok但核心API不通
-页面打开但后台接口报错
-端口监听但日志持续报错
-服务自检通过但反向代理/认证/依赖失败

## gotchas

- `/health` 200不代表数据库就真的可用
-容器 `Up` 不代表应用初始化完成
-只看首页能打开，可能忽略登录态、后端API、worker
-日志中偶发warning与持续error不是一回事，要区分
-生产验证应尽量避开破坏性写操作

## 何时读取参考文件

-需要扩展smoke test矩阵时，读取：
  `references/smoke-test-design.md`
-需要判断日志中的错误是否阻塞上线时，读取：
  `references/log-triage.md`
