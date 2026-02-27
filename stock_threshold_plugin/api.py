from rest_framework.response import Response
from rest_framework.views import APIView

from common.settings import get_global_setting
from plugin import registry


class ThresholdCheckAPI(APIView):
    """API endpoint for checking stock items below threshold.

    Returns a list of stock item IDs that are below their configured threshold.
    """

    def get(self, request, *args, **kwargs):
        """Return list of stock item IDs below threshold."""
        if not get_global_setting('ENABLE_PLUGINS_INTERFACE'):
            return Response({'low_stock_ids': [], 'error': 'Plugins not enabled'})

        from stock.models import StockItem

        from plugin import PluginMixinEnum
        plugin = None
        for p in registry.with_mixin(PluginMixinEnum.API, active=True):
            if hasattr(p, 'get_stock_threshold'):
                plugin = p
                break

        if not plugin:
            return Response({'low_stock_ids': [], 'error': 'Plugin not found'})

        low_stock_ids = []
        queryset = StockItem.objects.filter(active=True)

        for stock_item in queryset:
            try:
                threshold = plugin.get_stock_threshold(stock_item)
                if stock_item.quantity < threshold:
                    low_stock_ids.append(stock_item.pk)
            except Exception:
                pass

        return Response({
            'low_stock_ids': low_stock_ids,
            'count': len(low_stock_ids),
        })
