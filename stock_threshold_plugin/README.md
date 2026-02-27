# Stock Threshold Plugin for InvenTree

A plugin that provides custom stock threshold functionality for StockItems, allowing users to set minimum stock levels and receive visual warnings when stock falls below the threshold.

## Features

- **Custom Thresholds**: Set individual minimum stock thresholds for each StockItem
- **Visual Warnings**: Red highlighting when quantity is below threshold
- **Panel Display**: Threshold information panel on stock item detail pages
- **Spotlight Action**: Quick access to view all low stock items
- **Compatible**: Works with InvenTree stable branch
- **No Database Changes**: Uses existing `MetadataMixin` on StockItem

## Installation

### Method 1: Manual Installation

1. Copy the `stock_threshold_plugin` folder to your InvenTree plugins directory:
   ```
   InvenTree/plugins/custom/stock_threshold_plugin/
   ```

2. Restart InvenTree

3. Enable the plugin in InvenTree admin settings (`/settings/admin/plugin/`)

### Method 2: pip Installation

```bash
pip install inventree-stock-threshold
```

## Configuration

### Plugin Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `ENABLE_THRESHOLD_WARNING` | Enable visual warning for low stock items | `True` |
| `DEFAULT_THRESHOLD` | Default minimum stock threshold | `0` |
| `WARNING_COLOR` | CSS color for low stock warning | `#ff4444` |
| `ENABLE_PANEL` | Show threshold panel on stock item detail page | `True` |

### Setting Custom Thresholds via API

Use the InvenTree API to set custom thresholds for individual StockItems:

```bash
# Set threshold for a stock item
PATCH /api/stock/{id}/
Content-Type: application/json

{
    "metadata": {
        "stock-threshold": {
            "threshold": 10
        }
    }
}
```

### Setting Custom Thresholds via Python

```python
from plugin import registry
from stock.models import StockItem

# Get the plugin instance
plugin = registry.get_plugin('stock-threshold')

# Get a stock item
stock_item = StockItem.objects.get(pk=1)

# Set custom threshold
plugin.set_stock_item_threshold(stock_item, 10)

# Check if below threshold
if plugin.is_below_threshold(stock_item):
    print(f"Stock item {stock_item.pk} is below threshold!")
```

## API Reference

### `get_stock_item_threshold(stock_item)`

Get the threshold value for a StockItem.

**Parameters:**
- `stock_item`: StockItem instance

**Returns:** `int` - The threshold value

### `set_stock_item_threshold(stock_item, threshold, user=None)`

Set a custom threshold for a StockItem.

**Parameters:**
- `stock_item`: StockItem instance
- `threshold`: Threshold value to set (int)
- `user`: Optional user performing the action

### `is_below_threshold(stock_item)`

Check if a StockItem is below its threshold.

**Parameters:**
- `stock_item`: StockItem instance

**Returns:** `bool` - True if quantity is below threshold

### `get_low_stock_items()`

Get all StockItems that are below their threshold.

**Returns:** `list` - List of StockItem pk values that are below threshold

## How It Works

### Metadata Storage

The plugin uses the existing `MetadataMixin` that StockItem already inherits from. Threshold values are stored in the `metadata` JSON field under the key `stock-threshold`:

```json
{
    "metadata": {
        "stock-threshold": {
            "threshold": 10
        },
        "other-plugin": {
            "data": "value"
        }
    }
}
```

This approach:
- Requires no database migrations
- Doesn't interfere with other plugins
- Works with existing InvenTree infrastructure

### UI Integration

The plugin uses `UserInterfaceMixin` to provide:

1. **Panel on Stock Item Detail Page**: Shows current quantity, threshold, and difference
2. **Spotlight Action**: Quick access to navigate to stock items

## Development

### Running Tests

```bash
# From InvenTree directory
python manage.py test stock_threshold_plugin.tests --verbosity=2
```

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting

```bash
black stock_threshold_plugin/
isort stock_threshold_plugin/
flake8 stock_threshold_plugin/ --max-line-length=120
```

## File Structure

```
stock_threshold_plugin/
├── __init__.py              # Plugin entry point
├── plugin.py                # Main plugin class
├── pyproject.toml           # Package configuration
├── README.md                # Documentation
├── static/
│   └── stock-threshold/
│       ├── threshold_panel.js    # Panel rendering
│       └── threshold_action.js   # Spotlight action
└── tests/
    ├── __init__.py
    └── test_plugin.py       # Unit tests
```

## Compatibility

- InvenTree stable branch
- Python 3.9+
- Django 4.2+

## License

MIT License
