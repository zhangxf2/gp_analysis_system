"""
数据获取模块 - 支持多数据源的A股真实数据获取
"""
import pandas as pd
import numpy as np


class DataFetcher:
    """A股数据获取类 - 支持多数据源"""
    
    @staticmethod
    def get_data(ticker, period='1y', interval='1d'):
        """
        获取A股真实数据
        
        Args:
            ticker: 股票代码 (如 600519.SS, 000001.SZ, 或直接 600519)
            period: 时间周期
            interval: 数据间隔
            
        Returns:
            DataFrame 或 None
        """
        ticker = DataFetcher._auto_complete_ticker(ticker)
        if not ticker:
            print(f"无效的股票代码: {ticker}")
            return None
        
        print(f"正在获取股票: {ticker}")
        
        data_sources = []
        
        # 优先使用 yfinance（更稳定，国际数据源）
        try:
            import yfinance
            data_sources.append(DataFetcher._try_yfinance)
            print("✅ yfinance 可用，优先使用")
        except Exception as e:
            print(f"❌ yfinance 未安装或有问题: {e}")
        
        # 备选使用 baostock（免费A股数据）
        try:
            import baostock
            data_sources.append(DataFetcher._try_baostock)
            print("✅ baostock 可用")
        except Exception as e:
            print(f"❌ baostock 未安装或有问题: {e}")
        
        # 备选使用 investpy（Investing.com数据）
        try:
            import investpy
            data_sources.append(DataFetcher._try_investpy)
            print("✅ investpy 可用")
        except Exception as e:
            print(f"❌ investpy 未安装或有问题: {e}")
        
        # 备选使用 AkShare（A股数据源）
        try:
            import akshare
            data_sources.append(DataFetcher._try_akshare)
            print("✅ AkShare 可用")
        except Exception:
            print("❌ AkShare 未安装或有问题")
        
        for source_func in data_sources:
            try:
                data = source_func(ticker, period, interval)
                if data is not None and not data.empty:
                    print(f"✅ 成功获取真实数据 ({source_func.__name__})")
                    data.attrs['source'] = source_func.__name__
                    return data
            except Exception as e:
                print(f"{source_func.__name__} 失败: {e}")
                continue
        
        print("❌ 无法获取真实数据")
        return None
    
    @staticmethod
    def _auto_complete_ticker(ticker):
        if not ticker or not isinstance(ticker, str):
            return None
        
        ticker = ticker.strip().upper()
        
        if ticker.endswith('.SS') or ticker.endswith('.SZ'):
            return ticker
        
        if len(ticker) == 6 and ticker.isdigit():
            first_three = ticker[:3]
            valid_sh_prefixes = ['600', '601', '603', '605', '688']
            valid_sz_prefixes = ['000', '001', '002', '003', '300', '301']
            
            if first_three in valid_sh_prefixes:
                return f"{ticker}.SS"
            elif first_three in valid_sz_prefixes:
                return f"{ticker}.SZ"
        
        return None
    
    @staticmethod
    def _try_akshare(ticker, period, interval):
        try:
            import akshare as ak
            import socket
            
            # 设置较短的超时时间，防止卡住
            socket.setdefaulttimeout(10)
            
            code = ticker.split('.')[0]
            end_date = pd.Timestamp.now().strftime('%Y%m%d')
            
            period_days = {
                '1mo': 30,
                '3mo': 90,
                '6mo': 180,
                '1y': 365,
                '2y': 730,
                '5y': 1825,
                'max': 3650,
            }
            
            days = period_days.get(period, 365)
            start_date = (pd.Timestamp.now() - pd.Timedelta(days=days)).strftime('%Y%m%d')
            
            print(f"正在通过 AkShare 获取 {code} 数据 (从 {start_date} 到 {end_date})")
            
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            
            if df is None or df.empty:
                return None
            
            df = df.rename(columns={
                '日期': 'Date',
                '开盘': 'Open',
                '最高': 'High',
                '最低': 'Low',
                '收盘': 'Close',
                '成交量': 'Volume',
            })
            
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = df['Close']
            
            return df.sort_index()
            
        except Exception as e:
            print(f"AkShare 错误: {e}")
            return None
    
    @staticmethod
    def _try_yfinance(ticker, period, interval):
        try:
            import yfinance as yf
            
            # 尝试多种代码格式
            ticker_variants = [ticker]
            if '.' in ticker:
                code = ticker.split('.')[0]
                ticker_variants.extend([code])
            
            for try_ticker in ticker_variants:
                try:
                    print(f"正在通过 yfinance 尝试获取 {try_ticker} 数据")
                    data = yf.download(try_ticker, period=period, progress=False)
                    
                    if data is not None and len(data) > 0:
                        try:
                            if hasattr(data.columns, 'levels') and len(data.columns.levels) > 1:
                                data.columns = data.columns.droplevel(1)
                        except:
                            pass
                        
                        print(f"✅ 成功通过 {try_ticker} 获取数据")
                        return data.sort_index()
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            print(f"yfinance 错误: {e}")
            return None
    
    @staticmethod
    def _try_baostock(ticker, period, interval):
        try:
            import baostock as bs
            import socket
            
            socket.setdefaulttimeout(10)
            
            code = ticker.split('.')[0]
            # baostock代码格式：sh.600519 或 sz.000001
            if ticker.endswith('.SS'):
                bs_code = f"sh.{code}"
            else:
                bs_code = f"sz.{code}"
            
            period_days = {
                '1mo': 30,
                '3mo': 90,
                '6mo': 180,
                '1y': 365,
                '2y': 730,
                '5y': 1825,
                'max': 3650,
            }
            
            days = period_days.get(period, 365)
            start_date = (pd.Timestamp.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
            
            print(f"正在通过 baostock 获取 {bs_code} 数据 (从 {start_date} 到 {end_date})")
            
            # 登录
            lg = bs.login()
            if lg.error_code != '0':
                print(f"baostock 登录失败: {lg.error_msg}")
                return None
            
            # 获取数据
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,volume",
                start_date=start_date,
                end_date=end_date,
                frequency="d",
                adjustflag="3"
            )
            
            # 登出
            bs.logout()
            
            if rs.error_code != '0':
                print(f"baostock 查询失败: {rs.error_msg}")
                return None
            
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return None
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 转换列名和数据类型
            df = df.rename(columns={
                'date': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume',
            })
            
            # 转换数值类型
            numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            return df.sort_index()
            
        except Exception as e:
            print(f"baostock 错误: {e}")
            return None
    
    @staticmethod
    def _try_investpy(ticker, period, interval):
        try:
            import investpy
            import socket
            
            socket.setdefaulttimeout(10)
            
            code = ticker.split('.')[0]
            print(f"正在通过 investpy 获取 {code} 数据")
            
            period_map = {
                '1mo': '1month',
                '3mo': '3months',
                '6mo': '6months',
                '1y': '1year',
                '2y': '2years',
                '5y': '5years',
                'max': 'max',
            }
            
            invest_period = period_map.get(period, '1year')
            
            # 尝试在中国市场搜索
            try:
                df = investpy.get_stock_historical_data(
                    stock=code,
                    country='china',
                    from_date=(pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%d/%m/%Y'),
                    to_date=pd.Timestamp.now().strftime('%d/%m/%Y'),
                    as_json=False,
                    order='ascending'
                )
                
                if df is not None and len(df) > 0:
                    df.index.name = 'Date'
                    return df.sort_index()
            except Exception:
                pass
            
            # 尝试在香港市场搜索
            try:
                df = investpy.get_stock_historical_data(
                    stock=code,
                    country='hong kong',
                    from_date=(pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%d/%m/%Y'),
                    to_date=pd.Timestamp.now().strftime('%d/%m/%Y'),
                    as_json=False,
                    order='ascending'
                )
                
                if df is not None and len(df) > 0:
                    df.index.name = 'Date'
                    return df.sort_index()
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            print(f"investpy 错误: {e}")
            return None
