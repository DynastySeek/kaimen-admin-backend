# 开门管理后台

基于 FastAPI 构建的现代化管理后台系统。

## 项目特性

- 🚀 **FastAPI**: 高性能的现代 Python Web 框架
- 🔐 **JWT 认证**: 安全的用户认证和授权
- ☁️ **云数据库**: 支持腾讯云等云数据库服务
- 📝 **Pydantic**: 数据验证和序列化
- 📖 **自动文档**: 自动生成 API 文档
- 🛡️ **异常处理**: 统一的错误处理机制
- 📦 **模块化设计**: 清晰的项目结构

## 项目结构

```
kaimen-admin-backend/
├── app/                    # 应用主目录
│   ├── api/               # API 路由
│   │   ├── deps.py        # 依赖注入
│   │   ├── router.py      # 主路由
│   │   └── endpoints/     # 端点模块
│   ├── config/            # 配置模块
│   │   └── env.py         # 环境配置
│   ├── constants/         # 常量和枚举
│   │   ├── constants.py   # 应用常量
│   │   ├── enums.py       # 枚举定义
│   │   └── status_codes.py # 状态码
│   ├── core/              # 核心功能
│   │   ├── dependencies.py # 依赖注入
│   │   ├── exceptions.py  # 异常处理
│   │   ├── middleware.py  # 中间件
│   │   └── response.py    # 响应格式
│   ├── models/            # 数据模型
│   │   ├── base.py        # 基础模型
│   │   └── user.py        # 用户模型
│   ├── schemas/           # Pydantic 模式
│   │   ├── base.py        # 基础模式
│   │   ├── response.py    # 响应模式
│   │   └── user.py        # 用户模式
│   ├── services/          # 业务逻辑层
│   │   ├── auth_service.py # 认证服务
│   │   └── user_service.py # 用户服务
│   └── utils/             # 工具函数
│       ├── db.py          # 数据库配置
│       ├── helpers.py     # 通用工具
│       └── security.py    # 安全工具
├── main.py                # 应用入口
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量示例
├── .env.test             # 测试环境配置
├── .env.prod             # 生产环境配置
└── README.md             # 项目说明
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

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑环境变量文件，配置云数据库等信息
vim .env
```

**注意**: 本项目已移除本地PostgreSQL配置，请使用腾讯云等云数据库服务。

### 4. 启动应用

```bash
# 开发模式启动
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问应用

- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 开发指南

### 环境配置

项目支持多环境配置：

- **开发环境**: `.env` 或 `.env.development`
- **测试环境**: `.env.test`
- **生产环境**: `.env.prod`

通过设置 `ENVIRONMENT` 环境变量来切换环境。

### API 开发

1. 在 `app/models/` 中定义数据模型
2. 在 `app/schemas/` 中定义 Pydantic 模式
3. 在 `app/services/` 中实现业务逻辑
4. 在 `app/api/endpoints/` 中创建 API 端点
5. 在 `app/api/router.py` 中注册路由

### 代码规范

- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 flake8 进行代码检查
- 使用 mypy 进行类型检查

```bash
# 代码格式化
black .

# 导入排序
isort .

# 代码检查
flake8 .

# 类型检查
mypy .
```

## 部署

### Docker 部署

```dockerfile
# Dockerfile 示例
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 生产环境注意事项

1. 设置强密钥 (`SECRET_KEY`)
2. 配置正确的云数据库连接
3. 设置合适的 CORS 域名
4. 关闭调试模式 (`DEBUG=false`)
5. 配置日志记录
6. 设置反向代理 (Nginx)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！