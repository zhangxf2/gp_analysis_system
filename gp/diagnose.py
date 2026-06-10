"""
诊断脚本 - 检查环境和测试数据源
"""
import sys
import subprocess

def check_package(package_name):
    """检查包是否安装"""
    try:
        __import__(package_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"❌ {package_name} 未安装")
        return False

def install_package(package_name):
    """尝试安装包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 安装成功")
        return True
    except:
        print(f"❌ {package_name} 安装失败")
        return False

def test_akshare():
    """测试 AkShare"""
    try:
        import akshare as ak
        print("\n测试 AkShare 获取数据...")
        df = ak.stock_zh_a_hist(symbol="600519", period="daily", 
                              start_date="20240101", end_date="20240131", adjust="qfq")
        if df is not None and not df.empty:
            print(f"✅ AkShare 获取成功: {len(df)} 条记录")
            print(f"   列名: {df.columns.tolist()}")
            return True
    except Exception as e:
        print(f"❌ AkShare 失败: {e}")
    return False

def test_yfinance():
    """测试 yfinance"""
    try:
        import yfinance as yf
        print("\n测试 yfinance 获取数据...")
        data = yf.download("600519.SS", period="1mo", progress=False)
        if data is not None and not data.empty:
            print(f"✅ yfinance 获取成功: {len(data)} 条记录")
            return True
    except Exception as e:
        print(f"❌ yfinance 失败: {e}")
    return False

def main():
    print("="*50)
    print("A股分析系统 - 环境诊断")
    print("="*50)
    
    print(f"\nPython 版本: {sys.version}")
    
    # 检查基础包
    print("\n--- 检查基础包 ---")
    check_package("pandas")
    check_package("numpy")
    check_package("plotly")
    check_package("ta")
    
    # 检查数据源包
    print("\n--- 检查数据源包 ---")
    if not check_package("akshare"):
        print("建议: 安装 AkShare (pip install akshare)")
    
    if not check_package("yfinance"):
        print("建议: 安装 yfinance (pip install yfinance)")
    
    check_package("streamlit")
    
    # 测试数据源
    print("\n--- 测试数据源 ---")
    print("\n注意: 如果无法连接网络，这些测试会失败")
    test_akshare()
    test_yfinance()
    
    print("\n--- 快速修复建议 ---")
    print("如果缺少依赖，运行: pip install -r requirements.txt")
    print("\n启动系统: python -m streamlit run app.py")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
