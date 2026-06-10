# Ubuntu 环境下 yfinance 问题修复

## 问题描述
在 Ubuntu Python 3.8 环境下运行时出现错误：
```
ModuleNotFoundError: No module named 'websockets.asyncio'
```

## 解决方案

### 方案一：安装兼容版本的依赖（推荐）

```bash
pip install "yfinance<0.2.40" "websockets<13.0"
```

或者使用 requirements.txt：
```bash
pip install -r requirements.txt
```

### 方案二：升级 Python 版本

如果可能，升级到 Python 3.10 或更高版本：
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

### 方案三：单独安装旧版 websockets

```bash
pip uninstall websockets
pip install "websockets<13.0"
```

## 当前改动说明

### 1. requirements.txt
已固定版本：
- `yfinance<0.2.40`
- `websockets<13.0`

### 2. stock_analyzer.py
- 延迟导入 yfinance，避免启动时直接报错
- 添加模拟数据 fallback，即使 yfinance 失败也能运行
- 添加 `is_using_sample_data()` 方法检测数据源

### 3. app.py
- 当使用模拟数据时显示警告提示

## 验证安装

```bash
python3 -c "import yfinance; print(yfinance.__version__)"
python3 -c "import websockets; print(websockets.__version__)"
```

## 完全重装依赖

如果问题持续：
```bash
pip uninstall -y yfinance websockets
pip install "yfinance<0.2.40" "websockets<13.0"
```
