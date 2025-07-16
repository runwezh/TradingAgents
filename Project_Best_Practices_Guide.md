# TradingAgents 项目最佳实践指南

---

## 目录
1. [智能体开发最佳实践](#智能体开发最佳实践)
2. [数据流开发最佳实践](#数据流开发最佳实践)
3. [性能优化指南](#性能优化指南)
4. [测试开发规范](#测试开发规范)
5. [安全开发规范](#安全开发规范)
6. [部署与运维建议](#部署与运维建议)
7. [代码审查清单](#代码审查清单)

---

## 1. 智能体开发最佳实践
- 继承基础结构，角色职责清晰
- 输出标准化，报告结构统一
- 工具集成，数据接口复用
- 命名规范：`create_{role}_{type}`

## 2. 数据流开发最佳实践
- 新增数据源需接口、缓存、错误处理、限流全覆盖
- 数据处理优先缓存，异常优雅降级
- 示例：
```python
# 数据获取函数结构
try:
    cached = check_cache(...)
    if cached:
        return cached
    data = fetch_from_api(...)
    save_to_cache(data)
    return data
except Exception as e:
    logger.error(f"数据获取失败: {e}")
    return fallback_data(...)
```

## 3. 性能优化指南
- LLM调用批量处理、缓存、模型选择、并发控制
- 数据流流式/批量处理，内存及时释放
- 数据库索引、连接池、批量操作
- 结构化日志、性能监控、错误追踪、资源监控

## 4. 测试开发规范
- 单元测试：pytest、mock
- 集成测试：端到端、API、性能
- 示例：
```python
import pytest
from unittest.mock import patch

def test_create_market_analyst():
    ...

@patch('tradingagents.dataflows.interface.get_stock_data')
def test_analyst_with_mock_data(mock_get_data):
    ...
```

## 5. 安全开发规范
- API密钥用环境变量，配置分离
- 日志脱敏，HTTPS传输
- 本地敏感数据加密

## 6. 部署与运维建议
- 推荐容器化部署（见下方 Dockerfile 示例）
- 结构化日志、性能监控、错误追踪
- 示例 Dockerfile：
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 7. 代码审查清单
- [ ] 代码实现符合需求
- [ ] 错误处理完善
- [ ] 测试覆盖充分
- [ ] 文档更新及时
- [ ] 无明显性能瓶颈
- [ ] 内存使用合理
- [ ] API调用优化
- [ ] 缓存策略有效
- [ ] 无硬编码敏感信息
- [ ] 输入验证充分
- [ ] 权限控制合理
- [ ] 依赖库安全

---

> 本指南为 TradingAgents 项目高质量开发与协作的最佳实践总结，建议团队成员严格遵循。 