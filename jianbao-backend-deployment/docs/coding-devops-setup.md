# 腾讯云CODING DevOps 配置指南

## 📋 概述

已为您配置了完整的腾讯云CODING DevOps流水线，专为Python FastAPI后端服务优化：
- ✅ 代码质量检查（Black、Flake8、MyPy）
- ✅ 自动化测试（单元测试、集成测试、覆盖率报告）
- ✅ 安全扫描（依赖漏洞、代码安全扫描）
- ✅ Docker镜像构建（自动推送到TCR）
- ✅ 自动部署到TKE集群（测试/生产环境）
- ✅ 企业微信通知

## 📁 配置文件位置

```
jianbao-backend-deployment/
├── .coding-ci.yml              # 🔥 CODING DevOps流水线配置
├── Dockerfile                  # Docker镜像构建
├── docker-entrypoint.sh        # 容器启动脚本
├── requirements.txt            # Python依赖
├── k8s/                       # Kubernetes部署配置
│   ├── deployment.yaml        # 后端服务部署
│   ├── service.yaml           # 服务暴露
│   └── configmap.yaml         # 配置管理
├── infrastructure/            # 基础设施配置
│   ├── secrets.yaml           # 密钥管理
│   └── ingress.yaml           # 负载均衡
└── docs/
    └── coding-devops-setup.md  # 本配置指南
```

## 🚀 CODING DevOps 快速开始

### 步骤1：创建CODING项目

#### 1.1 注册登录
```bash
# 访问CODING官网
https://coding.net

# 使用腾讯云账号登录（推荐）
# 或注册新的CODING账号
```

#### 1.2 创建团队和项目
```bash
1. 点击"创建团队" → 填写团队信息
2. 进入团队 → 点击"创建项目"
3. 选择"DevOps项目" → 填写项目信息
   - 项目名称: jianbao-backend
   - 项目标识: jianbao-backend
   - 项目描述: 鉴宝管理后台后端服务
```

#### 1.3 导入代码仓库
```bash
# 方式1: 从GitHub导入
代码仓库 → 导入外部仓库 → 填写GitHub仓库地址

# 方式2: 手动推送代码
git remote add coding https://your-team.coding.net/p/jianbao-backend/d/backend/git
git push coding main
```

### 步骤2：配置构建环境

#### 2.1 创建构建计划
```bash
1. 进入项目 → 持续集成 → 构建计划
2. 点击"创建构建计划"
3. 选择"自定义构建过程"
4. 构建计划名称: "后端服务CI/CD"
5. 代码源: 选择刚才导入的代码仓库
6. 配置文件: .coding-ci.yml
```

#### 2.2 配置环境变量
在构建计划设置中添加以下环境变量：

```bash
# 基础配置（系统会自动注入CODING相关变量）
TCR_REGISTRY=ccr.ccs.tencentyun.com
TCR_NAMESPACE=jianbao
IMAGE_NAME=backend
TKE_REGION=ap-beijing

# 环境配置
PROD_NAMESPACE=jianbao-system
STAGING_NAMESPACE=jianbao-staging
DEPLOYMENT_NAME=jianbao-backend

# 通知配置（可选）
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key
```

### 步骤3：配置腾讯云集成

#### 3.1 配置容器镜像仓库（TCR）
```bash
1. 项目设置 → 开发者选项 → 腾讯云账号绑定
2. 绑定您的腾讯云账号
3. 构建计划 → 流程配置 → 添加"推送到TCR"步骤
4. 配置TCR信息:
   - 地域: ap-beijing
   - 命名空间: jianbao
   - 镜像仓库: backend
```

#### 3.2 配置TKE集群访问
```bash
1. 项目设置 → 开发者选项 → 凭据管理
2. 添加"Kubernetes凭据"
3. 凭据名称: tke-cluster-access
4. 上传kubeconfig文件或填写集群信息:
   - 集群地址: your-tke-cluster-endpoint
   - Token: your-service-account-token
```

## 🔄 流水线阶段详解

### 阶段1：代码质量检查
```yaml
触发条件: 所有分支的Push和MR
检查内容:
  ✅ Black代码格式检查
  ✅ isort导入排序检查
  ✅ Flake8代码规范检查
  ✅ MyPy类型检查
持续时间: 2-3分钟
```

### 阶段2：自动化测试
```yaml
触发条件: 代码检查通过后
测试环境:
  - MySQL 8.0数据库
  - Redis 7缓存服务
测试内容:
  ✅ 单元测试
  ✅ 集成测试
  ✅ 代码覆盖率统计
持续时间: 5-8分钟
```

### 阶段3：安全扫描
```yaml
触发条件: main/master/develop分支
扫描工具:
  ✅ Safety: 依赖包漏洞扫描
  ✅ Bandit: Python代码安全扫描
  ✅ TCR镜像安全扫描
持续时间: 3-5分钟
```

### 阶段4：构建Docker镜像
```yaml
触发条件: 测试通过的main/develop分支
构建特性:
  ✅ 多阶段Docker构建
  ✅ 自动生成镜像标签（时间戳+提交ID）
  ✅ 自动推送到TCR
持续时间: 3-5分钟
```

### 阶段5：部署测试环境
```yaml
触发条件: develop分支构建成功
部署目标: jianbao-staging命名空间
部署策略: 滚动更新
健康检查: 自动验证服务可用性
持续时间: 2-3分钟
```

### 阶段6：部署生产环境
```yaml
触发条件: main/master分支构建成功
部署目标: jianbao-system命名空间
部署策略: 蓝绿部署
安全机制: 健康检查失败自动回滚
持续时间: 3-5分钟
```

### 阶段7：通知
```yaml
触发条件: 部署完成（成功或失败）
通知方式: 企业微信群消息
通知内容: 部署状态、访问地址、操作者等
```

## 🎯 分支策略和工作流

### 推荐的Git工作流

```bash
# 1. 功能开发
git checkout -b feature/user-management
# ... 开发代码 ...
git add .
git commit -m "feat: add user management API"
git push origin feature/user-management

# 2. 创建合并请求到develop（触发代码检查）
# 在CODING网页操作：代码仓库 → 合并请求 → 创建合并请求

# 3. 合并到develop分支（触发测试环境部署）
# 合并请求通过后自动合并，或手动合并：
git checkout develop
git merge feature/user-management
git push origin develop  # 🚀 自动部署到测试环境

# 4. 测试验证通过后，合并到main分支（触发生产环境部署）
git checkout main
git merge develop
git push origin main     # 🚀 自动部署到生产环境
```

### 分支保护规则
```bash
在CODING中设置分支保护：
代码仓库 → 设置 → 分支设置

main分支保护:
  ✅ 禁止强制推送
  ✅ 合并前必须通过构建
  ✅ 合并前必须代码评审
  ✅ 删除源分支

develop分支保护:
  ✅ 禁止强制推送
  ✅ 合并前必须通过构建
```

## 📊 监控和管理

### 构建监控
```bash
# 查看构建状态
持续集成 → 构建计划 → 构建历史

# 查看构建日志
点击具体构建 → 查看详细日志

# 构建统计
持续集成 → 统计 → 构建成功率、平均构建时间等
```

### 部署监控
```bash
# 查看部署状态
持续部署 → 应用 → 部署历史

# TKE集群监控
腾讯云控制台 → 容器服务TKE → 集群监控

# 服务健康检查
curl https://api.jianbao.com/health
curl https://api-staging.jianbao.com/health
```

## 🎯 CODING DevOps vs GitHub Actions优势

### 集成优势
```yaml
CODING优势:
  ✅ 原生腾讯云集成，无需配置复杂认证
  ✅ 中文界面，学习成本低
  ✅ TCR和TKE一键集成
  ✅ 可视化配置界面
  ✅ 内置项目管理功能
  ✅ 更好的网络连接速度
```

### 成本优势
```yaml
免费额度对比:
  CODING DevOps: 400分钟/月免费
  GitHub Actions: 2000分钟/月免费
  
实际使用（每周2次部署）:
  每次构建时间: 15-20分钟
  月使用量: 20分钟 × 8次 = 160分钟
  
结论: 都在免费范围内，CODING超出后更便宜
```

## 🚀 快速部署检查清单

### 部署前检查
- [ ] CODING项目已创建
- [ ] 代码已推送到CODING仓库
- [ ] 构建计划已配置
- [ ] 腾讯云账号已绑定
- [ ] TCR镜像仓库已创建
- [ ] TKE集群已创建并配置访问权限
- [ ] 环境变量已配置
- [ ] 分支保护规则已设置

### 首次部署
```bash
# 1. 推送代码触发构建
git push origin develop  # 部署到测试环境

# 2. 查看构建过程
# 在CODING控制台查看构建日志

# 3. 验证部署结果
curl https://api-staging.jianbao.com/health

# 4. 生产环境部署
git push origin main     # 部署到生产环境
curl https://api.jianbao.com/health
```

现在您的Python后端服务拥有了完全自动化的CODING DevOps流水线！🎉