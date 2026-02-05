"""URL configuration for stock threshold plugin."""

from django.urls import path

from . import api

urlpatterns = [
    path('threshold/', api.StockItemThresholdList.as_view(), name='threshold-list'),
    path('threshold/<int:pk>/', api.StockItemThresholdDetail.as_view(), name='threshold-detail'),
    path('stock-item/<int:pk>/threshold-status/', api.get_stock_item_threshold_status, name='stock-item-threshold-status'),
    path('low-stock/', api.get_low_stock_items, name='low-stock-items'),
]
