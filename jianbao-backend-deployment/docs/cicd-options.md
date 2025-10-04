# CI/CD部署选项详解

## 🏗️ 腾讯云CI/CD服务对比

### 1. 腾讯云CODING DevOps（推荐）

#### 优势：
- ✅ **原生集成**：与腾讯云服务深度集成
- ✅ **免费额度**：提供免费的构建时长
- ✅ **中文界面**：完全中文化，易于使用
- ✅ **TKE集成**：直接部署到TKE集群
- ✅ **TCR集成**：自动推送到腾讯云镜像仓库

#### 配置方式：
```yaml
# 在CODING中创建项目
1. 访问 https://coding.net
2. 创建团队和项目
3. 导入代码仓库
4. 配置构建计划
```

### 2. GitLab CI/CD（已配置）

#### 优势：
- ✅ **功能强大**：丰富的CI/CD功能
- ✅ **社区活跃**：大量插件和文档
- ✅ **配置灵活**：yaml配置文件
- ✅ **已经配置**：开箱即用

#### 文件位置：
```
jianbao-backend-deployment/ci-cd/gitlab-ci.yml
```

### 3. GitHub Actions

#### 优势：
- ✅ **GitHub集成**：如果使用GitHub仓库
- ✅ **marketplace**：丰富的Action市场
- ✅ **免费额度**：提供一定的免费构建时间

### 4. Jenkins（自建）

#### 优势：
- ✅ **完全自主**：部署在自己的服务器
- ✅ **插件丰富**：海量插件支持
- ❌ **维护成本**：需要自行维护服务器

## 🎯 ✅ 已选择方案：腾讯云CODING DevOps

### 为什么推荐CODING？
1. **成本最低**：免费额度足够小团队使用
2. **集成最好**：与TKE、TCR无缝集成
3. **使用简单**：中文界面，配置简单
4. **维护成本低**：无需自建服务器

### CODING DevOps 配置步骤

#### 步骤1：创建CODING项目
```bash
# 1. 访问 https://coding.net
# 2. 注册/登录腾讯云账号
# 3. 创建团队
# 4. 创建项目
```

#### 步骤2：导入代码
```bash
# 方式1：直接在CODING创建代码仓库
# 方式2：从GitHub/GitLab导入
git remote add coding https://your-team.coding.net/p/jianbao/d/backend/git
git push coding main
```

#### 步骤3：配置构建计划
创建 `.coding-ci.yml` 文件：
```yaml
master:
  push:
    - stages:
        - name: 代码检查
          image: python:3.11
          commands:
            - pip install -r requirements.txt
            - flake8 .
            - pytest tests/
        
        - name: 构建镜像
          image: docker:latest
          commands:
            - docker build -t $TCR_REGISTRY/jianbao/backend:$CI_BUILD_REF .
            - docker push $TCR_REGISTRY/jianbao/backend:$CI_BUILD_REF
          
        - name: 部署到TKE
          image: coding-public-docker.pkg.coding.net/public/docker/tke-kubectl:latest
          commands:
            - kubectl set image deployment/jianbao-backend backend=$TCR_REGISTRY/jianbao/backend:$CI_BUILD_REF -n jianbao-system
            - kubectl rollout status deployment/jianbao-backend -n jianbao-system
```

## 🔧 当前GitLab CI/CD配置详解

### 流水线阶段：
1. **validate** - 代码验证（格式检查、类型检查）
2. **test** - 自动化测试（单元测试、集成测试）
3. **security** - 安全扫描（依赖漏洞、代码安全）
4. **build** - 构建Docker镜像
5. **deploy-staging** - 部署到测试环境
6. **deploy-production** - 部署到生产环境（手动触发）
7. **notify** - 部署通知（企业微信）

### 环境变量配置：
```bash
# 在GitLab项目设置中配置这些变量
TCR_REGISTRY=ccr.ccs.tencentyun.com
TCR_NAMESPACE=jianbao
TCR_USERNAME=your_username
TCR_PASSWORD=your_password
KUBE_CONFIG=base64_encoded_kubeconfig
WECHAT_WEBHOOK_URL=your_webhook_url
```

## 📊 CI/CD服务成本对比

| 服务 | 免费额度 | 超出后价格 | 适用场景 |
|------|----------|------------|----------|
| **CODING DevOps** | 400分钟/月 | 0.1元/分钟 | 中小团队 |
| **GitLab.com** | 400分钟/月 | $10/用户/月 | 开源项目 |
| **GitHub Actions** | 2000分钟/月 | $0.008/分钟 | GitHub用户 |
| **Jenkins自建** | 服务器成本 | 维护成本 | 大型团队 |

## 🚀 快速迁移到CODING DevOps

如果您想使用腾讯云CODING，我可以为您创建相应的配置文件：

```bash
# 1. 创建CODING配置
cp ci-cd/gitlab-ci.yml .coding-ci.yml
# 然后调整为CODING语法

# 2. 配置腾讯云集成
# 在CODING项目设置中添加TKE和TCR集成

# 3. 推送代码触发构建
git push coding main
```

## 💡 建议

### 对于您的项目：
1. **如果已有GitLab**：继续使用现有的GitLab CI/CD配置
2. **如果想要最佳集成**：推荐迁移到腾讯云CODING DevOps
3. **如果使用GitHub**：可以考虑GitHub Actions

需要我帮您创建腾讯云CODING的配置文件吗？