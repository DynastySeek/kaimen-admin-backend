# 鉴宝管理后台 - Python后端服务部署方案

## 📋 项目概述
- **项目类型**: Python FastAPI后端服务
- **团队规模**: 20人以内
- **DAU**: 50人（管理后台）
- **核心功能**: 图片视频处理、业务API服务
- **技术栈**: Python FastAPI + SQLAlchemy + MySQL + Redis
- **部署频率**: 每周至少1次

## 🏗️ 后端服务架构

```
API网关 → 负载均衡 → FastAPI服务集群 → 数据库集群
    ↓         ↓           ↓              ↓
  限流     分发请求    业务逻辑处理    数据持久化
    ↓         ↓           ↓              ↓
CDN加速   健康检查    异步任务处理   Redis缓存
```

## 💰 成本预估（后端服务）

### 按量付费配置（灵活成本控制）

#### 💡 全天候运行（24小时/天）
| 服务组件 | 配置规格 | 按量价格 | 月成本(720小时) | 说明 |
|---------|---------|---------|---------------|------|
| **TKE节点** | 2节点×2C4G | 0.4元/小时/节点 | 576元 | FastAPI服务运行 |
| **MySQL** | 2C4G单节点 | 0.5元/小时 | 360元 | 业务数据存储 |
| **Redis** | 1G标准版 | 0.12元/小时 | 86元 | 缓存和会话 |
| **COS存储** | 50GB | 0.118元/GB/月 | 6元 | 文件存储 |
| **CLB负载均衡** | 标准版 | 0.02元/小时 | 14元 | 服务负载均衡 |
| **网络流量** | 按实际使用 | 约1元/GB | 20元 | 预估20GB/月 |
| **小计** | | | **1062元/月** | 全天候运行 |

#### 🕐 工作时间运行（12小时/天，仅工作日）
| 运行模式 | 月运行时长 | 月成本 | 节省 |
|---------|------------|-------|------|
| **开发环境** | 12小时/天 × 22工作日 = 264小时 | **390元** | 节省672元 |
| **测试环境** | 8小时/天 × 22工作日 = 176小时 | **260元** | 节省802元 |
| **生产环境** | 24小时/天 × 30天 = 720小时 | **1062元** | 按需运行 |

### 扩容配置（业务增长）
| 服务组件 | 配置规格 | 月成本 | 说明 |
|---------|---------|-------|------|
| **TKE集群** | 5节点×4C8G | 1200元 | 高并发支持 |
| **MySQL** | 4C8G双节点 | 380元 | 主从复制 |
| **Redis** | 2G集群版 | 120元 | 高可用缓存 |
| **其他组件** | 扩容配置 | 300元 | 监控、存储等 |
| **总计** | | **2000元/月** | |

## 🚀 核心特性

### 1. FastAPI后端服务
- **高性能**: 异步处理，支持高并发
- **自动文档**: Swagger UI自动生成API文档
- **类型安全**: Pydantic数据验证
- **易扩展**: 模块化架构设计

### 2. 图片视频处理能力
- **异步处理**: Celery + Redis队列
- **智能压缩**: PIL/OpenCV图片处理
- **视频转码**: FFmpeg视频处理
- **COS集成**: 自动上传腾讯云存储

### 3. 基础部署配置
- **固定副本**: 2个Pod实例保证基本可用性
- **滚动更新**: 零停机部署更新
- **资源限制**: 合理的资源配置避免浪费

### 4. 监控告警
- **服务监控**: API响应时间、错误率
- **资源监控**: CPU、内存、磁盘使用率
- **业务监控**: 文件处理成功率
- **告警通知**: 企业微信群通知

## 📂 项目结构

```
jianbao-backend-deployment/
├── README.md                    # 项目概述
├── .env.example                # 后端环境配置
├── .coding-ci.yml              # 🔥 CODING DevOps流水线配置
├── Dockerfile                  # FastAPI服务镜像
├── docker-entrypoint.sh        # 容器启动脚本
├── requirements.txt            # Python依赖
├── k8s/                        # Kubernetes配置
│   ├── deployment.yaml         # 后端服务部署
│   ├── service.yaml           # 服务暴露配置
│   └── configmap.yaml         # 配置管理
├── infrastructure/             # 基础设施
│   ├── secrets.yaml           # 密钥管理
│   └── ingress.yaml           # 负载均衡
├── scripts/                   # 部署脚本
│   ├── deploy-backend.sh      # 后端服务部署
│   └── cost-control.sh        # 成本控制
└── docs/                      # 部署文档
    ├── coding-devops-setup.md  # 🔥 CODING DevOps配置指南
    ├── cicd-options.md         # CI/CD服务对比
    └── cost-optimization.md    # 成本优化指南
```

## 🔧 技术栈详情

### 后端服务
- **Framework**: FastAPI 0.104+
- **ASGI Server**: Uvicorn
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Task Queue**: Celery + Redis
- **Cache**: Redis
- **Database**: MySQL 8.0

### 容器化
- **Container**: Docker
- **Orchestration**: Kubernetes (TKE)
- **Registry**: 腾讯云容器镜像服务 TCR
- **Storage**: 腾讯云对象存储 COS

### 监控运维
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: ELK Stack
- **Alerting**: AlertManager + 企业微信

## 🚀 部署方案选择

### 🎯 **方案一：GitHub Actions + ArgoCD（推荐）**

**现代化GitOps CI/CD流水线，替代即将下线的CODING DevOps：**

```bash
# 1. 快速部署ArgoCD
chmod +x scripts/deploy-argocd.sh
./scripts/deploy-argocd.sh

# 2. 配置Secrets和权限
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/serviceaccount.yaml

# 3. 创建ArgoCD应用
kubectl apply -f argocd/application.yaml
```

**🔥 核心优势：**
- ✅ **GitHub Actions**: 代码检查 → 构建镜像 → 推送TCR
- ✅ **ArgoCD**: 检测变更 → 自动部署 → 状态监控  
- ✅ **GitOps**: 声明式配置 + 自动同步
- ✅ **零停机**: 滚动更新 + 自动回滚
- ✅ **免费**: GitHub Actions免费额度 + ArgoCD开源

📖 **完整配置指南**: [GitHub Actions + ArgoCD 设置文档](docs/github-actions-argocd-setup.md)

---

### 🔧 **方案二：CODING DevOps（即将下线）**

⚠️ **重要提醒**: CODING DevOps将于2025年9月1日下线标准版，建议迁移到方案一。

### 1. 环境准备
```bash
# 配置后端环境变量
cp .env.example .env
vim .env  # 填入数据库、Redis、COS配置

# 确认按量付费模式
echo "BILLING_MODE=POSTPAID_BY_HOUR" >> .env
```

### 2. 配置CODING DevOps
```bash
# 运行配置向导（交互式）
chmod +x scripts/setup-coding.sh
./scripts/setup-coding.sh

# 或使用自动配置（非交互）
./scripts/setup-coding.sh --auto

# 访问CODING创建项目
# https://coding.net
# 按照生成的指南配置项目
```

### 3. 自动化部署
```bash
# 推送到develop分支 → 自动部署测试环境
git push origin develop

# 推送到main分支 → 自动部署生产环境  
git push origin main

# 在CODING查看构建过程和部署日志
```

### 4. 成本监控设置
```bash
# 设置费用告警（日费用超过50元时告警）
tccli billing CreateBudget \
  --BudgetName "jianbao-daily-budget" \
  --BudgetValue 50 \
  --TimeUnit "daily"
```

### 5. 验证和监控
```bash
# 检查服务状态
kubectl get pods -n jianbao-system
curl https://api.jianbao.com/health

# 查看当前费用
tccli billing DescribeBillSummaryByProduct --PayerUin your-uin
```

## 📊 服务监控

### 关键指标
- **API响应时间**: P95 < 200ms
- **服务可用性**: >99.9%
- **错误率**: <0.1%
- **处理吞吐量**: >1000 req/s
- **文件处理**: 图片<5s，视频<30s

### 监控面板
- **服务概览**: 请求量、响应时间、错误率
- **资源监控**: CPU、内存、磁盘使用
- **业务监控**: 用户活跃度、文件处理量
- **告警中心**: 实时告警状态和历史

通过以上配置，您的Python后端服务可以稳定支撑50 DAU的管理后台，并具备处理大规模图片视频的能力！