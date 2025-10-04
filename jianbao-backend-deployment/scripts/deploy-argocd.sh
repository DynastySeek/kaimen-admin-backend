#!/bin/bash
# ArgoCD 自动化部署脚本
# 在TKE集群中安装和配置ArgoCD

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARGOCD_VERSION="v2.9.3"
NAMESPACE="argocd"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查前置条件
check_prerequisites() {
    log_step "检查前置条件..."
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl未安装，请先安装kubectl"
        exit 1
    fi
    
    # 检查集群连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群，请检查kubeconfig"
        exit 1
    fi
    
    # 检查权限
    if ! kubectl auth can-i create namespace &> /dev/null; then
        log_error "当前用户没有创建namespace的权限"
        exit 1
    fi
    
    log_info "前置条件检查通过 ✓"
}

# 创建命名空间
create_namespace() {
    log_step "创建ArgoCD命名空间..."
    
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warn "命名空间 $NAMESPACE 已存在，跳过创建"
    else
        kubectl create namespace $NAMESPACE
        log_info "命名空间 $NAMESPACE 创建成功 ✓"
    fi
}

# 安装ArgoCD
install_argocd() {
    log_step "安装ArgoCD $ARGOCD_VERSION..."
    
    # 下载并应用ArgoCD manifests
    kubectl apply -n $NAMESPACE -f https://raw.githubusercontent.com/argoproj/argo-cd/$ARGOCD_VERSION/manifests/install.yaml
    
    log_info "ArgoCD核心组件已安装 ✓"
}

# 应用自定义配置
apply_custom_configs() {
    log_step "应用自定义配置..."
    
    # 应用ArgoCD配置
    if [[ -f "$PROJECT_ROOT/argocd/install.yaml" ]]; then
        kubectl apply -f "$PROJECT_ROOT/argocd/install.yaml"
        log_info "ArgoCD自定义配置已应用 ✓"
    fi
    
    # 创建secrets（如果存在）
    if [[ -f "$PROJECT_ROOT/k8s/secrets.yaml" ]]; then
        log_warn "检测到secrets.yaml文件，请手动检查并应用敏感信息"
        log_warn "建议使用: kubectl apply -f k8s/secrets.yaml"
    fi
}

# 等待ArgoCD启动
wait_for_argocd() {
    log_step "等待ArgoCD服务启动..."
    
    # 等待所有pod就绪
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-application-controller -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-repo-server -n $NAMESPACE --timeout=300s
    
    log_info "ArgoCD服务启动完成 ✓"
}

# 获取管理员密码
get_admin_password() {
    log_step "获取ArgoCD管理员密码..."
    
    # 等待secret创建
    while ! kubectl get secret argocd-initial-admin-secret -n $NAMESPACE &> /dev/null; do
        log_info "等待管理员secret创建..."
        sleep 5
    done
    
    # 获取密码
    ADMIN_PASSWORD=$(kubectl -n $NAMESPACE get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
    
    echo ""
    echo "========================================"
    echo "ArgoCD 管理员登录信息:"
    echo "用户名: admin"
    echo "密码: $ADMIN_PASSWORD"
    echo "========================================"
    echo ""
}

# 配置端口转发
setup_port_forward() {
    log_step "设置端口转发..."
    
    echo "要访问ArgoCD UI，请运行以下命令:"
    echo "kubectl port-forward svc/argocd-server -n $NAMESPACE 8080:443"
    echo "然后访问: https://localhost:8080"
    echo ""
    
    read -p "是否现在启动端口转发? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "启动端口转发..."
        kubectl port-forward svc/argocd-server -n $NAMESPACE 8080:443
    fi
}

# 部署应用
deploy_application() {
    log_step "部署ArgoCD应用配置..."
    
    if [[ -f "$PROJECT_ROOT/argocd/application.yaml" ]]; then
        kubectl apply -f "$PROJECT_ROOT/argocd/application.yaml"
        log_info "ArgoCD应用配置已部署 ✓"
        
        echo ""
        echo "应用部署状态:"
        kubectl get applications -n $NAMESPACE
    else
        log_warn "未找到应用配置文件: argocd/application.yaml"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_step "显示部署信息..."
    
    echo ""
    echo "=== ArgoCD 组件状态 ==="
    kubectl get pods -n $NAMESPACE
    echo ""
    
    echo "=== ArgoCD 服务状态 ==="
    kubectl get svc -n $NAMESPACE
    echo ""
    
    echo "=== ArgoCD 应用状态 ==="
    kubectl get applications -n $NAMESPACE 2>/dev/null || echo "暂无应用"
    echo ""
}

# 清理函数
cleanup() {
    if [[ "${1:-}" == "--uninstall" ]]; then
        log_step "卸载ArgoCD..."
        kubectl delete -n $NAMESPACE -f https://raw.githubusercontent.com/argoproj/argo-cd/$ARGOCD_VERSION/manifests/install.yaml || true
        kubectl delete namespace $NAMESPACE || true
        log_info "ArgoCD已卸载"
        exit 0
    fi
}

# 主函数
main() {
    echo "🚀 ArgoCD 自动化部署脚本"
    echo "==============================="
    echo ""
    
    # 处理参数
    if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --help, -h     显示帮助信息"
        echo "  --uninstall    卸载ArgoCD"
        echo "  --skip-app     跳过应用部署"
        echo ""
        exit 0
    fi
    
    cleanup "$@"
    
    # 执行部署步骤
    check_prerequisites
    create_namespace
    install_argocd
    apply_custom_configs
    wait_for_argocd
    get_admin_password
    
    # 部署应用（除非跳过）
    if [[ "${1:-}" != "--skip-app" ]]; then
        deploy_application
    fi
    
    show_deployment_info
    setup_port_forward
    
    log_info "ArgoCD部署完成! 🎉"
    echo ""
    echo "下一步:"
    echo "1. 访问ArgoCD UI并登录"
    echo "2. 配置Git仓库连接"
    echo "3. 同步应用部署"
    echo "4. 配置GitHub Actions的部署密钥"
}

# 脚本入口
main "$@"