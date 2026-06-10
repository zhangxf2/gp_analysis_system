"""
股票筛选器 - 优化版
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from stock_analyzer import StockAnalyzer


class StockScreener:
    """优化的股票筛选器"""
    
    # 热门股票列表
    HOT_STOCKS = {
        '600519.SS': '贵州茅台',
        '000001.SZ': '平安银行',
        '601318.SS': '中国平安',
        '000858.SZ': '五粮液',
        '002594.SZ': '比亚迪',
        '300750.SZ': '宁德时代',
        '600036.SS': '招商银行',
        '601899.SS': '紫金矿业',
        '601857.SS': '中国石油',
        '000002.SZ': '万科A',
        '600900.SS': '长江电力',
        '600276.SS': '恒瑞医药',
        '000568.SZ': '泸州老窖',
        '000651.SZ': '格力电器',
        '000333.SZ': '美的集团'
    }
    
    @staticmethod
    def analyze_all_stocks(period='1y') -> Dict:
        """分析所有股票并返回筛选结果"""
        results = {
            'overbought': [],      # 超买股票
            'oversold': [],        # 超卖股票
            'macd_gold_cross': [], # MACD金叉
            'macd_death_cross': [] # MACD死叉
        }
        
        for code, name in StockScreener.HOT_STOCKS.items():
            try:
                analyzer = StockAnalyzer(code, period=period)
                if analyzer.data is None or analyzer.data.empty:
                    continue
                
                signals = analyzer.get_latest_signals()
                
                stock_info = {
                    'code': code,
                    'name': name,
                    'close': signals['close'],
                    'rsi': signals['rsi'],
                    'macd': signals['macd'],
                    'macd_signal': signals['macd_signal'],
                    'k': signals['k'],
                    'd': signals['d'],
                    'cci': signals['cci'],
                    'volume_ratio': signals['volume_ratio']
                }
                
                # 超买 (RSI > 70)
                if signals['rsi'] and signals['rsi'] > 70:
                    results['overbought'].append(stock_info)
                
                # 超卖 (RSI < 30)
                if signals['rsi'] and signals['rsi'] < 30:
                    results['oversold'].append(stock_info)
                
                # MACD金叉
                if signals['macd'] and signals['macd_signal']:
                    # 检查是否刚刚金叉
                    if StockScreener._check_macd_gold_cross(analyzer):
                        results['macd_gold_cross'].append(stock_info)
                
                # MACD死叉
                if signals['macd'] and signals['macd_signal']:
                    if StockScreener._check_macd_death_cross(analyzer):
                        results['macd_death_cross'].append(stock_info)
            
            except Exception as e:
                print(f"分析 {code} 失败: {e}")
                continue
        
        return results
    
    @staticmethod
    def _check_macd_gold_cross(analyzer) -> bool:
        """检查MACD金叉"""
        try:
            df = analyzer.data
            if len(df) < 2:
                return False
            
            # 获取最近两天的MACD和Signal
            macd_current = df['MACD'].iloc[-1]
            macd_prev = df['MACD'].iloc[-2]
            signal_current = df['MACD_Signal'].iloc[-1]
            signal_prev = df['MACD_Signal'].iloc[-2]
            
            # 金叉：MACD从下往上穿过Signal
            if (macd_prev <= signal_prev) and (macd_current > signal_current):
                return True
                
        except Exception:
            pass
        
        return False
    
    @staticmethod
    def _check_macd_death_cross(analyzer) -> bool:
        """检查MACD死叉"""
        try:
            df = analyzer.data
            if len(df) < 2:
                return False
            
            # 获取最近两天的MACD和Signal
            macd_current = df['MACD'].iloc[-1]
            macd_prev = df['MACD'].iloc[-2]
            signal_current = df['MACD_Signal'].iloc[-1]
            signal_prev = df['MACD_Signal'].iloc[-2]
            
            # 死叉：MACD从上往下穿过Signal
            if (macd_prev >= signal_prev) and (macd_current < signal_current):
                return True
                
        except Exception:
            pass
        
        return False
    
    @staticmethod
    def find_stock_code(input_str: str) -> str:
        """
        根据输入查找股票代码
        支持：
        - 股票代码：600519, 600519.SS
        - 股票名称：贵州茅台
        """
        input_str = input_str.strip()
        
        # 1. 首先检查是否直接是股票代码（完整格式）
        if input_str in StockScreener.HOT_STOCKS:
            return input_str
        
        # 2. 检查是否是股票名称（反向匹配）
        # 创建反向映射：名称 -> 代码
        name_to_code = {name: code for code, name in StockScreener.HOT_STOCKS.items()}
        if input_str in name_to_code:
            return name_to_code[input_str]
        
        # 3. 检查是否是6位数字代码，自动补全后缀
        if len(input_str) == 6 and input_str.isdigit():
            if input_str.startswith('6'):  # 上交所
                return f"{input_str}.SS"
            else:  # 深交所
                return f"{input_str}.SZ"
        
        # 4. 检查是否是包含后缀的代码
        if '.' in input_str:
            return input_str
        
        # 如果没有匹配到，尝试直接返回（让后续处理尝试）
        return input_str
