"""Django app configuration for stock threshold plugin."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StockThresholdConfig(AppConfig):
    """App configuration for Stock Threshold Plugin."""
    
    name = 'inventree_threshold_plugin'
    verbose_name = _('Stock Threshold Plugin')
    
    def ready(self):
        """Called when the app is ready."""
        # Import signal handlers
        from . import signals
