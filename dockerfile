# Dockerfile
FROM python:3.11-slim

# 避免生成 .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


# 复制依赖并安装
COPY jianbao-backend-deployment/backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制整个 backend 包到 /app/backend/
COPY jianbao-backend-deployment/backend/ ./backend/

# 可改为 uvicorn 的命令行参数或使用 gunicorn + uvicorn workers
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--workers", "1"]

