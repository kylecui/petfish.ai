# Deployment Signal Priority

当repo中存在多种运行线索时，按以下优先级判断：

1. **明确的生产部署材料**
   - compose
   - k8s manifests/helm
   - systemd units
   - deploy scripts
2. **README中明确写明的生产方式**
3. **构建文件中可验证的启动方式**
4. **代码中的默认入口**
5. **推断出的保底方案**

## 冲突处理

-若 `README` 与实际文件不一致，优先相信仓库中真实存在且近期维护的部署材料。
-若同时存在 `Dockerfile` 与 `systemd` 线索，不要主观选择；应按目标主机条件和用户要求决定。
-若只有开发服务器命令，没有生产线索，应明确标记“需补充生产部署约束”。
