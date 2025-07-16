# TradingAgents 开发命令指南

## 环境设置
```bash
# 创建虚拟环境
conda create -n tradingagents python=3.13
conda activate tradingagents

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

## 运行命令
```bash
# CLI模式运行
python -m cli.main

# 直接运行主程序
python main.py

# 运行特定配置
python -c "from tradingagents.graph.trading_graph import TradingAgentsGraph; from tradingagents.default_config import DEFAULT_CONFIG; ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy()); _, decision = ta.propagate('NVDA', '2024-05-10'); print(decision)"
```

## 代码质量工具
```bash
# 代码格式化
python -m black tradingagents/ cli/
python -m isort tradingagents/ cli/

# 代码检查
python -m flake8 tradingagents/ cli/ --max-line-length=88
python -m pylint tradingagents/ cli/

# 类型检查
python -m mypy tradingagents/ cli/
```

## 测试命令
```bash
# 运行单元测试
python -m pytest tests/ -v

# 运行覆盖率测试
python -m pytest tests/ --cov=tradingagents --cov-report=html

# 运行特定测试
python -m pytest tests/test_trading_graph.py -v
```

## 数据管理
```bash
# 清理缓存数据
rm -rf tradingagents/dataflows/data_cache/*

# 检查数据目录
ls -la tradingagents/dataflows/data_cache/

# 验证API连接
python -c "import os; from tradingagents.dataflows.interface import get_finnhub_news; print('API连接正常' if get_finnhub_news('AAPL', '2024-01-01', '2024-01-02') else 'API连接失败')"
```

## 调试命令
```bash
# 调试模式运行
python -m pdb main.py

# 详细日志输出
PYTHON_LOG_LEVEL=DEBUG python main.py

# 性能分析
python -m cProfile -o profile_output.prof main.py
python -c "import pstats; p = pstats.Stats('profile_output.prof'); p.sort_stats('cumulative').print_stats(10)"
```

## 构建和分发
```bash
# 构建包
python -m build

# 安装本地包
pip install -e .

# 检查包结构
python setup.py check
```