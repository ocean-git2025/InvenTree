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

## 环境异常快速修复方案

### 🔧 启动前环境检查（推荐）

在启动服务前，建议先运行环境检查：

```powershell
# 检查 Python 版本
python --version

# 检查 pip 版本
pip --version

# 检查 PowerShell 版本
$PSVersionTable.PSVersion
```

**推荐版本**：
- Python: 3.8.0 或更高
- PowerShell: 5.1 或更高

---

### 🚨 快速修复清单

#### 1. Python 版本过低

**错误表现**：脚本提示 "Python 版本过低"

**修复方法**：
```powershell
# 方案1：使用 pyenv 管理版本（推荐）
# 安装 pyenv 后
pyenv install 3.10.0
pyenv global 3.10.0

# 方案2：从官网下载安装最新版本
# https://www.python.org/downloads/

# 验证
python --version
```

#### 2. pip 命令不可用

**错误表现**："pip : 无法将 'pip' 项识别为 cmdlet、函数、脚本文件或可运行程序的名称"

**修复方法**：
```powershell
# 方案1：使用 python -m pip
python -m pip --version

# 方案2：添加 Python 到 PATH
# Python 安装时勾选 "Add Python to PATH"
# 或手动添加：C:\Users\<用户名>\AppData\Local\Programs\Python\Python310\Scripts

# 方案3：重新安装 pip
python -m ensurepip --upgrade
```

#### 3. 依赖安装失败

**错误表现**：pip install 报错，常见于网络问题或依赖冲突

**修复方法**：
```powershell
# 方案1：使用国内镜像源
pip install -r ../requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 方案2：升级 pip 后重试
python -m pip install --upgrade pip
pip install -r ../requirements.txt

# 方案3：使用虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ../requirements.txt
```

#### 4. 数据库迁移错误

**错误表现**："No changes detected" 或数据库连接失败

**修复方法**：
```powershell
# 方案1：清理迁移文件并重新生成
# 注意：这会删除所有迁移历史
cd InvenTree\stock\migrations
Remove-Item -Path "0*.py" -Exclude "__init__.py"
cd ..\..
python manage.py makemigrations
python manage.py migrate

# 方案2：重置数据库（危险！会删除所有数据）
python manage.py flush
python manage.py migrate
python manage.py createsuperuser

# 方案3：检查数据库配置
# 编辑 InvenTree/settings.py
# 确认 DATABASES 配置正确
```

#### 5. 端口被占用

**错误表现**："Error: That port is already in use"

**修复方法**：
```powershell
# 方案1：查找并终止占用端口的进程
netstat -ano | findstr :8000
# 记下 PID，例如 1234
Stop-Process -Id 1234 -Force

# 方案2：使用其他端口
..\quick_start.ps1 -Port 8080

# 方案3：修改默认端口
# 在脚本中修改 Port 参数默认值
```

#### 6. Django 导入错误

**错误表现**："ModuleNotFoundError: No module named 'django'"

**修复方法**：
```powershell
# 方案1：重新安装依赖
pip install -r ../requirements.txt --force-reinstall

# 方案2：单独安装 Django
pip install django>=4.2.0

# 验证
python -c "import django; print(django.get_version())"
```

#### 7. 环境变量问题

**错误表现**：找不到 Python 或其他命令

**修复方法**：
```powershell
# 检查 PATH 环境变量
$env:Path -split ';'

# 添加 Python 到临时 PATH
$env:Path += ";C:\Users\<用户名>\AppData\Local\Programs\Python\Python310"
$env:Path += ";C:\Users\<用户名>\AppData\Local\Programs\Python\Python310\Scripts"

# 永久添加（需要管理员权限）
[Environment]::SetEnvironmentVariable('Path', $env:Path + ";C:\PythonPath", 'User')
```

#### 8. 文件权限问题

**错误表现**："Permission denied" 或无法写入文件

**修复方法**：
```powershell
# 方案1：以管理员身份运行 PowerShell
# 右键点击 PowerShell > 以管理员身份运行

# 方案2：修改文件夹权限
icacls . /grant Users:F /T

# 方案3：检查是否有文件被占用
# 关闭所有可能占用文件的程序（IDE、编辑器等）
```

#### 9. 虚拟环境问题

**错误表现**：虚拟环境激活失败或依赖安装到全局

**修复方法**：
```powershell
# 创建新的虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\Activate.ps1

# 确认已激活（命令行前应显示 (.venv)）

# 安装依赖
pip install -r ../requirements.txt

# 退出虚拟环境
Deactivate
```

#### 10. PowerShell 执行策略限制

**错误表现**："无法加载文件 xxx.ps1，因为在此系统上禁止运行脚本"

**修复方法**：
```powershell
# 查看当前执行策略
Get-ExecutionPolicy

# 设置执行策略（需要管理员权限）
Set-ExecutionPolicy RemoteSigned

# 或仅为当前用户设置
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 验证
Get-ExecutionPolicy -List
```

---

### ⚡ 一键修复脚本

已创建增强版启动脚本，包含自动环境检查和修复提示：

- `start_backend.ps1`：详细版本，支持参数选项，包含完整的版本检查
- `quick_start.ps1`：快速版本，单命令执行，包含基础环境检查

直接运行即可，脚本会自动检测问题并给出修复建议！

---

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