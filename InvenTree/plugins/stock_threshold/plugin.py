"""Stock Threshold Plugin for InvenTree."""

from collections import OrderedDict
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import QuerySet

from rest_framework import serializers

from common.models import DataOutput
from part.models import Part
from stock.models import StockItem

from plugin import InvenTreePlugin
from plugin.base.event.mixins import EventMixin
from plugin.base.integration.SettingsMixin import SettingsMixin
from plugin.base.integration.DataExport import DataExportMixin
from plugin.base.ui.mixins import UserInterfaceMixin
from plugin.base.integration.UrlsMixin import UrlsMixin

from . import urls


class StockThresholdPlugin(
    InvenTreePlugin,
    SettingsMixin,
    UserInterfaceMixin,
    EventMixin,
    DataExportMixin,
    UrlsMixin,
):
    """Stock threshold management plugin for InvenTree."""

    NAME = "StockThreshold"
    SLUG = "stockthreshold"
    TITLE = "Stock Threshold Management"
    DESCRIPTION = "Manage stock thresholds and receive notifications when stock levels fall below threshold"
    VERSION = "1.0.0"
    AUTHOR = "InvenTree Community"

    # URL configuration
    URLS = urls.urlpatterns

    # Settings definition
    SETTINGS = {
        "NOTIFICATION_ENABLED": {
            "name": "Enable Notifications",
            "description": "Enable notifications when stock levels fall below threshold",
            "default": True,
            "type": "boolean",
        },
        "NOTIFICATION_EMAIL": {
            "name": "Notification Email",
            "description": "Email address to receive threshold notifications",
            "default": "",
            "type": "string",
        },
        "CHECK_INTERVAL": {
            "name": "Check Interval",
            "description": "Interval (in minutes) to check stock thresholds",
            "default": 60,
            "type": "integer",
        },
    }

    def __init__(self):
        """Initialize the plugin."""
        super().__init__()

    def wants_process_event(self, event: str) -> bool:
        """Check if the plugin wants to process the given event."""
        return event in [
            "stock.item.created",
            "stock.item.updated",
            "stock.item.deleted",
            "stock.location.stock_updated",
        ]

    def process_event(self, event: str, *args, **kwargs) -> None:
        """Process the given event."""
        if not self.get_setting("NOTIFICATION_ENABLED", backup_value=True):
            return

        self.check_stock_thresholds()

    def check_stock_thresholds(self) -> None:
        """Check stock levels against thresholds and send notifications."""
        # Get all parts with stock thresholds
        from .models import StockThreshold
        thresholds = StockThreshold.objects.filter(stock_threshold__gt=0)

        for threshold in thresholds:
            part = threshold.part
            # Calculate current stock level
            current_stock = part.available_stock

            # Check if stock is below threshold
            if current_stock < threshold.stock_threshold:
                # Here you would implement notification logic
                # For example, send an email or create a notification
                pass

    def get_ui_panels(self, request, context, **kwargs):
        """Return custom UI panels."""
        panels = []

        # Check if we're on a part detail page
        if context.get('page') == 'part-detail':
            panels.append({
                'key': 'stock_threshold',
                'title': 'Stock Threshold',
                'description': 'Manage stock threshold for this part',
                'icon': 'inventory',
                'feature_type': 'panel',
                'options': {},
                'context': {},
                'source': 'stock_threshold/panels/stock_threshold_panel.js',
            })

        return panels

    def supports_export(self, model_class, user, serializer_class=None, view_class=None, *args, **kwargs) -> bool:
        """Check if the plugin supports exporting data for the given model."""
        return model_class == Part

    def export_data(self, queryset, serializer_class, headers, context, output, serializer_context=None, **kwargs):
        """Export data from the queryset."""
        import inventree
        inven_tree_version = inventree.__version__
        use_v012_format = inven_tree_version.startswith("0.12.")

        exported_data = []

        for part in queryset:
            # Get threshold for this part
            from .models import StockThreshold
            try:
                threshold = StockThreshold.objects.get(part=part)
                stock_threshold = threshold.stock_threshold
            except StockThreshold.DoesNotExist:
                stock_threshold = 0

            if use_v012_format:
                # v0.12.x format: id, part_number, stock_threshold
                exported_data.append({
                    'id': part.id,
                    'part_number': part.part_number,
                    'stock_threshold': stock_threshold,
                })
            else:
                # stable branch format: id, name, part_number, description, stock_threshold
                exported_data.append({
                    'id': part.id,
                    'name': part.name,
                    'part_number': part.part_number,
                    'description': part.description or '',
                    'stock_threshold': stock_threshold,
                })

        return exported_data

    def generate_filename(self, model_class, export_format: str) -> str:
        """Generate a filename for the exported data."""
        from InvenTree.helpers import current_date
        date = current_date().isoformat()
        return f'stock_thresholds_{date}.{export_format}'
