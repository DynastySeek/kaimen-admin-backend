#!/bin/bash
# GitHub Actions + ArgoCD GitOps 一键配置脚本
# 替代CODING DevOps的现代化CI/CD解决方案

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARGOCD_VERSION="v2.9.3"
NAMESPACE_APP="jianbao-system"
NAMESPACE_ARGOCD="argocd"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

# 显示帮助信息
show_help() {
    echo "GitHub Actions + ArgoCD GitOps 一键配置脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h        显示此帮助信息"
    echo "  --check-only      仅检查环境，不执行部署"
    echo "  --skip-argocd     跳过ArgoCD安装"
    echo "  --skip-app        跳过应用配置"
    echo "  --uninstall       卸载所有组件"
    echo "  --setup-secrets   交互式配置Secrets"
    echo ""
    echo "示例:"
    echo "  $0                    # 完整安装"
    echo "  $0 --check-only      # 仅检查环境"
    echo "  $0 --setup-secrets   # 配置密钥"
    echo ""
}

# 检查前置条件
check_prerequisites() {
    log_header "检查前置条件"
    
    local errors=0
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl 未安装，请先安装 kubectl"
        errors=$((errors + 1))
    else
        log_info "kubectl 已安装: $(kubectl version --client --short)"
    fi
    
    # 检查集群连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到 Kubernetes 集群，请检查 kubeconfig"
        errors=$((errors + 1))
    else
        log_info "Kubernetes 集群连接正常"
        kubectl cluster-info | head -1
    fi
    
    # 检查权限
    if ! kubectl auth can-i create namespace &> /dev/null; then
        log_error "当前用户没有创建 namespace 的权限"
        errors=$((errors + 1))
    else
        log_info "具备必要的 Kubernetes 权限"
    fi
    
    # 检查必要文件
    local required_files=(
        "$PROJECT_ROOT/.github/workflows/ci.yml"
        "$PROJECT_ROOT/argocd/application.yaml"
        "$PROJECT_ROOT/k8s/deployment.yaml"
        "$PROJECT_ROOT/k8s/secrets.yaml"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "缺少必要文件: ${file#$PROJECT_ROOT/}"
            errors=$((errors + 1))
        fi
    done
    
    if [[ $errors -gt 0 ]]; then
        log_error "检查到 $errors 个问题，请解决后重试"
        return 1
    fi
    
    log_success "前置条件检查通过！"
    return 0
}

# 交互式配置Secrets
setup_secrets_interactive() {
    log_header "交互式配置 Kubernetes Secrets"
    
    echo "请提供以下配置信息（按回车跳过使用示例值）:"
    echo ""
    
    # 数据库配置
    read -p "数据库连接URL (mysql://user:pass@host:3306/db): " DATABASE_URL
    DATABASE_URL=${DATABASE_URL:-"mysql://jianbao:password@mysql:3306/jianbao"}
    
    # Redis配置
    read -p "Redis连接URL (redis://host:6379/0): " REDIS_URL
    REDIS_URL=${REDIS_URL:-"redis://redis:6379/0"}
    
    # JWT密钥
    read -p "JWT密钥 (随机生成): " JWT_SECRET
    JWT_SECRET=${JWT_SECRET:-"$(openssl rand -base64 32)"}
    
    # 腾讯云COS配置
    read -p "腾讯云COS SecretId: " COS_SECRET_ID
    COS_SECRET_ID=${COS_SECRET_ID:-"AKIDxxxxxxxxxxxxxxxx"}
    
    read -p "腾讯云COS SecretKey: " COS_SECRET_KEY
    COS_SECRET_KEY=${COS_SECRET_KEY:-"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
    
    read -p "腾讯云COS Bucket: " COS_BUCKET
    COS_BUCKET=${COS_BUCKET:-"jianbao-bucket"}
    
    read -p "腾讯云COS Region: " COS_REGION
    COS_REGION=${COS_REGION:-"ap-guangzhou"}
    
    # 微信小程序配置
    read -p "微信小程序AppId: " WECHAT_APP_ID
    WECHAT_APP_ID=${WECHAT_APP_ID:-"wxXXXXXXXXXXXXXXXX"}
    
    read -p "微信小程序AppSecret: " WECHAT_APP_SECRET
    WECHAT_APP_SECRET=${WECHAT_APP_SECRET:-"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
    
    # GitHub配置
    read -p "GitHub Personal Access Token: " GITHUB_TOKEN
    GITHUB_TOKEN=${GITHUB_TOKEN:-"ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
    
    # 生成secrets.yaml
    log_step "生成 secrets.yaml 文件..."
    
    cat > "$PROJECT_ROOT/k8s/secrets-generated.yaml" << EOF
# 自动生成的 Kubernetes Secrets 配置
# 生成时间: $(date)

apiVersion: v1
kind: Secret
metadata:
  name: jianbao-secrets
  namespace: jianbao-system
  labels:
    app: jianbao-backend
type: Opaque
data:
  database-url: $(echo -n "$DATABASE_URL" | base64)
  redis-url: $(echo -n "$REDIS_URL" | base64)
  cos-secret-id: $(echo -n "$COS_SECRET_ID" | base64)
  cos-secret-key: $(echo -n "$COS_SECRET_KEY" | base64)
  cos-bucket: $(echo -n "$COS_BUCKET" | base64)
  cos-region: $(echo -n "$COS_REGION" | base64)
  jwt-secret: $(echo -n "$JWT_SECRET" | base64)
  wechat-app-id: $(echo -n "$WECHAT_APP_ID" | base64)
  wechat-app-secret: $(echo -n "$WECHAT_APP_SECRET" | base64)
  
---
apiVersion: v1
kind: Secret
metadata:
  name: github-token-secret
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
type: Opaque
stringData:
  type: git
  url: https://github.com/DynastySeek/kaimen-backend.git
  username: not-used
  password: $GITHUB_TOKEN
EOF

    log_success "已生成: k8s/secrets-generated.yaml"
    log_warn "请妥善保管此文件，不要提交到Git仓库！"
}

# 部署应用
deploy_complete_stack() {
    log_header "部署完整GitOps技术栈"
    
    # 1. 创建命名空间
    log_step "创建必要的命名空间..."
    kubectl create namespace $NAMESPACE_APP --dry-run=client -o yaml | kubectl apply -f -
    kubectl create namespace $NAMESPACE_ARGOCD --dry-run=client -o yaml | kubectl apply -f -
    
    # 2. 部署ArgoCD
    if [[ "${SKIP_ARGOCD:-false}" != "true" ]]; then
        log_step "部署ArgoCD..."
        if [[ -x "$SCRIPT_DIR/deploy-argocd.sh" ]]; then
            "$SCRIPT_DIR/deploy-argocd.sh" --skip-app
        else
            log_warn "ArgoCD部署脚本不存在，手动安装ArgoCD..."
            kubectl apply -n $NAMESPACE_ARGOCD -f https://raw.githubusercontent.com/argoproj/argo-cd/$ARGOCD_VERSION/manifests/install.yaml
        fi
    fi
    
    # 3. 应用RBAC和权限
    log_step "配置RBAC和服务权限..."
    kubectl apply -f "$PROJECT_ROOT/k8s/serviceaccount.yaml"
    
    # 4. 应用Secrets
    log_step "应用Kubernetes Secrets..."
    if [[ -f "$PROJECT_ROOT/k8s/secrets-generated.yaml" ]]; then
        kubectl apply -f "$PROJECT_ROOT/k8s/secrets-generated.yaml"
        log_info "已应用生成的secrets配置"
    else
        log_warn "未找到生成的secrets文件，请先运行: $0 --setup-secrets"
        log_warn "或手动编辑并应用: k8s/secrets.yaml"
    fi
    
    # 5. 应用ArgoCD配置
    if [[ "${SKIP_APP:-false}" != "true" ]]; then
        log_step "配置ArgoCD应用..."
        kubectl apply -f "$PROJECT_ROOT/argocd/application.yaml"
    fi
    
    # 6. 等待服务就绪
    log_step "等待服务启动..."
    if kubectl get namespace $NAMESPACE_ARGOCD &> /dev/null; then
        kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n $NAMESPACE_ARGOCD --timeout=300s || true
    fi
}

# 显示部署状态
show_status() {
    log_header "部署状态概览"
    
    echo "📋 ArgoCD 组件状态:"
    kubectl get pods -n $NAMESPACE_ARGOCD 2>/dev/null || echo "  ArgoCD未安装"
    echo ""
    
    echo "📋 应用状态:"
    kubectl get pods -n $NAMESPACE_APP 2>/dev/null || echo "  应用未部署"
    echo ""
    
    echo "📋 ArgoCD 应用:"
    kubectl get applications -n $NAMESPACE_ARGOCD 2>/dev/null || echo "  暂无应用"
    echo ""
    
    # 获取ArgoCD管理员密码
    if kubectl get secret argocd-initial-admin-secret -n $NAMESPACE_ARGOCD &> /dev/null; then
        ADMIN_PASSWORD=$(kubectl -n $NAMESPACE_ARGOCD get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d 2>/dev/null || echo "获取失败")
        echo "🔑 ArgoCD 登录信息:"
        echo "   用户名: admin"
        echo "   密码: $ADMIN_PASSWORD"
        echo "   访问: kubectl port-forward svc/argocd-server -n argocd 8080:443"
        echo "   URL: https://localhost:8080"
    fi
}

# 卸载所有组件
uninstall_all() {
    log_header "卸载 GitOps 技术栈"
    
    read -p "⚠️  确定要卸载所有组件吗? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "已取消卸载操作"
        return 0
    fi
    
    log_step "删除ArgoCD应用..."
    kubectl delete applications --all -n $NAMESPACE_ARGOCD 2>/dev/null || true
    
    log_step "删除应用组件..."
    kubectl delete namespace $NAMESPACE_APP 2>/dev/null || true
    
    log_step "卸载ArgoCD..."
    kubectl delete -n $NAMESPACE_ARGOCD -f https://raw.githubusercontent.com/argoproj/argo-cd/$ARGOCD_VERSION/manifests/install.yaml 2>/dev/null || true
    kubectl delete namespace $NAMESPACE_ARGOCD 2>/dev/null || true
    
    log_success "卸载完成"
}

# 主函数
main() {
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --check-only)
                CHECK_ONLY=true
                shift
                ;;
            --skip-argocd)
                SKIP_ARGOCD=true
                shift
                ;;
            --skip-app)
                SKIP_APP=true
                shift
                ;;
            --uninstall)
                uninstall_all
                exit 0
                ;;
            --setup-secrets)
                setup_secrets_interactive
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示欢迎信息
    log_header "GitHub Actions + ArgoCD GitOps 配置"
    echo "替代CODING DevOps的现代化CI/CD解决方案"
    echo ""
    
    # 检查前置条件
    if ! check_prerequisites; then
        exit 1
    fi
    
    # 仅检查模式
    if [[ "${CHECK_ONLY:-false}" == "true" ]]; then
        log_success "环境检查完成，可以进行部署！"
        exit 0
    fi
    
    # 执行部署
    deploy_complete_stack
    
    # 显示状态
    show_status
    
    # 完成提示
    log_header "🎉 GitOps 配置完成！"
    echo ""
    echo "下一步操作:"
    echo "1. 配置GitHub Actions Secrets (TCR_USERNAME, TCR_PASSWORD)"
    echo "2. 访问ArgoCD UI并验证应用同步状态"
    echo "3. 推送代码到main分支触发CI/CD流水线"
    echo "4. 在ArgoCD中监控部署状态"
    echo ""
    echo "📖 详细文档: docs/github-actions-argocd-setup.md"
    echo ""
    log_success "现代化CI/CD流水线已就绪！🚀"
}

# 执行主函数
main "$@"