# InvenTree 供应链风险管理模块

## 概述

这是一个为 InvenTree 系统开发的高级供应链风险管理模块，提供多层级供应商风险评估、供应链中断预警和风险缓解策略管理功能。

## 功能特性

### 1. 多层级供应商风险评估
- **风险评分系统**：财务风险、交付风险、质量风险、地域风险
- **动态阈值配置**：支持自定义风险阈值和自动告警
- **实时影响采购决策**：风险评估结果自动影响采购流程

### 2. 供应链中断预警系统
- **基于指标的预测**：采购订单交付延迟率、库存周转率等
- **参数可配置化**：风险评估模型参数支持自定义配置
- **自动和手动评估**：支持定时自动评估和手动触发评估

### 3. 风险缓解策略管理
- **自动备选供应商建议**：为高风险供应商自动生成备选供应商
- **风险处理追踪**：记录风险处理过程和结果
- **历史分析和报告**：风险事件的历史分析和报告生成

## 安装和配置

### 1. 模型迁移

运行数据库迁移以创建新的风险管理相关表：

```bash
python manage.py makemigrations company
python manage.py migrate company
```

### 2. 配置自动风险评估

在系统中配置定时任务以自动运行风险评估：

1. 安装 Django Q2（如果尚未安装）：
```bash
pip install django-q2
```

2. 在 `settings.py` 中配置 Django Q2：
```python
INSTALLED_APPS = [
    ...
    'django_q',
    ...
]

# Django Q2 配置
Q_CLUSTER = {
    'name': 'InvenTree',
    'workers': 4,
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
}
```

3. 启动 Django Q2 工作进程：
```bash
python manage.py qcluster
```

4. 创建定时任务以每天运行风险评估：
```bash
python manage.py qscheduler --create --name "Daily Risk Assessment" --func "company.management.commands.run_risk_assessment.Command.run_daily_assessment" --schedule "0 2 * * *"
```

## 使用方法

### 1. 手动运行风险评估

使用管理命令手动运行风险评估：

```bash
# 运行完整风险评估
python manage.py run_risk_assessment --full

# 只运行供应商风险评估
python manage.py run_risk_assessment --supplier-only

# 只运行供应链风险评估
python manage.py run_risk_assessment --supply-chain-only

# 强制重新计算所有风险
python manage.py run_risk_assessment --force
```

### 2. API 访问

通过 REST API 访问风险管理功能：

#### 供应商风险 API

- `GET /api/company/risk/supplier/` - 获取供应商风险列表
- `POST /api/company/risk/supplier/` - 创建新的供应商风险评估
- `GET /api/company/risk/supplier/<pk>/` - 获取特定供应商风险详情
- `PUT /api/company/risk/supplier/<pk>/` - 更新供应商风险评估
- `DELETE /api/company/risk/supplier/<pk>/` - 删除供应商风险评估
- `POST /api/company/risk/supplier/<pk>/recalculate/` - 重新计算供应商风险
- `GET /api/company/risk/supplier/summary/` - 获取供应商风险摘要
- `GET /api/company/risk/supplier/high-risk/` - 获取高风险供应商

#### 供应链风险 API

- `GET /api/company/risk/supply-chain/` - 获取供应链风险列表
- `POST /api/company/risk/supply-chain/` - 创建新的供应链风险评估
- `GET /api/company/risk/supply-chain/<pk>/` - 获取特定供应链风险详情
- `PUT /api/company/risk/supply-chain/<pk>/` - 更新供应链风险评估
- `DELETE /api/company/risk/supply-chain/<pk>/` - 删除供应链风险评估
- `POST /api/company/risk/supply-chain/<pk>/recalculate/` - 重新计算供应链风险
- `GET /api/company/risk/supply-chain/summary/` - 获取供应链风险摘要
- `GET /api/company/risk/supply-chain/high-risk/` - 获取高风险供应链项目
- `GET /api/company/risk/supply-chain/single-source/` - 获取单一来源供应商的项目

#### 风险缓解策略 API

- `GET /api/company/risk/mitigation/` - 获取风险缓解策略列表
- `POST /api/company/risk/mitigation/` - 创建新的风险缓解策略
- `GET /api/company/risk/mitigation/<pk>/` - 获取特定风险缓解策略详情
- `PUT /api/company/risk/mitigation/<pk>/` - 更新风险缓解策略
- `DELETE /api/company/risk/mitigation/<pk>/` - 删除风险缓解策略
- `GET /api/company/risk/mitigation/implemented/` - 获取已实施的策略
- `GET /api/company/risk/mitigation/not-implemented/` - 获取未实施的策略

#### 备选供应商建议 API

- `GET /api/company/risk/alternative-suppliers/` - 获取备选供应商建议列表
- `POST /api/company/risk/alternative-suppliers/` - 创建新的备选供应商建议
- `GET /api/company/risk/alternative-suppliers/<pk>/` - 获取特定备选供应商建议详情
- `PUT /api/company/risk/alternative-suppliers/<pk>/` - 更新备选供应商建议
- `DELETE /api/company/risk/alternative-suppliers/<pk>/` - 删除备选供应商建议
- `POST /api/company/risk/alternative-suppliers/<pk>/mark-reviewed/` - 标记建议为已审核
- `GET /api/company/risk/alternative-suppliers/unreviewed/` - 获取未审核的建议

#### 风险事件 API

- `GET /api/company/risk/events/` - 获取风险事件列表
- `POST /api/company/risk/events/` - 创建新的风险事件
- `GET /api/company/risk/events/<pk>/` - 获取特定风险事件详情
- `PUT /api/company/risk/events/<pk>/` - 更新风险事件
- `DELETE /api/company/risk/events/<pk>/` - 删除风险事件
- `POST /api/company/risk/events/<pk>/resolve/` - 标记事件为已解决
- `GET /api/company/risk/events/unresolved/` - 获取未解决的事件
- `GET /api/company/risk/events/high-severity/` - 获取高严重性事件

### 3. 管理界面集成

风险评估数据可以通过 Django 管理界面访问：

1. 登录管理界面
2. 导航到 "Company" 部分
3. 可以看到新增的风险管理相关模型：
   - Supplier Risks
   - Supply Chain Risks
   - Risk Mitigation Strategies
   - Alternative Supplier Suggestions
   - Risk Events

## 模型结构

### 核心模型

1. **SupplierRisk** - 供应商风险评估
   - 财务风险评分 (0-100)
   - 交付风险评分 (0-100)
   - 质量风险评分 (0-100)
   - 地域风险评分 (0-100)
   - 整体风险评分和等级

2. **SupplyChainRisk** - 供应链风险评估
   - 缺货风险评分 (0-100)
   - 单一来源风险
   - 长提前期风险
   - 高价值风险

3. **RiskMitigationStrategy** - 风险缓解策略
   - 策略类型（增加库存、寻找备选供应商等）
   - 实施状态
   - 预期效果

4. **AlternativeSupplierSuggestion** - 备选供应商建议
   - 相似度评分
   - 审核状态
   - 建议理由

5. **RiskEvent** - 风险事件
   - 事件类别（自然灾害、运输问题等）
   - 严重程度
   - 影响范围

### 枚举类型

- **RiskLevel** - 风险等级：LOW, MEDIUM, HIGH, CRITICAL
- **RiskCategory** - 风险类别：DELIVERY, QUALITY, FINANCIAL, GEOGRAPHICAL, OTHER

## 风险计算逻辑

### 供应商风险计算

```python
# 整体风险评分 = (财务风险 * 0.3) + (交付风险 * 0.3) + (质量风险 * 0.2) + (地域风险 * 0.2)
overall_score = (financial * 0.3) + (delivery * 0.3) + (quality * 0.2) + (geographical * 0.2)

# 风险等级划分
if overall_score >= 80: CRITICAL
elif overall_score >= 60: HIGH
elif overall_score >= 40: MEDIUM
else: LOW
```

### 供应链风险计算

```python
# 缺货风险评分基于：
# - 库存周转率
# - 平均交付时间
# - 供应商风险
# - 需求预测准确性
```

## 扩展和定制

### 自定义风险计算逻辑

可以通过继承 `SupplierRisk` 和 `SupplyChainRisk` 模型来扩展风险计算逻辑：

```python
class CustomSupplierRisk(SupplierRisk):
    def calculate_overall_risk(self):
        # 自定义整体风险计算逻辑
        pass
```

### 新增风险类别

可以通过扩展 `RiskCategory` 枚举来添加新的风险类别：

```python
class CustomRiskCategory(RiskCategory):
    CYBERSECURITY = 'cybersecurity'
    REGULATORY = 'regulatory'
```

## 性能优化

### 批量处理

使用批量更新来提高大规模数据处理的性能：

```python
SupplierRisk.objects.bulk_update(risk_objects, ['overall_risk_score', 'overall_risk_level'])
```

### 索引优化

在频繁查询的字段上创建数据库索引：

```python
class Meta:
    indexes = [
        models.Index(fields=['overall_risk_level']),
        models.Index(fields=['last_assessment_date']),
    ]
```

## 监控和维护

### 定期检查

1. 定期监控风险评估任务的执行情况
2. 检查数据库性能，确保查询效率
3. 根据业务需求调整风险阈值
4. 定期审查和更新风险缓解策略

### 日志记录

风险评估过程会记录详细日志，可以通过以下方式查看：

```bash
# 查看 Django 日志
python manage.py tail -f logs/inventree.log

# 查看 Django Q2 任务日志
python manage.py qmonitor
```

## 故障排除

### 常见问题

1. **风险评估任务未执行**
   - 检查 Django Q2 工作进程是否正在运行
   - 检查任务调度器配置
   - 查看任务日志

2. **API 访问失败**
   - 检查 API 端点是否正确配置
   - 验证用户权限
   - 查看 Django 错误日志

3. **性能问题**
   - 优化数据库查询
   - 增加 Django Q2 工作进程数量
   - 考虑使用缓存机制

## 许可证

该模块遵循 InvenTree 项目的许可证条款。

## 贡献

欢迎提交问题报告和改进建议！
