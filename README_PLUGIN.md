# InvenTree Stock Threshold Alert Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/license/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![InvenTree](https://img.shields.io/badge/InvenTree-0.15.0+-green.svg)](https://inventree.org/)

## 概述

**Stock Threshold Alert** 是一个为 InvenTree 库存管理系统开发的插件，用于在库存物品数量低于配置的阈值时提供警报提示。

## 功能特性

- **阈值警报**：当库存物品数量低于设定阈值时自动显示警报
- **灵活配置**：支持全局默认阈值和单个物品自定义阈值
- **仪表板显示**：在仪表板中显示低于阈值的库存物品概览
- **自定义面板**：在库存物品详情页显示阈值状态面板
- **事件监听**：监听库存变化事件，实时更新阈值状态
- **用户设置**：用户可自定义是否显示警报

## 安装

### 前置要求

- InvenTree 版本 >= 0.15.0
- Python 版本 >= 3.9

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/inventree/inventree-stock-threshold-alert.git
cd inventree-stock-threshold-alert
```

2. **安装插件**

```bash
pip install -e .
```

或者直接从 PyPI 安装：

```bash
pip install inventree-stock-threshold-alert
```

3. **启用插件**

在 InvenTree 管理界面中：
- 进入 **设置** -> **插件**
- 找到 `Stock Threshold Alert` 插件
- 点击启用

## 配置

### 插件全局设置

| 设置项 | 描述 | 默认值 |
|--------|------|--------|
| `DEFAULT_THRESHOLD` | 默认最低库存阈值 | 10 |
| `ENABLED` | 启用插件 | True |

### 用户设置

| 设置项 | 描述 | 默认值 |
|--------|------|--------|
| `SHOW_ALERTS` | 在库存列表中显示警报 | True |

### 单个物品阈值设置

可以通过库存物品的元数据设置单个物品的阈值：

```python
from stock.models import StockItem

item = StockItem.objects.get(pk=1)
item.set_metadata('threshold', 50)  # 设置阈值为 50
```

## 使用说明

### 查看仪表板警报

插件会在仪表板中显示一个"Low Stock Alert"卡片，列出所有低于阈值的库存物品。

### 查看物品详情

在库存物品详情页，"Stock Threshold"面板会显示：
- 当前库存数量
- 配置的阈值
- 是否低于阈值的状态指示

### API 使用

插件通过 InvenTree 的插件系统工作，无需额外的 API 端点。

## 开发

### 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/inventree/inventree-stock-threshold-alert.git
cd inventree-stock-threshold-alert

# 安装开发依赖
pip install -e .[dev]
```

### 运行测试

```bash
pytest tests/ -v
```

### 代码质量检查

```bash
# 代码格式检查
black --check stock_threshold_alert/

# 导入排序检查
isort --check-only stock_threshold_alert/

# 代码风格检查
flake8 stock_threshold_alert/ --max-line-length=127
```

### 构建包

```bash
pip install build
python -m build
```

## CI/CD

项目使用 GitHub Actions 进行持续集成：

- **plugin-test.yml**：运行测试和代码质量检查
  - 在 `main` 和 `master` 分支的 push 和 pull request 时触发
  - 测试与 InvenTree Docker 镜像（stable 和 latest）的兼容性
  - 执行 flake8、black、isort 代码质量检查
  - 构建并上传插件包作为工件

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 支持

如有问题或建议，请在 [GitHub Issues](https://github.com/inventree/inventree-stock-threshold-alert/issues) 中提出。

## 作者

- **InvenTree** - [support@inventree.org](mailto:support@inventree.org)

## 致谢

- [InvenTree](https://inventree.org) - 开源库存管理系统
