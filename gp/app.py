import streamlit as st
import pandas as pd
import sys

# =========================================
# 导入我们的模块 - 它们会安全处理依赖问题
# =========================================
from stock_analyzer import StockAnalyzer
from stock_screener import StockScreener

st.set_page_config(page_title='A股分析系统', layout='wide')

# =========================================
# 页面导航
# =========================================
page = st.sidebar.radio("选择功能", ["单股分析", "股票筛选"])

# =========================================
# 页面1：单股分析
# =========================================
if page == "单股分析":
    st.title('📈 A股分析系统')

    st.sidebar.header('参数设置')

    # 股票代码输入选项
    input_mode = st.sidebar.radio('输入方式', ['直接输入', '从列表选择'])

    if input_mode == '直接输入':
        ticker_input = st.sidebar.text_input('股票代码/名称', value='600519', help='支持格式：600519、600519.SS、或直接输入股票名称如"贵州茅台"')
        # 使用智能查找
        ticker = StockScreener.find_stock_code(ticker_input)
        if ticker_input != ticker:
            st.sidebar.info(f"✅ 已识别: {ticker} ({StockScreener.HOT_STOCKS.get(ticker, '')})")
    else:
        stock_options = StockScreener.HOT_STOCKS
        selected_stock = st.sidebar.selectbox(
            '选择热门股票',
            options=list(stock_options.keys()),
            format_func=lambda x: f"{x} ({stock_options[x]})"
        )
        ticker = selected_stock

    period = st.sidebar.selectbox(
        '时间周期',
        ['1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'],
        index=3
    )

    interval = st.sidebar.selectbox(
        '数据间隔',
        ['1d', '1wk', '1mo'],
        index=0
    )

    analyze_button = st.sidebar.button('开始分析', type='primary')

    if analyze_button or 'analyzer' not in st.session_state:
        with st.spinner('正在加载数据...'):
            analyzer = StockAnalyzer(ticker, period, interval)
            st.session_state.analyzer = analyzer

    if 'analyzer' in st.session_state:
        analyzer = st.session_state.analyzer

        if analyzer.data is None or analyzer.data.empty:
            st.error("❌ 无法获取真实数据")
            st.error("")
            st.subheader("🔧 解决方案")

            col1, col2 = st.columns(2)

            with col1:
                st.info("**安装数据源**")
                st.code("pip install yfinance")
                st.text("或")
                st.code("pip install akshare")

            with col2:
                st.info("**检查以下项目**")
                st.text("1. 股票代码格式正确")
                st.text("2. 网络连接正常")
                st.text("3. 数据源已安装")

        else:
            # 显示数据源信息
            try:
                source = analyzer.data.attrs.get('source', 'unknown')
                st.success(f"✅ 使用真实数据 ({source})")
            except:
                st.success("✅ 数据加载成功")

            st.subheader('🚨 重要顶底信号')

            signals = analyzer.get_latest_signals()

            signal_cols = st.columns(4)
            with signal_cols[0]:
                if signals['strong_buy']:
                    st.error('🌟 强买信号')
                else:
                    st.info('无强买')
            with signal_cols[1]:
                if signals['strong_sell']:
                    st.error('⚠️ 强卖信号')
                else:
                    st.info('无强卖')
            with signal_cols[2]:
                if signals['divergence_buy']:
                    st.success('💎 底背离')
                else:
                    st.info('无底背离')
            with signal_cols[3]:
                if signals['divergence_sell']:
                    st.error('🔴 顶背离')
                else:
                    st.info('无顶背离')

            st.subheader('📊 最新行情')

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric('收盘价', f'¥{signals["close"]}')

            with col2:
                if signals['buy_signal']:
                    st.success('✅ 买入信号')
                elif signals['sell_signal']:
                    st.error('❌ 卖出信号')
                else:
                    st.info('⏸️ 观望')

            with col3:
                st.metric('RSI', signals['rsi'])

            with col4:
                st.metric('量比', signals['volume_ratio'])

            col_macd, col_kdj, col_other = st.columns(3)

            with col_macd:
                st.write('**MACD**:')
                st.write(f'MACD: {signals["macd"]}')
                st.write(f'Signal: {signals["macd_signal"]}')

            with col_kdj:
                st.write('**KDJ**:')
                st.write(f'K: {signals["k"]}')
                st.write(f'D: {signals["d"]}')
                st.write(f'J: {signals["j"]}')

            with col_other:
                st.write('**其他指标**:')
                st.write(f'CCI: {signals["cci"]}')
                st.write(f'ROC: {signals["roc"]}')

            st.subheader('💡 分析摘要')
            summary = analyzer.get_summary()
            for item in summary:
                st.write(f'• {item}')

            st.subheader('📈 技术分析图表')
            fig = analyzer.get_price_chart()
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.subheader('📋 历史数据')
            st.dataframe(analyzer.data.tail(30), use_container_width=True)

    st.sidebar.markdown('---')
    st.sidebar.subheader('使用说明')
    st.sidebar.info('''
**输入方式**:
- 直接输入 6 位数字代码 (系统自动补全后缀)
- 直接输入股票名称 (如"贵州茅台")
- 或从热门股票列表中选择

**上交所**: 600xxx, 601xxx, 603xxx, 605xxx, 688xxx
- 例如: 600519 (贵州茅台)

**深交所**: 000xxx, 001xxx, 002xxx, 003xxx, 300xxx, 301xxx
- 例如: 000001 (平安银行)
''')

    st.sidebar.markdown('---')
    st.sidebar.subheader('数据源状态')

    # 动态检查数据源
    try:
        import yfinance
        st.sidebar.success("✅ yfinance 已安装")
    except ImportError:
        st.sidebar.warning("⚠️ yfinance 未安装")

    try:
        import akshare
        st.sidebar.success("✅ AkShare 已安装")
    except ImportError:
        st.sidebar.info("ℹ️ AkShare 可选 (有依赖冲突可跳过)")

    st.sidebar.info("💡 使用真实市场数据！")

# =========================================
# 页面2：股票筛选
# =========================================
elif page == "股票筛选":
    st.title('🎯 股票筛选器')
    
    st.sidebar.header('筛选设置')
    period = st.sidebar.selectbox(
        '分析周期',
        ['1mo', '3mo', '6mo', '1y'],
        index=3
    )
    
    refresh_button = st.sidebar.button('🔄 刷新数据', type='primary')
    
    if refresh_button or 'screener_results' not in st.session_state:
        with st.spinner('正在分析所有股票...'):
            results = StockScreener.analyze_all_stocks(period=period)
            st.session_state.screener_results = results
            st.session_state.screener_refresh_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if 'screener_results' in st.session_state:
        results = st.session_state.screener_results
        refresh_time = st.session_state.screener_refresh_time
        
        # 统计信息
        total_overbought = len(results['overbought'])
        total_oversold = len(results['oversold'])
        total_gold_cross = len(results['macd_gold_cross'])
        total_death_cross = len(results['macd_death_cross'])
        
        # 显示统计
        st.info(f"📊 数据更新时间: {refresh_time}")
        
        # 统计面板
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("超买股票", total_overbought, help="RSI > 70")
        with stat_cols[1]:
            st.metric("超卖股票", total_oversold, help="RSI < 30")
        with stat_cols[2]:
            st.metric("MACD金叉", total_gold_cross, help="MACD上穿Signal，看涨信号")
        with stat_cols[3]:
            st.metric("MACD死叉", total_death_cross, help="MACD下穿Signal，看跌信号")
        
        st.markdown("---")
        
        # 创建标签页
        tab1, tab2, tab3, tab4 = st.tabs([
            "📉 超买股票", 
            "📈 超卖股票", 
            "💫 MACD金叉", 
            "⚠️ MACD死叉"
        ])
        
        # 超买股票
        with tab1:
            st.subheader('📉 超买股票 (RSI > 70)')
            st.caption('超买区域，可能回调，注意风险')
            
            if len(results['overbought']) > 0:
                overbought_df = pd.DataFrame(results['overbought'])
                overbought_df['RSI'] = overbought_df['rsi'].round(1)
                overbought_df['收盘价'] = overbought_df['close'].round(2)
                overbought_df = overbought_df[['code', 'name', '收盘价', 'RSI', 'k', 'd']]
                overbought_df.columns = ['代码', '名称', '收盘价', 'RSI', 'K值', 'D值']
                st.dataframe(overbought_df, use_container_width=True)
            else:
                st.info("当前没有超买股票")
        
        # 超卖股票
        with tab2:
            st.subheader('📈 超卖股票 (RSI < 30)')
            st.caption('超卖区域，可能反弹，关注机会')
            
            if len(results['oversold']) > 0:
                oversold_df = pd.DataFrame(results['oversold'])
                oversold_df['RSI'] = oversold_df['rsi'].round(1)
                oversold_df['收盘价'] = oversold_df['close'].round(2)
                oversold_df = oversold_df[['code', 'name', '收盘价', 'RSI', 'k', 'd']]
                oversold_df.columns = ['代码', '名称', '收盘价', 'RSI', 'K值', 'D值']
                st.dataframe(oversold_df, use_container_width=True)
            else:
                st.info("当前没有超卖股票")
        
        # MACD金叉
        with tab3:
            st.subheader('💫 MACD金叉向上（看涨）')
            st.caption('MACD上穿Signal线，通常是看涨信号')
            
            if len(results['macd_gold_cross']) > 0:
                macd_gold_df = pd.DataFrame(results['macd_gold_cross'])
                macd_gold_df['MACD'] = macd_gold_df['macd'].round(3)
                macd_gold_df['Signal'] = macd_gold_df['macd_signal'].round(3)
                macd_gold_df['收盘价'] = macd_gold_df['close'].round(2)
                macd_gold_df = macd_gold_df[['code', 'name', '收盘价', 'MACD', 'Signal', 'rsi']]
                macd_gold_df.columns = ['代码', '名称', '收盘价', 'MACD', 'Signal', 'RSI']
                st.dataframe(macd_gold_df, use_container_width=True)
            else:
                st.info("当前没有MACD金叉的股票")
        
        # MACD死叉
        with tab4:
            st.subheader('⚠️ MACD死叉向下（看跌）')
            st.caption('MACD下穿Signal线，通常是看跌信号')
            
            if len(results['macd_death_cross']) > 0:
                macd_death_df = pd.DataFrame(results['macd_death_cross'])
                macd_death_df['MACD'] = macd_death_df['macd'].round(3)
                macd_death_df['Signal'] = macd_death_df['macd_signal'].round(3)
                macd_death_df['收盘价'] = macd_death_df['close'].round(2)
                macd_death_df = macd_death_df[['code', 'name', '收盘价', 'MACD', 'Signal', 'rsi']]
                macd_death_df.columns = ['代码', '名称', '收盘价', 'MACD', 'Signal', 'RSI']
                st.dataframe(macd_death_df, use_container_width=True)
            else:
                st.info("当前没有MACD死叉的股票")
    
    # 显示热门股票列表
    st.markdown('---')
    st.subheader('📋 热门股票列表')
    st.write("包含以下股票：")
    for code, name in StockScreener.HOT_STOCKS.items():
        st.text(f"  • {code} - {name}")
