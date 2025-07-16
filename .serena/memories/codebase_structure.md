# TradingAgents 代码库结构

## 顶层目录结构
```
TradingAgents/
├── tradingagents/          # 核心框架代码
├── cli/                    # 命令行界面
├── assets/                 # 静态资源文件
├── .serena/               # Serena配置目录
├── requirements.txt        # Python依赖
├── pyproject.toml         # 项目配置
├── main.py               # 主入口文件
└── README.md             # 项目说明
```

## 核心模块结构
```
tradingagents/
├── agents/                # 智能体实现
│   ├── analysts/         # 分析师团队
│   │   ├── market_analyst.py
│   │   ├── social_media_analyst.py
│   │   ├── news_analyst.py
│   │   └── fundamentals_analyst.py
│   ├── researchers/      # 研究团队
│   │   ├── bull_researcher.py
│   │   └── bear_researcher.py
│   ├── managers/         # 管理层
│   │   ├── research_manager.py
│   │   └── risk_manager.py
│   ├── trader/          # 交易员
│   │   └── trader.py
│   ├── risk_mgmt/       # 风险管理团队
│   │   ├── aggressive_debator.py
│   │   ├── neutral_debator.py
│   │   └── conservative_debator.py
│   └── utils/           # 智能体工具
│       ├── agent_states.py
│       ├── agent_utils.py
│       └── memory.py
├── graph/               # 图结构和工作流
│   ├── trading_graph.py
│   ├── conditional_logic.py
│   ├── setup.py
│   ├── propagation.py
│   ├── reflection.py
│   └── signal_processing.py
├── dataflows/           # 数据流处理
│   ├── interface.py
│   ├── yfin_utils.py
│   ├── finnhub_utils.py
│   ├── stockstats_utils.py
│   ├── googlenews_utils.py
│   ├── reddit_utils.py
│   ├── config.py
│   ├── utils.py
│   └── data_cache/      # 数据缓存目录
└── default_config.py    # 默认配置
```

## CLI模块结构
```
cli/
├── main.py             # CLI主入口
├── models.py           # 数据模型
└── utils.py            # CLI工具函数
```

## 关键入口点
- **主程序入口**: `main.py`
- **CLI入口**: `cli/main.py`
- **核心图类**: `tradingagents/graph/trading_graph.py`
- **配置文件**: `tradingagents/default_config.py`
- **智能体工厂**: `tradingagents/agents/__init__.py`

## 数据流向
1. **数据获取**: `dataflows/interface.py` -> 各种数据源
2. **智能体处理**: `agents/` -> 各专业智能体分析
3. **工作流编排**: `graph/trading_graph.py` -> LangGraph协调
4. **决策输出**: 最终交易建议

## 扩展点
- **新增智能体**: 在`agents/`目录下创建新的智能体类
- **新增数据源**: 在`dataflows/`目录下添加新的数据接口
- **自定义工作流**: 修改`graph/`目录下的图结构
- **新增LLM支持**: 在`trading_graph.py`中添加新的LLM提供商