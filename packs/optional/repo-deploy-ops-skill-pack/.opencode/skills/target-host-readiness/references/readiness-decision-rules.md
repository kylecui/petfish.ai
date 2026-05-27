# Readiness Decision Rules

## Blocking issue（阻塞项）
符合任一项即可视为阻塞：

-缺少必需运行时
-关键目录不可写
-无法创建/管理服务
-关键端口冲突且无替代方案
-必需网络依赖无法访问
-必需配置/密钥缺失

## Non-blocking suggestion（建议项）
例如：

-缺少jq但不影响运行
-缺少htop/lsof等调试工具
-日志目录尚未做logrotate
-未配置监控/告警但服务可运行
