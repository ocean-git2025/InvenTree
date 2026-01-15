"""Stock Threshold Alert Plugin for InvenTree."""

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import F, Case, When, Value, BooleanField

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, UserInterfaceMixin, AppMixin
from stock.models import StockItem





class StockThresholdPlugin(AppMixin, SettingsMixin, UserInterfaceMixin, InvenTreePlugin):
    """Plugin to provide stock threshold alerts for StockItem objects."""

    NAME = 'StockThresholdPlugin'
    SLUG = 'stockthreshold'
    TITLE = 'Stock Threshold Alert Plugin'
    DESCRIPTION = 'A plugin to set custom stock thresholds and display alerts'
    VERSION = '1.0.0'

    AUTHOR = 'InvenTree'
    PUBLISH_DATE = '2025-01-01'

    def __init__(self):
        super().__init__()
        self._thresholds = {}

    def get_ui_features(self, request, context, **kwargs):
        """Return UI features for this plugin."""

        return {
            'stock_list': {
                'threshold_check': True,
            },
        }

    def get_ui_context(self, request, context, **kwargs):
        """Provide additional context for UI rendering."""

        target_model = context.get('target_model', None)

        if target_model == 'stockitem' and context.get('target_id'):
            try:
                stock_item = StockItem.objects.get(pk=context['target_id'])
                threshold = stock_item.get_custom_data().get('threshold', 0)
                return {
                    'stock_threshold': threshold,
                    'below_threshold': stock_item.quantity < threshold,
                }
            except (StockItem.DoesNotExist, ValueError):
                pass

        return {}

    def annotate_stock_items(self, queryset):
        """Annotate StockItem queryset with threshold information."""
        from django.db.models import F, Case, When, Value, BooleanField, IntegerField
        from django.db.models.functions import Cast

        queryset = queryset.annotate(
            threshold=Cast(
                Case(
                    When(
                        custom_data__has_key='threshold',
                        then=F('custom_data__threshold'),
                    ),
                    default=Value(0),
                ),
                output_field=models.DecimalField(max_digits=19, decimal_places=9),
            ),
            below_threshold=Case(
                When(
                    quantity__lt=F('threshold'),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )

        return queryset

    def ready(self):
        """Plugin is ready."""
        super().ready()
        self.annotate_stock_items(StockItem.objects.all())
