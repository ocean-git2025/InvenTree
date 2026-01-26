"""URL routes for Stock Threshold plugin."""

from django.urls import path

from . import views

app_name = 'stock_threshold'

urlpatterns = [
    path('parts/', views.StockThresholdList.as_view(), name='stock-threshold-list'),
    path('parts/<int:pk>/', views.StockThresholdDetail.as_view(), name='stock-threshold-detail'),
]
