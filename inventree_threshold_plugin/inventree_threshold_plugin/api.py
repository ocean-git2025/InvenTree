"""API endpoints for stock threshold plugin."""

from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import stock.models
from .models import StockItemThreshold
from .serializers import StockItemThresholdSerializer


class StockItemThresholdList(generics.ListCreateAPIView):
    """API endpoint to list and create stock item thresholds."""
    
    queryset = StockItemThreshold.objects.all()
    serializer_class = StockItemThresholdSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter by stock_item if provided."""
        queryset = super().get_queryset()
        stock_item_id = self.request.query_params.get('stock_item', None)
        if stock_item_id:
            queryset = queryset.filter(stock_item_id=stock_item_id)
        return queryset


class StockItemThresholdDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update or delete a stock item threshold."""
    
    queryset = StockItemThreshold.objects.all()
    serializer_class = StockItemThresholdSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_stock_item_threshold_status(request, pk):
    """Get threshold status for a specific stock item.
    
    Args:
        request: HTTP request
        pk: StockItem ID
        
    Returns:
        JSON response with threshold status
    """
    stock_item = get_object_or_404(stock.models.StockItem, pk=pk)
    
    try:
        threshold = stock_item.threshold_config
        return Response({
            'has_threshold': True,
            'threshold': threshold.threshold,
            'enabled': threshold.enabled,
            'is_low_stock': threshold.is_low_stock,
            'quantity_below_threshold': threshold.quantity_below_threshold
        })
    except StockItemThreshold.DoesNotExist:
        return Response({
            'has_threshold': False,
            'threshold': None,
            'enabled': False,
            'is_low_stock': False,
            'quantity_below_threshold': 0
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_low_stock_items(request):
    """Get all stock items that are below their threshold.
    
    Returns:
        JSON response with list of low stock items
    """
    low_stock_thresholds = StockItemThreshold.objects.filter(
        enabled=True,
        stock_item__quantity__lt=models.F('threshold')
    ).select_related('stock_item', 'stock_item__part')
    
    serializer = StockItemThresholdSerializer(low_stock_thresholds, many=True)
    return Response(serializer.data)
