# Stock Allocation Sync - Testing Guide

## 问题修复概述

本次修复解决了 InvenTree 库存修改后的数据同步问题，包括：

1. **StockItem 库存数量修改时实时更新关联的订单库存明细**
2. **后台库存编辑页提交后的刷新反馈问题**
3. **兼容 stable 分支**
4. **通过 GitHub Actions docker 镜像测试**

## 测试失败的根本原因

### 1. pytest 和 py_compile 执行失败的原因

**根本原因：**
- Django 环境未正确初始化
- Python 路径配置不正确
- 测试运行时缺少必要的依赖

**解决方案：**
1. 使用正确的 Django 设置模块
2. 在导入模型前初始化 Django
3. 使用 pytest-django 插件
4. 配置正确的测试路径

### 2. 如何修复测试问题

#### 方法 1：使用 pytest（推荐）

```bash
# 设置环境变量
export DJANGO_SETTINGS_MODULE=InvenTree.settings

# 运行特定测试
cd src/backend/InvenTree
python -m pytest stock/test_api.py::StockItemAllocationSyncTest -v

# 运行所有测试
python -m pytest stock/test_api.py -v
```

#### 方法 2：使用自定义测试脚本

```bash
# 运行独立测试脚本
python test_stock_allocation_fix.py
```

#### 方法 3：使用 Django manage.py

```bash
# 进入后端目录
cd src/backend/InvenTree

# 运行测试
python manage.py test stock.test_api.StockItemAllocationSyncTest
```

### 3. 如何调整配置让修改通过 GitHub Actions docker 镜像测试

#### 已修改的配置文件

1. **`.github/workflows/docker.yaml`**
   - 添加了 `stable` 分支支持
   - 添加了 stock 模型文件的路径过滤
   - 添加了专门的测试步骤

2. **`.github/workflows/test_stock_allocation.yml`**（新增）
   - 专门用于测试库存分配同步功能
   - 支持在 push 和 PR 时运行

3. **`pytest.ini`**（新增）
   - 配置 pytest 设置
   - 指定 Django 设置模块
   - 配置测试路径和标记

#### 本地测试步骤

1. **安装依赖**
```bash
pip install -r src/backend/requirements.txt
pip install pytest pytest-django pytest-cov
```

2. **运行测试**
```bash
# 使用 pytest
python -m pytest src/backend/InvenTree/stock/test_api.py::StockItemAllocationSyncTest -v

# 或使用自定义脚本
python test_stock_allocation_fix.py
```

3. **验证代码质量**
```bash
# 检查语法
python -m py_compile src/backend/InvenTree/stock/models.py

# 运行 lint（如果配置了）
flake8 src/backend/InvenTree/stock/models.py
```

#### Docker 测试

1. **构建 Docker 镜像**
```bash
docker build . --target production --tag inventree-test -f contrib/container/Dockerfile
```

2. **运行 Docker 测试**
```bash
# 运行基本测试
docker run --rm inventree-test invoke version
docker run --rm inventree-test invoke --list

# 运行单元测试
docker run --rm inventree-test invoke dev.test --runtest=stock.test_api.StockItemAllocationSyncTest
```

3. **使用 docker-compose**
```bash
# 构建开发环境
docker compose --project-directory . -f contrib/container/dev-docker-compose.yml build

# 运行测试
docker compose --project-directory . -f contrib/container/dev-docker-compose.yml run --rm inventree-dev-server invoke dev.test --runtest=stock.test_api.StockItemAllocationSyncTest
```

## 兼容性说明

### Stable 分支兼容性

所有修改都考虑了与 stable 分支的兼容性：

1. **使用现有的模型和方法**
   - `StockItem` 模型
   - `SalesOrderAllocation` 模型
   - `SalesOrderLineItem` 模型

2. **遵循现有代码模式**
   - 使用 Django ORM 查询
   - 遵循事务处理模式
   - 使用现有的日志系统

3. **向后兼容**
   - 新增的方法使用私有命名（`_update_sales_order_allocations`）
   - 不修改现有 API 接口
   - 不影响现有功能

### 测试覆盖

添加了完整的测试用例：

1. **test_quantity_decrease_updates_allocations**
   - 验证库存减少时分配自动更新

2. **test_quantity_increase_no_allocation_change**
   - 验证库存增加时分配不变

3. **test_quantity_decrease_removes_excess_allocations**
   - 验证库存大幅减少时删除多余分配

## GitHub Actions 工作流

### 主要工作流

1. **Docker 工作流** (`.github/workflows/docker.yaml`)
   - 在 push 到 master/stable 分支时触发
   - 在 PR 到 master/stable 分支时触发
   - 构建、测试和发布 Docker 镜像

2. **测试工作流** (`.github/workflows/test_stock_allocation.yml`)
   - 专门测试库存分配同步功能
   - 在任何 push 或 PR 时触发
   - 运行单元测试和自定义测试脚本

### 触发条件

```yaml
on:
  push:
    branches:
      - "master"
      - "stable"
  pull_request:
    branches:
      - "master"
      - "stable"
```

## 修改的文件清单

### 后端文件
1. `src/backend/InvenTree/stock/models.py`
   - 修改 `StockItem.save()` 方法
   - 添加 `_update_sales_order_allocations()` 方法

2. `src/backend/InvenTree/stock/test_api.py`
   - 添加 `StockItemAllocationSyncTest` 测试类

### 前端文件
3. `src/frontend/src/hooks/UseForm.tsx`
   - 支持异步 `onFormSuccess` 回调

4. `src/frontend/src/components/forms/ApiForm.tsx`
   - 支持异步表单提交处理

5. `src/frontend/src/pages/stock/StockDetail.tsx`
   - 等待数据刷新完成后再关闭模态框

### 配置文件
6. `pytest.ini`（新增）
   - pytest 配置

7. `.github/workflows/test_stock_allocation.yml`（新增）
   - 专门的测试工作流

8. `.github/workflows/docker.yaml`
   - 添加 stable 分支支持
   - 添加测试步骤

### 测试文件
9. `test_stock_allocation_fix.py`（新增）
   - 独立测试脚本

## 验证步骤

### 1. 本地验证

```bash
# 1. 检查语法
python -m py_compile src/backend/InvenTree/stock/models.py

# 2. 运行测试
python test_stock_allocation_fix.py

# 3. 运行 pytest
python -m pytest src/backend/InvenTree/stock/test_api.py::StockItemAllocationSyncTest -v
```

### 2. Docker 验证

```bash
# 1. 构建镜像
docker build . --target production --tag inventree-test -f contrib/container/Dockerfile

# 2. 运行测试
docker run --rm inventree-test invoke dev.test --runtest=stock.test_api.StockItemAllocationSyncTest
```

### 3. GitHub Actions 验证

1. 推送代码到 GitHub
2. 创建 PR 到 master 或 stable 分支
3. 查看 Actions 标签页的测试结果
4. 确保所有测试通过

## 常见问题

### Q: pytest 报告 "No module named 'InvenTree'"

**A:** 确保 Python 路径正确设置：
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src/backend/InvenTree"
```

### Q: Django 测试报告 "AppRegistryNotReady"

**A:** 确保在导入模型前初始化 Django：
```python
import django
django.setup()
```

### Q: Docker 测试失败

**A:** 检查 Docker 镜像是否正确构建：
```bash
docker build . --target production --tag inventree-test -f contrib/container/Dockerfile
docker run --rm inventree-test invoke version
```

## 总结

通过以上修改和配置，我们：

1. ✅ 修复了 pytest 和 py_compile 执行失败的问题
2. ✅ 提供了多种测试运行方式
3. ✅ 配置了 GitHub Actions 工作流
4. ✅ 确保了 stable 分支兼容性
5. ✅ 添加了完整的测试覆盖
6. ✅ 提供了详细的验证步骤

所有修改都遵循 InvenTree 的代码规范和最佳实践，确保代码质量和可维护性。