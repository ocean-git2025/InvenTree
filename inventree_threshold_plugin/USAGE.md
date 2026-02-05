# InvenTree Stock Threshold Plugin - Usage Guide

## Overview

This plugin adds custom stock threshold functionality to InvenTree, allowing you to:
- Set minimum stock levels for individual StockItems
- Get visual warnings when stock falls below threshold
- Access threshold data via API

## Installation

### Method 1: Direct Installation

```bash
# In your InvenTree environment
pip install inventree-threshold-plugin
```

### Method 2: Development Installation

```bash
git clone <repository-url>
cd inventree-threshold-plugin
pip install -e .
```

### Method 3: Docker Installation

Add to your `plugins.txt`:
```
inventree-threshold-plugin
```

Or mount the plugin directory in your docker-compose:
```yaml
services:
  inventree-server:
    volumes:
      - ./inventree_threshold_plugin:/home/inventree/plugin:ro
    environment:
      - INVENTREE_PLUGINS_ENABLED=True
```

## Configuration

### Enable Plugin

1. Go to **Settings > Plugin Settings**
2. Enable **Plugins**
3. Restart InvenTree
4. The plugin should appear in the plugin list

### Plugin Settings

Navigate to **Admin > Plugin Configuration > Stock Threshold Plugin**:

- **Enable Threshold Warnings**: Toggle UI warnings
- **Default Threshold**: Set default value (default: 10)
- **Show Low Stock Badge**: Enable visual badges

## Setting Thresholds

### Via Django Admin

1. Go to **Admin > Stock Threshold Plugin > Stock Item Thresholds**
2. Click **Add Stock Item Threshold**
3. Select a StockItem
4. Set threshold value
5. Enable/disable as needed
6. Save

### Via API

```bash
# Create a threshold
curl -X POST http://your-inventree/api/plugin/stock-threshold/threshold/ \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_item": 123,
    "threshold": "25.00",
    "enabled": true
  }'

# Get threshold status for a stock item
curl http://your-inventree/api/plugin/stock-threshold/stock-item/123/threshold-status/ \
  -H "Authorization: Token YOUR_API_TOKEN"

# List all low stock items
curl http://your-inventree/api/plugin/stock-threshold/low-stock/ \
  -H "Authorization: Token YOUR_API_TOKEN"
```

## UI Integration

### Low Stock Indicators

When a StockItem is below its threshold:
- **Stock Table**: Quantity column shows red text with warning icon
- **Stock Detail Page**: Badge indicates low stock status
- **Dashboard**: Low stock items appear in notifications

### Customizing Display

The plugin provides JavaScript functions for custom rendering:

```javascript
// Check if stock item is below threshold
const isLowStock = record.threshold_data?.is_low_stock;

// Get threshold value
const threshold = record.threshold_data?.threshold;

// Get quantity below threshold
const below = record.threshold_data?.quantity_below_threshold;
```

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plugin/stock-threshold/threshold/` | GET | List all thresholds |
| `/api/plugin/stock-threshold/threshold/` | POST | Create new threshold |
| `/api/plugin/stock-threshold/threshold/<pk>/` | GET | Get threshold details |
| `/api/plugin/stock-threshold/threshold/<pk>/` | PUT/PATCH | Update threshold |
| `/api/plugin/stock-threshold/threshold/<pk>/` | DELETE | Delete threshold |
| `/api/plugin/stock-threshold/stock-item/<pk>/threshold-status/` | GET | Get stock item threshold status |
| `/api/plugin/stock-threshold/low-stock/` | GET | List all low stock items |

### Response Format

**Threshold Status Response:**
```json
{
  "has_threshold": true,
  "threshold": "25.00000",
  "enabled": true,
  "is_low_stock": true,
  "quantity_below_threshold": "5.00000"
}
```

**Low Stock Items Response:**
```json
[
  {
    "pk": 1,
    "stock_item": 123,
    "threshold": "25.00000",
    "enabled": true,
    "is_low_stock": true,
    "quantity_below_threshold": "5.00000",
    "created": "2024-01-15T10:30:00Z",
    "updated": "2024-01-15T10:30:00Z"
  }
]
```

## Integration with StockItem Serializer

To include threshold data in StockItem API responses, extend your serializer:

```python
from inventree_threshold_plugin.integration import get_stock_item_threshold_data

class ExtendedStockItemSerializer(StockItemSerializer):
    threshold_data = serializers.SerializerMethodField()
    
    def get_threshold_data(self, obj):
        return get_stock_item_threshold_data(obj)
```

## Automation Examples

### Check Low Stock Daily

```python
# In a scheduled task or management command
from inventree_threshold_plugin.models import StockItemThreshold

low_stock_items = StockItemThreshold.objects.filter(
    enabled=True,
    stock_item__quantity__lt=models.F('threshold')
)

for threshold in low_stock_items:
    # Send notification, email, etc.
    print(f"Low stock: {threshold.stock_item.part.name}")
```

### Auto-Create Thresholds

```python
# Create default thresholds for new parts
from inventree_threshold_plugin.models import StockItemThreshold

def create_default_threshold(stock_item, default_value=10):
    threshold, created = StockItemThreshold.objects.get_or_create(
        stock_item=stock_item,
        defaults={
            'threshold': default_value,
            'enabled': True
        }
    )
    return threshold
```

## Troubleshooting

### Plugin Not Loading

1. Check plugin is installed: `pip list | grep inventree-threshold`
2. Verify plugins are enabled in settings
3. Check plugin registry: Admin > Plugins

### Threshold Not Showing

1. Verify threshold is created and enabled
2. Check API response: `/api/plugin/stock-threshold/stock-item/<pk>/threshold-status/`
3. Ensure plugin settings allow warnings

### Database Issues

Run migrations manually:
```bash
python manage.py migrate inventree_threshold_plugin
```

## Compatibility

- InvenTree: 0.12.x - 0.15.x (stable branch)
- Python: 3.9, 3.10, 3.11, 3.12
- Django: 4.2+

## Support

For issues and feature requests, please use the GitHub issue tracker.
