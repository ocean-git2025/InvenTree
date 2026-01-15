# 本地验证库存阈值插件

本文档提供本地启动后验证红色警示标记的具体操作步骤。

## 前提条件

- 已完成插件开发和代码修改
- 已安装所有依赖包
- 已完成数据库迁移

## 启动服务

### 方法1：使用快速启动脚本（推荐）

在 `src/backend` 目录下运行：

```powershell
..\quick_start.ps1
```

这将自动执行：
- 安装依赖
- 执行数据库迁移
- 启动开发服务器（默认端口8000）

### 方法2：使用详细启动脚本

```powershell
..\start_backend.ps1
```

支持的参数：
- `-SkipInstall`：跳过依赖安装
- `-SkipMigrate`：跳过数据库迁移
- `-Port 8080`：指定端口（默认8000）

### 方法3：手动启动

```powershell
# 1. 安装依赖
pip install -r ../requirements.txt

# 2. 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 3. 创建管理员账户（如果还没有）
python manage.py createsuperuser

# 4. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

## 验证步骤

### 步骤1：登录后台

1. 打开浏览器访问：`http://localhost:8000`
2. 使用管理员账户登录

### 步骤2：确保插件已启用

1. 点击左侧菜单 **Settings**（设置）
2. 选择 **Plugins**（插件）
3. 找到 `StockThresholdPlugin`
4. 确保插件处于 **Enabled**（已启用）状态
5. 如果未启用，点击启用按钮并保存

### 步骤3：创建/选择一个零件（Part）

1. 点击左侧菜单 **Parts**（零件）
2. 点击 **Parts** 选项
3. 点击右上角的 **+ New Part**（新建零件）按钮
4. 填写必要信息：
   - **Name**（名称）：例如 "电阻 100Ω"
   - **Description**（描述）：可选
   - **Part Category**（零件类别）：选择或创建一个类别
   - **Active**（激活）：勾选
5. 点击 **Save**（保存）

### 步骤4：创建库存项目（Stock Item）

1. 在零件详情页面，点击 **Create Stock Item**（创建库存项目）
2. 填写信息：
   - **Quantity**（数量）：输入一个测试值，例如 `5`
   - **Location**（位置）：选择或创建一个仓库位置
3. 点击 **Save**（保存）

### 步骤5：设置库存阈值

1. 在库存项目列表中，找到刚创建的库存项目
2. 点击进入库存项目详情页面
3. 在 **Custom Data**（自定义数据）区域，点击 **Edit**（编辑）
4. 添加自定义字段：
   - 键（Key）：`stock_threshold`
   - 值（Value）：输入阈值，例如 `10`
   - 类型：选择 **Number**（数字）
5. 点击 **Save**（保存）

### 步骤6：验证红色警示标记

1. 点击左侧菜单 **Stock**（库存）
2. 选择 **Stock Items**（库存项目）
3. 在库存列表中查看刚创建的库存项目

**预期结果**：
- 由于当前库存数量（5）低于阈值（10），该库存项目的状态标记应为 **红色**
- 鼠标悬停在状态标记上，应显示提示文本："Stock level is below threshold"（库存水平低于阈值）

### 步骤7：测试不同场景

#### 场景1：库存数量等于阈值
1. 编辑库存项目，将数量改为 `10`
2. 返回库存列表
3. **预期结果**：红色警示标记消失

#### 场景2：库存数量高于阈值
1. 编辑库存项目，将数量改为 `15`
2. 返回库存列表
3. **预期结果**：红色警示标记消失

#### 场景3：移除阈值
1. 编辑库存项目，删除 `stock_threshold` 自定义字段
2. 返回库存列表
3. **预期结果**：红色警示标记消失

#### 场景4：设置不同阈值
1. 设置阈值为 `3`
2. 当前数量为 `5`
3. **预期结果**：红色警示标记不显示（5 > 3）
4. 将数量改为 `2`
5. **预期结果**：红色警示标记显示（2 < 3）

## API 验证（可选）

可以通过API接口验证低库存标记：

### 获取所有库存项目

```bash
curl http://localhost:8000/api/stock/item/
```

查看响应中的 `low_stock` 字段，对于低库存项目应为 `true`。

### 仅获取低库存项目

```bash
curl "http://localhost:8000/api/stock/item/?low_stock=true"
```

应只返回库存数量低于阈值的项目。

### 通过插件API获取阈值信息

```bash
curl http://localhost:8000/api/plugin/stockthreshold/
```

返回所有设置了阈值的库存项目及其阈值信息。

## 常见问题排查

### 问题1：红色警示标记不显示

**可能原因**：
- 插件未启用
- 未设置 `stock_threshold` 自定义字段
- 库存数量高于或等于阈值
- 前端缓存未清除

**解决方法**：
1. 检查插件是否启用（Settings > Plugins）
2. 确认库存项目已设置 `stock_threshold` 自定义字段
3. 确保库存数量确实低于阈值
4. 清除浏览器缓存或强制刷新页面（Ctrl+F5）

### 问题2：无法登录后台

**解决方法**：
```powershell
# 创建新的管理员账户
python manage.py createsuperuser
```

### 问题3：数据库迁移失败

**解决方法**：
```powershell
# 重置数据库（注意：这会删除所有数据）
python manage.py flush

# 重新执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 问题4：端口8000已被占用

**解决方法**：
```powershell
# 使用其他端口
python manage.py runserver 0.0.0.0:8080
```

或使用快速启动脚本：
```powershell
..\quick_start.ps1 -Port 8080
```

## 总结

通过以上步骤，您应该能够成功验证库存阈值插件的核心功能：

✅ 为库存项目设置自定义阈值
✅ 当库存低于阈值时显示红色警示标记
✅ 当库存高于或等于阈值时不显示警示标记
✅ 移除阈值后警示标记消失

如果所有步骤都能顺利完成，说明插件已正确安装并正常工作。