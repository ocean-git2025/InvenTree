"""Admin configuration for stock threshold plugin."""

from django.contrib import admin

from .models import StockItemThreshold


@admin.register(StockItemThreshold)
class StockItemThresholdAdmin(admin.ModelAdmin):
    """Admin interface for StockItemThreshold model."""
    
    list_display = [
        'stock_item',
        'threshold',
        'enabled',
        'is_low_stock_indicator',
        'updated'
    ]
    list_filter = ['enabled', 'created', 'updated']
    search_fields = ['stock_item__part__name', 'stock_item__part__IPN']
    autocomplete_fields = ['stock_item']
    
    def is_low_stock_indicator(self, obj):
        """Display low stock status with color indicator."""
        if obj.is_low_stock:
            return "⚠️ Low Stock"
        return "✅ OK"
    is_low_stock_indicator.short_description = "Stock Status"
