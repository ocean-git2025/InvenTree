# Stock Threshold Plugin for InvenTree

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The Stock Threshold plugin for InvenTree provides a comprehensive stock level monitoring system, allowing users to set minimum stock thresholds for parts and receive notifications when stock levels fall below these thresholds.

## Features

### Core Functionality

1. **Stock Threshold Configuration**
   - Set minimum stock thresholds for individual parts
   - Global settings for notification preferences
   - Per-user notification settings

2. **Automatic Notifications**
   - Triggered when stock levels change and fall below thresholds
   - Multiple notification channels (system, email)
   - Configurable notification frequency

3. **UI Warning Indicators**
   - Visual alerts in stock lists for low stock items
   - Dedicated stock threshold panel in part detail pages
   - Color-coded indicators for different stock levels

4. **Bulk Import/Export**
   - Import stock thresholds from CSV files
   - Export stock thresholds to CSV files
   - Compatible with different InvenTree versions

### Version Compatibility

| InvenTree Version | Supported | Export Format |
|-------------------|-----------|---------------|
| v0.12.x           | ✅         | `id, part_number, stock_threshold` |
| Stable Branch     | ✅         | `id, name, part_number, description, stock_threshold` |

## Installation

### Method 1: Install via Package Manager

```bash
pip install inventree-stock-threshold
```

### Method 2: Install from Source

1. Clone the repository to your InvenTree plugins directory:

```bash
cd /path/to/inventree/src/backend/InvenTree/plugins
git clone https://github.com/inventree/inventree-stock-threshold.git stock_threshold
```

2. Run migrations to create the required database tables:

```bash
python manage.py migrate stock_threshold
```

3. Restart your InvenTree server

4. Enable the plugin in the InvenTree plugin settings

## Configuration

### Plugin Settings

Navigate to **Settings > Plugins > Stock Threshold** to configure the plugin:

- **Enable Notifications**: Toggle stock threshold notifications on/off
- **Notification Email**: Email address to receive low stock notifications
- **Check Interval**: How often to check stock levels (in hours)

### Per-Part Thresholds

Set stock thresholds for individual parts:

1. Navigate to a part detail page
2. Scroll to the **Stock Threshold** panel
3. Enter the minimum stock level before notification
4. Click **Save**

## Usage

### Checking Stock Levels

The plugin automatically checks stock levels when:

- A stock item is added or removed
- A stock item is updated
- The plugin's scheduled task runs (based on check interval)

### Receiving Notifications

When stock levels fall below thresholds, notifications are sent via:

- System notifications (visible in the InvenTree UI)
- Email notifications (if configured)

### Importing/Exporting Thresholds

#### Exporting Thresholds

1. Navigate to **Stock > Export > Stock Thresholds**
2. Select the export format (v0.12.x or Stable)
3. Click **Export** to download the CSV file

#### Importing Thresholds

1. Prepare a CSV file with the appropriate format:
   - For v0.12.x: `id, part_number, stock_threshold`
   - For Stable: `id, name, part_number, description, stock_threshold`

2. Navigate to **Stock > Import > Stock Thresholds**
3. Upload the CSV file
4. Click **Import** to process the file

## API Endpoints

The plugin provides the following API endpoints:

### Get/Update Stock Threshold

```
GET /api/plugin/stockthreshold/threshold/{part_id}/
POST /api/plugin/stockthreshold/threshold/{part_id}/
```

### Import Thresholds

```
POST /api/plugin/stockthreshold/import/
```

### Export Thresholds

```
GET /api/plugin/stockthreshold/export/?version={version}
```

## Development

### Running Tests

```bash
python manage.py test plugins.stock_threshold
```

### Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues, please:

1. Check the [InvenTree documentation](https://inventree.readthedocs.io/)
2. Search the [InvenTree forums](https://forum.inventree.org/)
3. Create a [GitHub issue](https://github.com/inventree/inventree-stock-threshold/issues)
