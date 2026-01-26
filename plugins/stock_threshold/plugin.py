"""Stock threshold notification plugin for InvenTree."""

from __future__ import annotations

import csv
import io
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from part.models import Part
from plugin import InvenTreePlugin
from plugin.base.event.mixins import EventMixin
from plugin.base.integration.DataExport import DataExportMixin
from plugin.base.integration.SettingsMixin import SettingsMixin
from plugin.base.integration.UrlsMixin import UrlsMixin
from plugin.base.ui.mixins import UserInterfaceMixin
from stock.models import StockItem
from stock.events import StockEvents

# Import InvenTree version
import InvenTree
inventree_version = InvenTree.__version__


class StockThreshold(models.Model):
    """Model to store stock threshold information for parts."""

    class Meta:
        """Metaclass for StockThreshold model."""
        verbose_name = _('Stock Threshold')
        verbose_name_plural = _('Stock Thresholds')
        unique_together = ('part',)

    part = models.OneToOneField(
        Part,
        on_delete=models.CASCADE,
        related_name='stock_threshold',
        verbose_name=_('Part')
    )

    stock_threshold = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Stock Threshold'),
        help_text=_('Minimum stock level before notification')
    )

    def __str__(self):
        """String representation of StockThreshold."""
        return f"{self.part.name} - Threshold: {self.stock_threshold}"


class StockThresholdPlugin(
    InvenTreePlugin,
    SettingsMixin,
    UserInterfaceMixin,
    EventMixin,
    DataExportMixin,
    UrlsMixin
):
    """Stock threshold notification plugin."""

    PLUGIN_NAME = "Stock Threshold"
    PLUGIN_SLUG = "stockthreshold"
    PLUGIN_VERSION = "1.0.0"
    PLUGIN_AUTHOR = "InvenTree Community"
    PLUGIN_DESCRIPTION = "Stock threshold notification system for InvenTree"
    PLUGIN_LICENSE = "MIT"
    PLUGIN_URL = "https://github.com/inventree/inventree"

    # Import URL patterns
    from . import urls
    URLS = urls.urlpatterns

    SETTINGS = {
        'ENABLE_NOTIFICATIONS': {
            'name': _('Enable Notifications'),
            'description': _('Enable stock threshold notifications'),
            'default': True,
            'validator': bool,
            'options': [True, False],
        },
        'NOTIFICATION_EMAIL': {
            'name': _('Notification Email'),
            'description': _('Email address to send notifications to'),
            'default': '',
        },
        'CHECK_INTERVAL': {
            'name': _('Check Interval'),
            'description': _('Interval (in hours) to check stock levels'),
            'default': 24,
            'validator': int,
            'min_value': 1,
            'max_value': 168,
        },
    }

    def __init__(self):
        """Initialize plugin."""
        super().__init__()

    def wants_process_event(self, event: str) -> bool:
        """Subscribe to stock-related events."""
        return event in [
            StockEvents.STOCK_ADDED,
            StockEvents.STOCK_REMOVED,
            StockEvents.STOCK_UPDATED,
        ]

    def process_event(self, event: str, *args, **kwargs) -> None:
        """Process stock events and check thresholds."""
        if not self.get_setting('ENABLE_NOTIFICATIONS', backup_value=True):
            return

        # Get stock item from kwargs
        stock_item = kwargs.get('stock_item')
        if not stock_item:
            return

        # Check threshold for the part
        self.check_stock_threshold(stock_item.part)

    def check_stock_threshold(self, part: Part) -> bool:
        """Check if part stock is below threshold."""
        try:
            threshold = part.stock_threshold
        except StockThreshold.DoesNotExist:
            return False

        # Calculate current stock level
        current_stock = part.total_stock

        if current_stock < threshold.stock_threshold:
            # Stock is below threshold - send notification
            self.send_notification(part, current_stock, threshold.stock_threshold)
            return True

        return False

    def send_notification(self, part: Part, current_stock: int, threshold: int) -> None:
        """Send notification for low stock."""
        # Implement notification logic here
        # This could be email, system notification, etc.
        print(f"NOTIFICATION: Part {part.name} (SKU: {part.part_number}) has low stock: {current_stock}/{threshold}")

    def get_ui_panels(self, request: Any, context: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Return custom UI panels for stock threshold."""
        panels = []

        # Add stock threshold panel to part detail page
        if context.get('model') == 'part':
            panels.append({
                'key': 'stock_threshold',
                'title': _('Stock Threshold'),
                'description': _('Minimum stock level before notification'),
                'icon': 'alert-triangle',
                'feature_type': 'panel',
                'options': {},
                'context': {},
                'source': 'stock_threshold/static/panels/stock_threshold_panel.js',
            })

        return panels

    def supports_export(self, model_class: type, user: User, **kwargs) -> bool:
        """Support exporting stock thresholds."""
        return model_class == Part

    def export_data(
        self,
        queryset: QuerySet,
        serializer_class: serializers.Serializer,
        headers: OrderedDict,
        context: Dict[str, Any],
        output: Any,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Export stock threshold data."""
        data = []

        for part in queryset:
            try:
                threshold = part.stock_threshold
                threshold_value = threshold.stock_threshold
            except StockThreshold.DoesNotExist:
                threshold_value = 0

            # Determine export format based on InvenTree version
            if inventree_version.startswith('0.12.'):
                # v0.12.x format: id, part_number, stock_threshold
                item = {
                    'id': part.id,
                    'part_number': part.part_number,
                    'stock_threshold': threshold_value,
                }
            else:
                # Stable branch format: id, name, part_number, description, stock_threshold
                item = {
                    'id': part.id,
                    'name': part.name,
                    'part_number': part.part_number,
                    'description': part.description or '',
                    'stock_threshold': threshold_value,
                }

            data.append(item)

        return data

    def import_stock_thresholds(self, csv_file: io.StringIO) -> Dict[str, Any]:
        """Import stock thresholds from CSV file."""
        reader = csv.DictReader(csv_file)
        imported = 0
        errors = []

        for row in reader:
            try:
                # Get part by ID or part_number
                part_id = row.get('id')
                part_number = row.get('part_number')

                if part_id:
                    part = Part.objects.get(id=part_id)
                elif part_number:
                    part = Part.objects.get(part_number=part_number)
                else:
                    errors.append(f"No part ID or part_number provided: {row}")
                    continue

                # Get threshold value
                threshold_value = int(row.get('stock_threshold', 0))

                # Create or update stock threshold
                threshold, created = StockThreshold.objects.update_or_create(
                    part=part,
                    defaults={'stock_threshold': threshold_value}
                )

                imported += 1

            except Part.DoesNotExist:
                errors.append(f"Part not found: {row}")
            except ValueError:
                errors.append(f"Invalid threshold value: {row}")
            except Exception as e:
                errors.append(f"Error processing row {row}: {str(e)}")

        return {
            'imported': imported,
            'errors': errors,
        }


@receiver(post_save, sender=StockItem)
def check_stock_threshold_on_save(sender: type, instance: StockItem, **kwargs) -> None:
    """Check stock threshold when stock item is saved."""
    # Import here to avoid circular imports
    from plugin.registry import registry

    # Get stock threshold plugin
    plugin = registry.get_plugin('stockthreshold')
    if plugin and plugin.mixin_enabled('Settings'):
        plugin.check_stock_threshold(instance.part)
