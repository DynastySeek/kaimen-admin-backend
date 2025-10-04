#!/bin/bash
# 简化版部署脚本

set -e

echo "🚀 部署简化版 FastAPI 服务..."

# 创建命名空间
echo "📦 创建命名空间..."
kubectl create namespace jianbao-system --dry-run=client -o yaml | kubectl apply -f -

# 应用配置文件
echo "⚙️ 应用配置文件..."
kubectl apply -f k8s/configmap-simple.yaml

# 部署应用
echo "🔨 部署应用..."
kubectl apply -f k8s/deployment-simple.yaml
kubectl apply -f k8s/service-simple.yaml

# 等待部署完成
echo "⏳ 等待部署完成..."
kubectl rollout status deployment/jianbao-backend -n jianbao-system --timeout=300s

# 显示部署状态
echo "📊 部署状态:"
kubectl get pods -n jianbao-system
kubectl get svc -n jianbao-system

echo "✅ 部署完成！"
echo "🌐 测试服务: kubectl port-forward svc/jianbao-backend 8000:80 -n jianbao-system"
echo "🔍 然后访问: http://localhost:8000/health"