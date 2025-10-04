#!/bin/bash
# FastAPI服务启动脚本

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

# 等待数据库就绪
wait_for_database() {
    log_info "等待数据库连接就绪..."
    
    if [ -n "$DATABASE_HOST" ] && [ -n "$DATABASE_PORT" ]; then
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if nc -z "$DATABASE_HOST" "$DATABASE_PORT" 2>/dev/null; then
                log_success "数据库连接成功！"
                return 0
            fi
            
            log_info "尝试连接数据库 ($attempt/$max_attempts)..."
            sleep 2
            attempt=$((attempt + 1))
        done
        
        log_error "数据库连接失败，超时退出"
        exit 1
    else
        log_warning "未配置数据库连接信息，跳过等待"
    fi
}

# 等待Redis就绪
wait_for_redis() {
    log_info "等待Redis连接就绪..."
    
    if [ -n "$REDIS_HOST" ] && [ -n "$REDIS_PORT" ]; then
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
                log_success "Redis连接成功！"
                return 0
            fi
            
            log_info "尝试连接Redis ($attempt/$max_attempts)..."
            sleep 2
            attempt=$((attempt + 1))
        done
        
        log_error "Redis连接失败，超时退出"
        exit 1
    else
        log_warning "未配置Redis连接信息，跳过等待"
    fi
}

# 数据库迁移
run_migrations() {
    log_info "执行数据库迁移..."
    
    if [ -f "alembic.ini" ]; then
        if alembic current >/dev/null 2>&1; then
            log_info "执行数据库升级..."
            alembic upgrade head
            log_success "数据库迁移完成！"
        else
            log_warning "Alembic配置未初始化，跳过迁移"
        fi
    else
        log_warning "未找到alembic.ini，跳过数据库迁移"
    fi
}

# 初始化数据
init_data() {
    log_info "初始化基础数据..."
    
    if [ -f "scripts/init_data.py" ]; then
        python scripts/init_data.py
        log_success "基础数据初始化完成！"
    else
        log_info "未找到初始化脚本，跳过数据初始化"
    fi
}

# 启动前检查
prestart_checks() {
    log_info "执行启动前检查..."
    
    # 检查必要的环境变量
    local required_vars=("DATABASE_URL")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "缺少必要的环境变量: ${missing_vars[*]}"
        exit 1
    fi
    
    # 检查文件权限
    if [ ! -w "/app/logs" ]; then
        log_warning "日志目录不可写，尝试修复权限"
        mkdir -p /app/logs
    fi
    
    log_success "启动前检查通过！"
}

# 启动服务
start_service() {
    log_info "启动FastAPI服务..."
    
    # 设置默认参数
    export HOST=${HOST:-"0.0.0.0"}
    export PORT=${PORT:-8000}
    export WORKERS=${WORKERS:-4}
    export LOG_LEVEL=${LOG_LEVEL:-"info"}
    
    log_info "服务配置:"
    log_info "  - Host: $HOST"
    log_info "  - Port: $PORT"
    log_info "  - Workers: $WORKERS"
    log_info "  - Log Level: $LOG_LEVEL"
    
    # 如果是开发环境，启用热重载
    if [ "$ENVIRONMENT" = "development" ]; then
        log_info "开发模式：启用热重载"
        exec uvicorn main:app \
            --host "$HOST" \
            --port "$PORT" \
            --reload \
            --log-level "$LOG_LEVEL"
    else
        log_info "生产模式：多进程启动"
        exec uvicorn main:app \
            --host "$HOST" \
            --port "$PORT" \
            --workers "$WORKERS" \
            --log-level "$LOG_LEVEL" \
            --access-log \
            --use-colors
    fi
}

# 主函数
main() {
    log_info "======================================"
    log_info "🚀 鉴宝后端服务启动中..."
    log_info "======================================"
    
    # 如果传入的是自定义命令，直接执行
    if [ "$1" != "uvicorn" ] && [ -n "$1" ]; then
        log_info "执行自定义命令: $*"
        exec "$@"
        return
    fi
    
    prestart_checks
    wait_for_database
    wait_for_redis
    run_migrations
    init_data
    start_service
}

# 信号处理
trap 'log_info "收到终止信号，正在优雅关闭..."; exit 0' SIGTERM SIGINT

# 执行主函数
main "$@"