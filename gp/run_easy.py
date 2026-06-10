
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键启动脚本 - 自动处理依赖问题
"""
import sys
import subprocess

def check_and_install_deps():
    """检查并安装依赖"""
    print("=" * 60)
    print("A股分析系统 - 启动检查")
    print("=" * 60)
    
    required = ['streamlit', 'pandas', 'numpy', 'matplotlib', 'plotly', 'ta']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ {pkg} - 已安装")
        except ImportError:
            print(f"❌ {pkg} - 未安装")
            missing.append(pkg)
    
    if missing:
        print(f"\n需要安装 {len(missing)} 个包...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("✅ 依赖安装完成！")
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False
    
    # 可选数据源
    print("\n可选数据源检查:")
    for pkg in ['yfinance', 'akshare']:
        try:
            __import__(pkg)
            print(f"✅ {pkg} - 已安装 (可选)")
        except ImportError:
            print(f"ℹ️ {pkg} - 未安装 (将使用演示数据)")
    
    return True

def main():
    """主函数"""
    if not check_and_install_deps():
        print("\n⚠️ 依赖检查有问题，但仍尝试启动...")
    
    print("\n" + "=" * 60)
    print("启动 Streamlit 应用...")
    print("=" * 60)
    
    try:
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "app.py", "--server.port=8501"]
        stcli.main()
    except ImportError:
        print("\n尝试替代启动方式...")
        subprocess.call([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
