#!/bin/bash
# Ubuntu 环境一键安装脚本

echo "========================================="
echo "  股票分析系统 - 依赖安装"
echo "========================================="

# 设置项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "📦 步骤 1: 卸载冲突版本..."
pip3 uninstall -y yfinance websockets 2>/dev/null

echo ""
echo "📦 步骤 2: 安装兼容版本..."
pip3 install "yfinance==0.2.38" "websockets==12.0"

echo ""
echo "📦 步骤 3: 安装其他依赖..."
pip3 install -r requirements.txt

echo ""
echo "✅ 验证安装..."
python3 -c "import yfinance; print('yfinance:', yfinance.__version__)"
python3 -c "import websockets; print('websockets:', websockets.__version__)"
python3 -c "import streamlit; print('streamlit:', streamlit.__version__)"

echo ""
echo "========================================="
echo "  安装完成！"
echo "========================================="
echo ""
echo "运行命令: python3 -m streamlit run app.py"
echo ""
