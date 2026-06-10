#!/bin/bash
# Ubuntu 环境一键运行脚本

echo "========================================="
echo "  📈 股票分析系统 - 启动脚本"
echo "========================================="

# 设置项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
echo ""
echo "🐍 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}$PYTHON_VERSION${NC}"

# 检查并安装依赖
echo ""
echo "📦 检查依赖..."
python3 -c "import streamlit, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}依赖不完整，正在安装...${NC}"
    
    # 先尝试安装固定版本
    pip3 install "yfinance==0.2.38" "websockets==12.0" 2>/dev/null
    
    # 安装所有依赖
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}尝试用户安装...${NC}"
        pip3 install --user -r requirements.txt
    fi
fi

# 验证关键包
echo ""
echo "✅ 验证包版本..."
python3 -c "
try:
    import streamlit
    print(f'streamlit: {streamlit.__version__}')
except:
    print('streamlit: ❌')
    
try:
    import yfinance
    print(f'yfinance: {yfinance.__version__}')
except:
    print('yfinance: ❌ (将使用模拟数据)')
    
try:
    import websockets
    print(f'websockets: {websockets.__version__}')
except:
    print('websockets: ❌')
"

echo ""
echo "========================================="
echo "  🚀 启动应用..."
echo "========================================="
echo ""
echo "应用将在以下地址运行:"
echo "  本地: http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止"
echo ""

# 使用 python -m 方式运行，最可靠
python3 -m streamlit run app.py
