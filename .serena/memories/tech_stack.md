# TradingAgents 技术栈

## 核心框架
- **LangGraph**: 多智能体工作流编排
- **LangChain**: LLM集成和工具链管理
- **Python 3.10+**: 主要开发语言

## LLM支持
- **OpenAI**: GPT-4o, o1-preview, gpt-4o-mini
- **Anthropic**: Claude系列模型
- **Google**: Gemini系列模型
- **支持自定义后端URL**: 兼容OpenAI API格式的服务

## 数据获取
- **yfinance**: Yahoo Finance数据
- **finnhub-python**: Finnhub金融数据API
- **akshare**: 中国金融数据
- **tushare**: 金融数据接口
- **eodhd**: 历史金融数据
- **praw**: Reddit社交媒体数据

## 数据处理与分析
- **pandas**: 数据处理和分析
- **stockstats**: 技术指标计算
- **backtrader**: 回测框架
- **pytz**: 时区处理

## 存储与缓存
- **chromadb**: 向量数据库（记忆系统）
- **redis**: 缓存系统

## CLI与界面
- **typer**: 命令行界面框架
- **rich**: 终端美化和进度显示
- **questionary**: 交互式命令行
- **chainlit**: Web界面（可选）

## 工具库
- **requests**: HTTP请求
- **feedparser**: RSS/新闻解析
- **parsel**: 网页解析
- **tqdm**: 进度条
- **typing-extensions**: 类型注解扩展