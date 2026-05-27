# Config and Secret Audit

盘点配置时，至少回答这些问题：

## 变量类
-哪些环境变量是必须的？
-哪些只影响可选能力？
-是否有默认值？
-是否存在 `.env.example` / sample config？

## 文件类
-是否需要证书、密钥文件、私钥、license文件？
-是否需要挂载目录？
-是否需要写入日志、缓存、上传目录？

## 外部依赖类
- DB/Redis/MQ/object storage/SMTP/OAuth/webhook
-第三方API key
- DNS/domain/TLS/reverse proxy

## 风险提示
-不要把示例配置当成真实可用配置
-不要在报告中暴露真实secret
-如果变量用途不清楚，要标记为待确认项
