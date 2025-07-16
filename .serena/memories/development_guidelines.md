# TradingAgents 开发指南

## 智能体开发规范

### 创建新智能体
1. **继承基础结构**: 使用现有智能体作为模板
2. **定义清晰角色**: 明确智能体的专业领域和职责
3. **标准化输出**: 遵循统一的报告格式
4. **工具集成**: 合理使用数据获取工具

### 智能体命名规范
```python
# 函数命名: create_{role}_{type}
def create_market_analyst():
    pass

def create_bull_researcher():
    pass
```

## 数据流开发规范

### 新增数据源
1. **在interface.py中添加接口函数**
2. **实现缓存机制**
3. **错误处理和重试逻辑**
4. **API限制遵守**

### 数据处理最佳实践
```python
# 示例：数据获取函数结构
def get_new_data_source(symbol, start_date, end_date):
    try:
        # 检查缓存
        cached_data = check_cache(symbol, start_date, end_date)
        if cached_data:
            return cached_data
        
        # 获取新数据
        data = fetch_from_api(symbol, start_date, end_date)
        
        # 保存到缓存
        save_to_cache(data, symbol, start_date, end_date)
        
        return data
    except Exception as e:
        logger.error(f"数据获取失败: {e}")
        return fallback_data(symbol, start_date, end_date)
```

## 性能优化指南

### LLM调用优化
- **批量处理**: 合并相似的LLM请求
- **缓存结果**: 相同输入缓存LLM响应
- **模型选择**: 根据任务复杂度选择合适模型
- **并发控制**: 避免超出API限制

### 内存管理
- **及时释放**: 大数据处理后清理内存
- **流式处理**: 大文件使用流式读取
- **对象池**: 重用昂贵的对象创建

### 数据库优化
- **索引优化**: 为常用查询字段建立索引
- **连接池**: 使用数据库连接池
- **批量操作**: 减少数据库往返次数

## 测试开发规范

### 单元测试
```python
import pytest
from unittest.mock import Mock, patch

class TestMarketAnalyst:
    def test_create_market_analyst(self):
        analyst = create_market_analyst()
        assert analyst is not None
    
    @patch('tradingagents.dataflows.interface.get_stock_data')
    def test_analyst_with_mock_data(self, mock_get_data):
        mock_get_data.return_value = sample_data
        result = analyst.analyze('AAPL')
        assert 'recommendation' in result
```

### 集成测试
- **端到端测试**: 完整工作流测试
- **API测试**: 外部数据源连接测试
- **性能测试**: 响应时间和资源使用测试

## 安全开发规范

### API密钥管理
- **环境变量**: 使用环境变量存储敏感信息
- **配置分离**: 敏感配置与代码分离
- **权限最小化**: 只申请必要的API权限

### 数据安全
- **数据脱敏**: 日志中避免敏感数据
- **传输加密**: 使用HTTPS传输数据
- **本地存储**: 敏感数据加密存储

## 部署和运维

### 容器化部署
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### 监控和日志
- **结构化日志**: 使用JSON格式日志
- **性能监控**: 监控API响应时间
- **错误追踪**: 集成错误报告系统
- **资源监控**: 监控CPU、内存使用

## 代码审查清单

### 功能性检查
- [ ] 代码实现符合需求
- [ ] 错误处理完善
- [ ] 测试覆盖充分
- [ ] 文档更新及时

### 性能检查
- [ ] 无明显性能瓶颈
- [ ] 内存使用合理
- [ ] API调用优化
- [ ] 缓存策略有效

### 安全检查
- [ ] 无硬编码敏感信息
- [ ] 输入验证充分
- [ ] 权限控制合理
- [ ] 依赖库安全