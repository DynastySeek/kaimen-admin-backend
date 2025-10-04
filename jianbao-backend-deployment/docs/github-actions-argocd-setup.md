# GitHub Actions + ArgoCD CI/CD 部署指南

本文档详细介绍如何使用 GitHub Actions + ArgoCD 替代 CODING DevOps，实现完整的 CI/CD 流水线。

## 📋 **架构概览**

```mermaid
flowchart TD
    A[开发者提交代码] --> B[GitHub Actions CI]
    B --> C[代码质量检查]
    B --> D[安全扫描]
    B --> E[构建Docker镜像]
    E --> F[推送到腾讯云TCR]
    F --> G[更新K8s配置]
    G --> H[ArgoCD检测变更]
    H --> I[自动同步部署]
    I --> J[TKE集群]
    
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#9ff,stroke:#333,stroke-width:2px
    style J fill:#9f9,stroke:#333,stroke-width:2px
```

## 🚀 **快速开始**

### **前置要求**

- [x] TKE集群已创建并可访问
- [x] kubectl已配置并连接到集群
- [x] GitHub仓库已创建
- [x] 腾讯云TCR镜像仓库已创建
- [x] 相关密钥和凭证已准备

### **一键部署命令**

```bash
# 1. 克隆仓库
git clone https://github.com/DynastySeek/kaimen-backend.git
cd kaimen-backend

# 2. 部署ArgoCD
chmod +x scripts/deploy-argocd.sh
./scripts/deploy-argocd.sh

# 3. 配置Secrets
kubectl apply -f k8s/secrets.yaml

# 4. 创建应用命名空间
kubectl create namespace jianbao-system
```

## ⚙️ **详细配置步骤**

### **第一步：配置GitHub Actions Secrets**

在GitHub仓库的 `Settings` → `Secrets and variables` → `Actions` 中添加以下密钥：

| 密钥名称 | 描述 | 示例值 |
|---------|------|--------|
| `TCR_USERNAME` | 腾讯云TCR用户名 | `100012345678` |
| `TCR_PASSWORD` | 腾讯云TCR密码/令牌 | `tcr_token_xxx` |
| `SLACK_WEBHOOK` | Slack通知webhook（可选） | `https://hooks.slack.com/...` |

### **第二步：部署ArgoCD**

```bash
# 运行自动化部署脚本
./scripts/deploy-argocd.sh

# 脚本会自动:
# 1. 检查前置条件
# 2. 创建ArgoCD命名空间
# 3. 安装ArgoCD核心组件
# 4. 应用自定义配置
# 5. 等待服务启动
# 6. 获取管理员密码
```

**预期输出：**
```
========================================
ArgoCD 管理员登录信息:
用户名: admin
密码: xxxxx-xxxxx-xxxxx
========================================
```

### **第三步：访问ArgoCD UI**

#### **方式1：端口转发（开发测试）**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# 访问: https://localhost:8080
```

#### **方式2：LoadBalancer（生产环境）**
```bash
# 获取外部IP
kubectl get svc argocd-server -n argocd

# 配置域名解析
# argocd.jianbao.com -> LoadBalancer_IP
```

#### **方式3：Ingress（推荐）**
- 已在 `argocd/install.yaml` 中配置
- 需要配置腾讯云CLB和SSL证书
- 域名：`argocd.jianbao.com`

### **第四步：配置Kubernetes Secrets**

**⚠️ 重要：修改敏感信息**

编辑 `k8s/secrets.yaml`，将示例值替换为实际值：

```bash
# 生成base64编码值
echo -n "mysql://user:pass@host:3306/db" | base64
echo -n "your-jwt-secret-key" | base64
echo -n "your-wechat-app-id" | base64

# 应用secrets
kubectl apply -f k8s/secrets.yaml
```

**必须配置的secrets：**
- 数据库连接URL
- Redis连接URL  
- 腾讯云COS密钥
- JWT密钥
- 微信小程序密钥
- TCR镜像拉取密钥

### **第五步：配置ArgoCD Git仓库**

在ArgoCD UI中添加Git仓库：

1. **Settings** → **Repositories** → **Connect Repo**
2. 填写仓库信息：
   - **Type**: `git`
   - **Repository URL**: `https://github.com/DynastySeek/kaimen-backend.git`
   - **Username**: GitHub用户名
   - **Password**: GitHub Personal Access Token

**或者使用kubectl应用：**
```bash
# 先修改 k8s/secrets.yaml 中的GitHub token
kubectl apply -f k8s/secrets.yaml
```

### **第六步：创建ArgoCD应用**

```bash
# 应用ArgoCD应用配置
kubectl apply -f argocd/application.yaml

# 查看应用状态
kubectl get applications -n argocd
```

应用配置详情：
- **应用名称**: `jianbao-backend`
- **源仓库**: `https://github.com/DynastySeek/kaimen-backend.git`
- **目标路径**: `k8s/`
- **目标命名空间**: `jianbao-system`
- **同步策略**: 自动同步 + 自我修复

## 🔄 **CI/CD 工作流程**

### **1. 开发阶段**
```bash
# 开发者本地开发
git checkout -b feature/new-feature
# ... 编写代码 ...
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### **2. Pull Request阶段**
- GitHub Actions触发CI流水线
- 执行代码质量检查
- 运行单元测试
- 安全扫描
- 不构建镜像（节省资源）

### **3. 合并到main分支**
```bash
# PR合并后，GitHub Actions执行完整流水线
1. 代码质量检查 ✓
2. 安全扫描 ✓
3. 构建Docker镜像 ✓
4. 推送到TCR ✓
5. 更新K8s配置文件 ✓
```

### **4. ArgoCD自动部署**
```bash
# ArgoCD检测到Git配置变更
1. 拉取最新配置 ✓
2. 对比当前集群状态 ✓
3. 应用配置差异 ✓
4. 监控部署状态 ✓
5. 部署成功/失败通知 ✓
```

## 📊 **监控和运维**

### **ArgoCD监控**
```bash
# 查看应用状态
kubectl get applications -n argocd

# 查看同步历史
kubectl describe application jianbao-backend -n argocd

# 手动同步
kubectl patch application jianbao-backend -n argocd -p '{"operation":{"sync":{}}}' --type merge
```

### **应用监控**
```bash
# 查看Pod状态
kubectl get pods -n jianbao-system

# 查看应用日志
kubectl logs -f deployment/jianbao-backend -n jianbao-system

# 查看服务状态
kubectl get svc -n jianbao-system
```

### **GitHub Actions监控**
- 访问GitHub仓库的 `Actions` 标签页
- 查看工作流执行历史
- 监控构建时间和成功率
- 查看详细的执行日志

## 🛠️ **故障排查**

### **常见问题解决**

#### **1. ArgoCD应用显示OutOfSync**
```bash
# 检查Git仓库连接
kubectl get secret github-token-secret -n argocd -o yaml

# 手动触发同步
kubectl patch application jianbao-backend -n argocd --type merge -p '{"operation":{"sync":{}}}'
```

#### **2. GitHub Actions构建失败**
```bash
# 检查Secrets配置
- TCR_USERNAME 是否正确
- TCR_PASSWORD 是否有效
- 代码测试是否通过
```

#### **3. Pod启动失败**
```bash
# 检查Secret配置
kubectl get secrets -n jianbao-system

# 检查镜像拉取
kubectl describe pod <pod-name> -n jianbao-system

# 检查配置文件
kubectl get configmap -n jianbao-system
```

#### **4. 健康检查失败**
```bash
# 检查应用端口
kubectl port-forward deployment/jianbao-backend 8000:8000 -n jianbao-system
curl http://localhost:8000/health

# 检查环境变量
kubectl exec deployment/jianbao-backend -n jianbao-system -- env | grep -E "(DATABASE|REDIS)"
```

## 🔒 **安全最佳实践**

### **1. Secrets管理**
- ✅ 使用Kubernetes Secrets存储敏感信息
- ✅ 定期轮换密钥和令牌
- ✅ 限制Secret访问权限
- ❌ 不要在代码中硬编码密钥

### **2. 镜像安全**
- ✅ 使用非root用户运行容器
- ✅ 定期扫描镜像漏洞
- ✅ 使用最小化基础镜像
- ✅ 启用镜像签名验证

### **3. 网络安全**
- ✅ 配置NetworkPolicy限制Pod通信
- ✅ 使用TLS加密所有通信
- ✅ 限制Ingress访问源IP
- ✅ 定期更新证书

### **4. RBAC权限**
- ✅ 最小权限原则
- ✅ 定期审查权限配置
- ✅ 使用ServiceAccount隔离
- ✅ 启用审计日志

## 📈 **性能优化**

### **1. 构建优化**
```yaml
# .github/workflows/ci.yml 中的优化
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
    platforms: linux/amd64,linux/arm64  # 多架构支持
```

### **2. 部署优化**
```yaml
# k8s/deployment.yaml 中的优化
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # 零停机部署
```

### **3. 资源优化**
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## 🎯 **迁移检查清单**

### **从CODING DevOps迁移**
- [ ] 导出现有流水线配置
- [ ] 备份环境变量和密钥
- [ ] 迁移构建脚本
- [ ] 更新部署配置
- [ ] 测试完整流水线
- [ ] 切换生产环境
- [ ] 清理CODING DevOps资源

### **验收测试**
- [ ] 代码提交触发CI流水线
- [ ] 构建和推送镜像成功
- [ ] ArgoCD自动检测并部署
- [ ] 应用健康检查通过
- [ ] 回滚机制测试
- [ ] 监控告警配置

## 🆘 **获取帮助**

- **GitHub Issues**: [仓库Issues页面]
- **官方文档**: 
  - [ArgoCD文档](https://argo-cd.readthedocs.io/)
  - [GitHub Actions文档](https://docs.github.com/en/actions)
- **社区支持**: 
  - [ArgoCD Slack](https://argoproj.github.io/community/join-slack/)
  - [Kubernetes Slack](https://kubernetes.slack.com/)

---

**🎉 恭喜！您已经成功配置了现代化的GitOps CI/CD流水线！**