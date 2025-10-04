#!/bin/bash
# 按量付费成本控制脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 脚本参数
ACTION=${1:-status}  # status, start, stop, schedule
ENVIRONMENT=${2:-dev}  # dev, test, prod

# 环境配置
case $ENVIRONMENT in
    "dev")
        NAMESPACE="jianbao-dev"
        SCHEDULE_START="09:00"  # 开发环境9点启动
        SCHEDULE_STOP="22:00"   # 开发环境22点关闭
        ;;
    "test")
        NAMESPACE="jianbao-test"
        SCHEDULE_START="08:00"  # 测试环境8点启动
        SCHEDULE_STOP="18:00"   # 测试环境18点关闭
        ;;
    "prod")
        NAMESPACE="jianbao-system"
        SCHEDULE_START="00:00"  # 生产环境24小时运行
        SCHEDULE_STOP="23:59"
        ;;
    *)
        log_error "未知环境: $ENVIRONMENT (支持: dev, test, prod)"
        exit 1
        ;;
esac

# 检查当前费用
check_cost() {
    log_info "检查当前费用..."
    
    # 获取今日费用（需要配置腾讯云CLI）
    if command -v tccli &> /dev/null; then
        TODAY=$(date +"%Y-%m-%d")
        COST=$(tccli billing DescribeBillSummaryByProduct \
            --BeginTime "$TODAY" \
            --EndTime "$TODAY" 2>/dev/null | jq -r '.Response.SummaryTotal.RealTotalCost // "0"' || echo "0")
        
        log_info "今日费用: ${COST}元"
        
        # 费用告警
        if (( $(echo "$COST > 100" | bc -l 2>/dev/null || echo 0) )); then
            log_warning "⚠️ 今日费用较高: ${COST}元，请检查资源使用情况"
        fi
    else
        log_warning "未安装tccli，无法检查费用"
    fi
}

# 启动环境
start_environment() {
    log_info "启动 $ENVIRONMENT 环境..."
    
    # 扩容应用
    kubectl scale deployment jianbao-backend --replicas=2 -n $NAMESPACE 2>/dev/null || {
        log_warning "未找到deployment，可能环境未部署"
        return
    }
    
    # 等待Pod就绪
    kubectl wait --for=condition=ready pod -l app=jianbao-backend -n $NAMESPACE --timeout=300s
    
    log_success "$ENVIRONMENT 环境启动完成"
    
    # 显示状态
    kubectl get pods -n $NAMESPACE
}

# 停止环境
stop_environment() {
    log_info "停止 $ENVIRONMENT 环境..."
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        log_error "🚫 不能停止生产环境！"
        exit 1
    fi
    
    # 缩容到0
    kubectl scale deployment jianbao-backend --replicas=0 -n $NAMESPACE 2>/dev/null || {
        log_warning "未找到deployment"
        return
    }
    
    log_success "$ENVIRONMENT 环境已停止"
}

# 查看环境状态
show_status() {
    log_info "查看 $ENVIRONMENT 环境状态..."
    
    echo "==========================================" 
    echo "📊 环境状态: $ENVIRONMENT"
    echo "=========================================="
    
    # 检查命名空间
    if kubectl get namespace $NAMESPACE &>/dev/null; then
        echo "✅ 命名空间: $NAMESPACE (存在)"
        
        # 检查Pod状态
        POD_COUNT=$(kubectl get pods -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
        RUNNING_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)
        
        echo "📦 Pod数量: $RUNNING_PODS/$POD_COUNT (运行中/总数)"
        
        if [ $RUNNING_PODS -gt 0 ]; then
            echo "🟢 环境状态: 运行中"
            kubectl get pods -n $NAMESPACE
        else
            echo "🔴 环境状态: 已停止"
        fi
        
        # 检查服务
        SERVICE_COUNT=$(kubectl get svc -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
        echo "🌐 服务数量: $SERVICE_COUNT"
        
    else
        echo "❌ 命名空间: $NAMESPACE (不存在)"
    fi
    
    echo "=========================================="
    
    # 检查费用
    check_cost
}

# 设置定时任务
setup_schedule() {
    log_info "设置 $ENVIRONMENT 环境定时任务..."
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        log_warning "生产环境不设置定时关机"
        return
    fi
    
    # 创建启动和停止的CronJob
    cat > /tmp/cost-control-cronjob.yaml << EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: start-${ENVIRONMENT}-env
  namespace: $NAMESPACE
spec:
  schedule: "0 $(echo $SCHEDULE_START | cut -d: -f2) $(echo $SCHEDULE_START | cut -d: -f1) * * 1-5"  # 工作日启动
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: kubectl
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - kubectl scale deployment jianbao-backend --replicas=2 -n $NAMESPACE
          restartPolicy: OnFailure
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: stop-${ENVIRONMENT}-env
  namespace: $NAMESPACE
spec:
  schedule: "0 $(echo $SCHEDULE_STOP | cut -d: -f2) $(echo $SCHEDULE_STOP | cut -d: -f1) * * 1-5"  # 工作日停止
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: kubectl
            image: bitnami/kubectl:latest
            command:
            - /bin/sh
            - -c
            - kubectl scale deployment jianbao-backend --replicas=0 -n $NAMESPACE
          restartPolicy: OnFailure
EOF
    
    # 应用CronJob
    kubectl apply -f /tmp/cost-control-cronjob.yaml
    
    log_success "定时任务设置完成:"
    log_info "  - 启动时间: $SCHEDULE_START (工作日)"
    log_info "  - 停止时间: $SCHEDULE_STOP (工作日)"
    
    # 清理临时文件
    rm -f /tmp/cost-control-cronjob.yaml
}

# 显示使用帮助
show_help() {
    echo "用法: $0 <action> [environment]"
    echo ""
    echo "Actions:"
    echo "  status     查看环境状态和费用"
    echo "  start      启动环境"
    echo "  stop       停止环境（不支持生产环境）"
    echo "  schedule   设置定时启停"
    echo "  cost       仅查看费用"
    echo "  help       显示帮助"
    echo ""
    echo "Environments:"
    echo "  dev        开发环境 (默认)"
    echo "  test       测试环境"
    echo "  prod       生产环境"
    echo ""
    echo "示例:"
    echo "  $0 status dev          # 查看开发环境状态"
    echo "  $0 start test          # 启动测试环境"
    echo "  $0 stop dev            # 停止开发环境"
    echo "  $0 schedule test       # 设置测试环境定时启停"
    echo "  $0 cost                # 查看当前费用"
}

# 主函数
main() {
    case $ACTION in
        "status")
            show_status
            ;;
        "start")
            start_environment
            ;;
        "stop")
            stop_environment
            ;;
        "schedule")
            setup_schedule
            ;;
        "cost")
            check_cost
            ;;
        "help")
            show_help
            ;;
        *)
            log_error "未知操作: $ACTION"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main