"""URL patterns for stock_threshold plugin."""

from django.urls import path
from plugins.stock_threshold import api

urlpatterns = [
    path('threshold/<int:part_id>/', api.threshold_api, name='stock_threshold_api'),
    path('import/', api.import_thresholds_api, name='stock_threshold_import'),
    path('export/', api.export_thresholds_api, name='stock_threshold_export'),
]
