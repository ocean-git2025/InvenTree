"""Signal handlers for stock threshold plugin."""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

import stock.models
from .models import StockItemThreshold


@receiver(post_save, sender=stock.models.StockItem)
def create_default_threshold(sender, instance, created, **kwargs):
    """Optionally create default threshold for new stock items.
    
    This is a placeholder for future functionality where thresholds
    could be auto-created based on part settings.
    """
    # Currently disabled - thresholds are created manually
    pass


@receiver(post_delete, sender=stock.models.StockItem)
def cleanup_threshold_on_delete(sender, instance, **kwargs):
    """Clean up threshold configuration when a stock item is deleted.
    
    The OneToOne relationship should handle this automatically via CASCADE,
    but this signal provides a hook for any additional cleanup.
    """
    try:
        if hasattr(instance, 'threshold_config'):
            instance.threshold_config.delete()
    except StockItemThreshold.DoesNotExist:
        pass
