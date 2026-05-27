# Release Layout

推荐用于传统主机部署：

```text
/opt/<service>/
  releases/
    20260423-210500/
    20260424-093200/
  current -> releases/20260424-093200
  shared/
    config/
    logs/
    data/
```

## 优点

-回滚简单
-新旧版本隔离
-更容易记录版本与变更
-更适合systemd WorkingDirectory/ExecStart指向 `current`

## 适用场景

- Python/Node/Go/Java主机部署
-需要频繁升级
-需要清晰留痕
