#!/bin/bash
# =========================================
# 简易安装脚本 - 无依赖冲突
# =========================================

echo "========================================="
echo "  A股分析系统 - 简易安装"
echo "========================================="
echo ""

# 1. 安装核心依赖
echo "📦 步骤1: 安装核心依赖..."
pip install streamlit pandas numpy matplotlib plotly ta

echo ""
echo "✅ 核心依赖安装完成！"
echo ""

# 2. 可选数据源安装
echo "========================================="
echo "  可选数据源"
echo "========================================="
echo ""
echo "💡 yfinance 和 AkShare 是可选的"
echo "💡 系统自带高质量演示数据"
echo ""
echo "如果需要真实数据，可以尝试："
echo "  pip install yfinance"
echo "  或者"
echo "  pip install akshare"
echo ""

# 3. 完成
echo "========================================="
echo "  安装完成！"
echo "========================================="
echo ""
echo "🚀 启动系统:"
echo "  python -m streamlit run app.py"
echo ""
