# 库存阈值插件 - 本地启动验证步骤

## 1. 准备工作

### 1.1 安装依赖和执行迁移

打开 PowerShell 并运行以下命令：

```powershell
cd d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\backend
.\setup_threshold_plugin.ps1
```

或者手动执行：

```powershell
cd d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
python manage.py migrate
```

### 1.2 创建插件数据库表

由于我们创建了新的 `StockThresholdSetting` 模型，需要创建数据库迁移：

```powershell
python manage.py makemigrations plugin
python manage.py migrate
```

## 2. 启动开发服务器

### 2.1 启动后端服务器

在一个终端窗口中运行：

```powershell
cd d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\backend
python manage.py runserver
```

后端服务器将在 `http://localhost:8000` 启动

### 2.2 启动前端开发服务器

在另一个终端窗口中运行：

```powershell
cd d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\frontend
npm install
npm start
```

前端服务器将在 `http://localhost:3000` 启动

## 3. 配置库存阈值

### 3.1 创建超级管理员账户（如果还没有）

```powershell
cd d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\backend
python manage.py createsuperuser
```

按照提示输入用户名、邮箱和密码

### 3.2 登录后台管理

访问 `http://localhost:8000/admin/` 并使用超级管理员账户登录

### 3.3 创建测试库存项目

1. 首先创建一个零件（Part）
   - 导航到 "Parts" -> "Parts" -> "Add Part"
   - 填写零件名称（例如："电阻 100Ω"）
   - 选择零件类别，填写其他信息
   - 点击 "Save"

2. 创建库存项目（StockItem）
   - 导航到 "Stock" -> "Stock Items" -> "Add Stock Item"
   - 选择刚才创建的零件
   - 设置库存数量（例如：5）
   - 填写其他必要信息
   - 点击 "Save"

### 3.4 配置库存阈值

通过 Django admin 或 API 设置库存阈值：

**方法1：通过 Django Admin**

1. 导航到 "Plugin" -> "Stock threshold settings" -> "Add Stock threshold setting"
2. 选择刚才创建的库存项目
3. 设置阈值（例如：10）
4. 点击 "Save"

**方法2：通过 Django Shell**

```powershell
cd d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\backend
python manage.py shell
```

在 shell 中执行：

```python
from InvenTree.stock.models import StockItem
from InvenTree.plugin.samples.integration.stock_threshold_plugin import StockThresholdSetting

# 获取库存项目（替换为你的库存项目ID）
stock_item = StockItem.objects.get(pk=1)

# 创建或更新阈值设置
setting, created = StockThresholdSetting.objects.get_or_create(
    stock_item=stock_item,
    defaults={'threshold': 10}
)

if not created:
    setting.threshold = 10
    setting.save()

print(f"阈值设置为: {setting.threshold}")
```

## 4. 验证红色警示标记

### 4.1 访问库存列表页面

1. 打开浏览器访问 `http://localhost:3000/stock/`
2. 登录系统（使用超级管理员账户）
3. 导航到 "Stock" -> "Stock Items"

### 4.2 验证红色警示

- 你应该看到刚才创建的库存项目
- 由于库存数量（5）低于阈值（10），该项目的库存数量应该显示为 **红色**
- 检查列表中的其他项目，如果它们的数量低于各自的阈值，也会显示红色

### 4.3 测试不同场景

**场景1：数量等于阈值**
- 将库存数量修改为 10
- 刷新页面，数量应该显示为正常颜色（不是红色）

**场景2：数量高于阈值**
- 将库存数量修改为 15
- 刷新页面，数量应该显示为正常颜色（不是红色）

**场景3：移除阈值**
- 删除该库存项目的阈值设置
- 刷新页面，数量应该显示为正常颜色（不是红色）

## 5. 验证 API 响应

你也可以通过 API 验证阈值信息：

```bash
curl http://localhost:8000/api/stock/item/1/ -H "Authorization: Token YOUR_API_TOKEN"
```

响应中应该包含：
```json
{
  "pk": 1,
  "quantity": 5,
  "threshold": 10,
  "below_threshold": true,
  // ... 其他字段
}
```

## 6. 故障排除

### 6.1 插件未加载

- 检查 `src/backend/InvenTree/plugin/samples/integration/stock_threshold_plugin.py` 文件是否存在
- 确保 Django 服务器已重启
- 检查服务器日志是否有插件加载错误

### 6.2 阈值未显示

- 确保已运行 `python manage.py migrate`
- 检查数据库中是否存在 `stock_threshold_setting` 表
- 验证阈值是否正确保存到数据库

### 6.3 红色标记未显示

- 确保前端代码已更新（`StockItemTable.tsx` 中的修改）
- 检查浏览器控制台是否有 JavaScript 错误
- 验证 API 响应中是否包含 `threshold` 和 `below_threshold` 字段

## 7. 清理测试数据

```powershell
cd d:\mypython\pythonProject\TraeCN_Projects\inventree-A\src\backend
python manage.py shell
```

```python
from InvenTree.plugin.samples.integration.stock_threshold_plugin import StockThresholdSetting

# 删除所有阈值设置
StockThresholdSetting.objects.all().delete()
print("所有阈值设置已删除")
```

---

**完成！** 你已经成功安装、配置并验证了库存阈值插件。
