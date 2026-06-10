import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from data_fetcher import DataFetcher


class StockAnalyzer:
    def __init__(self, ticker, period='1y', interval='1d'):
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.data = None
        self.load_data()

    def load_data(self):
        """加载真实数据"""
        try:
            self.data = DataFetcher.get_data(self.ticker, self.period, self.interval)
            if self.data is not None and not self.data.empty:
                self.calculate_indicators()
        except Exception as e:
            print(f"加载数据失败: {e}")
            self.data = None

    def calculate_indicators(self):
        if self.data is None or self.data.empty:
            return

        df = self.data.copy()

        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA10'] = df['Close'].rolling(window=10).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()

        macd = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()

        kdj = ta.momentum.StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'])
        df['K'] = kdj.stoch()
        df['D'] = kdj.stoch_signal()
        df['J'] = 3 * df['K'] - 2 * df['D']

        df['Volume_MA5'] = df['Volume'].rolling(window=5).mean()
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()

        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

        bollinger = ta.volatility.BollingerBands(close=df['Close'])
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Low'] = bollinger.bollinger_lband()
        df['BB_Mid'] = bollinger.bollinger_mavg()

        df['ROC'] = ta.momentum.roc(df['Close'], window=10)
        df['CCI'] = ta.trend.cci(high=df['High'], low=df['Low'], close=df['Close'], window=20)

        self.data = df
        self.calculate_signals()
        self.calculate_top_bottom_signals()

    def calculate_signals(self):
        if self.data is None or self.data.empty:
            return

        df = self.data.copy()
        df['Buy_Signal'] = False
        df['Sell_Signal'] = False

        # 使用向量运算代替循环
        # MACD 金叉
        macd_cross_up = (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
        # KDJ 金叉在超卖区
        kdj_cross_up = (df['K'] > df['D']) & (df['K'].shift(1) <= df['D'].shift(1)) & (df['K'] < 30)
        # MA 金叉
        ma_cross_up = (df['MA5'] > df['MA20']) & (df['MA5'].shift(1) <= df['MA20'].shift(1))
        # 放量
        volume_surge = df['Volume'] > df['Volume_MA20'] * 1.5
        
        # 买入信号
        df['Buy_Signal'] = ((macd_cross_up | kdj_cross_up) & (ma_cross_up | volume_surge))

        # MACD 死叉
        macd_cross_down = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
        # KDJ 死叉在超买区
        kdj_cross_down = (df['K'] < df['D']) & (df['K'].shift(1) >= df['D'].shift(1)) & (df['K'] > 70)
        # MA 死叉
        ma_cross_down = (df['MA5'] < df['MA20']) & (df['MA5'].shift(1) >= df['MA20'].shift(1))
        
        # 卖出信号
        df['Sell_Signal'] = ((macd_cross_down | kdj_cross_down) | ma_cross_down)

        self.data = df

    def calculate_top_bottom_signals(self):
        if self.data is None or self.data.empty:
            return

        df = self.data.copy()
        
        df['Strong_Buy'] = False
        df['Strong_Sell'] = False
        df['Bottom_Signal'] = False
        df['Top_Signal'] = False
        df['Divergence_Buy'] = False
        df['Divergence_Sell'] = False
        
        # 计算强买强卖条件
        conditions = pd.DataFrame(index=df.index)
        conditions['cond1'] = df['RSI'] < 25
        conditions['cond2'] = (df['K'] < 20) & (df['K'] > df['D'])
        conditions['cond3'] = df['Close'] <= df['BB_Low']
        conditions['cond4'] = df['CCI'] < -200
        conditions['cond5'] = df['ROC'] < -10
        
        # 统计满足条件的数量
        df['Strong_Buy'] = conditions.sum(axis=1) >= 3
        
        conditions_sell = pd.DataFrame(index=df.index)
        conditions_sell['cond1'] = df['RSI'] > 75
        conditions_sell['cond2'] = (df['K'] > 80) & (df['K'] < df['D'])
        conditions_sell['cond3'] = df['Close'] >= df['BB_High']
        conditions_sell['cond4'] = df['CCI'] > 200
        conditions_sell['cond5'] = df['ROC'] > 10
        
        df['Strong_Sell'] = conditions_sell.sum(axis=1) >= 3
        
        # 底背离
        if len(df) > 20:
            price_lower = df['Close'] < df['Close'].shift(10)
            macd_higher = df['MACD'] > df['MACD'].shift(10)
            df.loc[price_lower & macd_higher, 'Divergence_Buy'] = True
            
            price_higher = df['Close'] > df['Close'].shift(10)
            macd_lower = df['MACD'] < df['MACD'].shift(10)
            df.loc[price_higher & macd_lower, 'Divergence_Sell'] = True
        
        # 顶底信号组合
        df['Bottom_Signal'] = df['Strong_Buy'] | df['Divergence_Buy']
        df['Top_Signal'] = df['Strong_Sell'] | df['Divergence_Sell']

        self.data = df

    def get_price_chart(self):
        if self.data is None or self.data.empty:
            return None

        # 创建5行子图：价格、成交量、信号面板、MACD+KDJ、RSI+CCI+ROC
        fig = make_subplots(rows=5, cols=1, shared_xaxes=True,
                            vertical_spacing=0.05,
                            row_heights=[0.28, 0.1, 0.12, 0.25, 0.25])

        # ========== 第1行：价格K线图 ==========
        fig.add_trace(go.Candlestick(
            x=self.data.index,
            open=self.data['Open'],
            high=self.data['High'],
            low=self.data['Low'],
            close=self.data['Close'],
            name='K线'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['MA5'],
            name='MA5', line=dict(color='orange', width=1)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['MA20'],
            name='MA20', line=dict(color='purple', width=1)
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['BB_High'],
            name='布林带上轨', line=dict(color='gray', width=1, dash='dash'),
            opacity=0.5
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['BB_Low'],
            name='布林带下轨', line=dict(color='gray', width=1, dash='dash'),
            opacity=0.5
        ), row=1, col=1)

        # 买卖信号标记
        buy_signals = self.data[self.data['Buy_Signal']]
        if not buy_signals.empty:
            fig.add_trace(go.Scatter(
                x=buy_signals.index, y=buy_signals['Low'],
                mode='markers', name='买入信号',
                marker=dict(symbol='triangle-up', size=12, color='green')
            ), row=1, col=1)

        sell_signals = self.data[self.data['Sell_Signal']]
        if not sell_signals.empty:
            fig.add_trace(go.Scatter(
                x=sell_signals.index, y=sell_signals['High'],
                mode='markers', name='卖出信号',
                marker=dict(symbol='triangle-down', size=12, color='red')
            ), row=1, col=1)

        # ========== 第2行：成交量 ==========
        fig.add_trace(go.Bar(
            x=self.data.index, y=self.data['Volume'],
            name='成交量', marker_color='lightblue'
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['Volume_MA20'],
            name='成交量MA20', line=dict(color='orange', width=1)
        ), row=2, col=1)

        # ========== 第3行：信号面板 ==========
        # 基准线
        fig.add_hline(y=0, line_color='gray', line_width=1, row=3, col=1)
        
        # 强买信号（位置+1）
        strong_buy_signals = self.data[self.data['Strong_Buy']]
        if not strong_buy_signals.empty:
            fig.add_trace(go.Scatter(
                x=strong_buy_signals.index, y=[1] * len(strong_buy_signals),
                mode='markers', name='强买信号',
                marker=dict(symbol='star', size=14, color='lime')
            ), row=3, col=1)

        # 强卖信号（位置-1）
        strong_sell_signals = self.data[self.data['Strong_Sell']]
        if not strong_sell_signals.empty:
            fig.add_trace(go.Scatter(
                x=strong_sell_signals.index, y=[-1] * len(strong_sell_signals),
                mode='markers', name='强卖信号',
                marker=dict(symbol='star', size=14, color='crimson')
            ), row=3, col=1)

        # 底背离信号（位置+2）
        divergence_buy = self.data[self.data['Divergence_Buy']]
        if not divergence_buy.empty:
            fig.add_trace(go.Scatter(
                x=divergence_buy.index, y=[2] * len(divergence_buy),
                mode='markers', name='底背离',
                marker=dict(symbol='diamond', size=12, color='cyan')
            ), row=3, col=1)

        # 顶背离信号（位置-2）
        divergence_sell = self.data[self.data['Divergence_Sell']]
        if not divergence_sell.empty:
            fig.add_trace(go.Scatter(
                x=divergence_sell.index, y=[-2] * len(divergence_sell),
                mode='markers', name='顶背离',
                marker=dict(symbol='diamond', size=12, color='magenta')
            ), row=3, col=1)

        # ========== 第4行：MACD + KDJ ==========
        # MACD
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['MACD'],
            name='MACD', line=dict(color='blue', width=1.5)
        ), row=4, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['MACD_Signal'],
            name='MACD Signal', line=dict(color='orange', width=1.5)
        ), row=4, col=1)

        macd_colors = ['crimson' if x < 0 else 'limegreen' for x in self.data['MACD_Hist']]
        fig.add_trace(go.Bar(
            x=self.data.index, y=self.data['MACD_Hist'],
            name='MACD Hist', marker_color=macd_colors, opacity=0.6
        ), row=4, col=1)

        # KDJ（使用双Y轴）
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['K'],
            name='K', line=dict(color='royalblue', width=1.5),
            yaxis=f'y4'
        ), row=4, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['D'],
            name='D', line=dict(color='darkorange', width=1.5),
            yaxis=f'y4'
        ), row=4, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['J'],
            name='J', line=dict(color='darkviolet', width=1.5),
            yaxis=f'y4'
        ), row=4, col=1)

        # KDJ超买超卖线
        fig.add_hline(y=20, line_dash='dash', line_color='green', row=4, col=1,
                     opacity=0.5, yref=f'y4')
        fig.add_hline(y=50, line_dash='dash', line_color='gray', row=4, col=1,
                     opacity=0.3, yref=f'y4')
        fig.add_hline(y=80, line_dash='dash', line_color='red', row=4, col=1,
                     opacity=0.5, yref=f'y4')

        # ========== 第5行：RSI + CCI + ROC ==========
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['RSI'],
            name='RSI', line=dict(color='darkblue', width=1.5)
        ), row=5, col=1)
        
        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['CCI'] / 10,  # 缩放CCI与RSI同范围
            name='CCI (缩放)', line=dict(color='purple', width=1.5),
        ), row=5, col=1)

        fig.add_trace(go.Scatter(
            x=self.data.index, y=self.data['ROC'] * 3,  # 缩放ROC与RSI同范围
            name='ROC (缩放)', line=dict(color='darkgreen', width=1.5),
        ), row=5, col=1)

        # 参考线
        fig.add_hline(y=30, line_dash='dash', line_color='green', row=5, col=1, opacity=0.5)
        fig.add_hline(y=50, line_dash='dash', line_color='gray', row=5, col=1, opacity=0.3)
        fig.add_hline(y=70, line_dash='dash', line_color='red', row=5, col=1, opacity=0.5)

        fig.update_layout(
            title=f'{self.ticker} 股票分析',
            height=1500,
            xaxis_rangeslider_visible=False,
            yaxis4=dict(
                title='KDJ',
                overlaying='y4',
                side='right',
                range=[0, 100]
            )
        )

        fig.update_yaxes(title_text='价格', row=1, col=1)
        fig.update_yaxes(title_text='成交量', row=2, col=1)
        fig.update_yaxes(title_text='信号', row=3, col=1, range=[-2.5, 2.5], showticklabels=False)
        fig.update_yaxes(title_text='MACD / KDJ', row=4, col=1)
        fig.update_yaxes(title_text='RSI / CCI / ROC', row=5, col=1, range=[0, 100])

        return fig

    def get_latest_signals(self):
        if self.data is None or self.data.empty:
            return None

        latest = self.data.iloc[-1]
        signals = {
            'ticker': self.ticker,
            'date': latest.name.strftime('%Y-%m-%d'),
            'close': round(latest['Close'], 2),
            'buy_signal': bool(latest['Buy_Signal']),
            'sell_signal': bool(latest['Sell_Signal']),
            'strong_buy': bool(latest['Strong_Buy']),
            'strong_sell': bool(latest['Strong_Sell']),
            'bottom_signal': bool(latest['Bottom_Signal']),
            'top_signal': bool(latest['Top_Signal']),
            'divergence_buy': bool(latest['Divergence_Buy']),
            'divergence_sell': bool(latest['Divergence_Sell']),
            'macd': round(latest['MACD'], 4) if pd.notna(latest['MACD']) else None,
            'macd_signal': round(latest['MACD_Signal'], 4) if pd.notna(latest['MACD_Signal']) else None,
            'k': round(latest['K'], 2) if pd.notna(latest['K']) else None,
            'd': round(latest['D'], 2) if pd.notna(latest['D']) else None,
            'j': round(latest['J'], 2) if pd.notna(latest['J']) else None,
            'rsi': round(latest['RSI'], 2) if pd.notna(latest['RSI']) else None,
            'cci': round(latest['CCI'], 2) if pd.notna(latest['CCI']) else None,
            'roc': round(latest['ROC'], 2) if pd.notna(latest['ROC']) else None,
            'volume_ratio': round(latest['Volume'] / latest['Volume_MA20'], 2) if pd.notna(latest['Volume_MA20']) else None
        }
        return signals

    def get_summary(self):
        if self.data is None or self.data.empty:
            return None

        latest = self.data.iloc[-1]
        summary = []

        if latest['Strong_Buy']:
            summary.append('🚨 强买信号：多重指标共振，可能见底')
        if latest['Strong_Sell']:
            summary.append('🚨 强卖信号：多重指标共振，可能见顶')
        if latest['Divergence_Buy']:
            summary.append('💎 底背离：价格创新低但指标未创新低，反转信号')
        if latest['Divergence_Sell']:
            summary.append('⚠️ 顶背离：价格创新高但指标未创新高，反转信号')

        if latest['MACD'] > latest['MACD_Signal']:
            summary.append('MACD: 金叉向上，看涨')
        else:
            summary.append('MACD: 死叉向下，看跌')

        if latest['K'] < 20:
            summary.append('KDJ: 超卖区域，可能反弹')
        elif latest['K'] > 80:
            summary.append('KDJ: 超买区域，可能回调')
        else:
            summary.append('KDJ: 正常区域')

        if latest['RSI'] < 30:
            summary.append('RSI: 超卖')
        elif latest['RSI'] > 70:
            summary.append('RSI: 超买')
        else:
            summary.append('RSI: 正常')

        if latest['CCI'] < -200:
            summary.append('CCI: 极度超卖，关注反弹机会')
        elif latest['CCI'] > 200:
            summary.append('CCI: 极度超买，注意回调风险')

        if latest['Close'] <= latest['BB_Low']:
            summary.append('布林带：价格触及下轨，可能反弹')
        elif latest['Close'] >= latest['BB_High']:
            summary.append('布林带：价格触及上轨，可能回调')

        if latest['Volume'] > latest['Volume_MA20'] * 1.5:
            summary.append('成交量: 放量')
        elif latest['Volume'] < latest['Volume_MA20'] * 0.5:
            summary.append('成交量: 缩量')
        else:
            summary.append('成交量: 正常')

        return summary
