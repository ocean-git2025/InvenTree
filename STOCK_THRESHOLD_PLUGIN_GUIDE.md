# 库存阈值插件使用指南

## 概述

本插件通过 StockItem 的 `custom_data` 字段存储库存阈值，当库存数量低于阈值时，在库存列表页面显示红色警示标记。

## 快速开始

### 1. 安装依赖和迁移

```powershell
cd d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\backend
.\setup_threshold_plugin.ps1
```

### 2. 启动开发服务器

**启动后端服务器（终端1）：**
```powershell
cd src\backend
python manage.py runserver
```

后端运行在：http://localhost:8000

**启动前端服务器（终端2）：**
```powershell
cd src\frontend
npm install
npm start
```

前端运行在：http://localhost:3000

### 3. 创建超级管理员

```powershell
cd src\backend
python manage.py createsuperuser
```

按照提示输入用户名、邮箱和密码。

## 设置库存阈值

### 方法1：通过 Django Admin 设置

1. 访问 http://localhost:8000/admin/
2. 使用超级管理员账户登录
3. 导航到 **Stock** -> **Stock items**
4. 点击要编辑的库存项目
5. 滚动到 **Custom data** 字段
6. 输入阈值 JSON：
   ```json
   {"threshold": 10}
   ```
7. 点击 **Save**

### 方法2：通过 Django Shell 设置

```powershell
cd src\backend
python manage.py shell
```

在 shell 中执行：

```python
# 导入 StockItem 模型
from InvenTree.stock.models import StockItem

# 获取库存项目（替换 pk 为你的库存项目ID）
stock_item = StockItem.objects.get(pk=1)

# 设置阈值为 10
stock_item.set_custom_data({'threshold': 10})

# 保存修改
stock_item.save()

# 验证阈值已设置
print("阈值已设置为:", stock_item.get_custom_data().get('threshold'))
```

### 方法3：通过 API 设置

#### 创建库存项目时设置阈值

```bash
curl -X POST http://localhost:8000/api/stock/item/ \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "part": 1,
    "quantity": 5,
    "custom_data": {"threshold": 10}
  }'
```

#### 更新现有库存项目的阈值

```bash
curl -X PATCH http://localhost:8000/api/stock/item/1/ \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_data": {"threshold": 10}
  }'
```

#### 仅更新阈值（保留其他 custom_data）

```bash
curl -X PATCH http://localhost:8000/api/stock/item/1/ \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_data": {"threshold": 10}
  }'
```

## 验证红色警示

### 1. 创建测试数据

```powershell
cd src\backend
python manage.py shell
```

```python
from InvenTree.stock.models import StockItem
from InvenTree.part.models import Part

# 确保存在零件（如果不存在则创建）
part, created = Part.objects.get_or_create(
    name="测试电阻",
    description="用于测试的100Ω电阻",
    defaults={
        "active": True,
        "virtual": False,
    }
)

# 创建库存项目1：数量 5，阈值 10（应该显示红色）
stock1 = StockItem.objects.create(
    part=part,
    quantity=5,
)
stock1.set_custom_data({'threshold': 10})
stock1.save()

# 创建库存项目2：数量 15，阈值 10（不显示红色）
stock2 = StockItem.objects.create(
    part=part,
    quantity=15,
)
stock2.set_custom_data({'threshold': 10})
stock2.save()

# 创建库存项目3：数量 8，无阈值（不显示红色）
stock3 = StockItem.objects.create(
    part=part,
    quantity=8,
)
stock3.save()

print(f"创建的库存项目:")
print(f"  ID {stock1.pk}: 数量 {stock1.quantity}, 阈值 {stock1.get_custom_data().get('threshold', '无')}")
print(f"  ID {stock2.pk}: 数量 {stock2.quantity}, 阈值 {stock2.get_custom_data().get('threshold', '无')}")
print(f"  ID {stock3.pk}: 数量 {stock3.quantity}, 阈值 {stock3.get_custom_data().get('threshold', '无')}")
```

### 2. 查看红色警示

1. 访问 http://localhost:3000/stock/
2. 登录系统
3. 查看库存列表

**预期结果：**
- 库存项目1（数量5，阈值10）：显示 **红色**
- 库存项目2（数量15，阈值10）：显示正常颜色
- 库存项目3（数量8，无阈值）：显示正常颜色

## 验证 API 响应

```bash
curl http://localhost:8000/api/stock/item/1/ \
  -H "Authorization: Token YOUR_API_TOKEN"
```

响应示例：

```json
{
  "pk": 1,
  "part": 1,
  "quantity": 5,
  "custom_data": {
    "threshold": 10
  },
  "threshold": 10,
  "below_threshold": true,
  // ... 其他字段
}
```

## 故障排除

### 插件未加载

检查插件是否已正确注册：

```powershell
cd src\backend
python manage.py shell
```

```python
from InvenTree.plugin.registry import registry

plugins = registry.plugins
print("已加载的插件:")
for plugin in plugins:
    print(f"  - {plugin.NAME} (v{plugin.VERSION})")
```

### 阈值未显示

检查 `custom_data` 是否已正确设置：

```python
from InvenTree.stock.models import StockItem

stock_item = StockItem.objects.get(pk=1)
print("Custom Data:", stock_item.get_custom_data())
print("阈值:", stock_item.get_custom_data().get('threshold'))
```

### 红色标记未显示

1. 检查浏览器控制台是否有 JavaScript 错误
2. 验证 API 响应中是否包含 `threshold` 和 `below_threshold` 字段
3. 确保前端代码已正确更新

## 高级用法

### 批量设置阈值

```powershell
cd src\backend
python manage.py shell
```

```python
from InvenTree.stock.models import StockItem

# 为所有库存项目设置默认阈值 5
for stock in StockItem.objects.all():
    if 'threshold' not in stock.get_custom_data():
        stock.set_custom_data({'threshold': 5})
        stock.save()
        print(f"为库存项目 {stock.pk} 设置阈值: 5")
```

### 批量修改阈值

```python
from InvenTree.stock.models import StockItem

# 将所有阈值从 5 修改为 10
for stock in StockItem.objects.all():
    current_threshold = stock.get_custom_data().get('threshold')
    if current_threshold == 5:
        stock.set_custom_data({'threshold': 10})
        stock.save()
        print(f"库存项目 {stock.pk} 阈值从 5 修改为 10")
```

## 清理测试数据

```powershell
cd src\backend
python manage.py shell
```

```python
from InvenTree.stock.models import StockItem

# 删除所有库存项目的阈值
for stock in StockItem.objects.all():
    custom_data = stock.get_custom_data()
    if 'threshold' in custom_data:
        del custom_data['threshold']
        stock.set_custom_data(custom_data)
        stock.save()

print("所有库存项目的阈值已删除")
```

---

**完成！** 你已成功使用库存阈值插件。
