# 开门管理后台

基于 FastAPI 构建的现代化管理后台系统。

## 项目结构

```
kaimen-admin-backend/
├── .github/               # GitHub Actions 配置
│   └── workflows/
│       └── cicd.yml       # CI/CD 流水线配置
├── app/                   # 应用主目录
│   ├── api/              # API 路由
│   │   ├── endpoints/    # 端点模块
│   │   └── router.py     # 主路由
│   ├── config/           # 配置模块
│   │   └── settings.py   # 环境配置
│   ├── constants/        # 常量和枚举
│   │   ├── enum.py       # 枚举定义
│   │   └── response_codes.py # 响应状态码
│   ├── core/             # 核心功能
│   │   ├── dependencies.py # 依赖注入
│   │   └── exception_handler.py # 异常处理
│   ├── models/           # 数据模型
│   │   ├── appraisal.py  # 鉴定模型
│   │   ├── appraisal_buy.py # 求购模型
│   │   ├── appraisal_consignment.py # 寄售模型
│   │   ├── appraisal_consignment_resource.py # 寄售资源模型
│   │   ├── appraisal_resource.py # 鉴定资源模型
│   │   ├── appraisal_result.py # 鉴定结果模型
│   │   ├── article.py    # 文章模型
│   │   ├── user.py       # 用户模型
│   │   └── user_info.py  # 用户信息模型
│   ├── schemas/          # Pydantic 模式
│   │   ├── appraisal.py  # 鉴定模式
│   │   ├── appraisal_buy.py # 求购模式
│   │   ├── appraisal_consignment.py # 寄售模式
│   │   ├── article.py    # 文章模式
│   │   ├── auth.py       # 认证模式
│   │   ├── upload.py     # 上传模式
│   │   └── user.py       # 用户模式
│   ├── services/         # 业务逻辑层
│   │   ├── appraisal.py  # 鉴定服务
│   │   ├── appraisal_buy.py # 求购服务
│   │   ├── appraisal_consignment.py # 寄售服务
│   │   ├── appraisal_stats.py # 鉴定统计服务
│   │   ├── article.py    # 文章服务
│   │   ├── auth.py       # 认证服务
│   │   ├── sms.py        # 短信服务
│   │   ├── sms_delay_manager.py # 短信延迟管理
│   │   ├── upload.py     # 上传服务
│   │   └── user.py       # 用户服务
│   └── utils/            # 工具函数
│       ├── db.py         # 数据库配置
│       ├── redis.py      # Redis 配置
│       ├── response.py   # 响应工具
│       └── tool.py       # 通用工具
├── charts/               # Helm 部署配置
│   └── kaimen-backend/
│       ├── Chart.yaml    # Helm Chart 配置
│       ├── templates/    # Kubernetes 模板
│       └── values.yaml   # 默认配置值
├── main.py               # 应用入口
├── requirements.txt      # 依赖包
├── Dockerfile           # Docker 镜像构建配置
├── .dockerignore        # Docker 忽略文件
├── .gitignore           # Git 忽略文件
└── README.md            # 项目说明
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- 腾讯云数据库或其他云数据库服务

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 开发模式启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 安装依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate
```

### 3. 访问应用

- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/health

## 部署说明

本项目采用 GitHub Actions 自动化部署，支持多环境部署策略，确保代码质量和发布安全。

### 分支管理策略

- **功能分支**: 开发者在自己的分支进行功能开发
- **develop 分支**: 预发布分支，用于测试验证
- **main 分支**: 生产分支，为客户提供正式服务

### 开发工作流程

#### 1. 功能开发
```bash
# 创建功能分支
git checkout -b feat/your-feature-name

# 开发完成后，提交 PR 前先同步 develop 分支
git pull origin develop

# 提交 PR 到 develop 分支
```

#### 2. 测试验证（develop 分支）
- 功能分支 PR 合并到 `develop` 分支后自动触发部署
- **构建时间**: 后端约 3 分钟，前端约 6 分钟
- 自动构建 Docker 镜像并部署到测试环境
- 在测试环境进行功能验证和测试

#### 3. 生产发布（main 分支）
- 测试验证通过后，从 `develop` 分支提交 PR 到 `main` 分支
- **部署时间**: 约 10 秒（复用已验证的镜像，仅部署）
- 使用 develop 分支已验证的镜像，确保生产环境稳定性

### 分支保护规则

⚠️ **重要提醒**:
- **禁止直接修改 `main` 分支**
- **禁止直接修改 `develop` 分支**（除紧急热修复外）
- 所有代码变更必须通过 PR 流程
- `main` 分支始终跟踪 `develop` 分支的稳定版本

### 部署环境

- **测试环境 (Dev)**: `develop` 分支自动部署，用于功能验证
- **生产环境 (Prod)**: `main` 分支自动部署，为客户提供服务

### 自动化部署流程

#### 1. Develop 分支部署（构建 + 部署）
- 触发条件：PR 合并到 `develop` 分支
- 执行步骤：
  1. 构建 Docker 多架构镜像（linux/amd64, linux/arm64）
  2. 推送镜像到腾讯云容器镜像服务（TCR）
  3. 部署到测试环境
- 部署目标：
  - 命名空间：`kaimen-admin-dev`
  - 应用名称：`kaimen-admin-backend-dev`
  - 环境变量：`ENVIRONMENT=development`

#### 2. Main 分支部署（仅部署）
- 触发条件：PR 从 `develop` 合并到 `main` 分支
- 执行步骤：
  1. 复用 develop 分支已构建的镜像
  2. 快速部署到生产环境
- 部署目标：
  - 命名空间：`kaimen-admin`
  - 应用名称：`kaimen-admin-backend`
  - 环境变量：`ENVIRONMENT=production`

### 紧急修复流程

当遇到紧急问题需要热修复时：

```bash
# 从 main 分支创建 hotfix 分支（基于当前生产环境代码）
git checkout main
git pull origin main
git checkout -b hotfix/fix-critical-issue

# 进行紧急修复
# ... 修复代码 ...

# 提交修复
git add .
git commit -m "hotfix: 紧急修复描述"
git push origin hotfix/fix-critical-issue

# 1. 提交 PR 到 develop 分支进行测试验证
# 2. develop 分支会自动部署到测试环境进行验证
# 3. 验证通过后，提交 PR 到 main 分支进行生产发布
# 4. 同时需要将 hotfix 合并回 develop 分支，保持分支同步
```

⚠️ **注意**: 
- hotfix 分支命名格式：`hotfix/简短描述`
- hotfix 分支基于 main 分支创建，确保修复的是生产环境的问题
- 需要同时合并到 develop 和 main 分支，保持代码同步
- 遵循正常的 PR 流程，确保代码审查和测试验证

#### 3. 配置管理
所有敏感配置通过 GitHub Secrets 管理，包括：

**数据库配置**
- `MYSQL_USER` - 数据库用户名
- `MYSQL_PASSWORD` - 数据库密码
- `MYSQL_HOST` - 数据库主机
- `MYSQL_PORT` - 数据库端口
- `MYSQL_DB` - 数据库名称

**Redis 配置**
- `REDIS_HOST` - Redis 主机
- `REDIS_PORT` - Redis 端口
- `REDIS_USER` - Redis 用户名
- `REDIS_PASSWORD` - Redis 密码
- `REDIS_DB` - Redis 数据库

**腾讯云服务配置**
- `COS_SECRET_ID` - 对象存储密钥 ID
- `COS_SECRET_KEY` - 对象存储密钥
- `COS_REGION` - 对象存储区域
- `COS_BUCKET` - 对象存储桶名称
- `TENCENT_CLOUD_SECRET_ID` - 腾讯云 API 密钥 ID
- `TENCENT_CLOUD_SECRET_KEY` - 腾讯云 API 密钥

**短信服务配置**
- `SMS_SDK_APP_ID` - 短信应用 ID
- `SMS_REGION` - 短信服务区域
- `SMS_SIGN_NAME` - 短信签名

**其他配置**
- `SECRET_KEY` - 应用密钥
- `TCR_USERNAME` - 容器镜像仓库用户名
- `TCR_PASSWORD` - 容器镜像仓库密码

#### 4. 部署技术栈
- **容器化**: Docker
- **编排工具**: Kubernetes
- **包管理**: Helm
- **镜像仓库**: 腾讯云容器镜像服务（TCR）
- **CI/CD**: GitHub Actions

### 部署监控
- 部署过程中会验证 Kubernetes 集群连接
- 使用 Helm 进行应用的安装和升级
- 支持回滚和版本管理
