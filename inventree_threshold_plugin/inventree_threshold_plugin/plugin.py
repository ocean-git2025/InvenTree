"""Main plugin class for InvenTree Stock Threshold Plugin."""

from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UrlsMixin, AppMixin

from .version import PLUGIN_VERSION


class StockThresholdPlugin(SettingsMixin, UrlsMixin, AppMixin, InvenTreePlugin):
    """Stock Threshold Plugin for InvenTree.
    
    This plugin provides:
    - Custom stock threshold configuration for StockItem models
    - Low stock warnings in the UI
    - API endpoints for threshold management
    """
    
    # Plugin metadata
    NAME = 'StockThresholdPlugin'
    SLUG = 'stockthreshold'
    TITLE = _('Stock Threshold Plugin')
    DESCRIPTION = _('Add custom stock thresholds and low stock warnings for StockItem models')
    VERSION = PLUGIN_VERSION
    AUTHOR = _('InvenTree Community')
    LICENSE = 'MIT'
    
    # Optional admin settings page
    ADMIN_SOURCE = 'admin_settings.js'
    
    # Plugin settings
    SETTINGS = {
        'ENABLE_THRESHOLD_WARNINGS': {
            'name': _('Enable Threshold Warnings'),
            'description': _('Enable low stock warnings in the user interface'),
            'default': True,
            'validator': bool,
        },
        'DEFAULT_THRESHOLD': {
            'name': _('Default Threshold'),
            'description': _('Default threshold value when creating new threshold configurations'),
            'default': 10,
            'validator': int,
        },
        'SHOW_LOW_STOCK_BADGE': {
            'name': _('Show Low Stock Badge'),
            'description': _('Show a visual badge for low stock items in tables'),
            'default': True,
            'validator': bool,
        },
    }
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
    
    def setup_urls(self):
        """Return URL patterns for this plugin."""
        from . import urls
        return [
            path('stock-threshold/', include(urls)),
        ]
    
    def ready(self):
        """Called when the plugin is ready."""
        # Import signal handlers
        from . import signals
