"""Stock threshold plugin app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StockThresholdPluginConfig(AppConfig):
    """App configuration for stock threshold plugin."""

    name = 'plugins.stock_threshold'
    verbose_name = _('Stock Threshold Plugin')

    def ready(self):
        """Run when app is ready."""
        # Import signals to ensure they are registered
        import plugins.stock_threshold.plugin
