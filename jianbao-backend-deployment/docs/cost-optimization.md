# 按量付费成本优化指南

## 💰 按量付费模式优势

### 1. 灵活性
- ✅ 随用随付，无需预付费
- ✅ 可随时调整配置
- ✅ 支持自动启停节省成本
- ✅ 适合开发测试环境

### 2. 成本控制
- 📊 实时费用监控
- ⏰ 定时启停功能
- 🚨 费用告警设置
- 📈 按需扩缩容

## 🕐 不同使用场景成本对比

### 开发环境（推荐配置）
```yaml
运行时间: 工作日 9:00-22:00 (13小时/天)
月运行时长: 13小时 × 22工作日 = 286小时
月成本: 约420元
节省: 比24小时运行节省640元/月
```

### 测试环境（推荐配置）
```yaml
运行时间: 工作日 8:00-18:00 (10小时/天)
月运行时长: 10小时 × 22工作日 = 220小时
月成本: 约320元
节省: 比24小时运行节省740元/月
```

### 生产环境
```yaml
运行时间: 24小时/天 × 30天 = 720小时
月成本: 约1060元
说明: 生产环境需要持续运行
```

## 🛠️ 成本优化实践

### 1. 环境分离策略

#### 开发环境
```bash
# 创建开发环境（低配置）
kubectl create namespace jianbao-dev

# 部署低配置版本
sed 's/memory: "256Mi"/memory: "128Mi"/g' k8s/deployment.yaml | \
sed 's/cpu: "200m"/cpu: "100m"/g' | \
sed 's/replicas: 2/replicas: 1/g' | \
kubectl apply -f - -n jianbao-dev
```

#### 测试环境
```bash
# 创建测试环境（中等配置）
kubectl create namespace jianbao-test

# 使用标准配置
kubectl apply -f k8s/ -n jianbao-test
```

### 2. 自动化成本控制

#### 安装成本控制脚本
```bash
# 设置执行权限
chmod +x scripts/cost-control.sh

# 查看开发环境状态
./scripts/cost-control.sh status dev

# 设置开发环境定时启停
./scripts/cost-control.sh schedule dev

# 手动停止测试环境
./scripts/cost-control.sh stop test
```

#### 定时任务配置
```yaml
开发环境:
  启动: 工作日 09:00
  停止: 工作日 22:00
  周末: 完全停止
  
测试环境:
  启动: 工作日 08:00  
  停止: 工作日 18:00
  周末: 完全停止
  
生产环境:
  运行: 24/7 持续运行
  备份: 每日自动备份
```

### 3. 监控和告警设置

#### 费用告警配置
```bash
# 设置日费用告警（超过50元）
tccli billing CreateBudget \
  --BudgetName "jianbao-daily-limit" \
  --BudgetValue 50 \
  --TimeUnit "daily" \
  --AlertConfig.EmailAlerts true

# 设置月费用告警（超过800元）
tccli billing CreateBudget \
  --BudgetName "jianbao-monthly-limit" \
  --BudgetValue 800 \
  --TimeUnit "monthly"
```

#### 资源使用监控
```bash
# 查看实时资源使用
kubectl top nodes
kubectl top pods -n jianbao-system

# 查看费用趋势
./scripts/cost-control.sh cost
```

## 📊 成本优化效果

### 每月成本对比
| 环境 | 24小时运行 | 优化后 | 节省金额 | 节省比例 |
|------|------------|--------|----------|----------|
| **开发环境** | 1060元 | 420元 | 640元 | 60% |
| **测试环境** | 1060元 | 320元 | 740元 | 70% |
| **生产环境** | 1060元 | 1060元 | 0元 | 0% |
| **总计** | 3180元 | 1800元 | 1380元 | 43% |

### 年成本节省
- **传统方式**: 3180元 × 12个月 = 38160元
- **优化后**: 1800元 × 12个月 = 21600元
- **年节省**: 16560元（43%成本节省）

## 🎯 最佳实践建议

### 1. 环境规划
- **开发**: 1个Pod，低配置，工作时间运行
- **测试**: 1个Pod，标准配置，测试时运行
- **生产**: 2个Pod，高配置，24小时运行

### 2. 资源配置
```yaml
开发环境:
  CPU: 100m (0.1核)
  Memory: 128Mi
  Storage: 10GB
  
测试环境:
  CPU: 200m (0.2核)
  Memory: 256Mi
  Storage: 20GB
  
生产环境:
  CPU: 500m (0.5核)
  Memory: 512Mi
  Storage: 50GB
```

### 3. 监控策略
- 🔍 每日检查费用报告
- 📱 设置微信/邮件告警
- 📊 周度成本分析
- 🎯 月度优化调整

### 4. 应急预案
- 费用异常时立即停止非生产环境
- 生产环境异常时降级运行
- 定期备份重要数据
- 保留核心服务优先级

通过以上优化措施，可以在保证服务质量的前提下，大幅降低云计算成本！