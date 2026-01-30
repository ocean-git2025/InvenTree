"""Stock Threshold Alert plugin for InvenTree."""

from django.utils.translation import gettext_lazy as _

import structlog

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UserInterfaceMixin, EventMixin
from stock.models import StockItem

logger = structlog.get_logger('inventree')


class StockThresholdPlugin(SettingsMixin, UserInterfaceMixin, EventMixin, InvenTreePlugin):
    """A plugin which provides stock threshold alerts for StockItems."""

    NAME = 'StockThresholdAlert'
    SLUG = 'stock-threshold-alert'
    TITLE = _('Stock Threshold Alert')
    DESCRIPTION = _('Displays alert indicators for stock items below configured threshold levels')
    VERSION = '1.0.0'
    AUTHOR = 'InvenTree'
    LICENSE = 'MIT'

    SETTINGS = {
        'DEFAULT_THRESHOLD': {
            'name': _('Default Threshold'),
            'description': _('Default minimum stock threshold (used when no item-specific threshold is set)'),
            'default': 10,
            'validator': int,
        },
        'ENABLED': {
            'name': _('Enable Plugin'),
            'description': _('Enable stock threshold alerts'),
            'default': True,
            'validator': bool,
        },
    }

    USER_SETTINGS = {
        'SHOW_ALERTS': {
            'name': _('Show Alerts'),
            'description': _('Show stock threshold alerts in stock list'),
            'default': True,
            'validator': bool,
        },
    }

    def wants_process_event(self, event, *args, **kwargs):
        """Determine if we want to process the given event."""
        if not self.get_setting('ENABLED'):
            return False
        
        relevant_events = [
            'stock.created',
            'stock.updated',
            'stock.counted',
        ]
        
        return event in relevant_events

    def process_event(self, event, *args, **kwargs):
        """Process triggered events."""
        logger.debug(f'StockThresholdPlugin: Processing event: {event}')

    def is_below_threshold(self, stock_item: StockItem) -> bool:
        """Check if a stock item is below its configured threshold.
        
        Arguments:
            stock_item: The StockItem object to check
            
        Returns:
            bool: True if stock item quantity is below threshold, False otherwise
        """
        if not self.get_setting('ENABLED'):
            return False
        
        metadata = stock_item.get_metadata('threshold')
        if metadata is not None:
            try:
                threshold = int(metadata)
                return stock_item.quantity < threshold
            except (ValueError, TypeError):
                pass
        
        default_threshold = self.get_setting('DEFAULT_THRESHOLD')
        return stock_item.quantity < default_threshold

    def get_threshold_value(self, stock_item: StockItem) -> int:
        """Get the threshold value for a stock item.
        
        Arguments:
            stock_item: The StockItem object
            
        Returns:
            int: The threshold value for the stock item
        """
        metadata = stock_item.get_metadata('threshold')
        if metadata is not None:
            try:
                return int(metadata)
            except (ValueError, TypeError):
                pass
        
        return int(self.get_setting('DEFAULT_THRESHOLD'))

    def get_ui_dashboard_items(self, request, context, **kwargs):
        """Return dashboard items showing stock items below threshold."""
        if not self.get_setting('ENABLED'):
            return []
        
        show_alerts = self.get_user_setting('SHOW_ALERTS')
        if not show_alerts:
            return []
        
        stock_items_below_threshold = []
        for item in StockItem.objects.filter(**StockItem.IN_STOCK_FILTER):
            if self.is_below_threshold(item):
                stock_items_below_threshold.append(item)
        
        if not stock_items_below_threshold:
            return []
        
        return [{
            'key': 'stock-threshold-alert',
            'title': _('Low Stock Alert'),
            'description': _('Stock items below minimum threshold levels'),
            'source': self.plugin_static_file('stock_threshold_dashboard.js'),
            'icon': 'ti:alert-triangle:outline',
            'context': {
                'alert_count': len(stock_items_below_threshold),
                'items': [
                    {
                        'pk': item.pk,
                        'part_name': item.part.full_name,
                        'quantity': float(item.quantity),
                        'threshold': self.get_threshold_value(item),
                    }
                    for item in stock_items_below_threshold[:10]
                ]
            },
            'options': {'width': 4, 'height': 2},
        }]

    def get_ui_panels(self, request, context, **kwargs):
        """Return custom panels for stock item views."""
        if not self.get_setting('ENABLED'):
            return []
        
        context = context or {}
        target_model = context.get('target_model', None)
        target_id = context.get('target_id', None)
        
        panels = []
        
        if target_model == 'stockitem' and target_id:
            try:
                stock_item = StockItem.objects.get(pk=target_id)
                is_below = self.is_below_threshold(stock_item)
                threshold = self.get_threshold_value(stock_item)
                
                panels.append({
                    'key': 'stock-threshold-panel',
                    'title': _('Stock Threshold'),
                    'source': self.plugin_static_file('stock_threshold_panel.js'),
                    'icon': 'ti:gauge:outline',
                    'context': {
                        'quantity': float(stock_item.quantity),
                        'threshold': threshold,
                        'is_below_threshold': is_below,
                        'stock_item_id': stock_item.pk,
                    }
                })
            except (StockItem.DoesNotExist, ValueError):
                pass
        
        return panels

    def get_admin_context(self) -> dict:
        """Return admin context data."""
        return {
            'plugin_name': self.NAME,
            'version': self.VERSION,
        }
