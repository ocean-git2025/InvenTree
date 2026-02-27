"""
Stock Threshold Plugin for InvenTree.

This plugin provides custom stock threshold functionality for StockItems,
allowing users to set minimum stock levels and receive visual warnings
when stock falls below the threshold.

The plugin uses the existing MetadataMixin on StockItem to store threshold values,
and UserInterfaceMixin to provide UI integration.
"""

from decimal import Decimal

from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UserInterfaceMixin


class StockThresholdPlugin(SettingsMixin, UserInterfaceMixin, InvenTreePlugin):
    """
    A plugin that provides custom stock threshold functionality for StockItems.

    Features:
    - Configure custom minimum stock thresholds for individual StockItems
    - Visual warning (red highlighting) in stock list when quantity is below threshold
    - Compatible with InvenTree stable branch

    The threshold values are stored in each StockItem's metadata field using the
    MetadataMixin that StockItem already inherits from.

    Usage via API:
        PATCH /api/stock/{id}/
        {
            "metadata": {
                "stock-threshold": {
                    "threshold": 10
                }
            }
        }
    """

    NAME = 'StockThresholdPlugin'
    SLUG = 'stock-threshold'
    TITLE = _('Stock Threshold Warning')
    DESCRIPTION = _(
        'Provides custom stock threshold functionality with visual warnings '
        'when stock levels fall below defined thresholds'
    )
    VERSION = '1.0.0'
    AUTHOR = 'InvenTree Community'
    LICENSE = 'MIT'

    SETTINGS = {
        'ENABLE_THRESHOLD_WARNING': {
            'name': _('Enable Threshold Warning'),
            'description': _('Enable visual warning for low stock items'),
            'default': True,
            'validator': bool,
        },
        'DEFAULT_THRESHOLD': {
            'name': _('Default Threshold'),
            'description': _(
                'Default minimum stock threshold for items without custom threshold'
            ),
            'default': 0,
            'validator': int,
        },
        'WARNING_COLOR': {
            'name': _('Warning Color'),
            'description': _('CSS color for low stock warning (e.g., #ff4444, red)'),
            'default': '#ff4444',
        },
        'ENABLE_PANEL': {
            'name': _('Enable Stock Panel'),
            'description': _(
                'Show threshold information panel on stock item detail page'
            ),
            'default': True,
            'validator': bool,
        },
    }

    def get_ui_panels(self, request, context, **kwargs):
        """
        Return custom panels to be injected into the UI.

        Adds a threshold panel to stock item detail pages showing current
        stock level vs threshold.
        """
        panels = []

        if not self.get_setting('ENABLE_PANEL'):
            return panels

        target_model = context.get('target_model', None)
        target_id = context.get('target_id', None)

        if target_model == 'stockitem' and target_id is not None:
            try:
                from stock.models import StockItem

                stock_item = StockItem.objects.get(pk=target_id)

                threshold = self.get_stock_item_threshold(stock_item)
                quantity = float(stock_item.quantity)
                is_below_threshold = stock_item.quantity < Decimal(str(threshold))

                panels.append({
                    'key': 'threshold-panel',
                    'title': _('Stock Threshold'),
                    'source': self.plugin_static_file('threshold_panel.js'),
                    'icon': 'ti:alert-triangle:outline',
                    'context': {
                        'threshold': threshold,
                        'quantity': quantity,
                        'is_below_threshold': is_below_threshold,
                        'warning_enabled': self.get_setting('ENABLE_THRESHOLD_WARNING'),
                        'warning_color': self.get_setting('WARNING_COLOR'),
                    },
                })
            except Exception:
                pass

        return panels

    def get_ui_spotlight_actions(self, request, context, **kwargs):
        """
        Return custom spotlight actions.

        Adds a quick action to view low stock items.
        """
        return [
            {
                'key': 'view-low-stock',
                'title': _('View Low Stock Items'),
                'description': _('Show all stock items below their threshold'),
                'icon': 'ti:alert-triangle:outline',
                'source': self.plugin_static_file(
                    'threshold_action.js:viewLowStockItems'
                ),
            }
        ]

    def get_stock_item_threshold(self, stock_item):
        """
        Get the threshold value for a StockItem.

        First checks if a custom threshold is set in the item's metadata
        (stored under the plugin's slug as key), otherwise falls back to
        the default threshold setting.

        Args:
            stock_item: StockItem instance (must have MetadataMixin)

        Returns:
            int: The threshold value for this stock item
        """
        metadata = stock_item.get_metadata(self.SLUG, {})
        if metadata and 'threshold' in metadata:
            return int(metadata['threshold'])

        return self.get_setting('DEFAULT_THRESHOLD')

    def set_stock_item_threshold(self, stock_item, threshold, user=None):
        """
        Set a custom threshold for a StockItem.

        Stores the threshold value in the item's metadata field under
        the plugin's slug as key.

        Args:
            stock_item: StockItem instance (must have MetadataMixin)
            threshold: Threshold value to set (int)
            user: Optional user performing the action (not used, for future)
        """
        metadata = stock_item.get_metadata(self.SLUG, {})
        metadata['threshold'] = int(threshold)
        stock_item.set_metadata(self.SLUG, metadata, commit=True)

    def is_below_threshold(self, stock_item):
        """
        Check if a StockItem is below its threshold.

        Args:
            stock_item: StockItem instance

        Returns:
            bool: True if quantity is below threshold
        """
        threshold = Decimal(str(self.get_stock_item_threshold(stock_item)))
        return stock_item.quantity < threshold

    def get_low_stock_items(self):
        """
        Get all StockItems that are below their threshold.

        Returns:
            list: List of StockItem pk values that are below threshold
        """
        from stock.models import StockItem

        low_stock_pks = []

        for item in StockItem.objects.filter(quantity__gt=0):
            if self.is_below_threshold(item):
                low_stock_pks.append(item.pk)

        return low_stock_pks
