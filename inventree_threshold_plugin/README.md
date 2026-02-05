# InvenTree Stock Threshold Plugin

A plugin for InvenTree that adds custom stock threshold warnings for StockItem models.

## Features

- **Custom Stock Thresholds**: Configure minimum stock levels for individual StockItem instances
- **Low Stock Warnings**: Visual indicators in the UI when stock falls below threshold
- **API Integration**: Full REST API for threshold management
- **Admin Interface**: Django admin integration for easy configuration

## Installation

### From Source

```bash
git clone https://github.com/yourusername/inventree-threshold-plugin.git
cd inventree-threshold-plugin
pip install .
```

### Using pip

```bash
pip install inventree-threshold-plugin
```

## Configuration

1. Install the plugin in your InvenTree environment
2. Enable the plugin in InvenTree settings
3. Configure thresholds via the Django admin or API

## Plugin Settings

The plugin provides the following settings:

- **Enable Threshold Warnings**: Enable/disable low stock warnings in the UI
- **Default Threshold**: Default threshold value for new configurations
- **Show Low Stock Badge**: Display visual badges for low stock items

## API Endpoints

The plugin adds the following API endpoints:

- `GET/POST /api/plugin/stock-threshold/threshold/` - List/Create thresholds
- `GET/PUT/DELETE /api/plugin/stock-threshold/threshold/<pk>/` - Retrieve/Update/Delete threshold
- `GET /api/plugin/stock-threshold/stock-item/<pk>/threshold-status/` - Get threshold status for a stock item
- `GET /api/plugin/stock-threshold/low-stock/` - Get all low stock items

## Usage

### Setting a Threshold

Via the Django Admin:
1. Navigate to Admin > Stock Threshold Plugin > Stock Item Thresholds
2. Click "Add Stock Item Threshold"
3. Select a StockItem and set the threshold value
4. Save

Via the API:
```bash
curl -X POST /api/plugin/stock-threshold/threshold/ \
  -H "Content-Type: application/json" \
  -d '{"stock_item": 1, "threshold": "10.00", "enabled": true}'
```

### Checking Low Stock Status

```bash
curl /api/plugin/stock-threshold/stock-item/1/threshold-status/
```

Response:
```json
{
  "has_threshold": true,
  "threshold": "10.00",
  "enabled": true,
  "is_low_stock": false,
  "quantity_below_threshold": 0
}
```

## Compatibility

- InvenTree: 0.12.x, 0.13.x, 0.14.x, 0.15.x (stable branch)
- Python: 3.9, 3.10, 3.11, 3.12
- Django: 4.2+

## Development

### Running Tests

```bash
pip install -e .
cd tests
python -m pytest
```

### Docker Testing

The plugin includes GitHub Actions workflows for testing against the latest InvenTree Docker image.

## License

MIT License - see LICENSE file for details.
