# 库存阈值警示功能验证步骤

## 功能概述

本插件为InvenTree添加库存阈值提醒功能，当库存物品的数量低于设定的最低库存阈值时，前端表格将显示红色警示标记。

## 前置条件

1. InvenTree已安装并正常运行
2. 插件已正确安装和启用
3. 前端代码已部署（StockItemTable.tsx已修改）
4. 拥有InvenTree管理员权限

## 验证步骤

### 步骤1：配置Part的最低库存阈值

1. 登录InvenTree管理界面
2. 进入 **Parts** 页面，选择一个需要设置阈值的零件
3. 进入零件详情页面，点击 **Edit**
4. 找到 **Minimum Stock** 字段，设置一个正数值（例如：10）
5. 保存更改

### 步骤2：创建/查看Stock Item

1. 进入零件详情页面，点击 **Stock** 标签
2. 查看现有的Stock Item列表，或创建新的Stock Item
3. 确保至少有一个Stock Item的数量低于或等于设置的minimum_stock值

### 步骤3：验证前端警示效果

1. 导航到 **Stock > Stock Items** 页面
2. 在表格中找到对应的Stock Item
3. **验证点**：
   - 当 `quantity <= minimum_stock` 时，Stock列显示**红色**文字
   - 鼠标悬停时，弹出卡片显示 **"Minimum stock: X"** 的红色提示
   - 当 `quantity > minimum_stock` 时，显示正常颜色

### 步骤4：测试不同场景

| 场景 | 操作 | 预期结果 |
|------|------|----------|
| 库存高于阈值 | 设置minimum_stock=5，quantity=10 | 正常颜色显示，无红色警示 |
| 库存等于阈值 | 设置minimum_stock=10，quantity=10 | 红色显示，显示"Minimum stock: 10" |
| 库存低于阈值 | 设置minimum_stock=10，quantity=5 | 红色显示，显示"Minimum stock: 10" |
| 未设置阈值 | minimum_stock为空或0 | 正常颜色显示，无红色警示 |
| 已分配库存 | allocated > 0但quantity > minimum_stock | 橙色分配提示，无红色阈值警示 |
| 库存为0 | quantity=0 | 红色显示（depleted状态） |

### 步骤5：验证插件仪表板（可选）

1. 登录后查看仪表板
2. 查找 **Stock Threshold Alert** 面板
3. 验证面板显示所有低于阈值的Stock Item列表

## 代码验证

### 前端代码位置

- **文件**：`src/frontend/src/tables/stock/StockItemTable.tsx`
- **行号**：约第196-204行
- **关键逻辑**：
```typescript
const min_stock = part?.minimum_stock ?? 0;
if (min_stock > 0 && quantity <= min_stock) {
  color = 'red';
  extra.push(
    <Text key='min-stock' size='sm' c='red'>
      {`${t`Minimum stock`}: ${formatDecimal(min_stock)}`}
    </Text>
  );
}
```

### 后端插件位置

- **文件**：`stock_threshold_alert/__init__.py`
- **关键方法**：`is_below_threshold()`, `get_threshold_value()`

## CI/CD验证

### GitHub Actions测试

1. 推送代码到GitHub仓库
2. 查看 **Actions** 标签页
3. 验证 **Plugin Test** workflow成功运行
4. 检查两个matrix job都通过：
   - `inventree-version: stable`
   - `inventree-version: latest`

### 本地测试

```bash
# 安装依赖
pip install -e .

# 运行插件导入测试
python -c "
from stock_threshold_alert import StockThresholdPlugin
print(f'Plugin: {StockThresholdPlugin.NAME}')
print(f'Version: {StockThresholdPlugin.VERSION}')
"

# 运行代码质量检查
flake8 stock_threshold_alert/ --max-line-length=127 --exclude=static/
black --check stock_threshold_alert/ --exclude=static/
```

## 常见问题排查

### 问题1：红色警示不显示

**可能原因**：
- minimum_stock未设置或为0
- 前端代码未正确部署
- 浏览器缓存未清除

**解决方法**：
1. 确认Part的minimum_stock字段值 > 0
2. 重新构建前端：`invoke frontend-build`
3. 清除浏览器缓存（Ctrl+Shift+R）

### 问题2：GitHub Actions失败

**可能原因**：
- Docker镜像拉取失败
- 依赖安装问题
- 代码格式问题

**解决方法**：
1. 检查workflow日志中的具体错误
2. 确保`requirements.txt`和`setup.py`配置正确
3. 运行`black`和`flake8`检查代码格式

## 验证结果记录

| 验证项 | 状态 | 备注 |
|--------|------|------|
| Part minimum_stock配置 | ☐ | |
| Stock Item表格红色显示 | ☐ | |
| 悬停卡片阈值提示 | ☐ | |
| 不同场景测试 | ☐ | |
| GitHub Actions测试通过 | ☐ | |
| 本地代码质量检查 | ☐ | |

**验证完成日期**：___________
**验证人员**：___________
