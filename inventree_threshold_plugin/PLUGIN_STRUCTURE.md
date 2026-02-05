# InvenTree Stock Threshold Plugin - Structure

## Directory Structure

```
inventree_threshold_plugin/
├── inventree_threshold_plugin/     # Main plugin package
│   ├── __init__.py                 # Package initialization
│   ├── version.py                  # Version information
│   ├── plugin.py                   # Main plugin class (StockThresholdPlugin)
│   ├── models.py                   # Database models (StockItemThreshold)
│   ├── admin.py                    # Django admin configuration
│   ├── serializers.py              # DRF serializers
│   ├── api.py                      # API endpoints
│   ├── urls.py                     # URL routing
│   ├── signals.py                  # Django signal handlers
│   ├── apps.py                     # Django app configuration
│   ├── integration.py              # Integration helpers
│   ├── migrations/                 # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── static/                     # Static files (JS, CSS)
│       └── plugins/
│           └── stockthreshold/
│               ├── threshold_column.js    # Column renderer
│               └── admin_settings.js      # Admin settings UI
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── settings.py                 # Test settings
│   ├── urls.py                     # Test URL config
│   ├── test_models.py              # Model tests
│   └── test_api.py                 # API tests
│
├── .github/
│   └── workflows/                  # GitHub Actions
│       ├── test.yml                # Unit tests
│       └── docker-test.yml         # Docker integration tests
│
├── setup.py                        # Package setup (setuptools)
├── pyproject.toml                  # Modern Python packaging
├── MANIFEST.in                     # Package manifest
├── pytest.ini                     # pytest configuration
├── LICENSE                         # MIT License
├── README.md                       # Main documentation
├── USAGE.md                        # Usage guide
├── PLUGIN_STRUCTURE.md            # This file
└── install.sh                      # Installation script
```

## Key Components

### 1. Plugin Class ([`plugin.py`](inventree_threshold_plugin/plugin.py))

The main plugin class that registers with InvenTree:

```python
class StockThresholdPlugin(SettingsMixin, UrlsMixin, AppMixin, InvenTreePlugin)
```

**Mixins used:**
- `SettingsMixin`: Plugin configuration settings
- `UrlsMixin`: Custom API endpoints
- `AppMixin`: Django app functionality
- `InvenTreePlugin`: Base plugin class

### 2. Model ([`models.py`](inventree_threshold_plugin/models.py))

**StockItemThreshold**: One-to-one relationship with StockItem

```python
class StockItemThreshold(models.Model):
    stock_item = OneToOneField(StockItem)
    threshold = DecimalField()      # Minimum stock level
    enabled = BooleanField()        # Enable/disable checking
```

### 3. API ([`api.py`](inventree_threshold_plugin/api.py))

REST API endpoints:
- `GET/POST /api/plugin/stock-threshold/threshold/`
- `GET/PUT/DELETE /api/plugin/stock-threshold/threshold/<pk>/`
- `GET /api/plugin/stock-threshold/stock-item/<pk>/threshold-status/`
- `GET /api/plugin/stock-threshold/low-stock/`

### 4. Frontend Integration

JavaScript files for UI customization:
- `threshold_column.js`: Custom column rendering for stock tables
- `admin_settings.js`: Admin panel settings UI

## InvenTree Integration Points

### 1. Plugin Registration

The plugin registers itself via entry points in `pyproject.toml`:
```toml
[project.entry-points."inventree_plugins"]
StockThresholdPlugin = "inventree_threshold_plugin.plugin:StockThresholdPlugin"
```

### 2. Model Extension Pattern

Uses OneToOne relationship to extend StockItem:
```python
# Access threshold from stock item
stock_item.threshold_config  # Returns StockItemThreshold or raises DoesNotExist
```

### 3. API Extension

Adds new endpoints under `/api/plugin/stock-threshold/`

### 4. Admin Integration

Registers with Django admin for easy configuration

## Testing Strategy

### Unit Tests
- Model tests: `test_models.py`
- API tests: `test_api.py`

### Integration Tests
- Docker-based testing against latest InvenTree
- GitHub Actions for CI/CD

### Test Configuration
- Uses SQLite in-memory database
- Minimal Django settings for fast tests
- Mock data for StockItem, Part, Location

## Compatibility

### InvenTree Versions
- Tested against stable branch
- Compatible with 0.12.x - 0.15.x

### Python Versions
- 3.9, 3.10, 3.11, 3.12

### Django Versions
- 4.2+ (matching InvenTree requirements)

## Development Workflow

1. **Local Development**
   ```bash
   pip install -e .
   pytest tests/
   ```

2. **Docker Testing**
   ```bash
   docker build -t inventree-with-plugin .
   docker run inventree-with-plugin
   ```

3. **CI/CD**
   - GitHub Actions runs tests on push/PR
   - Daily tests against latest InvenTree Docker image

## Extension Points

### Adding Custom Fields to StockItem API

Use the integration module:
```python
from inventree_threshold_plugin.integration import get_stock_item_threshold_data

# In your serializer
def get_threshold_data(self, obj):
    return get_stock_item_threshold_data(obj)
```

### Custom Threshold Logic

Extend the model:
```python
class CustomThreshold(StockItemThreshold):
    def custom_check(self):
        # Your custom logic
        pass
```

### Frontend Customization

Modify JavaScript files:
- `threshold_column.js`: Change rendering logic
- `admin_settings.js`: Add custom settings UI

## Security Considerations

1. **API Permissions**: All endpoints require authentication
2. **Admin Access**: Threshold configuration restricted to staff users
3. **Data Validation**: Decimal validators prevent invalid threshold values

## Performance

1. **Database**: OneToOne relationship with indexed foreign key
2. **API**: Uses `select_related` for efficient queries
3. **Frontend**: Lazy loading of threshold data

## Future Enhancements

Potential improvements:
- [ ] Part-level default thresholds
- [ ] Email notifications for low stock
- [ ] Bulk threshold configuration
- [ ] Threshold history/audit log
- [ ] Integration with purchase orders
