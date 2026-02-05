"""Integration module for extending StockItem functionality.

This module provides functions to integrate threshold data into StockItem
serializers and API responses.
"""

from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist


def get_stock_item_threshold_data(stock_item):
    """Get threshold data for a stock item.
    
    This function can be used to extend StockItem serializers
    to include threshold information.
    
    Args:
        stock_item: A StockItem instance
        
    Returns:
        dict: Threshold data or None if no threshold configured
    """
    try:
        threshold = stock_item.threshold_config
        return {
            'threshold': threshold.threshold,
            'enabled': threshold.enabled,
            'is_low_stock': threshold.is_low_stock,
            'quantity_below_threshold': threshold.quantity_below_threshold,
        }
    except ObjectDoesNotExist:
        return None


def annotate_stock_queryset(queryset):
    """Annotate a StockItem queryset with threshold information.
    
    This function adds threshold-related annotations to a queryset
    for efficient bulk queries.
    
    Args:
        queryset: A StockItem queryset
        
    Returns:
        QuerySet: The annotated queryset
    """
    from django.db.models import OuterRef, Subquery, F, Case, When, Value
    
    from .models import StockItemThreshold
    
    # Subquery to get threshold for each stock item
    threshold_subquery = StockItemThreshold.objects.filter(
        stock_item=OuterRef('pk')
    ).values('threshold')[:1]
    
    enabled_subquery = StockItemThreshold.objects.filter(
        stock_item=OuterRef('pk')
    ).values('enabled')[:1]
    
    return queryset.annotate(
        threshold_value=Subquery(threshold_subquery),
        threshold_enabled=Subquery(enabled_subquery),
    )


def is_low_stock(stock_item):
    """Check if a stock item is below its threshold.
    
    This is a helper function that can be used in templates or views.
    
    Args:
        stock_item: A StockItem instance
        
    Returns:
        bool: True if stock is below threshold
    """
    try:
        return stock_item.threshold_config.is_low_stock
    except ObjectDoesNotExist:
        return False


def get_low_stock_color_class(stock_item):
    """Get the appropriate CSS class for low stock display.
    
    Args:
        stock_item: A StockItem instance
        
    Returns:
        str: CSS class name ('text-danger' for low stock, '' otherwise)
    """
    if is_low_stock(stock_item):
        return 'text-danger fw-bold'
    return ''


def get_low_stock_badge(stock_item):
    """Get HTML badge for low stock items.
    
    Args:
        stock_item: A StockItem instance
        
    Returns:
        str: HTML badge or empty string
    """
    try:
        threshold = stock_item.threshold_config
        if threshold.enabled and threshold.is_low_stock:
            return '<span class="badge bg-danger">Low Stock</span>'
    except ObjectDoesNotExist:
        pass
    return ''
