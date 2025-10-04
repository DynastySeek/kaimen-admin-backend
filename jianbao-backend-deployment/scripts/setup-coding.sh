#!/bin/bash
# 腾讯云CODING DevOps 快速配置脚本

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

# 显示欢迎信息
show_welcome() {
    echo "==========================================="
    echo "🚀 腾讯云CODING DevOps 快速配置向导"
    echo "==========================================="
    echo "本脚本将帮助您快速配置CODING DevOps环境"
    echo ""
}

# 检查必要工具
check_prerequisites() {
    log_info "检查必要工具..."
    
    local missing_tools=()
    
    # 检查git
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi
    
    # 检查curl
    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必要工具: ${missing_tools[*]}"
        log_error "请先安装必要的工具"
        exit 1
    fi
    
    log_success "工具检查通过"
}

# 收集配置信息
collect_config() {
    log_info "收集配置信息..."
    
    echo "请提供以下信息（按Enter跳过使用默认值）："
    echo ""
    
    # CODING团队信息
    read -p "🏢 CODING团队名称 (如: my-team): " CODING_TEAM
    CODING_TEAM=${CODING_TEAM:-"my-team"}
    
    read -p "📦 项目名称 (默认: jianbao-backend): " PROJECT_NAME
    PROJECT_NAME=${PROJECT_NAME:-"jianbao-backend"}
    
    # 腾讯云配置
    read -p "🌏 腾讯云地域 (默认: ap-beijing): " TKE_REGION
    TKE_REGION=${TKE_REGION:-"ap-beijing"}
    
    read -p "📦 TCR命名空间 (默认: jianbao): " TCR_NAMESPACE
    TCR_NAMESPACE=${TCR_NAMESPACE:-"jianbao"}
    
    # 环境配置
    read -p "🏭 生产环境命名空间 (默认: jianbao-system): " PROD_NAMESPACE
    PROD_NAMESPACE=${PROD_NAMESPACE:-"jianbao-system"}
    
    read -p "🧪 测试环境命名空间 (默认: jianbao-staging): " STAGING_NAMESPACE
    STAGING_NAMESPACE=${STAGING_NAMESPACE:-"jianbao-staging"}
    
    # 通知配置
    read -p "📱 企业微信Webhook URL (可选): " WECHAT_WEBHOOK_URL
    
    echo ""
    log_info "配置信息收集完成"
}

# 生成配置文件
generate_config() {
    log_info "生成配置文件..."
    
    # 创建CODING项目配置
    cat > .coding-project.json << EOF
{
  "team": "${CODING_TEAM}",
  "project": "${PROJECT_NAME}",
  "description": "鉴宝管理后台后端服务",
  "template": "DevOps项目",
  "repository": {
    "name": "backend",
    "description": "Python FastAPI后端服务",
    "visibility": "private"
  },
  "ci": {
    "name": "后端服务CI/CD",
    "config_file": ".coding-ci.yml",
    "auto_trigger": true
  }
}
EOF
    
    # 更新.coding-ci.yml中的变量
    if [ -f ".coding-ci.yml" ]; then
        # 备份原文件
        cp .coding-ci.yml .coding-ci.yml.backup
        
        # 替换配置变量
        sed -i "s/TCR_NAMESPACE: \"jianbao\"/TCR_NAMESPACE: \"${TCR_NAMESPACE}\"/g" .coding-ci.yml
        sed -i "s/TKE_REGION: \"ap-beijing\"/TKE_REGION: \"${TKE_REGION}\"/g" .coding-ci.yml
        sed -i "s/PROD_NAMESPACE: \"jianbao-system\"/PROD_NAMESPACE: \"${PROD_NAMESPACE}\"/g" .coding-ci.yml
        sed -i "s/STAGING_NAMESPACE: \"jianbao-staging\"/STAGING_NAMESPACE: \"${STAGING_NAMESPACE}\"/g" .coding-ci.yml
    fi
    
    # 生成环境变量配置文件
    cat > .coding-env-vars.txt << EOF
# 复制以下环境变量到CODING构建计划中
# 路径: 持续集成 → 构建计划 → 设置 → 环境变量

# 基础配置
TCR_REGISTRY=ccr.ccs.tencentyun.com
TCR_NAMESPACE=${TCR_NAMESPACE}
IMAGE_NAME=backend
TKE_REGION=${TKE_REGION}

# 环境配置
PROD_NAMESPACE=${PROD_NAMESPACE}
STAGING_NAMESPACE=${STAGING_NAMESPACE}
DEPLOYMENT_NAME=jianbao-backend

# 通知配置（可选）
WECHAT_WEBHOOK_URL=${WECHAT_WEBHOOK_URL}
EOF
    
    log_success "配置文件生成完成"
}

# 显示配置指南
show_setup_guide() {
    log_info "显示详细配置指南..."
    
    echo ""
    echo "==========================================="
    echo "📋 CODING DevOps 配置步骤"
    echo "==========================================="
    echo ""
    
    echo "🔧 步骤1：创建CODING项目"
    echo "   1. 访问 https://coding.net"
    echo "   2. 登录/注册账号（推荐使用腾讯云账号）"
    echo "   3. 创建团队: ${CODING_TEAM}"
    echo "   4. 创建项目: ${PROJECT_NAME}"
    echo "   5. 选择 'DevOps项目' 模板"
    echo ""
    
    echo "📦 步骤2：导入代码仓库"
    echo "   1. 进入项目 → 代码仓库"
    echo "   2. 选择 '导入外部仓库'"
    echo "   3. 填写GitHub仓库地址"
    echo "   或手动添加remote:"
    echo "   git remote add coding https://${CODING_TEAM}.coding.net/p/${PROJECT_NAME}/d/backend/git"
    echo "   git push coding main"
    echo ""
    
    echo "⚙️ 步骤3：配置构建计划"
    echo "   1. 进入 持续集成 → 构建计划"
    echo "   2. 点击 '创建构建计划'"
    echo "   3. 选择 '自定义构建过程'"
    echo "   4. 构建计划名称: 后端服务CI/CD"
    echo "   5. 代码源: 选择刚导入的仓库"
    echo "   6. 配置文件: .coding-ci.yml"
    echo ""
    
    echo "🔐 步骤4：配置环境变量"
    echo "   复制文件 .coding-env-vars.txt 中的内容到:"
    echo "   构建计划 → 设置 → 环境变量"
    echo ""
    
    echo "☁️ 步骤5：配置腾讯云集成"
    echo "   1. 项目设置 → 开发者选项 → 腾讯云账号绑定"
    echo "   2. 绑定您的腾讯云账号"
    echo "   3. 配置TCR访问权限"
    echo "   4. 配置TKE集群访问权限"
    echo ""
    
    echo "🚀 步骤6：测试部署"
    echo "   1. 推送代码到develop分支测试:"
    echo "      git push origin develop"
    echo "   2. 在CODING查看构建过程和日志"
    echo "   3. 验证测试环境部署:"
    echo "      curl https://api-staging.jianbao.com/health"
    echo "   4. 推送到main分支部署生产环境:"
    echo "      git push origin main"
    echo ""
    
    echo "📚 步骤7：查看详细文档"
    echo "   详细配置说明请查看: docs/coding-devops-setup.md"
    echo ""
    
    log_success "配置指南显示完成！"
}

# 清理临时文件
cleanup() {
    log_info "清理临时文件..."
    # 如果需要，可以在这里清理临时文件
}

# 主函数
main() {
    show_welcome
    check_prerequisites
    collect_config
    generate_config
    show_setup_guide
    cleanup
    
    echo ""
    echo "==========================================="
    log_success "🎉 CODING DevOps配置向导完成！"
    echo "==========================================="
    echo ""
    echo "📁 生成的文件:"
    echo "   - .coding-project.json    (项目配置信息)"
    echo "   - .coding-env-vars.txt    (环境变量配置)"
    echo "   - .coding-ci.yml         (CI/CD流水线配置)"
    echo ""
    echo "🚀 下一步:"
    echo "   1. 按照上述步骤在CODING创建项目"
    echo "   2. 配置环境变量和腾讯云集成"
    echo "   3. 推送代码测试部署"
    echo ""
    echo "📚 详细文档: docs/coding-devops-setup.md"
    echo ""
}

# 脚本入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo "  --auto         使用默认配置（非交互模式）"
    echo ""
    echo "描述:"
    echo "  快速配置CODING DevOps环境的交互式脚本"
    echo "  生成必要的配置文件并提供详细的设置指南"
    exit 0
fi

# 非交互模式
if [ "$1" = "--auto" ]; then
    CODING_TEAM="my-team"
    PROJECT_NAME="jianbao-backend"
    TKE_REGION="ap-beijing"
    TCR_NAMESPACE="jianbao"
    PROD_NAMESPACE="jianbao-system"
    STAGING_NAMESPACE="jianbao-staging"
    WECHAT_WEBHOOK_URL=""
    
    show_welcome
    check_prerequisites
    generate_config
    show_setup_guide
    cleanup
    
    log_success "🎉 自动配置完成！"
    exit 0
fi

# 执行主函数
main