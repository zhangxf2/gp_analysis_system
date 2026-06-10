# 📈 A股分析系统 - 真实数据版

专业的A股技术分析系统，只使用真实市场数据。
<img width="1872" height="809" alt="8dfe23db-5826-4dfa-a48d-b0c0ff4d398c" src="https://github.com/user-attachments/assets/397f33c4-5774-47b3-b866-62e16d6f3d7f" />

<img width="1478" height="691" alt="9079531a-8469-4781-8ce0-8eb8e08085bf" src="https://github.com/user-attachments/assets/51946471-40ac-4b95-919b-9ea3ed1739da" />

---

## 🚀 快速开始

### 两步启动

```bash
# 1. 安装所有依赖（包含数据源）
pip install -r requirements.txt

# 2. 启动系统
python -m streamlit run app.py
```

---

## 📦 依赖说明

### 必需依赖
- streamlit - Web界面
- pandas, numpy - 数据处理
- matplotlib, plotly - 图表
- ta - 技术指标

### 数据源（至少一个）
- **yfinance** - 已包含，通用数据源
- **AkShare** - 可选，更好用的A股数据（可能有冲突）

---

## 🎯 数据来源优先级

```
1. AkShare (专业A股数据) → 如已安装
2. yfinance (通用数据) → 默认选择
```

---

## 🔧 安装数据源

### yfinance（推荐，已包含）
```bash
pip install yfinance
```

### AkShare（可选）
```bash
pip install akshare
```

如果有冲突，尝试：
```bash
pip install akshare --no-deps
```

---

## 💡 使用说明

### 股票代码格式

- **上交所**: `600519.SS` 或直接 `600519`
- **深交所**: `000001.SZ` 或直接 `000001`

### 功能
- 📊 MACD, KDJ, RSI, CCI, ROC, 布林带
- 🎯 智能买卖信号
- 🔄 顶底识别
- 📈 交互式K线图

---

## ❌ 无法获取数据？

### 检查以下项目

1. ✅ yfinance 或 AkShare 已安装
2. ✅ 股票代码格式正确
3. ✅ 网络连接正常

### 安装指引

系统界面会显示详细的安装指引。

---

## ⚠️ 免责声明

本系统仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎！
