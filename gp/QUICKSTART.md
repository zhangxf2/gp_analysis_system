# 🚀 快速开始 - 无依赖冲突版

## 三分钟上手

### 第一步：安装核心依赖
```bash
pip install streamlit pandas numpy matplotlib plotly ta
```

### 第二步：启动系统
```bash
python -m streamlit run app.py
```

就是这么简单！

---

## 📦 依赖说明

### ✅ 已包含（无冲突）
- streamlit - Web界面
- pandas, numpy - 数据处理
- matplotlib, plotly - 图表
- ta - 技术指标

### 🟡 可选数据源（单独安装）
- yfinance - 通用数据
- AkShare - A股专业数据

**重要**: 即使不安装数据源，系统也有高质量演示数据！

---

## 🎯 两种使用方式

### 方式1：仅演示数据（推荐先试）
直接启动，无需其他依赖。

### 方式2：真实数据（可选）
```bash
# 安装 yfinance
pip install yfinance

# 或者安装 AkShare（可能有冲突）
pip install akshare
```

---

## 🔧 如果遇到问题

### 依赖冲突
```bash
# 使用pip的回退功能
pip install yfinance --no-deps
```

### 安装缓慢
```bash
# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple streamlit
```

---

## ✨ 系统特性

即使只有演示数据，也能体验：
- 📊 完整的技术分析
- 🎯 智能买卖信号
- 📈 交互式K线图
- 🔄 顶底识别

---

## 📞 需要帮助？

运行诊断脚本：
```bash
python diagnose.py
```
