# Python FastAPI 后端服务 Dockerfile
# 多阶段构建优化镜像大小和安全性

# ================================
# 构建阶段
# ================================
FROM python:3.11-slim AS builder

# 设置构建参数
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# ================================
# 生产阶段
# ================================
FROM python:3.11-slim AS production

# 设置标签
LABEL maintainer="jianbao-team" \
      version="${VERSION}" \
      description="鉴宝管理后台FastAPI后端服务" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# 创建应用目录和用户
WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# 从构建阶段复制Python依赖
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY --chown=appuser:appgroup . .

# 设置环境变量
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# JVM优化参数（如果使用Java组件）
ENV JAVA_OPTS="-Xms256m -Xmx512m -XX:+UseG1GC"

# 创建必要目录
RUN mkdir -p /app/logs /app/uploads /tmp/processing && \
    chown -R appuser:appgroup /app /tmp/processing

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动脚本
COPY --chown=appuser:appgroup docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# 启动命令
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]