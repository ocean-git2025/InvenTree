# Stock Threshold Plugin for InvenTree

## Overview

The Stock Threshold plugin for InvenTree provides a comprehensive solution for managing inventory thresholds and receiving notifications when stock levels fall below specified thresholds.

## Features

- **Background Configuration**: Set stock thresholds for individual parts through the plugin settings
- **Inventory Change Triggers**: Automatically check stock levels when inventory changes occur
- **UI Alerts**: Visual indicators in inventory lists and part detail pages for low stock levels
- **Batch Import/Export**: CSV import/export functionality for managing thresholds in bulk

## Compatibility

- **InvenTree v0.12.x**: Export format: `id, part_number, stock_threshold`
- **InvenTree stable branch**: Export format: `id, name, part_number, description, stock_threshold`

## Installation

### Method 1: Install via pip

```bash
pip install inventree-stock-threshold
```

### Method 2: Install from source

1. Clone the repository:

```bash
git clone https://github.com/inventree/inventree-stock-threshold.git
```

2. Install the plugin:

```bash
cd inventree-stock-threshold
pip install -e .
```

### Method 3: Manual installation

1. Copy the `stock_threshold` directory to your InvenTree plugins directory:

```bash
cp -r stock_threshold /path/to/inventree/InvenTree/plugins/
```

2. Install the plugin dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. **Enable the Plugin**: In the InvenTree admin interface, navigate to `Plugins` → `Plugin List` and enable the "Stock Threshold Management" plugin.

2. **Configure Plugin Settings**: Navigate to `Plugins` → `Plugin Settings` → `StockThreshold` to configure the plugin settings:

   - **Enable Notifications**: Toggle to enable/disable threshold notifications
   - **Notification Email**: Email address to receive threshold notifications
   - **Check Interval**: Interval (in minutes) to check stock thresholds

3. **Set Part Thresholds**: 
   - Navigate to a part detail page
   - Scroll down to the "Stock Threshold" panel
   - Enter the desired threshold value
   - Click "Save Threshold"

## Usage

### Setting Thresholds

1. **Individual Parts**: Use the "Stock Threshold" panel on each part detail page to set and manage thresholds.

2. **Batch Import**: Use the CSV import functionality to import thresholds in bulk:
   - Navigate to `Parts` → `Import/Export` → `Import Parts`
   - Select the "Stock Threshold" import format
   - Upload your CSV file

3. **Batch Export**: Use the CSV export functionality to export thresholds in bulk:
   - Navigate to `Parts` → `Import/Export` → `Export Parts`
   - Select the "Stock Threshold" export format
   - Download the CSV file

### Receiving Notifications

When stock levels fall below the configured thresholds:

1. **UI Alerts**: Visual indicators will appear in inventory lists and part detail pages
2. **Email Notifications**: If configured, email notifications will be sent to the specified email address

## API Endpoints

The plugin extends the InvenTree API with the following endpoints:

- **GET /api/plugin/stockthreshold/parts/**: List all parts with their current stock levels and thresholds
- **PUT /api/plugin/stockthreshold/parts/{id}/**: Update the threshold for a specific part

## Development

### Directory Structure

```
stock_threshold/
├── __init__.py              # Plugin initialization
├── plugin.py                # Core plugin implementation
├── models.py                # StockThreshold model definition
├── serializers.py           # API serializers
├── views.py                 # API views
├── urls.py                  # URL configuration
├── setup.py                 # Python package setup
├── README.md                # Plugin documentation
├── static/
│   └── panels/              # Frontend panels
│       └── stock_threshold_panel.js  # Part detail page threshold panel
└── migrations/              # Database migration files
```

### Database Model

The plugin uses a custom `StockThreshold` model that has a one-to-one relationship with the `Part` model. This allows for storing threshold values separately from the core Part model, ensuring no conflicts with existing inventory calculation and permission control.

### Running Tests

```bash
# Run unit tests
pytest

# Run Docker tests
docker-compose -f docker-compose.test.yml up --build
```

### GitHub Actions

The plugin includes GitHub Actions workflows for automated testing:

- **Python Tests**: Run tests for multiple Python versions
- **Docker Tests (stable)**: Test with InvenTree stable branch
- **Docker Tests (v0.12.x)**: Test with InvenTree v0.12.x branch

## Contributing

Contributions are welcome! Please submit a pull request or open an issue on the GitHub repository.

## License

This plugin is released under the MIT License. See the LICENSE file for more information.
