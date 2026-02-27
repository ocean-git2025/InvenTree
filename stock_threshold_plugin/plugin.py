from django.utils.translation import gettext_lazy as _

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UserInterfaceMixin, APIMixin


class StockThresholdPlugin(SettingsMixin, UserInterfaceMixin, APIMixin, InvenTreePlugin):

    NAME = 'StockThresholdPlugin'
    SLUG = 'stock-threshold'
    TITLE = _('Stock Threshold Alert')
    DESCRIPTION = _('Highlights stock items with quantity below configured threshold in stock list.')
    VERSION = '1.0.0'
    AUTHOR = 'InvenTree Contributors'
    LICENSE = 'MIT'

    SETTINGS = {
        'DEFAULT_THRESHOLD': {
            'name': _('Default Threshold'),
            'description': _('Default stock threshold for items without custom threshold'),
            'default': 10,
            'validator': int,
        },
        'ALERT_COLOR': {
            'name': _('Alert Color'),
            'description': _('Background color for low stock alerts (CSS color)'),
            'default': '#fef2f2',
        },
        'ALERT_BORDER_COLOR': {
            'name': _('Alert Border Color'),
            'description': _('Border color for low stock alerts (CSS color)'),
            'default': '#ef4444',
        },
    }

    def get_api_urls(self):
        from django.urls import path
        from . import api
        return [
            path('threshold-check/', api.ThresholdCheckAPI.as_view(), name='threshold-check'),
        ]

    def get_stock_threshold(self, stock_item):
        custom_threshold = stock_item.get_metadata('stock_threshold')
        if custom_threshold is not None:
            try:
                return int(custom_threshold)
            except (ValueError, TypeError):
                pass
        return self.get_setting('DEFAULT_THRESHOLD', 10)

    def is_below_threshold(self, stock_item):
        threshold = self.get_stock_threshold(stock_item)
        return stock_item.quantity < threshold

    def get_ui_panels(self, request, context, **kwargs):
        panels = []
        context = context or {}
        target_model = context.get('target_model', '')
        target_id = context.get('target_id')

        if target_model == 'stockitem' and target_id:
            try:
                from stock.models import StockItem
                stock_item = StockItem.objects.get(pk=target_id)
                threshold = self.get_stock_threshold(stock_item)
                is_low = stock_item.quantity < threshold

                panels.append({
                    'key': 'stock-threshold-panel',
                    'title': _('Stock Threshold'),
                    'source': self.plugin_static_file('threshold_panel.js:renderPanel'),
                    'icon': 'ti:alert-triangle:outline' if is_low else 'ti:settings',
                    'context': {
                        'stock_id': stock_item.id,
                        'quantity': float(stock_item.quantity),
                        'threshold': threshold,
                        'is_low': is_low,
                        'alert_color': self.get_setting('ALERT_COLOR'),
                    },
                })
            except StockItem.DoesNotExist:
                pass

        panels.append({
            'key': 'stock-list-threshold-highlighter',
            'title': _('Threshold Highlighter'),
            'hidden': True,
            'source': self.plugin_static_file('threshold_highlighter.js:init'),
            'context': {
                'api_url': '/plugin/stock-threshold/threshold-check/',
                'alert_color': self.get_setting('ALERT_COLOR'),
                'border_color': self.get_setting('ALERT_BORDER_COLOR'),
            },
        })

        return panels

    def get_ui_dashboard_items(self, request, context, **kwargs):
        from stock.models import StockItem
        default_threshold = self.get_setting('DEFAULT_THRESHOLD', 10)
        low_stock_ids = []
        for stock_item in StockItem.objects.filter(active=True):
            threshold = self.get_stock_threshold(stock_item)
            if stock_item.quantity < threshold:
                low_stock_ids.append(stock_item.pk)

        items = [{
            'key': 'low-stock-dashboard',
            'title': _('Low Stock Alert'),
            'description': _('Stock items below configured threshold'),
            'source': self.plugin_static_file('low_stock_dashboard.js'),
            'context': {
                'low_stock_count': len(low_stock_ids),
                'api_url': '/plugin/stock-threshold/threshold-check/',
            },
            'options': {'width': 4, 'height': 2},
        }]

        return items
